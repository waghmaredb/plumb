"""Job-postings module: AI-skill share of postings over a 24-month window,
with peer comparison (instrument D4.1 primary; D2.2, D3.2, D4.5, D6.2 by
sub-lexicon).

Method (Babina, Fedyk, He & Hodson, NBER, instrument source P1): a posting is
AI-related when its required skills include AI terms; the firm-level measure
is the share of AI-related postings in all postings. P1 validates the share
against sales, employment and market value. This module keeps the same
numerator/denominator and extends the skill lexicon with LLM/GenAI and
MLOps/LLMOps terms (2023+), grouped so sub-shares can feed the instrument's
other posting proxies.

A ``PostingsSource`` supplies postings; ``CsvPostingsSource`` is the fixture
and offline implementation (and the natural landing format for a metered
scraping export). ``MyCareersFutureSource`` and ``LinkedInJobsSource`` are
interface stubs: no live collection is implemented here.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Protocol

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import PeerRole, Subject

MODULE = "postings"
WINDOW_MONTHS = 24
MAX_EXEMPLARS = 5  # exemplar postings fetched for verification (bounded by the C10 cap)

# --------------------------------------------------------------------------
# Skill lexicon (word-boundary regexes; case-insensitive unless noted)
# --------------------------------------------------------------------------
LEXICON: dict[str, list[str]] = {
    # Babina et al. core: machine learning / AI / NLP / computer vision skills
    "ml": [r"machine[- ]learning", r"deep[- ]learning", r"neural networks?", r"artificial intelligence", r"\bAI\b", r"\bML\b",
           r"natural language processing", r"\bNLP\b", r"computer vision", r"reinforcement learning", r"predictive model",
           r"recommendation (?:system|engine)", r"scikit-learn", r"\bsklearn\b", r"tensorflow", r"pytorch", r"keras", r"xgboost",
           r"data scien(?:ce|tist)", r"feature engineering", r"model (?:training|development|validation)"],
    # LLM / generative AI (2023+ extension)
    "llm": [r"large language models?", r"\bLLMs?\b", r"generative ai", r"gen[- ]?ai", r"prompt engineering", r"\bRAG\b",
            r"retrieval[- ]augmented", r"vector (?:database|store|search)", r"embeddings?", r"langchain", r"llamaindex",
            r"\bopenai\b", r"\bgpt-?\d", r"anthropic", r"claude", r"gemini", r"copilot", r"agentic", r"ai agents?",
            r"fine[- ]tun(?:e|ing)", r"transformers?", r"hugging ?face", r"foundation models?"],
    # MLOps / LLMOps / platform
    "mlops": [r"mlops", r"llmops", r"model (?:deployment|serving|monitoring|registry|governance)", r"mlflow", r"kubeflow",
              r"sagemaker", r"vertex ai", r"azure (?:ml|machine learning|openai)", r"databricks", r"feature store",
              r"model drift", r"\bevaluation (?:suite|framework|pipeline)s?\b", r"observability", r"ci/cd for (?:ml|models)"],
    # Data engineering (feeds D2.2 / D2.3)
    "data_eng": [r"data engineer", r"data pipelines?", r"\bETL\b", r"\bELT\b", r"data warehouse", r"data lake(?:house)?",
                 r"spark", r"pyspark", r"airflow", r"dbt\b", r"snowflake", r"bigquery", r"kafka", r"data quality", r"data steward",
                 r"data governance", r"data catalog(?:ue)?", r"data lineage", r"master data"],
    # AI governance / model risk (feeds D6.2)
    "ai_governance": [r"responsible ai", r"ai governance", r"model risk", r"ai risk", r"ai ethics", r"fairness", r"explainab",
                      r"ai assurance", r"model validation", r"\bFEAT\b", r"ISO(?:/IEC)? 42001", r"ai policy"],
    # AI product / translator roles (feeds D4.5)
    "ai_product": [r"ai product (?:manager|owner|lead)", r"analytics translator", r"product manager[^.]{0,40}\b(?:ai|ml|data)\b",
                   r"head of (?:ai|data|analytics)"],
}
_COMPILED = {k: re.compile("|".join(f"(?:{p})" for p in v), re.I) for k, v in LEXICON.items()}
# the bare acronyms are case-sensitive to avoid 'ai' inside ordinary words
_ACRONYMS = re.compile(r"\b(?:AI|ML|NLP|LLMs?|RAG|ETL|ELT|FEAT)\b")

AI_GROUPS = ("ml", "llm", "mlops", "ai_governance", "ai_product")  # groups that make a posting "AI-related"


@dataclass
class Posting:
    id: str
    company: str
    title: str
    description: str
    posted_at: date
    url: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None  # mycareersfuture | linkedin | careers-site | fixture


@dataclass
class PostingTag:
    ai_related: bool
    groups: dict[str, list[str]] = field(default_factory=dict)  # group -> matched terms


def tag_posting(p: Posting) -> PostingTag:
    text = f"{p.title}\n{p.description}"
    groups: dict[str, list[str]] = {}
    for g, rx in _COMPILED.items():
        hits = []
        for m in rx.finditer(text):
            tok = m.group(0)
            # acronym hits must be upper-case in the original text
            if tok.upper() in ("AI", "ML", "NLP", "LLM", "LLMS", "RAG", "ETL", "ELT", "FEAT") and not _ACRONYMS.search(tok):
                continue
            hits.append(tok)
        if hits:
            groups[g] = sorted(set(hits), key=str.lower)
    return PostingTag(ai_related=any(g in groups for g in AI_GROUPS), groups=groups)


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------
class PostingsSource(Protocol):
    def postings(self, company_patterns: Iterable[str], since: date, until: date) -> list[Posting]: ...


class CsvPostingsSource:
    """CSV columns: id, company, title, description, posted_at (YYYY-MM-DD), url, location, source."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def postings(self, company_patterns: Iterable[str], since: date, until: date) -> list[Posting]:
        pats = [p.lower() for p in company_patterns]
        out: list[Posting] = []
        if not self.path.exists():
            return out
        with self.path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                try:
                    d = date.fromisoformat(row["posted_at"][:10])
                except Exception:
                    continue
                if not (since <= d <= until):
                    continue
                if pats and not any(p in (row.get("company") or "").lower() for p in pats):
                    continue
                out.append(Posting(id=row.get("id") or f"{row['company']}-{d.isoformat()}-{len(out)}", company=row["company"],
                                   title=row.get("title", ""), description=row.get("description", ""), posted_at=d,
                                   url=row.get("url") or None, location=row.get("location") or None, source=row.get("source") or "csv"))
        return out


class MyCareersFutureSource:
    """STUB. Singapore's MyCareersFuture portal exposes a JSON search endpoint
    used by its web app; terms of use and rate limits must be checked before
    production use (alpha-targets §4 budgets this under metered scraping).
    Not implemented: raises so a run never silently returns zero postings."""

    def __init__(self, client=None):
        self.client = client

    def postings(self, company_patterns: Iterable[str], since: date, until: date) -> list[Posting]:
        raise NotImplementedError("MyCareersFutureSource: live collection not implemented; export to CSV and use CsvPostingsSource")


class LinkedInJobsSource:
    """STUB. LinkedIn Jobs requires a licensed data provider (data annex). Not implemented."""

    def postings(self, company_patterns: Iterable[str], since: date, until: date) -> list[Posting]:
        raise NotImplementedError("LinkedInJobsSource: requires a licensed provider export; use CsvPostingsSource")


# --------------------------------------------------------------------------
# Share computation
# --------------------------------------------------------------------------
@dataclass
class ShareResult:
    company: str
    total: int
    ai: int
    share: Optional[float]  # 0-1, None when total == 0
    by_group: dict[str, int]
    monthly: dict[str, tuple[int, int]]  # YYYY-MM -> (ai, total)
    first_half_share: Optional[float]
    second_half_share: Optional[float]
    window_start: date
    window_end: date


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def months_back(d: date, n: int) -> date:
    y, m = d.year, d.month - n
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, 1)


def compute_share(postings: list[Posting], as_of: date, window_months: int = WINDOW_MONTHS, company: str = "") -> ShareResult:
    start = months_back(as_of, window_months - 1)
    mid = months_back(as_of, window_months // 2 - 1)
    monthly: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    by_group: dict[str, int] = defaultdict(int)
    total = ai = 0
    h1 = [0, 0]
    h2 = [0, 0]
    for p in postings:
        if not (start <= p.posted_at <= as_of):
            continue
        t = tag_posting(p)
        total += 1
        monthly[month_key(p.posted_at)][1] += 1
        bucket = h2 if p.posted_at >= mid else h1
        bucket[1] += 1
        if t.ai_related:
            ai += 1
            monthly[month_key(p.posted_at)][0] += 1
            bucket[0] += 1
        for g in t.groups:
            by_group[g] += 1
    return ShareResult(company=company, total=total, ai=ai, share=(ai / total) if total else None, by_group=dict(by_group),
                       monthly={k: (v[0], v[1]) for k, v in sorted(monthly.items())},
                       first_half_share=(h1[0] / h1[1]) if h1[1] else None, second_half_share=(h2[0] / h2[1]) if h2[1] else None,
                       window_start=start, window_end=as_of)


def percentile_rank(value: float, peers: list[float]) -> Optional[float]:
    """Share of peer values at or below `value`, in percent. None without peers."""
    if not peers:
        return None
    return round(100.0 * sum(1 for v in peers if v <= value) / len(peers), 1)


# --------------------------------------------------------------------------
# Module entry point
# --------------------------------------------------------------------------
def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None,
        source: Optional[PostingsSource] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    source = source or CsvPostingsSource(ctx.subject_dir / "postings.csv")
    gaps: list[Gap] = []
    cp = ctx.checkpoint(MODULE)
    as_of = ctx.as_of
    since = months_back(as_of, WINDOW_MONTHS - 1)

    if not cp.has("_shares"):
        try:
            ctx.charge(MODULE, "postings_source", source=type(source).__name__, since=str(since), until=str(as_of))
            subj_posts = source.postings(subject.patterns(), since, as_of)
            peer_posts: dict[str, list[Posting]] = {}
            for peer in subject.peers_by_role(PeerRole.core):
                pats = peer.name_patterns or [peer.name]
                peer_posts[peer.name] = source.postings(pats, since, as_of)
        except NotImplementedError as e:
            gaps.append(Gap(module=MODULE, topic="postings source", detail=str(e), instrument_items=["D4.1"]))
            return ModuleResult(module=MODULE, subject_slug=subject.slug, gaps=gaps, data_available=False, tool_calls=ctx.budget(MODULE).calls)
        subj = compute_share(subj_posts, as_of, company=subject.short_name)
        peers = {n: compute_share(pl, as_of, company=n) for n, pl in peer_posts.items()}
        exemplars = []
        for p in sorted(subj_posts, key=lambda p: p.posted_at, reverse=True):
            t = tag_posting(p)
            if t.ai_related and p.url:
                exemplars.append({"id": p.id, "title": p.title, "url": p.url, "posted_at": p.posted_at.isoformat(),
                                  "groups": t.groups})
            if len(exemplars) >= MAX_EXEMPLARS:
                break
        cp.put("_shares", {"subject": _share_dict(subj), "peers": {n: _share_dict(s) for n, s in peers.items()}, "exemplars": exemplars})
    shares = cp.get("_shares")

    # exemplar postings: fetched one per work item so a cap hit resumes cleanly
    claims: list[ResearchClaim] = []
    for ex in shares["exemplars"]:
        key = f"ex:{ex['id']}"
        if cp.has(key):
            claims.extend(ResearchClaim.model_validate(c) for c in cp.get(key)["claims"])
            continue
        src = ctx.fetch(MODULE, ex["url"])
        tier = src.tier
        c = ResearchClaim(id=f"{subject.slug}.postings.{ex['id']}", module=MODULE, text=ex["title"], kind=ClaimKind.fact,
                          load_bearing=False, sources=[ex["url"]], passage=ex["title"], tier=tier,
                          confidence_label=confidence_for_tier(tier), instrument_items=["D4.1"],
                          signal_ids=[f"{subject.slug}.postings.share"], period=ex["posted_at"],
                          note="AI-related posting; matched terms: " + "; ".join(f"{g}: {', '.join(v)}" for g, v in ex["groups"].items()))
        cp.put(key, {"claims": [c.model_dump(mode="json")]})
        claims.append(c)

    subj = shares["subject"]
    peer_shares = {n: s["share"] for n, s in shares["peers"].items() if s["share"] is not None}
    pct = percentile_rank(subj["share"], list(peer_shares.values())) if subj["share"] is not None else None
    src_desc = f"{type(source).__name__} ({getattr(source, 'path', '')})" if hasattr(source, "path") else type(source).__name__
    signals = [
        Signal(id=f"{subject.slug}.postings.share", module=MODULE, name="AI-skill share of job postings (24 months)",
               instrument_items=["D4.1"], value=round(subj["share"] * 100, 1) if subj["share"] is not None else None, unit="%",
               source=src_desc, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims],
               detail={"ai": subj["ai"], "total": subj["total"], "window": [subj["window_start"], subj["window_end"]],
                       "first_12m_share": subj["first_half_share"], "last_12m_share": subj["second_half_share"],
                       "by_group": subj["by_group"], "monthly": subj["monthly"]},
               note="Babina et al. method; numerator = postings matching the AI lexicon (ml/llm/mlops/ai_governance/ai_product)"),
        Signal(id=f"{subject.slug}.postings.peer_percentile", module=MODULE, name="AI-skill share: percentile vs core peers",
               instrument_items=["D4.1"], value=pct, unit="percentile", source=src_desc, confidence_label=ConfidenceLabel.model_inferred,
               detail={"peer_shares": {n: round(v * 100, 1) for n, v in peer_shares.items()}, "peer_n": len(peer_shares)},
               note="peer n below the instrument's 15 threshold: directional only" if len(peer_shares) < 15 else None),
    ]
    for g, items in (("data_eng", ["D2.2", "D2.3"]), ("mlops", ["D3.2"]), ("ai_product", ["D4.5"]), ("ai_governance", ["D6.2"]), ("llm", ["D3.1"])):
        n = subj["by_group"].get(g, 0)
        signals.append(Signal(id=f"{subject.slug}.postings.{g}", module=MODULE, name=f"Postings mentioning {g} skills (24 months)",
                              instrument_items=items, value=n, unit="postings", source=src_desc,
                              confidence_label=ConfidenceLabel.model_inferred,
                              detail={"share_of_all": round(n / subj["total"], 3) if subj["total"] else None}))
    if subj["total"] == 0:
        gaps.append(Gap(module=MODULE, topic="no postings in window", detail=f"no postings for {subject.patterns()} between {since} and {as_of} in {src_desc}; "
                        "alpha-targets §6 item 5: 24-month posting series not yet collected", instrument_items=["D4.1"], verify_flag=True))
    if subj["total"] and subj["total"] < 30:
        gaps.append(Gap(module=MODULE, topic="thin posting sample", detail=f"only {subj['total']} postings in window; share is noisy", instrument_items=["D4.1"]))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        data_available=subj["total"] > 0, tool_calls=ctx.budget(MODULE).calls,
                        detail={"subject": subj, "peers": shares["peers"]})


def _share_dict(s: ShareResult) -> dict:
    return {"company": s.company, "total": s.total, "ai": s.ai, "share": s.share, "by_group": s.by_group,
            "monthly": {k: list(v) for k, v in s.monthly.items()}, "first_half_share": s.first_half_share,
            "second_half_share": s.second_half_share, "window_start": s.window_start.isoformat(), "window_end": s.window_end.isoformat()}
