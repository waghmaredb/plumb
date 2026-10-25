"""YAML ↔ markdown consistency (48 capability items + 4 value items)."""

import re
from collections import Counter
from pathlib import Path

MD = Path(__file__).resolve().parents[2] / "methodology" / "maturity-instrument.md"

ROW = re.compile(r"^\| (D\d\.\d) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|$", re.M)


def test_counts(inst):
    assert len(inst.items) == 48
    assert len(inst.value_items) == 4
    assert Counter(i.dimension for i in inst.items) == {f"D{d}": 6 for d in range(1, 9)}
    assert sum(inst.weights.values()) == 100
    assert len(inst.kappa_subset) == 20
    assert sum(1 for i in inst.items if i.kappa_subset) == 20


def test_item_ids_match_markdown(inst):
    md = MD.read_text(encoding="utf-8")
    md_rows = ROW.findall(md)
    assert len(md_rows) == 48
    assert [r[0] for r in md_rows] == [i.id for i in inst.items]
    v_ids = re.findall(r"^\| (V\d) \| ", md, re.M)
    assert v_ids == [v.id for v in inst.value_items] == ["V1", "V2", "V3", "V4"]


def test_questions_anchors_evidence_verbatim(inst):
    md = MD.read_text(encoding="utf-8")
    by = inst.item_by_id
    for rid, q, l1, l2, l3, l4, l5, ev in ROW.findall(md):
        it = by[rid]
        assert it.question == q.strip(), rid
        assert [it.anchors[k] for k in (1, 2, 3, 4, 5)] == [x.strip() for x in (l1, l2, l3, l4, l5)], rid
        assert it.evidence_class_required_text == ev.strip(), rid
        # required class set is exactly the class letters in the Ev≥4 text (outside parentheses)
        letters = set(re.findall(r"\b([DSIO])\b", re.sub(r"\([^)]*\)", "", ev)))
        assert set(it.evidence_class_required) == letters, (rid, ev)


def test_weights_match_markdown(inst):
    md = MD.read_text(encoding="utf-8")
    for d in inst.dimensions:
        m = re.search(rf"^\| {d.id} \| (.+?) \| (\d+) \|", md, re.M)
        assert m, d.id
        assert m.group(1).strip() == d.name
        assert int(m.group(2)) == d.weight


def test_kappa_subset_matches_markdown(inst):
    md = MD.read_text(encoding="utf-8")
    sec = md.split("## 7.")[1].split("## 8.")[0]
    ids = re.findall(r"^\| \d+ \| (D\d\.\d) \|", sec, re.M)
    assert ids == inst.kappa_subset
    # covers every dimension and all four evidence classes
    assert {inst.item_by_id[i].dimension for i in ids} == {f"D{d}" for d in range(1, 9)}
    assert {c for i in ids for c in inst.item_by_id[i].evidence_class_required} == {"D", "S", "I", "O"}


def test_proxies_present(inst):
    for it in inst.items:
        assert it.outside_in_proxies, it.id
        for p in it.outside_in_proxies:
            assert p.signal and p.validation
