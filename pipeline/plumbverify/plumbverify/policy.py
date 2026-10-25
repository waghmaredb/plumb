"""Block-not-flag enforcement (spec C11; CL-011) and confidence-label lint (C9; CL-009).

Decision rules (v0.1):
  - No citable source / no citation reaching verified or partial  -> BLOCKED ("unverified")
  - Any quotation that fails C5                                    -> BLOCKED
  - load_bearing and best citation only PARTIAL                    -> BLOCKED (PARTIAL = UNSUPPORTED for load-bearing)
  - load_bearing number with < 2 independent upstreams             -> BLOCKED ("single-upstream")
  - non-load-bearing fact with PARTIAL only, no second VERIFIED    -> BLOCKED
  - number claim with no confidence label                          -> BLOCKED (export lint, C9)
  - C2a (build_profile="client", the default): a citation whose only support
    is an ATTACHED source with reconciliation != MATCH does not count. If no
    other support remains the claim is BLOCKED with the reason "awaiting
    publisher reconciliation" and goes to the gap register. In an "internal"
    (draft) build the labelled path remains: the claim is released and the
    label travels with it.
Blocked claims never carry a warning into output; they go to the gap register.

Change log: 0.4 — C2a build_profile added (red-team review 2026-10-25, Blocker 2 / §2.6).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from .models import (
    ATTACHED_LABEL_PREFIX, Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, GapEntry, UpstreamPair,
)

MIN_INDEPENDENT_UPSTREAMS = 2

BuildProfile = Literal["client", "internal"]
BUILD_PROFILES: tuple[str, ...] = ("client", "internal")
DEFAULT_BUILD_PROFILE: BuildProfile = "client"
#: gap-register reason prefix for C2a withholdings (spec C2a; the deck template lists them under this heading)
AWAITING_RECONCILIATION = "awaiting publisher reconciliation"


def is_attached_unreconciled(c: Citation) -> bool:
    """True when the citation rests on an ATTACHED source whose publisher hash is not MATCH."""
    return any(l.startswith(ATTACHED_LABEL_PREFIX) for l in c.labels)


def decide(
    claim: Claim,
    citations: list[Citation],
    independent_upstreams: int = 0,
    upstream_pairs: Optional[list[UpstreamPair]] = None,
    build_profile: BuildProfile = DEFAULT_BUILD_PROFILE,
) -> ClaimDecision:
    if build_profile not in BUILD_PROFILES:
        raise ValueError(f"build_profile must be one of {BUILD_PROFILES}, got {build_profile!r}")
    reasons: list[str] = []
    mine = [c for c in citations if c.claim_id == claim.id]
    # C2a: in a client-facing build, support that rests on an unreconciled attachment is set aside
    held: list[Citation] = []
    if build_profile == "client":
        held = [c for c in mine if c.status in (CitationStatus.verified, CitationStatus.partial) and is_attached_unreconciled(c)]
    verified = [c for c in mine if c.status == CitationStatus.verified and c not in held]
    partial = [c for c in mine if c.status == CitationStatus.partial and c not in held]
    blocked_cites = [c for c in mine if c.status == CitationStatus.blocked]

    if not mine:
        reasons.append("no citation supplied (C3: claims with no citation are UNSUPPORTED)")
    if held and not verified and not partial:
        urls = ", ".join(sorted({c.source_url for c in held}))
        reasons.append(f"{AWAITING_RECONCILIATION}: supporting source(s) {urls} are ATTACHED with reconciliation != MATCH; "
                       "a client-facing build treats them as BLOCKED until `plumbverify reconcile` returns MATCH (C2a)")
    elif claim.kind == ClaimKind.quote:
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
    # labels (e.g. "attached; publisher hash unreconciled") travel with the supporting citations into the output
    labels: list[str] = []
    for c in (verified or partial):
        for l in c.labels:
            if l not in labels:
                labels.append(l)
    return ClaimDecision(
        claim_id=claim.id, status=status, blocked=blocked, load_bearing=claim.load_bearing,
        reasons=reasons, labels=labels, independent_upstreams=independent_upstreams, upstream_pairs=upstream_pairs or [],
        withheld_awaiting_reconciliation=bool(held and blocked and any(r.startswith(AWAITING_RECONCILIATION) for r in reasons)),
    )


@dataclass
class BuildGate:
    passed: bool
    blocked_count: int
    gap_register: list[GapEntry]
    #: count of BLOCKED claims whose only defect is C2a (awaiting publisher reconciliation)
    withheld_awaiting_reconciliation: int = 0

    def presentation(self, total: int) -> str:
        """Run-presentation sentence (red-team review §5.4): never 'Build: FAIL'."""
        return present_outcome(total, self.blocked_count, self.withheld_awaiting_reconciliation)


def present_outcome(total: int, blocked: int, awaiting_reconciliation: int = 0) -> str:
    """'Released: N claims. Withheld: M claims (listed).' — the only sentence a
    prospect sees about a run's outcome (red-team review §5.4)."""
    released = max(total - blocked, 0)
    s = f"Released: {released} claim{'s' if released != 1 else ''}. Withheld: {blocked} claim{'s' if blocked != 1 else ''}"
    if blocked:
        s += " (listed in the gap register"
        if awaiting_reconciliation:
            s += f"; {awaiting_reconciliation} {AWAITING_RECONCILIATION}"
        s += ")"
    return s + "."


def build_gate(claims: list[Claim], decisions: list[ClaimDecision]) -> BuildGate:
    """Deliverable build fails if any claim is BLOCKED (spec C11, T-09)."""
    by_id = {c.id: c for c in claims}
    gaps = [GapEntry(claim_id=d.claim_id, text=by_id[d.claim_id].text if d.claim_id in by_id else "", reasons=d.reasons)
            for d in decisions if d.blocked]
    return BuildGate(passed=not gaps, blocked_count=len(gaps), gap_register=gaps,
                     withheld_awaiting_reconciliation=sum(1 for d in decisions if d.withheld_awaiting_reconciliation))


def released_claims(claims: list[Claim], decisions: list[ClaimDecision]) -> list[Claim]:
    """Claims allowed into client-facing output: everything not blocked. No
    'unverified' footnotes exist by construction."""
    blocked = {d.claim_id for d in decisions if d.blocked}
    return [c for c in claims if c.id not in blocked]
