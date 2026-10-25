"""Shared text helpers: AI-term lexicon, sentence splitting, word counts,
NER-lite for organisation names. Pure functions, no network."""
from __future__ import annotations

import re
from typing import Iterable

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


def ai_sentences(text: str) -> list[str]:
    return [s for s in sentences(text) if ai_mentions(s)]


def has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def count_any(text: str, patterns: Iterable[str]) -> int:
    return sum(len(re.findall(p, text, re.I)) for p in patterns)


# --------------------------------------------------------------------------
# NER-lite: organisation names in a sentence
# --------------------------------------------------------------------------
_ORG_SUFFIX = (
    r"(?:Bank|Banking|Berhad|Bhd|Group|Holdings|Financial|Finance|Insurance|Assurance|Life|Capital|Corporation|Corp|"
    r"Limited|Ltd|Plc|plc|Inc|Trust|Securities|Asset Management|Takaful|Reinsurance|Re)"
)
# Capitalised token run (allowing &, ', -, and lowercase connectors) optionally ending in an org suffix,
# or a run that ends in a suffix. Also all-caps acronyms of 3-6 letters (DBS, UOB, OCBC, AIA, CIMB, HSBC).
_ORG_RE = re.compile(
    rf"\b((?:[A-Z][A-Za-z&'’.-]+(?:\s+(?:of|de|the|&)\s+)?\s*){{0,4}}{_ORG_SUFFIX}\b(?:\s+{_ORG_SUFFIX}\b)?)|\b([A-Z]{{3,6}})\b"
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
}

COMPETITOR_CONTEXT = [
    r"\bcompetitors?\b", r"\bpeers?\b", r"\bcompared (?:with|to|against)\b", r"\brivals?\b", r"\bversus\b", r"\bvs\.?\b",
    r"\bindustry (?:leaders|players)\b", r"\bbenchmark(?:ed|ing)? against\b", r"\bmarket share\b", r"\brelative to\b",
    r"\bcompet(?:e|ing|ition) (?:with|against|from)\b",
]


def org_names(sentence: str, exclude_patterns: Iterable[str] = ()) -> list[str]:
    names: list[str] = []
    excl = [e.lower() for e in exclude_patterns]
    for m in _ORG_RE.finditer(sentence):
        name = (m.group(1) or m.group(2) or "").strip(" ,.;:")
        if not name or name in _NOT_ORG or name.split()[0] in _NOT_ORG and len(name.split()) == 1:
            continue
        if any(e and e in name.lower() for e in excl):
            continue
        if len(name.split()) == 1 and not name.isupper():
            continue  # a single capitalised word is not enough evidence of an org
        if name not in names:
            names.append(name)
    return names


def is_competitor_context(sentence: str) -> bool:
    return has_any(sentence, COMPETITOR_CONTEXT)


def snippet(text: str, start: int, end: int, radius: int = 160) -> str:
    a, b = max(0, start - radius), min(len(text), end + radius)
    return text[a:b].strip()
