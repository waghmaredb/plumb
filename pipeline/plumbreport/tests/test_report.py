import copy
from pathlib import Path

import pytest
import yaml

from plumbreport import lint as lintmod
from plumbreport.build import build
from plumbreport.data import load_research, load_run, load_storyline
from plumbreport.pages import Folio
from plumbreport.render import check_quotes
from plumbreport.spec import BindingError, bind, load_spec, parse_sensitivity_page

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parents[1]
RUN = REPO / "runs" / "great-eastern" / "2026-10-26-run6"
STORY = REPO / "pipeline" / "plumbdeck" / "exec" / "storylines" / "geh-preread-exec-v4.json"
RESEARCH = REPO / "runs" / "great-eastern" / "2026-10-26-update" / "RESEARCH.md"
SPEC = PKG / "specs" / "geh-deep-dive-v1.yaml"
PDF = Path("/mnt/user-data/attachments/598a1fc4-71d0-5dc6-b611-3434cc77d612/"
           "19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf")
needs_pdf = pytest.mark.skipif(not PDF.exists(), reason="source annual report not available")

VERIFIED = "great-eastern.findings.deploy.4"
BLOCKED = "great-eastern.findings.reg.sg-mas-airm.effective"


@pytest.fixture(scope="module")
def inputs():
    return load_run(RUN), load_storyline(STORY), load_research(RESEARCH)


def mini_spec(blocks, kind="body", extra_sections=()):
    full = load_spec(SPEC)
    return {"report": full["report"], "documents": full["documents"],
            "sections": [{"id": "s", "title": "Test", "kind": kind, "blocks": blocks}, *extra_sections]}


# ------------------------------------------------------------------ printed pages

def test_printed_page_conversion():
    f = Folio(offset=-2, first_pdf=6, last_pdf=239)
    assert f.printed(14) == 12 and f.printed(40) == 38 and f.printed(80) == 78
    assert f.printed(6) == 4 and f.printed(239) == 237
    assert f.printed(5) is None and f.printed(240) is None      # no folio printed
    assert f.label(43) == "p. 41" and f.label(3) == "PDF p. 3"
    assert f.labels([40, 14, 14]) == "pp. 12 and 38"
    assert f.labels([14, 40, 80]) == "pp. 12, 38 and 78"
    with pytest.raises(ValueError):
        f.printed(0)


def test_citation_uses_printed_page(inputs):
    run, story, research = inputs
    m = bind(mini_spec([{"type": "quote", "claim": VERIFIED}]), run, story, research, strict=False)
    q = m["sections"][0]["blocks"][0]
    assert q["source"] == "Annual Report 2025, p. 38"          # PDF page 40
    assert m["sources_main"][0]["pages"] == "p. 38"


# --------------------------------------------------------------- verified-only rule

def test_blocked_claim_refused_in_body(inputs):
    run, story, research = inputs
    assert not run.claims[BLOCKED].verified
    for block in ({"type": "quote", "claim": BLOCKED},
                  {"type": "para", "text": "x", "support": [BLOCKED]},
                  {"type": "uses_table", "rows": [{"stage": "a", "use": "b", "status": "take effect",
                                                   "claim": BLOCKED}]}):
        with pytest.raises(BindingError, match="Only verified statements may be printed"):
            bind(mini_spec([block]), run, story, research, strict=False)


def test_blocked_claim_allowed_only_in_awaiting_section(inputs):
    run, story, research = inputs
    item = {"type": "awaiting", "items": [{"text": "Reported to take effect on 7 October 2027.",
                                            "source_type": "the regulator", "claim": BLOCKED}]}
    m = bind(mini_spec([item], kind="awaiting"), run, story, research, strict=False)
    assert m["binding"]["not_verified_in_awaiting"] == [BLOCKED]
    # the same awaiting block in a body section is refused
    with pytest.raises(BindingError, match="awaiting"):
        bind(mini_spec([item]), run, story, research, strict=False)


def test_storyline_sentence_with_unverified_support_refused(inputs):
    run, story, research = inputs
    s = copy.deepcopy(story)
    s.data["slides"][2]["title"]["support"] = [BLOCKED]          # exec-summary.title
    with pytest.raises(BindingError):
        bind(mini_spec([{"type": "lead", "storyline": "exec-summary.title"}]), run, s, research, strict=False)


def test_awaiting_url_must_be_traceable(inputs):
    run, story, research = inputs
    item = {"type": "awaiting", "items": [{"text": "x", "source_type": "y", "research": "4.1",
                                            "url": "https://example.com/made-up.pdf"}]}
    with pytest.raises(BindingError, match="traceable"):
        bind(mini_spec([item], kind="awaiting"), run, story, research, strict=False)


def test_status_must_be_company_wording(inputs):
    run, story, research = inputs
    row = {"stage": "Claims", "use": "x", "status": "Scaled", "claim": "great-eastern.findings.deploy.2"}
    with pytest.raises(BindingError, match="own wording"):
        bind(mini_spec([{"type": "uses_table", "rows": [row]}]), run, story, research, strict=False)


# ------------------------------------------------------------------------- strict

@needs_pdf
def test_strict_omits_awaiting_section(inputs):
    run, story, research = inputs
    spec = load_spec(SPEC)
    full = bind(spec, run, story, research, strict=False, source_pdf=PDF)
    strict = bind(spec, run, story, research, strict=True, source_pdf=PDF)
    assert "developments" in [s["id"] for s in full["sections"]]
    assert "developments" not in [s["id"] for s in strict["sections"]]
    assert full["sources_awaiting"] and not strict["sources_awaiting"]
    assert full["binding"]["not_verified_in_awaiting"] and not strict["binding"]["not_verified_in_awaiting"]
    from plumbreport.render import render_html
    html = render_html(strict)
    for leaked in ("Monetary Authority", "S$849.5", "7 October 2027", "awaiting source check",
                   "To be confirmed", "mas.gov.sg"):
        assert leaked not in html
    assert "awaiting source check" in render_html(full)
    # sections renumber: hypotheses is 7 in the full build, 6 under --strict
    lab = lambda m: {s["id"]: s["label"] for s in m["sections"]}
    assert lab(full)["hypotheses"] == "7" and lab(strict)["hypotheses"] == "6"


def test_reference_to_omitted_section_fails_in_strict(inputs):
    run, story, research = inputs
    spec = mini_spec([{"type": "para", "text": "See section {sec:dev}."}],
                     extra_sections=[{"id": "dev", "title": "Later", "kind": "awaiting", "blocks": []}])
    assert "See section 2." in repr(bind(spec, run, story, research, strict=False)["sections"])
    with pytest.raises(BindingError, match="not in this build"):
        bind(spec, run, story, research, strict=True)


# --------------------------------------------------------------------------- lint

@pytest.mark.parametrize("bad", [
    "see great-eastern.findings.deploy.4", "3 claims withheld", "the gap register", "item G-1",
    "a T2 source", "publisher hash", "1 attachment unreconciled", "interlock not passed",
    "no QA gate 3 sign-off", "[[FOUNDER: week]]",
])
def test_lint_catches_internal_vocabulary(bad):
    assert lintmod.lint_text(f"<p>Clean text, then {bad}.</p>", "x")


def test_lint_passes_client_language():
    ok = ("<p>Awaiting source check. Source: Annual Report 2025, p. 38. To be confirmed. "
          "https://www.greateasternlife.com/annual-report/great-eastern-holdings-limited-ar-2025.pdf</p>")
    assert lintmod.lint_text(ok, "x") == []


def test_lint_fails_the_build(inputs, tmp_path):
    spec = mini_spec([{"type": "para", "text": "Seven statements were withheld."}])
    p = tmp_path / "spec.yaml"
    p.write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    res = build(p, RUN, STORY, RESEARCH, tmp_path / "out", pdf=False)
    assert not res.ok
    assert any(e["rule"] == "withheld" for e in res.lint["errors"])
    assert not (tmp_path / "out" / "report.pdf").exists()


# ------------------------------------------------------- source re-checks (PDF)

def test_table_figures_need_the_source(inputs):
    run, story, research = inputs
    spec = load_spec(SPEC)
    spec["sections"] = spec["sections"][:1]
    with pytest.raises(BindingError, match="source-pdf"):
        bind(spec, run, story, research, strict=True)


@needs_pdf
def test_sensitivity_read_from_source():
    import subprocess
    t = subprocess.run(["pdftotext", "-layout", "-f", "189", "-l", "189", str(PDF), "-"],
                       capture_output=True, text=True, check=True).stdout
    rows = parse_sensitivity_page(t, "2025")
    assert len(rows) == 7
    assert rows[3]["scenario"] == "Scenario 4 – Accident and Health" and rows[3]["net_pat"] == "99.3"


@needs_pdf
def test_tampered_quotation_is_caught(inputs):
    run, *_ = inputs
    good = {"pdf_page": 40, "text": run.claims[VERIFIED].text, "where": "a"}
    bad = dict(good, text=good["text"].replace("75%", "80%"), where="b")
    errs = check_quotes([good, bad], PDF)
    assert len(errs) == 1 and errs[0].startswith("b:")


@needs_pdf
def test_full_report_binds_both_modes(inputs):
    run, story, research = inputs
    spec = load_spec(SPEC)
    for strict in (False, True):
        m = bind(spec, run, story, research, strict=strict, source_pdf=PDF)
        assert not check_quotes(m["quotes"], PDF)
        assert m["binding"]["not_verified_unaccounted"] == []
        ids = [s["id"] for s in m["sections"]]
        assert ("developments" in ids) is (not strict)


# ------------------------------------------------------------------ deck and report agree

@needs_pdf
def test_report_carries_every_headline_number_on_the_deck(tmp_path):
    """The deck shows numbers; the report is where a reader checks them. Every number on the
    deck face must appear in the report, and the abandoned total-claims anchor must not."""
    import json as _json
    import re as _re
    build(SPEC, RUN, STORY, RESEARCH, tmp_path, strict=True, source_pdf=PDF, pdf=False)
    html = (tmp_path / "report.html").read_text()
    text = _re.sub(r"<[^>]+>", " ", html).replace("&nbsp;", " ")
    story = _json.loads(STORY.read_text())
    nums = set()
    for s in story["slides"]:
        nums |= {t["big"] for t in s.get("tiles", [])}
        nums |= {f["value"] for f in s.get("figures", [])}
        d = s.get("title", {}).get("derived")
        if d:
            nums.add(d["display"])
    missing = [n for n in sorted(nums) if n not in text]
    assert not missing, f"deck numbers absent from the report: {missing}"
    assert "S$40m" not in text and "every 1%" not in text.lower()
