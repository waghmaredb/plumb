"""C4 fact-claim verification (0.5): decomposition, negation/hedge, contradiction rules,
synonym recall, backend chain, pipeline integration and the calibration harness.
Fully offline: model backends are exercised with injected predictors."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from plumbverify import semantic as sem
from plumbverify.calibrate import calibrate, format_table, load_pairs, wilson_upper
from plumbverify.cli import main
from plumbverify.models import CitationStatus, Claim, ClaimKind, ConfidenceLabel
from plumbverify.pipeline import Verifier
from plumbverify.tier import load_tier_rules

FIX = Path(__file__).parent / "fixtures"
CAL = Path(__file__).parent.parent / "calibration" / "geh_c4_v1.jsonl"

# verbatim passages from the Great Eastern FY2025 annual report (pp. 14, 13, 6, 40, 44)
P_CLAIMS = ("We rolled out a proprietary AI-powered platform to automate medical claims, enhancing claim efficiency while "
            "improving customer experience. We are also testing an AI solution for complex underwriting cases to further "
            "improve automation and associated efficiency.")
P_ADVISORY = ("In 2025, we deployed an AI-enabled advisory platform that aims to reduce preparation time for financial advisors "
              "by approximately 75%, enabling them to focus more on customer engagement and advice.")
P_TWNS = ("Total Weighted New Sales for FY2025 recorded a year-on-year decline of 15%, in line with our strategic shift away "
          "from short-term single-premium products towards a more diversified range of longer-term product offerings.")
P_RIDER = ("Introduced the Great Life Multiplier, an award-winning whole-life plan with a first-in-market Parent Care Rider that "
           "provides late-stage critical illness protection for elderly parents without medical underwriting.")
P_SAMEDAY = ("In 2025, our AI-driven claims system delivered same-day turnarounds for 75% of medical claims, one of the fastest "
             "among Singapore’s health insurers based on Ministry of Health service indicators.")
P_MYSALAM = ("To date, mySalam has recorded close to two million claims, benefiting over 1.86 million Malaysians with claims "
             "payments exceeding RM1.35 billion.")


def rules(claim, passage):
    return {r.rule for r in sem.contradiction_rules(claim, passage)}


# ---- decomposition -------------------------------------------------------------
def test_decompose_subject_predicate_object_numbers_qualifiers():
    d = sem.decompose("Great Eastern's AI advisory platform aims to reduce advisor preparation time by approximately 75% in 2025.")
    assert d.predicate == "reduce"
    assert "advisory" in d.subject and "preparation" in d.object
    assert d.numbers == ["75%"] and d.years == [2025]
    assert "hedge/intent" in d.qualifiers and "approx:approximately" in d.qualifiers
    assert d.modality == "INTENT"
    t = sem.decompose("Great Eastern is testing an AI solution for complex underwriting cases.")
    assert t.predicate == "trial" and t.modality == "TRIAL" and "trial/pilot" in t.qualifiers
    n = sem.decompose("The rider is not available without medical underwriting.")
    assert n.modality == "NEG" and "negation" in n.qualifiers
    assert sem.decompose("Great Eastern rolled out a platform.").as_dict()["predicate"] == "deploy"


# ---- negation / hedge detection -------------------------------------------------
@pytest.mark.parametrize("text,word,modality", [
    (P_ADVISORY, "preparation", "INTENT"),        # "aims to"
    (P_ADVISORY, "advisory", "PLAIN"),            # before the hedge: the platform was deployed
    (P_CLAIMS, "underwriting", "TRIAL"),          # "testing"
    (P_CLAIMS, "medical", "PLAIN"),               # the claims platform was rolled out
    (P_RIDER, "underwriting", "NEG"),             # "without"
    ("The dividend will be payable on 6 May 2026.", "zzpay", "INTENT"),
    ("The Board has recommended a final dividend of 30 cents.", "dividend", "INTENT"),
    ("Great Eastern expects to launch the plan in 2026.", "zzdeploy", "INTENT"),
    ("Great Eastern is piloting the platform.", "zzsystem", "TRIAL"),
])
def test_modality_tags(text, word, modality):
    a = sem.analyse(text)
    toks = [t for t in a.tokens if t.surface == word or t.stem == word]
    assert toks, f"{word} not tokenised in {text!r}"
    assert toks[0].modality == modality


def test_noun_uses_of_hedge_words_are_not_hedges():
    a = sem.analyse("an electric vehicle insurance plan to support Malaysia's growing EV ecosystem")
    assert not a.has_intent
    assert not sem.analyse("Expected credit loss allowances rose under the Targeted Compliance Framework.").has_intent
    assert not sem.analyse("one of the fastest health insurers").has_trial  # "fastest" is not "test"
    assert sem.analyse("we plan to expand").has_intent


# ---- contradiction rules ---------------------------------------------------------
def test_production_claim_against_pilot_passage_is_contradiction():
    assert "production_vs_pilot" in rules("Great Eastern has deployed an AI solution for complex underwriting cases.", P_CLAIMS)
    assert "production_vs_pilot" in rules("An AI underwriting platform is now live in production at Great Eastern.", P_CLAIMS)
    assert not rules("Great Eastern is trialling an AI solution for complex underwriting cases.", P_CLAIMS)
    assert not rules("Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)


def test_pilot_claim_against_production_passage_is_contradiction():
    assert "pilot_vs_production" in rules("Great Eastern is piloting an AI platform to automate medical claims.", P_CLAIMS)


def test_dropped_hedge_caps_at_partial():
    hits = sem.contradiction_rules("Great Eastern's AI-enabled advisory platform reduced financial advisors' preparation time by approximately 75%.", P_ADVISORY)
    assert {h.rule for h in hits} >= {"dropped_hedge"} and all(h.effect == "cap" for h in hits)
    assert not rules("In 2025 Great Eastern deployed an AI-enabled advisory platform aimed at cutting financial advisors' "
                     "preparation time by roughly 75%.", P_ADVISORY)


def test_purpose_stated_as_outcome_caps():
    p = "In 2025, we enhanced the GreatPlanner app, utilising in-app alerts to reduce costs and improve operational efficiency."
    assert "purpose_as_outcome" in rules("The GreatPlanner app has reduced costs.", p)
    assert "purpose_as_outcome" not in rules("The GreatPlanner app uses in-app alerts to reduce costs.", p)


def test_number_year_and_approx_rules():
    assert "number_mismatch" in rules("The AI-enabled advisory platform aims to reduce preparation time for financial advisors by approximately 50%.", P_ADVISORY)
    assert "year_mismatch" in rules("In 2024, the AI-driven claims system delivered same-day turnarounds for 75% of medical claims.", P_SAMEDAY)
    assert "year_unverified" in rules("In 2025 Great Eastern rolled out a proprietary AI platform to automate medical claims.", P_CLAIMS)
    assert "approx_inflation" in rules("mySalam has recorded more than two million claims.", P_MYSALAM)
    assert not rules("mySalam has paid claims exceeding RM1.35 billion to over 1.86 million Malaysians.", P_MYSALAM)


def test_number_binding_and_counted_noun():
    p = "Dr Andrew Khoo, who was appointed to the Board on 8 September 2025, will succeed Mr Soon Tit Koon as Chairman on 15 April 2026."
    assert "number_binding" in rules("Dr Andrew Khoo succeeded Mr Soon Tit Koon as Chairman on 8 September 2025.", p)
    likes = "The livestream received over 3.2 million likes, 12 thousand comments, and more than 17 thousand visitors in just 24 hours."
    assert "counted_noun_mismatch" in rules("The livestream received over 3.2 million comments.", likes)
    assert "counted_noun_mismatch" not in rules("The livestream received over 3.2 million likes.", likes)


def test_direction_negation_superlative_entity_role():
    assert "direction_flip" in rules("Total Weighted New Sales grew 15% year on year in FY2025.", P_TWNS)
    assert "direction_flip" not in rules("Total Weighted New Sales fell 15% year on year in FY2025.", P_TWNS)
    assert "negation_mismatch" in rules("The Parent Care Rider requires full medical underwriting for elderly parents.", P_RIDER)
    assert "negation_mismatch" in rules("Great Eastern does not use AI to automate medical claims.", P_CLAIMS)
    assert not rules("The Parent Care Rider provides late-stage critical illness protection for elderly parents without medical underwriting.", P_RIDER)
    assert "superlative_inflation" in rules("Great Eastern's AI claims system made it the fastest health insurer in Singapore.", P_SAMEDAY)
    assert "entity_substitution" in rules("Great Eastern became the first insurer in Malaysia to attain the Cyber Trust Mark.",
                                          "we became the first insurer in the industry to attain the Cyber Trust Mark in Singapore")
    assert "role_substitution" in rules("The AI-enabled advisory solution aims to reduce preparation time for customers by approximately 75%.", P_ADVISORY)
    assert "absolute_inflation" in rules("Great Eastern fully automated medical claims.", P_CLAIMS)


# ---- synonym recall --------------------------------------------------------------
@pytest.mark.parametrize("claim,passage", [
    ("Great Eastern launched an AI platform.", "Great Eastern rolled out an AI platform."),
    ("Great Eastern deployed an AI platform.", "Great Eastern launched an AI platform."),
    ("The tool cut preparation time.", "The tool reduced preparation time."),
    ("The tool helps advisers.", "The tool helps advisors."),
    ("Great Eastern uses artificial intelligence for underwriting.", "Great Eastern uses AI for underwriting."),
    ("Great Eastern uses machine learning for medical claims.", "Great Eastern leverages AI for medical claims."),
    ("The in-house platform automates claims.", "The proprietary system automates claims."),
    ("Great Eastern developed an OCR solution.", "we have developed an Optical Character Recognition solution"),
])
def test_synonym_recall(claim, passage):
    s, missing = sem.key_term_recall(claim, passage)
    assert s >= 0.85 and not missing, (s, missing)


def test_missing_distinctive_term_drops_below_supported():
    s, missing = sem.key_term_recall("In 2025, the AI-driven underwriting system delivered same-day turnarounds for 75% of medical claims.", P_SAMEDAY)
    assert "underwriting" in missing and s < 0.85


# ---- backend chain and decision logic ----------------------------------------------
def _nli(entail, contra=0.0):
    return sem.NLIBackend(predictor=lambda pairs: [{"entailment": entail, "contradiction": contra, "neutral": 1 - entail - contra}] * len(pairs))


def test_model_backends_report_missing_weights(tmp_path):
    for b in (sem.NLIBackend(cache_dir=tmp_path), sem.EmbeddingBackend(cache_dir=tmp_path)):
        assert not b.available()
        assert "plumbverify models pull" in b.unavailable_reason
        with pytest.raises(sem.BackendUnavailable):
            b.assess("a", "b")
    v = sem.C4Verifier(backends=sem.default_backends(cache_dir=tmp_path))
    assert [b.name for b in v.live_backends()] == ["offline"]
    a = v.assess("Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)
    assert a.matcher == "offline" and a.label == "supported" and set(a.backend_scores) == {"offline"}


def test_nli_preferred_and_recorded_but_rules_still_veto():
    v = sem.C4Verifier(backends=[_nli(0.97), sem.OfflineBaseline()])
    ok = v.assess("Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)
    assert ok.matcher == "nli" and ok.label == "supported" and set(ok.backend_scores) == {"nli", "offline"}
    bad = v.assess("Great Eastern has deployed an AI solution for complex underwriting cases.", P_CLAIMS)
    assert bad.matcher == "nli" and bad.raw_score == 0.97 and bad.label == "unsupported"
    assert any("production_vs_pilot" in r for r in bad.rules_fired)


def test_nli_contradiction_probability_fires_rule_and_low_entailment_fails():
    v = sem.C4Verifier(backends=[_nli(0.30, contra=0.65), sem.OfflineBaseline()])
    a = v.assess("Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)
    assert a.label == "unsupported" and any(r.startswith("nli_contradiction") for r in a.rules_fired)
    weak = sem.C4Verifier(backends=[_nli(0.75), sem.OfflineBaseline()]).assess(
        "Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)
    assert weak.label == "partial"  # best backend says partial even though offline says 1.0


def test_embedding_needs_lexical_agreement():
    emb = sem.EmbeddingBackend(predictor=lambda pairs: [0.93] * len(pairs))
    v = sem.C4Verifier(backends=[emb, sem.OfflineBaseline()])
    a = v.assess("Revenue from cloud services tripled in the quarter.", P_CLAIMS)
    assert a.matcher == "embedding" and a.label != "supported"


def test_plain_semantic_matcher_still_plugs_in():
    class Fake:
        def score(self, claim, passage):
            return 0.9
    v = sem.C4Verifier.from_matcher(Fake())
    a = v.assess("Great Eastern deployed a proprietary AI platform that automates medical claims.", P_CLAIMS)
    assert a.matcher == "custom" and a.label == "supported"


def test_best_picks_supporting_window_and_page():
    windows = [(P_TWNS, 13), (P_CLAIMS, 14), (P_ADVISORY, 14)]
    a = sem.C4Verifier().best("Great Eastern rolled out an AI platform that automates medical claims.", windows)
    assert a.passage == P_CLAIMS and a.page == 14 and a.label == "supported" and a.decomposition["predicate"] == "deploy"


def test_sentence_windows_are_paged():
    from plumbverify.extract import PAGE_SEP
    w = sem.sentence_windows("First page one. Second sentence here." + PAGE_SEP + "Page two text.")
    assert ("First page one.", 1) in w and ("First page one. Second sentence here.", 1) in w and ("Page two text.", 2) in w


# ---- pipeline integration ----------------------------------------------------------
RULES = load_tier_rules()


def test_pipeline_fact_citation_records_matcher_scores_and_rules(fetcher, store):
    v = Verifier(fetcher=fetcher, store=store, tier_rules=RULES)
    url = "https://www.example-press.org/report"
    rep = v.run([
        Claim(id="ok", text="Deloitte Australia agreed to partially refund the Department of Employment and Workplace Relations",
              kind=ClaimKind.fact, sources=[url]),
        Claim(id="neg", text="The A$440,000 report did not contain fabricated references", kind=ClaimKind.fact, sources=[url]),
    ])
    c = {x.claim_id: x for x in rep.citations}
    assert c["ok"].status == CitationStatus.verified and c["ok"].matcher == "offline" and "offline" in c["ok"].backend_scores
    assert c["ok"].decomposition and c["ok"].decomposition["predicate"]
    assert c["neg"].status == CitationStatus.unverified and any("negation_mismatch" in r for r in c["neg"].rules_fired)
    d = {x.claim_id: x for x in rep.decisions}
    assert not d["ok"].blocked and d["neg"].blocked  # block-not-flag unchanged
    data = json.loads(rep.model_dump_json())
    assert data["citations"][0]["matcher"] == "offline" and "rules_fired" in data["citations"][0]


def test_pipeline_number_claim_rules(store, mock_client, tmp_path):
    """Number claims keep the number gate and also get the C4 rules, evaluated on the sentence around the number."""
    from plumbverify.fetch import Fetcher
    from plumbverify.ingest import ingest_local
    doc = tmp_path / "geh.html"
    doc.write_text(f"<html><body><main><p>{P_TWNS}</p><p>{P_ADVISORY}</p></main></body></html>", encoding="utf-8")
    url = "https://www.greateasternlife.com/ar2025.html"
    ingest_local(doc, url, store, tier_rules=RULES)
    v = Verifier(fetcher=Fetcher(store=store, client=mock_client, sleep=lambda s: None), store=store, tier_rules=RULES,
                 build_profile="internal")
    L = ConfidenceLabel.filed
    rep = v.run([
        Claim(id="down", text="Total Weighted New Sales declined 15% year on year in FY2025", kind=ClaimKind.number, confidence_label=L, sources=[url]),
        Claim(id="up", text="Total Weighted New Sales grew 15% year on year in FY2025", kind=ClaimKind.number, confidence_label=L, sources=[url]),
        Claim(id="hedged", text="The AI-enabled advisory platform aims to reduce preparation time for financial advisors by approximately 75%",
              kind=ClaimKind.number, confidence_label=L, sources=[url]),
        Claim(id="dropped", text="The AI-enabled advisory platform reduced preparation time for financial advisors by 75%",
              kind=ClaimKind.number, confidence_label=L, sources=[url]),
    ])
    c = {x.claim_id: x for x in rep.citations}
    assert c["down"].status == CitationStatus.verified and c["hedged"].status == CitationStatus.verified
    assert c["up"].status == CitationStatus.unverified and any("direction_flip" in r for r in c["up"].rules_fired)
    assert c["dropped"].status == CitationStatus.partial and any("dropped_hedge" in r for r in c["dropped"].rules_fired)


# ---- calibration harness ----------------------------------------------------------
def test_calibration_on_fixture_subset():
    pairs = load_pairs(FIX / "c4_small.jsonl", split="all")
    assert len(pairs) == 15
    results, status = calibrate(pairs, [sem.NLIBackend(cache_dir="/nonexistent"), sem.OfflineBaseline()])
    by = {r.backend: r for r in results}
    assert set(by) == {"lexical (pre-0.5 rapidfuzz)", "offline"}
    assert any(s["backend"] == "nli" and not s["available"] for s in status)
    off, lex = by["offline"], by["lexical (pre-0.5 rapidfuzz)"]
    assert off.false_support == 0 and off.recall == 1.0 and off.precision == 1.0
    assert lex.false_support >= 2            # the reason 0.5 exists: lexical passes flipped claims
    assert off.suggested_supported_threshold is not None
    table = format_table(results, status, "all", 0.02)
    assert "false-SUPPORT" in table and "author-assigned" in table and "not evaluated" in table


def test_wilson_upper_bound():
    assert wilson_upper(0, 57) > 0.05 and wilson_upper(0, 0) == 0.0 and abs(wilson_upper(5, 10) - 0.763) < 0.01


def test_calibration_set_shape():
    rows = [json.loads(l) for l in CAL.read_text(encoding="utf-8").splitlines() if l.strip()]
    held = [r for r in rows if r["split"] in ("heldout", "fresh")]
    assert len(held) >= 80 and len({r["id"] for r in rows}) == len(rows)
    labels = [r["label"] for r in rows]
    for lab in ("supported", "partial", "unsupported"):
        assert 0.2 <= labels.count(lab) / len(labels) <= 0.45
    assert all(r["labelled_by"].startswith("author") for r in rows)
    meta = json.loads((CAL.parent / "geh_c4_v1.meta.json").read_text(encoding="utf-8"))
    assert "independent reviewer" in meta["label_status"]


def test_cli_calibrate_and_models_status(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("PLUMBVERIFY_MODEL_DIR", str(tmp_path))
    rc = main(["calibrate", str(FIX / "c4_small.jsonl"), "--split", "all", "--json", str(tmp_path / "cal.json")])
    out = capsys.readouterr().out
    assert rc == 0 and "| offline |" in out
    data = json.loads((tmp_path / "cal.json").read_text())
    assert any(r["backend"] == "offline" and r["per_pair"] for r in data["results"])
    assert main(["models", "status", "--dir", str(tmp_path)]) == 0
    st = json.loads(capsys.readouterr().out)
    assert [s["available"] for s in st] == [False, False, True]


def test_cli_models_pull_reports_failure(monkeypatch, tmp_path, capsys):
    import sys
    import types
    fake = types.ModuleType("huggingface_hub")

    def snapshot_download(**kw):
        raise OSError("403 Forbidden")
    fake.snapshot_download = snapshot_download
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake)
    assert main(["models", "pull", "--dir", str(tmp_path)]) == 1
    assert "403" in capsys.readouterr().err
