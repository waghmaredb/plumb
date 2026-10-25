"""Attached-document ingest and publisher reconciliation (0.3).

Why this exists. The pipeline treats URL-fetched bytes as the only citable
evidence (spec C1/C2). In an environment without egress the person running
the sprint attaches the primary document (an annual-report PDF) directly.
That document must enter the evidence store with the same integrity
guarantees as a fetch, not through a side door:

* it is hashed (SHA-256 over the raw bytes), text-extracted (PDF/HTML,
  page-aware, ``needs_ocr`` for scans) and stored immutably exactly like a
  fetch, **under the declared canonical URL** - the publisher's URL the file
  claims to come from - so the citation of record stays the URL;
* its ``Source.state`` is ``ATTACHED`` and ``Source.provenance`` records who
  supplied it, when, the original file name and the declared URL;
* it is citable (C2) but weaker than fetched evidence: every citation from it
  carries the visible label ``"attached; publisher hash unreconciled"`` until
  :func:`reconcile` has fetched the declared URL and found the publisher's
  bytes hash-identical (``MATCH``), at which point the state flips to
  FETCHED/LIVE (or ARCHIVED when the bytes came from the archive) and the
  label disappears. A ``MISMATCH`` makes the source non-citable, which blocks
  every claim citing it (C11). ``UNAVAILABLE`` leaves it ATTACHED and labelled.
* ``recheck_after`` is set so the S6 re-check picks it up like any LIVE
  classification: when egress is available, run ``plumbverify reconcile``.

Tier assignment uses the declared URL's domain as for any fetched source.
"""
from __future__ import annotations

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .extract import extract_document
from .fetch import EvidenceStore, Fetcher, recheck_deadline
from .models import HealthClass, Reconciliation, Source, SourceState
from .tier import TierRules, assign_tier


def _guess_content_type(path: Path) -> Optional[str]:
    t, _ = mimetypes.guess_type(str(path))
    if t:
        return t
    return "application/pdf" if path.suffix.lower() == ".pdf" else None


def ingest_local(
    path: str | Path,
    declared_url: str,
    store: EvidenceStore,
    *,
    provenance: Optional[dict] = None,
    supplied_by: Optional[str] = None,
    document_key: Optional[str] = None,
    tier_rules: Optional[TierRules] = None,
    now: Optional[datetime] = None,
) -> Source:
    """Read a local file, hash it, extract its text and store it under
    ``declared_url`` as an ``ATTACHED`` source.

    ``provenance`` may pre-fill ``supplied_by`` / ``supplied_at`` /
    ``original_filename`` / ``declared_url``; missing keys are filled in here.
    Re-ingesting the same URL replaces the attachment row (the raw bytes of
    both versions stay in the store, keyed by hash).
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"attached document not found: {path}")
    if not declared_url.lower().startswith(("http://", "https://")):
        raise ValueError(f"declared URL must be an absolute http(s) URL (the publisher's URL): {declared_url!r}")
    now = now or datetime.now(timezone.utc)
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    prov = {
        "supplied_by": supplied_by,
        "supplied_at": now.isoformat(),
        "original_filename": path.name,
        "declared_url": declared_url,
        "size_bytes": len(raw),
    }
    if provenance:
        prov.update({k: v for k, v in provenance.items() if v is not None})
    if document_key:
        prov["document_key"] = document_key
    src = Source(
        url=declared_url, url_final=declared_url, fetched_at=now, sha256=sha,
        content_type=_guess_content_type(path), http_status=None,
        health_class=HealthClass.UNCHECKED, state=SourceState.ATTACHED,
        recheck_after=recheck_deadline(now), provenance=prov,
    )
    src.tier = assign_tier(declared_url, tier_rules).tier
    Fetcher._extract_into(src, raw)
    store.put_attachment(src, raw)
    return src


def reconcile(store: EvidenceStore, url: str, fetched_bytes: Optional[bytes], *,
              archived_url: Optional[str] = None, now: Optional[datetime] = None) -> Reconciliation:
    """Compare the publisher's bytes for ``url`` with the attached copy.

    ``fetched_bytes`` is what a fresh GET of the declared URL (or of its
    archive snapshot, with ``archived_url`` set) returned; ``None`` means the
    URL could not be fetched. Updates the attachment row in the store:

    * MATCH: state -> FETCHED (health LIVE) or ARCHIVED when ``archived_url`` is
      given; the attached label no longer applies; ``recheck_after`` restarts.
    * MISMATCH: state stays ATTACHED, ``reconciliation`` = MISMATCH, source is
      no longer citable; the publisher bytes are kept in the store under their
      own hash (``reconciled_sha256``) as evidence of the discrepancy.
    * UNAVAILABLE: no change except the recorded attempt.
    """
    att = store.get_attachment(url)
    if att is None:
        raise KeyError(f"no attached document stored under {url}")
    now = now or datetime.now(timezone.utc)
    if fetched_bytes is None:
        store.update_attachment(att["url"], reconciliation=Reconciliation.UNAVAILABLE, reconciled_at=now)
        return Reconciliation.UNAVAILABLE
    live_sha = hashlib.sha256(fetched_bytes).hexdigest()
    if live_sha == att["sha256"]:
        store.update_attachment(
            att["url"], reconciliation=Reconciliation.MATCH, reconciled_at=now, reconciled_sha256=live_sha,
            state=SourceState.ARCHIVED if archived_url else SourceState.FETCHED,
            health_class=HealthClass.ARCHIVED if archived_url else HealthClass.LIVE,
            archived_url=archived_url, recheck_after=recheck_deadline(now), error=None,
        )
        return Reconciliation.MATCH
    # keep the publisher's bytes: they are the evidence that the attachment is not the published document
    mismatch_path = store.raw_dir / live_sha
    if not mismatch_path.exists():
        mismatch_path.write_bytes(fetched_bytes)
    store.update_attachment(
        att["url"], reconciliation=Reconciliation.MISMATCH, reconciled_at=now, reconciled_sha256=live_sha,
        error=f"reconcile MISMATCH: attached document hash {att['sha256'][:16]}... does not match publisher bytes {live_sha[:16]}... "
              f"fetched {now.isoformat(timespec='minutes')}; all claims citing it are BLOCKED",
    )
    return Reconciliation.MISMATCH


def reconcile_all(store: EvidenceStore, fetcher: Fetcher, url: Optional[str] = None,
                  include_reconciled: bool = False) -> list[tuple[str, Reconciliation]]:
    """Re-fetch every attached URL (or just ``url``) with ``fetcher`` and
    reconcile. Sources already at MATCH are skipped unless ``include_reconciled``.
    The fetcher is used only for transport (``_request`` / ``check_health``), so
    an ``httpx.MockTransport`` client reconciles offline in tests."""
    rows = [store.get_attachment(url)] if url else store.list_attachments()
    out: list[tuple[str, Reconciliation]] = []
    for att in rows:
        if att is None:
            raise KeyError(f"no attached document stored under {url}")
        if att["reconciliation"] == Reconciliation.MATCH.value and not include_reconciled:
            out.append((att["url"], Reconciliation.MATCH))
            continue
        resp, _err, _ = fetcher._request("GET", att["url"])
        if resp is not None and 200 <= resp.status_code < 300:
            out.append((att["url"], reconcile(store, att["url"], resp.content[: fetcher.max_body])))
            continue
        health = fetcher.check_health(att["url"])
        if health.health_class == HealthClass.ARCHIVED and health.archived_url:
            arch, _e, _ = fetcher._request("GET", health.archived_url)
            if arch is not None and 200 <= arch.status_code < 300:
                out.append((att["url"], reconcile(store, att["url"], arch.content[: fetcher.max_body], archived_url=health.archived_url)))
                continue
        out.append((att["url"], reconcile(store, att["url"], None)))
    return out
