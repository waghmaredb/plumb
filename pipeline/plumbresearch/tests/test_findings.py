"""Findings module (P5): prospect-level claims, the governance observation (a search, never a claim)
and questions for management. Synthetic text is built from GEH FY2025 sentences (pp. 14, 40, 43, 67, 80)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from plumbverify.models import ClaimKind, Tier

from plumbresearch.cli import FIXTURES_DIR
from plumbresearch.modules import findings as F
from plumbresearch.orchestrator import MODULE_ORDER, run_subject
from plumbresearch.subject import load_subject

GEH = Path(F.__file__).resolve().parents[1] / "subjects" / "great-eastern.yaml"
ACME = FIXTURES_DIR / "acme-bank" / "subject.yaml"

P14 = ("Letter to Shareholders “We rolled out a proprietary AI-\n\npowered platform to automate medical claims, enhancing claim efficiency.”\n\n"
       "In 2025, we deployed an AI-enabled advisory platform that aims to reduce preparation time for financial advisors by "
       "approximately 75%, enabling them to focus more on customer engagement and advice. We rolled out a proprietary AI-powered "
       "platform to automate medical claims, enhancing claim efficiency while improving customer experience. We are also testing an "
       "AI solution for complex underwriting cases to further improve automation and associated efficiency. As we expanded the use "
       "of digital and AI capabilities, we did so with discipline and robust governance.")
P40 = ("The Group also deployed an AI-enabled advisory solution that aims to reduce preparation time for financial advisors by "
       "approximately 75%, enabling them to focus more on customer engagement and advice. In 2025, our AI-driven claims system "
       "delivered same-day turnarounds for 75% of medical claims, one of the fastest among Singapore’s health insurers.")
P41 = "In 2025, we restructured our Data & AI operating model to accelerate transformation."
P43 = ("Leveraging Emerging Technologies and AI As AI accelerates transformation across the insurance industry, we have developed an "
       "Optical Character Recognition solution that extracts and analyses data from medical bills to identify potential wastage and "
       "abuse within medical claims. This capability has significantly strengthened our claims oversight and operational efficiency. "
       "The initiative was awarded the Best Claims Initiative in Malaysia at the Insurance Asia Awards 2025. We have also developed an "
       "AI-driven model to help identify potential misconduct cases, significantly reducing the manual effort and time required for "
       "investigations.")
P67 = ("Ms Zhao Jingyuan (Managing Director, Group Data and Artificial Intelligence) is expected to join Oversea-Chinese Banking "
       "Corporation Limited (“OCBC”) as the Head of the Group Data Office in March 2026. Mr Jimmy Tong (Managing Director, General "
       "and Group Insurance) will be leaving the Group in April 2026. The successors to Ms Zhao Jingyuan and Mr Jimmy Tong will be "
       "named in due course.")
P80 = ("(4) Dr Chong Yoke Sin and Mr Lee Fook Sun will each receive a fixed amount of $20,000 and $5,699 respectively for their "
       "contributions in respect of Great Eastern Group’s information technology infrastructure, data and artificial intelligence "
       "initiatives for FY2025.")
PAGES = {14: P14, 40: P40, 41: P41, 43: P43, 67: P67, 80: P80}


def _text() -> str:
    pages = [PAGES.get(i, f"Page {i} filler text about insurance products and the group governance framework.") for i in range(1, 81)]
    return "\n\f\n".join(pages)


@pytest.fixture(scope="module")
def payload():
    s = load_subject(GEH)
    return F.analyse(s, "https://example.test/ar.pdf", 2025, _text(), Tier.T2, sha256="ab" * 32, page_count=80, engine="test-engine")


def _claims(p):
    return {c["id"].split(".findings.", 1)[1]: c for c in p["claims"]}


def test_deployments_quoted_exactly_with_stage_and_page(payload):
    c = _claims(payload)
    deploy = {k: v for k, v in c.items() if k.startswith("deploy.") and "context" not in k}
    texts = [v["text"] for v in deploy.values()]
    # pull quote (unbalanced “, broken "AI- powered") is not evidence; the body sentence is
    assert not any("“" in t or "AI- powered" in t for t in texts)
    adv = next(v for v in deploy.values() if "advisory platform" in v["text"])
    assert adv["attrs"]["stage"] == "in use" and adv["attrs"]["page_expected"] == 14
    assert adv["attrs"]["also_reported_on_pages"] == [40]  # the p. 40 rewording is merged, not double counted
    und = next(v for v in deploy.values() if "underwriting" in v["text"])
    assert und["attrs"]["stage"] == "testing" and und["attrs"]["use_case"] == "underwriting"
    ocr = next(v for v in deploy.values() if "Optical Character Recognition" in v["text"])
    assert ocr["text"].startswith("As AI accelerates")  # run-in heading trimmed; still an exact substring
    assert ocr["attrs"]["stage"] == "developed" and ocr["attrs"]["page_expected"] == 43
    mis = next(v for v in deploy.values() if "misconduct" in v["text"])
    assert mis["attrs"]["stage"] == "developed; outcome stated"  # verb is "developed"; the stage never promotes it to "in use"
    ctx = [v for k, v in c.items() if k.startswith(ocr["id"].split(".findings.")[1] + ".context")]
    assert any("Malaysia" in v["text"] for v in ctx)  # the market is itself a quotation, not a typed word
    flat = " ".join(_text().split())
    for v in c.values():
        if v["kind"] == "quote":
            assert v["text"] in flat  # every quotation is an exact substring of the whitespace-normalised document


def test_leadership_transition_and_successor(payload):
    c = _claims(payload)
    lead = next(v for k, v in c.items() if k.startswith("leadership.") and v["attrs"].get("status") == "in transition")
    assert "is expected to join Oversea-Chinese Banking Corporation" in lead["text"]
    assert lead["attrs"]["seat_short"] == "Group Data and AI" and lead["attrs"]["page_expected"] == 67
    succ = c["leadership.successor"]
    assert "will be named in due course" in succ["text"] and succ["attrs"]["status"] == "successor not yet named"
    assert "opmodel.1" in c and "Data & AI operating model" in c["opmodel.1"]["text"]


def test_governance_is_an_observation_not_a_claim(payload):
    obs = payload["detail"]["observations"]
    assert len(obs) == 1
    o = obs[0]
    assert o["type"] == "observation" and o["presentation"] == "question"
    assert not any(cl["id"] == o["id"] for cl in payload["claims"])  # never passed to the Verifier as a fact
    se = o["search"]
    assert se["sha256"] == "ab" * 32 and se["pages_searched"] == "1–80" and se["extraction_engine"] == "test-engine"
    assert "model risk" in se["zero_hit_terms"] and "responsible AI" in se["zero_hit_terms"]
    gov = next(t for t in se["broad_governance_terms"] if t["term"] == "governance")
    assert gov["hits"] >= 1 and gov["pages_with_ai_term"] == [14]
    assert len(o["limitations"]) >= 5 and any("Group-level" in l and "OCBC" in l for l in o["limitations"])
    assert "not a finding" in o["statement"]
    # the sentences the observation sits beside are quotation claims (released or withheld by the Verifier)
    adj = [cl for cl in payload["claims"] if cl["attrs"].get("category") == "governance-adjacent"]
    assert any("robust governance" in cl["text"] for cl in adj) and any("artificial intelligence initiatives" in cl["text"] for cl in adj)
    assert o["evidence_claim_ids"] == [cl["id"] for cl in adj]


def test_questions_carry_basis_claims(payload):
    qs = {q["id"].split(".q.", 1)[1]: q for q in payload["detail"]["questions"]}
    ids = {cl["id"] for cl in payload["claims"]}
    assert qs["governance"]["kind"] == "observation" and qs["governance"]["observation_id"].endswith("obs.governance")
    for q in qs.values():
        assert q["basis_claim_ids"] and set(q["basis_claim_ids"]) <= ids
    assert "Group Data and AI" in qs["successor"]["text"]
    assert "75%" in qs["measurement"]["text"] and "aims" in qs["measurement"]["text"]
    assert "underwriting" in next(v["text"] for k, v in qs.items() if k.startswith("testing"))
    assert "regulatory" in qs  # Singapore insurer: MAS clock applies


def test_regulatory_claims_only_where_they_apply():
    geh, acme = load_subject(GEH), load_subject(ACME)
    assert [i["key"] for i in F.load_regulatory(geh)] == ["sg-mas-airm"]
    assert F.load_regulatory(acme) == []
    inst = F.load_regulatory(geh)[0]
    assert all(u.startswith("https://www.mas.gov.sg/") for u in inst["sources"])  # primary source, nothing else
    assert {c["date"] for c in inst["claims"]} == {"7 October 2026", "7 October 2027", "7 October 2028"}


def test_run_offline_withholds_regulatory_clock_and_writes_findings(tmp_path):
    """End to end on the fixture web with a Singapore subject: the MAS host is not in the fixture web, so the
    regulatory claims are withheld (DEAD) — correct behaviour — and the regulatory question is not shown."""
    import yaml

    raw = yaml.safe_load(ACME.read_text())
    raw["home_market"] = "Singapore"
    subj_path = tmp_path / "acme-sg.yaml"
    subj_path.write_text(yaml.safe_dump(raw))
    s = load_subject(subj_path)
    assert "findings" in MODULE_ORDER
    out = run_subject(s, tmp_path / "o", FIXTURES_DIR, fixtures=True, as_of=date(2026, 10, 25), modules=["annual-report", "findings"])
    blocked = {d.claim_id for d in out.report.decisions if d.blocked}
    reg = [c.id for c in out.claims if ".findings.reg." in c.id]
    assert len(reg) == 3 and set(reg) <= blocked
    quotes = [c.id for c in out.claims if c.module == "findings" and c.kind == ClaimKind.quote]
    assert quotes and not set(quotes) & blocked  # quotations lifted from the stored text exact-match (C5)
    rep = json.loads((out.out_dir / "report.json").read_text())
    assert rep["findings"]["observations"][0]["presentation"] == "question"
    assert any(q["id"].endswith("q.regulatory") for q in rep["findings"]["questions"])
    gap_md = (out.out_dir / "gap-register.md").read_text()
    assert "## 6. Observations and questions for management" in gap_md
    assert "withheld (basis not released)" in gap_md
    assert any(g.module == "findings" and g.topic.startswith("observation (question for management") for g in out.gaps)


def test_no_annual_report_means_no_findings(tmp_path):
    import yaml

    raw = yaml.safe_load(ACME.read_text())
    raw["documents"] = [d for d in raw["documents"] if d["kind"] != "annual_report"]
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(raw))
    out = run_subject(load_subject(p), tmp_path / "o", FIXTURES_DIR, fixtures=True, as_of=date(2026, 10, 25), modules=["findings"])
    assert out.claims == [] and not out.modules[0].data_available
