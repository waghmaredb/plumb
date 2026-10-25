"""PDF extraction, magic-byte content-type detection and page-aware citations (v0.2)."""
import json

from plumbverify.extract import (
    PAGE_SEP, extract_document, extract_main_text, extract_pdf, page_of, sniff_content_type,
    split_passages, split_passages_paged,
)
from plumbverify.match import normalize
from plumbverify.models import CitationStatus, ConfidenceLabel, SourceState
from plumbverify.pipeline import Verifier, load_claims
from plumbverify.tier import load_tier_rules

from .conftest import REPORT_HTML, REPORT_PDF, SCANNED_PDF

RULES = load_tier_rules(overrides={"tiers": {"T1": {"domains": ["example-gov.sg"]},
                                             "T3": {"domains": ["example-press.org", "example-wire.com"]}}})


# ---- content-type sniffing -------------------------------------------------
def test_sniff_magic_bytes_beat_declared_header():
    assert sniff_content_type(REPORT_PDF, "text/html; charset=utf-8") == "application/pdf"
    assert sniff_content_type(b"\n  %PDF-1.7 ...", None) == "application/pdf"
    assert sniff_content_type(REPORT_HTML.encode(), "application/pdf") == "text/html"
    assert sniff_content_type(b"<html><body>x</body></html>", None) == "text/html"
    assert sniff_content_type(b"plain words", "text/csv; charset=utf-8") == "text/csv"
    assert sniff_content_type(b"plain words", None) == "text/plain"
    assert sniff_content_type(b"\x89PNG\r\n", "text/html") == "image/png"
    assert sniff_content_type(b"PK\x03\x04zip", None) == "application/zip"


# ---- PDF text, pages -------------------------------------------------------
def test_extract_pdf_pages_and_engine():
    pdf = extract_pdf(REPORT_PDF)
    assert pdf.engine in ("pypdf", "pdfminer") and pdf.page_count == 2 and not pdf.needs_ocr
    assert "A$440,000" in pdf.pages[0].text
    assert "3% and 13%" in pdf.pages[1].text
    assert PAGE_SEP in pdf.text


def test_extract_document_pdf_is_page_aware():
    ex = extract_document(REPORT_PDF, "text/html")  # mislabelled header, magic wins
    assert ex.content_type == "application/pdf" and ex.page_count == 2 and not ex.needs_ocr
    paged = split_passages_paged(ex.text)
    pages = {p.page for p in paged}
    assert pages == {1, 2}
    assert any("A$440,000" in p.text and p.page == 1 for p in paged)
    assert any("13%" in p.text and p.page == 2 for p in paged)
    # legacy splitter still works and treats the page separator as a break
    legacy = split_passages(ex.text)
    assert len(legacy) == len(paged) and all(PAGE_SEP not in p for p in legacy)
    # back-compat wrapper
    assert "fabricated references" in extract_main_text(REPORT_PDF, "application/pdf")


def test_page_of_locates_fragment_after_normalisation():
    text = extract_main_text(REPORT_PDF, "application/pdf")
    assert page_of(text, "The substance of the independent review is retained", normalize) == 2
    assert page_of(text, "a$440,000", normalize) == 1
    assert page_of(text, "not in the document", normalize) is None
    assert page_of("single page no separator", "single", normalize) is None  # not paginated


def test_scanned_pdf_flags_needs_ocr_not_empty_string():
    pdf = extract_pdf(SCANNED_PDF)
    assert pdf.needs_ocr is True and pdf.page_count == 2
    ex = extract_document(SCANNED_PDF, "application/pdf")
    assert ex.needs_ocr is True and ex.text == ""


def test_corrupt_pdf_reports_error_without_raising():
    pdf = extract_pdf(b"%PDF-1.4 garbage without xref or pages")
    assert pdf.engine is None or pdf.page_count == 0
    assert pdf.error or pdf.needs_ocr


def test_html_and_text_paths_have_no_pages():
    ex = extract_document(REPORT_HTML.encode(), "text/html")
    assert ex.content_type == "text/html" and ex.page_count is None and not ex.needs_ocr
    assert all(p.page is None for p in split_passages_paged(ex.text))


# ---- fetch + pipeline: citations carry p. N -------------------------------
def test_fetch_pdf_records_detected_type_pages_and_recheck(fetcher):
    src = fetcher.fetch("https://docs.example-gov.sg/mislabelled")
    assert src.state == SourceState.FETCHED
    assert src.content_type.startswith("text/html") and src.detected_content_type == "application/pdf"
    assert src.page_count == 2 and not src.needs_ocr and src.recheck_after is not None
    assert (src.recheck_after - src.fetched_at).total_seconds() == 24 * 3600
    scan = fetcher.fetch("https://docs.example-gov.sg/scan.pdf")
    assert scan.needs_ocr and scan.text_extract == "" and scan.citable and "OCR" in scan.error


def test_pipeline_citation_carries_page_number(fetcher, store, tmp_path):
    claims_path = tmp_path / "claims.json"
    claims_path.write_text(json.dumps({"claims": [
        {"id": "n1", "text": "The department commissioned the report for A$440,000", "kind": "number", "load_bearing": False,
         "confidence_label": "filed", "sources": ["https://docs.example-gov.sg/review.pdf"]},
        {"id": "q1", "text": "The substance of the independent review is retained, and there are no changes to the recommendations.",
         "kind": "quote", "sources": ["https://docs.example-gov.sg/review.pdf"]},
        {"id": "f1", "text": "fabricated references were found", "kind": "fact",
         "sources": ["https://docs.example-gov.sg/review.pdf"]},
        {"id": "s1", "text": "fabricated references were found", "kind": "fact",
         "sources": ["https://docs.example-gov.sg/scan.pdf"]},
    ]}))
    v = Verifier(fetcher=fetcher, store=store, tier_rules=RULES)
    report = v.run(load_claims(claims_path))
    cites = {c.claim_id: c for c in report.citations}
    assert cites["n1"].status == CitationStatus.verified and cites["n1"].page == 1
    assert cites["q1"].status == CitationStatus.verified and cites["q1"].page == 2
    assert cites["q1"].locator.endswith("(p. 2)")
    assert cites["f1"].status == CitationStatus.verified and cites["f1"].page == 1
    assert cites["s1"].status == CitationStatus.unverified and any("OCR" in r for r in cites["s1"].reasons)
    d = {x.claim_id: x for x in report.decisions}
    assert not d["n1"].blocked and not d["q1"].blocked and d["s1"].blocked
    # report JSON round-trips the new fields
    data = json.loads(report.model_dump_json())
    assert data["citations"][1]["page"] == 2
    assert any(s["needs_ocr"] for s in data["sources"])
