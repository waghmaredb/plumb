"""Attached-document path (plumbverify 0.3): the annual report is attached by a
person instead of fetched. It enters the run's evidence store under the
declared IR URL, the rubric scores from it, every claim is released with the
label "attached; publisher hash unreconciled", and the outputs show the
reconciliation status per document. Reconciliation against the publisher's
bytes lifts the label (MATCH) or blocks every claim (MISMATCH)."""
import json

import yaml

from plumbverify.models import ATTACHED_LABEL, SourceState

from plumbresearch.cli import ingest_document, main
from plumbresearch.context import RunContext
from plumbresearch.orchestrator import run_subject
from plumbresearch.subject import Document, Subject, load_subject

from .conftest import AS_OF
from .test_pdf_path import LINES, minimal_pdf

URL = "https://ir.pdfco.example/annual-report-2025.pdf"


def _subject_yaml(tmp_path, local_file="ar-2025.pdf"):
    doc = {"kind": "annual_report", "fy": 2025, "url": URL}
    if local_file:
        doc["local_file"] = local_file
    data = {"slug": "pdfco", "name": "PDF Co", "short_name": "PDF Co", "sector": "banks", "listing": {"exchange": "X"},
            "latest_fy": 2025, "documents": [doc], "tier_overrides": {"T2": ["pdfco.example"]}}
    p = tmp_path / "pdfco.yaml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


def test_document_key_resolution():
    s = Subject(slug="x", name="X", short_name="X", sector="banks", listing={"exchange": "X"}, latest_fy=2025,
                documents=[Document(kind="annual_report", fy=2025, url=URL, local_file="ar.pdf"),
                           Document(kind="results_release", fy=2025, url="https://ir.pdfco.example/results.html", key="results")])
    assert s.documents[0].document_key == "annual_report-2025" and s.documents[1].document_key == "results"
    for k in ("annual_report-2025", "annual_report:2025", URL, "ar.pdf"):
        assert s.find_document(k) is s.documents[0], k
    assert s.find_document("results") is s.documents[1] and s.find_document("annual_report-2024") is None


def test_end_to_end_with_attached_annual_report_offline(tmp_path, capsys):
    """No local file, no egress: the attached PDF is the evidence. The rubric scores,
    claims are released with the attached label, outputs disclose the status."""
    subj_yaml = _subject_yaml(tmp_path)  # local_file declared but absent in data/
    pdf = tmp_path / "GEH-style annual report.pdf"
    pdf.write_bytes(minimal_pdf(LINES))
    out_root = tmp_path / "out"
    rc = main(["ingest", str(subj_yaml), "--file", str(pdf), "--doc", "annual_report-2025", "--out", str(out_root), "--supplied-by", "deepak"])
    info = json.loads(capsys.readouterr().out)
    assert rc == 0 and info["state"] == "ATTACHED" and info["url"] == URL and info["label"] == ATTACHED_LABEL
    assert info["document_key"] == "annual_report-2025" and info["tier"] == "T2" and info["provenance"]["supplied_by"] == "deepak"
    assert main(["ingest", str(subj_yaml), "--file", str(pdf), "--doc", "annual_report-2031", "--out", str(out_root)]) == 2

    subject = load_subject(subj_yaml)
    out = run_subject(subject, out_root / subject.slug, tmp_path / "data", offline=True, modules=["annual-report"], as_of=AS_OF)
    assert out.report.build_pass, [(g.claim_id, g.reasons) for g in out.report.gap_register]
    rub = next(s for s in out.signals if s.id.endswith(".rubric"))
    assert rub.value == 4 and rub.status == "released" and rub.tier.value == "T2"  # same score as the served-local-PDF path
    assert out.claims and all(d.labels == [ATTACHED_LABEL] for d in out.report.decisions)
    src = next(s for s in out.report.sources if s.url == URL)
    assert src.state == SourceState.ATTACHED and src.provenance["supplied_by"] == "deepak" and src.provenance["document_key"] == "annual_report-2025"
    assert "rolled out across all branches" in src.text_extract  # PDF line unwrapping applied to the attached copy too
    assert not any("local file missing" in g.detail for g in out.gaps)  # the attachment stands in for the absent local file
    # per-document reconciliation status in the outputs
    assert out.attached_documents[0]["reconciliation"] is None and out.attached_documents[0]["claims_released"] == len(out.claims)
    sig_md = (out.out_dir / "signals.md").read_text()
    gap_md = (out.out_dir / "gap-register.md").read_text()
    assert "## Attached documents (reconciliation status)" in sig_md and "| annual_report-2025 |" in sig_md and "| pending |" in sig_md
    assert src.sha256 in sig_md and "deepak" in sig_md
    assert "## 5. Attached documents awaiting publisher reconciliation (1 of 1)" in gap_md and ATTACHED_LABEL in gap_md
    rep = json.loads((out.out_dir / "report.json").read_text())
    assert rep["attached_documents"][0]["sha256"] == src.sha256 and rep["attached_documents"][0]["state"] == "ATTACHED"
    assert rep["verification"]["metrics"]["claims_on_unreconciled_attachments"] == len(out.claims)


def test_online_run_reconciles_attachment_against_publisher_match(tmp_path):
    """Egress available (simulated by the local-document transport serving the
    declared URL): the run re-fetches, hashes MATCH, the label disappears."""
    subj_yaml = _subject_yaml(tmp_path)
    data = tmp_path / "data" / "pdfco"
    data.mkdir(parents=True)
    (data / "ar-2025.pdf").write_bytes(minimal_pdf(LINES))  # what the "publisher" serves
    attached = tmp_path / "attached.pdf"
    attached.write_bytes(minimal_pdf(LINES))                 # identical bytes attached by the person
    ingest_document(subj_yaml, attached, "annual_report-2025", tmp_path / "out", supplied_by="deepak")
    subject = load_subject(subj_yaml)
    ctx = RunContext.build(subject, tmp_path / "out" / "pdfco", tmp_path / "data", as_of=AS_OF)  # online mode, URL served locally
    assert ctx.fetcher.reconcile_on_fetch
    out = run_subject(subject, ctx.out_dir, tmp_path / "data", modules=["annual-report"], as_of=AS_OF, ctx=ctx)
    assert out.report.build_pass
    src = next(s for s in out.report.sources if s.url == URL)
    assert src.state == SourceState.FETCHED and src.reconciliation.value == "MATCH" and src.attached_label is None
    assert all(not d.labels for d in out.report.decisions)
    assert out.attached_documents[0]["reconciliation"] == "MATCH" and out.attached_documents[0]["state"] == "FETCHED"
    gap_md = (out.out_dir / "gap-register.md").read_text()
    assert "awaiting publisher reconciliation (0 of 1)" in gap_md and "| MATCH |" in gap_md
    ctx.store.close()


def test_online_run_blocks_everything_on_mismatch(tmp_path):
    subj_yaml = _subject_yaml(tmp_path)
    data = tmp_path / "data" / "pdfco"
    data.mkdir(parents=True)
    (data / "ar-2025.pdf").write_bytes(minimal_pdf(LINES))
    tampered = tmp_path / "attached.pdf"
    tampered.write_bytes(minimal_pdf(LINES + ["Our AI programme delivered S$900 million in savings."]))  # not the published document
    ingest_document(subj_yaml, tampered, "annual_report-2025", tmp_path / "out", supplied_by="unknown")
    subject = load_subject(subj_yaml)
    ctx = RunContext.build(subject, tmp_path / "out" / "pdfco", tmp_path / "data", as_of=AS_OF)
    out = run_subject(subject, ctx.out_dir, tmp_path / "data", modules=["annual-report"], as_of=AS_OF, ctx=ctx)
    # the module cannot read a MISMATCH source (not citable): no rubric, a gap, nothing released
    assert not out.claims and not any(s.id.endswith(".rubric") for s in out.signals)
    assert any("MISMATCH" in g.detail for g in out.gaps)
    row = out.attached_documents[0]
    assert row["reconciliation"] == "MISMATCH" and row["state"] == "ATTACHED" and row["reconciled_sha256"] != row["sha256"]
    gap_md = (out.out_dir / "gap-register.md").read_text()
    assert "MISMATCH** — the attached file is not the document at the declared URL" in gap_md
    ctx.store.close()


def test_offline_prefers_attachment_over_404_without_local_file(tmp_path):
    """Document declared with no local_file, URL unreachable offline (404 -> DEAD):
    the attached copy is used and labelled."""
    subj_yaml = _subject_yaml(tmp_path, local_file=None)
    pdf = tmp_path / "ar.pdf"
    pdf.write_bytes(minimal_pdf(LINES))
    ingest_document(subj_yaml, pdf, URL, tmp_path / "out")  # the URL itself is a valid --doc key
    subject = load_subject(subj_yaml)
    ctx = RunContext.build(subject, tmp_path / "out" / "pdfco", tmp_path / "data", offline=True, as_of=AS_OF)
    src = ctx.fetch("annual-report", URL)
    assert src.state == SourceState.ATTACHED and src.citable and src.attached_label == ATTACHED_LABEL and src.tier.value == "T2"
    ctx.store.close()
