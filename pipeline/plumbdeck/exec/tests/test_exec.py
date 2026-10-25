import json, sys
from pathlib import Path
import pytest

EXEC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXEC))
from resolve_storyline import resolve, StorylineError  # noqa: E402
from face_lint import lint  # noqa: E402

RUN = EXEC.parents[2] / "runs" / "great-eastern" / "2026-10-25-run5"
STORY = EXEC / "storylines" / "geh-preread-exec-v1.json"
pytestmark = pytest.mark.skipif(not RUN.exists(), reason="run 5 not present")


def _story():
    return json.loads(STORY.read_text())


def test_storyline_resolves_and_is_draft_without_signoff():
    story, rows, lock = resolve(_story(), RUN, None, None)
    assert story["_status"]["final"] is False
    assert story["_status"]["marker"] == "Discussion draft"
    assert all(s.get("_source", "").startswith("Source: ") for s in story["slides"] if s["id"] in ("exec-summary", "value-chain", "outcomes"))


def test_withheld_claim_cannot_back_face_text():
    s = _story()
    s["slides"][1]["points"][0]["body"]["support"].append("great-eastern.findings.reg.sg-mas-airm.effective")
    with pytest.raises(StorylineError, match="WITHHELD"):
        resolve(s, RUN, None, None)


def test_synthesis_without_support_is_refused():
    s = _story()
    s["slides"][1]["points"][0]["body"]["support"] = []
    with pytest.raises(StorylineError, match="no supporting claim"):
        resolve(s, RUN, None, None)


def test_face_lint_clean_on_storyline_and_catches_leaks():
    story, _, _ = resolve(_story(), RUN, None, None)
    assert lint(story) == []
    story["slides"][1]["points"][0]["body"]["text"] += " (4 claims withheld, see gap register G-1)"
    assert lint(story)


RUN6 = EXEC.parents[2] / "runs" / "great-eastern" / "2026-10-26-run6"
STORY2 = EXEC / "storylines" / "geh-preread-exec-v2.json"


@pytest.mark.skipif(not RUN6.exists(), reason="run 6 not present")
def test_v2_resolves_with_printed_pages_and_founder_inputs_block_final():
    story, rows, lock = resolve(json.loads(STORY2.read_text()), RUN6, None, None)
    st = story["_status"]
    assert st["final"] is False and st["marker"] == "Discussion draft"
    assert len(st["founder_inputs"]) == 4
    src = {s["id"]: s.get("_source", "") for s in story["slides"]}
    assert "pp. 12, 38" in src["outcomes"]  # printed folios, not PDF pages 14, 40
    assert lint(story) == []


STORY3 = EXEC / "storylines" / "geh-preread-exec-v3.json"
AR_PDF = Path("/mnt/user-data/attachments/598a1fc4-71d0-5dc6-b611-3434cc77d612/19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf")
v3 = pytest.mark.skipif(not (RUN6.exists() and AR_PDF.exists()), reason="run 6 or attached AR not present")


@v3
def test_v3_figures_verified_and_pending_slides_block_final():
    story, _, _ = resolve(json.loads(STORY3.read_text()), RUN6, AR_PDF, None)
    st = story["_status"]
    assert st["final"] is False
    assert set(st["pending_slides"]) == {"peers", "mas-clock"}
    src = {s["id"]: s.get("_source", "") for s in story["slides"]}
    assert "p. 145" in src["value-base"]  # PDF 147 -> printed 145
    assert lint(story) == []


@v3
def test_v3_wrong_figure_is_refused():
    s = json.loads(STORY3.read_text())
    vb = next(x for x in s["slides"] if x["id"] == "value-base")
    vb["figures"][0]["value"] = "4,133.8"
    with pytest.raises(StorylineError, match="not found on PDF page"):
        resolve(s, RUN6, AR_PDF, None)


@v3
def test_v3_figure_without_pdf_is_refused():
    with pytest.raises(StorylineError, match="needs --pdf"):
        resolve(json.loads(STORY3.read_text()), RUN6, None, None)


@v3
def test_v3_word_budget_enforced():
    s = json.loads(STORY3.read_text())
    s["slides"][8]["cards"][0]["text"] = " ".join(["word"] * 40)
    with pytest.raises(StorylineError, match="word"):
        resolve(s, RUN6, AR_PDF, None)
