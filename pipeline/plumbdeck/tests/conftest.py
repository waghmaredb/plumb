import copy
import json
import shutil
from pathlib import Path

import pytest
import yaml

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parents[1]
RUN3 = REPO / "runs" / "great-eastern" / "2026-10-25-ar-attached-fixed"
RUN4 = REPO / "runs" / "great-eastern" / "2026-10-25-run4"
SPEC = PKG / "specs" / "plumb-assessment-v0.1.yaml"
SCORECARD = PKG / "tests" / "fixtures" / "scorecard_harbourline.json"
OPERATOR = "Deepak Waghmare"  # supplied_by on the run-3 attachment
REVIEWER = "Ines Ortega"  # fictional independent reviewer


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def make_run(tmp: Path, *, profile="client", recon="MATCH", resolution=1.0, mutate=None) -> Path:
    """A copy of the run-3 report with the interlock-relevant fields set explicitly."""
    d = tmp / f"run-{profile}-{recon}-{resolution}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    rep = copy.deepcopy(_load(RUN3 / "report.json"))
    v = rep["verification"]
    rep["build_profile"] = v["build_profile"] = profile
    for s in v["sources"]:
        if s.get("state") == "ATTACHED":
            s["reconciliation"] = recon
    for a in rep["attached_documents"]:
        a["reconciliation"] = recon
    m = v["metrics"]
    m["citation_resolution_rate"] = resolution
    m["attached_unreconciled"] = 0 if recon in ("MATCH", "MISMATCH") else 1
    m["attached_mismatch"] = 1 if recon == "MISMATCH" else 0
    if recon == "MATCH":  # reconciliation lifts the attached label (spec C2a)
        for x in v["decisions"] + v["citations"]:
            x["labels"] = [l for l in x.get("labels") or [] if not l.startswith("attached")]
    if mutate:
        mutate(rep)
    (d / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    shutil.copy(RUN3 / "claims.json", d / "claims.json")
    return d


def make_signoff(tmp: Path, run_dir: Path, **over) -> Path:
    rep = _load(run_dir / "report.json")
    data = {
        "qa_gate": 3,
        "run_id": rep["run_id"],
        "reviewer": {"name": REVIEWER, "role": "Independent reviewer"},
        "independence_attestation": True,
        "date": "2026-10-26",
        "sample": {"total": 30, "exec_summary": 6, "module_fill": 10, "qualitative": 5, "fabricated": 0, "quotation_failures": 0},
        "decision": "approved",
        "approver": {"name": "Engagement Partner (fictional)", "role": "Lead partner"},
    }
    for k, v in over.items():
        if v is None:
            data.pop(k, None)
        else:
            data[k] = v
    p = tmp / f"signoff-{abs(hash(json.dumps(over, sort_keys=True, default=str)))}.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return p


@pytest.fixture
def tmp(tmp_path):
    return tmp_path
