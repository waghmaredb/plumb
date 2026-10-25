import json

from plumbverify.log import GENESIS, HashChainLog
from plumbverify.models import Citation, CitationStatus, Claim, ClaimKind, ConfidenceLabel
from plumbverify.policy import build_gate, decide, released_claims


def _claim(kind=ClaimKind.fact, lb=False, label=ConfidenceLabel.filed, cid="c1"):
    return Claim(id=cid, text="t", kind=kind, load_bearing=lb, confidence_label=label, sources=["u"])


def _cite(status, cid="c1", url="u"):
    return Citation(claim_id=cid, source_url=url, status=status, match_score=0.9)


# ---- C11 block-not-flag ---------------------------------------------------
def test_unverified_claim_is_blocked_with_reason():
    d = decide(_claim(), [_cite(CitationStatus.unverified)])
    assert d.blocked and d.status == CitationStatus.blocked and any("C4" in r for r in d.reasons)


def test_no_citation_is_blocked():
    d = decide(_claim(), [])
    assert d.blocked and any("no citation" in r for r in d.reasons)


def test_verified_non_load_bearing_passes():
    d = decide(_claim(), [_cite(CitationStatus.verified)])
    assert not d.blocked and d.status == CitationStatus.verified


def test_partial_blocked_for_load_bearing_and_without_second_supported():
    assert decide(_claim(lb=True), [_cite(CitationStatus.partial)]).blocked
    assert decide(_claim(lb=False), [_cite(CitationStatus.partial)]).blocked
    # partial plus a second SUPPORTED source is fine for non-load-bearing
    assert not decide(_claim(lb=False), [_cite(CitationStatus.partial), _cite(CitationStatus.verified, url="u2")]).blocked


def test_load_bearing_number_needs_two_independent_upstreams():
    c = _claim(kind=ClaimKind.number, lb=True)
    blocked = decide(c, [_cite(CitationStatus.verified)], independent_upstreams=1)
    assert blocked.blocked and any("single-upstream" in r for r in blocked.reasons)
    ok = decide(c, [_cite(CitationStatus.verified)], independent_upstreams=2)
    assert not ok.blocked


def test_non_load_bearing_number_single_upstream_allowed():
    d = decide(_claim(kind=ClaimKind.number, lb=False), [_cite(CitationStatus.verified)], independent_upstreams=1)
    assert not d.blocked


def test_quote_failure_blocks_not_downgrades():
    d = decide(_claim(kind=ClaimKind.quote), [_cite(CitationStatus.blocked)])
    assert d.blocked and d.status == CitationStatus.blocked and any("C5" in r for r in d.reasons)


def test_number_without_confidence_label_fails_lint():
    d = decide(_claim(kind=ClaimKind.number, label=None), [_cite(CitationStatus.verified)], independent_upstreams=2)
    assert d.blocked and any("C9" in r for r in d.reasons)


def test_build_gate_fails_on_one_blocked_claim_and_writes_gap_register():
    claims = [_claim(cid="a"), _claim(cid="b")]
    decisions = [decide(claims[0], [_cite(CitationStatus.verified, cid="a")]),
                 decide(claims[1], [_cite(CitationStatus.unverified, cid="b")])]
    gate = build_gate(claims, decisions)
    assert not gate.passed and gate.blocked_count == 1
    assert gate.gap_register[0].claim_id == "b" and gate.gap_register[0].reasons
    assert [c.id for c in released_claims(claims, decisions)] == ["a"]


# ---- C12/C13 hash chain ---------------------------------------------------
def test_hash_chain_appends_and_verifies(tmp_path):
    log = HashChainLog(tmp_path / "log.jsonl")
    r1 = log.log_inference(run_id="r", model_id="m", model_version="1", caller="t", prompt="secret prompt",
                           tool_calls=[{"tool": "fetch"}], outcome="ok", region_asserted="asia-southeast1")
    r2 = log.append({"type": "action", "tool": "match"})
    assert r1["prev_sha256"] == GENESIS and r2["prev_sha256"] == r1["sha256"]
    assert "secret prompt" not in (tmp_path / "log.jsonl").read_text()
    assert len(r1["prompt_sha256"]) == 64
    v = log.verify()
    assert v.ok and v.records == 2


def test_hash_chain_detects_tamper(tmp_path):
    p = tmp_path / "log.jsonl"
    log = HashChainLog(p)
    for i in range(3):
        log.append({"type": "inference", "i": i, "outcome": "ok"})
    lines = p.read_text().splitlines()
    rec = json.loads(lines[1])
    rec["outcome"] = "tampered"
    lines[1] = json.dumps(rec, sort_keys=True)
    p.write_text("\n".join(lines) + "\n")
    v = HashChainLog(p).verify()
    assert not v.ok and v.broken_at == 2


def test_hash_chain_detects_deletion_and_reorder(tmp_path):
    p = tmp_path / "log.jsonl"
    log = HashChainLog(p)
    for i in range(3):
        log.append({"i": i})
    lines = p.read_text().splitlines()
    p.write_text("\n".join([lines[0], lines[2]]) + "\n")
    assert not HashChainLog(p).verify().ok
    p.write_text("\n".join([lines[1], lines[0], lines[2]]) + "\n")
    assert not HashChainLog(p).verify().ok


def test_hash_chain_resumes_after_reopen(tmp_path):
    p = tmp_path / "log.jsonl"
    HashChainLog(p).append({"a": 1})
    log2 = HashChainLog(p)
    r = log2.append({"a": 2})
    assert r["seq"] == 2 and log2.verify().ok
