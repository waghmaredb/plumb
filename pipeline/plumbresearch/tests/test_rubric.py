"""Annual-report rubric: three synthetic excerpts that must score 1, 3 and 5,
plus competitor and leadership extraction."""
from plumbverify.extract import PAGE_SEP

from plumbresearch.modules.annual_report import classify_title, extract_competitors, extract_leadership, score_rubric
from plumbresearch.textutil import is_competitor_context, org_names

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


# ---- defect 1: the two Great Eastern FY2025 layouts, and a negative ----------
# page 31 of the report (pdftotext -layout + column split): name in caps above a two-line title
GEH_NAME_ABOVE_TITLE = (
    "GARY GOH\nManaging Director,\nGroup Information Technology\n\nWith Great Eastern since January 2025.\n"
    "Over 28 years of experience in IT.\n\nZHAO JINGYUAN\nManaging Director,\nGroup Data and AI\n\n"
    "With Great Eastern since 2022.\nOver 20 years of experience in Data,\nAnalytics & AI and has held leadership\n"
    "positions leading data-driven transformation across various industries.\n"
)
# page 229 (management-team listing, one person per line pair; pypdf joins the whole column into one sentence)
GEH_NAME_BEFORE_TITLE = (
    "Gary Goh Kaye Lee Managing Director, Group Information Technology Zhao Jingyuan Managing Director, Group Data and AI "
    "James Lee Soo Hian Managing Director, Group Human Capital Kate Chiew Fung Yen Group Chief Risk Officer"
)
# page 67 (corporate governance report)
GEH_PARENTHETICAL = (
    "Ms Zhao Jingyuan (Managing Director, Group Data and Artificial Intelligence) is expected to join Oversea-Chinese "
    "Banking Corporation Limited (\u201cOCBC\u201d) as the Head of the Group Data Office in March 2026."
)
GEH_NEGATIVE = (
    "David Lim Kang Chiang Managing Director, Group Agency and Financial Advisors Chua Keng Hong Group Chief Investment "
    "Officer Patrick Kok Managing Director, Group Operations. The data showed that the Director of Group Agency reported strong sales."
)


def test_leadership_name_above_title_layout():
    out = extract_leadership(GEH_NAME_ABOVE_TITLE)
    proxies = [l for l in out if l["ai_scope"]]
    assert len(proxies) == 1, out
    l = proxies[0]
    assert l["title"] == "Managing Director, Group Data and AI"
    assert l["names"] == ["Zhao Jingyuan"] and l["role_class"] == "CAIO-equivalent"
    assert "ZHAO JINGYUAN" in l["context"]
    # the IT title on the same page has no data / AI / digital scope and is not returned
    assert [l["title"] for l in out] == ["Managing Director, Group Data and AI"]


def test_leadership_name_before_title_listing():
    out = {l["title"]: l for l in extract_leadership(GEH_NAME_BEFORE_TITLE)}
    assert "Managing Director, Group Data and AI" in out, out.keys()
    l = out["Managing Director, Group Data and AI"]
    assert l["names"] == ["Zhao Jingyuan"] and l["ai_scope"] and l["role_class"] == "CAIO-equivalent"
    assert "Managing Director, Group Human Capital" not in out  # no scope keyword


def test_leadership_parenthetical_title_and_page():
    text = "Page one text.\n" + PAGE_SEP + "\n" + GEH_PARENTHETICAL
    out = {l["title"]: l for l in extract_leadership(text)}
    l = out["Managing Director, Group Data and Artificial Intelligence"]
    assert l["names"] == ["Zhao Jingyuan"] and l["role_class"] == "CAIO-equivalent" and l["page"] == 2
    assert l["context"].startswith("Ms Zhao Jingyuan")


def test_leadership_negative_titles_do_not_match():
    out = extract_leadership(GEH_NEGATIVE)
    assert [l for l in out if l["ai_scope"]] == [], out
    assert "Managing Director, Group Agency" not in {l["title"] for l in out}


def test_leadership_merges_ai_and_artificial_intelligence_spellings():
    out = extract_leadership(GEH_NAME_ABOVE_TITLE + "\n\n" + GEH_PARENTHETICAL)
    proxies = [l for l in out if l["ai_scope"]]
    titles = sorted(l["title"] for l in proxies)
    # one entry for Zhao's title (AI / Artificial Intelligence spellings merged) plus the OCBC-side title in the same sentence
    assert titles == ["Head of the Group Data Office", "Managing Director, Group Data and AI"], titles
    assert proxies[0]["names"] == ["Zhao Jingyuan"] or proxies[1]["names"] == ["Zhao Jingyuan"]


def test_classify_title():
    assert classify_title("Managing Director, Group Data and AI") == "CAIO-equivalent"
    assert classify_title("Chief Data Officer") == "CDO-equivalent"
    assert classify_title("Head of Analytics") == "CDO-equivalent"
    assert classify_title("Chief Digital Officer") == "CDigO"
    assert classify_title("Head of Machine Learning") == "CAIO-equivalent"
    assert classify_title("Chief Technology Officer") == "other"


# ---- defect 3: competitor extraction needs an organisation hit ----------------
def test_period_comparison_is_not_a_competitor_context():
    assert not is_competitor_context("Total Weighted New Sales fell 15% compared with FY2025.")
    assert not is_competitor_context("Profit rose 21% versus the prior year, relative to the previous period.")
    assert is_competitor_context("Compared with peers, our digital penetration ranks second.")
    assert is_competitor_context("We gained market share from AIA Group during the year.")


def test_competitor_requires_org_hit_not_bare_acronym():
    text = ("Claims were paid faster compared with FY2025 and ahead of NEA and MOH service indicators. "
            "We compete with Prudential Assurance Company Singapore and AIA for agency talent. "
            "Compared with peers our market share in Singapore Insurance rose, and we benchmarked against Income Insurance Ltd.")
    names = [c["name"] for c in extract_competitors(text, ["Great Eastern"])]
    assert "NEA" not in names and "MOH" not in names and "FY2025" not in names
    assert "Prudential Assurance Company Singapore" in names
    assert "Income Insurance Ltd" in names
    assert "AIA" not in names  # bare acronym without a known alias
    assert "Singapore Insurance" not in names  # descriptive phrase, not a name


def test_competitor_known_peer_alias_from_subject_yaml_counts():
    text = "We compete with AIA and Prudential for agency talent, and our market share compared with Singlife rose."
    with_alias = [c["name"] for c in extract_competitors(text, ["Great Eastern"], known_aliases=["AIA", "Prudential", "Singlife"])]
    assert sorted(with_alias) == ["AIA", "Prudential", "Singlife"]
    assert extract_competitors(text, ["Great Eastern"]) == []


def test_org_names_suffix_and_exclusions():
    assert org_names("Oversea-Chinese Banking Corporation Limited (\u201cOCBC\u201d) is our parent.") == ["Oversea-Chinese Banking Corporation Limited"]
    assert org_names("Our life insurance business and the Group grew.") == []
    assert org_names("Great Eastern General Insurance Limited grew.", ["Great Eastern"]) == []
