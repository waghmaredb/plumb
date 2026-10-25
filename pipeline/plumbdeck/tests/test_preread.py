"""Pre-read spec (P5): claim-bound slides, questions not findings, withheld rendering, labelled offer text."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from plumbdeck.build import build_deck, write_outputs
from plumbdeck.lint import MAX_TITLE_WORDS, lint_dir, title_words
from plumbdeck.spec import SpecError, load_spec

from conftest import PKG, REPO

RUN5 = REPO / "runs" / "great-eastern" / "2026-10-25-run5"
PRE = PKG / "specs" / "plumb-prospect-preread-v0.1.yaml"
FULL = PKG / "specs" / "plumb-assessment-v0.1.yaml"

pytestmark = pytest.mark.skipif(not (RUN5 / "report.json").is_file(), reason="run 5 outputs not present")


def _copy_run(tmp: Path, mutate=None) -> Path:
    d = tmp / "run"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir()
    rep = json.loads((RUN5 / "report.json").read_text())
    if mutate:
        mutate(rep)
    (d / "report.json").write_text(json.dumps(rep))
    shutil.copy(RUN5 / "claims.json", d / "claims.json")
    return d


def _withhold(*suffixes):
    def m(rep):
        rep["released_claim_ids"] = [c for c in rep["released_claim_ids"] if not any(c.endswith(s) for s in suffixes)]
        for d in rep["verification"]["decisions"]:
            if any(d["claim_id"].endswith(s) for s in suffixes):
                d["blocked"] = True
                d["reasons"] = ["no citation reaches the support threshold (C4)"]
    return m


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("pre")
    deck = build_deck(PRE, RUN5)
    rep = write_outputs(deck, out)
    return deck, rep, out


def test_spec_loads_with_11_ids(built):
    spec = load_spec(PRE)
    assert [s.id for s in spec.slides] == ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "A1"]


def test_lint_zero_errors_and_titles_short(built):
    deck, rep, out = built
    assert rep["ok"], rep["errors"]
    assert all(title_words(s.title) <= MAX_TITLE_WORDS for s in deck.slides if not s.title_exempt)
    # the only placeholder is the slide whose claims are all withheld
    assert [s.id for s in deck.slides if s.kind == "placeholder"] == ["S07"]
    assert all(s.placeholder_reason == "withheld" for s in deck.slides if s.kind == "placeholder")


def test_regulatory_clock_withheld_offline(built):
    deck, _, _ = built
    s07 = next(s for s in deck.slides if s.id == "S07")
    assert s07.title.startswith("[H]") and "withheld" in s07.title
    text = " ".join(getattr(b, "text", "") for b in s07.blocks)
    assert "Withheld — see gap register G-" in text and "2027" not in text


def test_slides_bind_released_claims_verbatim(built):
    deck, _, out = built
    run = deck.run
    s04 = next(s for s in deck.slides if s.id == "S04")
    assert s04.bound_claims and all(run.claims[c].released for c in s04.bound_claims)
    table = s04.blocks[0]
    for row in table.rows:
        assert row[1].startswith("“")  # verbatim quotation, nothing typed
    assert "one still in testing" in s04.title
    s05 = next(s for s in deck.slides if s.id == "S05")
    assert "Group Data and AI seat is in transition" in s05.title


def test_governance_observation_only_as_a_question(built):
    deck, _, out = built
    md = (out / "deck-DRAFT.md").read_text()
    s08 = next(s for s in deck.slides if s.id == "S08")
    assert s08.section == "Questions for management"
    t = s08.blocks[0]
    q1 = t.rows[0]
    assert q1[0] == "Q1 (observation)" and q1[1].endswith("?") and "Observation, not a finding" in q1[2]
    assert any("Limitations:" in getattr(b, "text", "") for b in s08.blocks)
    # the observation never becomes a title or a statement elsewhere
    for s in deck.slides:
        assert "governance" not in s.title.lower() or s.id == "S08"
    assert "Governance = 0" not in md and "governance is 0" not in md.lower()
    s06 = next(s for s in deck.slides if s.id == "S06")
    gov_row = next(r for r in s06.blocks[0].left[0].rows if r[0] == "governance")
    assert gov_row[2] == "see note" and "not a score" in gov_row[3]


def test_question_with_withheld_basis_shows_gap_id(built):
    deck, _, _ = built
    rows = next(s for s in deck.slides if s.id == "S08").blocks[0].rows
    wh = [r for r in rows if r[1].startswith("Withheld — see gap register")]
    assert len(wh) == 1 and "MAS" not in wh[0][1]


def test_scqa_placeholder_for_withheld_claim(built):
    deck, _, _ = built
    s03 = next(s for s in deck.slides if s.id == "S03")
    boxes = dict(s03.blocks[0].boxes)
    comp = next(v for k, v in boxes.items() if k.startswith("Complication"))
    assert any("Placeholder for a withheld claim: Withheld — see gap register G-" in p.text for p in comp)
    ans = next(v for k, v in boxes.items() if k.startswith("Answer"))
    assert all(p.text.startswith("Offer — not a finding") for p in ans)


def test_offer_slide_is_labelled(built):
    deck, _, out = built
    s09 = next(s for s in deck.slides if s.id == "S09")
    assert s09.kind == "offer" and s09.blocks[0].text.startswith("Offer — not a finding")


def test_title_falls_back_when_its_claim_is_withheld(tmp_path):
    run = _copy_run(tmp_path, _withhold(".findings.leadership.successor"))
    deck = build_deck(PRE, run)
    s05 = next(s for s in deck.slides if s.id == "S05")
    assert s05.title.startswith("[H]") and "successor" not in s05.title
    row = next(r for r in s05.blocks[0].rows if r[1].startswith("Withheld"))
    assert row[1].startswith("Withheld — see gap register G-")
    s03 = next(s for s in deck.slides if s.id == "S03")
    assert s03.title.startswith("[H]")
    rep = write_outputs(deck, tmp_path / "out")
    assert rep["ok"], rep["errors"]  # including the withheld-text leak check


def test_offer_exhibit_refused_on_a_data_slide(tmp_path):
    import yaml

    raw = yaml.safe_load(PRE.read_text())
    s09 = next(s for s in raw["slides"] if s["id"] == "S09")
    s09["kind"] = "data"
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(SpecError):
        load_spec(p)


def test_full_assessment_spec_still_builds_on_run5(tmp_path):
    deck = build_deck(FULL, RUN5)
    rep = write_outputs(deck, tmp_path / "full")
    assert rep["ok"], rep["errors"]
