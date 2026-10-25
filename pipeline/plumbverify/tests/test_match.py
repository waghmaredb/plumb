from plumbverify import match as m


SOURCE = (
    "In a statement the department said: “The substance of the independent review is retained, "
    "and there are no changes to the recommendations.” Deloitte agreed to a partial refund of the "
    "A$440,000 fee after fabricated references were found."
)


# ---- quotation (C5) -------------------------------------------------------
def test_quote_exact_after_normalisation():
    q = m.quote_match('"The substance of the independent  review is retained, and there are no changes to the recommendations."', SOURCE)
    assert q.passed and q.exact and q.score == 1.0


def test_quote_smart_quotes_and_whitespace_normalised():
    q = m.quote_match("“the substance of the\nindependent review is retained”", SOURCE)
    assert q.passed and q.exact


def test_quote_paraphrase_fails():
    q = m.quote_match("The independent review's substance is kept and the recommendations are unchanged.", SOURCE)
    assert not q.passed and q.score < m.QUOTE_THRESHOLD


def test_quote_altered_word_fails():
    q = m.quote_match("The substance of the independent review is removed, and there are no changes to the recommendations.", SOURCE)
    assert not q.passed


def test_quote_threshold_is_strict_and_configurable():
    # Spec: zero tolerance on quotations. A one-character change must fail by default.
    assert m.QUOTE_THRESHOLD == 1.0
    q = m.quote_match("Deloitte agreed to a partial refund of the A$440,00 fee", SOURCE)
    assert q.score < 1.0 and not q.passed
    # Looser threshold remains available for exploratory runs, never for release.
    loose = m.quote_match("Deloitte agreed to a partial refund of the A$440,00 fee", SOURCE, threshold=0.98)
    assert loose.passed


def test_quote_ellipsis_logs_omitted_span():
    q = m.quote_match("The substance of the independent review is retained ... no changes to the recommendations.", SOURCE)
    assert q.passed
    assert q.omitted_spans and "and there are" in q.omitted_spans[0]


def test_quote_ellipsis_out_of_order_fails():
    q = m.quote_match("no changes to the recommendations ... The substance of the independent review", SOURCE)
    assert not q.passed


# ---- number normalisation (C4) -------------------------------------------
def test_parse_numbers_commas_scale_currency_percent():
    toks = m.parse_numbers("A$440,000 fee; US$3.2 billion market; 12.5% growth; 1.6M users; 40 per cent; 3bn")
    vals = {(t.value, t.unit) for t in toks}
    assert (440000.0, "AUD") in vals
    assert (3.2e9, "USD") in vals
    assert (12.5, "%") in vals
    assert (1.6e6, "") in vals
    assert (40.0, "%") in vals
    assert (3e9, "") in vals


def test_parse_numbers_ignores_bare_years():
    toks = m.parse_numbers("In 2025 the report cost 440,000 dollars")
    assert [t.value for t in toks] == [440000.0]


def test_number_in_passage_scale_word_equivalence():
    nc = m.number_in_passage("Plan cost C$1,600,000", "a C$1.6 million health workforce plan")
    assert nc.passed


def test_number_in_passage_percent_variants():
    assert m.number_in_passage("fell 42%", "fell about 42 per cent on average").passed
    assert not m.number_in_passage("fell 42%", "42 tool calls were made").passed  # unit mismatch


def test_number_in_passage_missing_number():
    nc = m.number_in_passage("Refund of A$290,000", "the A$440,000 report")
    assert not nc.passed and nc.missing[0].value == 290000.0


def test_currency_mismatch_fails():
    assert not m.number_in_passage("US$440,000", "A$440,000 report").passed


# ---- claim-to-passage (C4) -----------------------------------------------
PASSAGES = [
    "Deloitte Australia has agreed to partially refund the department after a A$440,000 report was found to contain fabricated references.",
    "Independent audits report that between 3% and 13% of cited URLs are hallucinated.",
    "The weather in Singapore is humid for most of the year.",
]


def test_claim_match_supported_above_085():
    pm = m.claim_match("a A$440,000 report was found to contain fabricated references", PASSAGES)
    assert pm.label == "supported" and pm.score >= 0.85 and pm.passage == PASSAGES[0]


def test_claim_match_unsupported_below_070():
    pm = m.claim_match("Revenue grew by nine percent in the quarter driven by cloud services", PASSAGES)
    assert pm.label == "unsupported" and pm.score < 0.70


def test_claim_match_partial_band():
    assert m.label_for(0.72) == "partial"
    assert m.label_for(0.85) == "supported"
    assert m.label_for(0.699) == "unsupported"


class _FakeSemantic:
    def score(self, claim, passage):
        return 0.9 if "hallucinated" in passage else 0.1


def test_semantic_matcher_plugs_in_and_lifts_paraphrase():
    claim = "Roughly one in ten references produced by these tools point to invented pages"
    lexical_only = m.claim_match(claim, PASSAGES)
    assert lexical_only.label == "unsupported"
    with_sem = m.claim_match(claim, PASSAGES, semantic=_FakeSemantic())
    assert with_sem.label == "supported" and with_sem.semantic_score == 0.9 and with_sem.passage == PASSAGES[1]


# ---- number-claim match (number presence hard gate + keyword context) ----
def test_number_claim_match_requires_number_then_context():
    nm = m.number_claim_match("Deloitte's report cost A$440,000", PASSAGES)
    assert nm.label == "supported" and nm.passage == PASSAGES[0] and nm.context_score >= m.NUMBER_CONTEXT_THRESHOLD
    missing = m.number_claim_match("Deloitte's report cost A$290,000", PASSAGES)
    assert missing.label == "unsupported"
    weak = m.number_claim_match("Quantum widget shipments reached A$440,000", PASSAGES)
    assert weak.label == "partial"  # number present, context absent
    with_sem = m.number_claim_match("Roughly 13% of links are hallucinated", PASSAGES, semantic=_FakeSemantic())
    assert with_sem.label == "supported" and with_sem.passage == PASSAGES[1]
