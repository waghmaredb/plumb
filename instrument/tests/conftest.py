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
    """make_responses(level_fn, n_exco=5, n_oper=7, evidence=None)

    level_fn(item_id, respondent_index, role_group) -> int
    """

    def _make(level_fn, n_exco=5, n_oper=7, evidence=None, items=None):
        instr = load_instrument()
        evidence = evidence or {}
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
                        }
                    )
        return responses_from_records(recs)

    return _make
