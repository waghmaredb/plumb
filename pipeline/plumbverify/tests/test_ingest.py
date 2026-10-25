"""0.3 attached-document ingest path: a person-supplied PDF enters the store
under its declared publisher URL with the same hash/extract guarantees as a
fetch, is citable with a visible label, and reconciliation against the
publisher either lifts the label (MATCH) or blocks every claim (MISMATCH).

0.4 (spec C2a, red-team review 2026-10-25 Blocker 2): the labelled path is
the INTERNAL build profile. The default CLIENT profile withholds every claim
whose only support is an unreconciled attachment ("awaiting publisher
reconciliation" in the gap register)."""
import hashlib
import json

import pytest

from plumbverify.cli import main
from plumbverify.fetch import EvidenceStore, Fetcher
from plumbverify.ingest import ingest_local, reconcile, reconcile_all
from plumbverify.models import (
    ATTACHED_LABEL, Claim, ClaimKind, CitationStatus, ConfidenceLabel, HealthClass, Reconciliation, SourceState, Tier,
)
from plumbverify.pipeline import Verifier
from plumbverify.report import build_sample, render_markdown
from plumbverify.tier import load_tier_rules

from .conftest import REPORT_HTML, REPORT_PDF

RULES = load_tier_rules(overrides={"tiers": {"T1": {"domains": ["example-gov.sg"]},
                                             "T3": {"domains": ["example-press.org", "example-wire.com"]}}})
PDF_URL = "https://docs.example-gov.sg/review.pdf"          # mock web serves REPORT_PDF here -> MATCH
MISSING_URL = "https://docs.example-gov.sg/not-published.pdf"  # mock web 404 -> UNAVAILABLE
HTML_URL = "https://www.example-press.org/report"            # mock web serves REPORT_HTML here

CLAIMS = [
    Claim(id="n1", text="The department commissioned the report for A$440,000", kind=ClaimKind.number,
          confidence_label=ConfidenceLabel.filed, sources=[PDF_URL]),
    Claim(id="q1", text="The substance of the independent review is retained, and there are no changes to the recommendations.",
          kind=ClaimKind.quote, sources=[PDF_URL]),
]


@pytest.fixture
def pdf_file(tmp_path):
    f = tmp_path / "GEH Annual Report FY2025.pdf"
    f.write_bytes(REPORT_PDF)
    return f


def _verifier(store, mock_client, build_profile="internal", **kw):
    f = Fetcher(store=store, client=mock_client, sleep=lambda s: None, **kw)
    return Verifier(fetcher=f, store=store, tier_rules=RULES, build_profile=build_profile)


# ---- ingest ---------------------------------------------------------------
def test_ingest_pdf_is_hashed_extracted_and_stored_under_declared_url(pdf_file, store):
    src = ingest_local(pdf_file, PDF_URL, store, supplied_by="deepak", tier_rules=RULES)
    assert src.state == SourceState.ATTACHED and src.health_class == HealthClass.UNCHECKED
    assert src.url == PDF_URL and src.sha256 == hashlib.sha256(REPORT_PDF).hexdigest()
    assert store.verify_hash(src.sha256) and store.lookup_url(PDF_URL)["sha256"] == src.sha256  # same store rows as a fetch
    assert src.detected_content_type == "application/pdf" and src.page_count == 2 and not src.needs_ocr
    assert "A$440,000" in src.text_extract
    assert src.tier == Tier.T1  # tier from the declared URL's domain
    assert src.citable and src.attached_label == ATTACHED_LABEL
    assert src.recheck_after is not None
    assert src.provenance["supplied_by"] == "deepak" and src.provenance["original_filename"] == pdf_file.name
    assert src.provenance["declared_url"] == PDF_URL and src.provenance["supplied_at"]
    # round-trips through the store
    back = store.load_attached_source(PDF_URL)
    assert back.state == SourceState.ATTACHED and back.sha256 == src.sha256 and back.provenance["supplied_by"] == "deepak"
    assert back.text_extract == src.text_extract and back.reconciliation is None


def test_ingest_rejects_missing_file_and_relative_url(tmp_path, store):
    with pytest.raises(FileNotFoundError):
        ingest_local(tmp_path / "nope.pdf", PDF_URL, store)
    f = tmp_path / "x.pdf"
    f.write_bytes(REPORT_PDF)
    with pytest.raises(ValueError):
        ingest_local(f, "data/geh.pdf", store)


# ---- citable with the label, no network (INTERNAL profile) -------------------
def test_attached_source_cites_with_label_without_touching_network(pdf_file, store, mock_client, net_state):
    ingest_local(pdf_file, PDF_URL, store, supplied_by="deepak", tier_rules=RULES)
    rep = _verifier(store, mock_client, build_profile="internal").run(CLAIMS)
    assert net_state.calls == []  # the attachment is used as is; reconcile is an explicit step
    assert rep.build_pass and rep.build_profile == "internal"
    d = {x.claim_id: x for x in rep.decisions}
    assert d["n1"].status == CitationStatus.verified and d["q1"].status == CitationStatus.verified
    assert d["n1"].labels == [ATTACHED_LABEL] and d["q1"].labels == [ATTACHED_LABEL]
    assert all(ATTACHED_LABEL in c.labels for c in rep.citations)
    assert next(c for c in rep.citations if c.claim_id == "q1").page == 2  # page-aware like a fetched PDF
    src = rep.sources[0]
    assert src.state == SourceState.ATTACHED and src.tier == Tier.T1 and src.provenance["supplied_by"] == "deepak"
    assert rep.metrics["attached_sources"] == 1 and rep.metrics["attached_unreconciled"] == 1
    assert rep.metrics["claims_on_unreconciled_attachments"] == 2 and rep.metrics["citation_resolution_rate"] == 1.0
    md = render_markdown(rep, seed=3)
    assert "## Attached sources (person-supplied documents)" in md
    assert src.sha256 in md and "deepak" in md and "pending (not yet attempted)" in md
    assert f"VERIFIED ({ATTACHED_LABEL})" in md
    assert "(f) attached-source claims sampled separately" in md


# ---- C2a: CLIENT profile (the default) withholds unreconciled attachments ----
def test_client_profile_blocks_claims_resting_on_unreconciled_attachment(pdf_file, store, mock_client, net_state):
    ingest_local(pdf_file, PDF_URL, store, supplied_by="deepak", tier_rules=RULES)
    f = Fetcher(store=store, client=mock_client, sleep=lambda s: None)
    rep = Verifier(fetcher=f, store=store, tier_rules=RULES).run(CLAIMS)  # default profile is "client"
    assert rep.build_profile == "client" and net_state.calls == []
    assert not rep.build_pass and {g.claim_id for g in rep.gap_register} == {"n1", "q1"}
    d = {x.claim_id: x for x in rep.decisions}
    assert all(d[k].blocked and d[k].withheld_awaiting_reconciliation and not d[k].labels for k in ("n1", "q1"))
    assert all(any(r.startswith("awaiting publisher reconciliation") and "C2a" in r for r in g.reasons) for g in rep.gap_register)
    # the citations themselves still matched (the evidence is sound; only its provenance is unreconciled)
    assert all(c.status == CitationStatus.verified and ATTACHED_LABEL in c.labels for c in rep.citations)
    assert rep.metrics["withheld_awaiting_reconciliation"] == 2 and rep.metrics["blocked_claims"] == 2
    assert rep.metrics["released_claims"] == 0 and rep.metrics["claims_on_unreconciled_attachments"] == 2
    md = render_markdown(rep, seed=3)
    assert "Released: 0 claims. Withheld: 2 claims (listed in the gap register; 2 awaiting publisher reconciliation)." in md
    assert "Build profile: client" in md
    # a second, fetched source keeps a claim released in a client build even while the attachment is unreconciled
    two = Claim(id="n2", text="The department commissioned the report for A$440,000", kind=ClaimKind.number,
                confidence_label=ConfidenceLabel.filed, sources=[PDF_URL, HTML_URL])
    rep2 = Verifier(fetcher=Fetcher(store=store, client=mock_client, sleep=lambda s: None), store=store, tier_rules=RULES).run([two])
    assert rep2.build_pass and not rep2.decisions[0].blocked and rep2.decisions[0].labels == []  # label does not travel
    # MATCH lifts the withholding in the client profile
    assert reconcile(store, PDF_URL, REPORT_PDF) == Reconciliation.MATCH
    rep3 = Verifier(fetcher=Fetcher(store=store, client=mock_client, sleep=lambda s: None), store=store, tier_rules=RULES).run(CLAIMS)
    assert rep3.build_pass and rep3.metrics["withheld_awaiting_reconciliation"] == 0
    with pytest.raises(ValueError):
        Verifier(fetcher=f, store=store, tier_rules=RULES, build_profile="board")


def test_cli_profile_flag_switches_c2a(pdf_file, tmp_path, capsys, monkeypatch, mock_client):
    import plumbverify.cli as cli
    store_dir = tmp_path / "store"
    assert main(["ingest", str(pdf_file), "--url", PDF_URL, "--store", str(store_dir)]) == 0
    capsys.readouterr()
    claims_path = tmp_path / "claims.json"
    claims_path.write_text(json.dumps({"claims": [c.model_dump(mode="json") for c in CLAIMS]}), encoding="utf-8")
    tiers = tmp_path / "tiers.yaml"
    tiers.write_text("default: T5\ntiers:\n  T1:\n    domains: [example-gov.sg]\n")
    monkeypatch.setattr(cli, "Fetcher", lambda **kw: Fetcher(store=kw["store"], client=mock_client, sleep=lambda s: None))
    common = [str(claims_path), "--store", str(store_dir), "--tiers", str(tiers)]
    rc = main(["verify", *common, "--out", str(tmp_path / "client.json"), "--log", str(tmp_path / "c.jsonl")])
    out = capsys.readouterr().out
    assert rc == 1 and "[client build]" in out and "Withheld: 2 claims" in out and "awaiting publisher reconciliation" in out
    assert json.loads((tmp_path / "client.json").read_text())["build_profile"] == "client"
    rc = main(["verify", *common, "--profile", "internal", "--out", str(tmp_path / "internal.json"), "--log", str(tmp_path / "i.jsonl")])
    out = capsys.readouterr().out
    assert rc == 0 and "[internal build]" in out and "Released: 2 claims. Withheld: 0 claims." in out
    rep = json.loads((tmp_path / "internal.json").read_text())
    assert rep["build_profile"] == "internal" and rep["build_pass"] is True
    assert all(d["labels"] == [ATTACHED_LABEL] for d in rep["decisions"])


# ---- reconcile ---------------------------------------------------------------
def test_reconcile_match_flips_state_to_live_and_drops_label(pdf_file, store, mock_client):
    ingest_local(pdf_file, PDF_URL, store, tier_rules=RULES)
    assert reconcile(store, PDF_URL, REPORT_PDF) == Reconciliation.MATCH
    src = store.load_attached_source(PDF_URL)
    assert src.state == SourceState.FETCHED and src.health_class == HealthClass.LIVE
    assert src.reconciliation == Reconciliation.MATCH and src.reconciled_sha256 == src.sha256
    assert src.attached_label is None and src.citable and src.provenance["declared_url"] == PDF_URL  # provenance is kept
    rep = _verifier(store, mock_client).run(CLAIMS)
    assert rep.build_pass and all(not x.labels for x in rep.decisions)
    assert rep.metrics["attached_sources"] == 1 and rep.metrics["attached_unreconciled"] == 0
    md = render_markdown(rep, seed=3)
    assert "| MATCH |" in md and ATTACHED_LABEL not in md.split("## Claims")[1].split("## Sources")[0]


def test_reconcile_mismatch_blocks_every_claim_citing_the_source(tmp_path, store, mock_client):
    tampered = tmp_path / "edited.pdf"
    tampered.write_bytes(REPORT_PDF + b"\n%% one extra byte\n")  # text identical, bytes differ
    ingest_local(tampered, PDF_URL, store, supplied_by="someone", tier_rules=RULES)
    assert reconcile(store, PDF_URL, REPORT_PDF) == Reconciliation.MISMATCH
    src = store.load_attached_source(PDF_URL)
    assert src.state == SourceState.ATTACHED and src.reconciliation == Reconciliation.MISMATCH and not src.citable
    assert src.reconciled_sha256 == hashlib.sha256(REPORT_PDF).hexdigest() and store.verify_hash(src.reconciled_sha256)  # publisher bytes kept
    rep = _verifier(store, mock_client).run(CLAIMS)
    assert not rep.build_pass and {g.claim_id for g in rep.gap_register} == {"n1", "q1"}
    assert all("MISMATCH" in r for g in rep.gap_register for r in g.reasons[1:2])
    assert rep.metrics["attached_mismatch"] == 1 and rep.metrics["citation_resolution_rate"] == 0.0
    # the frame has no released claims, and the report says why
    md = render_markdown(rep, seed=3)
    assert "| MISMATCH |" in md and "MISMATCH: 1" in md


def test_reconcile_unavailable_keeps_attached_and_labelled(pdf_file, store, mock_client):
    ingest_local(pdf_file, MISSING_URL, store, tier_rules=RULES)
    f = Fetcher(store=store, client=mock_client, sleep=lambda s: None)
    assert reconcile_all(store, f) == [(MISSING_URL, Reconciliation.UNAVAILABLE)]
    src = store.load_attached_source(MISSING_URL)
    assert src.state == SourceState.ATTACHED and src.reconciliation == Reconciliation.UNAVAILABLE
    assert src.citable and src.attached_label == ATTACHED_LABEL and src.reconciled_at is not None


def test_reconcile_all_uses_fetcher_transport_and_skips_matched(pdf_file, store, mock_client, net_state):
    ingest_local(pdf_file, PDF_URL, store, tier_rules=RULES)
    f = Fetcher(store=store, client=mock_client, sleep=lambda s: None)
    assert reconcile_all(store, f) == [(PDF_URL, Reconciliation.MATCH)]
    n = len(net_state.calls)
    assert reconcile_all(store, f) == [(PDF_URL, Reconciliation.MATCH)] and len(net_state.calls) == n  # already MATCH: no refetch
    assert reconcile_all(store, f, include_reconciled=True)[0][1] == Reconciliation.MATCH and len(net_state.calls) == n + 1
    with pytest.raises(KeyError):
        reconcile_all(store, f, url="https://docs.example-gov.sg/never-attached.pdf")


def test_fetcher_reconcile_on_fetch_prefers_attachment_over_404_and_reconciles_on_200(pdf_file, store, mock_client, net_state):
    ingest_local(pdf_file, MISSING_URL, store, tier_rules=RULES)
    ingest_local(pdf_file, PDF_URL, store, tier_rules=RULES)
    f = Fetcher(store=store, client=mock_client, sleep=lambda s: None, reconcile_on_fetch=True)
    missing = f.fetch(MISSING_URL)  # web says 404; the attachment wins over DEAD
    assert missing.state == SourceState.ATTACHED and missing.citable and missing.reconciliation == Reconciliation.UNAVAILABLE
    assert any(u.endswith("/not-published.pdf") for _, u in net_state.calls)
    live = f.fetch(PDF_URL)  # web serves identical bytes: reconciled in passing
    assert live.state == SourceState.FETCHED and live.reconciliation == Reconciliation.MATCH and live.attached_label is None


# ---- sampling: attached-source claims stratified separately ------------------
def test_sample_stratifies_attached_claims_separately(pdf_file, store, mock_client):
    ingest_local(pdf_file, PDF_URL, store, tier_rules=RULES)
    many = [Claim(id=f"a{i}", text="The department commissioned the report for A$440,000", kind=ClaimKind.number, module="annual-report",
                  confidence_label=ConfidenceLabel.filed, sources=[PDF_URL]) for i in range(8)]
    fetched = [Claim(id=f"h{i}", text="Deloitte Australia has agreed to partially refund the Department of Employment and Workplace Relations",
                     kind=ClaimKind.fact, module="exec-summary", sources=[HTML_URL]) for i in range(8)]
    rep = _verifier(store, mock_client).run(many + fetched)
    assert rep.build_pass
    plan = build_sample(rep, seed=5, sample_min=30)
    by = {s.claim.id: s.stratum for s in plan.sampled}
    assert plan.counts["f"] == 5 and all(by[k] == "f" for k in by if by[k] == "f" and k.startswith("a"))
    assert all(k.startswith("a") for k, v in by.items() if v == "f")  # only attached-source claims land in (f)
    assert plan.counts["attached_in_sample"] >= 5
    assert build_sample(rep, seed=5, sample_min=30).ids == plan.ids  # still deterministic


# ---- CLI ------------------------------------------------------------------------
def test_cli_ingest_and_reconcile(pdf_file, tmp_path, capsys, monkeypatch, mock_client):
    store_dir = tmp_path / "store"
    rc = main(["ingest", str(pdf_file), "--url", PDF_URL, "--store", str(store_dir), "--supplied-by", "deepak"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["state"] == "ATTACHED" and out["label"] == ATTACHED_LABEL and out["page_count"] == 2
    assert out["provenance"]["supplied_by"] == "deepak" and out["sha256"] == hashlib.sha256(REPORT_PDF).hexdigest()
    assert main(["ingest", str(tmp_path / "missing.pdf"), "--url", PDF_URL, "--store", str(store_dir)]) == 2

    import plumbverify.cli as cli
    monkeypatch.setattr(cli, "_make_fetcher", lambda args, store: Fetcher(store=store, client=mock_client, sleep=lambda s: None))
    rc = main(["reconcile", "--store", str(store_dir)])
    rows = json.loads(capsys.readouterr().out)
    assert rc == 0 and rows[0]["reconciliation"] == "MATCH" and rows[0]["state"] == "FETCHED"
    s = EvidenceStore(store_dir)
    assert s.load_attached_source(PDF_URL).state == SourceState.FETCHED
    s.close()

    # a tampered second attachment makes reconcile exit 1
    bad = tmp_path / "bad.html"
    bad.write_bytes(REPORT_HTML.encode() + b"<!-- edited -->")
    assert main(["ingest", str(bad), "--url", HTML_URL, "--store", str(store_dir)]) == 0
    capsys.readouterr()
    rc = main(["reconcile", "--store", str(store_dir), "--url", HTML_URL])
    rows = json.loads(capsys.readouterr().out)
    assert rc == 1 and rows[0]["reconciliation"] == "MISMATCH" and rows[0]["sha256_publisher"] != rows[0]["sha256_attached"]
    assert main(["reconcile", "--store", str(tmp_path / "empty-store")]) == 2
