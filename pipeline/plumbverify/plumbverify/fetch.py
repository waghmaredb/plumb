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
from pathlib import Path
from typing import Callable, Optional, Protocol

import httpx

from .extract import extract_document
from .models import HealthClass, Source, SourceState

USER_AGENT = "plumbverify/0.2 (+PLUMB verification pipeline; citation verification)"
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
    ):
        self.store = store
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
        ARCHIVED, DEAD or LIKELY_HALLUCINATED state."""
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
