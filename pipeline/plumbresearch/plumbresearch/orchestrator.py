"""Runs every Phase 1 module for a subject under the C10 cap, verifies every
claim through plumbverify, and writes the outputs:

    out/<slug>/claims.json       every ResearchClaim with provenance (plumbverify input shape)
    out/<slug>/report.json       module summaries, VerificationReport, signals, gap register, budget stats
    out/<slug>/peer-set.md       peer-set protocol exhibit
    out/<slug>/signals.md        proxy-signal table: value, source, tier, confidence, status
    out/<slug>/gap-register.md   blocked claims + module data gaps + [VERIFY] items
    out/<slug>/kpi-percentiles.md (financials exhibit)
    out/<slug>/inference.jsonl   hash-chained log (plumbverify.log), checkpoints/, evidence/

Module order matters once: the annual-report module's competitor names feed
the peer-set funnel. There is no other cross-module context (C10: "no
cross-module context carry other than the structured claim store").
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from plumbverify.log import HashChainLog
from plumbverify.models import CitationStatus
from plumbverify.pipeline import Verifier

from .context import DEFAULT_CAP, RunContext, ToolCapExceeded
from .models import Gap, ModuleResult, ResearchClaim, Signal
from .modules import annual_report, earnings_calls, financials, patents, peerset, postings
from .subject import Subject

MODULE_ORDER = ["annual-report", "peer-set", "postings", "earnings-calls", "patents", "financials"]


@dataclass
class RunOutcome:
    subject: Subject
    run_id: str
    out_dir: Path
    modules: list[ModuleResult]
    claims: list[ResearchClaim]
    signals: list[Signal]
    report: object  # plumbverify VerificationReport
    gaps: list[Gap]
    escalations: list[str] = field(default_factory=list)

    @property
    def released_claims(self) -> list[ResearchClaim]:
        blocked = {d.claim_id for d in self.report.decisions if d.blocked}
        return [c for c in self.claims if c.id not in blocked]


def run_module_with_cap(ctx: RunContext, name: str, fn: Callable[[RunContext], ModuleResult]) -> ModuleResult:
    """C10: terminate at cap, restart once from checkpoint, escalate on the second hit."""
    hits = 0
    while True:
        ctx.reset_budget(name)
        try:
            res = fn(ctx)
            res.restarts = hits
            res.tool_calls = ctx.budget(name).calls
            ctx.log_call(name, "module_done", name, "ok", tool_calls=res.tool_calls, restarts=hits, claims=len(res.claims))
            return res
        except ToolCapExceeded as e:
            hits += 1
            ctx.log_call(name, "tool_cap", name, "CAP_HIT", cap=e.cap, calls=e.calls, hit=hits)
            if hits >= 2:
                ctx.log_call(name, "escalation", name, "ESCALATED", detail="cap hit twice; escalated to research lead (C10)")
                return ModuleResult(module=name, subject_slug=ctx.subject.slug, escalated=True, restarts=hits, tool_calls=e.calls,
                                    data_available=False,
                                    gaps=[Gap(module=name, topic="tool-call cap", detail=f"module hit the {e.cap}-call cap twice; run escalated to the research lead "
                                              "(spec C10). Partial state is in checkpoints/ and is NOT released.")])
            # loop: restart from checkpoint with a fresh budget


def _module_fns(ctx: RunContext, competitors_box: dict) -> dict[str, Callable[[RunContext], ModuleResult]]:
    s = ctx.subject
    return {
        "annual-report": lambda c: annual_report.run(s, c.store, c.log, c),
        "peer-set": lambda c: peerset.run(s, c.store, c.log, c, extra_competitors=competitors_box.get("names", [])),
        "postings": lambda c: postings.run(s, c.store, c.log, c),
        "earnings-calls": lambda c: earnings_calls.run(s, c.store, c.log, c),
        "patents": lambda c: patents.run(s, c.store, c.log, c),
        "financials": lambda c: financials.run(s, c.store, c.log, c),
    }


def run_subject(subject: Subject, out_dir: str | Path, data_dir: str | Path, *, fixtures: bool = False, cap: int = DEFAULT_CAP,
                modules: Optional[list[str]] = None, as_of: Optional[date] = None, offline: bool = False,
                ctx: Optional[RunContext] = None) -> RunOutcome:
    ctx = ctx or RunContext.build(subject, out_dir, data_dir, fixtures=fixtures, cap=cap, as_of=as_of, offline=offline)
    out_dir = ctx.out_dir
    ctx.log_call("orchestrator", "run_start", subject.slug, "ok", fixtures=fixtures, cap=cap, modules=modules or MODULE_ORDER)
    competitors_box: dict = {}
    fns = _module_fns(ctx, competitors_box)
    results: list[ModuleResult] = []
    for name in (modules or MODULE_ORDER):
        res = run_module_with_cap(ctx, name, fns[name])
        results.append(res)
        if name == "annual-report":
            names = []
            for d in res.detail.get("documents", []):
                for c in (d.get("competitors") or []):
                    if c["name"] not in names:
                        names.append(c["name"])
            competitors_box["names"] = names
    claims = [c for r in results for c in r.claims]
    signals = [s for r in results for s in r.signals]
    gaps = [g for r in results for g in r.gaps]

    # --- verification (S2–S5) over the structured claim store ---------------
    verifier = Verifier(fetcher=ctx.fetcher, store=ctx.store, log=ctx.log, tier_rules=ctx.tier_rules, region=ctx.region)
    report = verifier.run(list(claims), run_id=ctx.run_id)
    decisions = {d.claim_id: d for d in report.decisions}
    for s in signals:
        if s.status == "not-available":
            continue
        ev = s.evidence_claim_ids
        if not ev:
            s.status = "computed" if s.value is not None else "not-available"
            continue
        rel = [i for i in ev if i in decisions and not decisions[i].blocked]
        s.status = "released" if len(rel) == len(ev) else ("blocked" if not rel else f"partial ({len(rel)}/{len(ev)} evidence released)")
    outcome = RunOutcome(subject=subject, run_id=ctx.run_id, out_dir=out_dir, modules=results, claims=claims, signals=signals,
                         report=report, gaps=gaps, escalations=[r.module for r in results if r.escalated])
    _write_outputs(ctx, outcome)
    ctx.log_call("orchestrator", "run_end", subject.slug, "PASS" if report.build_pass else "FAIL", claims=len(claims),
                 blocked=report.metrics.get("blocked_claims"), signals=len(signals))
    return outcome


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------
def _write_outputs(ctx: RunContext, o: RunOutcome) -> None:
    out = o.out_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "claims.json").write_text(json.dumps({"subject": o.subject.slug, "run_id": o.run_id,
                                                  "claims": [c.model_dump(mode="json") for c in o.claims]}, indent=2, ensure_ascii=False), encoding="utf-8")
    report = {
        "subject": o.subject.model_dump(mode="json"),
        "run_id": o.run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cap": ctx.cap,
        "fixtures": ctx.fixtures,
        "modules": [{"module": r.module, "claims": len(r.claims), "signals": len(r.signals), "gaps": len(r.gaps), "tool_calls": r.tool_calls,
                     "restarts": r.restarts, "escalated": r.escalated, "data_available": r.data_available, "detail": r.detail} for r in o.modules],
        "signals": [s.model_dump(mode="json") for s in o.signals],
        "verification": o.report.model_dump(mode="json"),
        "released_claim_ids": [c.id for c in o.released_claims],
        "gap_register": {"blocked_claims": [g.model_dump(mode="json") for g in o.report.gap_register],
                         "module_gaps": [g.model_dump(mode="json") for g in o.gaps],
                         "verify_items": o.subject.all_verify_items()},
        "escalations": o.escalations,
        "log": str(ctx.log.path) if ctx.log else None,
        "log_chain_ok": ctx.log.verify().ok if ctx.log else None,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    for r in o.modules:
        for name, md in r.exhibits.items():
            (out / name).write_text(md, encoding="utf-8")
    if not (out / "peer-set.md").exists():
        (out / "peer-set.md").write_text(f"# Peer-set protocol exhibit — {o.subject.name}\n\nPeer-set module did not run.\n", encoding="utf-8")
    (out / "signals.md").write_text(signals_markdown(o), encoding="utf-8")
    (out / "gap-register.md").write_text(gap_register_markdown(o), encoding="utf-8")


def _fmt_val(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.2f}".rstrip("0").rstrip(".") if abs(v) < 1e6 else f"{v:,.0f}"
    return str(v)


def signals_markdown(o: RunOutcome) -> str:
    L = [f"# Outside-in proxy signals — {o.subject.name}", "",
         f"Run {o.run_id}. Status is set from plumbverify's verdict on each signal's evidence claims: `released` = all evidence claims released; "
         "`partial` = some blocked; `blocked` = none released; `computed` = derived figure with no evidence claim of its own; `not-available` = no data. "
         "Proxies corroborate only and never lift an item above level 3 (instrument §5.4). Capability scores from these are an "
         "**outside-in pre-score, self-report absent**, not a maturity result.", "",
         "| Signal | Instrument items | Value | Unit | Source | Tier | Confidence | Status | Note |", "|---|---|---|---|---|---|---|---|---|"]
    for s in o.signals:
        src = s.source if len(s.source) < 90 else s.source[:87] + "..."
        L.append(f"| {s.name} | {', '.join(s.instrument_items)} | {_fmt_val(s.value)} | {s.unit or ''} | {src} | {s.tier.value if s.tier else '—'} | "
                 f"{s.confidence_label.value} | {s.status} | {(s.note or '').replace('|', '/')} |")
    L.append("")
    L.append("## Module runs (C10)")
    L.append("")
    L.append("| Module | Tool calls | Restarts | Escalated | Claims | Signals | Data available |")
    L.append("|---|---|---|---|---|---|---|")
    for r in o.modules:
        L.append(f"| {r.module} | {r.tool_calls} | {r.restarts} | {'yes' if r.escalated else 'no'} | {len(r.claims)} | {len(r.signals)} | {'yes' if r.data_available else 'no'} |")
    L.append("")
    m = o.report.metrics
    L.append(f"Verification: {m.get('claims')} claims, {m.get('blocked_claims')} BLOCKED, build {'PASS' if o.report.build_pass else 'FAIL'}; "
             f"citation resolution {m.get('citation_resolution_rate')}, quotation pass rate {m.get('quotation_pass_rate')}, "
             f"two-upstream coverage {m.get('two_upstream_coverage')}, AI/farm pages cited {m.get('aigen_or_farm_cited')}.")
    return "\n".join(L)


def gap_register_markdown(o: RunOutcome) -> str:
    by_id = {c.id: c for c in o.claims}
    L = [f"# Gap register — {o.subject.name}", "",
         "Blocked claims never appear in client-facing material; they are disclosed here (spec C11). Module gaps are data the sprint could not obtain. "
         "[VERIFY] items are carried from the candidate screen and the subject file.", ""]
    L.append(f"## 1. Blocked claims ({len(o.report.gap_register)})")
    L.append("")
    if o.report.gap_register:
        L.append("| Claim | Module | Text | Reasons |")
        L.append("|---|---|---|---|")
        for g in o.report.gap_register:
            c = by_id.get(g.claim_id)
            txt = (g.text[:100] + "...") if len(g.text) > 100 else g.text
            L.append(f"| {g.claim_id} | {c.module if c else ''} | {txt.replace('|', '/')} | {'; '.join(g.reasons).replace('|', '/')} |")
    else:
        L.append("None.")
    L.append("")
    L.append(f"## 2. Module data gaps ({len(o.gaps)})")
    L.append("")
    if o.gaps:
        L.append("| Module | Topic | Detail | Items | [VERIFY] |")
        L.append("|---|---|---|---|---|")
        for g in o.gaps:
            L.append(f"| {g.module} | {g.topic} | {g.detail.replace('|', '/')} | {', '.join(g.instrument_items)} | {'yes' if g.verify_flag else ''} |")
    else:
        L.append("None.")
    L.append("")
    items = o.subject.all_verify_items()
    L.append(f"## 3. [VERIFY] items from the subject file ({len(items)})")
    L.append("")
    for it in items:
        L.append(f"- {it}")
    if o.escalations:
        L.append("")
        L.append("## 4. Escalations (C10)")
        L.append("")
        for e in o.escalations:
            L.append(f"- {e}: hit the tool-call cap twice; escalated to the research lead")
    return "\n".join(L) + "\n"
