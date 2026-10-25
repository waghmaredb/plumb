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
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Protocol

import httpx

from .extract import extract_main_text
from .models import HealthClass, Source, SourceState

USER_AGENT = "plumbverify/0.1 (+PLUMB verification pipeline; citation verification)"
DEFAULT_TIMEOUT = 20.0
DEFAULT_MAX_BODY = 25 * 1024 * 1024
DEFAULT_BACKOFF = (2.0, 8.0, 32.0)  # spec C2: retry 3x with exponential backoff


# --------------------------------------------------------------------------
# Archive (Wayback) hook
# --------------------------------------------------------------------------
@dataclass
class ArchiveSnapshot:
    archive_url: str
    timestamp: Optional[datetime] = None


class ArchiveProvider(Protocol):
    """Interface for the C2 archive fallback. ``lookup`` returns a snapshot or None."""

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]: ...


class NullArchive:
    """Default: no archive lookups (keeps tests offline)."""

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]:
        return None


class WaybackArchive:
    """STUB: minimal Wayback availability-API client. Not exercised by tests.

    Spec C2 asks for a snapshot within 24 months; the window check is applied
    on the returned timestamp when present.
    """

    ENDPOINT = "https://archive.org/wayback/available"

    def __init__(self, client: Optional[httpx.Client] = None, max_age_days: int = 730):
        self.client = client or httpx.Client(timeout=DEFAULT_TIMEOUT, headers={"User-Agent": USER_AGENT})
        self.max_age_days = max_age_days

    def lookup(self, url: str) -> Optional[ArchiveSnapshot]:
        try:
            r = self.client.get(self.ENDPOINT, params={"url": url})
            r.raise_for_status()
            snap = (r.json().get("archived_snapshots") or {}).get("closest")
        except Exception:
            return None
        if not snap or not snap.get("available"):
            return None
        ts = None
        try:
            ts = datetime.strptime(snap["timestamp"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - ts).days > self.max_age_days:
                return None
        except Exception:
            pass
        return ArchiveSnapshot(archive_url=snap["url"], timestamp=ts)


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
                return result
        # persistent failure: archive fallback
        snap = self.archive.lookup(url)
        if snap is not None:
            result.health_class = HealthClass.ARCHIVED
            result.archived_url = snap.archive_url
            return result
        dns_or_connect_failure = resp is None and err is not None and (
            "ConnectError" in err or "ConnectTimeout" in err
        )
        if dns_or_connect_failure and looks_pattern_plausible(url):
            result.health_class = HealthClass.LIKELY_HALLUCINATED
        else:
            result.health_class = HealthClass.DEAD
        return result

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
            try:
                src.text_extract = extract_main_text(raw, src.content_type)
            except Exception as e:  # parse failure: keep bytes, text_extract=None (spec C1)
                src.text_extract = None
                src.error = f"extract: {e}"
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
                try:
                    src.text_extract = extract_main_text(raw, src.content_type)
                except Exception:
                    src.text_extract = None
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
