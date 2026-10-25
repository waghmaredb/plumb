"""Run-3 issues (runs/great-eastern/2026-10-25-ar-attached-fixed/README.md, "New issues"):
org attribution, departed / leaving status, pull-quote fragments and biography sentences.
Every fixture is a short excerpt of the Great Eastern Holdings FY2025 annual report as the
layout extractor (pdftotext -layout + column split) returns it."""
from pathlib import Path

from plumbverify.extract import PAGE_SEP
from plumbverify.models import Tier

from plumbresearch.modules.annual_report import _analyse, extract_leadership, has_leadership_title, score_rubric, subject_org_aliases
from plumbresearch.subject import load_subject
from plumbresearch.textutil import drop_fragments, is_bio_sentence, is_fragment, rubric_sentences

GEH_YAML = Path(__file__).resolve().parents[1] / "plumbresearch" / "subjects" / "great-eastern.yaml"
ALIASES = {
    "subject": ["Great Eastern Holdings", "Great Eastern", "GEH"],
    "subject_subsidiary": ["Great Eastern Life", "GE Life", "Great Eastern General", "GE General", "Great Eastern Takaful", "GELM"],
    "parent": ["OCBC", "Oversea-Chinese Banking Corporation", "Bank of Singapore"],
}

# p. 67, corporate governance report (Nominating Committee, senior management changes)
P67 = (
    "Mr Colin Chan (Managing Director, Group Marketing), Mr Ryan Cheong (Managing Director, Group Customer and Digital), "
    "Mr Clement Lien (Managing Director, Group Premier Wealth) and Mr Patrick Peck (Managing Director, Regional Agency, "
    "Financial Advisors and Bancassurance) left the Group in 2025. Ms Zhao Jingyuan (Managing Director, Group Data and "
    "Artificial Intelligence) is expected to join Oversea-Chinese Banking Corporation Limited (“OCBC”) as the Head of "
    "the Group Data Office in March 2026. Mr Jimmy Tong (Managing Director, General and Group Insurance) will be leaving "
    "the Group in April 2026. The successors to Ms Zhao Jingyuan and Mr Jimmy Tong will be named in due course."
)
# p. 229, management-team listing with region and entity headers
P229 = (
    "Management Team\n\nGROUP AND SINGAPORE\n\nGreat Eastern Holdings Limited The Great Eastern Life Assurance Company Limited "
    "Great Eastern General Insurance Limited\n\nGary Goh Kaye Lee Managing Director, Group Information Technology\n\n"
    "Zhao Jingyuan Managing Director, Group Data and AI\n\nMALAYSIA\n\nGreat Eastern Life Assurance (Malaysia) Berhad\n\n"
    "Wynn Chew Ai Ling Division Head, Group & Digital Affinity\n\n"
    "Great Eastern General Insurance (Malaysia) Berhad Jeremy Yeap Cheng Sun Chief Executive Officer Denise Chai Kuam Sau "
    "Division Head, Distribution Strategy & Management Lucy Loo Liuxi Division Head, Marketing and Digital Transformation "
    "Chew Han Wah Appointed Actuary\n"
)
# p. 18, director biography (roles held at the parent)
P18 = ("Mr Choo was previously an Advisor to the Group CEO of OCBC from January 2023 to January 2024. He was the Group Chief "
       "Risk Officer of OCBC from 2014 to 2022 and the Group Chief Information Security Officer of OCBC from 2021 to 2022.")
# p. 14, letter to shareholders: pull quote set as short lines, then the body text it repeats
P14 = (
    "“We rolled out a proprietary AI-\n\npowered platform to automate medical claims, enhancing\n\nclaim efficiency while\n\n"
    "improving customer experience. We are also\n\ntesting an AI solution for\n\ncomplex underwriting cases to further improve "
    "automation and associated efficiency.”\n\n"
    "In 2025, we deployed an AI-enabled advisory platform that aims to reduce preparation time for financial advisors by "
    "approximately 75%, enabling them to focus more on customer engagement and advice. We rolled out a proprietary "
    "AI-powered platform to automate medical claims, enhancing claim efficiency while improving customer experience. "
    "We are also testing an AI solution for complex underwriting cases to further improve automation and associated efficiency.\n"
)
# p. 31, key-executive biography (name above title, then bio sentences)
P31 = (
    "ZHAO JINGYUAN Managing Director, Group Data and AI\n\nWith Great Eastern since 2022. Over 20 years of experience in Data, "
    "Analytics & AI and has held leadership positions leading data-driven transformation across various industries. "
    "Responsible for improving customer experience, operational efficiency and risk management through Data, Analytics & AI.\n"
)


def _by_title(text, aliases=ALIASES):
    return {l["title"]: l for l in extract_leadership(text, org_aliases=aliases)}


# ---- issue 2: org attribution ---------------------------------------------------
def test_join_as_title_is_attributed_to_the_parent():
    out = _by_title(P67)
    head = out["Head of the Group Data Office"]
    assert head["org_role"] == "parent" and head["org"].startswith("Oversea-Chinese Banking Corporation")
    assert head["org_basis"] == "clause" and head["status"] == "incoming" and head["effective"] == "March 2026"
    assert not head["counts_d12"]
    zhao = out["Managing Director, Group Data and Artificial Intelligence"]
    assert zhao["org_role"] == "subject" and zhao["names"] == ["Zhao Jingyuan"]


def test_of_parent_clause_and_former_role_in_director_bio():
    out = extract_leadership(P18, org_aliases=ALIASES)
    ciso = next(l for l in out if l["title"] == "Group Chief Information Security Officer")
    assert ciso["org"] == "OCBC" and ciso["org_role"] == "parent" and ciso["status"] == "former"


def test_listing_section_headers_attribute_subject_and_subsidiaries():
    out = _by_title(P229)
    zhao = out["Managing Director, Group Data and AI"]
    assert zhao["org_role"] == "subject" and zhao["org"] == "Great Eastern Holdings Limited" and zhao["org_basis"] == "section"
    wynn = out["Division Head, Group & Digital Affinity"]
    assert wynn["org_role"] == "subject-subsidiary" and wynn["org"] == "Great Eastern Life Assurance (Malaysia) Berhad"
    lucy = out["Division Head, Marketing and Digital Transformation"]
    assert lucy["org_role"] == "subject-subsidiary" and lucy["org"] == "Great Eastern General Insurance (Malaysia) Berhad"
    assert lucy["names"] == ["Lucy Loo Liuxi"]
    assert all(l["counts_d12"] for l in (zhao, wynn, lucy))


def test_biography_next_sentence_names_the_employer():
    out = _by_title(P31)
    zhao = out["Managing Director, Group Data and AI"]
    assert zhao["org_role"] == "subject" and zhao["org_basis"] == "biography"


def test_parent_only_title_sentence_is_not_subject_ownership():
    s = "Mr Tan is the Head of the Group Data Office of OCBC."
    assert has_leadership_title(s) is True  # no aliases: the report's own default
    assert has_leadership_title(s, ALIASES) is False


# ---- issue 3: departed / leaving status ---------------------------------------------
def test_left_the_group_is_departed_and_not_counted():
    ryan = _by_title(P67)["Managing Director, Group Customer and Digital"]
    assert ryan["names"] == ["Ryan Cheong"] and ryan["status"] == "departed"
    assert ryan["status_detail"] == "left the Group" and ryan["effective"] == "2025"
    assert ryan["org_role"] == "subject" and not ryan["counts_d12"] and not ryan["seat_in_transition"]


def test_expected_to_join_other_org_is_seat_in_transition():
    zhao = _by_title(P67)["Managing Director, Group Data and Artificial Intelligence"]
    assert zhao["status"] == "leaving" and zhao["seat_in_transition"] and zhao["counts_d12"]
    assert "expected to join Oversea-Chinese Banking Corporation" in zhao["status_detail"]
    assert "successor to be named in due course" in zhao["status_detail"]
    assert zhao["effective"] == "March 2026"


def test_leaving_status_propagates_by_name_to_listing_and_bio_pages():
    text = P31 + PAGE_SEP + P67 + PAGE_SEP + P229
    proxies = [l for l in extract_leadership(text, org_aliases=ALIASES) if l["ai_scope"]]
    zhao = next(l for l in proxies if "Zhao Jingyuan" in l["names"] and l["org_role"] == "subject")
    assert zhao["pages"] == [1, 2, 3] and zhao["status"] == "leaving" and zhao["seat_in_transition"]
    counted = sorted(l["title"] for l in proxies if l["counts_d12"])
    assert counted == ["Division Head, Group & Digital Affinity", "Division Head, Marketing and Digital Transformation",
                       "Managing Director, Group Data and AI"], counted
    assert [l["title"] for l in proxies if l["org_role"] == "parent"] == ["Head of the Group Data Office"]


def test_other_departure_phrases():
    for sent, status in [
        ("Mr Tan Ah Kow, Chief Data Officer, retired on 30 June 2025.", "departed"),
        ("Ms Lim Bee Hoon stepped down as Head of Digital on 1 May 2025.", "departed"),
        ("Mr Lee Kok Wah ceased to be the Chief Digital Officer with effect from 1 April 2025.", "departed"),
        ("Mr Ong Boon Seng, Head of Data Analytics, will be leaving the Group in April 2026.", "leaving"),
        ("Ms Ng Siew Lan was appointed Chief Data Officer of Great Eastern Life in 2025.", "present"),
    ]:
        out = [l for l in extract_leadership(sent, org_aliases=ALIASES) if l["ai_scope"]]
        assert out and out[0]["status"] == status, (sent, out)
    retired = extract_leadership("Mr Tan Ah Kow, Chief Data Officer, retired on 30 June 2025.", org_aliases=ALIASES)[0]
    assert retired["effective"] == "30 June 2025"


def test_successor_sentence_alone_marks_named_holder_in_transition():
    text = "Mr Jimmy Tong, Head of Digital Insurance, oversees the platform team. The successor to Mr Jimmy Tong will be announced in due course."
    l = [x for x in extract_leadership(text, org_aliases=ALIASES) if x["ai_scope"]][0]
    assert l["status"] == "leaving" and l["seat_in_transition"] and "successor" in l["status_detail"]


# ---- issue 1: pull-quote fragments --------------------------------------------------
def test_pull_quote_fragment_is_a_fragment():
    assert is_fragment("“We rolled out a proprietary AI-")
    assert is_fragment("testing an AI solution for")
    assert not is_fragment("We rolled out a proprietary AI-powered platform to automate medical claims, enhancing claim efficiency.")


def test_fragments_and_duplicates_are_dropped_from_rubric_sentences():
    kept = rubric_sentences(P14)
    assert "“We rolled out a proprietary AI-" not in kept
    assert not any(s.startswith("testing an AI") for s in kept)
    assert sum(s.startswith("We rolled out a proprietary AI-powered platform") for s in kept) == 1
    # an exact repeat elsewhere (pull quote set in full) is counted once
    assert drop_fragments(["We deployed an AI chatbot for claims triage in 2025.", "We deployed an AI chatbot for claims triage in 2025."]) == \
        ["We deployed an AI chatbot for claims triage in 2025."]


def test_pull_quote_no_longer_inflates_production():
    r = score_rubric(P14)
    assert r.production == 2, r.evidence["production"]  # deployed advisory + rolled out claims, no fragment
    assert all(not s.startswith("“") for s in r.evidence["production"])
    assert r.fragments_dropped >= 2


# ---- issue 4: biography sentences ---------------------------------------------------
def test_bio_sentence_patterns():
    assert is_bio_sentence("Responsible for improving customer experience, operational efficiency and risk management through Data, Analytics & AI.")
    assert is_bio_sentence("Over 20 years of experience in Data, Analytics & AI and has held leadership positions across industries.")
    assert is_bio_sentence("With Great Eastern since 2022.")
    assert not is_bio_sentence("We rolled out a proprietary AI-powered platform to automate medical claims.")


def test_bio_sentences_count_only_toward_ownership():
    r = score_rubric(P31, ALIASES)
    assert r.production == 0 and r.specificity == 0 and r.quantified == 0, r.as_dict()
    assert r.bio_sentences == 2
    assert r.ownership == 1  # the name-and-title line
    bio_own = score_rubric("Responsible for the Group AI programme as Chief Data Officer, deployed across 5 markets with 30% savings.", ALIASES)
    assert bio_own.production == 0 and bio_own.quantified == 0 and bio_own.ownership == 1


def test_operational_efficiency_is_not_production():
    r = score_rubric("Our in-house AI capabilities are increasingly reshaping how we serve customers and drive operational efficiency.")
    assert r.production == 0
    assert score_rubric("Our AI claims engine has been operational since March across all markets.").production == 1


# ---- module: D1.2 signal counts subject seats only; parent titles are context --------
def test_module_signal_counts_subject_seats_and_reports_parent_context():
    subject = load_subject(GEH_YAML)
    aliases = subject_org_aliases(subject)
    assert "OCBC" in aliases["parent"] and "GELM" in aliases["subject_subsidiary"]
    text = P31 + PAGE_SEP + P67 + PAGE_SEP + P229
    res = _analyse(subject, "https://example.test/ar.pdf", "annual_report", 2025, text, Tier.T2)
    sig = {s["id"].rsplit(".", 1)[-1]: s for s in res["signals"]}
    lead = sig["leadership"]
    assert lead["value"] == 3 and lead["detail"]["present"] == 2 and lead["detail"]["in_transition"] == 1
    assert lead["detail"]["departed_or_former"] == 1 and lead["detail"]["parent_context"] == 1
    assert "seat(s) in transition (Managing Director, Group Data and AI (Zhao Jingyuan)" in lead["note"]
    assert sig["leadership_parent"]["value"] == 1
    notes = [c["note"] for c in res["claims"] if c["id"].split(".")[-1].startswith("l")]
    assert any("Head of the Group Data Office" in n and "(parent, clause)" in n for n in notes)
    zhao_claim = next(c for c in res["claims"] if "Managing Director, Group Data and AI" in c["note"])
    assert "expected to join" in zhao_claim["passage"]  # the transition sentence is the evidence


def test_entity_header_expansion_stops_at_the_first_legal_suffix():
    aliases = subject_org_aliases(load_subject(GEH_YAML))  # includes the full name "Great Eastern Holdings Limited"
    zhao = _by_title(P229, aliases)["Managing Director, Group Data and AI"]
    assert zhao["org"] == "Great Eastern Holdings Limited", zhao["org"]


def test_long_listing_line_yields_a_name_and_title_passage():
    subject = load_subject(GEH_YAML)
    filler = " ".join(f"Person{chr(65 + i)} Name{chr(65 + i)} Division Head, Claims Management" for i in range(12))
    text = ("MALAYSIA\n\nGreat Eastern General Insurance (Malaysia) Berhad " + filler +
            " Lucy Loo Liuxi Division Head, Marketing and Digital Transformation Chew Han Wah Appointed Actuary\n")
    res = _analyse(subject, "https://example.test/ar.pdf", "annual_report", 2025, text, Tier.T2)
    lucy = next(c for c in res["claims"] if "Lucy Loo Liuxi" in c["note"])
    assert lucy["passage"] == "Lucy Loo Liuxi Division Head, Marketing and Digital Transformation"
    assert lucy["passage"] in text
