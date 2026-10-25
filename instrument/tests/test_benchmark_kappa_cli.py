import json
import math
import random
import subprocess
import sys
from pathlib import Path

import pytest

from plumbscore.benchmark import BenchmarkRow, load_benchmark, peer_percentile, percentile_rank
from plumbscore.kappa import exact_agreement, kappa_report, weighted_kappa

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"


# ------------------------------------------------------------- percentile
def _rows(n, sector="banking", size="large", start=10.0, step=2.0, population="evidenced", evidence_gated=None):
    out = []
    for i in range(n):
        t = start + i * step
        eg = evidence_gated(i) if evidence_gated else (population == "evidenced")
        out.append(BenchmarkRow(org_id=f"{sector[0].upper()}{i}", sector=sector, size_band=size, dims={f"D{d}": t for d in range(1, 9)}, total=t,
                                evidence_gated=eg, population=population))
    return out


def test_percentile_rank_midrank():
    assert percentile_rank(5, [1, 2, 3, 4]) == 100
    assert percentile_rank(0, [1, 2, 3, 4]) == 0
    assert percentile_rank(3, [1, 2, 3, 4]) == 62.5  # 2 below + 0.5 equal → 2.5/4
    assert percentile_rank(1, []) is None


def test_peer_n_insufficient_falls_back_to_global_and_ranks_named_peers(inst):
    rows = _rows(14) + _rows(30, sector="telco", size="mid", start=50)
    p = peer_percentile(inst, rows, total=40, dim_scores={f"D{d}": 40 for d in range(1, 9)}, sector="banking", size_band="large")
    assert p["scope"] == "global" and not p["peer_n_sufficient"]
    assert p["n"] == 44 and p["n_peer_candidates"] == 14
    assert p["label"].startswith("global, peer n insufficient") and "population: evidenced" in p["label"]
    assert p["total_percentile"] == pytest.approx(100 * 14 / 44)
    # review Blocker 3: with peer n < 15 the deck shows a rank within the named peers, each peer's value visible
    pr = p["peer_rank"]
    assert pr["n"] == 14 and pr["rank"] == 1 and len(pr["peers"]) == 14  # totals 10..36 are all below 40
    assert pr["peers"][0]["total"] == 36.0 and pr["peers"][-1]["total"] == 10.0 and "n=14" in pr["label"]
    p2 = peer_percentile(inst, rows, total=20, dim_scores={}, sector="banking", size_band="large")
    assert p2["peer_rank"]["rank"] == 9  # 8 peers strictly above 20 (22..36)


def test_peer_n_sufficient_uses_peer_set(inst):
    rows = _rows(15) + _rows(30, sector="telco", size="mid", start=50)
    p = peer_percentile(inst, rows, total=20, dim_scores={f"D{d}": 20 for d in range(1, 9)}, sector="banking", size_band="large", peer_set_date="2026-10-01")
    assert p["scope"] == "peer" and p["peer_n_sufficient"] and p["n"] == 15 and p["peer_rank"] is None
    # totals 10,12,...,38: five below 20, one equal → (5 + 0.5)/15
    assert p["total_percentile"] == pytest.approx(100 * 5.5 / 15)
    assert p["dimension_percentiles"]["D1"] == pytest.approx(100 * 5.5 / 15)
    assert p["evidence_gated_share"] == pytest.approx(1.0)
    assert p["peer_set_date"] == "2026-10-01"


def test_no_filters_is_global(inst):
    p = peer_percentile(inst, _rows(20), total=100, dim_scores={})
    assert p["scope"] == "global" and p["total_percentile"] == 100 and "no peer filters" in p["label"]


def test_populations_are_never_pooled(inst):
    """Tier-0 self-scored entries (capped ≤ 3 per item) and evidence-gated engagement entries are
    different populations (review 2026-10-25 Blocker 3)."""
    evidenced = _rows(15)
    selfpool = _rows(20, start=5, step=1, population="self")
    mixed = evidenced + selfpool
    with pytest.raises(ValueError, match="never pooled"):
        peer_percentile(inst, mixed, total=20, dim_scores={}, sector="banking", size_band="large")
    pe = peer_percentile(inst, mixed, total=20, dim_scores={}, sector="banking", size_band="large", population="evidenced")
    assert pe["n"] == 15 and pe["peer_n_sufficient"] and pe["population"]["population"] == "evidenced"
    assert pe["population"]["n_excluded_other_population"] == 20
    ps = peer_percentile(inst, mixed, total=20, dim_scores={}, sector="banking", size_band="large", population="self")
    assert ps["n"] == 20 and ps["population"]["n_excluded_other_population"] == 15 and ps["total_percentile"] != pe["total_percentile"]
    # a homogeneous set needs no population argument; an unknown population is refused
    assert peer_percentile(inst, evidenced, total=20, dim_scores={}, sector="banking", size_band="large")["n"] == 15
    with pytest.raises(ValueError):
        peer_percentile(inst, mixed, total=20, dim_scores={}, population="pooled")
    # population derives from evidence_gated when the column is absent
    legacy = BenchmarkRow(org_id="L", dims={}, total=1.0, evidence_gated=False)
    assert legacy.population == "self" and BenchmarkRow(org_id="L", dims={}, total=1.0).population is None
    with pytest.raises(ValueError):
        BenchmarkRow(org_id="L", dims={}, total=1.0, population="mixed")


def test_example_benchmark_calibration(inst):
    rows = load_benchmark(EX / "benchmark_synthetic_40.csv")
    assert len(rows) == 40
    from plumbscore.scoring import band_for

    leading = sum(1 for r in rows if band_for(inst, r.total) == "Leading")
    assert 0.05 <= leading / 40 <= 0.10  # 3/40 = 7.5%
    for r in rows:  # published total is the exact weighted sum of the dimension scores
        assert r.total == pytest.approx(sum(inst.weights[d] * r.dims[d] for d in inst.weights) / 100, abs=0.006)


# ------------------------------------------------------------------ kappa
def _qwk_reference(a, b):
    """Independent identity: quadratic-weighted κ = 2·cov / (var_a + var_b + (μa − μb)²) (population moments)."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    va = sum((x - ma) ** 2 for x in a) / n
    vb = sum((y - mb) ** 2 for y in b) / n
    return 2 * cov / (va + vb + (ma - mb) ** 2)


def test_kappa_known_pairs():
    assert weighted_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(1.0)
    assert weighted_kappa([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == pytest.approx(-1.0)
    assert weighted_kappa([3, 3, 3], [3, 3, 3]) is None  # no variance → undefined
    assert weighted_kappa([], []) is None
    a = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 2, 3]
    b = [1, 2, 4, 4, 5, 2, 2, 3, 3, 5, 2, 2]
    assert weighted_kappa(a, b) == pytest.approx(_qwk_reference(a, b))
    assert exact_agreement(a, b) == pytest.approx(8 / 12)


def test_kappa_matches_reference_on_random_pairs():
    rng = random.Random(7)
    for _ in range(50):
        a = [rng.randint(1, 5) for _ in range(30)]
        b = [max(1, min(5, x + rng.choice([-1, 0, 0, 1]))) for x in a]
        assert weighted_kappa(a, b) == pytest.approx(_qwk_reference(a, b), abs=1e-12)


def test_kappa_report_subset_and_exit(inst):
    a = {(f"O{o}", it): ((o + i) % 5) + 1 for o in range(10) for i, it in enumerate(inst.kappa_subset)}
    b = dict(a)
    a[("O0", "D9.9")] = 3  # outside the subset: ignored
    b[("O0", "D9.9")] = 1
    rep = kappa_report(inst, a, b)
    assert rep["n_items"] == 20 and rep["n_pairs"] == 200 and rep["n_orgs"] == 10
    assert rep["pooled_kappa_w"] == pytest.approx(1.0) and rep["exit_criterion_met"]
    assert all(i["verdict"] == "accept" for i in rep["items"])
    # drop one item's pairs → missing → exit criterion not met
    for o in range(10):
        del b[(f"O{o}", "D8.4")]
    rep = kappa_report(inst, a, b)
    assert rep["missing_subset_items"] == ["D8.4"] and not rep["exit_criterion_met"]


def test_kappa_verdict_thresholds(inst):
    from plumbscore.kappa import classify

    t = inst.kappa.thresholds
    assert classify(0.70, t) == "accept"
    assert classify(0.69, t) == "rewrite anchors"
    assert classify(0.50, t) == "rewrite anchors"
    assert classify(0.49, t) == "rewrite or drop"
    assert classify(None, t) == "undefined"


# -------------------------------------------------------------------- CLI
def test_cli_score_and_kappa(tmp_path):
    md = tmp_path / "s.md"
    js = tmp_path / "s.json"
    r = subprocess.run(
        [sys.executable, "-m", "plumbscore", "score", str(EX / "responses_harbourline_fictional.csv"), "--benchmark", str(EX / "benchmark_synthetic_40.csv"),
         "--sector", "banking", "--size-band", "large", "--region", "SG", "--org", "Fictional FI", "--out", str(md), "--json", str(js)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    text = md.read_text(encoding="utf-8")
    for h in ("## S08", "## S09", "## S10", "## S11", "production boundary", "percentile"):
        assert h in text
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["n_respondents"] == 12 and data["band"] == "Emerging"
    assert data["percentile"]["peer_n_sufficient"] is True and data["percentile"]["n"] >= 15
    # the example exercises caps, σ flags and the ExCo gap
    assert any(i["cap_flag"] for i in data["items"])
    assert any(i["sigma_flag"] for i in data["items"])
    assert any(d["exco_gap_flag"] for d in data["dimensions"])
    assert data["value_axis"][0]["recorded"] == "A" and data["value_axis"][1]["capped"]
    assert data["percentile"]["population"]["population"] == "evidenced" and "population: evidenced" in text

    # peer n < 15: the scorecard shows the rank-within-named-peers exhibit, no percentile sentence (review Blocker 3)
    r = subprocess.run(
        [sys.executable, "-m", "plumbscore", "score", str(EX / "responses_harbourline_fictional.csv"), "--benchmark", str(EX / "benchmark_synthetic_40.csv"),
         "--sector", "insurance", "--size-band", "mid", "--org", "Fictional FI", "--out", str(md), "--json", str(js)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    text = md.read_text(encoding="utf-8")
    assert "within the named peer set" in text and "| Rank | Organisation |" in text and "percentile overall" not in text
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["percentile"]["peer_rank"] and not data["percentile"]["peer_n_sufficient"]

    r = subprocess.run([sys.executable, "-m", "plumbscore", "kappa", str(EX / "rater_a.csv"), str(EX / "rater_b.csv")], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "Pooled κw" in r.stdout and "| D8.4 |" in r.stdout


def test_cli_rejects_bad_score(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("respondent_id,role_group,item_id,score,evidence_class,evidence_ref\nR1,exco,D1.1,6,none,\n")
    r = subprocess.run([sys.executable, "-m", "plumbscore", "score", str(bad)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "outside 1–5" in (r.stderr + r.stdout)


def test_benchmark_requires_region(tmp_path):
    """v0.2 decision 7: region is optional as a filter but required in every benchmark row."""
    hdr = "org_id,sector,size_band,{}D1,D2,D3,D4,D5,D6,D7,D8,total\n"
    vals = ",".join(["50"] * 9)
    p = tmp_path / "b.csv"
    p.write_text(hdr.format("") + f"O1,banking,large,{vals}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="region"):
        load_benchmark(p)
    p.write_text(hdr.format("region,") + f"O1,banking,large,,{vals}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty region"):
        load_benchmark(p)
    p.write_text(hdr.format("region,") + f"O1,banking,large,SG,{vals}\n", encoding="utf-8")
    assert load_benchmark(p)[0].region == "SG"


def test_percentile_ties_mid_rank_all_equal():
    """v0.2 decision 6: tied organisations share one value; an all-equal set places everyone at the 50th."""
    assert percentile_rank(40, [40, 40, 40, 40]) == 50
    assert percentile_rank(40, [30, 40, 40, 50]) == 50
