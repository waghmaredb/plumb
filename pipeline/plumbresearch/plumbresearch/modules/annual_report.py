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
    ownership     AI sentences naming board or C-level accountability (CAIO/CDO or any senior title with
                  AI / data / analytics / digital scope, board committee, targets)

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
from ..textutil import ai_sentences, has_any, is_competitor_context, mentions_per_1000, org_names, sentences, sentences_paged

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

# --------------------------------------------------------------------------
# Leadership lexicon (instrument D1.2 / D2.1 / D5.2 proxies)
# --------------------------------------------------------------------------
# A D1.2 proxy is any senior title (C-level, Managing Director, Head, Director, VP ...) whose text
# names Data, Analytics, AI / Artificial Intelligence, Digital or Machine Learning. Two title shapes:
#   form A  "Chief <scope> Officer"          scope sits between Chief and Officer
#   form B  "<rank>[,| of| for| -] <scope>"  Managing Director, Group Data and AI / Head of Data Science
# Acronyms (CAIO, CDO, CDAO, CTO, CIO) only count with a role word in the sentence, as before.
# "AI" must be upper case: "Ai" is a common syllable in Chinese and Malay names (Chew Ai Ling), which sit next to
# titles in management listings; the spelt-out forms are matched case-insensitively.
SCOPE_KEYWORDS = re.compile(
    r"\b(?:AI|A\.I\.|GenAI)\b|(?i:\b(?:Artificial\s+Intelligence|Data|Analytics|Digital|Digitalisation|Digitalization|"
    r"Machine\s+Learning|Generative\s+AI|Data\s+Science)\b)"
)
_RANK = (
    r"(?:Group\s+|Regional\s+|Global\s+)?(?:Managing\s+Director|Executive\s+Director|Deputy\s+Managing\s+Director|"
    r"(?:(?:Senior|Executive|Assistant|Associate|Deputy|Group)\s+)?Vice[\s-]President|SVP|EVP|AVP|VP|General\s+Manager|"
    r"Deputy\s+General\s+Manager|Division\s+Head|Head|Director|Lead|Leader|President)"
)
_SCOPE_WORD = r"(?:[A-Z][\w’'&./-]*|AI|&|and|of|for|the|\d+)"
LEADERSHIP_FORM_A = re.compile(
    r"(?P<title>(?:Group\s+|Regional\s+|Global\s+|Deputy\s+)?Chief\s+(?P<scope>[A-Z][\w&,’'/ -]{1,60}?)\s+Officer)\b"
)
LEADERSHIP_RANK = re.compile(rf"\b(?P<rank>{_RANK})\b")
LEADERSHIP_SCOPE = re.compile(rf"(?P<sep>\s*[,:\u2013\u2014-]\s*|\s+(?:of|for)\s+|\s+)(?P<scope>(?:{_SCOPE_WORD}\s*,?\s*){{1,8}})")
LEADERSHIP_ACRONYMS = re.compile(r"\b(?P<title>CAIO|CDAO|CDO|CTO|CIO|CDIO)\b")
# where a scope phrase may end: the last word must carry the scope, so trailing name / prose words are trimmed
SCOPE_TAIL = re.compile(
    r"\b(?:AI|A\.I\.|Intelligence|Data|Analytics|Digital|Digitalisation|Digitalization|Learning|Science|GenAI|Office|"
    r"Technology|Innovation|Transformation|Strategy|Platforms?|Engineering|Insights?|Governance|Architecture|Products?|"
    r"Solutions?|Experience|Operations|Information|Systems?|Automation|Excellence|Services?|Officer|Business|Banking|"
    r"Insurance|Marketing|Wealth|Investments?|Finance|Risk|Compliance|Capital|Agency|Affinity|Propositions|Advisory|"
    r"Channels?|Centre|Center|Hub|Labs?|Factory|Programmes?|Programs?|Initiatives?|Enablement|Partnerships?|Ecosystems?|"
    r"Assets?|Management|Offices?|Division|Unit|Function|Team|Analysis|Modelling|Modeling|Research|Intelligence)\b",
    re.I,
)
REPORTS_TO = re.compile(r"report(?:s|ing)?\s+(?:directly\s+)?to\s+the\s+(?P<to>(?:Group\s+)?(?:CEO|Chief Executive(?: Officer)?|COO|Board|President|Managing Director))", re.I)
HONORIFICS = {"mr", "ms", "mrs", "mdm", "madam", "dr", "prof", "professor", "dato", "dato'", "datuk", "datin", "puan", "encik",
              "ir", "sir", "dame", "tan sri", "dato sri", "dato' sri", "datuk seri", "dato seri"}
NAME_CONNECTORS = {"bin", "binti", "bte", "binte", "al", "de", "van", "der", "da", "di", "du", "la", "le", "a/l", "a/p", "s/o", "d/o"}
# words that end a name walk (title vocabulary and ordinary sentence words that happen to be capitalised)
NAME_STOP = {
    "chief", "officer", "head", "director", "managing", "executive", "group", "regional", "global", "deputy", "senior",
    "vice", "president", "general", "manager", "division", "lead", "leader", "data", "digital", "analytics",
    "artificial", "intelligence", "technology", "information", "operations", "insurance", "assurance", "bank", "limited",
    "officer,", "with", "since", "joined", "appointed", "responsible", "leads", "oversees", "prior", "before", "previously",
    "is", "was", "has", "he", "she", "they", "our", "the", "a", "an", "in", "on", "at", "for", "of", "and", "to", "as",
    "who", "new", "its", "his", "her", "their", "mr", "ms", "mrs", "dr", "board", "committee", "company", "annual",
    "report", "page", "note", "notes", "management", "team", "key", "senior", "principal", "subsidiaries", "singapore",
    "malaysia", "indonesia", "brunei", "china", "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "years", "year", "experience", "over", "more", "than", "from",
}


def _name_token_ok(tok: str) -> bool:
    t = tok.strip(",.;:()“”\"'")
    if not t:
        return False
    if t.lower() in NAME_CONNECTORS:
        return True
    if t == "AI" or t.upper() in ("GENAI",):
        return False  # the scope word, not the syllable in a name (Chew Ai Ling)
    if t.lower() in NAME_STOP or t.lower().rstrip(",") in NAME_STOP:
        return False
    if re.fullmatch(r"[A-Z]\.", t):
        return True  # initial
    if re.fullmatch(r"[A-Z][a-z’'-]+(?:-[A-Z][a-z’'-]+)?", t):
        return True  # Title case
    if re.fullmatch(r"[A-Z]{2,}(?:-[A-Z]{2,})?", t) and len(t) <= 14:
        return True  # ALL CAPS (name-above-title layouts set names in caps)
    return False


def _normalise_name(tokens: list[str]) -> Optional[str]:
    toks = [t.strip(",.;:()“”\"'") for t in tokens]
    while toks:
        if len(toks) > 1 and f"{toks[0]} {toks[1]}".lower() in HONORIFICS:
            toks = toks[2:]
        elif toks[0].lower().rstrip(".") in HONORIFICS:
            toks = toks[1:]
        else:
            break
    toks = [t for t in toks if t]
    if len(toks) < 2 or len(toks) > 5:
        return None
    if all(t.lower() in NAME_CONNECTORS for t in toks):
        return None
    name = " ".join(toks)
    if name.isupper():  # ZHAO JINGYUAN -> Zhao Jingyuan (keeps the caps form in the context)
        name = " ".join(w.capitalize() if w.lower() not in NAME_CONNECTORS else w.lower() for w in toks)
    return name


def _name_before(prefix: str) -> Optional[str]:
    """Name immediately preceding a title: '... Zhao Jingyuan Managing Director, ...',
    'ZHAO JINGYUAN Managing Director', 'Ms Zhao Jingyuan (Managing Director ...'."""
    pre = prefix.rstrip()
    pre = re.sub(r"[\s(\u2013\u2014,:-]+$", "", pre)  # separators between the name and the title
    # "Priya Nair was appointed <title>", "Tan Wei Ming, our <title>", "X serves as <title>"
    pre = re.sub(r"(?:[\s,]+(?:is|was|as|has|been|appointed|serves?|our|the|new|its|named|promoted|became|joined|current|"
                 r"incumbent|now|also|remains|continues|continued|acting|interim|role|of))+$", "", pre, flags=re.I)
    words = pre.split()
    picked: list[str] = []
    for tok in reversed(words[-7:]):
        if _name_token_ok(tok) and not (picked and re.search(r"[.;:!?]$", tok)):
            picked.insert(0, tok)
            if len(picked) >= 5:
                break
            continue
        break
    # include an honorific immediately before the picked run (dropped by _normalise_name)
    return _normalise_name(picked)


def _name_after(suffix: str) -> Optional[str]:
    """Name following a title when a separator introduces it: 'Head of Data Science, Tan Wei Ming, joined ...'."""
    m = re.match(r"^\s*[,:\u2013\u2014-]\s*(?:(?:Mr|Ms|Mrs|Mdm|Dr)\.?\s+)?", suffix)
    if not m:
        return None
    rest = suffix[m.end():].split()
    picked: list[str] = []
    for tok in rest[:5]:
        if _name_token_ok(tok):
            picked.append(tok)
            if re.search(r"[,.;:)]$", tok):
                break
        else:
            break
    return _normalise_name(picked)


def _trim_scope(scope: str) -> str:
    """Cut a form-B scope at its last scope-bearing word so trailing prose or the
    next listed name is dropped ('Group Data and AI With Great Eastern since 2022' -> 'Group Data and AI')."""
    scope = re.sub(r"\s+", " ", scope).strip(" ,;:-\u2013\u2014")
    words = scope.split(" ")
    last = None
    for i, w in enumerate(words):
        if SCOPE_TAIL.fullmatch(w.strip(",.;:()")):
            last = i
    if last is None:
        return ""
    out = " ".join(words[: last + 1]).strip(" ,;:")
    # a scope must not run into a new rank ("Group Data and AI James Lee Soo Hian Managing Director")
    cut = re.search(r"\s(?:Managing|Executive|Chief|Head|Director|Division)\b", out)
    if cut and SCOPE_KEYWORDS.search(out[: cut.start()]):
        out = out[: cut.start()].strip(" ,;:")
    return out


def has_leadership_title(sentence: str) -> bool:
    """True when the sentence carries a D1.2 proxy title (AI / data / analytics /
    digital scope) in either title form; used by the rubric's ownership component."""
    return any(l["ai_scope"] for l in extract_leadership(sentence, require_scope=True))


def classify_title(title: str) -> str:
    """CAIO-equivalent (AI / Artificial Intelligence / Machine Learning), CDO-equivalent
    (Data / Analytics), CDigO (Digital), else 'other' (CTO / CIO and similar)."""
    if re.search(r"\b(?:AI|A\.I\.|GenAI)\b|(?i:\b(?:Artificial\s+Intelligence|Machine\s+Learning|Generative\s+AI)\b)", title):
        return "CAIO-equivalent"
    if re.search(r"\b(?:Data|Analytics|Data\s+Science)\b", title, re.I):
        return "CDO-equivalent"
    if re.search(r"\b(?:Digital|Digitalisation|Digitalization)\b", title, re.I):
        return "CDigO"
    return "other"


def _title_key(title: str) -> str:
    k = title.lower().replace("&", "and")
    k = re.sub(r"\bartificial intelligence\b", "ai", k)
    k = re.sub(r"\s*,\s*", ", ", k)
    return re.sub(r"\s+", " ", k).strip()


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
        own = has_any(s, OWNERSHIP) or has_leadership_title(s)
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
def extract_competitors(text: str, exclude_patterns: list[str], known_aliases: Optional[list[str]] = None) -> list[dict]:
    """Named competitors / peers: a competitor-context sentence (compared with,
    peers, market share ...) that also carries an organisation hit, either a
    suffix-terminated name (NER-lite in ``textutil.org_names``) or a peer alias
    the subject YAML already lists. A period comparison ("compared with
    FY2025") is not a competitor context, and a bare acronym is not a hit."""
    found: dict[str, dict] = {}
    for s, page in sentences_paged(text):
        if not is_competitor_context(s):
            continue
        for name in org_names(s, exclude_patterns, known_aliases or []):
            e = found.setdefault(name, {"name": name, "count": 0, "passages": [], "pages": []})
            e["count"] += 1
            if len(e["passages"]) < 3:
                e["passages"].append(s)
                e["pages"].append(page)
    return sorted(found.values(), key=lambda e: -e["count"])


def peer_aliases(subject: Subject) -> list[str]:
    """Peer names and name_patterns from the subject YAML, used as known
    organisation aliases by the competitor extractor."""
    out: list[str] = []
    for p in subject.peers:
        for a in [*p.name_patterns, p.entity or "", p.name]:
            a = (a or "").strip()
            if a and a not in out and len(a) >= 3 and "(" not in a and ";" not in a and "," not in a:
                out.append(a)
    return out


# --------------------------------------------------------------------------
# Leadership-structure extraction
# --------------------------------------------------------------------------
def extract_leadership(text: str, require_scope: bool = False) -> list[dict]:
    """Senior titles with Data / Analytics / AI / Digital / Machine Learning scope
    (D1.2 proxies), plus C-level technology titles (class 'other') for context.

    Returns one entry per distinct title: ``title``, ``names`` (name-above-title
    and name-before-title layouts, and name-after-title when a separator
    introduces it), ``role_class`` (CAIO-equivalent / CDO-equivalent / CDigO /
    other), ``ai_scope`` (True for the three proxy classes), ``context`` (the
    first sentence), ``page``, ``reports_to`` and up to three passages with
    their pages. ``require_scope=True`` drops the 'other' class."""
    out: dict[str, dict] = {}

    def add(title: str, name: Optional[str], sent: str, page: Optional[int]) -> None:
        title = re.sub(r"\s+", " ", title).strip(" ,;:")
        if not title:
            return
        role_class = classify_title(title)
        if require_scope and role_class == "other":
            return
        key = _title_key(title)
        e = out.setdefault(key, {"title": title, "names": [], "role_class": role_class, "ai_scope": role_class != "other",
                                 "reports_to": None, "context": sent, "page": page, "passages": [], "pages": []})
        if name and name not in e["names"]:
            e["names"].append(name)
        rt = REPORTS_TO.search(sent)
        if rt and not e["reports_to"]:
            e["reports_to"] = rt.group("to")
        if len(e["passages"]) < 3 and sent not in e["passages"]:
            e["passages"].append(sent)
            e["pages"].append(page)

    for sent, page in sentences_paged(text):
        spans: list[tuple[int, int]] = []
        # form A: Chief <scope> Officer
        for m in LEADERSHIP_FORM_A.finditer(sent):
            scope = m.group("scope")
            if len(scope.split()) > 6:
                continue
            tech = re.search(r"\b(?:Technology|Information|Transformation|Innovation|Operating\s+and\s+Technology)\b", scope, re.I)
            if not SCOPE_KEYWORDS.search(scope) and not tech:
                continue
            name = _name_before(sent[: m.start()]) or _name_after(sent[m.end():])
            add(m.group("title"), name, sent, page)
            spans.append(m.span())
        # form B: <rank>[, | of | for] <scope>; ranks are located first so one long listing line
        # ("... Managing Director, Group Information Technology Zhao Jingyuan Managing Director, Group Data and AI ...")
        # yields every title, each with the name that precedes it
        for rm in LEADERSHIP_RANK.finditer(sent):
            if any(a <= rm.start() < b for a, b in spans):
                continue
            if rm.start() > 0 and re.match(r"[\w-]", sent[rm.start() - 1]):
                continue
            sm = LEADERSHIP_SCOPE.match(sent, rm.end())
            if not sm:
                continue
            scope = _trim_scope(sm.group("scope"))
            if not scope or not SCOPE_KEYWORDS.search(scope):
                continue
            rank = re.sub(r"\s+", " ", rm.group("rank"))
            sep = sm.group("sep")
            sep = "," if "," in sep else (" of" if re.search(r"\bof\b", sep) else (" for" if re.search(r"\bfor\b", sep) else ""))
            title = f"{rank}{sep} {scope}".replace(" ,", ",")
            end_m = re.compile(r"\s+".join(re.escape(w) for w in scope.split())).match(sent, sm.start("scope"))
            end = end_m.end() if end_m else sm.end()
            name = _name_before(sent[: rm.start()]) or _name_after(sent[end:])
            add(title, name, sent, page)
        # acronyms with a role word in the sentence
        for m in LEADERSHIP_ACRONYMS.finditer(sent):
            if any(a <= m.start() < b for a, b in spans):
                continue
            if not re.search(r"\b(officer|chief|appointed|role|our|the|as)\b", sent, re.I):
                continue
            add(m.group("title"), None, sent, page)
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
    competitors = extract_competitors(text, subject.patterns(), peer_aliases(subject))
    for i, c in enumerate(competitors[:8], 1):
        p = c["passages"][0]
        if 40 <= len(p) <= 600:
            claims.append(ResearchClaim(id=f"{base}.c{i}", module=MODULE, text=p, kind=ClaimKind.quote, load_bearing=False,
                                        sources=[doc_url], passage=p, tier=tier, confidence_label=label,
                                        instrument_items=["peer-seed"], signal_ids=[f"{base}.competitors"],
                                        note=f"names competitor/peer: {c['name']}"))
    leaders = extract_leadership(text)
    proxies = [l for l in leaders if l["ai_scope"]]
    for i, l in enumerate((proxies + [l for l in leaders if not l["ai_scope"]])[:8], 1):
        p = l["passages"][0]
        if 40 <= len(p) <= 600:
            claims.append(ResearchClaim(id=f"{base}.l{i}", module=MODULE, text=p, kind=ClaimKind.quote, load_bearing=False,
                                        sources=[doc_url], passage=p, tier=tier, confidence_label=label,
                                        instrument_items=["D1.2", "D2.1", "D5.2"], signal_ids=[f"{base}.leadership"],
                                        note=f"leadership title: {l['title']} [{l['role_class']}]" + (f" ({', '.join(l['names'])})" if l["names"] else "")))
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
               instrument_items=["D1.2", "D2.1", "D5.2"], value=len(proxies), unit="titles", source=doc_url,
               source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims if f"{base}.leadership" in c.signal_ids],
               detail={"titles": [{"title": l["title"], "names": l["names"], "role_class": l["role_class"], "reports_to": l["reports_to"],
                                   "ai_scope": l["ai_scope"], "context": l["context"], "page": l["page"]} for l in leaders],
                       "classes": {k: sum(1 for l in proxies if l["role_class"] == k) for k in ("CAIO-equivalent", "CDO-equivalent", "CDigO")},
                       "other_titles": len(leaders) - len(proxies)},
               note="value counts D1.2 proxy titles (AI / data / analytics / digital scope); CTO/CIO-type titles are listed as 'other' "
                    "and not counted. CAIO/CDO presence is the D1.2 proxy (BCG: future-built 3x CAIO, 2x CDO)"),
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
