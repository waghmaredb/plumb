"""Interlock truth table (ghost deck R8/R9, evidence-pack §12.1, pipeline S8)."""
import pytest

from plumbdeck.build import build_deck, write_outputs
from plumbdeck.interlock import compute_interlock
from plumbdeck.runio import RunData

from conftest import OPERATOR, RUN3, SPEC, make_run, make_signoff


def _il(run_dir, signoff):
    return compute_interlock(RunData(run_dir), signoff)


def test_all_conditions_met_is_final(tmp):
    run = make_run(tmp)
    il = _il(run, make_signoff(tmp, run))
    assert il.passed and il.reasons == [] and il.banner is None
    assert il.signoff_status == "approved"


# each failing condition alone -> DRAFT with exactly that reason
CASES = [
    ("internal profile", dict(profile="internal"), {}, ["internal profile"]),
    ("attachment pending", dict(recon=None), {}, ["1 attachment unreconciled"]),
    ("attachment UNAVAILABLE", dict(recon="UNAVAILABLE"), {}, ["1 attachment unreconciled"]),
    ("attachment MISMATCH", dict(recon="MISMATCH"), {}, ["1 attachment mismatched"]),
    ("resolution below 1", dict(resolution=0.95), {}, ["resolution 0.95"]),
    ("no sign-off", {}, None, ["no QA gate 3 sign-off"]),
    ("decision returned", {}, dict(decision="returned"), ["QA gate 3 decision: returned"]),
    ("reviewer is operator", {}, dict(reviewer={"name": OPERATOR, "role": "x"}), [f"QA gate 3 reviewer is the run operator ({OPERATOR})"]),
    ("reviewer is operator, case/space variant", {}, dict(reviewer="  deepak   WAGHMARE "), ["QA gate 3 reviewer is the run operator (deepak   WAGHMARE)"]),
    ("independence not attested", {}, dict(independence_attestation=False), ["QA gate 3 reviewer independence not attested"]),
    ("sign-off for another run", {}, dict(run_id="research-000000000000"), None),
    ("sign-off missing fields", {}, dict(sample=None, date=None), ["QA gate 3 sign-off missing date, sample"]),
]


@pytest.mark.parametrize("name,run_kw,so_kw,expected", CASES, ids=[c[0] for c in CASES])
def test_single_failure_gives_draft_with_reason(tmp, name, run_kw, so_kw, expected):
    run = make_run(tmp, **run_kw)
    so = None if so_kw is None else make_signoff(tmp, run, **so_kw)
    il = _il(run, so)
    assert not il.passed
    if expected is None:
        assert len(il.reasons) == 1 and "is for run research-000000000000" in il.reasons[0]
    else:
        assert il.reasons == expected
    assert il.banner.startswith("DRAFT — not for board use (")


def test_missing_signoff_file_is_draft(tmp):
    run = make_run(tmp)
    il = _il(run, tmp / "nope.yaml")
    assert not il.passed and il.reasons == ["QA gate 3 sign-off file not found (nope.yaml)"]


def test_operator_unrecorded_blocks_signoff(tmp):
    def strip(rep):
        for a in rep["attached_documents"]:
            a.pop("supplied_by", None)
        for s in rep["verification"]["sources"]:
            (s.get("provenance") or {}).pop("supplied_by", None)
    run = make_run(tmp, mutate=strip)
    il = _il(run, make_signoff(tmp, run))
    assert il.reasons == ["run operator not recorded; QA gate 3 reviewer independence cannot be checked"]


def test_metrics_never_understate_attachment_problems(tmp):
    def bump(rep):
        rep["verification"]["metrics"]["attached_unreconciled"] = 2
    run = make_run(tmp, mutate=bump)
    il = _il(run, make_signoff(tmp, run))
    assert il.reasons == ["2 attachments unreconciled"]


def test_geh_run3_reasons_exact():
    il = _il(RUN3, None)
    assert "; ".join(il.reasons) == "internal profile; 1 attachment unreconciled; resolution 0.2; no QA gate 3 sign-off"
    assert il.outcome_sentence == "Released: 10 claims. Withheld: 4 claims (listed)."


def test_several_failures_listed_in_order(tmp):
    run = make_run(tmp, profile="internal", recon=None, resolution=0.5)
    il = _il(run, make_signoff(tmp, run, reviewer=OPERATOR))
    assert il.reasons == ["internal profile", "1 attachment unreconciled", "resolution 0.5",
                          f"QA gate 3 reviewer is the run operator ({OPERATOR})"]


def test_build_final_vs_draft_files(tmp):
    run = make_run(tmp)
    final = build_deck(SPEC, run, signoff=make_signoff(tmp, run))
    write_outputs(final, tmp / "out")
    assert (tmp / "out" / "deck.pptx").exists() and (tmp / "out" / "deck.md").exists()
    # same folder rebuilt as draft: the final-named files must disappear
    draft = build_deck(SPEC, run, signoff=None)
    write_outputs(draft, tmp / "out")
    assert not (tmp / "out" / "deck.pptx").exists() and not (tmp / "out" / "deck.md").exists()
    assert (tmp / "out" / "deck-DRAFT.pptx").exists() and (tmp / "out" / "deck-DRAFT.md").exists()
