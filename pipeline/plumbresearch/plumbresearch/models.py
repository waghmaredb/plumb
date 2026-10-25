"""Research-layer models built on plumbverify's claim model.

A module produces two kinds of thing:

* ``ResearchClaim`` — a ``plumbverify.models.Claim`` with provenance attached
  (source URL, the passage the claim was lifted from, tier, confidence label,
  the instrument items it feeds). These go through ``plumbverify.Verifier``
  unchanged; the extra fields ride along for the evidence appendix.
* ``Signal`` — a derived figure computed in code (rubric level, posting share,
  call density, percentile). Spec 3.1 architecture note: derived figures are
  computed in code, never by a model, and are not themselves "claims" that a
  passage can support. A signal lists the evidence claims it rests on; the
  orchestrator sets its status from their verification outcome.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from plumbverify.models import Claim, ConfidenceLabel, Tier


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchClaim(Claim):
    """plumbverify Claim plus provenance. ``sources`` (inherited) is the list of
    URLs the Verifier will fetch; ``passage`` is the span the module lifted the
    claim from, kept so the reviewer can locate it quickly (spec 6.2 P4)."""

    passage: Optional[str] = None
    tier: Optional[Tier] = None
    instrument_items: list[str] = Field(default_factory=list, description="e.g. ['D1.1', 'D8.3']")
    signal_ids: list[str] = Field(default_factory=list)
    value: Optional[float] = None
    unit: Optional[str] = None
    period: Optional[str] = None
    note: Optional[str] = None
    attrs: dict[str, Any] = Field(default_factory=dict, description="module-specific structured metadata (e.g. findings: category, stage, "
                                  "use_case, page_expected); rides along into claims.json for the deck, never read by the Verifier")


class Signal(BaseModel):
    """A proxy-signal value for the signals table (instrument §3 proxy rows)."""

    id: str
    module: str
    name: str
    instrument_items: list[str] = Field(default_factory=list)
    value: Optional[float | int | str] = None
    unit: Optional[str] = None
    source: str = ""
    source_urls: list[str] = Field(default_factory=list)
    tier: Optional[Tier] = None
    confidence_label: ConfidenceLabel = ConfidenceLabel.model_inferred
    evidence_claim_ids: list[str] = Field(default_factory=list)
    detail: dict[str, Any] = Field(default_factory=dict)
    note: Optional[str] = None
    status: str = "computed"  # set by the orchestrator: released | partial | blocked | not-available | computed


class Gap(BaseModel):
    """A data gap the module could not close (disclosed, never estimated silently)."""

    module: str
    topic: str
    detail: str
    verify_flag: bool = False
    instrument_items: list[str] = Field(default_factory=list)


class ModuleResult(BaseModel):
    module: str
    subject_slug: str
    claims: list[ResearchClaim] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    exhibits: dict[str, str] = Field(default_factory=dict, description="name -> Markdown")
    data_available: bool = True
    tool_calls: int = 0
    restarts: int = 0
    escalated: bool = False
    detail: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=utcnow)


def confidence_for_tier(tier: Optional[Tier]) -> ConfidenceLabel:
    """Spec C9 label rules. T1/T2 primary = filed; T4 vendor = vendor-estimate.
    Extension (documented in README): T3 reported figures are also labelled
    filed (they are figures a named publisher filed, not pipeline estimates);
    T5 and untiered figures are labelled model-inferred because an aggregator
    figure has not been traced to a terminus."""
    if tier in (Tier.T1, Tier.T2, Tier.T3):
        return ConfidenceLabel.filed
    if tier == Tier.T4:
        return ConfidenceLabel.vendor_estimate
    return ConfidenceLabel.model_inferred
