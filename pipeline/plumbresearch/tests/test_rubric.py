"""Annual-report rubric: three synthetic excerpts that must score 1, 3 and 5,
plus competitor and leadership extraction."""
from plumbresearch.modules.annual_report import extract_competitors, extract_leadership, score_rubric

EXCERPT_L1 = """
Chairman's statement. The Group delivered a resilient performance in a year of margin pressure. Net profit rose 4% to
S$820 million and the Board proposes a final dividend of 40 cents. Our technology programme continued, with core
banking upgrades in two markets and further investment in cyber resilience. We also continue to monitor developments
in cloud computing and AI as part of our technology roadmap. Customer deposits grew 6% and the loan book 5%.
Credit quality remained sound with a non-performing loan ratio of 1.4%. We thank our 12,000 employees.
"""

EXCERPT_L3 = """
Digital and innovation. During the year we established an AI centre of excellence and began exploring generative AI.
We piloted a chatbot in our contact centre to answer customer service enquiries about card transactions.
A proof of concept using machine learning for fraud detection on card payments was completed with a vendor partner.
We continue to assess further use cases in onboarding and collections for 2026. Artificial intelligence will be an
important part of our strategy in the years ahead and we are building the data foundations to support it.
"""

EXCERPT_L5 = """
Artificial intelligence at scale. AI is now deployed across the Group's core processes under the leadership of our
Chief AI Officer, who reports to the Group CEO, and the Board Technology Committee reviews AI performance quarterly.
Our AI-powered underwriting engine for SME credit decisions is in production in all markets and has reduced
turnaround time by 60%, from five days to two. The generative AI assistant rolled out to 4,000 contact centre agents
has reduced average handling time by 22% and contributed S$45 million of cost savings in 2025.
Our AI-driven collections model is live and lifted recoveries by 9%. We committed S$1.2 billion to technology and AI
over three years. Our responsible AI framework, aligned to the MAS FEAT principles and ISO/IEC 42001, mandates
model risk validation, fairness testing and human oversight for every production AI system, and realised AI value
is a KPI in the Group CEO scorecard with targets through 2028.
"""


def test_excerpt_scores_1():
    r = score_rubric(EXCERPT_L1)
    assert r.level == 1, r.as_dict()
    assert r.specificity == 0 and r.production == 0


def test_excerpt_scores_3():
    r = score_rubric(EXCERPT_L3)
    assert r.level == 3, r.as_dict()
    assert r.specificity >= 1 and r.quantified == 0 and r.production == 0
    assert r.pilot_only >= 1


def test_excerpt_scores_5():
    r = score_rubric(EXCERPT_L5)
    assert r.level == 5, r.as_dict()
    assert r.production >= 2 and r.quantified >= 2 and r.governance >= 1 and r.ownership >= 1
    assert r.investment_disclosed


def test_rubric_is_monotone_and_explains_itself():
    levels = [score_rubric(t).level for t in (EXCERPT_L1, EXCERPT_L3, EXCERPT_L5)]
    assert levels == sorted(levels) == [1, 3, 5]
    r = score_rubric(EXCERPT_L5)
    assert r.rule.startswith("L5") and r.evidence["quantified"]  # the rater can see the triggering sentences


def test_empty_text_is_level_1():
    assert score_rubric("").level == 1


def test_competitor_extraction():
    text = ("Compared with peers such as Beta Bank and Gamma Financial, our digital penetration ranks second, while Delta Bank "
            "remains the largest competitor by assets. Acme Bank opened three branches. The weather was fine.")
    names = [c["name"] for c in extract_competitors(text, ["Acme Bank", "Acme"])]
    assert names == ["Beta Bank", "Gamma Financial", "Delta Bank"]


def test_leadership_extraction():
    text = ("Priya Nair was appointed Group Chief Data and AI Officer in January 2025, reporting to the Group CEO. "
            "The Head of Data Science, Tan Wei Ming, joined in March. Our CTO oversees infrastructure. "
            "The CIO of a peer bank spoke at the conference.")
    out = {l["title"].lower(): l for l in extract_leadership(text)}
    assert "group chief data and ai officer" in out
    assert out["group chief data and ai officer"]["names"] == ["Priya Nair"]
    assert out["group chief data and ai officer"]["reports_to"] == "Group CEO"
    assert out["group chief data and ai officer"]["ai_scope"] is True
    assert "head of data science" in out and "Tan Wei Ming" in out["head of data science"]["names"]
