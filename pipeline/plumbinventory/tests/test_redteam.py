"""Tests for the source red-team gate: no web claim reaches a page unless an independent check confirmed it."""
import json
import shutil
from pathlib import Path

import pytest
import yaml

from plumbinventory.build import build
from plumbinventory.redteam import claim_status, cmd_merge, cmd_prompt, latest

REPO = Path(__file__).resolve().parents[3]
RUN = REPO / "runs/great-eastern/2026-11-06-inventory"


def _round(key, cid, verdict, checker="independent-agent", excerpt="x y z"):
    return {"checker": checker, "checked_at": "2026-11-06",
            "sources": [{"key": key, "claims": [{"id": cid, "verdict": verdict, "excerpt": excerpt, "note": ""}]}]}


def test_later_round_overrides_earlier():
    view = latest({"rounds": [_round("s", "c1", "PARTIAL"), _round("s", "c1", "SUPPORTED")]})
    assert claim_status(view, {}, "s", "c1", "internal")[0]


def test_only_supported_passes():
    for v in ("PARTIAL", "NOT_SUPPORTED", "WRONG_ENTITY", "UNREACHABLE"):
        ok, reason, _ = claim_status(latest({"rounds": [_round("s", "c1", v)]}), {}, "s", "c1", "internal")
        assert not ok and v in reason


def test_unchecked_claim_is_blocked():
    assert not claim_status({}, {}, "s", "c1", "internal")[0]


def test_client_profile_requires_refetch_match():
    view = latest({"rounds": [_round("s", "c1", "SUPPORTED")]})
    assert not claim_status(view, {}, "s", "c1", "client")[0]
    assert not claim_status(view, {"s": {"c1": "MISMATCH"}}, "s", "c1", "client")[0]
    assert claim_status(view, {"s": {"c1": "MATCH"}}, "s", "c1", "client")[0]


@pytest.fixture
def run_copy(tmp_path):
    """Copy of the GEH inventory run inside a fake repo, so tests can change verdicts freely."""
    if not RUN.exists():
        pytest.skip("GEH run not present")
    fake = tmp_path / "repo"
    dst = fake / "runs/great-eastern/2026-11-06-inventory"
    shutil.copytree(RUN, dst)
    src_run = REPO / "runs/great-eastern/2026-10-26-run6"
    (fake / "runs/great-eastern/2026-10-26-run6").mkdir(parents=True)
    shutil.copy(src_run / "report.json", fake / "runs/great-eastern/2026-10-26-run6/report.json")
    return dst


def test_geh_internal_build_uses_only_supported(run_copy, tmp_path):
    out = build(run_copy / "candidates.yaml", tmp_path / "o")
    assert out["summary"]["failures"] == []
    r = out["redteam"]
    assert r["used"] == r["used_passed"] > 0
    for e in out["entries"]:
        if e.get("secondary"):
            assert len(e["secondary"]["verified"]) == len(e["secondary"]["claims"])
    # the claim the red team would not confirm never appears in a used note
    assert all(c["claim_id"] != "c6" or c["source"] != "ocbc-ar2025" for e in out["entries"]
               for c in (e.get("secondary") or {}).get("verified", []))


def test_downgraded_claim_withholds_secondary_only_row(run_copy, tmp_path):
    checks = json.loads((run_copy / "source_checks.json").read_text())
    checks["rounds"].append(_round("panda-gerica", "c6", "NOT_SUPPORTED"))
    (run_copy / "source_checks.json").write_text(json.dumps(checks))
    out = build(run_copy / "candidates.yaml", tmp_path / "o")
    assert "inv-11" not in {e["id"] for e in out["entries"]}
    assert any(w["id"] == "inv-11" for w in out["withheld"])


def test_downgrade_keeps_row_with_annual_report_evidence(run_copy, tmp_path):
    checks = json.loads((run_copy / "source_checks.json").read_text())
    checks["rounds"].append(_round("job-daie", "c3", "PARTIAL"))
    (run_copy / "source_checks.json").write_text(json.dumps(checks))
    out = build(run_copy / "candidates.yaml", tmp_path / "o")
    row = next(e for e in out["entries"] if e["id"] == "inv-14")
    assert "secondary" not in row and row["evidence"]


def test_merge_refuses_self_check(run_copy, tmp_path):
    f = tmp_path / "self.json"
    f.write_text(json.dumps(_round("pega2024", "c1", "SUPPORTED", checker="claude-main-session")))
    with pytest.raises(SystemExit):
        cmd_merge(run_copy / "candidates.yaml", f)


def test_prompt_carries_claims_not_reasoning(run_copy, tmp_path):
    out = tmp_path / "brief.md"
    cmd_prompt(run_copy / "candidates.yaml", out)
    text = out.read_text()
    assert "PROVE THEM WRONG" in text and "pega2024" in text
    spec = yaml.safe_load((run_copy / "candidates.yaml").read_text())
    # entry notes and why_it_matters (our reasoning) are not in the brief
    assert spec["entries"][9]["secondary"]["note"] not in text
