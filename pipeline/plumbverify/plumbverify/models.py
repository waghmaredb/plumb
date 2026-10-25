"""Pydantic models for the PLUMB verification layer (spec section 3.1).

Field names follow the task brief; the spec's richer state names are kept
as enums so the report can be read against the spec tables.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tier(str, Enum):
    T1 = "T1"  # regulator filings, primary documents, peer-reviewed
    T2 = "T2"  # investor materials, central-bank and official statistics
    T3 = "T3"  # named consulting-firm research, reputable trade press
    T4 = "T4"  # vendor and practitioner content (labelled)
    T5 = "T5"  # aggregators and SEO content; discovery only


class HealthClass(str, Enum):
    LIVE = "LIVE"
    ARCHIVED = "ARCHIVED"
    DEAD = "DEAD"
    LIKELY_HALLUCINATED = "LIKELY_HALLUCINATED"
    UNCHECKED = "UNCHECKED"  # attached document: no URL health check has run yet (0.3)


class SourceState(str, Enum):
    FETCHED = "FETCHED"
    ARCHIVED = "ARCHIVED"
    ATTACHED = "ATTACHED"  # supplied by a person, stored under its declared publisher URL, publisher hash not yet reconciled (0.3)
    DEAD = "DEAD"
    LIKELY_HALLUCINATED = "LIKELY_HALLUCINATED"
    REJECTED_AIGEN = "REJECTED_AIGEN"
    REJECTED_FARM = "REJECTED_FARM"


class Reconciliation(str, Enum):
    """Outcome of re-fetching an ATTACHED source's declared URL and comparing hashes."""
    MATCH = "MATCH"            # publisher bytes hash equal: the attachment is the published document
    MISMATCH = "MISMATCH"      # publisher bytes differ: every claim citing the attachment is BLOCKED
    UNAVAILABLE = "UNAVAILABLE"  # declared URL could not be fetched (no egress, 4xx/5xx, no archive)


#: label every citation from an unreconciled ATTACHED source must carry
ATTACHED_LABEL = "attached; publisher hash unreconciled"
#: prefix the policy layer keys on (spec C2a); any label starting with it marks an unreconciled attachment
ATTACHED_LABEL_PREFIX = "attached;"


class ClaimKind(str, Enum):
    number = "number"
    quote = "quote"
    fact = "fact"


class ConfidenceLabel(str, Enum):
    filed = "filed"
    vendor_estimate = "vendor-estimate"
    model_inferred = "model-inferred"
    interview_anecdote = "interview-anecdote"


class CitationStatus(str, Enum):
    verified = "verified"
    partial = "partial"
    unverified = "unverified"
    blocked = "blocked"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Source(BaseModel):
    url: str
    url_final: Optional[str] = None
    fetched_at: Optional[datetime] = None
    sha256: Optional[str] = None
    tier: Tier = Tier.T5
    content_type: Optional[str] = None
    detected_content_type: Optional[str] = Field(default=None, description="media type sniffed from magic bytes (may differ from the declared header)")
    page_count: Optional[int] = Field(default=None, description="pages in a paginated source (PDF)")
    needs_ocr: bool = Field(default=False, description="PDF with no usable text layer (scanned); OCR required before matching")
    recheck_after: Optional[datetime] = Field(default=None, description="spec C2: LIVE URLs must be re-checked within 24 h of release; the health result is stale after this instant")
    archived_url: Optional[str] = None
    http_status: Optional[int] = None
    health_class: HealthClass = HealthClass.DEAD
    state: SourceState = SourceState.DEAD
    text_extract: Optional[str] = None
    aigen_score: float = 0.0
    farm_score: float = 0.0
    upstream_of: list[str] = Field(default_factory=list, description="URLs of the original study/filing this source summarises (traced upstream)")
    upstream_candidates: list[str] = Field(default_factory=list, description="ranked candidate originals found by trace_upstream on an aggregator page; untraced until fetched and hashed")
    provenance: Optional[dict] = Field(default=None, description="ATTACHED sources: supplied_by, supplied_at, original_filename, declared_url (+ document_key when mapped by plumbresearch)")
    reconciliation: Optional[Reconciliation] = Field(default=None, description="ATTACHED sources: result of the last publisher re-fetch and hash comparison; None until reconcile has run")
    reconciled_at: Optional[datetime] = None
    reconciled_sha256: Optional[str] = Field(default=None, description="SHA-256 of the publisher bytes seen at reconciliation (differs from sha256 on MISMATCH)")
    error: Optional[str] = None

    @property
    def attached(self) -> bool:
        """True while the source is a person-supplied document whose publisher hash is unreconciled."""
        return self.state == SourceState.ATTACHED

    @property
    def attached_label(self) -> Optional[str]:
        """Visible label every citation from an unreconciled attachment carries (None otherwise)."""
        return ATTACHED_LABEL if self.attached else None

    @property
    def citable(self) -> bool:
        """Spec C2/C7: only LIVE or ARCHIVED-with-hash sources that are not rejected may be cited.
        0.3: an ATTACHED source is citable (with the attached label) unless reconciliation found a MISMATCH."""
        if self.state in (SourceState.REJECTED_AIGEN, SourceState.REJECTED_FARM):
            return False
        if self.reconciliation == Reconciliation.MISMATCH:
            return False
        if self.state == SourceState.ATTACHED:
            return self.sha256 is not None
        if self.health_class == HealthClass.LIVE:
            return self.sha256 is not None
        if self.health_class == HealthClass.ARCHIVED:
            return self.sha256 is not None and self.archived_url is not None
        return False


class Claim(BaseModel):
    id: str
    text: str
    kind: ClaimKind
    load_bearing: bool = False
    confidence_label: Optional[ConfidenceLabel] = None
    module: Optional[str] = None
    sources: list[str] = Field(default_factory=list, description="Candidate source URLs cited for this claim")


class Citation(BaseModel):
    claim_id: str
    source_url: str
    passage: Optional[str] = None
    page: Optional[int] = Field(default=None, description="1-based page of the matched passage for paginated sources (renders as 'p. N')")
    match_score: float = 0.0
    status: CitationStatus = CitationStatus.unverified
    reasons: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list, description="visible caveats that travel with the citation into output, e.g. the attached label (0.3)")

    @property
    def locator(self) -> str:
        """Citation locator for reviewer output: the URL plus 'p. N' when known."""
        return f"{self.source_url} (p. {self.page})" if self.page else self.source_url


class UpstreamPair(BaseModel):
    a: str
    b: str
    independent: bool
    reasons: list[str] = Field(default_factory=list)


class ClaimDecision(BaseModel):
    claim_id: str
    status: CitationStatus
    blocked: bool
    load_bearing: bool
    reasons: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list, description="labels carried by the supporting citations (e.g. attached; publisher hash unreconciled)")
    independent_upstreams: int = 0
    upstream_pairs: list[UpstreamPair] = Field(default_factory=list)
    withheld_awaiting_reconciliation: bool = Field(default=False, description="C2a: blocked in a client build only because its support is an unreconciled attachment (0.4)")


class GapEntry(BaseModel):
    claim_id: str
    text: str
    reasons: list[str]


class VerificationReport(BaseModel):
    run_id: str
    generated_at: datetime = Field(default_factory=utcnow)
    spec_version: str = "PI-CV v0.1"
    build_profile: str = Field(default="client", description="'client' (C2a: unreconciled attachments BLOCKED) or 'internal' (labelled path) (0.4)")
    sources: list[Source] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    decisions: list[ClaimDecision] = Field(default_factory=list)
    gap_register: list[GapEntry] = Field(default_factory=list)
    build_pass: bool = False
    metrics: dict[str, float | int] = Field(default_factory=dict)
