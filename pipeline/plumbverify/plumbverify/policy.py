"""Block-not-flag enforcement (spec C11; CL-011) and confidence-label lint (C9; CL-009).

Decision rules (v0.1):
  - No citable source / no citation reaching verified or partial  -> BLOCKED ("unverified")
  - Any quotation that fails C5                                    -> BLOCKED
  - load_bearing and best citation only PARTIAL                    -> BLOCKED (PARTIAL = UNSUPPORTED for load-bearing)
  - load_bearing number with < 2 independent upstreams             -> BLOCKED ("single-upstream")
  - non-load-bearing fact with PARTIAL only, no second VERIFIED    -> BLOCKED
  - number claim with no confidence label                          -> BLOCKED (export lint, C9)
Blocked claims never carry a warning into output; they go to the gap register.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import (
    Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, GapEntry, UpstreamPair,
)

MIN_INDEPENDENT_UPSTREAMS = 2


def decide(
    claim: Claim,
    citations: list[Citation],
    independent_upstreams: int = 0,
    upstream_pairs: Optional[list[UpstreamPair]] = None,
) -> ClaimDecision:
    reasons: list[str] = []
    mine = [c for c in citations if c.claim_id == claim.id]
    verified = [c for c in mine if c.status == CitationStatus.verified]
    partial = [c for c in mine if c.status == CitationStatus.partial]
    blocked_cites = [c for c in mine if c.status == CitationStatus.blocked]

    if not mine:
        reasons.append("no citation supplied (C3: claims with no citation are UNSUPPORTED)")
    if claim.kind == ClaimKind.quote:
        if not verified:
            reasons.append("quotation does not exact-match any stored source (C5)")
            for c in blocked_cites:
                reasons.extend(f"{c.source_url}: {r}" for r in c.reasons)
    else:
        if not verified and not partial and mine:
            reasons.append("no citation reaches the support threshold (C4)")
            for c in mine:
                reasons.extend(f"{c.source_url}: {r}" for r in c.reasons)
        elif not verified and partial:
            if claim.load_bearing:
                reasons.append("only PARTIAL support; PARTIAL counts as UNSUPPORTED for load-bearing claims (C4)")
            else:
                reasons.append("PARTIAL support without a second SUPPORTED source (C4)")
    if claim.kind == ClaimKind.number and claim.load_bearing and independent_upstreams < MIN_INDEPENDENT_UPSTREAMS:
        reasons.append(
            f"single-upstream: {independent_upstreams} independent upstream(s), {MIN_INDEPENDENT_UPSTREAMS} required for load-bearing numbers (C6)"
        )
    if claim.kind == ClaimKind.number and claim.confidence_label is None:
        reasons.append("missing confidence label on a metric (C9 export lint)")

    blocked = bool(reasons)
    if blocked:
        status = CitationStatus.blocked
    elif verified:
        status = CitationStatus.verified
    else:
        status = CitationStatus.partial
    return ClaimDecision(
        claim_id=claim.id, status=status, blocked=blocked, load_bearing=claim.load_bearing,
        reasons=reasons, independent_upstreams=independent_upstreams, upstream_pairs=upstream_pairs or [],
    )


@dataclass
class BuildGate:
    passed: bool
    blocked_count: int
    gap_register: list[GapEntry]


def build_gate(claims: list[Claim], decisions: list[ClaimDecision]) -> BuildGate:
    """Deliverable build fails if any claim is BLOCKED (spec C11, T-09)."""
    by_id = {c.id: c for c in claims}
    gaps = [GapEntry(claim_id=d.claim_id, text=by_id[d.claim_id].text if d.claim_id in by_id else "", reasons=d.reasons)
            for d in decisions if d.blocked]
    return BuildGate(passed=not gaps, blocked_count=len(gaps), gap_register=gaps)


def released_claims(claims: list[Claim], decisions: list[ClaimDecision]) -> list[Claim]:
    """Claims allowed into client-facing output: everything not blocked. No
    'unverified' footnotes exist by construction."""
    blocked = {d.claim_id for d in decisions if d.blocked}
    return [c for c in claims if c.id not in blocked]
