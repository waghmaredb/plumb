"""Scoring engine: cap rule (§5.4), item/dimension/total (§5.1), bands (§5.2),
leadership-perception variance (§5.3), value axis (§4).

All statistics are pure Python; numpy is not required.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Optional, Union

from pydantic import BaseModel, Field

from .instrument import Instrument, Item, ValueItem
from .responses import Response


# ---------------------------------------------------------------------------
# small stats helpers
# ---------------------------------------------------------------------------
def _mean(xs: list[float]) -> Optional[float]:
    return sum(xs) / len(xs) if xs else None


def _pstdev(xs: list[float]) -> Optional[float]:
    """Population standard deviation (§5.3: 'population standard deviation')."""
    if not xs:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


# ---------------------------------------------------------------------------
# result models
# ---------------------------------------------------------------------------
class ItemResult(BaseModel):
    item_id: str
    dimension: str
    n_responses: int
    raw_scores: list[int]
    capped_scores: list[int]
    n_capped: int
    cap_flag: bool
    capped_respondents: list[str] = Field(default_factory=list)
    mean_raw: Optional[float]
    mean_capped: Optional[float]
    sigma_raw: Optional[float]  # None when n < min_respondents_for_sigma
    range_raw: Optional[tuple[int, int]]
    sigma_flag: bool
    extremes_high: list[str] = Field(default_factory=list)  # roles at max raw level
    extremes_low: list[str] = Field(default_factory=list)  # roles at min raw level
    evidence_logged: bool
    evidence_classes_logged: list[str] = Field(default_factory=list)
    evidence_required: list[str]
    exco_mean_raw: Optional[float] = None
    operating_mean_raw: Optional[float] = None


class DimensionResult(BaseModel):
    id: str
    name: str
    weight: float
    effective_weight: float
    scored: bool
    n_items_scored: int
    mean: Optional[float]  # m_d on 1–5
    score: Optional[float]  # s_d on 0–100
    n_items_sigma_flagged: int
    alignment_index: Optional[float]  # share of items flagged σ>1.0
    not_aligned: bool
    exco_mean: Optional[float]
    operating_mean: Optional[float]
    exco_gap: Optional[float]
    exco_gap_flag: bool
    exco_gap_sign: Optional[str]


class ValueResult(BaseModel):
    item_id: str
    reported: Optional[Union[str, int]]
    recorded: Optional[Union[str, int]]
    capped: bool
    label: str  # e.g. "V1 B" or "V1 A (not evidenced)"
    n_rows: int
    note: str = ""


class ScoreResult(BaseModel):
    instrument_version: str
    org_label: str = ""
    n_respondents: int
    n_exco: int
    n_operating: int
    capability_score: Optional[float]  # unrounded
    capability_score_rounded: Optional[float]
    band: Optional[str]
    production_boundary: float
    above_production_boundary: Optional[bool]
    weights_renormalised: bool
    evidence_coverage: float  # 0–1 share of items with evidence logged
    self_report_dominant: bool
    variance_mode: str  # "sigma" or "range"
    dimensions: list[DimensionResult]
    items: list[ItemResult]
    value_axis: list[ValueResult]
    value_profile: str
    value_gap_flag: bool
    flags: list[str]
    percentile: Optional[dict] = None


# ---------------------------------------------------------------------------
# bands
# ---------------------------------------------------------------------------
def band_for(instrument: Instrument, score: float) -> str:
    """Band on the unrounded score (§5.1).

    The md's band table uses integer edges (0–25, 26–50, 51–75, 76–100) but
    the band is assigned on the unrounded value, so the scorer treats each
    band's upper edge as inclusive: ≤25 Stagnating, ≤50 Emerging, ≤75 Scaling,
    >75 Leading. This matches the §5.1 worked check (50.0 = top of Emerging;
    Scaling requires an average above level 3). See the `note:` under `bands`.
    """
    bands = instrument.band_list
    for b in bands[:-1]:
        if score <= b.high:
            return b.name
    return bands[-1].name


# ---------------------------------------------------------------------------
# cap rule
# ---------------------------------------------------------------------------
def apply_cap(item: Item, r: Response, cap: int = 3) -> tuple[int, bool]:
    """Return (recorded_score, was_capped).

    A self-report above the cap is recorded at the cap unless *all* of the
    item's Ev≥4 classes are logged on that response (§1, §5.4). Interview
    evidence alone never lifts an item whose Ev≥4 is D or S (§5.4), which
    falls out of the subset test.
    """
    score = int(r.score)
    if score <= cap:
        return score, False
    required = set(item.evidence_class_required)
    if required and required.issubset(r.evidence_classes):
        return score, False
    return cap, True


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------
def score_responses(
    instrument: Instrument,
    responses: list[Response],
    org_label: str = "",
) -> ScoreResult:
    spec = instrument.scoring
    cap = spec.cap_rule.self_report_cap
    var = spec.variance
    flags: list[str] = []

    cap_rows = [r for r in responses if r.is_capability]
    val_rows = [r for r in responses if not r.is_capability]

    unknown = sorted({r.item_id for r in cap_rows} - set(instrument.item_by_id))
    if unknown:
        raise ValueError(f"unknown capability item ids: {unknown}")

    respondents = {r.respondent_id: r.role_group for r in responses}
    n_resp = len(respondents)
    n_exco = sum(1 for g in respondents.values() if g == "exco")
    n_oper = n_resp - n_exco
    variance_mode = "sigma" if n_resp >= var.min_respondents_for_sigma else "range"
    if variance_mode == "range":
        flags.append(
            f"Only {n_resp} respondents (<{var.min_respondents_for_sigma}); "
            "min–max range reported instead of σ (§5.3)"
        )

    by_item: dict[str, list[Response]] = defaultdict(list)
    for r in cap_rows:
        by_item[r.item_id].append(r)

    # ---- items ------------------------------------------------------------
    item_results: dict[str, ItemResult] = {}
    for item in instrument.items:
        rows = by_item.get(item.id, [])
        raw = [int(r.score) for r in rows]
        capped: list[int] = []
        capped_resp: list[str] = []
        for r in rows:
            s, was = apply_cap(item, r, cap)
            capped.append(s)
            if was:
                capped_resp.append(r.respondent_id)
        sigma = _pstdev(raw) if (raw and variance_mode == "sigma") else None
        sigma_flag = bool(sigma is not None and sigma > var.sigma_flag_threshold)
        ext_hi: list[str] = []
        ext_lo: list[str] = []
        if raw:
            mx, mn = max(raw), min(raw)

            def _role(r: Response) -> str:
                return r.role or r.role_group

            ext_hi = sorted({_role(r) for r in rows if int(r.score) == mx})
            ext_lo = sorted({_role(r) for r in rows if int(r.score) == mn})
        ev_classes = sorted({c for r in rows for c in r.evidence_classes})
        exco_raw = [int(r.score) for r in rows if r.role_group == "exco"]
        oper_raw = [int(r.score) for r in rows if r.role_group == "operating"]
        item_results[item.id] = ItemResult(
            item_id=item.id,
            dimension=item.dimension,
            n_responses=len(rows),
            raw_scores=raw,
            capped_scores=capped,
            n_capped=len(capped_resp),
            cap_flag=bool(capped_resp),
            capped_respondents=capped_resp,
            mean_raw=_mean(raw),
            mean_capped=_mean(capped),
            sigma_raw=sigma,
            range_raw=(min(raw), max(raw)) if raw else None,
            sigma_flag=sigma_flag,
            extremes_high=ext_hi if sigma_flag else [],
            extremes_low=ext_lo if sigma_flag else [],
            evidence_logged=bool(ev_classes),
            evidence_classes_logged=ev_classes,
            evidence_required=list(item.evidence_class_required),
            exco_mean_raw=_mean(exco_raw),
            operating_mean_raw=_mean(oper_raw),
        )

    # ---- dimensions -------------------------------------------------------
    dim_results: list[DimensionResult] = []
    scored_dims: dict[str, float] = {}
    for dim in instrument.dimensions:
        items = instrument.items_by_dimension[dim.id]
        irs = [item_results[i.id] for i in items]
        scored_irs = [ir for ir in irs if ir.n_responses > 0]
        n_scored = len(scored_irs)
        scored = n_scored >= spec.dimension_min_items_scored
        m_d = _mean([ir.mean_capped for ir in scored_irs]) if scored else None  # type: ignore[arg-type]
        s_d = (m_d - 1) / 4 * 100 if m_d is not None else None
        if scored:
            scored_dims[dim.id] = s_d  # type: ignore[assignment]
        else:
            flags.append(
                f"{dim.id} not scored: {n_scored} of {spec.dimension_items} items answered "
                f"(<{spec.dimension_min_items_scored}); weight renormalised (§5.1)"
            )
        n_flag = sum(1 for ir in scored_irs if ir.sigma_flag)
        align = (n_flag / n_scored) if (n_scored and variance_mode == "sigma") else None
        not_aligned = bool(align is not None and align >= var.alignment_not_aligned_share)
        # ExCo vs operating gap on raw (pre-cap) levels, per dimension (§5.3, S10)
        exco_vals = [int(r.score) for i in items for r in by_item.get(i.id, []) if r.role_group == "exco"]
        oper_vals = [int(r.score) for i in items for r in by_item.get(i.id, []) if r.role_group == "operating"]
        em, om = _mean(exco_vals), _mean(oper_vals)
        gap = (em - om) if (em is not None and om is not None) else None
        gap_flag = bool(gap is not None and abs(gap) > var.exco_gap_flag_abs)
        sign = None
        if gap is not None:
            sign = "ExCo-optimistic" if gap > 0 else ("ExCo-pessimistic" if gap < 0 else "aligned")
        dim_results.append(
            DimensionResult(
                id=dim.id,
                name=dim.name,
                weight=dim.weight,
                effective_weight=dim.weight,  # patched below if renormalised
                scored=scored,
                n_items_scored=n_scored,
                mean=m_d,
                score=s_d,
                n_items_sigma_flagged=n_flag,
                alignment_index=align,
                not_aligned=not_aligned,
                exco_mean=em,
                operating_mean=om,
                exco_gap=gap,
                exco_gap_flag=gap_flag,
                exco_gap_sign=sign,
            )
        )
        if not_aligned:
            flags.append(f"{dim.id} leadership not aligned: {n_flag}/{n_scored} items σ>{var.sigma_flag_threshold} (§5.3)")
        if gap_flag:
            flags.append(f"{dim.id} ExCo-vs-operating gap {gap:+.2f} ({sign}) exceeds {var.exco_gap_flag_abs} (§5.3)")

    # ---- weighted total ---------------------------------------------------
    weights = instrument.weights
    renorm = len(scored_dims) != len(weights)
    C: Optional[float] = None
    if scored_dims:
        wsum = sum(weights[d] for d in scored_dims)
        for dr in dim_results:
            dr.effective_weight = (weights[dr.id] / wsum * 100) if dr.id in scored_dims else 0.0
        C = sum(weights[d] * s for d, s in scored_dims.items()) / wsum
    band = band_for(instrument, C) if C is not None else None
    C_round = round(C, spec.rounding_decimals) if C is not None else None

    # ---- evidence coverage ------------------------------------------------
    n_items = len(instrument.items)
    n_ev = sum(1 for ir in item_results.values() if ir.evidence_logged)
    coverage = n_ev / n_items if n_items else 0.0
    srd = coverage < spec.cap_rule.evidence_coverage_self_report_dominant_below
    if srd:
        flags.append(
            f"Evidence coverage {coverage:.0%} < "
            f"{spec.cap_rule.evidence_coverage_self_report_dominant_below:.0%}: capability score is self-report-dominant (§5.4)"
        )
    n_cap_items = sum(1 for ir in item_results.values() if ir.cap_flag)
    if n_cap_items:
        flags.append(f"Cap rule applied on {n_cap_items} items (self-report >{cap} without required evidence class, §5.4)")

    # ---- value axis -------------------------------------------------------
    d84 = item_results["D8.4"].mean_capped if "D8.4" in item_results else None
    value_results = _score_value_axis(instrument, val_rows, d84_mean=d84)
    profile = " · ".join(v.label for v in value_results)
    v1 = next((v for v in value_results if v.item_id == "V1"), None)
    v3 = next((v for v in value_results if v.item_id == "V3"), None)
    value_gap = bool(
        band in {"Scaling", "Leading"}
        and (
            (v1 is not None and str(v1.recorded) == "A")
            or (v3 is not None and isinstance(v3.recorded, int) and v3.recorded <= 2)
        )
    )
    if value_gap:
        flags.append("Value gap flag: capability band Scaling/Leading but V1 = Band A or V3 ≤ 2 (§4)")

    return ScoreResult(
        instrument_version=instrument.version,
        org_label=org_label,
        n_respondents=n_resp,
        n_exco=n_exco,
        n_operating=n_oper,
        capability_score=C,
        capability_score_rounded=C_round,
        band=band,
        production_boundary=instrument.production_boundary,
        above_production_boundary=(C > instrument.production_boundary) if C is not None else None,
        weights_renormalised=renorm,
        evidence_coverage=coverage,
        self_report_dominant=srd,
        variance_mode=variance_mode,
        dimensions=dim_results,
        items=list(item_results.values()),
        value_axis=value_results,
        value_profile=profile,
        value_gap_flag=value_gap,
        flags=flags,
    )


# ---------------------------------------------------------------------------
# value axis (§4)
# ---------------------------------------------------------------------------
def _cap_value_row(vi: ValueItem, r: Response, d84_mean: Optional[float]) -> tuple[Union[str, int], bool, str]:
    """Apply the item's evidence rule to one value-axis row."""
    reported: Union[str, int] = r.score
    try:
        rank = vi.rank(reported)
    except ValueError as e:
        raise ValueError(f"{vi.id}: value {reported!r} not on scale {vi.scale}") from e
    required = set(vi.evidence_class_required)
    has = required.issubset(r.evidence_classes)
    if vi.id == "V1":
        dep_ok = d84_mean is not None and d84_mean >= float((vi.dependency or {}).get("min_level", 3))
        if has and dep_ok:
            return reported, False, ""
        why = "no S+D evidence" if not has else "D8.4 < 3"
        return vi.unevidenced_value, rank > 0, f"recorded Band A ({vi.unevidenced_label}: {why})"  # type: ignore[return-value]
    if vi.self_report_cap is None or has:
        return reported, False, ""
    cap_rank = vi.rank(vi.self_report_cap)
    if rank > cap_rank:
        return vi.scale[cap_rank], True, f"self-report capped at {vi.self_report_cap} without {'+'.join(sorted(required))} evidence"
    return reported, False, ""


def _score_value_axis(instrument: Instrument, rows: list[Response], d84_mean: Optional[float]) -> list[ValueResult]:
    out: list[ValueResult] = []
    by: dict[str, list[Response]] = defaultdict(list)
    for r in rows:
        by[r.item_id.upper()].append(r)
    for vi in instrument.value_items:
        rs = by.get(vi.id, [])
        if not rs:
            out.append(ValueResult(item_id=vi.id, reported=None, recorded=None, capped=False, label=f"{vi.id} —", n_rows=0, note="not answered"))
            continue
        recorded_vals: list[tuple[int, Union[str, int], bool, str]] = []
        for r in rs:
            rec, capped, note = _cap_value_row(vi, r, d84_mean)
            recorded_vals.append((vi.rank(rec), rec, capped, note))
        # consensus: mode of recorded ranks; ties → lower (conservative)
        counts = Counter(rk for rk, *_ in recorded_vals)
        top = max(counts.values())
        chosen_rank = min(rk for rk, c in counts.items() if c == top)
        chosen = next(v for rk, v, _, _ in recorded_vals if rk == chosen_rank)
        any_capped = any(c for _, _, c, _ in recorded_vals)
        notes = sorted({n for _, _, c, n in recorded_vals if c and n})
        rep_counts = Counter(str(r.score) for r in rs)
        reported = rep_counts.most_common(1)[0][0]
        if str(reported).lstrip("-").isdigit():
            reported = int(reported)
        label = f"{vi.id} {chosen}"
        if vi.id == "V1" and str(chosen) == "A" and any_capped:
            label += " (not evidenced)"
        out.append(
            ValueResult(
                item_id=vi.id,
                reported=reported,
                recorded=chosen,
                capped=any_capped,
                label=label,
                n_rows=len(rs),
                note="; ".join(notes),
            )
        )
    return out
