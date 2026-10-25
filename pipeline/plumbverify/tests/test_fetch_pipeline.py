import hashlib
import json

from plumbverify.cli import main
from plumbverify.extract import extract_main_text, split_passages
from plumbverify.fetch import ArchiveSnapshot, Fetcher, looks_pattern_plausible
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel, HealthClass, SourceState, Tier
from plumbverify.pipeline import Verifier, load_claims
from plumbverify.tier import load_tier_rules

from .conftest import REPORT_HTML

RULES = load_tier_rules(overrides={"tiers": {
    "T3": {"domains": ["example-press.org", "example-wire.com"]},
}})


# ---- C1 fetch + hash store ------------------------------------------------
def test_fetch_hashes_and_stores(fetcher, store):
    src = fetcher.fetch("https://www.example-press.org/report")
    assert src.state == SourceState.FETCHED and src.health_class == HealthClass.LIVE
    assert src.sha256 == hashlib.sha256(REPORT_HTML.encode()).hexdigest()
    assert store.verify_hash(src.sha256)
    assert store.lookup_url("https://www.example-press.org/report")["sha256"] == src.sha256
    assert "A$440,000" in src.text_extract and "ignore me" not in src.text_extract
    assert src.citable


def test_fetch_hash_deterministic_on_refetch(fetcher):
    a = fetcher.fetch("https://www.example-press.org/report")
    b = fetcher.fetch("https://www.example-press.org/report")
    assert a.sha256 == b.sha256


def test_fetch_records_redirect_final_url(fetcher):
    src = fetcher.fetch("https://www.example-press.org/old-report")
    assert src.url == "https://www.example-press.org/old-report"
    assert src.url_final == "https://www.example-press.org/report"


def test_fetch_retries_with_backoff_on_5xx(mock_client, store, net_state):
    waits = []
    f = Fetcher(store=store, client=mock_client, sleep=waits.append)
    src = f.fetch("https://www.example-press.org/flaky")
    assert src.state == SourceState.FETCHED
    assert waits == [2.0]  # one 503 then success; first backoff step is 2 s


# ---- C2 health check ------------------------------------------------------
def test_health_live_and_dead(fetcher):
    assert fetcher.check_health("https://www.example-press.org/report").health_class == HealthClass.LIVE
    dead = fetcher.check_health("https://www.example-press.org/missing")
    assert dead.health_class == HealthClass.DEAD and dead.http_status == 404


def test_health_falls_back_to_get_when_head_rejected(fetcher):
    h = fetcher.check_health("https://www.example-press.org/head-not-allowed")
    assert h.health_class == HealthClass.LIVE and h.http_status == 200


def test_health_likely_hallucinated_on_no_dns_plausible_path(fetcher):
    h = fetcher.check_health("https://nxdomain.example/2025/10/deloitte-refund-report")
    assert h.health_class == HealthClass.LIKELY_HALLUCINATED
    src = fetcher.fetch("https://nxdomain.example/2025/10/deloitte-refund-report")
    assert src.state == SourceState.LIKELY_HALLUCINATED and not src.citable
    assert looks_pattern_plausible("https://x.example/research/ai-citation-audit-2026")
    assert not looks_pattern_plausible("https://x.example/")


def test_health_no_dns_unplausible_path_is_dead(fetcher):
    assert fetcher.check_health("https://nxdomain.example/").health_class == HealthClass.DEAD


class _FakeArchive:
    def lookup(self, url):
        if url.endswith("/missing"):
            return ArchiveSnapshot(archive_url="https://www.example-press.org/report")  # stands in for a Wayback snapshot
        return None


def test_archive_hook_yields_archived_with_hash(mock_client, store):
    f = Fetcher(store=store, client=mock_client, archive=_FakeArchive(), sleep=lambda s: None)
    src = f.fetch("https://www.example-press.org/missing")
    assert src.state == SourceState.ARCHIVED and src.health_class == HealthClass.ARCHIVED
    assert src.archived_url and src.sha256 and src.citable


# ---- extraction -----------------------------------------------------------
def test_extract_and_split():
    text = extract_main_text(REPORT_HTML.encode(), "text/html")
    assert "fabricated references" in text and "console.log" not in text
    passages = split_passages(text)
    assert len(passages) >= 3 and all(len(p) <= 800 for p in passages)


# ---- end to end (S2-S5) ---------------------------------------------------
CLAIMS = {"claims": [
    {"id": "n1", "text": "Deloitte's report cost A$440,000", "kind": "number", "load_bearing": True,
     "confidence_label": "filed",
     "sources": ["https://www.example-press.org/report", "https://news.example-wire.com/senate"]},
    {"id": "n2", "text": "Deloitte's report cost A$440,000", "kind": "number", "load_bearing": True,
     "confidence_label": "filed",
     "sources": ["https://www.example-press.org/report", "https://mirror.example-press.org/report-copy"]},
    {"id": "n3", "text": "The consulting AI segment is valued at US$3.2 billion", "kind": "number", "load_bearing": True,
     "confidence_label": "vendor-estimate",
     "sources": ["https://www.example-press.org/report", "https://www.statista.com/statistics/1/"]},
    {"id": "q1", "text": "The substance of the independent review is retained, and there are no changes to the recommendations.",
     "kind": "quote", "sources": ["https://www.example-press.org/report"]},
    {"id": "q2", "text": "The substance of the independent review is retained, and there are several changes to the recommendations.",
     "kind": "quote", "sources": ["https://www.example-press.org/report"]},
    {"id": "f1", "text": "a dozen citations to the work of a professor who does not exist", "kind": "fact",
     "sources": ["https://www.example-press.org/report"]},
    {"id": "f2", "text": "The department sued Deloitte for the full fee", "kind": "fact",
     "sources": ["https://www.example-press.org/report"]},
    {"id": "f3", "text": "GPT-4o hosted on Azure OpenAI was used to assist with drafting", "kind": "fact",
     "sources": ["https://nxdomain.example/2025/10/deloitte-refund-report"]},
    {"id": "f4", "text": "3% and 13% of cited URLs are hallucinated", "kind": "number", "load_bearing": False,
     "confidence_label": "filed", "sources": ["https://blog.contentfarm.example/top-10"]},
]}


def test_end_to_end_blocks_and_passes_correctly(fetcher, store, tmp_path):
    log = HashChainLog(tmp_path / "inference.jsonl")
    v = Verifier(fetcher=fetcher, store=store, log=log, tier_rules=RULES)
    claims = [c for c in load_claims(_write(tmp_path, CLAIMS))]
    report = v.run(claims)
    d = {x.claim_id: x for x in report.decisions}

    assert not d["n1"].blocked and d["n1"].independent_upstreams == 2          # two independent upstreams
    assert d["n2"].blocked and any("single-upstream" in r for r in d["n2"].reasons)  # mirror = same content
    assert d["n3"].blocked and any("single-upstream" in r for r in d["n3"].reasons)  # statista untraced
    assert not d["q1"].blocked                                                   # exact quotation
    assert d["q2"].blocked and any("C5" in r for r in d["q2"].reasons)           # altered quotation
    assert not d["f1"].blocked                                                   # lexical support
    assert d["f2"].blocked                                                       # unsupported fact
    assert d["f3"].blocked and any("LIKELY_HALLUCINATED" in r for r in d["f3"].reasons)
    assert d["f4"].blocked and any("rejected (C7)" in r for r in d["f4"].reasons)

    assert not report.build_pass
    assert {g.claim_id for g in report.gap_register} == {"n2", "n3", "q2", "f2", "f3", "f4"}
    assert report.metrics["aigen_or_farm_cited"] == 0
    tiers = {s.url: s.tier for s in report.sources}
    assert tiers["https://www.statista.com/statistics/1/"] == Tier.T5
    assert tiers["https://www.example-press.org/report"] == Tier.T3
    # every step logged, chain intact, region asserted, prompt hashed not stored
    recs = log.records()
    assert log.verify().ok and len(recs) > len(claims)
    assert all(r["region_asserted"] == "asia-southeast1" for r in recs if r.get("type") == "inference")
    assert all("prompt_sha256" in r for r in recs if r.get("type") == "inference")


def test_cli_verify_writes_report_and_exit_code(fetcher, store, tmp_path, monkeypatch):
    # route the CLI's Fetcher/Verifier through the offline transport
    import plumbverify.cli as cli
    monkeypatch.setattr(cli, "Fetcher", lambda **kw: fetcher)
    monkeypatch.setattr(cli, "EvidenceStore", lambda path: store)
    claims_path = _write(tmp_path, {"claims": [CLAIMS["claims"][0], CLAIMS["claims"][3]]})
    tiers = tmp_path / "tiers.yaml"
    tiers.write_text("default: T5\ntiers:\n  T3:\n    domains: [example-press.org, example-wire.com]\n")
    out = tmp_path / "report.json"
    rc = main(["verify", str(claims_path), "--out", str(out), "--log", str(tmp_path / "log.jsonl"),
               "--store", str(tmp_path / "ev"), "--tiers", str(tiers)])
    assert rc == 0
    rep = json.loads(out.read_text())
    assert rep["build_pass"] is True and len(rep["decisions"]) == 2
    rc2 = main(["verify-log", str(tmp_path / "log.jsonl")])
    assert rc2 == 0


def test_cli_check_url_offline(fetcher, tmp_path, monkeypatch, capsys):
    import plumbverify.cli as cli
    monkeypatch.setattr(cli, "Fetcher", lambda **kw: fetcher)
    rc = main(["check-url", "https://www.example-press.org/old-report"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["health_class"] == "LIVE" and out["url_final"].endswith("/report")
    rc = main(["check-url", "https://nxdomain.example/2025/10/deloitte-refund-report"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1 and out["health_class"] == "LIKELY_HALLUCINATED" and out["citable"] is False


def _write(tmp_path, payload):
    p = tmp_path / "claims.json"
    p.write_text(json.dumps(payload))
    return p
