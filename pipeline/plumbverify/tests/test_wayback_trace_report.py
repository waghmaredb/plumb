"""WaybackArchive (C2), crawl-based upstream tracing (C6) and the reviewer
Markdown report with the 6.2 sampling worksheet (C16). All offline."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

from plumbverify.cli import main
from plumbverify.fetch import RECHECK_WINDOW, ArchiveSnapshot, Fetcher, WaybackArchive, recheck_deadline
from plumbverify.models import (
    Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, ConfidenceLabel, HealthClass, Source,
    SourceState, Tier, VerificationReport,
)
from plumbverify.report import build_sample, render_markdown
from plumbverify.tier import load_tier_rules
from plumbverify.upstream import (
    MAX_TRACE_HOPS, count_independent_upstreams, find_upstream_candidates, terminus_of, trace_to_original,
    trace_upstream,
)

from .conftest import AGGREGATOR_HTML, FIXTURES

NOW = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
FRESH_TS = "20260901000000"
STALE_TS = "20230101000000"  # > 24 months before NOW


# ---------------------------------------------------------------------------
# Wayback
# ---------------------------------------------------------------------------
class _Wayback:
    def __init__(self):
        self.calls: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(f"{request.method} {request.url}")
        host, path = request.url.host, request.url.path
        if host == "archive.org" and path == "/wayback/available":
            target = request.url.params.get("url", "")
            if "dead-but-archived" in target:
                return httpx.Response(200, json={"url": target, "archived_snapshots": {"closest": {
                    "available": True, "status": "200", "timestamp": FRESH_TS,
                    "url": f"http://web.archive.org/web/{FRESH_TS}/{target}"}}})
            if "stale" in target:
                return httpx.Response(200, json={"archived_snapshots": {"closest": {
                    "available": True, "status": "200", "timestamp": STALE_TS,
                    "url": f"http://web.archive.org/web/{STALE_TS}/{target}"}}})
            if "api-down" in target:
                return httpx.Response(503)
            return httpx.Response(200, json={"url": target, "archived_snapshots": {}})
        if host == "web.archive.org" and path.startswith("/save/"):
            target = str(request.url)[len("https://web.archive.org/save/"):]
            if "unsaveable" in target:
                return httpx.Response(429)
            return httpx.Response(200, headers={"content-location": f"/web/20261025120000/{target}"}, content=b"ok")
        if host == "web.archive.org" and path.startswith("/web/"):
            return httpx.Response(200, headers={"content-type": "text/html"},
                                  content=b"<html><body><p>archived copy with the A$440,000 figure</p></body></html>")
        return httpx.Response(404)


@pytest.fixture
def wb():
    return _Wayback()


@pytest.fixture
def wb_client(wb):
    return httpx.Client(transport=httpx.MockTransport(wb), follow_redirects=True)


def test_wayback_lookup_available_within_24_months(wb_client):
    arch = WaybackArchive(client=wb_client, now=lambda: NOW)
    snap = arch.lookup("https://old.example.org/dead-but-archived")
    assert snap is not None and snap.archive_url.startswith("http://web.archive.org/web/" + FRESH_TS)
    assert snap.timestamp == datetime(2026, 9, 1, tzinfo=timezone.utc)
    assert snap.recheck_after == NOW + timedelta(hours=24) and not snap.saved_now


def test_wayback_lookup_rejects_stale_missing_and_api_errors(wb_client):
    arch = WaybackArchive(client=wb_client, now=lambda: NOW)
    assert arch.lookup("https://old.example.org/stale") is None and "24 months" in arch.last_error
    assert arch.lookup("https://old.example.org/nothing") is None and arch.last_error == "no snapshot available"
    assert arch.lookup("https://old.example.org/api-down") is None and "availability" in arch.last_error


def test_wayback_save_is_opt_in(wb, wb_client):
    off = WaybackArchive(client=wb_client, now=lambda: NOW)  # default: no save
    assert off.lookup("https://old.example.org/nothing") is None
    assert not any("/save/" in c for c in wb.calls)
    on = WaybackArchive(client=wb_client, now=lambda: NOW, save_missing=True)
    snap = on.lookup("https://old.example.org/nothing")
    assert snap is not None and snap.saved_now
    assert snap.archive_url == "https://web.archive.org/web/20261025120000/https://old.example.org/nothing"
    assert snap.timestamp == datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
    assert any("/save/" in c for c in wb.calls)
    assert on.save("https://old.example.org/unsaveable") is None and "429" in on.last_error


def test_recheck_rule_is_24h_and_set_on_live_and_archived(wb_client, mock_client, store):
    assert RECHECK_WINDOW == timedelta(hours=24)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert recheck_deadline(t0) == t0 + timedelta(hours=24)
    live = Fetcher(store=store, client=mock_client, sleep=lambda s: None).check_health("https://www.example-press.org/report")
    assert live.health_class == HealthClass.LIVE and live.recheck_after is not None
    dead = Fetcher(store=store, client=mock_client, sleep=lambda s: None).check_health("https://www.example-press.org/missing")
    assert dead.recheck_after is None


def test_fetcher_uses_wayback_for_dead_url(wb, wb_client, store):
    """Primary transport 404s; the Wayback transport answers both the availability API and the snapshot GET."""
    def primary(request: httpx.Request) -> httpx.Response:
        if request.url.host == "web.archive.org" or request.url.host == "archive.org":
            return wb(request)
        return httpx.Response(404)
    client = httpx.Client(transport=httpx.MockTransport(primary), follow_redirects=True)
    arch = WaybackArchive(client=client, now=lambda: NOW)
    f = Fetcher(store=store, client=client, archive=arch, sleep=lambda s: None)
    src = f.fetch("https://old.example.org/dead-but-archived")
    assert src.state == SourceState.ARCHIVED and src.citable and src.archived_url and src.sha256
    assert src.recheck_after == NOW + timedelta(hours=24)
    assert "A$440,000" in src.text_extract


def test_cli_archive_flags_build_wayback(monkeypatch):
    import plumbverify.cli as cli
    built = {}

    class _Spy(WaybackArchive):
        def __init__(self, **kw):
            built.update(kw)
            super().__init__(client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404))), **kw)

    monkeypatch.setattr(cli, "WaybackArchive", _Spy)
    monkeypatch.setattr(cli, "Fetcher", lambda **kw: type("F", (), {"check_health": lambda self, u: Fetcher(
        client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404)))).check_health(u)})())
    main(["check-url", "https://x.example/page", "--archive-save"])
    assert built == {"save_missing": True}
    built.clear()
    main(["check-url", "https://x.example/page", "--archive"])
    assert built == {"save_missing": False}


# ---------------------------------------------------------------------------
# Upstream tracing
# ---------------------------------------------------------------------------
AGG_URL = "https://www.statista.com/statistics/1/"
HOP2_HTML = (FIXTURES / "aggregator_hop2.html").read_text(encoding="utf-8")


def test_find_upstream_candidates_ranks_attributed_primary_sources_first():
    tc = find_upstream_candidates(AGGREGATOR_HTML, AGG_URL)
    urls = tc.urls
    # attributed T1 links first, then press, then vendor blog, then the aggregator (wikipedia) last
    assert urls[:2] == ["https://arxiv.org/abs/2604.03173",
                        "https://www.example-university.edu/reports/citation-audit-2026.pdf"]
    assert urls.index("https://fortune.com/2025/10/07/deloitte-ai-australia") < urls.index("https://www.someco.com/blog/why-our-tool-wins")
    assert urls[-1].startswith("https://en.wikipedia.org/")
    assert tc.candidates[0].attributed and tc.candidates[0].tier == Tier.T1 and tc.candidates[0].terminal
    assert not tc.candidates[-1].terminal
    # same-domain, nav, share and affiliate links are excluded
    assert not any("statista.com" in u or "twitter.com" in u or "linkedin.com" in u or "facebook.com" in u
                   or "amzn.to" in u for u in urls)
    # unlinked attribution surfaced for the researcher
    assert "Gartner Research" in tc.attributions


def test_find_upstream_candidates_from_plain_text_extract():
    text = ("Market size reached US$3.2bn according to https://www.mas.gov.sg/publications/report-2025.pdf "
            "and a vendor post at https://www.someco.com/blog/x. Share: https://twitter.com/x")
    tc = find_upstream_candidates(text, AGG_URL)
    assert tc.urls[0] == "https://www.mas.gov.sg/publications/report-2025.pdf" and tc.candidates[0].attributed
    assert "https://twitter.com/x" not in tc.urls


def test_trace_to_original_one_hop_from_html():
    src = Source(url=AGG_URL, tier=Tier.T5, state=SourceState.FETCHED, health_class=HealthClass.LIVE, sha256="x")
    assert trace_to_original(src) is None  # no html, no loader: untraced (back-compat)
    assert trace_to_original(src, html=AGGREGATOR_HTML) == "https://arxiv.org/abs/2604.03173"
    tr = trace_upstream(src, html=AGGREGATOR_HTML)
    assert tr.traced and tr.hops == 1 and tr.path == [AGG_URL, "https://arxiv.org/abs/2604.03173"]


def test_trace_to_original_follows_second_hop_and_stops_at_max_hops():
    # hop 1 page links only to another aggregator (statista) and a vendor blog; hop 2 reaches MAS (T1)
    hop1 = """<html><body><main><p>Figures from <a href="https://www.researchandmarkets.com/reports/1">a market report</a>
             and commentary at <a href="https://www.someco.com/blog/x">SomeCo</a>.</p></main></body></html>"""
    pages = {"https://www.researchandmarkets.com/reports/1": HOP2_HTML}
    loads: list[str] = []

    def loader(url):
        loads.append(url)
        return pages.get(url)

    src = Source(url="https://www.mordorintelligence.com/x", tier=Tier.T5, state=SourceState.FETCHED,
                 health_class=HealthClass.LIVE, sha256="y")
    assert MAX_TRACE_HOPS == 2
    tr = trace_upstream(src, html=hop1, page_loader=loader)
    assert tr.traced and tr.terminus == "https://www.mas.gov.sg/publications/annual-report-2025" and tr.hops == 2
    assert tr.path == ["https://www.mordorintelligence.com/x", "https://www.researchandmarkets.com/reports/1",
                       "https://www.mas.gov.sg/publications/annual-report-2025"]
    assert loads == ["https://www.researchandmarkets.com/reports/1"]
    # max_hops=1: the guard refuses to follow and reports why
    tr1 = trace_upstream(src, html=hop1, page_loader=loader, max_hops=1)
    assert not tr1.traced and "max_hops=1" in tr1.reason
    # a chain of aggregators longer than max_hops is never followed past the guard
    chain = {
        "https://www.researchandmarkets.com/reports/1":
            '<p>Data from <a href="https://www.grandviewresearch.com/r/2">another mill</a></p>',
        "https://www.grandviewresearch.com/r/2":
            '<p>Data from <a href="https://www.mas.gov.sg/publications/annual-report-2025">MAS</a></p>',
    }
    loads.clear()
    tr2 = trace_upstream(src, html=hop1, page_loader=lambda u: chain.get(u))
    assert not tr2.traced and "max_hops=2" in tr2.reason
    # without a loader the tracer never leaves the first page
    tr3 = trace_upstream(src, html=hop1)
    assert not tr3.traced and "no page_loader" in tr3.reason


def test_declared_upstream_still_wins_and_counts_for_independence():
    agg = Source(url=AGG_URL, tier=Tier.T5, state=SourceState.FETCHED, health_class=HealthClass.LIVE, sha256="a",
                 upstream_of=["https://arxiv.org/abs/2604.03173"], text_extract="statista summary text")
    assert trace_to_original(agg, html=AGGREGATOR_HTML) == "https://arxiv.org/abs/2604.03173"
    assert terminus_of(agg) == "https://arxiv.org/abs/2604.03173"
    other = Source(url="https://www.mas.gov.sg/publications/x", tier=Tier.T1, state=SourceState.FETCHED,
                   health_class=HealthClass.LIVE, sha256="b", text_extract="completely different MAS text")
    assert count_independent_upstreams([agg, other]).count == 2
    # crawl candidates alone do NOT count: the terminus must be fetched and hashed first
    untraced = Source(url=AGG_URL, tier=Tier.T5, state=SourceState.FETCHED, health_class=HealthClass.LIVE, sha256="c",
                      upstream_candidates=["https://arxiv.org/abs/2604.03173"], text_extract="statista summary text")
    assert terminus_of(untraced) is None and count_independent_upstreams([untraced, other]).count == 1


def test_pipeline_records_upstream_candidates_on_aggregator(fetcher, store, monkeypatch, tmp_path):
    import plumbverify.pipeline as pl
    from .conftest import make_handler, _State
    state = _State()
    base = make_handler(state)

    def handler(request):
        if request.url.host == "www.statista.com":
            return httpx.Response(200, headers={"content-type": "text/html"}, content=AGGREGATOR_HTML.encode())
        return base(request)

    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    f = Fetcher(store=store, client=client, sleep=lambda s: None)
    v = pl.Verifier(fetcher=f, store=store)
    src = v.resolve_source(AGG_URL, "run-x")
    assert src.tier == Tier.T5 and src.upstream_candidates[0] == "https://arxiv.org/abs/2604.03173"
    assert not src.upstream_of  # candidates are advisory, not traced


# ---------------------------------------------------------------------------
# Reviewer report + 6.2 sampling worksheet
# ---------------------------------------------------------------------------
def _report(n_modules: int = 4, lb_per_module: int = 8, qual_per_module: int = 3, blocked: int = 2) -> VerificationReport:
    claims, cites, decs, sources = [], [], [], []
    mods = ["executive-summary"] + [f"module-{i}" for i in range(1, n_modules)]
    k = 0
    for mod in mods:
        for j in range(lb_per_module):
            kind = ClaimKind.quote if (mod == "executive-summary" and j % 3 == 2) else ClaimKind.number
            claims.append(Claim(id=f"c{k}", module=mod, text=f"claim {k} says 42% in {mod}", kind=kind, load_bearing=True,
                                confidence_label=ConfidenceLabel.filed if kind == ClaimKind.number else None,
                                sources=[f"https://src{k}.example.org/p"]))
            k += 1
        for j in range(qual_per_module):
            claims.append(Claim(id=f"c{k}", module=mod, text=f"qualitative claim {k}", kind=ClaimKind.fact,
                                load_bearing=False, sources=[f"https://src{k}.example.org/p"]))
            k += 1
    for i, c in enumerate(claims):
        url = c.sources[0]
        sources.append(Source(url=url, url_final=url, sha256="ab" * 32, tier=Tier.T3 if i % 2 else Tier.T1,
                              health_class=HealthClass.LIVE, state=SourceState.FETCHED, text_extract="x",
                              page_count=3 if i % 5 == 0 else None))
        is_blocked = i < blocked
        cites.append(Citation(claim_id=c.id, source_url=url, passage="p", page=2 if i % 5 == 0 else None,
                              match_score=0.5 if is_blocked else 0.93,
                              status=CitationStatus.unverified if is_blocked else CitationStatus.verified))
        decs.append(ClaimDecision(claim_id=c.id, status=CitationStatus.blocked if is_blocked else CitationStatus.verified,
                                  blocked=is_blocked, load_bearing=c.load_bearing,
                                  reasons=["no citation reaches the support threshold (C4)"] if is_blocked else [],
                                  independent_upstreams=0 if is_blocked else 2))
    from plumbverify.policy import build_gate
    gate = build_gate(claims, decs)
    return VerificationReport(run_id="run-test", sources=sources, claims=claims, citations=cites, decisions=decs,
                              gap_register=gate.gap_register, build_pass=gate.passed,
                              metrics={"claims": len(claims), "blocked_claims": gate.blocked_count,
                                       "citation_resolution_rate": 1.0, "quotation_pass_rate": 1.0,
                                       "two_upstream_coverage": 0.95, "aigen_or_farm_cited": 0})


def test_sample_is_deterministic_and_stratified():
    rep = _report()
    a, b = build_sample(rep, seed=7), build_sample(rep, seed=7)
    assert a.ids == b.ids and len(a.sampled) == 30 and a.shortfall == 0
    assert build_sample(rep, seed=8).ids != a.ids
    blocked = {d.claim_id for d in rep.decisions if d.blocked}
    assert not blocked & set(a.ids)  # P2: released frame only
    strata = {s.claim.id: s.stratum for s in a.sampled}
    # (a) every exec-summary load-bearing number and quotation that is released
    exec_a = [c for c in rep.claims if c.module == "executive-summary" and c.load_bearing and c.id not in blocked]
    assert all(strata[c.id] == "a" for c in exec_a)
    # (b) >= 2 remaining load-bearing per other module
    for mod in ("module-1", "module-2", "module-3"):
        assert sum(1 for s in a.sampled if s.stratum == "b" and s.claim.module == mod) >= 2
    # (c) >= 5 qualitative
    assert a.counts["c"] >= 5 and all(not s.claim.load_bearing for s in a.sampled if s.stratum == "c")
    # (d) top-up is load-bearing
    assert all(s.claim.load_bearing for s in a.sampled if s.stratum == "d")


def test_sample_reports_shortfall_on_small_frame():
    rep = _report(n_modules=2, lb_per_module=3, qual_per_module=2, blocked=1)
    plan = build_sample(rep, seed=1)
    assert plan.frame_size == 9 and len(plan.sampled) == 9 and plan.shortfall == 21
    assert plan.counts["e"] == 0  # qualitative claims already taken under (c)
    # when load-bearing claims run out but qualitative ones remain, the fill is labelled (e) not (d)
    rep2 = _report(n_modules=2, lb_per_module=3, qual_per_module=20, blocked=0)
    plan2 = build_sample(rep2, seed=1)
    assert len(plan2.sampled) == 30 and plan2.counts["e"] > 0
    assert all(s.claim.load_bearing for s in plan2.sampled if s.stratum == "d")


def test_render_markdown_contains_claim_table_and_worksheet():
    rep = _report()
    md = render_markdown(rep, seed=42)
    assert md.startswith("# Verification report run-test")
    assert "| # | Claim | Module | Kind | LB | Status | Score | Tier | Indep. upstreams | Source (locator) | Reasons |" in md
    assert "| c0 | claim 0 says 42% in executive-summary | executive-summary | number | yes | BLOCKED | 0.50 | T1 | 0 |" in md
    assert "(p. 2)" in md  # page locator rendered
    assert "## Gap register" in md and "no citation reaches the support threshold (C4)" in md
    assert "Random seed: `42`" in md and "--seed 42" in md
    assert "Sample frame (P2): " in md and "2 BLOCKED claims excluded" in md
    for heading in ("### P1 Reviewer eligibility", "### P4 Per-claim checks", "### P5 C7 agreement sample",
                    "### P6 Totals", "### P7 Decision"):
        assert heading in md
    assert "| Load-bearing full-support rate | | >= 95% |" in md
    # worksheet rows: 30 sampled claims, quote / upstream cells pre-filled with n.a. where not applicable
    ws = md.split("### P4 Per-claim checks")[1].split("### P5")[0]
    rows = [ln for ln in ws.splitlines() if ln.startswith("| c")]
    assert len(rows) == 30
    quote_rows = [r for r in rows if "| quote |" in r]
    assert quote_rows and all("| n.a. |" in r for r in quote_rows)  # upstream n.a. for quotes
    # pipe characters in claim text are escaped so the table stays intact
    rep.claims[5].text = "pipe | in text"
    assert "pipe \\| in text" in render_markdown(rep, seed=1)


def test_cli_report_md_and_json(tmp_path, capsys):
    rep = _report()
    path = tmp_path / "report.json"
    path.write_text(rep.model_dump_json())
    out = tmp_path / "report.md"
    rc = main(["report", str(path), "--format", "md", "--seed", "3", "--out", str(out)])
    assert rc == 1  # build failed (2 blocked) -> non-zero, mirrors `verify`
    md = out.read_text()
    assert "Random seed: `3`" in md and "### P7 Decision" in md
    capsys.readouterr()
    rc = main(["report", str(path), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["run_id"] == "run-test"
    # a passing report exits 0 and the seed is auto-generated when omitted
    rep2 = _report(blocked=0)
    path.write_text(rep2.model_dump_json())
    assert main(["report", str(path)]) == 0
    assert "Random seed: `" in capsys.readouterr().out
