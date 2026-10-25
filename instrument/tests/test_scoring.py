import math

import pytest

from conftest import full_evidence
from plumbscore.responses import responses_from_records
from plumbscore.scoring import apply_cap, band_for, score_responses


# ---------------------------------------------------------------- cap rule
def _resp(item_id, score, ev="none", rid="R1", grp="exco", ref="", interviewees=None):
    return responses_from_records(
        [{"respondent_id": rid, "role_group": grp, "item_id": item_id, "score": score, "evidence_class": ev,
          "evidence_ref": ref, "interviewees": interviewees}]
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
    it2 = inst.item_by_id["D4.4"]  # I (≥2) + O
    assert apply_cap(it2, _resp("D4.4", 4, "I")) == (3, True)
    # v0.2 decision 11: one interview reference is not two independent interviewees
    assert apply_cap(it2, _resp("D4.4", 4, "I+O")) == (3, True)
    assert apply_cap(it2, _resp("D4.4", 4, "I+O", interviewees=2)) == (4, False)
    assert apply_cap(it2, _resp("D4.4", 4, "I+O"), interview_verified=True) == (4, False)
    assert apply_cap(it2, _resp("D4.4", 4, "I", interviewees=3)) == (3, True)  # O still missing


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
    ev, iv = full_evidence(inst)
    res4 = score_responses(inst, make_responses(lambda i, n, g: 4, evidence=ev, interviewees=iv))
    assert res4.capability_score == 75.0 and res4.band == "Scaling"
    # one item lifted to 5 pushes the weighted mean above 4.0 → Leading
    res = score_responses(inst, make_responses(lambda i, n, g: 5 if i == "D8.1" else 4, evidence=ev, interviewees=iv))
    assert res.capability_score > 75 and res.band == "Leading"


@pytest.mark.parametrize("level,expected_c,band", [(2, 25.0, "Stagnating"), (3, 50.0, "Emerging"), (4, 75.0, "Scaling")])
def test_band_edges_exactly_25_50_75_end_to_end(inst, make_responses, level, expected_c, band):
    """v0.2 decision 1: upper-inclusive edges — a score of exactly 25 / 50 / 75 is in the lower band."""
    ev, iv = full_evidence(inst)
    res = score_responses(inst, make_responses(lambda i, n, g: level, evidence=ev, interviewees=iv))
    assert res.capability_score == expected_c and res.band == band
    assert res.self_view_score == expected_c and res.self_view_band == band


def test_band_intervals_in_yaml(inst):
    bl = inst.band_list
    assert [b.interval for b in bl] == ["0 ≤ C ≤ 25", "25 < C ≤ 50", "50 < C ≤ 75", "75 < C ≤ 100"]
    assert [b.high for b in bl] == [25, 50, 75, 100] and [b.low for b in bl] == [0, 25, 50, 75]
    shares = [float(b.target_share.split("%")[0]) for b in bl]
    assert shares == [15, 45, 32.5, 7.5] and sum(shares) == 100  # decision 9


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
    # v0.2 decision 3: item score = median of capped responses (7 operating 1s outvote 5 capped 3s)
    assert d5.mean == pytest.approx(1.0)
    d5_items = [i for i in score_responses(inst, rs).items if i.dimension == "D5"]
    assert all(i.score == 1 and i.mean_capped == pytest.approx((5 * 3 + 7 * 1) / 12) for i in d5_items)


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
    ev, iv = full_evidence(inst)
    cap = make_responses(lambda i, n, g: 4, evidence=ev, interviewees=iv)  # C = 75 → Scaling
    res = score_responses(inst, cap + responses_from_records(_value_rows(V1=("A", "S+D"))))
    assert res.band == "Scaling" and res.value_gap_flag
    res = score_responses(inst, cap + responses_from_records(_value_rows()))
    assert not res.value_gap_flag
    res = score_responses(inst, make_responses(lambda i, n, g: 3) + responses_from_records(_value_rows(V1=("A", "S+D"))))
    assert not res.value_gap_flag  # Emerging never raises it


# ------------------------------------------------- v0.2: median aggregation
def test_median_aggregation_robust_to_enthusiasts(inst, make_responses):
    """v0.2 decision 3: two evidenced 5s among twelve respondents do not move the item off the team's 2."""
    lvl = lambda i, n, g: (5 if n in (1, 2) else 2) if i == "D1.1" else 3
    rs = make_responses(lvl, evidence={("R01", "D1.1"): "D", ("R02", "D1.1"): "D"})
    ir = next(i for i in score_responses(inst, rs).items if i.item_id == "D1.1")
    assert ir.capped_scores.count(5) == 2 and ir.n_capped == 0  # evidence lifts both 5s
    assert ir.score == 2.0  # median
    assert ir.mean_capped == pytest.approx((2 * 5 + 10 * 2) / 12)  # 2.5, shown as secondary only
    d1 = next(d for d in score_responses(inst, rs).dimensions if d.id == "D1")
    assert d1.mean == pytest.approx((2 + 5 * 3) / 6)


def test_median_even_count_gives_half_level(inst, make_responses):
    rs = make_responses(lambda i, n, g: [1, 2, 3, 3, 3, 3][n - 1] if i == "D2.2" else 3, n_exco=3, n_oper=3)
    ir = next(i for i in score_responses(inst, rs).items if i.item_id == "D2.2")
    assert ir.score == 3.0
    rs = make_responses(lambda i, n, g: [1, 2, 3, 3][n - 1] if i == "D2.2" else 3, n_exco=2, n_oper=2)
    ir = next(i for i in score_responses(inst, rs).items if i.item_id == "D2.2")
    assert ir.score == 2.5 and ir.mean_capped == pytest.approx(2.25)


def test_self_view_and_evidenced_view(inst, make_responses):
    """md §1: self-view (median raw) beside the evidenced view (median capped); the latter is the score of record."""
    res = score_responses(inst, make_responses(lambda i, n, g: 4))
    assert res.self_view_score == 75.0 and res.self_view_band == "Scaling"
    assert res.capability_score == 50.0 and res.band == "Emerging"
    assert all(i.score_self == 4 and i.score == 3 for i in res.items)


def test_v1_dependency_uses_d84_median(inst, make_responses):
    """v0.2 decision 10: V1 ↔ D8.4 checked on the D8.4 organisation item score (median), not the mean."""
    rows = [{"respondent_id": "R02", "role_group": "exco", "item_id": "V1", "score": "B", "evidence_class": "S+D"}]
    # D8.4: 7 operating at 2, 5 ExCo at 4 with D evidence → mean 2.83, median 2 → V1 not evidenced
    lvl = lambda i, n, g: (4 if g == "exco" else 2) if i == "D8.4" else 3
    rs = make_responses(lvl, evidence={"D8.4": "D"}) + responses_from_records(rows)
    res = score_responses(inst, rs)
    d84 = next(i for i in res.items if i.item_id == "D8.4")
    assert d84.score == 2 and d84.mean_capped > 2.5
    assert next(v for v in res.value_axis if v.item_id == "V1").recorded == "A"


# ------------------------------------------------ v0.2: I (≥2) verification
def _iv_rows(refs, interviewees=None, ev="I+D", item="D7.2"):
    return responses_from_records(
        [{"respondent_id": f"R{k:02d}", "role_group": "exco", "item_id": item, "score": 5, "evidence_class": ev,
          "evidence_ref": ref, "interviewees": interviewees} for k, ref in enumerate(refs, start=1)]
    )


def test_interview_evidence_needs_two_verifiable_interviewees(inst, make_responses):
    base = make_responses(lambda i, n, g: 3, items=[i.id for i in inst.items if i.id != "D7.2"])
    # one interview reference repeated on every row → not verifiable → capped, I not counted as evidence
    res = score_responses(inst, base + _iv_rows(["EV-1 interview BU head A"] * 5))
    ir = next(i for i in res.items if i.item_id == "D7.2")
    assert ir.interview_refs == 1 and ir.interview_verified is False
    assert ir.n_capped == 5 and ir.score == 3 and ir.evidence_classes_logged == ["D"]
    # two distinct interview references → verified → lifted
    res = score_responses(inst, base + _iv_rows(["EV-1 interview BU head A", "EV-2 interview BU head B"]))
    ir = next(i for i in res.items if i.item_id == "D7.2")
    assert ir.interview_refs == 2 and ir.interview_verified is True
    assert ir.n_capped == 0 and ir.score == 5 and ir.evidence_classes_logged == ["D", "I"]
    # one reference that records two interviewees (interviewees column) → verified
    res = score_responses(inst, base + _iv_rows(["EV-3 joint note, 2 BU heads"], interviewees=2))
    ir = next(i for i in res.items if i.item_id == "D7.2")
    assert ir.interview_verified is True and ir.score == 5
    # an item without any I row reports None
    assert next(i for i in res.items if i.item_id == "D1.1").interview_verified is None


def test_interviewees_column_loads_from_csv(tmp_path, inst):
    from plumbscore.responses import load_responses

    p = tmp_path / "r.csv"
    p.write_text("respondent_id,role_group,item_id,score,evidence_class,evidence_ref,interviewees\n"
                 "R1,exco,D4.4,4,I+O,EV-9,2\nR2,operating,D4.4,2,none,,\n", encoding="utf-8")
    rs = load_responses(p)
    assert rs[0].interviewees == 2 and rs[1].interviewees is None
    p.write_text("respondent_id,role_group,item_id,score,interviewees\nR1,exco,D4.4,4,two\n", encoding="utf-8")
    with pytest.raises(ValueError, match="interviewees"):
        load_responses(p)


# ------------------------------------------------------- v0.2: V2 share edges
@pytest.mark.parametrize(
    "share,code",
    [(0, "<12%"), (11.99, "<12%"), (12, "12–39%"), (39, "12–39%"), (39.01, "40–61%"), (39.5, "40–61%"),
     (40, "40–61%"), (61, "40–61%"), (61.5, "≥62%"), (62, "≥62%"), (100, "≥62%")],
)
def test_v2_share_edges_upper_inclusive(inst, share, code):
    assert inst.value_item_by_id["V2"].band_for_share(share) == code


def test_v2_numeric_share_in_responses(inst, make_responses):
    rows = [{"respondent_id": "R02", "role_group": "exco", "item_id": "V2", "score": "61.5%", "evidence_class": "S"}]
    res = score_responses(inst, make_responses(lambda i, n, g: 3) + responses_from_records(rows))
    assert next(v for v in res.value_axis if v.item_id == "V2").recorded == "≥62%"
    rows[0]["evidence_class"] = "none"
    res = score_responses(inst, make_responses(lambda i, n, g: 3) + responses_from_records(rows))
    assert next(v for v in res.value_axis if v.item_id == "V2").recorded == "12–39%"  # self-report cap
