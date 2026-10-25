"""Fetcher, content-hash evidence store and URL health check (spec C1, C2; CL-001, CL-002).

The fetcher is deliberately injectable: pass an ``httpx.Client`` built on
``httpx.MockTransport`` for offline tests, and a ``sleep`` callable to skip
backoff waits.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional, Protocol

import httpx

from .extract import extract_document
from .models import HealthClass, Reconciliation, Source, SourceState

USER_AGENT = "plumbverify/0.3 (+PLUMB verification pipeline; citation verification)"
DEFAULT_TIMEOUT = 20.0
DEFAULT_MAX_BODY = 25 * 1024 * 1024
DEFAULT_BACKOFF = (2.0, 8.0, 32.0)  # spec C2: retry 3x with exponential backoff
#: spec C2: "Re-check all LIVE URLs within 24 h of deck release". Every health
#: result carries ``recheck_after`` = checked_at + RECHECK_WINDOW; a release
#: must not rely on a LIVE classification older than that.
RECHECK_WINDOW = timedelta(hours=24)
#: spec C2: Wayback snapshot must be within 24 months
ARCHIVE_MAX_AGE_DAYS = 730


def recheck_deadline(checked_at: Optional[datetime] = None) -> datetime:
    """Instant after which a LIVE/ARCHIVED classification is stale (spec C2, S6)."""
    return (checked_at or datetime.now(timezone.utc)) + RECHECK_WINDOW


# --------------------------------------------------------------------------
# Archive (Wayback) hook
# --------------------------------------------------------------------------
@dataclass
class ArchiveSnapshot:
    archive_url: str
    timestamp: Optional[datetime] = None
    #: spec C2 24 h rule: re-verify the snapshot (and the live URL) after this instant
    recheck_after: datetime = field(default_factory=recheck_deadline)
    saved_now: bool = False  # True when produced by the save endpoint in this run


class ArchiveProvider(Protocol):
    """Interface for the C2 archive fallback. ``lookup`` returns a snapshot or None."""

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]: ...


class NullArchive:
    """Default: no archive lookups (keeps tests offline)."""

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]:
        return None


_WAYBACK_TS = re.compile(r"/web/(\d{14})(?:id_|if_|js_|cs_|im_)?/")


class WaybackArchive:
    """Wayback Machine client for the C2 archive fallback. Off by default: the
    CLI enables it with ``--archive``; saving is a second opt-in
    (``save_missing=True`` / ``--archive-save``) because it writes to a third
    party and is rate-limited.

    * ``lookup(url)`` queries the availability API and accepts the closest
      snapshot only if it is within ``max_age_days`` (spec: 24 months).
    * ``save(url)`` calls the Save Page Now endpoint and returns the new
      snapshot (parsed from the ``Content-Location`` / ``Location`` header).
    * every snapshot carries ``recheck_after`` (spec C2 24 h re-check rule).

    The ``client`` is injectable so tests run against ``httpx.MockTransport``.
    """

    ENDPOINT = "https://archive.org/wayback/available"
    SAVE_ENDPOINT = "https://web.archive.org/save/"

    def __init__(self, client: Optional[httpx.Client] = None, max_age_days: int = ARCHIVE_MAX_AGE_DAYS,
                 save_missing: bool = False, now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self.client = client or httpx.Client(timeout=DEFAULT_TIMEOUT, follow_redirects=True,
                                             headers={"User-Agent": USER_AGENT})
        self.max_age_days = max_age_days
        self.save_missing = save_missing
        self.now = now
        self.last_error: Optional[str] = None

    @staticmethod
    def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
        if not ts:
            return None
        try:
            return datetime.strptime(ts[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]:
        self.last_error = None
        try:
            r = self.client.get(self.ENDPOINT, params={"url": url})
            r.raise_for_status()
            snap = (r.json().get("archived_snapshots") or {}).get("closest")
        except Exception as e:
            self.last_error = f"availability: {type(e).__name__}: {e}"
            return None
        if snap and snap.get("available") and snap.get("url"):
            ts = self._parse_ts(snap.get("timestamp"))
            if ts is None or (self.now() - ts).days <= self.max_age_days:
                return ArchiveSnapshot(archive_url=snap["url"], timestamp=ts, recheck_after=recheck_deadline(self.now()))
            self.last_error = f"snapshot {snap.get('timestamp')} older than {self.max_age_days} days (C2: 24 months)"
        else:
            self.last_error = "no snapshot available"
        if self.save_missing:
            return self.save(url)
        return None

    def save(self, url: str) -> Optional[ArchiveSnapshot]:
        """Opt-in Save Page Now. Returns the new snapshot or None (error in ``last_error``)."""
        try:
            r = self.client.get(self.SAVE_ENDPOINT + url)
        except Exception as e:
            self.last_error = f"save: {type(e).__name__}: {e}"
            return None
        if r.status_code >= 400:
            self.last_error = f"save: HTTP {r.status_code}"
            return None
        loc = r.headers.get("content-location") or r.headers.get("location") or ""
        if loc and not loc.startswith("http"):
            loc = "https://web.archive.org" + (loc if loc.startswith("/") else "/" + loc)
        if not loc:
            final = str(r.url)
            loc = final if "/web/" in final else ""
        if not loc:
            self.last_error = "save: no snapshot location in response"
            return None
        m = _WAYBACK_TS.search(loc)
        return ArchiveSnapshot(archive_url=loc, timestamp=self._parse_ts(m.group(1)) if m else self.now(),
                               recheck_after=recheck_deadline(self.now()), saved_now=True)


# --------------------------------------------------------------------------
# Evidence store (sqlite index + raw bytes on disk, keyed by content hash)
# --------------------------------------------------------------------------
class EvidenceStore:
    """Immutable object store keyed by SHA-256 (spec C1). Raw bytes land in
    ``<root>/raw/<sha256>``; the sqlite index records fetch metadata and text."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.raw_dir = self.root / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "evidence.sqlite")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS sources (
                sha256 TEXT NOT NULL,
                url TEXT NOT NULL,
                url_final TEXT,
                fetched_at TEXT NOT NULL,
                http_status INTEGER,
                content_type TEXT,
                text_extract TEXT,
                PRIMARY KEY (sha256, url)
            )"""
        )
        # 0.3: person-supplied documents stored under their declared publisher URL.
        # One row per declared URL; the raw bytes sit in raw/<sha256> like any fetch.
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS attachments (
                url TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                supplied_by TEXT,
                supplied_at TEXT NOT NULL,
                original_filename TEXT,
                document_key TEXT,
                content_type TEXT,
                state TEXT NOT NULL,
                health_class TEXT NOT NULL,
                archived_url TEXT,
                recheck_after TEXT,
                reconciliation TEXT,
                reconciled_at TEXT,
                reconciled_sha256 TEXT,
                page_count INTEGER,
                needs_ocr INTEGER NOT NULL DEFAULT 0,
                detected_content_type TEXT,
                error TEXT
            )"""
        )
        self.db.commit()

    def put(self, source: Source, raw: bytes) -> None:
        assert source.sha256
        path = self.raw_dir / source.sha256
        if not path.exists():  # immutable: never overwrite
            path.write_bytes(raw)
        self.db.execute(
            "INSERT OR IGNORE INTO sources VALUES (?,?,?,?,?,?,?)",
            (
                source.sha256,
                source.url,
                source.url_final,
                (source.fetched_at or datetime.now(timezone.utc)).isoformat(),
                source.http_status,
                source.content_type,
                source.text_extract,
            ),
        )
        self.db.commit()

    def get_raw(self, sha256: str) -> Optional[bytes]:
        path = self.raw_dir / sha256
        return path.read_bytes() if path.exists() else None

    def lookup_url(self, url: str) -> Optional[dict]:
        row = self.db.execute(
            "SELECT sha256,url,url_final,fetched_at,http_status,content_type,text_extract FROM sources WHERE url=? ORDER BY fetched_at DESC LIMIT 1",
            (url,),
        ).fetchone()
        if not row:
            return None
        keys = ["sha256", "url", "url_final", "fetched_at", "http_status", "content_type", "text_extract"]
        return dict(zip(keys, row))

    def verify_hash(self, sha256: str) -> bool:
        raw = self.get_raw(sha256)
        return raw is not None and hashlib.sha256(raw).hexdigest() == sha256

    # -- attachments (0.3) ---------------------------------------------------
    _ATT_COLS = ("url", "sha256", "supplied_by", "supplied_at", "original_filename", "document_key", "content_type",
                 "state", "health_class", "archived_url", "recheck_after", "reconciliation", "reconciled_at",
                 "reconciled_sha256", "page_count", "needs_ocr", "detected_content_type", "error")

    def put_attachment(self, source: Source, raw: bytes) -> None:
        """Store a person-supplied document under its declared URL. The bytes
        and the ``sources`` row are written exactly as for a fetch; the
        ``attachments`` row carries provenance and reconciliation state and is
        the one record that is updated later (by :func:`plumbverify.ingest.reconcile`)."""
        assert source.sha256 and source.provenance
        self.put(source, raw)
        prov = source.provenance
        self.db.execute(
            f"INSERT OR REPLACE INTO attachments ({','.join(self._ATT_COLS)}) VALUES ({','.join('?' * len(self._ATT_COLS))})",
            (source.url, source.sha256, prov.get("supplied_by"), prov.get("supplied_at") or (source.fetched_at or datetime.now(timezone.utc)).isoformat(),
             prov.get("original_filename"), prov.get("document_key"), source.content_type, source.state.value,
             source.health_class.value, source.archived_url,
             source.recheck_after.isoformat() if source.recheck_after else None,
             source.reconciliation.value if source.reconciliation else None,
             source.reconciled_at.isoformat() if source.reconciled_at else None, source.reconciled_sha256,
             source.page_count, 1 if source.needs_ocr else 0, source.detected_content_type, source.error),
        )
        self.db.commit()

    def update_attachment(self, url: str, **fields) -> None:
        bad = set(fields) - set(self._ATT_COLS)
        if bad:
            raise ValueError(f"unknown attachment columns: {sorted(bad)}")
        if not fields:
            return
        sets = ", ".join(f"{k}=?" for k in fields)
        vals = [(v.value if isinstance(v, Enum) else v.isoformat() if isinstance(v, datetime) else v) for v in fields.values()]
        self.db.execute(f"UPDATE attachments SET {sets} WHERE url=?", (*vals, url))
        self.db.commit()

    def get_attachment(self, url: str) -> Optional[dict]:
        row = self.db.execute(f"SELECT {','.join(self._ATT_COLS)} FROM attachments WHERE url=?", (url,)).fetchone()
        if not row:
            row = self.db.execute(f"SELECT {','.join(self._ATT_COLS)} FROM attachments WHERE url=?", (url.rstrip("/"),)).fetchone()
        return dict(zip(self._ATT_COLS, row)) if row else None

    def list_attachments(self) -> list[dict]:
        rows = self.db.execute(f"SELECT {','.join(self._ATT_COLS)} FROM attachments ORDER BY supplied_at, url").fetchall()
        return [dict(zip(self._ATT_COLS, r)) for r in rows]

    def load_attached_source(self, url: str) -> Optional[Source]:
        """Rebuild the ``Source`` for an attached URL (None when nothing is attached)."""
        att = self.get_attachment(url)
        if not att:
            return None
        row = self.db.execute(
            "SELECT text_extract, fetched_at FROM sources WHERE sha256=? AND url=?", (att["sha256"], att["url"])
        ).fetchone()
        text, fetched_at = (row or (None, att["supplied_at"]))
        _dt = lambda v: datetime.fromisoformat(v) if v else None
        return Source(
            url=att["url"], url_final=att["url"], fetched_at=_dt(fetched_at), sha256=att["sha256"],
            content_type=att["content_type"], detected_content_type=att["detected_content_type"],
            page_count=att["page_count"], needs_ocr=bool(att["needs_ocr"]), recheck_after=_dt(att["recheck_after"]),
            archived_url=att["archived_url"], health_class=HealthClass(att["health_class"]), state=SourceState(att["state"]),
            text_extract=text,
            provenance={"supplied_by": att["supplied_by"], "supplied_at": att["supplied_at"],
                        "original_filename": att["original_filename"], "declared_url": att["url"],
                        **({"document_key": att["document_key"]} if att["document_key"] else {})},
            reconciliation=Reconciliation(att["reconciliation"]) if att["reconciliation"] else None,
            reconciled_at=_dt(att["reconciled_at"]), reconciled_sha256=att["reconciled_sha256"], error=att["error"],
        )

    def close(self) -> None:
        self.db.close()


# --------------------------------------------------------------------------
# Health classification
# --------------------------------------------------------------------------
@dataclass
class HealthResult:
    url: str
    health_class: HealthClass
    http_status: Optional[int] = None
    url_final: Optional[str] = None
    redirects: list[str] = field(default_factory=list)
    archived_url: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    recheck_after: Optional[datetime] = None  # spec C2 24 h rule; set for LIVE / ARCHIVED


_PLAUSIBLE_PATH = re.compile(r"/(?:[a-z0-9]+(?:-[a-z0-9]+){1,}|\d{4}/\d{1,2})(?:/|\.html?|\.pdf|$)", re.I)


def looks_pattern_plausible(url: str) -> bool:
    """Heuristic for LIKELY_HALLUCINATED: a slug-like or dated path that a model
    would plausibly invent (e.g. /2025/10/deloitte-refund-report)."""
    try:
        path = httpx.URL(url).path
    except Exception:
        return False
    return bool(_PLAUSIBLE_PATH.search(path))


# --------------------------------------------------------------------------
# Fetcher
# --------------------------------------------------------------------------
class Fetcher:
    def __init__(
        self,
        store: Optional[EvidenceStore] = None,
        client: Optional[httpx.Client] = None,
        archive: Optional[ArchiveProvider] = None,
        timeout: float = DEFAULT_TIMEOUT,
        backoff: tuple[float, ...] = DEFAULT_BACKOFF,
        max_body: int = DEFAULT_MAX_BODY,
        sleep: Callable[[float], None] = time.sleep,
        reconcile_on_fetch: bool = False,
    ):
        """``reconcile_on_fetch`` (0.3): when the store holds an ATTACHED document
        for a URL, ``False`` (default) returns the attachment without touching the
        network, so a no-egress run does not burn the retry/backoff budget on a
        URL it cannot reach; ``True`` fetches the declared URL and reconciles the
        attachment against the publisher bytes (MATCH flips it to LIVE/ARCHIVED,
        MISMATCH blocks it), falling back to the attachment when the fetch fails."""
        self.store = store
        self.reconcile_on_fetch = reconcile_on_fetch
        self.client = client or httpx.Client(
            timeout=timeout, follow_redirects=True, headers={"User-Agent": USER_AGENT}
        )
        self.archive = archive or NullArchive()
        self.backoff = backoff
        self.max_body = max_body
        self.sleep = sleep

    # -- low-level request with retries ------------------------------------
    def _request(self, method: str, url: str) -> tuple[Optional[httpx.Response], Optional[str], int]:
        """Returns (response, error, attempts). Retries on transport errors and 5xx."""
        last_err: Optional[str] = None
        attempts = 0
        for i in range(len(self.backoff) + 1):
            attempts += 1
            try:
                resp = self.client.request(method, url)
            except httpx.TransportError as e:  # DNS, connect, timeout, read errors
                last_err = f"{type(e).__name__}: {e}"
                resp = None
            if resp is not None and resp.status_code < 500:
                return resp, None, attempts
            if resp is not None:
                last_err = f"HTTP {resp.status_code}"
            if i < len(self.backoff):
                self.sleep(self.backoff[i])
        return None, last_err, attempts

    # -- health check ------------------------------------------------------
    def check_health(self, url: str) -> HealthResult:
        """HEAD then GET; classify LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED (spec C2)."""
        resp, err, attempts = self._request("HEAD", url)
        if resp is None or resp.status_code >= 400 or resp.status_code == 405:
            resp2, err2, attempts2 = self._request("GET", url)
            attempts += attempts2
            if resp2 is not None:
                resp, err = resp2, None
            elif resp is None:
                err = err2
        result = HealthResult(url=url, health_class=HealthClass.DEAD, attempts=attempts, error=err)
        if resp is not None:
            result.http_status = resp.status_code
            result.url_final = str(resp.url)
            result.redirects = [str(h.url) for h in resp.history]
            if 200 <= resp.status_code < 300:
                result.health_class = HealthClass.LIVE
                result.recheck_after = recheck_deadline()
                return result
        # persistent failure: archive fallback
        snap = self.archive.lookup(url)
        if snap is not None:
            result.health_class = HealthClass.ARCHIVED
            result.archived_url = snap.archive_url
            result.recheck_after = snap.recheck_after
            return result
        dns_or_connect_failure = resp is None and err is not None and (
            "ConnectError" in err or "ConnectTimeout" in err
        )
        if dns_or_connect_failure and looks_pattern_plausible(url):
            result.health_class = HealthClass.LIKELY_HALLUCINATED
        else:
            result.health_class = HealthClass.DEAD
        return result

    # -- extraction helper -------------------------------------------------
    @staticmethod
    def _extract_into(src: Source, raw: bytes) -> None:
        """Extract text; on parse failure keep the bytes and set text_extract=None (spec C1)."""
        try:
            ex = extract_document(raw, src.content_type)
        except Exception as e:
            src.text_extract = None
            src.error = f"extract: {e}"
            return
        src.detected_content_type = ex.content_type
        src.page_count = ex.page_count
        src.needs_ocr = ex.needs_ocr
        src.text_extract = ex.text
        if ex.needs_ocr:
            src.error = "PDF has no usable text layer (scanned); needs OCR before claims can match"
        elif ex.error and not ex.text:
            src.error = f"extract: {ex.error}"

    # -- fetch + hash ------------------------------------------------------
    def fetch(self, url: str) -> Source:
        """Fetch once, hash, extract text, store; returns a Source in FETCHED,
        ARCHIVED, DEAD or LIKELY_HALLUCINATED state. An ATTACHED document in the
        store is preferred over a failed fetch (0.3; see ``reconcile_on_fetch``)."""
        attached = self.store.load_attached_source(url) if self.store is not None else None
        if attached is not None:
            if not self.reconcile_on_fetch or attached.reconciliation == Reconciliation.MISMATCH:
                return attached
            return self._fetch_and_reconcile(url, attached)
        return self._fetch_live(url)

    def _fetch_and_reconcile(self, url: str, attached: Source) -> Source:
        from .ingest import reconcile  # local import: ingest depends on this module

        resp, _err, _ = self._request("GET", url)
        if resp is not None and 200 <= resp.status_code < 300:
            reconcile(self.store, url, resp.content[: self.max_body])
            return self.store.load_attached_source(url) or attached
        health = self.check_health(url)
        if health.health_class == HealthClass.ARCHIVED and health.archived_url:
            arch_resp, _e, _ = self._request("GET", health.archived_url)
            if arch_resp is not None and 200 <= arch_resp.status_code < 300:
                reconcile(self.store, url, arch_resp.content[: self.max_body], archived_url=health.archived_url)
                return self.store.load_attached_source(url) or attached
        reconcile(self.store, url, None)
        return self.store.load_attached_source(url) or attached

    def _fetch_live(self, url: str) -> Source:
        src = Source(url=url, fetched_at=datetime.now(timezone.utc))
        resp, err, _ = self._request("GET", url)
        if resp is not None and 200 <= resp.status_code < 300:
            raw = resp.content[: self.max_body]
            src.http_status = resp.status_code
            src.url_final = str(resp.url)
            src.content_type = resp.headers.get("content-type")
            src.sha256 = hashlib.sha256(raw).hexdigest()
            src.health_class = HealthClass.LIVE
            src.state = SourceState.FETCHED
            src.recheck_after = recheck_deadline(src.fetched_at)
            self._extract_into(src, raw)
            if self.store is not None:
                self.store.put(src, raw)
            return src
        # failure path: health classification decides the state
        health = self.check_health(url)
        src.http_status = health.http_status
        src.url_final = health.url_final
        src.error = health.error or err
        src.health_class = health.health_class
        if health.health_class == HealthClass.ARCHIVED and health.archived_url:
            src.archived_url = health.archived_url
            arch_resp, arch_err, _ = self._request("GET", health.archived_url)
            if arch_resp is not None and 200 <= arch_resp.status_code < 300:
                raw = arch_resp.content[: self.max_body]
                src.sha256 = hashlib.sha256(raw).hexdigest()
                src.content_type = arch_resp.headers.get("content-type")
                src.state = SourceState.ARCHIVED
                src.recheck_after = health.recheck_after
                self._extract_into(src, raw)
                if self.store is not None:
                    self.store.put(src, raw)
            else:
                src.error = f"archive fetch failed: {arch_err}"
                src.state = SourceState.DEAD
                src.health_class = HealthClass.DEAD
        elif health.health_class == HealthClass.LIKELY_HALLUCINATED:
            src.state = SourceState.LIKELY_HALLUCINATED
        else:
            src.state = SourceState.DEAD
        return src
