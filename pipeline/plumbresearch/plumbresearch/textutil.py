"""Shared text helpers: AI-term lexicon, sentence splitting, word counts,
NER-lite for organisation names. Pure functions, no network."""
from __future__ import annotations

import re
from typing import Iterable, Optional

try:
    from plumbverify.extract import PAGE_SEP
except ImportError:  # pragma: no cover
    PAGE_SEP = "\f"

# AI mention lexicon used by the annual-report rubric and the call-density
# module. Word-boundary matched, case-insensitive except the bare acronyms,
# which must be upper-case to avoid "ai" inside words.
AI_TERMS_CI = [
    r"artificial intelligence", r"machine[- ]learning", r"deep[- ]learning", r"generative ai", r"gen[- ]?ai",
    r"large language models?", r"natural language processing", r"computer vision", r"neural networks?",
    r"predictive (?:analytics|models?|modelling)", r"agentic", r"ai[- ]agents?", r"ai[- ](?:powered|enabled|driven|based|assisted|first)",
    r"responsible ai", r"ai governance", r"copilot", r"chatbots?", r"conversational ai", r"robo[- ]advis(?:or|ory)",
    r"foundation models?", r"retrieval[- ]augmented", r"\brag\b", r"mlops", r"llmops", r"data science",
]
AI_TERMS_CS = [r"\bAI\b", r"\bML\b", r"\bLLMs?\b", r"\bGenAI\b", r"\bNLP\b"]

AI_RE = re.compile("|".join(f"(?:{t})" for t in AI_TERMS_CI), re.I)
AI_RE_CS = re.compile("|".join(f"(?:{t})" for t in AI_TERMS_CS))

_WORD = re.compile(r"\b[\w'-]+\b")
_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")


def word_count(text: str) -> int:
    return len(_WORD.findall(text or ""))


def ai_mentions(text: str) -> list[re.Match]:
    out = list(AI_RE.finditer(text or ""))
    out.extend(AI_RE_CS.finditer(text or ""))
    out.sort(key=lambda m: m.start())
    # de-duplicate overlapping matches (e.g. "AI-powered" matched by both regexes)
    dedup: list[re.Match] = []
    last_end = -1
    for m in out:
        if m.start() >= last_end:
            dedup.append(m)
            last_end = m.end()
    return dedup


def mentions_per_1000(text: str) -> tuple[int, int, float]:
    n = len(ai_mentions(text))
    w = word_count(text)
    return n, w, (n / w * 1000.0) if w else 0.0


def sentences(text: str) -> list[str]:
    """Sentence-ish units. Each unit is an exact substring of the (whitespace
    normalised) input so quotations lifted from it exact-match under C5."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", text or ""):
        # hard-wrapped lines (PDF extraction) belong to the same sentence: join with a space.
        # Whitespace-normalised matching (C5) treats "\n" and " " alike, so quotes still exact-match.
        para = re.sub(r"\s*\n\s*", " ", para).strip()
        if not para:
            continue
        for s in _SENT.split(para):
            s = s.strip()
            if s:
                out.append(s)
    return out


def sentences_paged(text: str) -> list[tuple[str, Optional[int]]]:
    """Like :func:`sentences` but keeps the page each sentence came from.
    Pages are the PAGE_SEP-joined extract plumbverify produces for PDFs; a
    text without separators yields ``page=None``."""
    if PAGE_SEP not in (text or ""):
        return [(s, None) for s in sentences(text)]
    out: list[tuple[str, Optional[int]]] = []
    for i, page in enumerate(text.split(PAGE_SEP), start=1):
        out.extend((s, i) for s in sentences(page))
    return out


def ai_sentences(text: str) -> list[str]:
    return [s for s in sentences(text) if ai_mentions(s)]


def has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def count_any(text: str, patterns: Iterable[str]) -> int:
    return sum(len(re.findall(p, text, re.I)) for p in patterns)


# --------------------------------------------------------------------------
# NER-lite: organisation names in a sentence
# --------------------------------------------------------------------------
# An organisation hit is a capitalised multi-word run that ENDS in a corporate suffix. Bare
# acronyms (DBS, NEA, MOH) are not hits on their own: in an annual report they are as often
# regulators, ministries and products as peers, which is how "compared with ... NEA" produced a
# false competitor. A peer the subject YAML already knows (name or name_patterns) is matched by
# alias instead, so "AIA" or "Prudential" still count when the YAML lists them.
_ORG_SUFFIX = (
    r"(?:Bank|Banking|Berhad|Bhd\.?|Group|Holdings|Financial|Finance|Insurance|Assurance|Life|Capital|Corporation|Corp\.?|"
    r"Company|Co\.?|Limited|Ltd\.?|Plc|plc|PLC|Inc\.?|Trust|Securities|Asset Management|Takaful|Reinsurance|Re|Insurers?)"
)
_ORG_GEO = r"(?:Singapore|Malaysia|Indonesia|Brunei|Thailand|Vietnam|Cambodia|Myanmar|Philippines|Asia|Hong Kong|China|Japan|Australia)"
_ORG_LEGAL = r"(?:Pte\.?|Sdn\.?|Private|Public)?\s*(?:Ltd\.?|Limited|Bhd\.?|Berhad|Inc\.?|Plc|plc|PLC)"
_ORG_WORD = r"[A-Z][A-Za-z&'’.-]+"
_ORG_RE = re.compile(
    rf"\b((?:(?:{_ORG_WORD}|\({_ORG_GEO}\))(?:\s+(?:of|de|the|&|and)\s+)?\s+){{1,5}}{_ORG_SUFFIX}\b(?:\s+{_ORG_SUFFIX}\b)*"
    rf"(?:\s+\(?{_ORG_GEO}\)?)?(?:\s+{_ORG_LEGAL}\b)?)"
)
_NOT_ORG = {
    "The", "Our", "We", "In", "On", "At", "For", "This", "These", "Group", "Bank", "Board", "Company", "Annual", "Report",
    "Holdings", "Life", "Insurance", "Financial", "Finance", "Capital", "Limited", "Ltd", "Trust", "Banking",
    "AI", "ML", "LLM", "NLP", "ESG", "CEO", "CFO", "CTO", "CIO", "CDO", "CAIO", "COO", "CRO", "KPI", "KPIS", "ROE", "ROA",
    "USD", "SGD", "MYR", "RM", "FY", "ASEAN", "GDP", "IT", "API", "APIS", "PBT", "NPAT", "YOY", "QOQ", "IFRS", "SFRS",
    "GCC", "MAS", "BNM", "HKMA", "IMDA", "PDPA", "ISO", "NIST", "OWASP", "GML", "EBIT", "EBITDA", "ROI", "SME", "SMES",
    "CASA", "NIM", "NII", "CET", "RWA", "SST", "GST", "TWNS", "NBEV", "VONB", "OPAT", "EV", "HR", "LMS", "HRIS", "CRM",
    "ERP", "SaaS", "SAAS", "PDF", "URL", "HTML", "Q&A", "QA", "FAQ", "UK", "US", "EU", "UAE", "MD", "SVP", "EVP", "VP",
    "Chief", "Officer", "Head", "Data", "Digital", "Technology", "Executive", "Committee", "Management", "Risk",
    "Singapore", "Malaysia", "Indonesia", "Thailand", "Philippines", "Vietnam", "Cambodia", "China", "Hong Kong",
    "Asia", "Pacific", "Greater", "January", "February", "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "Note", "Notes", "Section", "Page", "Table", "Figure", "Total", "Net",
    "Pte", "Pte.", "Sdn", "Sdn.", "Private", "Public", "Co", "Co.", "Company", "Corporation", "Corp", "Berhad", "Bhd", "Inc",
}
# generic phrases that end in a suffix word but are not organisations
_NOT_ORG_PHRASES = {
    "life insurance", "general insurance", "health insurance", "medical insurance", "group insurance", "term life",
    "whole life", "universal life", "the group", "the bank", "the company", "central bank", "investment holdings",
    "the board", "audit committee", "risk committee", "total assets", "net assets", "new business", "customer group",
    "working capital", "share capital", "regulatory capital", "economic capital", "human capital", "the trust", "unit trust",
    "the insurance", "the life", "comprehensive equity",
}
# leading words that make a run descriptive rather than a name ("Our Life", "Singapore Insurance")
_ORG_LEAD_STOP = {"The", "Our", "Their", "Its", "A", "An", "This", "These", "Those", "Other", "Total", "Net", "New",
                  "Group", "Life", "General", "Health", "Medical", "Singapore", "Malaysia", "Indonesia", "Asia", "Asian",
                  "Regional", "Local", "Global", "Many", "Several", "Some", "All", "Both", "Each", "Every"}

COMPETITOR_CONTEXT = [
    r"\bcompetitors?\b", r"\bpeers?\b", r"\bcompared (?:with|to|against)\b", r"\brivals?\b", r"\bversus\b", r"\bvs\.?\b",
    r"\bindustry (?:leaders|players)\b", r"\bbenchmark(?:ed|ing)? against\b", r"\bmarket share\b", r"\brelative to\b",
    r"\bcompet(?:e|ing|ition) (?:with|against|from)\b",
]
# "compared with FY2025" / "compared to last year" / "relative to the prior period": a period comparison, not a peer
_PERIOD_COMPARISON = re.compile(
    r"\b(?:compared (?:with|to|against)|relative to|versus|vs\.?)\s+(?:the\s+)?(?:(?:FY|1H|2H|[1-4]Q|H[12]|Q[1-4])\s?\d{2,4}"
    r"|\d{4}|(?:a\s+)?year\s+(?:ago|earlier)|(?:the\s+)?(?:last|previous|prior|preceding|corresponding|same)\s+"
    r"(?:year|quarter|period|half|financial year|fiscal year)|(?:the\s+)?(?:previous|prior|preceding|corresponding)\b)",
    re.I,
)


def _clean_org(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip(" ,.;:’'")


def org_names(sentence: str, exclude_patterns: Iterable[str] = (), known_aliases: Iterable[str] = ()) -> list[str]:
    """Organisation names in a sentence: suffix-terminated capitalised runs
    (NER-lite), plus any of ``known_aliases`` (peer names from the subject
    YAML) present as whole words. ``exclude_patterns`` drops the subject's own
    names. A single capitalised word, a bare acronym or a generic phrase
    ("life insurance", "the Group") is never an organisation here."""
    names: list[str] = []
    excl = [e.lower() for e in exclude_patterns if e]

    def keep(name: str) -> bool:
        low = name.lower()
        if not name or low in _NOT_ORG_PHRASES or name in _NOT_ORG:
            return False
        if any(e in low for e in excl):
            return False
        return name not in names

    for m in _ORG_RE.finditer(sentence):
        name = _clean_org(m.group(1))
        words = name.split()
        # drop descriptive lead words ("the", "our", "Singapore") and re-test
        while len(words) > 1 and words[0] in _ORG_LEAD_STOP:
            words = words[1:]
        name = " ".join(words)
        if len(words) < 2:
            continue  # a suffix word on its own ("Group", "Limited") or a one-word run
        if all(w.lower() in {x.lower() for x in _NOT_ORG} for w in words):
            continue
        if keep(name):
            names.append(name)
    for alias in known_aliases:
        alias = (alias or "").strip()
        if len(alias) < 3:
            continue
        if re.search(rf"(?<![\w-]){re.escape(alias)}(?![\w-])", sentence) and keep(alias):
            if not any(alias.lower() in n.lower() for n in names):
                names.append(alias)
    return names


def is_competitor_context(sentence: str) -> bool:
    """A sentence that compares the subject with others. A comparison with a
    period ("compared with FY2025", "versus the prior year") does not count
    on its own."""
    if not has_any(sentence, COMPETITOR_CONTEXT):
        return False
    stripped = _PERIOD_COMPARISON.sub(" ", sentence)
    return has_any(stripped, COMPETITOR_CONTEXT)


def snippet(text: str, start: int, end: int, radius: int = 160) -> str:
    a, b = max(0, start - radius), min(len(text), end + radius)
    return text[a:b].strip()
