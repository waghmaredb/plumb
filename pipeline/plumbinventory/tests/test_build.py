"""Tests for plumbinventory: the build must block drift, wrong pages and fragment figure matches."""
import json
from pathlib import Path

import pytest
import yaml

from plumbinventory.build import build, check_figure, check_quote, norm

REPO = Path(__file__).resolve().parents[3]
GEH = REPO / "runs/great-eastern/2026-11-06-inventory/candidates.yaml"

PAGES = [
    "Letter \n We rolled out a proprietary AI- powered platform to automate medical claims.",
    "Table 15.9 (8.2) 5.9 138.3",
]


def test_norm_rejoins_hyphen_breaks_and_quote_marks():
    assert norm("AI- powered  “x” Singapore’s") == "AI-powered \"x\" Singapore's"


def test_quote_matches_on_its_page_only():
    assert check_quote(PAGES, 1, "proprietary AI-powered platform")["ok"]
    res = check_quote(PAGES, 2, "proprietary AI-powered platform")
    assert not res["ok"] and res["found_on"] == [1]


def test_paraphrase_drift_is_blocked():
    # red-team 2026-11-02 §2: "settled same day" is not what the source says
    assert not check_quote(PAGES, 1, "proprietary AI-powered platform to settle medical claims")["ok"]


def test_figure_is_a_whole_token():
    assert check_figure(PAGES, 2, "5.9")["ok"]
    assert check_figure(PAGES, 2, "15.9")["ok"]
    assert not check_figure(PAGES, 2, "5.5")["ok"]
    # "5.9" must not be satisfied by "15.9" alone
    assert not check_figure(["Table 15.9 only"], 1, "5.9")["ok"]


@pytest.mark.skipif(not GEH.exists(), reason="GEH run not present")
def test_geh_inventory_builds_clean(tmp_path):
    out = build(GEH, tmp_path)
    s = out["summary"]
    assert s["failures"] == []
    assert s["checks_passed"] == s["checks"] > 0
    for e in out["entries"]:
        for ev in e["evidence"]:
            assert ev["link"].endswith(f"#page={ev['pdf_page']}")
            assert ev["printed_page"] == ev["pdf_page"] - 2


@pytest.mark.skipif(not GEH.exists(), reason="GEH run not present")
def test_geh_wrong_page_fails(tmp_path):
    spec = yaml.safe_load(GEH.read_text())
    spec["entries"][0]["evidence"][0]["pdf_page"] = 15
    bad = GEH.parent / "_bad_candidates.yaml"
    try:
        bad.write_text(yaml.safe_dump(spec, allow_unicode=True))
        out = build(bad, tmp_path)
        assert any("PDF p.15" in f for f in out["summary"]["failures"])
    finally:
        bad.unlink(missing_ok=True)
