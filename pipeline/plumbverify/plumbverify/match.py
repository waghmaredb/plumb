"""Claim-to-passage, quotation and number matching (spec C4, C5; CL-003, CL-004).

Thresholds (v0.1 defaults, to be re-calibrated at G1 against reviewer labels):
  QUOTE_THRESHOLD           0.98  rapidfuzz ratio for quotations (exact substring after normalisation = 1.0)
  SUPPORTED_THRESHOLD       0.85  claim-to-passage score at or above which a claim is SUPPORTED (verified)
  PARTIAL_THRESHOLD         0.70  below SUPPORTED but at or above this is PARTIAL
  NUMBER_CONTEXT_THRESHOLD  0.60  keyword overlap required around a found number when no semantic matcher is set
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence

from rapidfuzz import fuzz

QUOTE_THRESHOLD = 1.0  # spec: zero tolerance on quotations; 0.98 let single-character edits through
SUPPORTED_THRESHOLD = 0.85
PARTIAL_THRESHOLD = 0.70
# Number claims without a semantic matcher: the number must be present (hard gate) and the
# claim's non-numeric keywords must overlap the passage at or above this token_set_ratio.
# Interim lexical stand-in for the 0.85 semantic threshold; re-calibrate at G1 (spec open item 1).
NUMBER_CONTEXT_THRESHOLD = 0.60


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------
_QUOTE_MAP = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "−": "-", " ": " ", "…": "...",
})
_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Unicode NFKC, smart quotes/dashes to ASCII, whitespace collapsed, lowercased."""
    t = unicodedata.normalize("NFKC", text).translate(_QUOTE_MAP)
    return _WS.sub(" ", t).strip().lower()


# --------------------------------------------------------------------------
# Quotation match (C5)
# --------------------------------------------------------------------------
@dataclass
class QuoteMatch:
    score: float
    passed: bool
    exact: bool
    matched_text: Optional[str] = None
    omitted_spans: list[str] = field(default_factory=list)


def _best_window(needle: str, hay: str) -> tuple[float, Optional[str]]:
    """Best alignment of `needle` inside `hay` using partial_ratio_alignment."""
    al = fuzz.partial_ratio_alignment(needle, hay)
    if al is None:
        return 0.0, None
    return al.score / 100.0, hay[al.dest_start:al.dest_end]


def quote_match(quote: str, source_text: str, threshold: float = QUOTE_THRESHOLD) -> QuoteMatch:
    """Exact (after normalisation) or near-exact match of a quotation in the
    stored source text. Ellipses ("...") split the quote into fragments that
    must each match in order; the omitted spans are returned for logging
    (spec C5: ellipses permitted only with logged omitted span)."""
    q = normalize(quote).strip('"\'')
    hay = normalize(source_text)
    if not q or not hay:
        return QuoteMatch(score=0.0, passed=False, exact=False)
    fragments = [f.strip() for f in q.split("...") if f.strip()]
    if len(fragments) <= 1:
        if q in hay:
            return QuoteMatch(score=1.0, passed=True, exact=True, matched_text=q)
        score, window = _best_window(q, hay)
        return QuoteMatch(score=score, passed=score >= threshold, exact=False, matched_text=window)
    # ellipsis handling: fragments in order, each exact/near-exact
    pos = 0
    omitted: list[str] = []
    scores: list[float] = []
    for frag in fragments:
        idx = hay.find(frag, pos)
        if idx >= 0:
            scores.append(1.0)
            if pos and idx > pos:
                omitted.append(hay[pos:idx].strip())
            pos = idx + len(frag)
            continue
        sub = hay[pos:]
        score, window = _best_window(frag, sub)
        scores.append(score)
        if score < threshold or window is None:
            return QuoteMatch(score=min(scores), passed=False, exact=False, omitted_spans=omitted)
        idx = sub.find(window) + pos
        if pos and idx > pos:
            omitted.append(hay[pos:idx].strip())
        pos = idx + len(window)
    s = min(scores)
    return QuoteMatch(score=s, passed=s >= threshold, exact=all(x == 1.0 for x in scores),
                      matched_text=hay[: pos][-len(q) - 80:], omitted_spans=omitted)


# --------------------------------------------------------------------------
# Number normalisation and number-in-passage check (C4)
# --------------------------------------------------------------------------
_SCALE = {
    "k": 1e3, "thousand": 1e3,
    "m": 1e6, "mn": 1e6, "mln": 1e6, "million": 1e6, "millions": 1e6,
    "b": 1e9, "bn": 1e9, "bln": 1e9, "billion": 1e9, "billions": 1e9,
    "t": 1e12, "tn": 1e12, "trn": 1e12, "trillion": 1e12, "trillions": 1e12,
}
_CURRENCY = {
    "$": "USD", "us$": "USD", "usd": "USD", "s$": "SGD", "sgd": "SGD", "sg$": "SGD",
    "a$": "AUD", "aud": "AUD", "au$": "AUD", "c$": "CAD", "cad": "CAD", "hk$": "HKD", "hkd": "HKD",
    "nz$": "NZD", "€": "EUR", "eur": "EUR", "£": "GBP", "gbp": "GBP", "¥": "JPY", "jpy": "JPY",
    "rm": "MYR", "myr": "MYR", "₹": "INR", "inr": "INR", "rs": "INR", "rs.": "INR",
}
_NUM_RE = re.compile(
    r"""
    (?<![A-Za-z0-9.])
    (?P<cur>(?:US\$|S\$|SG\$|A\$|AU\$|C\$|HK\$|NZ\$|\$|€|£|¥|₹|USD|SGD|AUD|CAD|HKD|NZD|EUR|GBP|JPY|MYR|INR|RM|Rs\.?)\s*)?
    (?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)
    \s*(?P<scale>thousand|millions?|billions?|trillions?|mln|bln|trn|mn|bn|tn|k|m|b|t)?\b
    \s*(?P<pct>%|percent|per\s+cent|pct|percentage\s+points?|pp)?
    """,
    re.I | re.X,
)


@dataclass(frozen=True)
class NumberToken:
    value: float
    unit: str  # "%", ISO currency code, or "" (plain)
    raw: str


def parse_numbers(text: str, ignore_years: bool = True) -> list[NumberToken]:
    """Extract normalised numbers: commas stripped, scale words applied,
    currency prefixes and percent markers folded into `unit`."""
    out: list[NumberToken] = []
    for m in _NUM_RE.finditer(unicodedata.normalize("NFKC", text)):
        num = float(m.group("num").replace(",", ""))
        scale = (m.group("scale") or "").lower()
        if scale:
            num *= _SCALE.get(scale, 1.0)
        unit = ""
        if m.group("pct"):
            unit = "%"
        elif m.group("cur"):
            unit = _CURRENCY.get(m.group("cur").strip().lower(), m.group("cur").strip().upper())
        raw = m.group(0).strip()
        if ignore_years and not unit and not scale and raw.isdigit() and 1900 <= num <= 2100:
            continue  # treat bare 4-digit values as years, not figures
        out.append(NumberToken(value=num, unit=unit, raw=raw))
    return out


def numbers_match(a: NumberToken, b: NumberToken, rel_tol: float = 1e-6) -> bool:
    if a.unit and b.unit and a.unit != b.unit:
        return False
    if a.unit and not b.unit and a.unit == "%":
        return False  # a percentage must appear as a percentage in the passage
    if a.value == b.value:
        return True
    return abs(a.value - b.value) <= rel_tol * max(abs(a.value), abs(b.value))


@dataclass
class NumberCheck:
    claim_numbers: list[NumberToken]
    found: list[NumberToken]
    missing: list[NumberToken]

    @property
    def passed(self) -> bool:
        return bool(self.claim_numbers) and not self.missing


def number_in_passage(claim_text: str, passage: str) -> NumberCheck:
    """Every number in the claim must appear in the passage after normalisation
    (spec C4: 'the number (with unit and period) must appear in the passage')."""
    cn = parse_numbers(claim_text)
    pn = parse_numbers(passage)
    found, missing = [], []
    for c in cn:
        (found if any(numbers_match(c, p) for p in pn) else missing).append(c)
    return NumberCheck(claim_numbers=cn, found=found, missing=missing)


# --------------------------------------------------------------------------
# Claim-to-passage match (C4) with pluggable semantic matcher
# --------------------------------------------------------------------------
class SemanticMatcher(Protocol):
    """Pluggable embedding-based matcher (spec open item 2). Returns cosine-like
    similarity in [0, 1] between a claim and a passage."""

    def score(self, claim: str, passage: str) -> float: ...


@dataclass
class PassageMatch:
    passage: Optional[str]
    score: float
    lexical_score: float
    semantic_score: Optional[float]
    label: str  # "supported" | "partial" | "unsupported"


def lexical_score(claim: str, passage: str) -> float:
    return fuzz.partial_ratio(normalize(claim), normalize(passage)) / 100.0


def label_for(score: float, supported: float = SUPPORTED_THRESHOLD, partial: float = PARTIAL_THRESHOLD) -> str:
    if score >= supported:
        return "supported"
    if score >= partial:
        return "partial"
    return "unsupported"


def claim_match(
    claim: str,
    passages: Sequence[str],
    semantic: Optional[SemanticMatcher] = None,
    supported: float = SUPPORTED_THRESHOLD,
    partial: float = PARTIAL_THRESHOLD,
) -> PassageMatch:
    """Best passage for a claim. Lexical score is rapidfuzz partial_ratio;
    when a semantic matcher is configured the final score is the max of
    lexical and semantic (so a paraphrase can pass on semantics alone)."""
    best = PassageMatch(passage=None, score=0.0, lexical_score=0.0, semantic_score=None, label="unsupported")
    for p in passages:
        lex = lexical_score(claim, p)
        sem = semantic.score(claim, p) if semantic is not None else None
        score = max(lex, sem) if sem is not None else lex
        if score > best.score:
            best = PassageMatch(passage=p, score=score, lexical_score=lex, semantic_score=sem, label="unsupported")
    best.label = label_for(best.score, supported, partial)
    return best


# --------------------------------------------------------------------------
# Number-claim match: number presence is the hard gate, context is secondary
# --------------------------------------------------------------------------
@dataclass
class NumberClaimMatch:
    passage: Optional[str]
    score: float
    context_score: float
    semantic_score: Optional[float]
    check: Optional[NumberCheck]
    label: str  # "supported" | "partial" | "unsupported"


_STOP = set("""a an the of in on at to for by with from and or but is are was were be been being has have had
this that these those it its as than then there their they them we our you your his her he she not no into over
about after before between during per up down out off above below under more most less least very also just only
said says say than which who whom whose what when where why how will would can could should may might must shall
""".split())


def _keywords(text: str) -> list[str]:
    toks = _WS.sub(" ", _NUM_RE.sub(" ", normalize(text))).split()
    out = []
    for t in toks:
        t = t.strip("\"'.,;:()[]{}!?").removesuffix("'s")
        if len(t) >= 3 and t not in _STOP:
            out.append(t)
    return out


def context_score(claim: str, passage: str) -> float:
    """Keyword recall: share of the claim's content words (numbers and stop
    words removed, possessives stripped, 5-char prefix stemming) that occur
    in the passage. 1.0 when the claim has no content words."""
    kws = _keywords(claim)
    if not kws:
        return 1.0
    ptoks = set(_keywords(passage))
    pprefix = {t[:5] for t in ptoks}
    hit = sum(1 for k in kws if k in ptoks or k[:5] in pprefix)
    return hit / len(kws)


def number_claim_match(
    claim: str,
    passages: Sequence[str],
    semantic: Optional[SemanticMatcher] = None,
    supported: float = SUPPORTED_THRESHOLD,
    context_threshold: float = NUMBER_CONTEXT_THRESHOLD,
) -> NumberClaimMatch:
    """Spec C4 for number claims: every number in the claim (with unit) must
    appear in the passage; among passages that satisfy this, the best one by
    context/semantic score is chosen. SUPPORTED needs semantic >= `supported`
    when a matcher is configured, else context >= `context_threshold`.
    Numbers present but context too weak -> PARTIAL. Numbers absent -> UNSUPPORTED."""
    best: Optional[NumberClaimMatch] = None
    any_numbers = bool(parse_numbers(claim))
    for p in passages:
        chk = number_in_passage(claim, p)
        ctx = context_score(claim, p)
        sem = semantic.score(claim, p) if semantic is not None else None
        score = max(ctx, sem) if sem is not None else ctx
        if not chk.passed:
            # keep as fallback candidate so the report shows the nearest passage
            cand = NumberClaimMatch(p, score * 0.5, ctx, sem, chk, "unsupported")
        else:
            ok = (sem is not None and sem >= supported) or ctx >= context_threshold
            cand = NumberClaimMatch(p, score, ctx, sem, chk, "supported" if ok else "partial")
        rank = ({"supported": 2, "partial": 1, "unsupported": 0}[cand.label], cand.score)
        if best is None or rank > ({"supported": 2, "partial": 1, "unsupported": 0}[best.label], best.score):
            best = cand
    if best is None:
        best = NumberClaimMatch(None, 0.0, 0.0, None, None, "unsupported")
    if not any_numbers:
        best.label = "unsupported"
    return best
