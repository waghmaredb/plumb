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
from ..textutil import (ai_mentions, has_any, is_bio_sentence, is_competitor_context, mentions_per_1000, org_names, rubric_sentences,
                        sentences, sentences_paged)

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
    # "operational" means deployment ("the platform is operational"), not "operational efficiency / risk" (run-3 issue 4)
    r"\boperational\b(?!\s+(?:efficienc\w*|excellence|risks?|resilience|costs?|performance|expenses?|effectiveness)\b)",
    r"\bimplemented\b", r"\bembedded in\b", r"\bprocess(?:es|ed|ing) (?:over|more than|\d)",
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


def has_leadership_title(sentence: str, org_aliases: Optional[dict] = None) -> bool:
    """True when the sentence carries a D1.2 proxy title (AI / data / analytics /
    digital scope) held at the subject or a subject subsidiary; used by the
    rubric's ownership component. A title the sentence attributes to another
    organisation (parent or other) does not count."""
    return any(l["ai_scope"] and l["org_role"] in SUBJECT_SIDE
               for l in extract_leadership(sentence, require_scope=True, org_aliases=org_aliases))


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
    fragments_dropped: int = 0  # AI sentence candidates dropped as layout fragments / duplicates (run-3 issue 1)
    bio_sentences: int = 0  # AI sentences in biography context: ownership only (run-3 issue 4)

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["evidence"] = {k: v[:5] for k, v in self.evidence.items()}
        return d


def score_rubric(text: str, org_aliases: Optional[dict] = None) -> RubricScore:
    """Apply the documented rules to extracted text. Deterministic.

    Candidate sentences are the AI sentences minus layout fragments and
    duplicates (``textutil.rubric_sentences``: a pull quote cut at "AI-" is
    not a second production statement). Biography sentences ("Responsible
    for ...", "Over 20 years of experience ...", "With Great Eastern since
    ...") describe a remit, not a system: they count toward ownership only.
    ``org_aliases`` lets the ownership check ignore titles held at another
    organisation (the parent's "Head of the Group Data Office")."""
    n, w, dens = mentions_per_1000(text)
    all_ai = [s for s in sentences(text) if ai_mentions(s)]
    ai_s = rubric_sentences(text)
    ev: dict[str, list[str]] = {k: [] for k in ("specificity", "production", "quantified", "governance", "ownership", "investment",
                                               "bio_ownership_only")}
    pilot_only = 0
    bio_n = 0
    for s in ai_s:
        own = has_any(s, OWNERSHIP) or has_leadership_title(s, org_aliases)
        if is_bio_sentence(s):
            bio_n += 1
            ev["bio_ownership_only"].append(s)
            if own:
                ev["ownership"].append(s)
            continue
        spec = has_any(s, SPECIFICITY)
        prod = has_any(s, PRODUCTION)
        pil = has_any(s, PILOT_ONLY)
        nums = [t for t in parse_numbers(s) if t.unit or t.value >= 10 or "." in t.raw]
        quant = bool(nums) and has_any(s, OUTCOME)
        gov = has_any(s, GOVERNANCE)
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
                       investment_disclosed=inv_b, rule=rule, evidence=ev, fragments_dropped=len(all_ai) - len(ai_s),
                       bio_sentences=bio_n)


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
# Organisation attribution (run-3 issue 2). Every title occurrence is attributed to an
# organisation and an org role:
#   subject              the reporting group itself (Great Eastern Holdings, "the Group")
#   subject-subsidiary   an entity of the subject group (GE Life, GE General, Great Eastern Takaful, GELM)
#   parent               the controlling shareholder's group (OCBC)
#   other                any other organisation (a director's former employer)
# Only subject-side titles count toward the D1.2 signal; parent titles are parent-group context.
SUBJECT_SIDE = ("subject", "subject-subsidiary")
_ROLE_RANK = {"subject": 0, "subject-subsidiary": 1, "parent": 2, "other": 3}
# how the org was decided, strongest first (the strongest basis wins when occurrences merge)
_BASIS_RANK = {"clause": 0, "section": 1, "biography": 2, "holder-moving": 3, "sentence": 4, "document-default": 5}
_SELF_REF = re.compile(r"\b(?:the|our)\s+(?:Group|Company)\b")
_LEGAL_TAIL = re.compile(
    r"(?:\s+(?:(?!The\b|Limited\b|Berhad\b|Ltd\b)[A-Z][\w&’'.-]*|\((?:Malaysia|Singapore|Indonesia|Brunei|Labuan|Hong Kong|China)\)|of|and|&)){0,6}?"
    r"\s+(?:Berhad|Bhd\.?|Limited|Ltd\.?|Pte\.?\s+Ltd\.?|Tbk|PLC|plc|Inc\.?)\b"
)
_LEGAL_END = re.compile(r"\b(?:Berhad|Bhd\.?|Limited|Ltd\.?|Tbk|PLC|plc|Inc\.?)$")
# management-listing pages: titles there belong to the entity / region header above them
MGMT_HEADING = re.compile(r"^(?:Management\s+Team|Senior\s+Management|Key\s+Executives|Key\s+Management(?:\s+Personnel)?|"
                          r"Group\s+Management\s+Committee|Executive\s+Committee|Leadership\s+Team)\b", re.I)
REGION_HEADER = re.compile(r"^(?P<h>GROUP(?:\s+AND\s+[A-Z ]+)?|SINGAPORE|MALAYSIA|INDONESIA|BRUNEI|THAILAND|VIETNAM|CHINA|HONG KONG|"
                           r"PHILIPPINES|REGIONAL|INTERNATIONAL)$")

# Transition status (run-3 issue 3)
_MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
EFFECTIVE = re.compile(rf"\b(?:with effect from|effective(?:\s+from)?|in|on|from|by)\s+(?P<d>(?:\d{{1,2}}\s+)?{_MONTH}\s+\d{{4}}|\d{{4}})\b")
DEPARTED = re.compile(r"\b(?:left\s+(?:the\s+)?(?:Group|Company|Bank|organisation|organization|[A-Z][\w-]+)|has\s+left|(?:has\s+|had\s+)?retired|"
                      r"stepped\s+down|ceased(?!\s+(?:granting|to\s+exist|operations))|resigned|relinquished)\b")
LEAVING = re.compile(r"\b(?:will\s+be\s+leaving|(?:is|are)\s+(?:expected|due|set)\s+to\s+(?:join|leave|retire|step\s+down)|"
                     r"will\s+(?:join|leave|retire|step\s+down|relinquish)|to\s+(?:retire|step\s+down)\s+(?:on|in|with\s+effect|effective))\b")
SUCCESSOR = re.compile(r"\bsuccessors?\b.{0,160}?\b(?:named|announced|appointed|identified)\b.{0,40}?\b(?:in\s+due\s+course|later|shortly|"
                       r"at\s+a\s+later\s+date)\b|\bsuccessors?\b.{0,80}?\b(?:to\s+be|will\s+be|yet\s+to\s+be)\s+(?:named|announced|appointed)\b",
                       re.I | re.S)
JOIN_AS = re.compile(r"\bjoin(?:s|ed|ing)?\s+(?P<org>[^.;]{2,160}?)\s+as\s+(?:the\s+|a\s+|an\s+|its\s+|their\s+)?$")
JOIN_VERB = re.compile(r"\b(?:is|are)\s+(?:expected|due|set)\s+to\s+join\s+(?P<org>[^.;]{2,160}?)(?:\s+as\b|[.;]|$)|\bwill\s+join\s+(?P<org2>[^.;]{2,160}?)(?:\s+as\b|[.;]|$)")
APPOINTED_BEFORE = re.compile(r"\b(?:appointed|promoted|named|redesignated)\s+(?:as\s+)?(?:the\s+|a\s+|an\s+|our\s+|its\s+)?$", re.I)
FORMER = re.compile(r"\b(?:was|had\s+been|previously|formerly|served\s+as|former)\b", re.I)
YEAR_RANGE = re.compile(r"\bfrom\s+(?:\w+\s+)?\d{4}\s+(?:to|until)\s+(?:\w+\s+)?\d{4}\b|\buntil\s+(?:\w+\s+)?\d{4}\b|\buntil\s+(?:his|her)\s+retirement\b")
HON_NAME = re.compile(r"\b(?:Mr|Ms|Mrs|Mdm|Madam|Dr|Dato'?|Datuk|Datin|Puan|Encik)\.?\s+(?P<n>[A-Z][\w’'-]+(?:\s+(?:[A-Z][\w’'-]+|bin|binti|a/l|a/p)){0,4})")
_STATUS_RANK = {"present": 0, "leaving": 1, "incoming": 2, "former": 3, "departed": 4}


class OrgResolver:
    """Org-alias matcher built from the subject YAML ``org_aliases`` (role ->
    aliases). Longest alias first, whole-word, case-sensitive (GEH, OCBC)."""

    def __init__(self, aliases: Optional[dict] = None):
        pairs: list[tuple[str, str]] = []
        for role, lst in (aliases or {}).items():
            role = role.replace("_", "-")
            if role not in _ROLE_RANK:
                continue
            for a in lst or []:
                a = (a or "").strip()
                if a and a not in [p[0] for p in pairs]:
                    pairs.append((a, role))
        pairs.sort(key=lambda p: -len(p[0]))
        self.role_of = dict(pairs)
        self.rx = re.compile("|".join(rf"(?<![\w-]){re.escape(a)}(?![\w-])" for a, _ in pairs)) if pairs else None

    def find(self, text: str) -> list[tuple[int, int, str, str]]:
        """(start, end, display name, role) for every alias hit; the display name is
        expanded to the full legal name when one follows ('Great Eastern General' ->
        'Great Eastern General Insurance (Malaysia) Berhad')."""
        if not self.rx:
            return []
        out = []
        for m in self.rx.finditer(text):
            name = m.group(0)
            tail = None if _LEGAL_END.search(name) else _LEGAL_TAIL.match(text, m.end())
            end = m.end()
            if tail:
                name = re.sub(r"\s+", " ", text[m.start():tail.end()])
                end = tail.end()
            out.append((m.start(), end, name, self.role_of[m.group(0)]))
        return out

    def resolve(self, phrase: str, at_start: bool = False) -> Optional[tuple[str, str]]:
        """(org, role) for an organisation phrase: an alias hit (at the start of the
        phrase when ``at_start``), else a suffix-terminated organisation name ('other')."""
        hits = self.find(phrase)
        if at_start:
            hits = [h for h in hits if h[0] == 0]
        if hits:
            h = min(hits, key=lambda h: (h[0], _ROLE_RANK[h[3]]))
            return h[2], h[3]
        if at_start:
            m = re.match(r"(?:[A-Z][\w&’'.-]*\s+){0,5}?(?:Bank|Banking\s+Corporation|Group|Holdings|Insurance|Assurance|Berhad|Limited|Ltd|"
                         r"Corporation|Company|Capital|Securities|Takaful|Bhd|plc|PLC|Inc)\b(?:\s+(?:Limited|Ltd|Berhad|Bhd|Pte\.?\s+Ltd))?", phrase)
            if m and len(m.group(0).split()) >= 2:
                return m.group(0), "other"
            return None
        names = org_names(phrase)
        if names:
            return names[0], "other"
        acr = re.search(r"\b[A-Z]{3,6}\b", phrase)
        return (acr.group(0), "other") if acr else None


def _effective(sent: str, start: int = 0) -> Optional[str]:
    m = EFFECTIVE.search(sent, start)
    return m.group("d") if m else None


def _occurrence_status(sent: str, a: int, joined_org: Optional[tuple[str, str]]) -> tuple[str, Optional[str], Optional[str]]:
    """(status, detail, effective) for one title occurrence at offset ``a``."""
    if joined_org:
        return "incoming", f"joining {joined_org[0]}", _effective(sent, a)
    if APPOINTED_BEFORE.search(sent[:a]):
        return "present", "appointed", _effective(sent, a)
    lv = LEAVING.search(sent)
    if lv:
        jm = JOIN_VERB.search(sent)
        detail = re.sub(r"\s+", " ", lv.group(0))
        if jm:
            detail = f"expected to join {(jm.group('org') or jm.group('org2')).strip()}"
        return "leaving", detail, _effective(sent, lv.end())
    dp = DEPARTED.search(sent)
    if dp:
        return "departed", re.sub(r"\s+", " ", dp.group(0)), _effective(sent, dp.end())
    if FORMER.search(sent[:a]) and YEAR_RANGE.search(sent):
        return "former", "former role (biography)", None
    return "present", None, None


def _names_in(sent: str) -> list[str]:
    out = []
    for m in HON_NAME.finditer(sent):
        toks = m.group("n").split()
        while toks and toks[-1].lower() in NAME_STOP:
            toks.pop()
        if len(toks) >= 2:
            out.append(" ".join(toks))
    return out


def _same_person(a: str, b: str) -> bool:
    ta, tb = set(a.lower().split()), set(b.lower().split())
    return bool(ta) and bool(tb) and (ta <= tb or tb <= ta)


def extract_leadership(text: str, require_scope: bool = False, org_aliases: Optional[dict] = None) -> list[dict]:
    """Senior titles with Data / Analytics / AI / Digital / Machine Learning scope
    (D1.2 proxies), plus C-level technology titles (class 'other') for context.

    Returns one entry per distinct (title, organisation side): ``title``,
    ``names`` (name-above-title and name-before-title layouts, and
    name-after-title when a separator introduces it), ``role_class``
    (CAIO-equivalent / CDO-equivalent / CDigO / other), ``ai_scope``,
    ``context`` (the first sentence), ``page``, ``reports_to``, up to three
    passages with their pages, and

    - ``org`` / ``org_role`` / ``org_basis``: who the title belongs to
      (subject | subject-subsidiary | parent | other) and why (clause "join X
      as" / "of X", management-listing section header, biography "With X
      since", holder moving to another org, sentence naming the subject, or the
      document default: the subject's own report);
    - ``status`` (present | leaving | incoming | former | departed),
      ``status_detail``, ``effective``: "left the Group", "will be leaving",
      "expected to join <org>", "successor to be named in due course" ...,
      propagated by holder name across the document;
    - ``seat_in_transition`` (a subject seat whose holder is leaving) and
      ``counts_d12`` (subject-side proxy whose holder is not departed/former).

    ``require_scope=True`` drops the 'other' class. ``org_aliases`` is the subject
    YAML ``org_aliases`` map (subject / subject_subsidiary / parent -> aliases)."""
    resolver = OrgResolver(org_aliases)
    out: dict[tuple[str, str], dict] = {}
    occurrences: list[tuple[dict, dict]] = []  # (entry, occurrence)

    def add(title: str, name: Optional[str], sent: str, page: Optional[int], org: tuple[str, str, str],
            status: tuple[str, Optional[str], Optional[str]]) -> None:
        title = re.sub(r"\s+", " ", title).strip(" ,;:")
        if not title:
            return
        role_class = classify_title(title)
        if require_scope and role_class == "other":
            return
        org_name, org_role, basis = org
        side = "subject" if org_role in SUBJECT_SIDE else f"{org_role}:{org_name.lower()}"
        key = (_title_key(title), side)
        e = out.get(key)
        if e is None:
            e = out[key] = {"title": title, "names": [], "role_class": role_class, "ai_scope": role_class != "other",
                            "reports_to": None, "context": sent, "page": page, "passages": [], "pages": [],
                            "org": org_name, "org_role": org_role, "org_basis": basis}
        elif _BASIS_RANK[basis] < _BASIS_RANK[e["org_basis"]]:
            e.update(org=org_name, org_role=org_role, org_basis=basis)
        if name and name not in e["names"]:
            e["names"].append(name)
        rt = REPORTS_TO.search(sent)
        if rt and not e["reports_to"]:
            e["reports_to"] = rt.group("to")
        if len(e["passages"]) < 3 and sent not in e["passages"]:
            e["passages"].append(sent)
            e["pages"].append(page)
        occurrences.append((e, {"name": name, "status": status[0], "detail": status[1], "effective": status[2], "page": page}))

    subj_default = next((a for a, r in resolver.role_of.items() if r == "subject"), "subject")

    def attribute(sent: str, a: int, b: int, listing: bool, state: Optional[tuple[str, str]], nxt: str
                  ) -> tuple[tuple[str, str, str], Optional[tuple[str, str]]]:
        """((org, role, basis), joined_org) for a title spanning sent[a:b]."""
        jm = JOIN_AS.search(sent[:a])
        if jm:
            r = resolver.resolve(jm.group("org")) or (re.sub(r"\s*\(.*$", "", jm.group("org")).strip(), "other")
            return (r[0], r[1], "clause"), r
        post = re.match(r"\s*,?\s*(?P<prep>of|at|with|in|for)\s+(?:the\s+)?", sent[b:])
        if post:
            r = resolver.resolve(sent[b + post.end():], at_start=True)
            if r:
                return (r[0], r[1], "clause"), None
        elif not listing:
            adj = re.match(r"\s*,?\s*", sent[b:])
            hits = [h for h in resolver.find(sent[b + adj.end():]) if h[0] == 0]
            if hits:
                return (hits[0][2], hits[0][3], "clause"), None
        if listing:
            before = [h for h in resolver.find(sent[:a])]
            if before:
                h = before[-1]
                return (h[2], h[3], "section"), None
            if state:
                return (state[0], state[1], "section"), None
        bio = re.match(r"\s*With\s+(?P<org>.{2,80}?)\s+since\b", nxt or "")
        if bio:
            r = resolver.resolve(bio.group("org"))
            if r:
                return (r[0], r[1], "biography"), None
        jv = JOIN_VERB.search(sent)
        if jv and jv.start() >= b:
            r = resolver.resolve((jv.group("org") or jv.group("org2")))
            if r and r[1] not in SUBJECT_SIDE:
                return (subj_default, "subject", "holder-moving"), None
        hits = resolver.find(sent)
        if any(h[3] in SUBJECT_SIDE for h in hits) or _SELF_REF.search(sent):
            h = next((h for h in hits if h[3] in SUBJECT_SIDE), None)
            return ((h[2], h[3]) if h else (subj_default, "subject")) + ("sentence",), None
        if FORMER.search(sent[:a]):
            r = resolver.resolve(sent)
            if r and r[1] not in SUBJECT_SIDE:
                return (r[0], r[1], "sentence"), None
        return (subj_default, "subject", "document-default"), None

    # page by page, so management-listing section headers carry to the titles below them
    pages: dict[Optional[int], list[str]] = {}
    for sent, page in sentences_paged(text):
        pages.setdefault(page, []).append(sent)
    name_status: list[tuple[str, str, str, Optional[str]]] = []  # (name, status, detail, effective)
    for page, sents in pages.items():
        listing = False
        state: Optional[tuple[str, str]] = None
        for idx, sent in enumerate(sents):
            nxt = sents[idx + 1] if idx + 1 < len(sents) else ""
            if MGMT_HEADING.match(sent) and len(sent.split()) <= 6:
                listing = True
            rh = REGION_HEADER.match(sent.strip())
            if rh:
                listing = True
                h = rh.group("h")
                state = (subj_default, "subject") if h.startswith("GROUP") else (f"{subj_default} ({h.title()})", "subject-subsidiary")
            # names whose holders leave / left, for propagation to their titles elsewhere in the report
            lv, dp, sc = LEAVING.search(sent), DEPARTED.search(sent), SUCCESSOR.search(sent)
            if lv or dp or sc:
                st = "leaving" if (lv or sc) else "departed"
                if sc and not lv and not dp:
                    det = "successor to be named in due course"
                else:
                    det = _occurrence_status(sent, len(sent), None)[1] or ""
                    if sc:
                        det += "; successor to be named in due course"
                for nm in _names_in(sent):
                    name_status.append((nm, st, det, _effective(sent)))
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
                org, joined = attribute(sent, m.start(), m.end(), listing, state, nxt)
                add(m.group("title"), name, sent, page, org, _occurrence_status(sent, m.start(), joined))
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
                org, joined = attribute(sent, rm.start(), end, listing, state, nxt)
                add(title, name, sent, page, org, _occurrence_status(sent, rm.start(), joined))
            # acronyms with a role word in the sentence
            for m in LEADERSHIP_ACRONYMS.finditer(sent):
                if any(a <= m.start() < b for a, b in spans):
                    continue
                if not re.search(r"\b(officer|chief|appointed|role|our|the|as)\b", sent, re.I):
                    continue
                org, joined = attribute(sent, m.start(), m.end(), listing, state, nxt)
                add(m.group("title"), None, sent, page, org, _occurrence_status(sent, m.start(), joined))
            # an entity line on a listing page sets the section org for the titles that follow
            if listing:
                hits = resolver.find(sent)
                if hits:
                    header_line = len(sent.split()) <= 30 and not LEADERSHIP_RANK.search(sent) and not re.search(r"\b(?:Officer|Actuary|Secretary|Auditor)\b", sent)
                    # an entity header naming several group companies ("GEH / GE Life / GE General") -> the holding company;
                    # inside a listing line, the last entity named is the one the following people belong to
                    h = min(hits, key=lambda h: _ROLE_RANK[h[3]]) if header_line else hits[-1]
                    state = (h[2], h[3])

    # propagate holder status by name, then roll occurrences up into entry status
    for e, occ in occurrences:
        if occ["name"] and occ["status"] == "present":
            for nm, st, det, eff in name_status:
                if _same_person(nm, occ["name"]):
                    occ.update(status=st, detail=det, effective=eff)
                    break
        elif occ["name"] and occ["status"] in ("leaving", "departed"):
            for nm, st, det, eff in name_status:
                if _same_person(nm, occ["name"]) and det and "successor" in det and "successor" not in (occ["detail"] or ""):
                    occ["detail"] = f"{occ['detail']}; successor to be named in due course" if occ["detail"] else det
    by_entry: dict[int, list[dict]] = {}
    for e, occ in occurrences:
        by_entry.setdefault(id(e), []).append(occ)
    for e in out.values():
        occs = by_entry.get(id(e), [])
        named = [o for o in occs if o["name"]] or occs
        best = min(named, key=lambda o: (_STATUS_RANK[o["status"]], o["detail"] is None)) if named else \
            {"status": "present", "detail": None, "effective": None}
        # among occurrences with the winning status, prefer the one that says the most
        same = [o for o in named if o["status"] == best["status"]]
        rich = max(same, key=lambda o: len(o["detail"] or "")) if same else best
        e["status"] = best["status"]
        e["status_detail"] = rich["detail"]
        e["effective"] = rich["effective"] or next((o["effective"] for o in same if o["effective"]), None)
        e["seat_in_transition"] = e["org_role"] in SUBJECT_SIDE and e["status"] == "leaving"
        e["counts_d12"] = bool(e["ai_scope"] and e["org_role"] in SUBJECT_SIDE and e["status"] in ("present", "leaving", "incoming"))
    return list(out.values())


# --------------------------------------------------------------------------
# Module entry point
# --------------------------------------------------------------------------
def subject_org_aliases(subject: Subject) -> dict[str, list[str]]:
    """Organisation aliases for leadership attribution: the subject YAML
    ``org_aliases`` (subject / subject_subsidiary / parent -> names). When the
    Subject model does not carry the field, it is read from the built-in YAML
    for the slug. The subject's own name patterns are added as ``subject``
    aliases unless the YAML already assigns them a role."""
    raw = getattr(subject, "org_aliases", None)
    if not raw:
        try:
            import yaml
            from ..subject import builtin_subject_path
            path = builtin_subject_path(subject.slug)
            if path.exists():
                raw = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("org_aliases")
        except Exception:  # pragma: no cover - a missing or unreadable YAML just means no aliases
            raw = None
    out: dict[str, list[str]] = {}
    for role, lst in (raw or {}).items():
        out.setdefault(str(role).replace("-", "_"), []).extend(str(a) for a in (lst or []) if a)
    known = {a for lst in out.values() for a in lst}
    subj = out.setdefault("subject", [])
    for a in [subject.name, *subject.patterns()]:
        if a and a not in known and a not in subj:
            subj.append(a)
    return out


_STATUS_EVIDENCE = re.compile(LEAVING.pattern + "|" + DEPARTED.pattern + r"|\bjoin(?:s|ed|ing)?\b")


def _leader_passage(l: dict) -> str:
    """The passage that proves the entry: for a holder who is leaving or has left,
    the sentence that says so; otherwise the first passage. A listing line that
    runs past 600 characters (a whole management column joined) is cut to the
    "<name> <title>" span, which is still an exact substring of the document."""
    p = l["passages"][0]
    if l["status"] != "present":
        p = next((x for x in l["passages"] if _STATUS_EVIDENCE.search(x)), p)
    if len(p) > 600:
        words = [re.escape(w) for w in l["title"].split()]
        rx = r"\s+".join(words)
        for nm in l["names"]:
            m = re.search(r"\s+".join(re.escape(w) for w in nm.split()) + r"\W{0,3}\s*" + rx, p, re.I)
            if m:
                return m.group(0)
        m = re.search(rx, p)
        if m:
            return p[max(0, m.start() - 60):m.end()].split(" ", 1)[-1] if m.start() > 60 else p[:m.end()]
    return p


def _leader_label(l: dict) -> str:
    who = f" ({', '.join(l['names'])})" if l["names"] else ""
    st = l["status"] + (f": {l['status_detail']}" if l.get("status_detail") else "") + (f", {l['effective']}" if l.get("effective") else "")
    return f"{l['title']} [{l['role_class']}]{who} @ {l['org']} ({l['org_role']}, {l['org_basis']}); {st}"


def _analyse(subject: Subject, doc_url: str, doc_kind: str, fy: Optional[int], text: str, tier) -> dict:
    aliases = subject_org_aliases(subject)
    rubric = score_rubric(text, aliases)
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
    leaders = extract_leadership(text, org_aliases=aliases)
    proxies = [l for l in leaders if l["ai_scope"]]
    counted = [l for l in proxies if l["counts_d12"]]
    present = [l for l in counted if not l["seat_in_transition"]]
    transition = [l for l in counted if l["seat_in_transition"]]
    departed = [l for l in proxies if l["org_role"] in SUBJECT_SIDE and not l["counts_d12"]]
    parent_ctx = [l for l in proxies if l["org_role"] == "parent"]
    other_org = [l for l in proxies if l["org_role"] == "other"]
    ordered = present + transition + departed + parent_ctx + other_org + [l for l in leaders if not l["ai_scope"]]
    li = 0
    for l in ordered[:8]:
        p = _leader_passage(l)
        if 40 <= len(p) <= 600:
            sid = f"{base}.leadership_parent" if l["org_role"] == "parent" and l["ai_scope"] else f"{base}.leadership"
            same = next((c for c in claims if c.passage == p and c.id.startswith(f"{base}.l")), None)
            if same:  # one sentence proving two titles (the leaver's title and the parent role she moves to): one claim
                if sid not in same.signal_ids:
                    same.signal_ids.append(sid)
                same.note = f"{same.note}; also {_leader_label(l)}"
                continue
            li += 1
            claims.append(ResearchClaim(id=f"{base}.l{li}", module=MODULE, text=p, kind=ClaimKind.quote, load_bearing=False,
                                        sources=[doc_url], passage=p, tier=tier, confidence_label=label,
                                        instrument_items=["D1.2", "D2.1", "D5.2"], signal_ids=[sid],
                                        note="leadership title: " + _leader_label(l)))

    def brief(ls: list[dict]) -> str:
        return "; ".join(f"{l['title']}" + (f" ({', '.join(l['names'])})" if l["names"] else "") +
                         (f" [{l['status_detail']}{', ' + l['effective'] if l.get('effective') else ''}]" if l["status"] != "present" and l.get("status_detail") else "")
                         for l in ls)

    lead_note = (f"value counts D1.2 proxy titles (AI / data / analytics / digital scope) held at the subject or a subject subsidiary and "
                 f"not vacated: {len(present)} present" + (f" ({brief(present)})" if present else "") +
                 f", {len(transition)} seat(s) in transition" + (f" ({brief(transition)})" if transition else "") +
                 f". Not counted: {len(departed)} departed/former" + (f" ({brief(departed)})" if departed else "") +
                 f"; {len(parent_ctx)} parent-group title(s), reported as parent-group context" + (f" ({brief(parent_ctx)})" if parent_ctx else "") +
                 (f"; {len(other_org)} at other organisations" if other_org else "") +
                 "; CTO/CIO-type titles are listed as 'other'. CAIO/CDO presence is the D1.2 proxy (BCG: future-built 3x CAIO, 2x CDO)")
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
        Signal(id=f"{base}.leadership", module=MODULE, name="AI / data leadership titles found (subject, present or in transition)",
               instrument_items=["D1.2", "D2.1", "D5.2"], value=len(counted), unit="titles", source=doc_url,
               source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims if f"{base}.leadership" in c.signal_ids],
               detail={"titles": [{"title": l["title"], "names": l["names"], "role_class": l["role_class"], "reports_to": l["reports_to"],
                                   "ai_scope": l["ai_scope"], "context": l["context"], "page": l["page"], "pages": l["pages"],
                                   "org": l["org"], "org_role": l["org_role"], "org_basis": l["org_basis"], "status": l["status"],
                                   "status_detail": l["status_detail"], "effective": l["effective"],
                                   "seat_in_transition": l["seat_in_transition"], "counts_d12": l["counts_d12"]} for l in leaders],
                       "classes": {k: sum(1 for l in counted if l["role_class"] == k) for k in ("CAIO-equivalent", "CDO-equivalent", "CDigO")},
                       "present": len(present), "in_transition": len(transition), "departed_or_former": len(departed),
                       "parent_context": len(parent_ctx), "other_org": len(other_org),
                       "other_titles": len(leaders) - len(proxies)},
               note=lead_note),
    ]
    if parent_ctx:
        signals.append(Signal(id=f"{base}.leadership_parent", module=MODULE, name="Parent-group AI / data titles (context, not counted for D1.2)",
                   instrument_items=["D1.2-context"], value=len(parent_ctx), unit="titles", source=doc_url,
                   source_urls=[doc_url], tier=tier, confidence_label=ConfidenceLabel.model_inferred,
                   evidence_claim_ids=[c.id for c in claims if f"{base}.leadership_parent" in c.signal_ids],
                   detail={"titles": [{"title": l["title"], "names": l["names"], "org": l["org"], "status": l["status"],
                                       "status_detail": l["status_detail"], "effective": l["effective"], "page": l["page"]} for l in parent_ctx]},
                   note="titles the report attributes to the parent group (e.g. a subject executive moving to the parent); parent-group "
                        "context only, never subject D1.2 evidence"))
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
