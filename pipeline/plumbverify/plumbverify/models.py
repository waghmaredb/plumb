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


class SourceState(str, Enum):
    FETCHED = "FETCHED"
    ARCHIVED = "ARCHIVED"
    DEAD = "DEAD"
    LIKELY_HALLUCINATED = "LIKELY_HALLUCINATED"
    REJECTED_AIGEN = "REJECTED_AIGEN"
    REJECTED_FARM = "REJECTED_FARM"


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
    archived_url: Optional[str] = None
    http_status: Optional[int] = None
    health_class: HealthClass = HealthClass.DEAD
    state: SourceState = SourceState.DEAD
    text_extract: Optional[str] = None
    aigen_score: float = 0.0
    farm_score: float = 0.0
    upstream_of: list[str] = Field(default_factory=list, description="URLs of the original study/filing this source summarises (traced upstream)")
    error: Optional[str] = None

    @property
    def citable(self) -> bool:
        """Spec C2/C7: only LIVE or ARCHIVED-with-hash sources that are not rejected may be cited."""
        if self.state in (SourceState.REJECTED_AIGEN, SourceState.REJECTED_FARM):
            return False
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
    match_score: float = 0.0
    status: CitationStatus = CitationStatus.unverified
    reasons: list[str] = Field(default_factory=list)


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
    independent_upstreams: int = 0
    upstream_pairs: list[UpstreamPair] = Field(default_factory=list)


class GapEntry(BaseModel):
    claim_id: str
    text: str
    reasons: list[str]


class VerificationReport(BaseModel):
    run_id: str
    generated_at: datetime = Field(default_factory=utcnow)
    spec_version: str = "PI-CV v0.1"
    sources: list[Source] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    decisions: list[ClaimDecision] = Field(default_factory=list)
    gap_register: list[GapEntry] = Field(default_factory=list)
    build_pass: bool = False
    metrics: dict[str, float | int] = Field(default_factory=dict)
