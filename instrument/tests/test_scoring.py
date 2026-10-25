import math

import pytest

from plumbscore.responses import responses_from_records
from plumbscore.scoring import apply_cap, band_for, score_responses


# ---------------------------------------------------------------- cap rule
def _resp(item_id, score, ev="none", rid="R1", grp="exco"):
    return responses_from_records(
        [{"respondent_id": rid, "role_group": grp, "item_id": item_id, "score": score, "evidence_class": ev}]
    )[0]


def test_cap_without_evidence(inst):
    it = inst.item_by_id["D1.1"]  # Ev≥4 = D
    assert apply_cap(it, _resp("D1.1", 4)) == (3, True)
    assert apply_cap(it, _resp("D1.1", 5)) == (3, True)
    assert apply_cap(it, _resp("D1.1", 3)) == (3, False)
    assert apply_cap(it, _resp("D1.1", 1)) == (1, False)


def test_cap_lifted_with_required_class(inst):
    it = inst.item_by_id["D1.1"]
    assert apply_cap(it, _resp("D1.1", 5, "D")) == (5, False)
    # wrong class does not lift; interview alone never lifts a D item (§5.4)
    assert apply_cap(it, _resp("D1.1", 5, "S")) == (3, True)
    assert apply_cap(it, _resp("D1.1", 4, "I")) == (3, True)


def test_cap_two_class_items_need_both(inst):
    it = inst.item_by_id["D1.4"]  # D+S
    assert apply_cap(it, _resp("D1.4", 4, "D")) == (3, True)
    assert apply_cap(it, _resp("D1.4", 4, "S")) == (3, True)
    assert apply_cap(it, _resp("D1.4", 4, "D+S")) == (4, False)
    it2 = inst.item_by_id["D4.4"]  # I + O
    assert apply_cap(it2, _resp("D4.4", 4, "I")) == (3, True)
    assert apply_cap(it2, _resp("D4.4", 4, "I+O")) == (4, False)


def test_cap_flag_surfaces_in_item_result(inst, make_responses):
    rs = make_responses(lambda i, n, g: 5 if i == "D2.2" else 3)
    res = score_responses(inst, rs)
    ir = next(i for i in res.items if i.item_id == "D2.2")
    assert ir.cap_flag and ir.n_capped == 12
    assert ir.mean_capped == 3 and ir.mean_raw == 5
    assert any("Cap rule applied" in f for f in res.flags)


# ----------------------------------------------------------- weighting
def test_all_threes_is_exactly_50(inst, make_responses):
    res = score_responses(inst, make_responses(lambda i, n, g: 3))
    assert res.capability_score == 50.0
    assert res.capability_score_rounded == 50.0
    assert res.band == "Emerging"
    assert res.above_production_boundary is False
    assert all(d.score == 50.0 for d in res.dimensions)


def test_weighted_arithmetic(inst, make_responses):
    # D6 (w=16) at level 5 with evidence, everything else at 1
    lvl = lambda i, n, g: 5 if i.startswith("D6") else 1
    ev = {i.id: "+".join(i.evidence_class_required) for i in inst.items if i.dimension == "D6"}
    res = score_responses(inst, make_responses(lvl, evidence=ev))
    assert res.capability_score == pytest.approx(16.0)  # 16 × 100 / 100
    assert res.band == "Stagnating"


def test_dimension_min_items_and_renormalisation(inst, make_responses):
    items = [i.id for i in inst.items if not (i.dimension == "D1" and i.id in {"D1.4", "D1.5", "D1.6"})]
    res = score_responses(inst, make_responses(lambda i, n, g: 3, items=items))
    d1 = next(d for d in res.dimensions if d.id == "D1")
    assert not d1.scored and d1.n_items_scored == 3 and d1.effective_weight == 0
    assert res.weights_renormalised
    assert res.capability_score == pytest.approx(50.0)
    assert sum(d.effective_weight for d in res.dimensions) == pytest.approx(100)
    assert any("D1 not scored" in f for f in res.flags)


# -------------------------------------------------------------- bands
@pytest.mark.parametrize(
    "score,band",
    [
        (0, "Stagnating"),
        (25, "Stagnating"),
        (25.01, "Emerging"),
        (26, "Emerging"),
        (50, "Emerging"),
        (50.01, "Scaling"),
        (51, "Scaling"),
        (75, "Scaling"),
        (75.01, "Leading"),
        (76, "Leading"),
        (100, "Leading"),
    ],
)
def test_band_edges(inst, score, band):
    assert band_for(inst, score) == band


def test_leading_requires_weighted_mean_above_4(inst, make_responses):
    ev = {i.id: "+".join(i.evidence_class_required) for i in inst.items}
    res4 = score_responses(inst, make_responses(lambda i, n, g: 4, evidence=ev))
    assert res4.capability_score == 75.0 and res4.band == "Scaling"


# ------------------------------------------------------------ variance
def test_sigma_flag_computed_before_cap(inst, make_responses):
    # D3.1: 5 ExCo say 5 (uncapped would be 3), 7 operating say 1 → σ raw ≈ 1.98
    rs = make_responses(lambda i, n, g: (5 if g == "exco" else 1) if i == "D3.1" else 3)
    res = score_responses(inst, rs)
    ir = next(i for i in res.items if i.item_id == "D3.1")
    assert ir.sigma_flag
    assert ir.sigma_raw == pytest.approx(math.sqrt(35 / 9))  # population σ of 5×5 and 7×1
    assert ir.capped_scores.count(3) == 5  # exco 5 → 3
    assert ir.extremes_high == ["exco"] and ir.extremes_low == ["operating"]
    d3 = next(d for d in res.dimensions if d.id == "D3")
    assert d3.n_items_sigma_flagged == 1 and d3.alignment_index == pytest.approx(1 / 6) and not d3.not_aligned
    assert d3.exco_gap == pytest.approx((5 + 3 * 5) / 6 - (1 + 3 * 5) / 6)
    assert d3.exco_gap_flag is False  # 0.67 < 0.75


def test_sigma_not_flagged_below_threshold(inst, make_responses):
    rs = make_responses(lambda i, n, g: 4 if (i == "D7.1" and n % 2) else 3)
    ir = next(i for i in score_responses(inst, rs).items if i.item_id == "D7.1")
    assert ir.sigma_raw == pytest.approx(0.5) and not ir.sigma_flag


def test_range_mode_below_five_respondents(inst, make_responses):
    rs = make_responses(lambda i, n, g: 1 if n == 1 else 5, n_exco=2, n_oper=2)
    res = score_responses(inst, rs)
    assert res.variance_mode == "range"
    assert all(i.sigma_raw is None and i.range_raw == (1, 5) for i in res.items)
    assert any("min–max range" in f for f in res.flags)


def test_exco_gap_and_alignment(inst, make_responses):
    # D5: ExCo 4 (capped to 3), operating 2 on every item → gap +2.0, all 6 items σ>1 → not aligned
    rs = make_responses(lambda i, n, g: (4 if g == "exco" else 2) if i.startswith("D5") else 3)
    res = score_responses(inst, rs)
    d5 = next(d for d in res.dimensions if d.id == "D5")
    assert d5.exco_gap == pytest.approx(2.0) and d5.exco_gap_flag and d5.exco_gap_sign == "ExCo-optimistic"
    # σ = sqrt(5·7/144)·2 ≈ 0.99 → not flagged; push operating to 1 for σ>1
    rs = make_responses(lambda i, n, g: (4 if g == "exco" else 1) if i.startswith("D5") else 3)
    d5 = next(d for d in score_responses(inst, rs).dimensions if d.id == "D5")
    assert d5.not_aligned and d5.alignment_index == 1.0
    assert d5.mean == pytest.approx((5 * 3 + 7 * 1) / 12)


def test_exco_pessimistic_sign(inst, make_responses):
    rs = make_responses(lambda i, n, g: (1 if g == "exco" else 3) if i.startswith("D8") else 3)
    d8 = next(d for d in score_responses(inst, rs).dimensions if d.id == "D8")
    assert d8.exco_gap == pytest.approx(-2.0) and d8.exco_gap_sign == "ExCo-pessimistic"


# ------------------------------------------------------- evidence coverage
def test_evidence_coverage_and_self_report_dominant(inst, make_responses):
    res = score_responses(inst, make_responses(lambda i, n, g: 3))
    assert res.evidence_coverage == 0 and res.self_report_dominant
    ev = {i.id: "+".join(i.evidence_class_required) for i in inst.items[:29]}  # 29/48 = 60.4%
    res = score_responses(inst, make_responses(lambda i, n, g: 3, evidence=ev))
    assert res.evidence_coverage == pytest.approx(29 / 48) and not res.self_report_dominant


# ------------------------------------------------------------ value axis
def _value_rows(**kw):
    base = {"V1": ("B", "S+D"), "V2": ("≥62%", "S"), "V3": (4, "S"), "V4": (3, "O+S")}
    base.update(kw)
    return [
        {"respondent_id": "R02", "role_group": "exco", "item_id": k, "score": v, "evidence_class": ev}
        for k, (v, ev) in base.items()
    ]


def test_value_axis_caps(inst, make_responses):
    cap = make_responses(lambda i, n, g: 3)
    rs = cap + responses_from_records(_value_rows(V1=("B", "S"), V2=("≥62%", "none"), V3=(5, "none"), V4=(4, "none")))
    res = score_responses(inst, rs)
    v = {x.item_id: x for x in res.value_axis}
    assert v["V1"].recorded == "A" and v["V1"].capped and "not evidenced" in v["V1"].label
    assert v["V2"].recorded == "12–39%" and v["V2"].capped
    assert v["V3"].recorded == 3 and v["V3"].capped
    assert v["V4"].recorded == 2 and v["V4"].capped
    assert res.value_profile == "V1 A (not evidenced) · V2 12–39% · V3 3 · V4 2"


def test_value_axis_v1_requires_d84_at_least_3(inst, make_responses):
    # full evidence on V1 but D8.4 consensus at 2 → Band A
    cap = make_responses(lambda i, n, g: 2 if i == "D8.4" else 3)
    res = score_responses(inst, cap + responses_from_records(_value_rows()))
    v1 = next(x for x in res.value_axis if x.item_id == "V1")
    assert v1.recorded == "A" and "D8.4" in v1.note
    cap = make_responses(lambda i, n, g: 3)
    res = score_responses(inst, cap + responses_from_records(_value_rows()))
    v = {x.item_id: x for x in res.value_axis}
    assert v["V1"].recorded == "B" and v["V2"].recorded == "≥62%" and v["V3"].recorded == 4 and v["V4"].recorded == 3


def test_value_gap_flag(inst, make_responses):
    ev = {i.id: "+".join(i.evidence_class_required) for i in inst.items}
    cap = make_responses(lambda i, n, g: 4, evidence=ev)  # C = 75 → Scaling
    res = score_responses(inst, cap + responses_from_records(_value_rows(V1=("A", "S+D"))))
    assert res.band == "Scaling" and res.value_gap_flag
    res = score_responses(inst, cap + responses_from_records(_value_rows()))
    assert not res.value_gap_flag
    res = score_responses(inst, make_responses(lambda i, n, g: 3) + responses_from_records(_value_rows(V1=("A", "S+D"))))
    assert not res.value_gap_flag  # Emerging never raises it
