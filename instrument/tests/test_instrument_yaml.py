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


# ------------------------------------------------------------------ v0.2
def test_default_is_v0_2_and_v0_1_kept_for_history(inst):
    from plumbscore import load_instrument
    from plumbscore.instrument import DEFAULT_INSTRUMENT_PATH, V0_1_INSTRUMENT_PATH

    assert inst.version == "0.2" and DEFAULT_INSTRUMENT_PATH.name == "instrument-v0.2.yaml"
    md = MD.read_text(encoding="utf-8")
    assert md.startswith("# Enterprise AI Maturity Instrument v0.2")
    old = load_instrument(V0_1_INSTRUMENT_PATH)
    assert old.version == "0.1" and len(old.items) == 48


def test_decisions_register_matches_markdown(inst):
    md = MD.read_text(encoding="utf-8")
    sec = md.split("### 5.6 Decisions resolved in v0.2")[1].split("\n---")[0]
    md_ids = [int(x) for x in re.findall(r"^\| (\d+) \| ", sec, re.M)]
    assert md_ids == list(range(1, 13))
    assert [d["id"] for d in inst.decisions_v0_2] == md_ids
    md_topics = re.findall(r"^\| \d+ \| (.+?) \| ", sec, re.M)
    assert [d["topic"] for d in inst.decisions_v0_2] == md_topics
    assert all(d["decision"] and d["rationale"] for d in inst.decisions_v0_2)


def test_single_proxy_items_marked_in_markdown(inst):
    """v0.2 decision 4: '1–4 proxies per item'; single-proxy items carry † in the md proxy tables."""
    md = MD.read_text(encoding="utf-8")
    daggers = re.findall(r"^\| (D\d\.\d) † \| ", md, re.M)
    one = [i.id for i in inst.items if len(i.outside_in_proxies) == 1]
    import yaml
    from plumbscore.instrument import DEFAULT_INSTRUMENT_PATH

    raw = yaml.safe_load(DEFAULT_INSTRUMENT_PATH.read_text(encoding="utf-8"))
    assert daggers == one == raw["structure"]["single_proxy_items"]
    assert len(one) == 10
    assert all(1 <= len(i.outside_in_proxies) <= 4 for i in inst.items)
    assert "1–4 per item" in md and "2–4 per item" not in md
    assert "D8.1–8.2" not in md.split("## 4.")[0]  # shared proxy row split


def test_d35_d66_anchors_do_not_overlap(inst):
    """v0.2 decision 12: D3.5 = technical controls, D6.6 = governance of agents."""
    d35 = " ".join(inst.item_by_id["D3.5"].anchors.values()).lower()
    d66 = " ".join(inst.item_by_id["D6.6"].anchors.values()).lower()
    for technical in ("kill switch", "credential", "cryptographic", "sandbox", "audit trail", "anomaly"):
        assert technical not in d66, technical
    for governance in ("policy", "accountable", "approval", "register", "board"):
        assert governance not in d35, governance
    assert set(inst.item_by_id["D6.6"].evidence_class_required) == {"D", "S"}
    assert set(inst.item_by_id["D3.5"].evidence_class_required) == {"O", "S"}


def test_markdown_body_states_v0_2_rules():
    md = MD.read_text(encoding="utf-8")
    # normative sections only (§1–§5.5 and §6–§9); the change log, §5.6 and the appendix quote the old text
    body = md.split("## 1. Structure")[1].split("### 5.6")[0] + md.split("## 6. Calibration")[1].split("## Appendix")[0]
    assert "≥76" not in body and "4.04" not in body
    assert "25 < C ≤ 50" in body and "75 < C ≤ 100" in body
    assert "consensus self-report" not in body
    assert "39 < p ≤ 61" in body
    assert "14 / 46 / 35 / 5" in body and "5 / 35 / 46 / 14" not in body
    assert "Interview + observation item" in body and "Interview-only item" not in body
    box = md.split("## What changed for respondents (v0.2)")[1].split("\n---")[0]
    assert len(re.findall(r"^> - ", box, re.M)) == 5
