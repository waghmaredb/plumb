"""C4 claim-to-passage verification for qualitative ("fact") claims (spec C4; CL-003). Added in 0.5.

Lexical similarity alone fails both ways on qualitative claims: a supported
paraphrase can score below 0.85, and a claim that flips the passage ("rolled
out" vs "testing", "reduced" vs "aims to reduce") can score above it. This
module puts real C4 verification behind the existing ``SemanticMatcher``
protocol:

Backends (tried in order; the best *available* one supplies the support score
and is recorded as ``Citation.matcher``):

  1. ``nli``        cross-encoder NLI model, score = P(entailment). Needs model
                    weights on disk (``plumbverify models pull``).
  2. ``embedding``  sentence-embedding cosine, secondary signal. Needs weights.
                    A SUPPORTED verdict from this backend also needs the offline
                    baseline to reach the PARTIAL band (cosine cannot see a
                    flipped number or a dropped hedge).
  3. ``offline``    deterministic baseline, no weights: claim decomposition,
                    domain synonym table, weighted key-term recall with a
                    per-missing-term penalty. Always available.

Contradiction rules run on every claim-passage pair whatever the backend
(they are deterministic and cheap). A fact claim is SUPPORTED only if the best
available backend says supported AND no rule fires:

  contradiction (-> UNSUPPORTED)          cap (-> PARTIAL at best)
  ------------------------------          ------------------------
  number_mismatch / number_absent         dropped_hedge  (passage "aims to",
  number_binding (number belongs to          "will", "would", "recommended" ...)
     another clause of the passage)       year_unverified (claim year, passage none)
  year_mismatch                           absolute_inflation ("all", "fully",
  approx_inflation ("more than X" vs         "eliminated" not in passage)
     "close to X")                        unsupported_superlative
  production_vs_pilot (claim asserts      embedding_without_lexical_agreement
     production, passage says testing)
  pilot_vs_production, intent_vs_done
  negation_mismatch
  direction_flip (grew vs declined)
  superlative_inflation ("the fastest" vs "one of the fastest")
  entity_substitution (claim market absent, another market present)
  nli_contradiction (NLI backend only)

Scores are in [0, 1] and comparable to SUPPORTED_THRESHOLD 0.85 /
PARTIAL_THRESHOLD 0.70. A contradiction caps the score at 0.60, a cap at 0.80.

Calibration: ``plumbverify calibrate calibration/geh_c4_v1.jsonl`` (see
``calibrate.py``). The labels in that set are author-assigned.
"""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Protocol, Sequence, runtime_checkable

from . import match as m

CONTRADICTION_CAP = 0.60
PARTIAL_CAP = 0.80
#: score multiplier per missing claim term (weight >= 1); makes one missing distinctive term drop a short claim below 0.85
MISSING_TERM_PENALTY = 0.92
#: NLI contradiction probability at or above which the nli_contradiction rule fires
NLI_CONTRADICTION_THRESHOLD = 0.50

DEFAULT_NLI_MODEL = os.environ.get("PLUMBVERIFY_NLI_MODEL", "cross-encoder/nli-deberta-v3-small")
DEFAULT_EMBEDDING_MODEL = os.environ.get("PLUMBVERIFY_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
WEIGHTS_HINT = "requires model weights; run `plumbverify models pull` on a machine with internet"


def model_cache_dir() -> Path:
    """Local directory holding pulled model weights (``PLUMBVERIFY_MODEL_DIR`` overrides)."""
    return Path(os.environ.get("PLUMBVERIFY_MODEL_DIR", Path.home() / ".cache" / "plumbverify" / "models")).expanduser()


def model_path(model_id: str, cache_dir: Optional[Path | str] = None) -> Path:
    return Path(cache_dir or model_cache_dir()) / model_id.replace("/", "__")


# ==========================================================================
# Text analysis: synonym concepts, stems, clause/sentence modality
# ==========================================================================
#: Curated domain synonym table. Each phrase regex is rewritten to one concept token before stemming,
#: so "rolled out" == "deployed" == "launched", "cut" == "reduce", "adviser" == "advisor", "AI" == "artificial intelligence".
SYNONYMS: list[tuple[str, str]] = [
    ("zzai", r"artificial intelligence|machine learning|a\.i\.|\bai\b"),
    ("zzproprietary", r"in-house|in house|proprietary|home-grown|internally developed|own-built"),
    ("zzdeploy", r"roll(?:ed|ing|s)?[- ]out|rollouts?|deploy\w*|launch\w*|introduc\w*|implement\w*|put in place|unveil\w*|"
                 r"go(?:es)? live|gone live|went live|live in production|in production|establish\w*|set up"),
    ("zztrial", r"\btest(?:s|ed|ing)?\b|\btrial(?:s|led|ling|ed|ing)?\b|\bpilot\w*|proof[- ]of[- ]concept|\bpoc\b|\bevaluat\w*|\bexperiment\w*|\bexploring\b"),
    ("zzreduce", r"reduc\w*|\bcut(?:s|ting)?\b|lower(?:ed|ing|s)?\b|decreas\w*|declin\w*|\bfell\b|\bfall(?:s|ing|en)?\b|"
                 r"\bdrop(?:s|ped|ping)?\b|shr[iau]nk\w*|slash\w*|halv\w*|shorten\w*"),
    ("zzincrease", r"increas\w*|\bgr[eo]w(?:s|n|th|ing)?\b|\bris(?:e|es|ing|en)\b|\brose\b|uplift\w*|expand\w*|expansion|boost\w*|\brais(?:e|ed|es|ing)\b|\bgain(?:s|ed)?\b"),
    ("zzaccelerate", r"accelerat\w*|speed(?:s|ed)? up|fast-track\w*"),
    ("zzslow", r"\bslow\w*|delay\w*|decelerat\w*"),
    ("zzadvisor", r"financial representatives?|financial planners?|advis[oe]rs?\b"),
    ("zzcustomer", r"customers?|policyholders?|clients?"),
    ("zzsystem", r"platforms?|solutions?|systems?|tools?|capabilit(?:y|ies)|applications?|engines?"),
    ("zzidentify", r"identif\w*|detect\w*|\bflag(?:s|ged|ging)?\b|\bspot(?:s|ted|ting)?\b"),
    ("zzimprove", r"improv\w*|enhanc\w*|strengthen\w*|sharpen\w*"),
    ("zzuse", r"\bus(?:e|es|ed|ing)\b|leverag\w*|utilis\w*|utiliz\w*|employ(?:s|ed|ing)?\b|appl(?:y|ies|ied|ying)\b"),
    ("zzachieve", r"achiev\w*|deliver\w*|attain\w*|\breach(?:es|ed|ing)?\b"),
    ("zzwin", r"\bw[oi]n(?:s|ning)?\b|award\w*"),
    ("zzmove", r"\bmov(?:e|ed|es|ing)\b|transition\w*|migrat\w*|switch\w*"),
    ("zzhelp", r"\bhelp\w*|enabl\w*|assist\w*"),
    ("zzpay", r"\bpa(?:id|y|ys|ying|yable|yments?)\b"),
    ("zzyoy", r"year[- ]on[- ]year|\byoy\b|y-o-y"),
    ("zzprofit", r"profits?|earnings"),
    ("zzbuild", r"\bbuil[dt]s?\b|building|develop(?:s|ed|ing)?\b|creat(?:e|es|ed|ing)\b"),
    ("zzoffer", r"\boffer(?:s|ed|ing)?\b|provid(?:e|es|ed|ing)\b|\bg[ia]ve?s?\b|giving|suppl(?:y|ies|ied)\b"),
    ("zzneed", r"\bneed(?:s|ed)?\b|requir(?:e|es|ed|ing)\b"),
    ("zzprocess", r"\bprocess(?:es|ed|ing)?\b|handl(?:e|es|ed|ing)\b"),
    ("zzreceive", r"\breceiv(?:e|es|ed|ing)\b|\bgot\b|\bget(?:s)?\b"),
    ("zzturnaround", r"turn(?:ed|s)? around|turnarounds?"),
]
_SYN_RE = [(c, re.compile(r"\b(?:" + p + ")")) for c, p in SYNONYMS]  # word-initial: "ecosystem" is not a system
DIRECTION_PAIRS = {("zzincrease", "zzreduce"), ("zzaccelerate", "zzslow")}
#: outcome concepts: "to reduce X" (purpose) is not "reduced X" (achieved)
OUTCOME_CONCEPTS = {"zzincrease", "zzreduce", "zzaccelerate", "zzslow", "zzimprove"}

_NUMBER_WORDS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split()) if i >= 2}
_FRACTIONS = [(re.compile(r"\bhalv(?:e|es|ed|ing)\b"), "reduce by 50%"),
              (re.compile(r"\bdoubl(?:e|es|ed|ing)\b(?!-digit)"), "increase by 100%"),
              (re.compile(r"\btripl(?:e|es|ed|ing)\b(?!-digit)"), "increase by 200%"),
              (re.compile(r"\bthree[- ]quarters\b"), "75%"), (re.compile(r"\ba quarter\b"), "25%"),
              (re.compile(r"\bhalf of\b"), "50% of"), (re.compile(r"\bone[- ]third\b"), "33%"),
              (re.compile(r"\btwo[- ]thirds\b"), "67%")]

TRIAL_CUES = {"zztrial"}
INTENT_CUES = {"aim", "aims", "aimed", "aiming", "plan", "plans", "planned", "planning", "expect", "expects", "expected",
               "expecting", "will", "would", "shall", "intend", "intends", "intended", "intending", "target", "targets",
               "targeted", "targeting", "seek", "seeks", "seeking", "hope", "hopes", "aspire", "aspires", "recommend",
               "recommends", "recommended", "propose", "proposes", "proposed", "pending", "subject", "upon", "envisage",
               "envisages", "forecast", "forecasts", "projected", "anticipate", "anticipates", "anticipated", "goal"}
#: cues that are also common nouns ("insurance plan", "sales target"): only hedges when followed by "to"
#: and adjectives ("Targeted Compliance Framework", "expected credit loss", "projected cash flows")
_NEEDS_TO = {"plan", "plans", "target", "targets", "targeted", "targeting", "goal", "subject", "aim", "hope", "forecast",
             "expected", "anticipated", "projected", "intended", "proposed"}
#: words that make a following "plan" / "target" a noun ("insurance plan to support ...")
_NOUN_MODIFIERS = {"insurance", "takaful", "savings", "protection", "health", "medical", "care", "the", "a", "an", "this",
                   "that", "our", "its", "their", "wealth", "retirement", "endowment", "life", "pension", "business",
                   "strategic", "action", "investment", "payment", "growth", "sales", "annual", "new", "shield", "rider"}
NEG_CUES = {"not", "no", "never", "without", "none", "neither", "nor", "cannot", "lack", "lacks", "lacking", "yet"}
NEG_SCOPE = 3
ABSOLUTES = re.compile(r"\b(all|every|fully|entire(?:ly)?|eliminat\w*|complete(?:ly|d)?|always|100%)")
SUPERLATIVE_RE = re.compile(r"\b(one of the |among the )?(?:the )?(fastest|first|largest|leading|best|highest|only|biggest|"
                            r"top|most \w+|lowest|cheapest|sole)\b")
APPROX_RE = re.compile(r"\b(more than|over|exceeding|above|at least|in excess of|close to|nearly|almost|approximately|about|"
                       r"around|roughly|up to|under|less than|fewer than|below)\s+(?:[a-z]{1,3}\$?|\$)?\s?(\d[\d,]*(?:\.\d+)?)")
#: a number directly followed by the noun it counts ("3.2 million likes", "75% of medical claims")
_COUNTED_RE = re.compile(r"(?<![\d.])(\d[\d,]*(?:\.\d+)?)\s*(?:%|thousand|million|billion|trillion|mn|bn|k)?\s+(?:of\s+)?([a-z]{3,})")
_LOWER_BOUND = {"more than", "over", "exceeding", "above", "at least", "in excess of"}
_UPPER_BOUND = {"close to", "nearly", "almost", "up to", "under", "less than", "fewer than", "below"}
GEOS = {"singapore", "malaysia", "indonesia", "brunei", "asia", "china", "hong kong", "thailand", "vietnam", "philippines",
        "india", "australia", "japan", "europe", "apac", "asean", "korea", "taiwan"}
MONTHS = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"}
_YEAR_RE = re.compile(r"\b(?:fy|cy)?\s?((?:19|20)\d{2})\b")
_STOP = m._STOP | {
    "great", "eastern", "group", "company", "we", "us", "our", "its", "their", "it", "has", "have", "had", "is", "are",
    "was", "were", "be", "been", "being", "powered", "driven", "enabled", "based", "led", "new", "also", "further",
    "significantly", "significant", "including", "such", "like", "well", "now", "made", "make", "makes", "since",
    "across", "within", "via", "through", "while", "where", "which", "who", "that", "this", "these", "those", "both",
    "per", "cent", "percent", "approximately", "about", "around", "roughly", "close", "nearly", "almost", "over",
    "more", "than", "exceeding", "above", "least", "up", "under", "less", "fewer", "below", "some", "several",
    "mr", "ms", "dr", "the", "and", "of", "to", "in", "on", "at", "for", "by", "with", "from", "as", "an", "a",
    "thanks", "due", "because", "according", "said", "says", "into", "onto", "total",
} - {"no", "not", "without"}
# low-information domain terms: counted, but with a small weight
_LOW_WEIGHT = {"zzai": 0.5, "zzsystem": 0.6, "zzcustomer": 0.8, "zzimprove": 0.6, "zzhelp": 0.4, "zzuse": 0.5,
               "zzproprietary": 0.8, "zzdeploy": 0.7, "zzachieve": 0.3, "year": 0.3, "insurer": 0.6, "insurance": 0.6}
_CUE_TOKENS = TRIAL_CUES | INTENT_CUES | NEG_CUES
_SUFFIXES = ("ational", "ation", "ising", "izing", "ised", "ized", "ings", "ing", "edly", "ies", "ied", "ers", "ed",
             "es", "er", "ly", "s")


def stem(tok: str) -> str:
    if tok.startswith("zz"):
        return tok
    for suf in _SUFFIXES:
        if len(tok) - len(suf) >= 4 and tok.endswith(suf):
            tok = tok[: -len(suf)]
            break
    return tok


def _same(a: str, b: str) -> bool:
    if a == b:
        return True
    if a.startswith("zz") or b.startswith("zz"):
        return False
    return len(a) >= 6 and len(b) >= 6 and a[:6] == b[:6]


@dataclass
class Token:
    stem: str
    surface: str
    sentence: int
    clause: int
    modality: str  # PLAIN | TRIAL | INTENT | NEG
    entity: bool = False
    weight: float = 1.0
    purpose: bool = False  # outcome verb in a purpose infinitive ("to reduce costs"), not an achieved outcome


@dataclass
class Analysis:
    text: str
    norm: str
    tokens: list[Token]
    numbers: list[m.NumberToken]
    years: set[int]
    geos: set[str]
    entities: set[str]
    approx: dict[float, str]            # number value -> qualifier preceding it
    counted: dict[float, set[str]]      # number literal -> stems of the noun it counts ("3.2 million likes" -> {"like"})
    superlatives: list[tuple[bool, str]]  # (hedged "one of the", word)
    absolutes: set[str]
    clause_text: dict[int, str]
    has_trial: bool
    has_intent: bool
    has_neg: bool

    def content(self) -> list[Token]:
        return [t for t in self.tokens if t.weight > 0]

    def stems(self) -> set[str]:
        return {t.stem for t in self.tokens}


def _prep(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).translate(m._QUOTE_MAP)
    t = re.sub(r"(\w)-\s+(\w)", r"\1-\2", t)          # "AI- powered" (line-break hyphen) -> "AI-powered"
    t = re.sub(r"(?i)\blower-risk\b", "lowrisk", t)    # adjective, not a direction
    t = re.sub(r"\b24\s?/\s?7\b", "round-the-clock", t)  # not the numbers 24 and 7
    return t


def _canon(low: str) -> str:
    for rx, rep in _FRACTIONS:
        low = rx.sub(rep, low)
    low = re.sub(r"\b(" + "|".join(_NUMBER_WORDS) + r")\b", lambda mm: _NUMBER_WORDS[mm.group(1)], low)
    for concept, rx in _SYN_RE:
        low = rx.sub(f" {concept} ", low)
    return low


_SENT_RE = re.compile(r"(?<!\d)[.!?](?!\d)|;")
_CLAUSE_RE = re.compile(r",(?!\d{3})|:|\(|\)| - | which | who | while ")
_WORD_RE = re.compile(r"[a-z][a-z0-9&'$]*|\d[\d,]*(?:\.\d+)?%?")


@lru_cache(maxsize=65536)
def analyse(text: str) -> Analysis:
    raw = _prep(text)
    low = raw.lower()
    entities = set()
    for i, mm in enumerate(re.finditer(r"\b([A-Z][A-Za-z0-9&]+|[A-Z]{2,}[a-z]?)\b", raw)):
        w = mm.group(1)
        start = mm.start()
        prev = raw[:start].rstrip()
        sentence_initial = not prev or prev[-1] in ".!?\"'“("
        lw = w.lower()
        if lw in _STOP or lw in MONTHS or lw in {"ai", "a", "in", "the"}:
            continue
        if sentence_initial and not w.isupper():
            continue
        entities.add(stem(lw))
    geos = {g for g in GEOS if re.search(rf"\b{g}\b", low)}
    years = {int(y) for y in _YEAR_RE.findall(low)}
    canon = _canon(low)
    numbers = m.parse_numbers(_canon_numbers_only(low))
    approx: dict[float, str] = {}
    for mm in APPROX_RE.finditer(_canon_numbers_only(low)):
        try:
            approx[float(mm.group(2).replace(",", ""))] = mm.group(1)
        except ValueError:
            pass
    counted: dict[float, set[str]] = {}
    for mm in _COUNTED_RE.finditer(_canon_numbers_only(low)):
        noun = mm.group(2)
        if noun in _STOP or noun in MONTHS:
            continue
        counted.setdefault(float(mm.group(1).replace(",", "")), set()).add(stem(noun))
    sups = [(bool(mm.group(1)), mm.group(2)) for mm in SUPERLATIVE_RE.finditer(low)]
    absolutes = {mm.group(1) for mm in ABSOLUTES.finditer(low)}
    tokens: list[Token] = []
    clause_text: dict[int, str] = {}
    clause_id = 0
    has_trial = has_intent = has_neg = False
    for si, sent in enumerate(s for s in _SENT_RE.split(canon) if s.strip()):
        sent_words = _WORD_RE.findall(sent)
        trial_sentence = any(w in TRIAL_CUES for w in sent_words)
        has_trial |= trial_sentence
        state = "TRIAL" if trial_sentence else "PLAIN"
        neg_budget = 0
        purpose_chain = False
        for clause in _CLAUSE_RE.split(sent):
            if not clause or not clause.strip():
                continue
            clause_id += 1
            clause_text[clause_id] = clause.strip()
            words = _WORD_RE.findall(clause)
            for j, w in enumerate(words):
                nxt = words[j + 1] if j + 1 < len(words) else ""
                prv = words[j - 1] if j > 0 else ""
                if w in INTENT_CUES and not (w == "upon" and "approval" not in words) and not (
                        w in _NEEDS_TO and (nxt not in {"to", "at"} or prv in _NOUN_MODIFIERS)):
                    if state != "TRIAL":
                        state = "INTENT"
                    has_intent = True
                    continue
                if w in TRIAL_CUES:
                    # kept as a zero-weight token so decomposition can name the predicate; never counted in recall
                    tokens.append(Token(stem=w, surface=w, sentence=si, clause=clause_id, modality="TRIAL", weight=0.0))
                    continue
                if w in NEG_CUES:
                    if w == "yet" and "has" not in words[max(0, j - 2):j] and "have" not in words[max(0, j - 2):j]:
                        continue
                    neg_budget = NEG_SCOPE
                    has_neg = True
                    continue
                if any(ch.isdigit() for ch in w):
                    continue
                w = w.strip("'").removesuffix("'s")
                if not w or (len(w) < 2) or w in MONTHS:
                    continue
                st = stem(w)
                if w in _STOP or st in _STOP:
                    continue
                prev_w = words[j - 1] if j > 0 else ""
                purpose = False
                if st in OUTCOME_CONCEPTS:
                    purpose = prev_w == "to" or (purpose_chain and prev_w in {"and", "or"})
                    purpose_chain = purpose
                modality = state
                if neg_budget > 0:
                    modality = "NEG"
                    neg_budget -= 1
                weight = _LOW_WEIGHT.get(st, 1.0)
                is_ent = st in entities or w in GEOS
                if is_ent:
                    weight = 1.5
                tokens.append(Token(stem=st, surface=w, sentence=si, clause=clause_id, modality=modality, entity=is_ent, weight=weight,
                                    purpose=purpose))
    return Analysis(text=text, norm=low, tokens=tokens, numbers=numbers, years=years, geos=geos, entities=entities,
                    approx=approx, counted=counted, superlatives=sups, absolutes=absolutes, clause_text=clause_text,
                    has_trial=has_trial, has_intent=has_intent, has_neg=has_neg)


def _canon_numbers_only(low: str) -> str:
    for rx, rep in _FRACTIONS:
        low = rx.sub(rep, low)
    return re.sub(r"\b(" + "|".join(_NUMBER_WORDS) + r")\b", lambda mm: _NUMBER_WORDS[mm.group(1)], low)


# ==========================================================================
# Claim decomposition (recorded in the citation; drives nothing on its own)
# ==========================================================================
_PREDICATE_CONCEPTS = {"zzdeploy", "zztrial", "zzreduce", "zzincrease", "zzaccelerate", "zzslow", "zzuse", "zzachieve",
                       "zzwin", "zzmove", "zzimprove", "zzidentify", "zzhelp", "zzpay", "zzturnaround"}


@dataclass
class Decomposition:
    subject: str
    predicate: str
    object: str
    numbers: list[str]
    years: list[int]
    qualifiers: list[str]
    modality: str  # PLAIN | TRIAL | INTENT | NEG

    def as_dict(self) -> dict:
        return {"subject": self.subject, "predicate": self.predicate, "object": self.object, "numbers": self.numbers,
                "years": self.years, "qualifiers": self.qualifiers, "modality": self.modality}


def decompose(claim: str) -> Decomposition:
    """Rule-based (subject, predicate, object/number, qualifiers) split of a claim.
    The predicate is the first verb concept from the synonym table (or the first
    -ed / -s verb-looking token); subject is what precedes it, object what follows."""
    a = analyse(claim)
    toks = a.tokens
    pi = next((i for i, t in enumerate(toks) if t.stem in _PREDICATE_CONCEPTS), None)
    if pi is None:
        pi = next((i for i, t in enumerate(toks) if t.surface.endswith("ed") and i > 0), None)
    quals: list[str] = []
    if a.has_trial:
        quals.append("trial/pilot")
    if a.has_intent:
        quals.append("hedge/intent")
    if a.has_neg:
        quals.append("negation")
    quals += [f"approx:{v}" for v in sorted(set(a.approx.values()))]
    quals += [("one of the " if h else "the ") + w for h, w in a.superlatives]
    quals += sorted(a.absolutes)
    modality = "TRIAL" if a.has_trial else "NEG" if a.has_neg else "INTENT" if a.has_intent else "PLAIN"
    words = lambda ts: " ".join(t.surface.removeprefix("zz") for t in ts)  # noqa: E731 - concept tokens shown by name
    if pi is None:
        return Decomposition(words(toks), "", "", [n.raw for n in a.numbers], sorted(a.years), quals, modality)
    return Decomposition(
        subject=words(toks[:pi]),
        predicate=toks[pi].stem.removeprefix("zz") if toks[pi].stem.startswith("zz") else toks[pi].surface,
        object=words(toks[pi + 1:]),
        numbers=[n.raw for n in a.numbers], years=sorted(a.years), qualifiers=quals, modality=modality,
    )


# ==========================================================================
# Offline scoring and contradiction rules
# ==========================================================================
@dataclass
class RuleHit:
    rule: str
    effect: str  # "contradiction" | "cap"
    detail: str

    def __str__(self) -> str:
        return f"{self.rule} ({self.effect}): {self.detail}"


def _occurrences(tok: Token, p: Analysis) -> list[Token]:
    return [t for t in p.tokens if _same(tok.stem, t.stem)]


def key_term_recall(claim: str, passage: str) -> tuple[float, list[str]]:
    """Weighted recall of the claim's content terms in the passage, with a
    multiplicative penalty per missing term of weight >= 1. Returns (score, missing)."""
    c, p = analyse(claim), analyse(passage)
    terms: dict[str, Token] = {}
    for t in c.content():
        terms.setdefault(t.stem, t)
    if not terms:
        return 1.0, []
    pst = p.stems()
    inits = _initialisms(_prep(passage))
    tot = hit = 0.0
    missing: list[str] = []
    for st, t in terms.items():
        tot += t.weight
        if st in pst or any(_same(st, q) for q in pst) or (t.entity and t.surface in inits):
            hit += t.weight
        else:
            missing.append(t.surface)
    n_missing = sum(1 for st, t in terms.items() if t.surface in missing and t.weight >= 1.0)
    return (hit / tot) * (MISSING_TERM_PENALTY ** n_missing), missing


def _aligned_sentences(c: Analysis, p: Analysis, exclude: set[str] = frozenset()) -> set[int]:
    cst = {t.stem for t in c.content() if t.stem not in exclude}
    best, out = 0.0, set()
    by_sent: dict[int, set[str]] = {}
    for t in p.tokens:
        by_sent.setdefault(t.sentence, set()).add(t.stem)
    for s, sts in by_sent.items():
        score = sum(1 for x in cst if any(_same(x, y) for y in sts))
        if score > best:
            best, out = score, {s}
        elif score == best and score > 0:
            out.add(s)
    return out


ROLES = {"zzcustomer", "zzadvisor", "employe", "employee", "staff", "agent", "director", "partner", "shareholder", "user",
         "investor", "member", "patient", "student"}
_FOR_ROLE_RE = re.compile(r"\bfor\s+(?:(?:all|existing|new|the|our|its|their|financial|eligible|selected|some|lower-risk|lowrisk)\s+)*([a-z]+)")


def _lead(n: m.NumberToken) -> float:
    """Numeric literal of a parsed number before scale words ("2 million" -> 2.0); approx qualifiers are keyed on it."""
    mm = re.search(r"\d[\d,]*(?:\.\d+)?", n.raw)
    return float(mm.group().replace(",", "")) if mm else n.value


def _initialisms(text: str) -> set[str]:
    out = set()
    for mm in re.finditer(r"\b[A-Z][a-z]+(?:\s+(?:of|and|&|for)?\s*[A-Z][a-z]+)+", text):
        out.add("".join(w[0] for w in re.findall(r"[A-Z][a-z]+", mm.group())).lower())
    return out


def _for_roles(canon_text: str) -> set[str]:
    out = set()
    for mm in _FOR_ROLE_RE.finditer(canon_text):
        st = stem(mm.group(1))
        if st in ROLES:
            out.add(st)
    return out


def contradiction_rules(claim: str, passage: str) -> list[RuleHit]:
    """Deterministic C4 rules. Every hit is recorded on the citation."""
    c, p = analyse(claim), analyse(passage)
    hits: list[RuleHit] = []
    # -- numbers -------------------------------------------------------------
    pn = p.numbers
    for n in c.numbers:
        if not any(m.numbers_match(n, q) for q in pn):
            if pn:
                hits.append(RuleHit("number_mismatch", "contradiction", f"claim number {n.raw!r} not in passage (passage has {', '.join(q.raw for q in pn[:6])})"))
            else:
                hits.append(RuleHit("number_absent", "contradiction", f"claim number {n.raw!r}; passage states no figure"))
            continue
        # approximate-qualifier inflation: "more than X" vs "close to X"
        cq, pq = c.approx.get(_lead(n)), p.approx.get(_lead(n))
        if cq in _LOWER_BOUND and pq in _UPPER_BOUND:
            hits.append(RuleHit("approx_inflation", "contradiction", f"claim says '{cq} {n.raw}', passage says '{pq} {n.raw}'"))
        # counted-noun substitution: "3.2 million comments" vs "3.2 million likes, 12 thousand comments"
        cn, pnn = c.counted.get(_lead(n), set()), p.counted.get(_lead(n), set())
        # fires only when the claim's noun is counted by a *different* number in the passage
        other_counted = {y for v, ys in p.counted.items() if v != _lead(n) for y in ys}
        swapped = [x for x in cn if pnn and not any(_same(x, y) for y in pnn) and any(_same(x, y) for y in other_counted)]
        if swapped:
            hits.append(RuleHit("counted_noun_mismatch", "contradiction",
                                f"claim counts {n.raw!r} {swapped[0]}; passage counts it as {sorted(pnn)[0]}"))
        # number binding: the clause holding the number in the passage must share a term with the claim
        cterms = {t.stem for t in c.content()}
        bound = False
        found_any = False
        for cid, ctext in p.clause_text.items():
            if not any(m.numbers_match(n, q) for q in m.parse_numbers(_canon_numbers_only(ctext))):
                continue
            found_any = True
            cl_stems = {t.stem for t in p.tokens if t.clause == cid}
            if any(_same(x, y) for x in cterms for y in cl_stems):
                bound = True
                break
        if found_any and not bound and cterms:
            hits.append(RuleHit("number_binding", "contradiction", f"{n.raw!r} appears in the passage only in a clause unrelated to the claim"))
    # -- years ---------------------------------------------------------------
    missing_years = c.years - p.years
    if missing_years:
        if p.years:
            hits.append(RuleHit("year_mismatch", "contradiction", f"claim year(s) {sorted(missing_years)} vs passage {sorted(p.years)}"))
        else:
            hits.append(RuleHit("year_unverified", "cap", f"claim year(s) {sorted(missing_years)}; passage states no year"))
    # -- modality: pilot / hedge / negation ----------------------------------
    trial_only, intent_only, neg_flip, unneg = [], [], [], []
    claim_trial_terms, claim_trial_mismatch = 0, 0
    for t in c.content():
        occ = _occurrences(t, p)
        if not occ:
            continue
        mods = {o.modality for o in occ}
        if t.modality == "PLAIN":
            if mods == {"TRIAL"} and t.weight >= 0.6:
                trial_only.append(t.surface)
            elif mods <= {"INTENT", "TRIAL"} and "INTENT" in mods:
                intent_only.append(t.surface)
            elif mods == {"NEG"}:
                unneg.append(t.surface)
        elif t.modality == "TRIAL":
            claim_trial_terms += 1
            if "TRIAL" not in mods:
                claim_trial_mismatch += 1
        elif t.modality == "NEG" and "NEG" not in mods:
            neg_flip.append(t.surface)
    # A bare label ("LLMOps Engineer") asserts nothing as done, so it cannot
    # contradict a passage that mentions testing/evaluation (C4 run-5 fix).
    claim_asserts = any(t.stem in _PREDICATE_CONCEPTS for t in c.content()) or bool(c.numbers)
    if trial_only and not c.has_trial and claim_asserts:
        hits.append(RuleHit("production_vs_pilot", "contradiction",
                            f"claim asserts it as done; passage puts {', '.join(trial_only)} under testing/pilot"))
    if claim_trial_terms and claim_trial_mismatch * 2 >= claim_trial_terms and not p.has_trial:
        hits.append(RuleHit("pilot_vs_production", "contradiction", "claim says testing/pilot; passage reports it as done"))
    elif claim_trial_terms and claim_trial_mismatch * 2 >= claim_trial_terms:
        hits.append(RuleHit("pilot_vs_production", "contradiction", "claim puts under testing what the passage reports as done"))
    if intent_only and not c.has_intent:
        hits.append(RuleHit("dropped_hedge", "cap", f"passage hedges {', '.join(intent_only[:4])} (aims to / will / would / recommended); claim states it as fact"))
    # claim hedges a predicate the passage reports as done ("plans to launch" vs "rolled out")
    if c.has_intent:
        for t in c.content():
            if t.modality == "INTENT" and t.stem in _PREDICATE_CONCEPTS:
                occ = _occurrences(t, p)
                if occ and all(o.modality == "PLAIN" for o in occ) and t.stem == "zzdeploy":
                    hits.append(RuleHit("intent_vs_done", "contradiction", f"claim says '{t.surface}' is planned; passage reports it as done"))
                break
    if neg_flip:
        hits.append(RuleHit("negation_mismatch", "contradiction", f"claim negates {', '.join(neg_flip)}; passage does not"))
    if unneg:
        hits.append(RuleHit("negation_mismatch", "contradiction", f"passage negates {', '.join(unneg)} (not/no/without); claim asserts it"))
    # -- direction ----------------------------------------------------------
    dir_concepts = {x for pair in DIRECTION_PAIRS for x in pair}
    sents = _aligned_sentences(c, p, exclude=dir_concepts)
    cst = {t.stem for t in c.content() if t.stem not in dir_concepts}
    need = min(2, len(cst)) or 1
    rel: dict[int, set[str]] = {}
    by_sent: dict[int, set[str]] = {}
    for t in p.tokens:
        by_sent.setdefault(t.sentence, set()).add(t.stem)
    for si, sts in by_sent.items():
        if sum(1 for x in cst if any(_same(x, y) for y in sts)) >= need:
            rel[si] = sts
    c_dirs = {t.stem for t in c.tokens if t.stem in dir_concepts}
    for a_, b_ in DIRECTION_PAIRS:
        for d, opp in ((a_, b_), (b_, a_)):
            if d in c_dirs and any(opp in sts and d not in sts for sts in rel.values()) and not any(d in sts for sts in rel.values()):
                hits.append(RuleHit("direction_flip", "contradiction", f"claim says {d[2:]}, passage says {opp[2:]}"))
    # purpose stated as outcome: passage "to reduce costs", claim "reduced costs"
    as_outcome = []
    for t in c.content():
        if t.stem in OUTCOME_CONCEPTS and not t.purpose and t.modality == "PLAIN":
            occ = _occurrences(t, p)
            if occ and all(o.purpose for o in occ):
                as_outcome.append(t.surface[2:] if t.surface.startswith("zz") else t.surface)
    if as_outcome:
        hits.append(RuleHit("purpose_as_outcome", "cap", f"passage gives '{', '.join(as_outcome)}' as a purpose ('to ...'); claim states it as achieved"))
    # -- beneficiary / role substitution ("for customers" vs "for financial advisors") --
    c_roles = _for_roles(" ".join(c.clause_text.values()))
    if c_roles:
        aligned_clauses = {t.clause for t in p.tokens if t.sentence in (sents or {t.sentence for t in p.tokens})}
        p_roles = _for_roles(" ".join(p.clause_text[i] for i in sorted(aligned_clauses) if i in p.clause_text))
        if p_roles and not (c_roles & p_roles):
            hits.append(RuleHit("role_substitution", "contradiction",
                                f"claim says it is for {sorted(r.removeprefix('zz') for r in c_roles)}, passage says for {sorted(r.removeprefix('zz') for r in p_roles)}"))
    # -- superlatives / absolutes -------------------------------------------
    for hedged, word in c.superlatives:
        if hedged:
            continue
        p_match = [h for h, w in p.superlatives if w == word]
        if p_match and all(p_match):
            hits.append(RuleHit("superlative_inflation", "contradiction", f"claim says 'the {word}', passage says 'one of the {word}'"))
        elif not p_match and word not in p.norm:
            hits.append(RuleHit("unsupported_superlative", "cap", f"'{word}' not stated in the passage"))
    if p.geos and not c.geos and any(not h for h, _ in c.superlatives) and p.superlatives:
        hits.append(RuleHit("dropped_scope", "cap", f"superlative stated without the passage's market scope {sorted(p.geos)}"))
    abs_missing = sorted(a for a in c.absolutes if not re.search(r"\b" + re.escape(a[:6]), p.norm))
    if abs_missing:
        hits.append(RuleHit("absolute_inflation", "cap", f"{', '.join(abs_missing)} not stated in the passage"))
    # -- market / geography substitution ------------------------------------
    if c.geos and p.geos and not (c.geos & p.geos):
        hits.append(RuleHit("entity_substitution", "contradiction", f"claim market {sorted(c.geos)} vs passage {sorted(p.geos)}"))
    # de-duplicate
    seen, out = set(), []
    for h in hits:
        k = (h.rule, h.detail)
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out


# ==========================================================================
# Backends
# ==========================================================================
@dataclass
class BackendScore:
    backend: str
    score: float
    detail: dict = field(default_factory=dict)


class BackendUnavailable(RuntimeError):
    pass


@runtime_checkable
class C4Backend(Protocol):
    name: str

    def available(self) -> bool: ...

    def assess(self, claim: str, passage: str) -> BackendScore: ...

    def score(self, claim: str, passage: str) -> float: ...  # SemanticMatcher-compatible


class OfflineBaseline:
    """Deterministic baseline: weighted key-term recall over the domain synonym table."""
    name = "offline"

    def available(self) -> bool:
        return True

    def assess(self, claim: str, passage: str) -> BackendScore:
        s, missing = key_term_recall(claim, passage)
        return BackendScore("offline", round(s, 4), {"missing_terms": missing})

    def score(self, claim: str, passage: str) -> float:
        return self.assess(claim, passage).score


class _ModelBackend:
    name = "model"
    default_model = ""

    def __init__(self, model_id: Optional[str] = None, cache_dir: Optional[Path | str] = None, device: str = "cpu",
                 predictor: Optional[Callable[..., Any]] = None):
        self.model_id = model_id or self.default_model
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.device = device
        self._predictor = predictor  # injectable for tests and for callers that already hold a model
        self._load_error: Optional[str] = None
        self._loaded = predictor is not None

    @property
    def path(self) -> Path:
        return model_path(self.model_id, self.cache_dir)

    def available(self) -> bool:
        if self._loaded:
            return True
        if self._load_error is not None:
            return False
        try:
            self._load()
            self._loaded = True
        except BackendUnavailable as e:
            self._load_error = str(e)
        return self._loaded

    @property
    def unavailable_reason(self) -> Optional[str]:
        if self._loaded:
            return None
        self.available()
        return self._load_error

    def _load(self) -> None:  # pragma: no cover - needs weights
        raise NotImplementedError

    def score(self, claim: str, passage: str) -> float:
        return self.assess(claim, passage).score


class NLIBackend(_ModelBackend):
    """Cross-encoder NLI (MNLI/ANLI-style 3-way head). Score = P(entailment) of
    premise=passage, hypothesis=claim. Lazy-loads from the local cache only
    (``local_files_only``); never downloads during a verification run."""
    name = "nli"
    default_model = DEFAULT_NLI_MODEL

    def _load(self) -> None:
        if not self.path.exists():
            raise BackendUnavailable(f"NLI model {self.model_id} not found at {self.path}: {WEIGHTS_HINT}")
        try:
            from sentence_transformers import CrossEncoder  # type: ignore
            ce = CrossEncoder(str(self.path), device=self.device, local_files_only=True)
            id2label = {int(k): v.lower() for k, v in ce.model.config.id2label.items()}

            def predict(pairs):
                import numpy as np
                logits = np.asarray(ce.predict(pairs, apply_softmax=False))
                e = np.exp(logits - logits.max(axis=1, keepdims=True))
                probs = e / e.sum(axis=1, keepdims=True)
                return [{id2label[i]: float(row[i]) for i in range(len(row))} for row in probs]
            self._predictor = predict
            return
        except ImportError:
            pass
        try:
            import torch  # type: ignore
            from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
        except ImportError as e:
            raise BackendUnavailable(f"NLI backend needs sentence-transformers or transformers+torch "
                                     f"(pip install 'plumbverify[models]'): {e}") from e
        tok = AutoTokenizer.from_pretrained(str(self.path), local_files_only=True)
        mdl = AutoModelForSequenceClassification.from_pretrained(str(self.path), local_files_only=True).to(self.device).eval()
        id2label = {int(k): v.lower() for k, v in mdl.config.id2label.items()}

        def predict(pairs):
            with torch.no_grad():
                enc = tok([a for a, _ in pairs], [b for _, b in pairs], truncation=True, max_length=512,
                          padding=True, return_tensors="pt").to(self.device)
                probs = torch.softmax(mdl(**enc).logits, dim=-1).cpu().tolist()
            return [{id2label[i]: p for i, p in enumerate(row)} for row in probs]
        self._predictor = predict

    def assess(self, claim: str, passage: str) -> BackendScore:
        if not self.available():
            raise BackendUnavailable(self._load_error or WEIGHTS_HINT)
        probs = self._predictor([(passage, claim)])[0]
        ent = next((v for k, v in probs.items() if k.startswith("entail")), 0.0)
        con = next((v for k, v in probs.items() if k.startswith("contradict")), 0.0)
        return BackendScore("nli", round(float(ent), 4), {"contradiction": round(float(con), 4), "probs": probs, "model": self.model_id})


class EmbeddingBackend(_ModelBackend):
    """Sentence-embedding cosine similarity (secondary signal), clipped to [0, 1]."""
    name = "embedding"
    default_model = DEFAULT_EMBEDDING_MODEL

    def _load(self) -> None:
        if not self.path.exists():
            raise BackendUnavailable(f"embedding model {self.model_id} not found at {self.path}: {WEIGHTS_HINT}")
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as e:
            raise BackendUnavailable(f"embedding backend needs sentence-transformers (pip install 'plumbverify[models]'): {e}") from e
        st = SentenceTransformer(str(self.path), device=self.device, local_files_only=True)

        def predict(pairs):
            import numpy as np
            a = st.encode([x for x, _ in pairs], normalize_embeddings=True)
            b = st.encode([y for _, y in pairs], normalize_embeddings=True)
            return [float(np.dot(u, v)) for u, v in zip(a, b)]
        self._predictor = predict

    def assess(self, claim: str, passage: str) -> BackendScore:
        if not self.available():
            raise BackendUnavailable(self._load_error or WEIGHTS_HINT)
        cos = float(self._predictor([(claim, passage)])[0])
        return BackendScore("embedding", round(max(0.0, min(1.0, cos)), 4), {"cosine": round(cos, 4), "model": self.model_id})


class SemanticMatcherBackend:
    """Adapter for a plain ``match.SemanticMatcher`` (score-only) passed by a caller."""

    def __init__(self, matcher: m.SemanticMatcher, name: str = "custom"):
        self.matcher, self.name = matcher, name

    def available(self) -> bool:
        return True

    def assess(self, claim: str, passage: str) -> BackendScore:
        return BackendScore(self.name, round(float(self.matcher.score(claim, passage)), 4))

    def score(self, claim: str, passage: str) -> float:
        return float(self.matcher.score(claim, passage))


def default_backends(cache_dir: Optional[Path | str] = None) -> list:
    """nli -> embedding -> offline. Model backends drop out silently when weights are absent."""
    return [NLIBackend(cache_dir=cache_dir), EmbeddingBackend(cache_dir=cache_dir), OfflineBaseline()]


# ==========================================================================
# Verifier (decision logic)
# ==========================================================================
@dataclass
class C4Assessment:
    passage: Optional[str]
    score: float
    label: str                 # supported | partial | unsupported
    matcher: str               # backend that supplied the support score
    backend_scores: dict[str, float]
    rules: list[RuleHit]
    raw_score: float           # best backend's score before rule caps
    decomposition: Optional[dict] = None
    page: Optional[int] = None
    detail: dict = field(default_factory=dict)

    @property
    def rules_fired(self) -> list[str]:
        return [str(r) for r in self.rules]


def _label(score: float, supported: float, partial: float) -> str:
    return m.label_for(score, supported, partial)


class C4Verifier:
    """Decision logic for fact claims: SUPPORTED only if the best available
    backend's score reaches ``supported`` AND no contradiction/cap rule fires."""

    def __init__(self, backends: Optional[Sequence] = None, supported: float = m.SUPPORTED_THRESHOLD,
                 partial: float = m.PARTIAL_THRESHOLD, require_lexical_agreement_for_embedding: bool = True,
                 nli_contradiction: float = NLI_CONTRADICTION_THRESHOLD):
        self.backends = list(backends) if backends is not None else default_backends()
        if not any(isinstance(b, OfflineBaseline) for b in self.backends):
            self.backends.append(OfflineBaseline())
        self.supported, self.partial = supported, partial
        self.require_lexical_agreement_for_embedding = require_lexical_agreement_for_embedding
        self.nli_contradiction = nli_contradiction

    @classmethod
    def from_matcher(cls, matcher: Optional[m.SemanticMatcher], **kw) -> "C4Verifier":
        """Build from the pipeline's ``semantic`` argument: None -> default backend chain;
        a C4Verifier -> itself; a C4Backend -> [it, offline]; a plain SemanticMatcher -> [custom, offline]."""
        if isinstance(matcher, C4Verifier):
            return matcher
        if matcher is None:
            return cls(**kw)
        if hasattr(matcher, "assess") and hasattr(matcher, "available"):
            return cls(backends=[matcher, OfflineBaseline()], **kw)
        return cls(backends=[SemanticMatcherBackend(matcher), OfflineBaseline()], **kw)

    def live_backends(self) -> list:
        return [b for b in self.backends if b.available()]

    def status(self) -> list[dict]:
        out = []
        for b in self.backends:
            ok = b.available()
            out.append({"backend": b.name, "available": ok,
                        "model": getattr(b, "model_id", None), "path": str(getattr(b, "path", "")) or None,
                        "reason": None if ok else getattr(b, "unavailable_reason", None)})
        return out

    def score(self, claim: str, passage: str) -> float:  # SemanticMatcher-compatible
        return self.assess(claim, passage).score

    def assess(self, claim: str, passage: str) -> C4Assessment:
        live = self.live_backends()
        scores: dict[str, BackendScore] = {}
        for b in live:
            try:
                scores[b.name] = b.assess(claim, passage)
            except BackendUnavailable:
                continue
        primary = next(b.name for b in live if b.name in scores)
        raw = scores[primary].score
        rules = contradiction_rules(claim, passage)
        nli = scores.get("nli")
        if nli is not None and nli.detail.get("contradiction", 0.0) >= self.nli_contradiction:
            rules.append(RuleHit("nli_contradiction", "contradiction", f"P(contradiction) = {nli.detail['contradiction']:.2f}"))
        if (primary == "embedding" and self.require_lexical_agreement_for_embedding
                and scores["offline"].score < self.partial and raw >= self.supported):
            rules.append(RuleHit("embedding_without_lexical_agreement", "cap",
                                 f"cosine {raw:.2f} but offline key-term score {scores['offline'].score:.2f} < {self.partial}"))
        s = raw
        if any(r.effect == "contradiction" for r in rules):
            s = min(s, CONTRADICTION_CAP)
        elif any(r.effect == "cap" for r in rules):
            s = min(s, PARTIAL_CAP)
        label = _label(s, self.supported, self.partial)
        if any(r.effect == "contradiction" for r in rules):
            label = "unsupported"
        elif label == "supported" and rules:
            label = "partial"
        return C4Assessment(passage=passage, score=round(s, 4), label=label, matcher=primary,
                            backend_scores={k: v.score for k, v in scores.items()}, rules=rules, raw_score=raw,
                            detail={k: v.detail for k, v in scores.items() if v.detail})

    def best(self, claim: str, passages: Sequence[str] | Sequence[tuple[str, Optional[int]]],
             top_k: int = 12) -> C4Assessment:
        """Best passage for a claim. Passages are pre-ranked by the offline
        key-term score; the full backend chain and rules run on the top ``top_k``."""
        items: list[tuple[str, Optional[int]]] = [(p, None) if isinstance(p, str) else (p[0], p[1]) for p in passages]
        dec = decompose(claim).as_dict()
        if not items:
            return C4Assessment(None, 0.0, "unsupported", "none", {}, [], 0.0, decomposition=dec)
        ranked = sorted(items, key=lambda it: key_term_recall(claim, it[0])[0], reverse=True)[:max(1, top_k)]
        rank = {"supported": 2, "partial": 1, "unsupported": 0}
        best: Optional[C4Assessment] = None
        for text, page in ranked:
            a = self.assess(claim, text)
            a.page = page
            # prefer higher label; among equal labels the higher score; among unsupported prefer
            # the passage with the highest raw (pre-rule) score so the report shows why it failed
            key = (rank[a.label], a.score, a.raw_score)
            if best is None or key > (rank[best.label], best.score, best.raw_score):
                best = a
        best.decomposition = dec
        return best


# ==========================================================================
# Passage windows for fact claims
# ==========================================================================
_WIN_SENT = re.compile(r"(?<=[.!?])[\"'”)]?\s+(?=[A-Z0-9\"'“(])")


@lru_cache(maxsize=16)
def sentence_windows(text: str, max_sentences: int = 2, max_chars: int = 900) -> list[tuple[str, Optional[int]]]:
    """Sentence windows (1..max_sentences consecutive sentences) per page, so
    a claim is compared with whole sentences rather than layout lines. Returns
    (window, page) with page=None for unpaginated text."""
    from .extract import PAGE_SEP, split_pages
    if not text:
        return []
    pages = split_pages(text) if PAGE_SEP in text else [type("P", (), {"page": None, "text": text})()]
    out: list[tuple[str, Optional[int]]] = []
    seen: set[tuple[str, Optional[int]]] = set()
    for pg in pages:  # result is cached per text: callers must not mutate it
        flat = re.sub(r"\s+", " ", re.sub(r"(\w)-\n\s*(\w)", r"\1-\2", pg.text)).strip()
        sents = [s.strip() for s in _WIN_SENT.split(flat) if s.strip()]
        for i in range(len(sents)):
            for k in range(1, max_sentences + 1):
                if i + k > len(sents):
                    break
                w = " ".join(sents[i:i + k])
                if len(w) > max_chars and k > 1:
                    break
                key = (w, pg.page)
                if key not in seen:
                    seen.add(key)
                    out.append(key)
    return out


def iter_backend_names(backends: Iterable) -> list[str]:
    return [b.name for b in backends]
