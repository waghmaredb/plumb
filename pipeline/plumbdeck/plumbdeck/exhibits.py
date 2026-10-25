"""Exhibit builders: turn run data / scorecard JSON into renderer-neutral blocks.

Rules every builder follows (ghost deck R6, R8):
  * a withheld claim's text and figures are never placed in a block; the cell or
    line reads "Withheld — see gap register G-n" instead;
  * numbers only come from released claims, released/computed signals with a
    tiered source, the scorecard JSON, or the build report;
  * the source line is built from the citations of the claims actually rendered.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .interlock import Interlock
from .model import Bar, Bars, Block, Bullets, Cells, Columns, Para, Table
from .runio import ATTACHED_LABEL, RunData
from .spec import SlideSpec

WITHHELD = "Withheld — see gap register"


def withheld_text(gap_ids: list[str]) -> str:
    return f"{WITHHELD} {', '.join(gap_ids)}" if gap_ids else WITHHELD


@dataclass
class Exhibit:
    blocks: list[Block] = field(default_factory=list)
    tokens: dict[str, Any] = field(default_factory=dict)
    withheld_tokens: set[str] = field(default_factory=set)
    bound: list[str] = field(default_factory=list)  # claim ids bound
    withheld: list[str] = field(default_factory=list)  # bound claim ids withheld
    source_line: Optional[str] = None
    all_withheld: bool = False
    requires: Optional[list[str]] = None  # set => becomes "requires engagement data" placeholder
    extra_signal_gaps: list[str] = field(default_factory=list)


# --------------------------------------------------------------- source lines
def _pages(ps: list[int]) -> str:
    ps = sorted(set(p for p in ps if p is not None))
    if not ps:
        return ""
    return f" p. {ps[0]}" if len(ps) == 1 else " pp. " + ", ".join(str(p) for p in ps)


def source_line(run: RunData, cids: list[str], extra_labels: list[str] | None = None,
                signal_refs: list[dict[str, Any]] | None = None) -> Optional[str]:
    """`Source: <T-tier> <doc>, <date>; confidence: <label>` from released claims' citations."""
    groups: dict[tuple, list] = {}
    labels: list[str] = []

    def add(tier, url, page, attached, label):
        if not tier or tier == "T5":
            return  # T5 is never a source of record; untiered sources cannot be cited
        s = run.sources.get(url)
        date = (s.date if s else None) or run.generated_date
        key = (tier, run.doc_label(url), date, attached)
        groups.setdefault(key, [])
        if page is not None:
            groups[key].append(page)
        if label and label not in labels:
            labels.append(label)

    for cid in cids:
        c = run.claims.get(cid)
        if not c or not c.released:
            continue
        attached = ATTACHED_LABEL in c.labels
        for url in c.sources[:1] or [None]:
            add(c.tier or (run.sources[url].tier if url in run.sources else None), url, c.page, attached, c.confidence_label)
    for sig in signal_refs or []:
        ev = [c for c in sig.get("evidence_claim_ids") or [] if c in run.claims and run.claims[c].released]
        pages = [run.claims[c].page for c in ev]
        attached = any(ATTACHED_LABEL in run.claims[c].labels for c in ev) or any(
            (run.sources.get(u) and (run.sources[u].state or "").upper() == "ATTACHED"
             and (run.sources[u].reconciliation or "").upper() != "MATCH")
            for u in sig.get("source_urls") or []
        )
        for url in sig.get("source_urls") or []:
            for p in pages or [None]:
                add(sig.get("tier"), url, p, attached, sig.get("confidence_label"))
    for l in extra_labels or []:
        if l not in labels:
            labels.append(l)
    if not groups:
        return None
    parts = []
    for (tier, doc, date, attached), pages in groups.items():
        att = f" ({ATTACHED_LABEL})" if attached else ""
        parts.append(f"{tier} {doc}{_pages(pages)}{att}, {date}")
    return "Source: " + "; ".join(parts) + f"; confidence: {' / '.join(labels) or 'unlabelled'}"


# ------------------------------------------------------------------ helpers
def _fmt(v: Any, unit: str | None = None) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        s = f"{v:,.2f}".rstrip("0").rstrip(".")
    else:
        s = f"{v:,}" if isinstance(v, int) else str(v)
    return f"{s} {unit}".strip() if unit else s


def _signal_has_citable_source(sig: dict[str, Any]) -> bool:
    return bool(sig.get("tier")) and sig.get("tier") != "T5" and bool(sig.get("source_urls"))


# ===================================================================== cover
def cover(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    strap = "AI-assisted, human-accountable" if il.passed else "AI-assisted draft — not yet approved by a named professional"
    blocks: list[Block] = [
        Para("Verified Enterprise AI Journey Assessment", "lead"),
        Para(f"{run.client_full} · board read-out · {ctx['date']}", "normal"),
        Para(f"Deliverable {ctx['deliverable_id']} · version {ctx['deliverable_version']} · run {run.run_id}", "muted"),
        Para(strap, "strong"),
    ]
    return Exhibit(blocks=blocks)


# ================================================================ disclosure
def disclosure(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    d = ctx["deliverable"]
    firm = d.get("firm") or "[Firm]"
    models = run.models_used()
    tools = list(d.get("tools") or [])
    tool_line = "; ".join(tools + ([f"run log models: {', '.join(models)}"] if models else [])) or "[model register entry required]"
    scope = d.get("scope_of_ai") or "research and source retrieval; rule-based claim verification"
    dates = sorted(s.fetched_at for s in run.sources.values() if s.fetched_at and any(
        s.url in run.claims[c].sources for c in run.released_ids))
    date_range = f"{dates[0][:10]} to {dates[-1][:10]}" if dates else "no released citations"
    tokens = {"n_released": il.released, "n_withheld": il.withheld}
    status_rows = [
        ["Build profile", str(il.build_profile or "not recorded")],
        ["Citation resolution rate", f"{il.resolution:g}" if il.resolution is not None else "not recorded"],
        ["Attachments reconciled MATCH", f"{il.attachments_total - il.attachments_unreconciled - il.attachments_mismatch} of {il.attachments_total}"],
        ["Run outcome", il.outcome_sentence],
        ["QA gate 3 sign-off", il.signoff_status if il.signoff_path else "absent"],
        ["Run ID", run.run_id],
    ]
    if il.passed:
        appr = il.approver or il.reviewer or "[approver]"
        appr_role = il.approver_role or ("" if il.approver else il.reviewer_role) or ""
        appr_txt = f"{appr}, {appr_role}" if appr_role else appr
        blocks: list[Block] = [
            Para(f"AI-assisted, human-accountable. This deliverable was prepared with the assistance of artificial-intelligence tools and reviewed, edited and approved by a named member of {firm}, who takes full editorial and professional responsibility for its content regardless of the use of generative AI.", "normal"),
            Para(f"Tools and models used. {tool_line}. Scope of AI assistance: {scope}. No AI tool executed actions in client systems; all external communications and writes were human-approved.", "normal"),
            Para(f"Verification performed. Every citation in this deliverable resolves to a source that was fetched and stored with a content hash on {date_range}. Every direct quotation has been string-matched against the stored source. Every load-bearing number has at least two independent upstream sources, or is marked as single-sourced. Claims that could not be verified were removed rather than flagged. {il.outcome_sentence} Citation resolution rate {il.resolution:g}; attachments reconciled {il.attachments_total} of {il.attachments_total}.", "normal"),
            Para(f"Limitations. AI tools may produce plausible but incorrect content. The verification steps above reduce but do not eliminate this risk. Information is current as at {ctx['date']}.", "muted"),
            Para(f"Reviewed and approved by: {appr_txt} on {il.signoff_date}. QA gate 3 reviewer: {il.reviewer}. Verification control owner: {d.get('verification_control_owner') or '[Name, role]'}. Corrections: {d.get('corrections_contact') or '[contact]'}. Deliverable {ctx['deliverable_id']}, version {ctx['deliverable_version']}.", "muted"),
        ]
    else:
        blocks = [
            Para(f"{il.outcome_sentence}", "lead"),
            Para("The verification statement is not rendered. It renders only when citation resolution = 1.0, every attachment is reconciled MATCH, the build profile is client and an independent QA gate 3 sign-off approves the run (ghost deck R8/R9).", "normal"),
            Para("Reasons: " + "; ".join(il.reasons) + ".", "strong"),
            Columns(
                left=[Table(["Build report field", "Value"], status_rows, widths=[1.2, 2.0], font_pt=10)],
                right=[
                    Para(f"AI-assisted draft. Prepared with the assistance of AI tools and not yet approved by a named member of {firm}. Tools and models: {tool_line}.", "muted"),
                    Para("Limitations. AI tools may produce plausible but incorrect content; withheld claims are listed in the gap register, not footnoted.", "muted"),
                ],
                ratio=0.55,
            ),
        ]
    return Exhibit(blocks=blocks, tokens=tokens, source_line=f"Source: PLUMB build report {run.run_id}, {run.generated_date}")


# =============================================================== peer funnel
def peer_funnel(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    sig = run.signal(ss.bind.get("signal", "").format(**ctx)) if ss.bind.get("signal") else run.signal_by_suffix(".peerset.core_n")
    size_claims = [c for c in run.claims if ".peer.size." in c]
    ev = list((sig or {}).get("evidence_claim_ids") or [])
    bound = list(dict.fromkeys(ev + size_claims))
    withheld = [c for c in bound if not run.claims[c].released]
    ex = Exhibit(bound=bound, withheld=withheld)
    if sig is None:
        ex.requires = ["peer-set module signal (core peer count)"]
        return ex
    sig_withheld = run.signal_withheld(sig)
    if sig_withheld:
        ex.withheld_tokens |= {"n_core", "n_exited", "n_secondary"}
        if all(c in withheld for c in bound):
            ex.all_withheld = True
            ex.extra_signal_gaps = run.gap_ids(bound)
            return ex
    det = sig.get("detail") or {}
    ex.tokens.update(n_core=sig.get("value"), n_exited=det.get("exited"), n_secondary=det.get("secondary"))
    size = run.subject.get("size") or {}
    band = det.get("band")
    funnel = [
        ["1 Seed", "industry codes + competitors named by the subject", run.subject.get("seed_description", "—")[:110]],
        ["4 Size band 0.3x–3x", size.get("metric", "size"), (f"band {band[0]:g}–{band[1]:g} US$bn" if band else "—")],
        ["5 Core / secondary", "5–12 core, labelled secondary", f"core {_fmt(sig.get('value'))}, secondary {_fmt(det.get('secondary'))}" if not sig_withheld else withheld_text(run.gap_ids(ev))],
        ["6 Exited", "survivorship control, never size-filtered", f"{_fmt(det.get('exited'))} events" if not sig_withheld else withheld_text(run.gap_ids(ev))],
    ]
    rows = []
    for i, p in enumerate(run.peers("core"), 1):
        cid = next((c for c in size_claims if run.peer_for_claim(c) is p), None)
        if cid and run.claims[cid].released:
            sz = run.claims[cid].text  # released: its text may render
        elif cid:
            sz = withheld_text([run.claims[cid].gap_id])
        else:
            sz = "not evidenced"
        rows.append([str(i), p.get("name", ""), (p.get("why") or "")[:80], sz])
    ex.blocks = [
        Table(["Step", "Rule", "Result"], funnel, widths=[1.0, 1.6, 2.4], font_pt=9),
        Table(["#", "Core peer", "Why included", "Size"], rows, widths=[0.3, 2.0, 2.4, 1.6], font_pt=9),
    ]
    ex.source_line = source_line(run, [c for c in bound if run.claims[c].released], signal_refs=[sig])
    return ex


# ============================================================== signals table
def signals_table(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    modules = ss.bind.get("modules")
    sigs = [s for s in run.signals if not modules or s.get("module") in modules]
    bound, withheld, rows, rendered = [], [], [], []
    for s in sigs:
        ev = list(s.get("evidence_claim_ids") or [])
        bound += ev
        status = s.get("status") or ""
        if run.signal_withheld(s):
            withheld += [c for c in ev if not run.claims.get(c) or not run.claims[c].released]
            val = withheld_text(run.gap_ids(ev))
        elif status == "not-available" or s.get("value") is None:
            val = "not evidenced (data gap)"
        elif not _signal_has_citable_source(s):
            val = "not evidenced (no tiered source)"
        else:
            unit = s.get("unit")
            val = f"{_fmt(s.get('value'))} ({unit})" if unit and unit.startswith("level") else _fmt(s.get("value"), unit)
            if status == "partial":
                val += f" (partial; {', '.join(run.gap_ids(ev))} withheld)"
            rendered.append(s)
        items = list(s.get("instrument_items") or [])
        if any(str(i).endswith("-context") for i in items):
            # parent-group context (run 4+): shown for context, never scored as instrument evidence
            items = [str(i).replace("-context", " context — not scored") for i in items]
            status = f"{status}; context only"
        rows.append([s.get("name", s.get("id")), ", ".join(items), val, status, s.get("tier") or "—"])
    ex = Exhibit(bound=list(dict.fromkeys(bound)), withheld=list(dict.fromkeys(withheld)))
    if not rendered:
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(ex.bound)
        return ex
    rub = next((s for s in sigs if str(s.get("id", "")).endswith(".rubric")), None)
    if rub and rub in rendered:
        ex.tokens["rubric_level"] = rub.get("value")
    else:
        ex.withheld_tokens.add("rubric_level")
    peer = run.signal_by_suffix(".peerset.core_n")
    if peer and not run.signal_withheld(peer) and peer.get("value") is not None:
        n = peer["value"]
        peer_line = (f"Peer rows: core peer n = {n}, below the instrument §5.5 minimum of 15 — ranked list only, no percentile; peer signal values require engagement data."
                     if n < 15 else f"Peer rows: core peer n = {n}; peer signal values require engagement data.")
    else:
        peer_line = "Peer rows: peer n not released (peer-set signal withheld); no ranking or percentile is shown. Peer signal values require engagement data."
    ex.blocks = [
        Table(["Signal", "Instrument items", "Value", "Status", "Tier"], rows, widths=[2.6, 1.1, 1.9, 0.9, 0.5], font_pt=9, rows_per_slide=14),
        Para("Proxies corroborate only and never lift an item above level 3 (instrument §5.4). " + peer_line, "muted"),
    ]
    ex.source_line = source_line(run, [], signal_refs=rendered)
    return ex


# =========================================================== scorecard (S08)
def _self_view(sc: dict) -> tuple[Optional[float], dict[str, float]]:
    """Recompute the uncapped (self-view) score from item raw means with the same
    dimension weights; returns None when the capped recomputation does not
    reproduce the scorecard's own capability score (integrity guard).

    plumbscore >= instrument v0.2 emits ``self_view_score`` and per-dimension
    ``self_score`` itself; those are used as-is when present."""
    if sc.get("self_view_score") is not None:
        per = {d["id"]: d["self_score"] for d in sc.get("dimensions") or [] if d.get("self_score") is not None}
        return float(sc["self_view_score"]), per
    dims = {d["id"]: d for d in sc.get("dimensions") or []}
    by_dim_raw: dict[str, list[float]] = {}
    by_dim_cap: dict[str, list[float]] = {}
    for it in sc.get("items") or []:
        if it.get("mean_raw") is None:
            continue
        by_dim_raw.setdefault(it["dimension"], []).append(it["mean_raw"])
        by_dim_cap.setdefault(it["dimension"], []).append(it.get("mean_capped", it["mean_raw"]))

    def total(by: dict[str, list[float]]) -> tuple[Optional[float], dict[str, float]]:
        num = den = 0.0
        per = {}
        for did, d in dims.items():
            xs = by.get(did)
            if not xs or not d.get("scored", True):
                continue
            score = (sum(xs) / len(xs) - 1) / 4 * 100
            per[did] = score
            w = d.get("effective_weight", d.get("weight", 0)) or 0
            num += score * w
            den += w
        return (num / den if den else None), per

    capped, _ = total(by_dim_cap)
    if capped is None or abs(capped - float(sc.get("capability_score", -1))) > 0.05:
        return None, {}
    return total(by_dim_raw)


def scorecard_two_axis(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    ex = Exhibit()
    if not sc:
        ex.requires = ["scorecard.json from plumbscore (10–30 maturity responses, evidence register)"]
        return ex
    C = sc.get("capability_score_rounded", sc.get("capability_score"))
    self_c, self_dim = _self_view(sc)
    va = sc.get("value_axis") or []
    v1 = next((v for v in va if v.get("item_id") == "V1"), None)
    headline = "value attribution still unmeasured" if (v1 and str(v1.get("recorded")) == "A") else f"value profile {sc.get('value_profile', '—')}"
    ex.tokens.update(org=sc.get("org_label"), capability=_fmt(C), band=sc.get("band"), value_headline=headline,
                     self_view=_fmt(round(self_c, 1)) if self_c is not None else None)
    bars = []
    if self_c is not None:
        bars.append(Bar("Self-view (uncapped)", round(self_c, 1), "as reported by respondents"))
    bars.append(Bar("Evidenced view (cap rule)", float(C), f"{sc.get('band')}"))
    dim_rows = []
    for d in sc.get("dimensions") or []:
        s_self = self_dim.get(d["id"])
        gap = (s_self - d["score"]) if (s_self is not None and d.get("score") is not None) else None
        dim_rows.append([d["id"], d.get("name", ""), f"{s_self:.1f}" if s_self is not None else "—",
                         f"{d['score']:.1f}" if d.get("score") is not None else "—",
                         f"{gap:+.1f}" if gap is not None else "—"])
    cells = [(v["item_id"], str(v.get("recorded")), (f"reported {v.get('reported')}; " if v.get("capped") else "") + (v.get("note") or "")) for v in va]
    cov = sc.get("evidence_coverage")
    flags = []
    if cov is not None:
        flags.append(f"Evidence coverage {cov*100:.0f}%" + (" — self-report-dominant" if sc.get("self_report_dominant") else ""))
    flags.append(f"n = {sc.get('n_respondents')} respondents (ExCo {sc.get('n_exco')}, operating {sc.get('n_operating')})")
    ex.blocks = [
        Columns(
            left=[
                Bars(bars, ticks=[(25, "Stagnating ≤25"), (50, "Emerging ≤50"), (75, "Scaling ≤75"), (100, "Leading >75")],
                     boundary=sc.get("production_boundary", 50), boundary_label="production boundary"),
                Table(["Dim", "Dimension", "Self", "Evidenced", "Gap"], dim_rows, widths=[0.4, 2.4, 0.6, 0.8, 0.5], font_pt=8),
            ],
            right=[
                Para("Value axis (never merged with capability)", "strong"),
                Cells(cells, columns=2),
                Bullets(flags),
            ],
            ratio=0.6,
        )
    ]
    src = ss.source or {}
    if src:
        fill = {**ctx, **{k: sc.get(k) for k in ("org_label", "instrument_version", "n_respondents")}}
        try:
            ex.source_line = (f"Source: {src.get('tier', 'T1')} {str(src.get('doc', 'maturity responses')).format(**fill)}, "
                              f"{str(src.get('date', '{date}')).format(**fill)}; confidence: {src.get('confidence', 'interview-anecdote')}")
        except (KeyError, IndexError):
            ex.source_line = None
    return ex


# ============================================================== gap register
def _reason_class(run: RunData, cid: str) -> tuple[str, str, str]:
    c = run.claims[cid]
    rs = " ".join(c.reasons + run.gap_reasons.get(cid, [])).lower()
    if c.awaiting_reconciliation or "reconcil" in rs:
        return ("awaiting publisher reconciliation", "plumbverify reconcile returns MATCH on a machine with egress", "PLUMB (operator)")
    if "mismatch" in rs:
        return ("mismatch", "obtain the publisher's document; the attachment is not it", "client / publisher")
    if "dead" in rs or "unreachable" in rs or "likely_hallucinated" in rs:
        return ("unreachable", "re-run from a machine with egress, or attach the document under its publisher URL", "PLUMB (operator)")
    if "upstream" in rs:
        return ("single upstream", "a second independent upstream source", "PLUMB research / client")
    if "quotation" in rs or "c5" in rs:
        return ("quotation mismatch", "exact passage from the stored source", "PLUMB research")
    return ("unsupported", "a source passage that supports the claim", "PLUMB research")


def gap_register(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    rows = []
    for cid in run.withheld_ids:
        c = run.claims[cid]
        reason, resolve, holder = _reason_class(run, cid)
        src = run.doc_label(c.sources[0]) if c.sources else "—"
        rows.append([c.gap_id, run.claim_descriptor(cid), src[:60], reason, resolve, holder])
    if not rows:
        rows.append(["—", "No claims withheld", "—", "—", "—", "—"])
    gr = run.report.get("gap_register") or {}
    n_verify = len(gr.get("verify_items") or [])
    n_mod = len(gr.get("module_gaps") or [])
    ex = Exhibit(tokens={"n_withheld": il.withheld, "n_verify": n_verify, "n_module_gaps": n_mod})
    ex.blocks = [
        Para(il.outcome_sentence, "lead"),
        Table(["Gap", "Claim", "Source attempted", "Reason", "What would resolve it", "Who holds it"], rows,
              widths=[0.45, 1.9, 1.7, 1.2, 2.2, 1.0], font_pt=9, rows_per_slide=8),
        Para(f"Also listed in the run's gap register: {n_mod} module data gaps and {n_verify} [VERIFY] items (what this run cannot tell you).", "muted"),
    ]
    ex.source_line = f"Source: PLUMB build report {run.run_id}, {run.generated_date}"
    return ex


# =============================================================== evidence log
def evidence_log(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    usage: dict[str, list[str]] = ctx.get("claim_usage", {})
    rows = []
    for cid in run.released_ids:
        c = run.claims[cid]
        src = run.sources.get(c.sources[0]) if c.sources else None
        rows.append([
            cid.rsplit(".", 1)[-1],
            ", ".join(usage.get(cid, [])) or "A1",
            c.text if len(c.text) <= 110 else c.text[:107] + "…",
            f"p. {c.page}" if c.page else "—",
            c.tier or "—",
            c.confidence_label or "—",
            (src.sha256 or "")[:8] if src else "—",
            "RELEASED" + (" (attached)" if ATTACHED_LABEL in c.labels else ""),
        ])
    ex = Exhibit(bound=list(run.released_ids) + list(run.withheld_ids), withheld=list(run.withheld_ids),
                 tokens={"n_released": il.released})
    if not rows:
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(run.withheld_ids)
        return ex
    ex.blocks = [Table(["Claim", "Slides", "Claim text", "Page", "Tier", "Label", "Hash", "State"], rows,
                       widths=[0.45, 0.55, 4.6, 0.5, 0.4, 0.7, 0.75, 1.0], font_pt=8, rows_per_slide=6)]
    ex.source_line = source_line(run, run.released_ids)
    return ex


def placeholder(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]) -> Exhibit:
    return Exhibit(requires=ss.requires or ["engagement data"])


BUILDERS = {
    "cover": cover,
    "disclosure": disclosure,
    "peer_funnel": peer_funnel,
    "signals_table": signals_table,
    "scorecard_two_axis": scorecard_two_axis,
    "gap_register": gap_register,
    "evidence_log": evidence_log,
    "placeholder": placeholder,
}
