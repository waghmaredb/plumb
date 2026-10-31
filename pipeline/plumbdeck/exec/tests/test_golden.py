"""Great Eastern v4 is the quality benchmark (founder, 2026-10-26).

These tests freeze what the benchmark says and how it is built, so later changes to the
pipeline cannot quietly lower the bar. An intentional change to the benchmark is made by
re-running with PLUMB_UPDATE_GOLDEN=1 and reviewing the diff of golden/geh-preread-v4.json.
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EXEC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXEC))
from resolve_storyline import resolve  # noqa: E402
from deck_rubric import evaluate  # noqa: E402

REPO = EXEC.parents[2]
RUN6 = REPO / "runs" / "great-eastern" / "2026-10-26-run6"
STORY4 = EXEC / "storylines" / "geh-preread-exec-v4.json"
STORY3 = EXEC / "storylines" / "geh-preread-exec-v3.json"
AR_PDF = Path("/mnt/user-data/attachments/598a1fc4-71d0-5dc6-b611-3434cc77d612/19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf")
GOLDEN = EXEC / "tests" / "golden" / "geh-preread-v4.json"
bench = pytest.mark.skipif(not (RUN6.exists() and AR_PDF.exists()), reason="benchmark inputs not present")
has_node = pytest.mark.skipif(not shutil.which("node") or not (EXEC / "node_modules").exists(), reason="renderer deps not installed")


def snapshot(story):
    snap = {"status": {k: story["_status"][k] for k in ("final", "marker", "founder_inputs", "pending_slides")}, "slides": []}
    for s in story["slides"]:
        snap["slides"].append({
            "id": s["id"], "layout": s["layout"], "title": s["title"]["text"], "source": s.get("_source"),
            "figures": {f["id"]: f["value"] for f in s.get("figures", [])},
            "tiles": [t["big"] for t in s.get("tiles", [])],
            "pending": bool(s.get("_pending")),
        })
    return snap


@pytest.fixture(scope="module")
def v4():
    story, rows, _ = resolve(json.loads(STORY4.read_text()), RUN6, AR_PDF, None)
    return story


@bench
def test_benchmark_matches_golden(v4):
    snap = snapshot(v4)
    if os.environ.get("PLUMB_UPDATE_GOLDEN") == "1" or not GOLDEN.exists():
        GOLDEN.write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n")
    assert snap == json.loads(GOLDEN.read_text()), "benchmark changed; review and re-run with PLUMB_UPDATE_GOLDEN=1"


@bench
def test_benchmark_passes_rubric_fully(v4):
    res = evaluate(v4)
    assert res["passed"], res["hard_failures"]
    assert all(s["pass"] for s in res["soft"]), res["soft"]


@bench
def test_rubric_fails_v3_on_the_review_findings():
    story, _, _ = resolve(json.loads(STORY3.read_text()), RUN6, AR_PDF, None)
    hard = " | ".join(evaluate(story)["hard_failures"])
    for finding in ("the ask quotes a fee", "credentials appear on slide 11", "placeholder bars imply a ranking", "without an addressable basis"):
        assert finding in hard


@bench
def test_rubric_refuses_unaddressable_value_base(v4):
    s = copy.deepcopy(v4)
    vb = next(x for x in s["slides"] if x["id"] == "value-base")
    vb["figures"][0].pop("addressable")
    assert any("addressable basis" in h for h in evaluate(s)["hard_failures"])


def _render(story, tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps(story))
    env = dict(os.environ, PPTX_SKILL_DIR="")
    return subprocess.run(["node", str(EXEC / "render_exec.js"), str(p), str(tmp_path / "d.pptx")], capture_output=True, text=True, env=env)


@bench
@has_node
def test_benchmark_renders_with_clean_layout_audit(v4, tmp_path):
    r = _render(v4, tmp_path)
    assert r.returncode == 0, r.stderr
    assert json.loads((tmp_path / "d.layout.json").read_text())["errors"] == []


@bench
@has_node
def test_layout_audit_refuses_orphan_title_and_wrapped_pill(v4, tmp_path):
    s = copy.deepcopy(v4)
    lc = next(x for x in s["slides"] if x["id"] == "lifecycle")
    lc["title"]["text"] = "AI is in use from advice to claims and compliance; complex underwriting is still in testing"
    lc["stages"][3]["items"][1]["text"] = "Bill-fraud detection and medical-bill OCR"
    r = _render(s, tmp_path)
    assert r.returncode == 3
    assert "alone on its last line" in r.stderr and "must fit on one line" in r.stderr
    assert not (tmp_path / "d.pptx").exists()
