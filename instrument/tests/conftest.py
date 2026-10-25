import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from plumbscore import load_instrument  # noqa: E402
from plumbscore.responses import responses_from_records  # noqa: E402


@pytest.fixture(scope="session")
def inst():
    return load_instrument()


@pytest.fixture
def make_responses():
    """make_responses(level_fn, n_exco=5, n_oper=7, evidence=None, interviewees=None)

    level_fn(item_id, respondent_index, role_group) -> int
    interviewees: {item_id: int} written on every row of that item that carries
    evidence (v0.2 decision 11: an I class needs ≥2 verifiable interviewees).
    """

    def _make(level_fn, n_exco=5, n_oper=7, evidence=None, items=None, interviewees=None):
        instr = load_instrument()
        evidence = evidence or {}
        interviewees = interviewees or {}
        ids = items or [i.id for i in instr.items]
        recs = []
        idx = 0
        for grp, n in (("exco", n_exco), ("operating", n_oper)):
            for _ in range(n):
                idx += 1
                rid = f"R{idx:02d}"
                for iid in ids:
                    ev = evidence.get((rid, iid)) or evidence.get(iid) or "none"
                    recs.append(
                        {
                            "respondent_id": rid,
                            "role_group": grp,
                            "item_id": iid,
                            "score": level_fn(iid, idx, grp),
                            "evidence_class": ev,
                            "evidence_ref": "EV" if ev != "none" else "",
                            "interviewees": interviewees.get(iid) if ev != "none" else None,
                        }
                    )
        return responses_from_records(recs)

    return _make


def full_evidence(instr, dims=None):
    """Every required Ev≥4 class logged, with ≥2 interviewees on the I items (v0.2 decision 11).

    Returns (evidence, interviewees) for make_responses."""
    items = [i for i in instr.items if dims is None or i.dimension in dims]
    ev = {i.id: "+".join(i.evidence_class_required) for i in items}
    iv = {i.id: 2 for i in items if "I" in i.evidence_class_required}
    return ev, iv
