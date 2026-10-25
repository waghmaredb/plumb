"""Reviewer-facing Markdown rendering of a VerificationReport (spec C16, section 6.2).

Two parts:
  1. the claim table (claim, status, score, tier, independent upstreams, reasons);
  2. the 30-claim sampling worksheet skeleton the independent reviewer fills
     in under protocol P1-P8. The sample is drawn deterministically from a
     recorded random seed and stratified per P3:
       (a) every load-bearing number and every quotation in the executive summary;
       (b) stratified fill from remaining load-bearing claims, >= 2 per module;
       (c) >= 5 non-load-bearing qualitative claims at random;
       (d) random load-bearing top-up to the minimum sample size.
     The frame is RELEASED claims only (P2): blocked claims are listed for
     context but never sampled.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Optional

from .models import Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, Source, VerificationReport

SAMPLE_MIN = 30
MIN_PER_MODULE = 2
MIN_QUALITATIVE = 5
_EXEC_MODULE = re.compile(r"exec(utive)?[-_ ]?summary|^exec$|^executive$", re.I)


@dataclass
class SampledClaim:
    claim: Claim
    stratum: str  # "a" | "b" | "c" | "d" per P3; "e" = non-load-bearing fill when load-bearing claims run out
    decision: Optional[ClaimDecision] = None


@dataclass
class SamplePlan:
    seed: int
    frame_size: int
    sampled: list[SampledClaim] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    shortfall: int = 0  # > 0 when the released frame is smaller than SAMPLE_MIN

    @property
    def ids(self) -> list[str]:
        return [s.claim.id for s in self.sampled]


def is_exec_module(module: Optional[str]) -> bool:
    return bool(module and _EXEC_MODULE.search(module))


def build_sample(report: VerificationReport, seed: int, sample_min: int = SAMPLE_MIN,
                 min_per_module: int = MIN_PER_MODULE, min_qualitative: int = MIN_QUALITATIVE) -> SamplePlan:
    """Deterministic stratified sample per spec 6.2 P3. Same report + seed = same sample."""
    rng = random.Random(seed)
    decisions = {d.claim_id: d for d in report.decisions}
    blocked = {cid for cid, d in decisions.items() if d.blocked}
    frame = [c for c in report.claims if c.id not in blocked]  # P2: RELEASED only
    plan = SamplePlan(seed=seed, frame_size=len(frame))
    chosen: dict[str, str] = {}

    def take(claim: Claim, stratum: str) -> None:
        if claim.id not in chosen:
            chosen[claim.id] = stratum

    # (a) all load-bearing numbers and all quotations in the executive summary
    for c in frame:
        if is_exec_module(c.module) and ((c.kind == ClaimKind.number and c.load_bearing) or c.kind == ClaimKind.quote):
            take(c, "a")
    # (b) stratified fill: remaining load-bearing claims, >= 2 per module
    remaining_lb = [c for c in frame if c.load_bearing and c.id not in chosen]
    by_module: dict[str, list[Claim]] = {}
    for c in remaining_lb:
        by_module.setdefault(c.module or "(no module)", []).append(c)
    for module in sorted(by_module):
        pool = sorted(by_module[module], key=lambda c: c.id)
        rng.shuffle(pool)
        for c in pool[:min_per_module]:
            take(c, "b")
    # (c) at least 5 non-load-bearing qualitative claims at random
    qual = sorted([c for c in frame if not c.load_bearing and c.kind != ClaimKind.number and c.id not in chosen],
                  key=lambda c: c.id)
    rng.shuffle(qual)
    for c in qual[:min_qualitative]:
        take(c, "c")
    # (d) random load-bearing top-up until the minimum
    topup = sorted([c for c in frame if c.load_bearing and c.id not in chosen], key=lambda c: c.id)
    rng.shuffle(topup)
    for c in topup:
        if len(chosen) >= sample_min:
            break
        take(c, "d")
    if len(chosen) < sample_min:  # load-bearing frame exhausted: fill with released non-load-bearing claims (e)
        rest = sorted([c for c in frame if c.id not in chosen], key=lambda c: c.id)
        rng.shuffle(rest)
        for c in rest:
            if len(chosen) >= sample_min:
                break
            take(c, "e")
    order = {c.id: i for i, c in enumerate(report.claims)}
    plan.sampled = sorted(
        [SampledClaim(claim=c, stratum=chosen[c.id], decision=decisions.get(c.id)) for c in frame if c.id in chosen],
        key=lambda s: (s.stratum, order[s.claim.id]),
    )
    plan.counts = {k: sum(1 for s in plan.sampled if s.stratum == k) for k in "abcde"}
    plan.shortfall = max(0, sample_min - len(plan.sampled))
    return plan


# --------------------------------------------------------------------------
# Markdown rendering
# --------------------------------------------------------------------------
def _esc(s: Optional[str], limit: int = 0) -> str:
    t = (s or "").replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(t) > limit:
        t = t[: limit - 1].rstrip() + "…"
    return t


def _best_citation(cites: list[Citation]) -> Optional[Citation]:
    rank = {CitationStatus.verified: 0, CitationStatus.partial: 1, CitationStatus.unverified: 2, CitationStatus.blocked: 3}
    return min(cites, key=lambda c: (rank[c.status], -c.match_score)) if cites else None


def _pct(x: float | int | None) -> str:
    return "-" if x is None else f"{100 * float(x):.1f}%"


def render_markdown(report: VerificationReport, seed: Optional[int] = None, sample_min: int = SAMPLE_MIN) -> str:
    seed = int(seed) if seed is not None else random.SystemRandom().randrange(1, 2**31)
    plan = build_sample(report, seed, sample_min)
    sources: dict[str, Source] = {s.url: s for s in report.sources}
    cites_by_claim: dict[str, list[Citation]] = {}
    for c in report.citations:
        cites_by_claim.setdefault(c.claim_id, []).append(c)
    decisions = {d.claim_id: d for d in report.decisions}
    m = report.metrics

    out: list[str] = []
    out.append(f"# Verification report {report.run_id}")
    out.append("")
    out.append(f"- Spec: {report.spec_version}")
    out.append(f"- Generated: {report.generated_at.isoformat()}")
    out.append(f"- Build gate: **{'PASS' if report.build_pass else 'FAIL'}** "
               f"({m.get('blocked_claims', 0)} of {m.get('claims', len(report.claims))} claims BLOCKED)")
    out.append(f"- Citation resolution rate: {_pct(m.get('citation_resolution_rate'))} (G1 target 100%)")
    out.append(f"- Quotation exact-match: {_pct(m.get('quotation_pass_rate'))} (G1 target 100%)")
    out.append(f"- Two-upstream coverage: {_pct(m.get('two_upstream_coverage'))} (G1 target >= 90%)")
    out.append(f"- AI-generated or farm pages cited: {m.get('aigen_or_farm_cited', 0)} (G1 target 0)")
    out.append("")

    out.append("## Claims")
    out.append("")
    out.append("| # | Claim | Module | Kind | LB | Status | Score | Tier | Indep. upstreams | Source (locator) | Reasons |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in report.claims:
        d = decisions.get(c.id)
        best = _best_citation(cites_by_claim.get(c.id, []))
        src = sources.get(best.source_url) if best else None
        status = d.status.value.upper() if d else "-"
        if d and d.blocked:
            status = "BLOCKED"
        score = f"{best.match_score:.2f}" if best else "-"
        tier = src.tier.value if src else "-"
        indep = str(d.independent_upstreams) if (d and c.kind == ClaimKind.number and c.load_bearing) else "n/a"
        reasons = "; ".join(d.reasons) if d and d.reasons else ""
        locator = best.locator if best else ""
        out.append(f"| {_esc(c.id)} | {_esc(c.text, 140)} | {_esc(c.module) or '-'} | {c.kind.value} | "
                   f"{'yes' if c.load_bearing else 'no'} | {status} | {score} | {tier} | {indep} | "
                   f"{_esc(locator, 120)} | {_esc(reasons, 240)} |")
    out.append("")

    if report.gap_register:
        out.append("## Gap register (BLOCKED, excluded from the deliverable)")
        out.append("")
        for g in report.gap_register:
            out.append(f"- **{_esc(g.claim_id)}** — {_esc(g.text, 160)}")
            for r in g.reasons:
                out.append(f"  - {_esc(r)}")
        out.append("")

    out.append("## Sources")
    out.append("")
    out.append("| URL | Final URL | Health | State | Tier | SHA-256 | Pages | Re-check after | Upstream candidates |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for s in report.sources:
        pages = ("needs OCR" if s.needs_ocr else (str(s.page_count) if s.page_count else "-"))
        cands = ", ".join(s.upstream_of) if s.upstream_of else ", ".join(s.upstream_candidates[:3])
        out.append(f"| {_esc(s.url, 90)} | {_esc(s.url_final or '', 90)} | {s.health_class.value} | {s.state.value} | "
                   f"{s.tier.value} | {_esc((s.sha256 or '')[:16])} | {pages} | "
                   f"{s.recheck_after.isoformat(timespec='minutes') if s.recheck_after else '-'} | {_esc(cands, 160)} |")
    out.append("")

    # ---- sampling worksheet (spec 6.2) ------------------------------------
    out.append(f"## Independent reviewer sampling worksheet (spec section 6.2, minimum {sample_min} claims)")
    out.append("")
    out.append(f"- Random seed: `{seed}` (record this; the sample is reproducible with `plumbverify report --seed {seed}`)")
    out.append(f"- Sample frame (P2): {plan.frame_size} RELEASED claims from the claim store; "
               f"{len(report.claims) - plan.frame_size} BLOCKED claims excluded")
    out.append(f"- Sample size: {len(plan.sampled)}"
               + (f" (**shortfall {plan.shortfall}**: fewer than {sample_min} released claims exist)" if plan.shortfall else ""))
    out.append(f"- Strata (P3): (a) exec-summary load-bearing numbers and quotations = {plan.counts.get('a', 0)}; "
               f"(b) stratified load-bearing fill, >= {MIN_PER_MODULE} per module = {plan.counts.get('b', 0)}; "
               f"(c) non-load-bearing qualitative >= {MIN_QUALITATIVE} = {plan.counts.get('c', 0)}; "
               f"(d) random load-bearing top-up = {plan.counts.get('d', 0)}"
               + (f"; (e) non-load-bearing fill after load-bearing frame exhausted = {plan.counts['e']}" if plan.counts.get('e') else ""))
    out.append("")
    out.append("### P1 Reviewer eligibility")
    out.append("")
    out.append("| Field | Entry |")
    out.append("|---|---|")
    out.append("| Reviewer name and role | |")
    out.append("| Did not run the agents (yes/no) | |")
    out.append("| Did not author module drafts (yes/no) | |")
    out.append("| Not the engagement lead (yes/no) | |")
    out.append("| Review start / end (timings, P8) | |")
    out.append("")
    out.append("### P4 Per-claim checks")
    out.append("")
    out.append("Support label: full / partial / none / broken. Partial is acceptable only for non-load-bearing qualitative claims.")
    out.append("")
    out.append("| # | Stratum | Claim | Kind | LB | Module | Cited source (locator) | Pipeline status | "
               "Live re-fetch resolves (Y/N) | Hash matches store (Y/N) | Support label | Quote visual exact (Y/N/n.a.) | "
               "Two termini distinct originals (Y/N/n.a.) | Tier shown / correct (Y/N) | Label shown / correct (Y/N) | "
               "AI-gen or farm indicators (Y/N) | Notes |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for sc in plan.sampled:
        c, d = sc.claim, sc.decision
        best = _best_citation(cites_by_claim.get(c.id, []))
        src = sources.get(best.source_url) if best else None
        tier = src.tier.value if src else "-"
        label = c.confidence_label.value if c.confidence_label else "-"
        quote_cell = "" if c.kind == ClaimKind.quote else "n.a."
        upstream_cell = "" if (c.kind == ClaimKind.number and c.load_bearing) else "n.a."
        out.append(f"| {_esc(c.id)} | {sc.stratum} | {_esc(c.text, 120)} | {c.kind.value} | {'yes' if c.load_bearing else 'no'} | "
                   f"{_esc(c.module) or '-'} | {_esc(best.locator if best else '', 100)} | "
                   f"{(d.status.value.upper() if d else '-')} | | | | {quote_cell} | {upstream_cell} | {tier} / | {label} / | | |")
    out.append("")
    out.append("### P5 C7 agreement sample")
    out.append("")
    out.append("Inspect 10 pages the pipeline rejected under C7 and 10 it accepted; record agreement.")
    out.append("")
    out.append("| # | URL | Pipeline decision (accepted/rejected) | Reviewer agrees (Y/N) | Notes |")
    out.append("|---|---|---|---|---|")
    rejected = [s for s in report.sources if s.state.value.startswith("REJECTED")][:10]
    accepted = [s for s in report.sources if s.citable][:10]
    for i, s in enumerate(rejected + accepted, start=1):
        out.append(f"| {i} | {_esc(s.url, 100)} | {'rejected' if s.state.value.startswith('REJECTED') else 'accepted'} | | |")
    for i in range(len(rejected) + len(accepted) + 1, 21):
        out.append(f"| {i} | | | | |")
    out.append("")
    out.append("### P6 Totals")
    out.append("")
    out.append("| Measure | Value | G1 threshold |")
    out.append("|---|---|---|")
    out.append("| Claims sampled | | >= 30 |")
    out.append("| Support labels: full / partial / none / broken | / / / | |")
    out.append("| Citation resolution rate (live re-fetch) | | 100% |")
    out.append("| Load-bearing full-support rate | | >= 95% |")
    out.append("| All-sampled full-or-partial rate | | >= 90% |")
    out.append("| Fabricated or non-resolving sources | | 0 |")
    out.append("| Quotation failures | | 0 |")
    out.append("| Two-upstream pass rate (load-bearing numbers) | | >= 90% |")
    out.append("| Tier errors / label errors | / | |")
    out.append("| C7 agreement (of 20) | | |")
    out.append("")
    out.append("### P7 Decision")
    out.append("")
    out.append("QA gate 3 may be signed only if: resolution 100%, load-bearing full support >= 95%, "
               "fabricated or non-resolving = 0, quotation failures = 0, no AI-generated or farm page cited. "
               "Any single failure returns the deck to the pipeline; after remediation re-sample the failed claims plus 10 fresh random claims.")
    out.append("")
    out.append("| QA gate 3 | Entry |")
    out.append("|---|---|")
    out.append("| Decision (SIGNED / RETURNED) | |")
    out.append("| Reviewer signature | |")
    out.append("| Date | |")
    out.append("| Reviewer time on deck (P8) | |")
    out.append("")
    return "\n".join(out)
