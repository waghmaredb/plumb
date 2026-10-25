"""Markdown scorecard consistent with ghost-deck slides S08–S11.

S08 two-axis scorecard (capability bar + V1–V4 profile + evidence coverage)
S09 peer percentile per dimension, n disclosed, evidence-gated share
S10 leadership-perception variance (ExCo gap, σ>1.0 items with roles)
S11 governance (D6) sub-dimension table with evidence class per cell
S12 (regulatory exposure) is not derived from instrument data and is not rendered here.
"""

from __future__ import annotations

from .instrument import Instrument
from .scoring import ScoreResult


def _f(x, nd=1, dash="—"):
    return dash if x is None else f"{x:.{nd}f}"


def _pct(x, dash="—"):
    return dash if x is None else f"{x:.0%}"


def _bar(score: float, width: int = 40) -> str:
    """ASCII capability bar with the 50-line production boundary marked."""
    filled = int(round(score / 100 * width))
    cells = ["█" if i < filled else "░" for i in range(width)]
    mid = width // 2
    cells[mid] = "┃"  # production boundary (50)
    return "".join(cells)


def render_scorecard(instrument: Instrument, res: ScoreResult, title: str = "") -> str:
    org = res.org_label or "Client"
    L: list[str] = []
    L.append(f"# {title or f'{org} — Enterprise AI Maturity Scorecard'}")
    L.append("")
    L.append(f"Instrument v{res.instrument_version} · respondents n={res.n_respondents} (ExCo {res.n_exco}, operating {res.n_operating}) · scores after cap rule (§5.4)")
    L.append("")

    # ---- S08 two-axis scorecard -----------------------------------------
    L.append("## S08 · Where you are: two-axis scorecard")
    L.append("")
    if res.capability_score is not None:
        headline = f"**{org} scores {res.capability_score_rounded:.1f} of 100, {res.band}**"
        vh = _value_headline(res)
        if vh:
            headline += f", with {vh}"
        L.append(headline + ".")
        L.append("")
        L.append("```")
        L.append(f"0 {_bar(res.capability_score)} 100   ┃ = production boundary (50)")
        L.append("  Stagnating ≤25 · Emerging ≤50 · Scaling ≤75 · Leading >75")
        L.append("```")
    else:
        L.append("**Capability score not computable** (no dimension reached the ≥4-of-6 item rule).")
    L.append("")
    L.append("| Capability axis | | Value axis (never merged) | |")
    L.append("|---|---|---|---|")
    L.append(f"| Capability score | **{_f(res.capability_score_rounded)}** / 100 | Profile | **{res.value_profile}** |")
    v_by = {v.item_id: v for v in res.value_axis}
    rows = [
        ("Band", res.band or "—", "V1 EBIT share attributable to AI", v_by.get("V1")),
        ("Production boundary (50)", "above" if res.above_production_boundary else ("at/below" if res.above_production_boundary is not None else "—"), "V2 share of initiatives in production", v_by.get("V2")),
        ("Evidence coverage", _pct(res.evidence_coverage) + (" — **self-report-dominant**" if res.self_report_dominant else ""), "V3 value-tracking rigour", v_by.get("V3")),
        ("Weights renormalised", "yes" if res.weights_renormalised else "no", "V4 agent control maturity (OWASP GML)", v_by.get("V4")),
    ]
    for a, b, c, v in rows:
        vtxt = "—"
        if v is not None:
            vtxt = f"{v.recorded if v.recorded is not None else '—'}"
            if v.capped:
                vtxt += f" (reported {v.reported}; {v.note})"
        L.append(f"| {a} | {b} | {c} | {vtxt} |")
    if res.value_gap_flag:
        L.append("")
        L.append("> **Value gap flag** (§4): capability band is Scaling/Leading but V1 = Band A or V3 ≤ 2.")
    L.append("")

    # ---- dimension table ---------------------------------------------------
    L.append("### Dimension scores")
    L.append("")
    L.append("| Dim | Dimension | Weight | Items scored | Mean (1–5) | Score (0–100) | σ-flagged items | Alignment |")
    L.append("|---|---|---|---|---|---|---|---|")
    for d in res.dimensions:
        w = f"{d.weight:.0f}" + (f" → {d.effective_weight:.1f}" if res.weights_renormalised and d.scored else "")
        align = "not aligned" if d.not_aligned else ("—" if d.alignment_index is None else f"{d.alignment_index:.0%} flagged")
        L.append(
            f"| {d.id} | {d.name} | {w} | {d.n_items_scored}/{instrument.scoring.dimension_items}{'' if d.scored else ' (not scored)'} | "
            f"{_f(d.mean, 2)} | {_f(d.score)} | {d.n_items_sigma_flagged} | {align} |"
        )
    L.append("")

    # ---- S09 peer percentile ---------------------------------------------
    L.append("## S09 · Peer percentile")
    L.append("")
    p = res.percentile
    if not p:
        L.append("No benchmark supplied; percentile not computed.")
    elif p.get("peer_rank"):
        # Peer n below the §5.5 minimum: show the rank within the named peers, each peer's value visible,
        # instead of a percentile against a benchmark of nobody (red-team review 2026-10-25, Blocker 3).
        pr = p["peer_rank"]
        L.append(f"**{org} ranks {pr['rank']} of {pr['n'] + 1} within the named peer set (n={pr['n']})** — "
                 f"peer n insufficient for a percentile (minimum {p['min_n']}, §5.5); no percentile is reported.")
        L.append("")
        pop = (p.get("population") or {}).get("population")
        L.append(
            f"Peer set: {', '.join(f'{k}={v}' for k, v in p['filters'].items())} · "
            f"peer-set definition date: {p.get('peer_set_date') or 'not supplied'} · "
            f"population: {pop or 'not tagged'} (self-scored and evidence-gated entries are never pooled)"
        )
        L.append("")
        L.append("| Rank | Organisation | Capability score | " + " | ".join(d.id for d in res.dimensions) + " |")
        L.append("|---|---|---|" + "---|" * len(res.dimensions))
        rows = [{"org_id": org, "total": res.capability_score, "dims": {d.id: d.score for d in res.dimensions}, "_self": True}]
        rows += pr["peers"]
        rows.sort(key=lambda r: (r["total"] if r["total"] is not None else -1), reverse=True)
        for i, r in enumerate(rows, start=1):
            name = f"**{r['org_id']}**" if r.get("_self") else r["org_id"]
            L.append(f"| {i} | {name} | {_f(r['total'])} | " + " | ".join(_f(r['dims'].get(d.id)) for d in res.dimensions) + " |")
        L.append("")
        L.append(f"> **{instrument.scoring.peer_percentile.fallback_label}** — no global percentile is shown in its place: "
                 "the global pool is not the client's peer set and the client cannot inspect it. Rank is on the capability score only; "
                 "outside-in peer values corroborate and never lift (§5.4).")
    else:
        tp = p.get("total_percentile")
        dp = p.get("dimension_percentiles", {})
        weakest = None
        valid = {k: v for k, v in dp.items() if v is not None}
        if valid:
            weakest = min(valid, key=valid.get)
        line = f"**{org} sits at the {_ordinal(tp)} percentile overall**"
        if weakest:
            dname = instrument.dimension_by_id[weakest].name
            line += f" but {_ordinal(valid[weakest])} on {dname} ({weakest})"
        L.append(line + f" — {p['label']}.")
        L.append("")
        eg = p.get("evidence_gated_share")
        pop = (p.get("population") or {}).get("population")
        L.append(
            f"Peer set: {', '.join(f'{k}={v}' for k, v in p['filters'].items()) or 'none (global)'} · "
            f"n={p['n']} ({p['scope']}; minimum n for a peer percentile is {p['min_n']}) · "
            f"peer-set definition date: {p.get('peer_set_date') or 'not supplied'} · "
            f"population: {pop or 'not tagged'} · "
            f"share of entries evidence-gated: {_pct(eg) if eg is not None else 'not recorded'}"
        )
        if not p.get("peer_n_sufficient"):
            L.append("")
            L.append(f"> **{instrument.scoring.peer_percentile.fallback_label}** — peer candidates n={p['n_peer_candidates']}; global benchmark used (§5.5).")
        L.append("")
        L.append("| Dim | Score | Set median | Global median | Percentile |")
        L.append("|---|---|---|---|---|")
        dscore = {d.id: d.score for d in res.dimensions}
        for d in res.dimensions:
            L.append(
                f"| {d.id} | {_f(dscore[d.id])} | {_f(p['peer_median_by_dimension'].get(d.id))} | "
                f"{_f(p['global_median_by_dimension'].get(d.id))} | {_f(dp.get(d.id), 0)} |"
            )
        L.append(f"| **Total** | **{_f(res.capability_score_rounded)}** | {_f(p.get('set_median_total'))} | {_f(p.get('global_median_total'))} | **{_f(tp, 0)}** |")
    L.append("")

    # ---- S10 leadership-perception variance --------------------------------
    L.append("## S10 · Leadership-perception variance")
    L.append("")
    if res.variance_mode == "range":
        L.append(f"Fewer than {instrument.scoring.variance.min_respondents_for_sigma} respondents: min–max range reported instead of σ (§5.3).")
        L.append("")
    gaps = [d for d in res.dimensions if d.exco_gap is not None]
    if gaps:
        big = max(gaps, key=lambda d: abs(d.exco_gap or 0))
        if big.exco_gap_flag:
            who = "ExCo" if big.exco_gap > 0 else "Operating managers"
            other = "operating managers" if big.exco_gap > 0 else "ExCo"
            L.append(f"**{who} rate {big.name} {abs(big.exco_gap):.2f} levels {'above' if big.exco_gap > 0 else 'below'} {other}** ({big.exco_gap_sign}).")
        else:
            L.append("No dimension shows an ExCo-vs-operating gap above 0.75 levels.")
        L.append("")
    L.append("| Dim | ExCo mean | Operating mean | Gap (ExCo − operating) | Flag (>0.75) | Items σ>1.0 | Alignment |")
    L.append("|---|---|---|---|---|---|---|")
    for d in res.dimensions:
        flag = (d.exco_gap_sign or "") if d.exco_gap_flag else "—"
        L.append(
            f"| {d.id} | {_f(d.exco_mean, 2)} | {_f(d.operating_mean, 2)} | {_f(d.exco_gap, 2) if d.exco_gap is None else f'{d.exco_gap:+.2f}'} | {flag} | "
            f"{d.n_items_sigma_flagged} | {'**leadership not aligned**' if d.not_aligned else '—'} |"
        )
    L.append("")
    flagged = [i for i in res.items if i.sigma_flag]
    if flagged:
        L.append("Items flagged for perception divergence (σ > 1.0 on raw self-report, computed before the cap rule):")
        L.append("")
        L.append("| Item | σ | Range | Roles at highest level | Roles at lowest level |")
        L.append("|---|---|---|---|---|")
        for i in flagged:
            L.append(f"| {i.item_id} | {i.sigma_raw:.2f} | {i.range_raw[0]}–{i.range_raw[1]} | {', '.join(i.extremes_high)} | {', '.join(i.extremes_low)} |")
    elif res.variance_mode == "range":
        wide = [i for i in res.items if i.range_raw and i.range_raw[1] - i.range_raw[0] >= 2]
        L.append("Items with a raw range of ≥2 levels: " + (", ".join(f"{i.item_id} ({i.range_raw[0]}–{i.range_raw[1]})" for i in wide) or "none") + ".")
    else:
        L.append("No item exceeds σ 1.0.")
    L.append("")

    # ---- S11 governance sub-dimensions -----------------------------------
    L.append("## S11 · Governance, risk & compliance (D6) by item")
    L.append("")
    L.append("| Item | Question | Level (mean, capped) | Ev≥4 required | Evidence logged | Capped responses | OWASP GML (D6.6) |")
    L.append("|---|---|---|---|---|---|---|")
    for i in res.items:
        if i.dimension != "D6":
            continue
        it = instrument.item_by_id[i.item_id]
        q = it.question.split(" (")[0]
        gml = f"GML {i.mean_capped - 1:.1f}" if (i.item_id == "D6.6" and i.mean_capped is not None) else "—"
        L.append(
            f"| {i.item_id} | {q} | {_f(i.mean_capped, 2)} | {it.evidence_class_required_text} | "
            f"{'+'.join(i.evidence_classes_logged) or 'none'} | {i.n_capped}/{i.n_responses} | {gml} |"
        )
    L.append("")
    L.append("S12 (regulatory exposure) is built from the regulatory-status map, not from instrument data.")
    L.append("")

    # ---- item detail ----------------------------------------------------------
    L.append("## Appendix · Item detail (all 48 items)")
    L.append("")
    L.append("| Item | n | Mean raw | Mean capped | σ raw | Capped | Evidence logged | Ev≥4 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for i in res.items:
        L.append(
            f"| {i.item_id} | {i.n_responses} | {_f(i.mean_raw, 2)} | {_f(i.mean_capped, 2)} | {_f(i.sigma_raw, 2)}{' ⚑' if i.sigma_flag else ''} | "
            f"{i.n_capped} | {'+'.join(i.evidence_classes_logged) or '—'} | {'+'.join(i.evidence_required)} |"
        )
    L.append("")

    # ---- flags ----------------------------------------------------------------
    L.append("## Flags")
    L.append("")
    if res.flags:
        for fl in res.flags:
            L.append(f"- {fl}")
    else:
        L.append("- none")
    L.append("")
    return "\n".join(L)


def _value_headline(res: ScoreResult) -> str:
    v = {x.item_id: x for x in res.value_axis}
    v1 = v.get("V1")
    if v1 is not None and v1.recorded is not None and str(v1.recorded) == "A":
        return "value attribution still unmeasured"
    v3 = v.get("V3")
    if v3 is not None and isinstance(v3.recorded, int) and v3.recorded <= 2:
        return "value tracking still anecdotal"
    if v1 is not None and v1.recorded is not None:
        return f"V1 Band {v1.recorded} on value"
    return ""


def _ordinal(p) -> str:
    if p is None:
        return "—"
    n = int(round(p))
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"
