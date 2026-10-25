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

Change log: 2026-10-25 — `build_profile` pass-through to plumbverify (spec C2a,
red-team review Blocker 2) and signals.md outcome wording "Released: N claims.
Withheld: M claims (listed)" in place of "build FAIL" (review §5.4 / Blocker 6).
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
from plumbverify.policy import BUILD_PROFILES, DEFAULT_BUILD_PROFILE, present_outcome

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
    attached_documents: list[dict] = field(default_factory=list)  # per attached document: hash, supplier, reconciliation status

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
                ctx: Optional[RunContext] = None, build_profile: str = DEFAULT_BUILD_PROFILE) -> RunOutcome:
    """`build_profile` (spec C2a): "client" (default) withholds every claim whose only support is an
    attached document with reconciliation != MATCH; "internal" releases them with the attached label."""
    if build_profile not in BUILD_PROFILES:
        raise ValueError(f"build_profile must be one of {BUILD_PROFILES}, got {build_profile!r}")
    ctx = ctx or RunContext.build(subject, out_dir, data_dir, fixtures=fixtures, cap=cap, as_of=as_of, offline=offline)
    out_dir = ctx.out_dir
    ctx.log_call("orchestrator", "run_start", subject.slug, "ok", fixtures=fixtures, cap=cap, modules=modules or MODULE_ORDER,
                 build_profile=build_profile)
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
    verifier = Verifier(fetcher=ctx.fetcher, store=ctx.store, log=ctx.log, tier_rules=ctx.tier_rules, region=ctx.region,
                        build_profile=build_profile)
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
                         report=report, gaps=gaps, escalations=[r.module for r in results if r.escalated],
                         attached_documents=_attached_documents(ctx, report))
    _write_outputs(ctx, outcome)
    ctx.log_call("orchestrator", "run_end", subject.slug, "PASS" if report.build_pass else "FAIL", claims=len(claims),
                 blocked=report.metrics.get("blocked_claims"), signals=len(signals))
    return outcome


def _attached_documents(ctx: RunContext, report) -> list[dict]:
    """Attached documents in the run's evidence store with their reconciliation
    status and how many released claims rest on each (plumbverify 0.3)."""
    rows = ctx.attached_documents()
    if not rows:
        return rows
    blocked = {d.claim_id for d in report.decisions if d.blocked}
    for r in rows:
        cites = [c for c in report.citations if c.source_url == r["url"]]
        r["claims_citing"] = len({c.claim_id for c in cites})
        r["claims_released"] = len({c.claim_id for c in cites if c.claim_id not in blocked})
        r["claims_blocked"] = len({c.claim_id for c in cites if c.claim_id in blocked})
    return rows


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
        "build_profile": o.report.build_profile,
        "outcome": present_outcome(len(o.claims), o.report.metrics.get("blocked_claims", 0),
                                   o.report.metrics.get("withheld_awaiting_reconciliation", 0)),
        "modules": [{"module": r.module, "claims": len(r.claims), "signals": len(r.signals), "gaps": len(r.gaps), "tool_calls": r.tool_calls,
                     "restarts": r.restarts, "escalated": r.escalated, "data_available": r.data_available, "detail": r.detail} for r in o.modules],
        "signals": [s.model_dump(mode="json") for s in o.signals],
        "verification": o.report.model_dump(mode="json"),
        "released_claim_ids": [c.id for c in o.released_claims],
        "gap_register": {"blocked_claims": [g.model_dump(mode="json") for g in o.report.gap_register],
                         "module_gaps": [g.model_dump(mode="json") for g in o.gaps],
                         "verify_items": o.subject.all_verify_items()},
        "escalations": o.escalations,
        "attached_documents": o.attached_documents,
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
    # Run-presentation format (red-team review 2026-10-25 §5.4): lead with what was released, list what was withheld
    # and why, never "Build: FAIL". The PASS/FAIL gate state lives in report.json for the operator.
    L.append("## Run outcome")
    L.append("")
    L.append(f"**{present_outcome(len(o.claims), m.get('blocked_claims', 0), m.get('withheld_awaiting_reconciliation', 0))}** "
             f"Build profile: `{o.report.build_profile}`"
             + (" (client-facing: claims resting on an unreconciled attachment are withheld, spec C2a)." if o.report.build_profile == "client"
                else " (internal draft: claims resting on an unreconciled attachment are released with the attached label; not for client use)."))
    L.append("")
    if o.report.gap_register:
        L.append("Removed, not footnoted:")
        L.append("")
        L.append("| Claim | Source attempted | Reason | What would resolve it |")
        L.append("|---|---|---|---|")
        by_id = {c.id: c for c in o.claims}
        for g in o.report.gap_register:
            c = by_id.get(g.claim_id)
            srcs = "; ".join(getattr(c, "sources", []) or []) if c else ""
            srcs = srcs if len(srcs) < 90 else srcs[:87] + "..."
            reason = "; ".join(g.reasons).replace("|", "/")
            fix = _what_would_resolve(reason)
            L.append(f"| {g.claim_id} | {srcs} | {reason[:160]} | {fix} |")
        L.append("")
    L.append(f"Footer: run `{o.run_id}` · citation resolution {m.get('citation_resolution_rate')} · quotation pass rate {m.get('quotation_pass_rate')} · "
             f"two-upstream coverage {m.get('two_upstream_coverage')} · AI/farm pages cited {m.get('aigen_or_farm_cited')} · "
             f"reviewer human-read: not yet recorded.")
    if o.attached_documents:
        L.append("")
        L.extend(attached_documents_markdown(o))
    return "\n".join(L)


def _what_would_resolve(reason: str) -> str:
    """Gap-register column 'what would resolve it' (review §5.4 item 3), keyed on the blocking reason."""
    r = reason.lower()
    if "awaiting publisher reconciliation" in r:
        return "run `plumbverify reconcile` with egress; MATCH releases the claim"
    if "mismatch" in r:
        return "obtain the published copy or correct the declared URL; re-ingest"
    if "dead" in r or "likely_hallucinated" in r or "not citable" in r:
        return "re-run from a machine with egress, or attach the document under its publisher URL"
    if "single-upstream" in r:
        return "a second independent upstream (original filing or dataset), or re-label non-load-bearing with rationale"
    if "quotation" in r or "c5" in r:
        return "re-extract the quotation from the stored text; multi-column pages need layout-aware extraction"
    if "confidence label" in r:
        return "set the C9 confidence label on the claim"
    if "no citation" in r:
        return "cite a fetchable source"
    return "see reason; reviewer to decide"


def attached_documents_markdown(o: RunOutcome, heading: str = "## Attached documents (reconciliation status)") -> list[str]:
    """Per attached document: which subject document it maps to, hash, supplier and
    whether the publisher's bytes have been reconciled. Attached evidence is weaker
    than fetched evidence until reconciliation returns MATCH; the signals that rest
    on it inherit the label."""
    L = [heading, "",
         "A person attached these documents instead of the pipeline fetching them. Each is stored and cited under the declared "
         "publisher URL. `pending` / `UNAVAILABLE` = the publisher hash is unreconciled: in a **client** build every claim resting only on "
         "the document is withheld (gap register: awaiting publisher reconciliation, spec C2a); in an **internal** build it is released "
         "with the label `attached; publisher hash unreconciled`. `MATCH` = the publisher's bytes are identical and the document now "
         "counts as fetched; `MISMATCH` = the attachment is not the published document and every claim citing it is BLOCKED in any profile. "
         "Run `plumbverify reconcile --store <out>/<slug>/evidence` when egress is available.", "",
         "| Document | Declared URL | File | Supplied by | Supplied at | SHA-256 (attached) | State | Reconciliation | SHA-256 (publisher) | Claims released / blocked |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in o.attached_documents:
        url = r["url"] if len(r["url"]) < 90 else r["url"][:87] + "..."
        rec = r.get("reconciliation") or "pending"
        L.append(f"| {r.get('document_key') or '—'} | {url} | {r.get('original_filename') or ''} | {r.get('supplied_by') or '—'} | "
                 f"{(r.get('supplied_at') or '')[:16]} | `{r['sha256']}` | {r['state']} | {rec} | "
                 f"{('`' + r['reconciled_sha256'] + '`') if r.get('reconciled_sha256') else '—'} | "
                 f"{r.get('claims_released', 0)} / {r.get('claims_blocked', 0)} |")
    return L


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
    if o.attached_documents:
        unrec = [r for r in o.attached_documents if r["state"] == "ATTACHED"]
        L.append("")
        L.extend(attached_documents_markdown(o, heading=f"## 5. Attached documents awaiting publisher reconciliation ({len(unrec)} of {len(o.attached_documents)})"))
        for r in unrec:
            if r.get("reconciliation") == "MISMATCH":
                L.append(f"- **{r.get('document_key') or r['url']}: MISMATCH** — the attached file is not the document at the declared URL; "
                         f"{r.get('claims_blocked', 0)} claim(s) BLOCKED. Obtain the published copy or correct the declared URL and re-ingest.")
            elif o.report.build_profile == "client":
                L.append(f"- {r.get('document_key') or r['url']}: publisher hash unreconciled; {r.get('claims_blocked', 0)} claim(s) withheld, "
                         f"awaiting publisher reconciliation (C2a), until `plumbverify reconcile` returns MATCH.")
            else:
                L.append(f"- {r.get('document_key') or r['url']}: publisher hash unreconciled; {r.get('claims_released', 0)} released claim(s) carry the attached label "
                         f"until `plumbverify reconcile` returns MATCH (internal build; not for client use).")
    return "\n".join(L) + "\n"
