"""Postings share arithmetic, call density, peer funnel, financial percentiles and economic profit."""
from datetime import date

import pytest

from plumbresearch.modules import earnings_calls as ec
from plumbresearch.modules import financials as fin
from plumbresearch.modules import postings as po
from plumbresearch.modules.peerset import build_peer_set, exhibit_markdown
from plumbresearch.subject import Peer, PeerRole, SizeMetric, Subject, load_subject, builtin_subject_path

from .conftest import AS_OF, FIXTURES


# ---- postings ---------------------------------------------------------------
def _p(i, title, desc, d, company="Acme Bank"):
    return po.Posting(id=str(i), company=company, title=title, description=desc, posted_at=d)


def test_tagging_lexicon_groups():
    t = po.tag_posting(_p(1, "LLMOps Engineer", "Operate the model gateway and evaluation suites for GenAI; MLflow.", AS_OF))
    assert t.ai_related and "llm" in t.groups and "mlops" in t.groups
    t2 = po.tag_posting(_p(2, "Data Engineer", "Build data pipelines with Spark and Airflow; data quality.", AS_OF))
    assert not t2.ai_related and "data_eng" in t2.groups  # data engineering alone is not an AI posting (Babina et al.)
    t3 = po.tag_posting(_p(3, "Branch Officer", "Maintain the daily cash position.", AS_OF))
    assert not t3.ai_related and not t3.groups
    t4 = po.tag_posting(_p(4, "Officer", "Liaise with Ai Ling on retail matters.", AS_OF))
    assert not t4.ai_related  # lowercase 'ai' inside a name must not count


def test_share_arithmetic_and_window():
    posts = [_p(1, "Machine Learning Engineer", "PyTorch", date(2026, 9, 1)),
             _p(2, "Teller", "cash", date(2026, 8, 1)),
             _p(3, "Teller", "cash", date(2025, 2, 1)),
             _p(4, "Data Scientist", "machine learning", date(2025, 1, 1)),
             _p(5, "ML Engineer", "deep learning", date(2024, 10, 1))]  # outside the 24-month window ending 2026-10-25
    r = po.compute_share(posts, AS_OF)
    assert r.window_start == date(2024, 11, 1)
    assert r.total == 4 and r.ai == 2 and r.share == 0.5
    assert r.first_half_share == 0.5 and r.second_half_share == 0.5
    assert r.monthly["2026-09"] == (1, 1) and "2024-10" not in r.monthly


def test_share_on_fixture_csv():
    src = po.CsvPostingsSource(FIXTURES / "acme-bank" / "postings.csv")
    since = po.months_back(AS_OF, 23)
    acme = po.compute_share(src.postings(["Acme Bank"], since, AS_OF), AS_OF)
    beta = po.compute_share(src.postings(["Beta Bank"], since, AS_OF), AS_OF)
    gamma = po.compute_share(src.postings(["Gamma Financial"], since, AS_OF), AS_OF)
    assert (acme.total, acme.ai) == (40, 12) and acme.share == pytest.approx(0.30)
    assert beta.share == pytest.approx(0.40) and gamma.share == pytest.approx(0.10)
    assert po.percentile_rank(acme.share, [beta.share, gamma.share]) == 50.0


def test_stub_sources_raise():
    with pytest.raises(NotImplementedError):
        po.MyCareersFutureSource().postings(["x"], AS_OF, AS_OF)


# ---- earnings calls ---------------------------------------------------------
def test_split_and_density():
    text = ("Prepared remarks. We use AI in underwriting. Margins were stable this year.\n\n"
            "=== Question-and-Answer Session ===\n\n"
            "Analyst: How much AI spend is in the budget? CEO: Our machine learning platform is on track and AI agents are next.")
    prep, qa = ec.split_qa(text)
    assert prep.startswith("Prepared") and qa.startswith("Analyst")
    t = ec.Transcript(url="u", date=AS_OF, quarter="q", prepared=prep, qa=qa)
    d = ec.density(t)
    assert d.prepared_mentions == 1 and d.qa_mentions == 3
    assert d.prepared_per_1000 == pytest.approx(1 / d.prepared_words * 1000, rel=1e-3)
    assert d.qa_per_1000 > d.prepared_per_1000
    assert d.mentions == 4 and d.per_1000 == pytest.approx(4 / d.words * 1000, rel=1e-3)


def test_no_double_count_of_overlapping_terms():
    t = ec.Transcript(url="u", date=AS_OF, quarter="q", prepared="Our AI-powered assistant and generative AI tools.", qa="")
    assert ec.density(t).mentions == 2


# ---- peer funnel ------------------------------------------------------------
def _subject(size, peers):
    return Subject(slug="t", name="T", short_name="T", sector="banks", listing={"exchange": "X"}, latest_fy=2025,
                   size=SizeMetric(value_usd_bn=size), peers=peers)


def test_funnel_size_band_demotes_and_keeps_exited():
    peers = [
        Peer(name="In1", role=PeerRole.core, size=SizeMetric(value_usd_bn=30)),      # exactly 0.3x -> in
        Peer(name="In2", role=PeerRole.core, size=SizeMetric(value_usd_bn=300)),     # exactly 3x -> in
        Peer(name="TooBig", role=PeerRole.core, size=SizeMetric(value_usd_bn=301)),  # out -> demoted
        Peer(name="TooSmall", role=PeerRole.core, size=SizeMetric(value_usd_bn=29)), # out -> demoted
        Peer(name="Unknown", role=PeerRole.core, size=SizeMetric(verify=True)),      # kept, flagged
        Peer(name="Sec", role=PeerRole.secondary, size=SizeMetric(value_usd_bn=100), reason_secondary="no licence"),
        Peer(name="Gone", role=PeerRole.exited, event="Gone sold to In1", event_year=2020, status="Consolidated",
             size=SizeMetric(value_usd_bn=5000)),  # size must never filter an exited peer
    ]
    ps = build_peer_set(_subject(100, peers))
    assert (ps.band_low_usd_bn, ps.band_high_usd_bn) == (30.0, 300.0)
    assert [p.name for p in ps.core] == ["In1", "In2", "Unknown"]
    assert {n for n, _ in ps.demoted} == {"TooBig", "TooSmall"}
    assert [p.name for p in ps.secondary] == ["TooBig", "TooSmall", "Sec"]
    assert [p.name for p in ps.exited] == ["Gone"]
    assert ps.retained_unverified == ["Unknown"]
    assert any("below the 5–12" in w for w in ps.warnings)
    assert "peer n insufficient" in ps.percentile_note
    md = exhibit_markdown(_subject(100, peers), ps)
    assert "Gone sold to In1" in md and "TooBig" in md and "[VERIFY]" in md


def test_funnel_without_subject_size_retains_core():
    peers = [Peer(name="A", role=PeerRole.core, size=SizeMetric(value_usd_bn=1)), Peer(name="B", role=PeerRole.core)]
    ps = build_peer_set(_subject(None, peers))
    assert len(ps.core) == 2 and any("filter not applied" in w for w in ps.warnings)


def test_funnel_flags_new_competitor_names():
    ps = build_peer_set(_subject(100, [Peer(name="Beta Bank", role=PeerRole.core, size=SizeMetric(value_usd_bn=100))]),
                        extra_competitors=["Beta Bank", "Newco Bank"])
    assert any("Newco Bank" in w and "Beta Bank" not in w for w in ps.warnings)


@pytest.mark.parametrize("slug,core_expected", [("maybank", 8), ("great-eastern", 9)])
def test_alpha_subjects_load_and_funnel(slug, core_expected):
    s = load_subject(builtin_subject_path(slug))
    assert s.latest_fy == 2025 and s.documents and s.ir_urls
    ps = build_peer_set(s)
    assert len(ps.core) == core_expected  # every declared core peer survives: in band or size [VERIFY]
    assert len(ps.exited) >= 5 and "peer n insufficient" in ps.percentile_note
    assert any("[VERIFY]" in it or "VERIFY" in it for it in s.all_verify_items())


def test_maybank_band_demotes_nothing_but_uob_is_in_band():
    s = load_subject(builtin_subject_path("maybank"))
    ps = build_peer_set(s)
    assert ps.band_low_usd_bn == 75.0 and ps.band_high_usd_bn == 750.0
    assert not ps.demoted and "UOB" in [p.name for p in ps.core]


# ---- financials -------------------------------------------------------------
def test_percentile_direction():
    assert fin.percentile(11.7, [12.5, 9.8, 8.1], higher_is_better=True) == pytest.approx(66.7)
    assert fin.percentile(43.5, [41.0, 48.2, 52.0], higher_is_better=False) == pytest.approx(66.7)
    assert fin.percentile(1.0, [], True) is None


def test_economic_profit_requires_explicit_assumptions():
    rows = fin.load_financials(FIXTURES / "acme-bank" / "financials.csv")
    subj = next(r for r in rows if r.role == "subject")
    ep = fin.economic_profit(subj, fin.EconomicProfitAssumptions())
    assert ep.economic_profit is None and ep.status.startswith("missing-assumption")
    ep2 = fin.economic_profit(subj, fin.EconomicProfitAssumptions(cost_of_equity=0.10, rationale="CAPM placeholder"))
    assert ep2.status == "computed" and ep2.capital_charge == pytest.approx(1050.0) and ep2.economic_profit == pytest.approx(157.1)
    beta = next(r for r in rows if r.entity == "Beta Bank")
    assert fin.economic_profit(beta, fin.EconomicProfitAssumptions(cost_of_equity=0.10)).status.startswith("missing-input")


def test_claim_text_formatting_matches_passages():
    rows = fin.load_financials(FIXTURES / "acme-bank" / "financials.csv")
    subj = next(r for r in rows if r.role == "subject")
    assert fin._fmt(subj, "npat") == "S$1,207.1 million" and fin._fmt(subj, "roe") == "11.7%"
