"""Two-independent-upstream rule with aggregator detection (spec C6; CL-005, CL-006).

Independence test (v0.1): two sources are independent only if
  1. their registrable domains differ,
  2. their content hashes differ and their text is not a near-duplicate
     (rapidfuzz ratio below CONTENT_SIMILARITY_THRESHOLD), and
  3. their upstream termini differ (an aggregator must be traced to an
     original in T1-T3 before it counts; untraced aggregators never count).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Optional
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, NavigableString
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


# --------------------------------------------------------------------------
# Aggregator tracing (spec C6: follow citations to the original study/filing)
# --------------------------------------------------------------------------
#: hops the crawl-based tracer will follow from an aggregator page before giving up.
#: Spec C6 caps tracing depth at 3; v0.2 runs a stricter 2-hop guard because each
#: hop is a network fetch of an untrusted page.
MAX_TRACE_HOPS = 2

_ATTRIBUTION = re.compile(
    r"(?:\b(?:according to|study by|report by|research by|survey by|analysis by|published by|"
    r"data from|figures from|released by|findings from|cited by|per (?:a|an|the)|via)\b|\bsources?\s*:)",
    re.I,
)
_ORG_AFTER_ATTRIB = re.compile(
    r"(?:according to|study by|report by|research by|survey by|analysis by|published by|data from|figures from|released by|findings from)"
    r"\s+(?:a |an |the |new |recent |\d{4} )*([A-Z][\w&.'-]*(?:\s+(?:of|for|and|&|de)?\s*[A-Z][\w&.'-]*){0,5})",
    re.I,
)
_URL_IN_TEXT = re.compile(r"https?://[^\s<>()\[\]\"']+")
_ORIGINAL_HINT = re.compile(r"\b(report|study|paper|filing|survey|dataset|data|release|statement|working paper|bulletin|annual report|10-k|press release|pdf|full text|methodology)\b", re.I)
_SKIP_HOSTS = {
    "twitter.com", "x.com", "t.co", "facebook.com", "linkedin.com", "instagram.com", "youtube.com", "youtu.be",
    "reddit.com", "pinterest.com", "whatsapp.com", "tiktok.com", "threads.net", "mastodon.social", "bsky.app",
    "google.com", "apple.com", "play.google.com", "amzn.to", "amazon.com", "bit.ly", "tinyurl.com",
}
_SKIP_SCHEMES = ("mailto:", "javascript:", "tel:", "#", "data:")


@dataclass
class UpstreamCandidate:
    url: str
    score: float
    reasons: list[str] = field(default_factory=list)
    anchor: Optional[str] = None
    tier: Optional[Tier] = None
    attributed: bool = False  # found inside an "according to / source:" context

    @property
    def terminal(self) -> bool:
        """A candidate that can be a C6 terminus: not an aggregator and in T1-T3."""
        return not self.reasons_has("aggregator") and self.tier in (Tier.T1, Tier.T2, Tier.T3)

    def reasons_has(self, token: str) -> bool:
        return any(token in r for r in self.reasons)


@dataclass
class TraceCandidates:
    candidates: list[UpstreamCandidate] = field(default_factory=list)
    attributions: list[str] = field(default_factory=list)  # named orgs with no link ("according to Gartner")

    @property
    def urls(self) -> list[str]:
        return [c.url for c in self.candidates]


def _clean_url(href: str, base_url: str) -> Optional[str]:
    href = (href or "").strip()
    if not href or href.lower().startswith(_SKIP_SCHEMES):
        return None
    url = urljoin(base_url, href)
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, parts.query, ""))


def _is_skip_host(url: str) -> bool:
    reg = registrable_domain(url)
    host = host_of(url)
    return reg in _SKIP_HOSTS or host in _SKIP_HOSTS


def _score_candidate(url: str, anchor: str, context: str, rules, extra_aggregators) -> UpstreamCandidate:
    from .tier import assign_tier  # local import: tier imports nothing from upstream, but keep the graph flat

    c = UpstreamCandidate(url=url, score=0.2, anchor=anchor or None)
    c.tier = assign_tier(url, rules).tier
    window = f"{context} {anchor}"
    if _ATTRIBUTION.search(window):
        c.attributed = True
        c.score += 0.35
        c.reasons.append("attribution phrase in context")
    tier_bonus = {Tier.T1: 0.30, Tier.T2: 0.25, Tier.T3: 0.15, Tier.T4: 0.0, Tier.T5: -0.20}[c.tier]
    c.score += tier_bonus
    c.reasons.append(f"tier {c.tier.value}")
    if is_aggregator(url, extra_aggregators):
        c.score -= 0.30
        c.reasons.append("aggregator domain (must itself be traced)")
    path = urlsplit(url).path.lower()
    if path.endswith(".pdf") or "doi.org" in url or "arxiv.org" in url:
        c.score += 0.15
        c.reasons.append("primary-document URL shape (pdf/doi/arxiv)")
    if _ORIGINAL_HINT.search(anchor or ""):
        c.score += 0.10
        c.reasons.append("anchor names a report/study/filing")
    c.score = round(max(0.0, min(1.0, c.score)), 3)
    return c


def _anchor_contexts(soup, window: int = 100) -> dict[int, str]:
    """Text immediately preceding each <a> within its block, since the previous
    link or the block start. Keeps "according to <a>" attributed while a later
    link in the same paragraph ("and commentary at <a>") is not."""
    out: dict[int, str] = {}
    for block in soup.find_all(["p", "li", "td", "th", "blockquote", "figcaption", "h1", "h2", "h3", "dd", "div", "span"]):
        if block.find(["p", "li", "td", "blockquote", "div"]) is not None and block.name in ("div", "span"):
            continue  # container: its child blocks will be handled on their own
        buf: list[str] = []
        for node in block.descendants:
            if isinstance(node, NavigableString):
                if node.find_parent("a") is None:
                    buf.append(str(node))
            elif getattr(node, "name", None) == "a":
                out.setdefault(id(node), " ".join("".join(buf).split())[-window:])
                buf = []
    return out


def find_upstream_candidates(content: str, base_url: str, rules=None,
                             extra_aggregators: Iterable[str] = ()) -> TraceCandidates:
    """Scan an aggregator page (HTML or extracted text) for the original it
    summarises. Outbound links are ranked by attribution context ("according
    to", "source:", "study by"...), tier of the linked domain, primary-document
    URL shape and anchor wording. Same-domain, navigation, share and tracking
    links are excluded. Named attributions with no link are returned
    separately so a researcher can search for them."""
    base_reg = registrable_domain(base_url)
    found: dict[str, UpstreamCandidate] = {}
    text_for_attrib = content
    if re.search(r"<\s*(a|html|body|p|div)\b", content, re.I):
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "form"]):
            tag.decompose()
        text_for_attrib = soup.get_text(" ", strip=True)
        contexts = _anchor_contexts(soup)
        for a in soup.find_all("a", href=True):
            url = _clean_url(a["href"], base_url)
            if not url or registrable_domain(url) == base_reg or _is_skip_host(url):
                continue
            rel = " ".join(a.get("rel") or [])
            if "nofollow" in rel and "sponsored" in rel:
                continue
            anchor = a.get_text(" ", strip=True)
            cand = _score_candidate(url, anchor, contexts.get(id(a), ""), rules, extra_aggregators)
            prev = found.get(url)
            if prev is None or cand.score > prev.score:
                found[url] = cand
    # plain URLs in text (covers text_extract input and unlinked URLs)
    for m_ in _URL_IN_TEXT.finditer(text_for_attrib if isinstance(text_for_attrib, str) else ""):
        url = _clean_url(m_.group(0).rstrip(".,;:"), base_url)
        if not url or url in found or registrable_domain(url) == base_reg or _is_skip_host(url):
            continue
        context = text_for_attrib[max(0, m_.start() - 160): m_.start()]
        found[url] = _score_candidate(url, "", context, rules, extra_aggregators)
    attributions: list[str] = []
    for m_ in _ORG_AFTER_ATTRIB.finditer(text_for_attrib or ""):
        org = m_.group(1).strip(" .,;:")
        if org and org[0].isupper() and org not in attributions and len(org) > 2:
            attributions.append(org)
    ranked = sorted(found.values(), key=lambda c: (-c.score, c.url))
    return TraceCandidates(candidates=ranked, attributions=attributions)


@dataclass
class TraceResult:
    terminus: Optional[str]
    path: list[str] = field(default_factory=list)  # pages visited, starting with the aggregator
    hops: int = 0
    candidates: list[UpstreamCandidate] = field(default_factory=list)  # ranked candidates from the first page
    attributions: list[str] = field(default_factory=list)
    reason: Optional[str] = None

    @property
    def traced(self) -> bool:
        return self.terminus is not None


def trace_upstream(source: Source, html: Optional[str] = None, page_loader=None, max_hops: int = MAX_TRACE_HOPS,
                   rules=None, extra_aggregators: Iterable[str] = ()) -> TraceResult:
    """Crawl-based aggregator tracing (spec C6). Starting from the aggregator
    page's HTML (or its text extract), rank outbound candidates; accept the
    best candidate that is a valid terminus (non-aggregator, T1-T3). If none
    is terminal, follow the top candidate using ``page_loader(url) -> str|None``
    and repeat, never exceeding ``max_hops`` fetches (guard against aggregator
    chains and link farms). Without a ``page_loader`` only the first page is
    inspected. The terminus returned here is a *candidate*: the pipeline must
    still FETCH and hash it before it becomes the citation of record."""
    start_url = source.url_final or source.url
    content = html or source.text_extract or ""
    result = TraceResult(terminus=None, path=[start_url])
    if not content:
        result.reason = "no content to trace"
        return result
    current_url = start_url
    visited = {registrable_domain(start_url)}
    for hop in range(1, max_hops + 1):
        tc = find_upstream_candidates(content, current_url, rules, extra_aggregators)
        if hop == 1:
            result.candidates, result.attributions = tc.candidates, tc.attributions
        fresh = [c for c in tc.candidates if registrable_domain(c.url) not in visited]
        if not fresh:
            result.reason = f"no outbound candidates on hop {hop}"
            return result
        terminal = [c for c in fresh if c.terminal]
        if terminal:
            result.terminus, result.hops = terminal[0].url, hop
            result.path.append(terminal[0].url)
            return result
        if hop == max_hops or page_loader is None:
            result.reason = (f"best candidate {fresh[0].url} is not a T1-T3 original and max_hops={max_hops} reached"
                             if page_loader is not None else
                             f"best candidate {fresh[0].url} is not a T1-T3 original; no page_loader to follow it")
            return result
        # follow the most promising lead: attributed links first (an aggregator that names its
        # source beats an unattributed vendor page), then score
        nxt = sorted(fresh, key=lambda c: (not c.attributed, -c.score, c.url))[0]
        content = page_loader(nxt.url) or ""
        result.path.append(nxt.url)
        result.hops = hop
        visited.add(registrable_domain(nxt.url))
        current_url = nxt.url
        if not content:
            result.reason = f"hop {hop}: could not load {nxt.url}"
            return result
    result.reason = f"max_hops={max_hops} reached"  # pragma: no cover (loop returns earlier)
    return result


def trace_to_original(source: Source, resolver=None, depth_cap: int = TRACE_DEPTH_CAP, *,
                      html: Optional[str] = None, page_loader=None, max_hops: int = MAX_TRACE_HOPS,
                      rules=None, extra_aggregators: Iterable[str] = ()) -> Optional[str]:
    """Upstream terminus of a source (spec C6).

    1. A declared ``upstream_of`` (by the researcher or an upstream tool) wins;
       an optional ``resolver(url) -> Optional[str]`` walks further declared
       hops up to ``depth_cap``.
    2. Otherwise, when ``html`` or ``page_loader`` is supplied, the crawl-based
       tracer (:func:`trace_upstream`) ranks outbound links and attribution
       patterns with a ``max_hops`` guard (default 2).
    3. Otherwise None: untraced aggregators never count towards independence.
    """
    if source.upstream_of:
        terminus: Optional[str] = source.upstream_of[0]
        if terminus and resolver is not None:
            hops = 0
            nxt = resolver(terminus)
            while nxt and hops < depth_cap - 1:
                terminus, nxt, hops = nxt, resolver(nxt), hops + 1
        return terminus
    if html is None and page_loader is None:
        return None
    return trace_upstream(source, html=html, page_loader=page_loader, max_hops=max_hops,
                          rules=rules, extra_aggregators=extra_aggregators).terminus


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
