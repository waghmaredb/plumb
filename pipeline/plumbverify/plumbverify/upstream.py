"""Two-independent-upstream rule with aggregator detection (spec C6; CL-005, CL-006).

Independence test (v0.1): two sources are independent only if
  1. their registrable domains differ,
  2. their content hashes differ and their text is not a near-duplicate
     (rapidfuzz ratio below CONTENT_SIMILARITY_THRESHOLD), and
  3. their upstream termini differ (an aggregator must be traced to an
     original in T1-T3 before it counts; untraced aggregators never count).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional
from urllib.parse import urlsplit

from rapidfuzz import fuzz

from .models import Source, Tier, UpstreamPair

CONTENT_SIMILARITY_THRESHOLD = 0.90
TRACE_DEPTH_CAP = 3

# Known aggregators / secondary summarisers (spec C6: statista, wikipedia, press-release wires,
# market-report mills). Extend via `extra_aggregators` on the functions below.
AGGREGATOR_DOMAINS: set[str] = {
    "statista.com", "wikipedia.org", "wikimedia.org", "wikidata.org",
    "prnewswire.com", "businesswire.com", "globenewswire.com", "prweb.com", "einpresswire.com",
    "newswire.ca", "accesswire.com", "marketwatch.com/press-release",
    "marketsandmarkets.com", "grandviewresearch.com", "mordorintelligence.com",
    "fortunebusinessinsights.com", "reportlinker.com", "researchandmarkets.com",
    "alliedmarketresearch.com", "precedenceresearch.com", "verifiedmarketresearch.com",
    "mintel.com", "euromonitor.com", "knoema.com", "tradingeconomics.com", "macrotrends.net",
}

# Common second-level public suffixes (good-enough replacement for a PSL lookup).
_CC_SLD = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "gov.au", "edu.au",
    "com.sg", "gov.sg", "edu.sg", "org.sg", "net.sg", "co.jp", "or.jp", "ne.jp", "go.jp", "ac.jp",
    "com.hk", "gov.hk", "edu.hk", "co.in", "gov.in", "ac.in", "co.nz", "govt.nz", "com.my", "gov.my",
    "co.kr", "or.kr", "go.kr", "com.cn", "gov.cn", "edu.cn", "com.br", "gov.br", "co.za", "gov.za",
    "com.tw", "gov.tw", "co.id", "go.id", "com.ph", "gov.ph", "com.vn", "gov.vn", "co.th", "go.th",
}


def host_of(url: str) -> str:
    try:
        host = urlsplit(url if "://" in url else f"https://{url}").hostname or ""
    except Exception:
        return ""
    return host.lower().rstrip(".")


def registrable_domain(url_or_host: str) -> str:
    host = host_of(url_or_host) if "/" in url_or_host or "://" in url_or_host else url_or_host.lower()
    labels = host.split(".")
    if len(labels) <= 2:
        return host
    if ".".join(labels[-2:]) in _CC_SLD:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def is_aggregator(url: str, extra_aggregators: Iterable[str] = ()) -> bool:
    host = host_of(url)
    reg = registrable_domain(url)
    path = urlsplit(url).path.lower() if "://" in url else ""
    for agg in set(AGGREGATOR_DOMAINS) | set(extra_aggregators):
        agg = agg.lower()
        if "/" in agg:  # host/path-prefix form, e.g. marketwatch.com/press-release
            ah, ap = agg.split("/", 1)
            if (host == ah or host.endswith("." + ah)) and path.startswith("/" + ap):
                return True
        elif host == agg or host.endswith("." + agg) or reg == agg:
            return True
    return False


def trace_to_original(source: Source, resolver=None, depth_cap: int = TRACE_DEPTH_CAP) -> Optional[str]:
    """PLACEHOLDER for aggregator tracing (spec C6: follow citations in an
    aggregator page to the original study/filing, max 3 hops, terminus must be
    FETCHED and hashed and sit in T1-T3).

    v0.1 behaviour: returns the first declared `upstream_of` URL if present
    (declared by the researcher or an upstream tool), otherwise None. A
    `resolver(url) -> Optional[str]` callable may be supplied to walk hops.
    """
    terminus: Optional[str] = source.upstream_of[0] if source.upstream_of else None
    if terminus and resolver is not None:
        hops = 0
        nxt = resolver(terminus)
        while nxt and hops < depth_cap - 1:
            terminus, nxt, hops = nxt, resolver(nxt), hops + 1
    return terminus


def terminus_of(source: Source, extra_aggregators: Iterable[str] = ()) -> Optional[str]:
    """Upstream terminus used for the independence test. Non-aggregator T1-T3
    sources are their own terminus; aggregators (and T4/T5 secondary
    summaries) must be traced, else None (cannot count)."""
    traced = trace_to_original(source)
    if traced:
        return traced
    url = source.url_final or source.url
    if is_aggregator(url, extra_aggregators) or source.tier in (Tier.T5,):
        return None
    return url


def content_similarity(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    return fuzz.ratio(a[:20000], b[:20000]) / 100.0


@dataclass
class IndependenceResult:
    independent: bool
    reasons: list[str] = field(default_factory=list)
    similarity: float = 0.0


def independence(a: Source, b: Source, similarity_threshold: float = CONTENT_SIMILARITY_THRESHOLD,
                 extra_aggregators: Iterable[str] = ()) -> IndependenceResult:
    reasons: list[str] = []
    ua, ub = a.url_final or a.url, b.url_final or b.url
    ta, tb = terminus_of(a, extra_aggregators), terminus_of(b, extra_aggregators)
    if ta is None:
        reasons.append(f"{ua}: aggregator/T5 not traced to an original (C6)")
    if tb is None:
        reasons.append(f"{ub}: aggregator/T5 not traced to an original (C6)")
    if ta and tb and registrable_domain(ta) == registrable_domain(tb):
        reasons.append(f"same upstream terminus domain: {registrable_domain(ta)}")
    if registrable_domain(ua) == registrable_domain(ub):
        reasons.append(f"same registrable domain: {registrable_domain(ua)}")
    if a.sha256 and b.sha256 and a.sha256 == b.sha256:
        reasons.append("identical content hash")
    sim = content_similarity(a.text_extract, b.text_extract)
    if sim >= similarity_threshold:
        reasons.append(f"near-duplicate content (ratio {sim:.2f} >= {similarity_threshold})")
    return IndependenceResult(independent=not reasons, reasons=reasons, similarity=sim)


@dataclass
class UpstreamCount:
    count: int
    accepted: list[str]
    pairs: list[UpstreamPair]


def count_independent_upstreams(sources: list[Source], **kw) -> UpstreamCount:
    """Greedy: accept a source if it is independent of every already-accepted
    source. Returns the count, accepted URLs and all pairwise results."""
    accepted: list[Source] = []
    pairs: list[UpstreamPair] = []
    for s in sources:
        if terminus_of(s, kw.get("extra_aggregators", ())) is None:
            pairs.append(UpstreamPair(a=s.url, b=s.url, independent=False,
                                      reasons=["aggregator/T5 not traced to an original (C6)"]))
            continue
        ok = True
        for acc in accepted:
            r = independence(acc, s, **kw)
            pairs.append(UpstreamPair(a=acc.url, b=s.url, independent=r.independent, reasons=r.reasons))
            ok = ok and r.independent
        if ok:
            accepted.append(s)
    return UpstreamCount(count=len(accepted), accepted=[s.url for s in accepted], pairs=pairs)
