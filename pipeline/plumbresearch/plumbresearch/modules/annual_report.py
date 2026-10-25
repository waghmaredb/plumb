"""Annual-report module: the 1–5 AI disclosure rubric, named-competitor
extraction and leadership-structure extraction (instrument D1.1, D1.2, D1.4,
D4.4, D5.4, D6.1, D8.3 proxies; competitor seed for the peer funnel).

Rubric (instrument D1.1 proxy: "annual report / 10-K AI paragraph scored on
the 1–5 Yu et al. rubric, L1 mention -> L5 deep integration"). Yu et al.
(arXiv 2607.08920) grade disclosures from bare mention through intent, pilot,
production with expected financial outcomes, to deep integration. This
module implements that ladder as explicit rules over five extracted
components so two raters (instrument §7 κ test) can see exactly why a level
was assigned:

    mentions      AI-term mentions, and density per 1,000 words
    specificity   AI sentences that name a concrete use case / function
    production    AI sentences with deployment language (live, rolled out, in production, scaled)
    quantified    AI sentences carrying a number tied to an outcome (savings, hours, %, value)
    governance    AI sentences with governance / responsible-AI / model-risk language
    ownership     AI sentences naming board or C-level accountability (CAIO/CDO, board committee, targets)

Level rules (first rule that fits, from the top):
    L5  production >= 2 and quantified >= 2 and governance >= 1 and ownership >= 1
    L4  production >= 1 and specificity >= 2 and (quantified >= 1 or investment disclosed)
    L3  specificity >= 1 (a named use case or pilot), whatever else is missing
    L2  mentions >= 3 (AI discussed as intent or strategy) without a named use case
    L1  mentions <= 2, or no mentions at all (absent / passing mention)

The rubric level is a Signal (computed in code). The sentences that triggered
each component are emitted as quotation claims so the Verifier proves they
exist in the stored document (C5), and disclosed investment figures as number
claims (C4). The proxy corroborates only; it never lifts an item above 3
(instrument §5.4).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from plumbverify.log import HashChainLog
from plumbverify.fetch import EvidenceStore
from plumbverify.match import parse_numbers
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import Subject
from ..textutil import ai_sentences, has_any, is_competitor_context, mentions_per_1000, org_names, sentences

MODULE = "annual-report"

SPECIFICITY = [
    r"\buse[- ]cases?\b", r"\bunderwrit", r"\bclaims? (?:automation|processing|assessment|triage)\b", r"\bfraud\b",
    r"\bonboarding\b", r"\bcredit (?:decision|scoring|assessment)\b", r"\badvisory\b", r"\bcustomer service\b",
    r"\bcontact centre\b", r"\bcall centre\b", r"\bchatbot\b", r"\bvirtual assistant\b", r"\btransaction monitoring\b",
    r"\banti[- ]money laundering\b", r"\baml\b", r"\bkyc\b", r"\bcollections?\b", r"\bpersonalis", r"\bnext[- ]best\b",
    r"\bdocument processing\b", r"\bcode (?:generation|assistant)\b", r"\bcopilot\b", r"\brelationship managers?\b",
    r"\bagents? (?:are|were|is|was) (?:using|equipped)\b", r"\bpilot(?:ed|s)?\b", r"\bproof of concept\b",
    r"\btrial(?:led|s)?\b", r"\bmedical claims\b", r"\bpolicy servicing\b", r"\bwealth\b", r"\btreasury\b",
]
PRODUCTION = [
    r"\bin production\b", r"\brolled out\b", r"\broll-?out\b", r"\bdeployed\b", r"\bdeployment\b", r"\blaunched\b",
    r"\bwent live\b", r"\bis live\b", r"\bnow live\b", r"\bscaled\b", r"\bat scale\b", r"\bin use across\b",
    r"\boperational\b", r"\bimplemented\b", r"\bembedded in\b", r"\bprocess(?:es|ed|ing) (?:over|more than|\d)",
]
PILOT_ONLY = [r"\bpilot", r"\bproof of concept\b", r"\bexploring\b", r"\bunder test\b", r"\bbeing tested\b", r"\btrial"]
OUTCOME = [
    r"\bsav(?:ed|ings?)\b", r"\breduc(?:ed|tion|ing)\b", r"\bproductivity\b", r"\brevenue\b", r"\bincome\b",
    r"\beconomic value\b", r"\bvalue (?:of|created|generated|delivered)\b", r"\buplift\b", r"\bfaster\b", r"\bcut\b",
    r"\bhours\b", r"\bstraight[- ]through\b", r"\baccuracy\b", r"\befficien", r"\bcost[- ]to[- ]income\b", r"\bebit\b",
    r"\bmargin\b", r"\btime[- ]to[- ]", r"\bturnaround\b", r"\bper cent\b", r"%",
]
GOVERNANCE = [
    r"\bresponsible ai\b", r"\bai governance\b", r"\bethic", r"\bmodel risk\b", r"\bfeat\b", r"\bveritas\b",
    r"\biso(?:/iec)? 42001\b", r"\bai (?:policy|policies|principles|framework|guardrails|oversight|committee|council)\b",
    r"\bfairness\b", r"\bexplainab", r"\btransparen", r"\baccountab", r"\bhuman[- ]in[- ]the[- ]loop\b",
    r"\bhuman oversight\b", r"\bbias\b", r"\bai risk\b", r"\bmodel validation\b", r"\bnist ai rmf\b", r"\bmas (?:airg|ai risk)\b",
]
OWNERSHIP = [
    r"\bboard\b", r"\bchief (?:ai|artificial intelligence|data|digital|technology|information|analytics)[\w &,]* officer\b",
    r"\bcaio\b", r"\bcdo\b", r"\bexecutive committee\b", r"\bexco\b", r"\bgroup ceo\b", r"\bchief executive\b",
    r"\bremuneration\b", r"\bscorecard\b", r"\bkpis?\b", r"\btarget(?:s|ed|ing)?\b", r"\bby 20\d\d\b", r"\bcommitt(?:ed|ment) to invest\b",
]
INVESTMENT = [r"\binvest(?:ment|ing|ed|s)?\b", r"\bspend(?:ing|s)?\b", r"\bbudget\b", r"\bcapex\b", r"\bcapital expenditure\b", r"\bcommit(?:s|ted|ment)?\b", r"\bearmark"]

LEADERSHIP_TITLES = re.compile(
    r"(?P<title>(?:Group\s+)?Chief\s+(?:Artificial Intelligence|AI|Data(?:\s+(?:and|&)\s+(?:AI|Analytics|Artificial Intelligence))?|"
    r"Digital(?:\s+(?:and|&)\s+(?:Data|Technology|AI))?|Technology(?:\s+(?:and|&)\s+(?:Operations|Data|AI))?|Information|Analytics|"
    r"Transformation|Innovation)\s+Officer"
    r"|(?:Group\s+)?Head\s+of\s+(?:AI Governance|Artificial Intelligence|Generative AI|GenAI|Machine Learning|Model Risk|"
    r"Data Science|Data(?:\s+(?:and|&)\s+(?:AI|Analytics))?|Analytics|AI)"
    r"|\bCAIO\b|\bCDAO\b|\bCDO\b|\bCTO\b|\bCIO\b)",
    re.I,
)
REPORTS_TO = re.compile(r"report(?:s|ing)?\s+(?:directly\s+)?to\s+the\s+(?P<to>(?:Group\s+)?(?:CEO|Chief Executive(?: Officer)?|COO|Board|President|Managing Director))", re.I)
NAME_BEFORE = re.compile(r"(?P<name>[A-Z][a-z]+(?:\s+(?:bin|binti|bte|al|de|van|[A-Z][a-z]+|[A-Z]\.)){1,4}),?\s+(?:is|as|was appointed|has been appointed|our|the|serves as|,)?\s*$")
NAME_AFTER = re.compile(r"^,?\s*(?P<name>[A-Z][a-z]+(?:\s+(?:bin|binti|bte|al|de|van|[A-Z][a-z]+|[A-Z]\.)){1,4})")


@dataclass
class RubricScore:
    level: int
    mentions: int
    words: int
    density_per_1000: float
    specificity: int
    production: int
    pilot_only: int
    quantified: int
    governance: int
    ownership: int
    investment_disclosed: bool
    rule: str
    evidence: dict[str, list[str]] = field(default_factory=dict)  # component -> sentences

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["evidence"] = {k: v[:5] for k, v in self.evidence.items()}
        return d


def score_rubric(text: str) -> RubricScore:
    """Apply the documented rules to extracted text. Deterministic."""
    n, w, dens = mentions_per_1000(text)
    ai_s = ai_sentences(text)
    ev: dict[str, list[str]] = {k: [] for k in ("specificity", "production", "quantified", "governance", "ownership", "investment")}
    pilot_only = 0
    for s in ai_s:
        spec = has_any(s, SPECIFICITY)
        prod = has_any(s, PRODUCTION)
        pil = has_any(s, PILOT_ONLY)
        nums = [t for t in parse_numbers(s) if t.unit or t.value >= 10 or "." in t.raw]
        quant = bool(nums) and has_any(s, OUTCOME)
        gov = has_any(s, GOVERNANCE)
        own = has_any(s, OWNERSHIP)
        inv = bool([t for t in parse_numbers(s) if t.unit and t.unit != "%"]) and has_any(s, INVESTMENT)
        strong_prod = has_any(s, [r"\brolled out\b", r"\bdeployed\b", r"\bin production\b", r"\blive\b", r"\bscaled\b"])
        if spec:
            ev["specificity"].append(s)
        if pil and not strong_prod:
            pilot_only += 1  # pilot / PoC / exploring language without a deployment verb is not production
        elif prod:
            ev["production"].append(s)
        if quant:
            ev["quantified"].append(s)
        if gov:
            ev["governance"].append(s)
        if own:
            ev["ownership"].append(s)
        if inv:
            ev["investment"].append(s)
    spec_n, prod_n, q_n, g_n, o_n = (len(ev[k]) for k in ("specificity", "production", "quantified", "governance", "ownership"))
    inv_b = bool(ev["investment"])
    if prod_n >= 2 and q_n >= 2 and g_n >= 1 and o_n >= 1:
        level, rule = 5, "L5: >=2 production use cases, >=2 quantified outcomes, governance statement, board/C-level ownership"
    elif prod_n >= 1 and spec_n >= 2 and (q_n >= 1 or inv_b):
        level, rule = 4, "L4: production language with >=2 specific use cases and a quantified outcome or disclosed investment"
    elif spec_n >= 1:
        level, rule = 3, "L3: at least one named use case or pilot; no production-with-outcomes evidence"
    elif n >= 3:
        level, rule = 2, "L2: AI discussed as intent or strategy (>=3 mentions) without a named use case"
    else:
        level, rule = 1, "L1: absent or passing mention (<=2 mentions)"
    return RubricScore(level=level, mentions=n, words=w, density_per_1000=round(dens, 2), specificity=spec_n,
                       production=prod_n, pilot_only=pilot_only, quantified=q_n, governance=g_n, ownership=o_n,
                       investment_disclosed=inv_b, rule=rule, evidence=ev)


# --------------------------------------------------------------------------
# Named-competitor extraction
# --------------------------------------------------------------------------
def extract_competitors(text: str, exclude_patterns: list[str]) -> list[dict]:
    found: dict[str, dict] = {}
    for s in sentences(text):
        if not is_competitor_context(s):
            continue
        for name in org_names(s, exclude_patterns):
            e = found.setdefault(name, {"name": name, "count": 0, "passages": []})
            e["count"] += 1
            if len(e["passages"]) < 3:
                e["passages"].append(s)
    return sorted(found.values(), key=lambda e: -e["count"])


# --------------------------------------------------------------------------
# Leadership-structure extraction
# --------------------------------------------------------------------------
def extract_leadership(text: str) -> list[dict]:
    out: dict[str, dict] = {}
    for s in sentences(text):
        for m in LEADERSHIP_TITLES.finditer(s):
            title = re.sub(r"\s+", " ", m.group("title")).strip()
            if title.upper() in ("CTO", "CIO", "CDO", "CAIO", "CDAO") and not re.search(r"\b(officer|chief|appointed|role|our|the)\b", s, re.I):
                continue  # bare acronym without a role context
            name = None
            mb = NAME_BEFORE.search(s[: m.start()])
            ma = NAME_AFTER.search(s[m.end():])
            if mb:
                name = mb.group("name")
            elif ma:
                name = ma.group("name")
            rt = REPORTS_TO.search(s)
            key = title.lower()
            e = out.setdefault(key, {"title": title, "names": [], "reports_to": None, "passages": [], "ai_scope": False})
            if name and name not in e["names"]:
                e["names"].append(name)
            if rt and not e["reports_to"]:
                e["reports_to"] = rt.group("to")
            if re.search(r"\b(ai|artificial intelligence|data|analytics)\b", title, re.I):
                e["ai_scope"] = True
            if len(e["passages"]) < 3 and s not in e["passages"]:
                e["passages"].append(s)
    return list(out.values())


# --------------------------------------------------------------------------
# Module entry point
# --------------------------------------------------------------------------
def _analyse(subject: Subject, doc_url: str, doc_kind: str, fy: Optional[int], text: str, tier) -> dict:
    rubric = score_rubric(text)
    claims: list[ResearchClaim] = []
    label = confidence_for_tier(tier)
    base = f"{subject.slug}.ar.{doc_kind}.{fy or 'na'}"
    k = 0
    # quotation claims for the sentences behind each component (max 2 per component, one claim per sentence)
    comp_items = {"production": ["D5.4"], "quantified": ["D8.3", "D1.6"], "governance": ["D6.1"],
                  "ownership": ["D1.2", "D4.4"], "specificity": ["D1.3"]}
    picked: dict[str, list[str]] = {}
    for comp in comp_items:
        for s in rubric.evidence.get(comp, [])[:2]:
            if 40 <= len(s) <= 600:
                picked.setdefault(s, []).append(comp)
    for s, comps in picked.items():
        k += 1
        items = sorted({i for c in comps for i in comp_items[c]})
        claims.append(ResearchClaim(id=f"{base}.q{k}", module=MODULE, text=s, kind=ClaimKind.quote, load_bearing=False,
                                    sources=[doc_url], passage=s, tier=tier, confidence_label=label, instrument_items=items,
                                    signal_ids=[f"{base}.rubric"], note="rubric component(s): " + ", ".join(comps)))
    # number claims for disclosed investment figures (D1.4)
    for s in rubric.evidence.get("investment", [])[:3]:
        toks = [t for t in parse_numbers(s) if t.unit and t.unit != "%"]
        if not toks:
            continue
        k += 1
        t = toks[0]
        claims.append(ResearchClaim(id=f"{base}.n{k}", module=MODULE, text=s, kind=ClaimKind.number, load_bearing=False,
                                    sources=[doc_url], passage=s, tier=tier, confidence_label=label, value=t.value, unit=t.unit,
                                    period=str(fy) if fy else None, instrument_items=["D1.4"], signal_ids=[f"{base}.spend"],
                                    note=f"disclosed AI/technology investment figure {t.raw}"))
    competitors = extract_competitors(text, subject.patterns())
    for i, c in enumerate(competitors[:8], 1):
        p = c["passages"][0]
        if 40 <= len(p) <= 600:
            claims.append(ResearchClaim(id=f"{base}.c{i}", module=MODULE, text=p, kind=ClaimKind.quote, load_bearing=False,
                                        sources=[doc_url], passage=p, tier=tier, confidence_label=label,
                                        instrument_items=["peer-seed"], signal_ids=[f"{base}.competitors"],
                                        note=f"names competitor/peer: {c['name']}"))
    leaders = extract_leadership(text)
    for i, l in enumerate(leaders[:8], 1):
        p = l["passages"][0]
        if 40 <= len(p) <= 600:
            claims.append(ResearchClaim(id=f"{base}.l{i}", module=MODULE, text=p, kind=ClaimKind.quote, load_bearing=False,
                                        sources=[doc_url], passage=p, tier=tier, confidence_label=label,
                                        instrument_items=["D1.2", "D2.1", "D5.2"], signal_ids=[f"{base}.leadership"],
                                        note=f"leadership title: {l['title']}" + (f" ({', '.join(l['names'])})" if l["names"] else "")))
    signals = [
        Signal(id=f"{base}.rubric", module=MODULE, name=f"Annual-report AI rubric level ({doc_kind} FY{fy})",
               instrument_items=["D1.1", "D5.4", "D8.3"], value=rubric.level, unit="level 1-5", source=doc_url,
               source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims if f"{base}.rubric" in c.signal_ids],
               detail=rubric.as_dict(), note=rubric.rule + "; corroborates only, never lifts above L3 (instrument §5.4)"),
        Signal(id=f"{base}.density", module=MODULE, name=f"AI mentions per 1,000 words ({doc_kind} FY{fy})",
               instrument_items=["D1.1"], value=rubric.density_per_1000, unit="per 1,000 words", source=doc_url,
               source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               detail={"mentions": rubric.mentions, "words": rubric.words}),
        Signal(id=f"{base}.competitors", module=MODULE, name="Named competitors / peers in the report",
               instrument_items=["peer-seed"], value=len(competitors), unit="names",
               source=doc_url, source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims if f"{base}.competitors" in c.signal_ids],
               detail={"names": [{"name": c["name"], "count": c["count"]} for c in competitors]}),
        Signal(id=f"{base}.leadership", module=MODULE, name="AI / data leadership titles found",
               instrument_items=["D1.2", "D2.1", "D5.2"], value=len(leaders), unit="titles", source=doc_url,
               source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims if f"{base}.leadership" in c.signal_ids],
               detail={"titles": [{"title": l["title"], "names": l["names"], "reports_to": l["reports_to"], "ai_scope": l["ai_scope"]} for l in leaders]},
               note="CAIO/CDO presence is the D1.2 proxy (BCG: future-built 3x CAIO, 2x CDO)"),
    ]
    if rubric.investment_disclosed:
        signals.append(Signal(id=f"{base}.spend", module=MODULE, name="Disclosed AI / technology investment",
                              instrument_items=["D1.4"], value=len(rubric.evidence["investment"]), unit="statements",
                              source=doc_url, source_urls=[doc_url], tier=tier, confidence_label=label,
                              evidence_claim_ids=[c.id for c in claims if f"{base}.spend" in c.signal_ids],
                              detail={"statements": rubric.evidence["investment"][:3]}))
    return {"claims": [c.model_dump(mode="json") for c in claims], "signals": [s.model_dump(mode="json") for s in signals],
            "rubric": rubric.as_dict(), "competitors": competitors, "leadership": leaders, "doc_url": doc_url, "doc_kind": doc_kind, "fy": fy}


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    cp = ctx.checkpoint(MODULE)
    gaps: list[Gap] = []
    docs = [d for d in subject.documents if d.kind in ("annual_report", "results_release", "analyst_deck", "strategy_doc")]
    if not docs:
        gaps.append(Gap(module=MODULE, topic="no documents declared", detail="subject YAML lists no annual report / results documents",
                        instrument_items=["D1.1"]))
    for d in docs:
        if cp.has(d.url):
            continue
        if d.local_file and not (ctx.subject_dir / d.local_file).exists() and not ctx.fixtures and not ctx.has_attachment(d.url):
            cp.put(d.url, {"claims": [], "signals": [], "gap": f"local file missing: data/{subject.slug}/{d.local_file} (download the PDF and place it there, "
                           f"or attach it: plumbresearch ingest <subject.yaml> --file <pdf> --doc {d.document_key})",
                           "doc_url": d.url, "doc_kind": d.kind, "fy": d.fy})
            continue
        src = ctx.fetch(MODULE, d.url)
        if not src.citable or not src.text_extract:
            cp.put(d.url, {"claims": [], "signals": [], "gap": f"document not readable: state={src.state.value} health={src.health_class.value} "
                           f"{src.error or ''} — text extraction {'empty' if src.citable else 'not attempted'}",
                           "doc_url": d.url, "doc_kind": d.kind, "fy": d.fy})
            continue
        cp.put(d.url, _analyse(subject, d.url, d.kind, d.fy, src.text_extract, src.tier))
    claims: list[ResearchClaim] = []
    signals: list[Signal] = []
    detail: dict = {"documents": []}
    for payload in cp.values():
        claims.extend(ResearchClaim.model_validate(c) for c in payload.get("claims", []))
        signals.extend(Signal.model_validate(s) for s in payload.get("signals", []))
        if payload.get("gap"):
            gaps.append(Gap(module=MODULE, topic=f"{payload.get('doc_kind')} FY{payload.get('fy')}", detail=payload["gap"],
                            instrument_items=["D1.1"], verify_flag=True))
        detail["documents"].append({k: payload.get(k) for k in ("doc_url", "doc_kind", "fy", "rubric", "competitors", "leadership", "gap")})
    for d in docs:
        if d.verify:
            gaps.append(Gap(module=MODULE, topic=f"{d.kind} FY{d.fy} URL", detail=f"[VERIFY] {d.url}: {d.note or 'confirm exact URL'}", verify_flag=True))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        data_available=any(s.id.endswith(".rubric") for s in signals), tool_calls=ctx.budget(MODULE).calls, detail=detail)
