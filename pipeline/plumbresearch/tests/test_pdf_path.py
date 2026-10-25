"""The real-mode path: a local PDF placed in data/<slug>/ is served under its
declared IR URL, text-extracted through the PdfAwareFetcher shim, scored, and
the lifted quotations / numbers verify against the stored copy."""
from pathlib import Path

from plumbverify.pipeline import Verifier

from plumbresearch.context import RunContext, extract_pdf_text
from plumbresearch.modules import annual_report
from plumbresearch.subject import Document, Subject

from .conftest import AS_OF

LINES = [
    "Acme Bank Annual Report 2025 - Technology and data",
    "Our AI-powered underwriting assistant was rolled out across all",
    "branches in 2025 and reduced turnaround time by 40%. The generative",
    "AI contact centre assistant is live and handles customer service",
    "enquiries. We committed S$300 million to technology and AI over",
    "three years. Our responsible AI framework mandates model risk",
    "validation and human oversight, and the Board reviews AI risk",
    "quarterly.",
]


def minimal_pdf(lines: list[str]) -> bytes:
    """Dependency-free single-page PDF with Helvetica text, one line per Tj."""
    esc = lambda s: s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = "BT /F1 11 Tf 50 750 Td 14 TL " + " ".join(f"({esc(l)}) Tj T*" for l in lines) + " ET"
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            f"<< /Length {len(content)} >>\nstream\n{content}\nendstream", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offs = "%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offs)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


def test_pdf_extract_unwraps_lines():
    text = extract_pdf_text(minimal_pdf(LINES))
    assert "rolled out across all branches in 2025" in text  # wrapped line joined with a space
    assert "S$300 million to technology and AI over three years" in text


def test_local_pdf_served_under_ir_url_scores_and_verifies(tmp_path):
    data = tmp_path / "data" / "pdfco"
    data.mkdir(parents=True)
    (data / "ar-2025.pdf").write_bytes(minimal_pdf(LINES))
    url = "https://ir.pdfco.example/annual-report-2025.pdf"
    subj = Subject(slug="pdfco", name="PDF Co", short_name="PDF Co", sector="banks", listing={"exchange": "X"}, latest_fy=2025,
                   documents=[Document(kind="annual_report", fy=2025, url=url, local_file="ar-2025.pdf")],
                   tier_overrides={"T2": ["pdfco.example"]})
    ctx = RunContext.build(subj, tmp_path / "out", tmp_path / "data", offline=True, as_of=AS_OF)
    res = annual_report.run(subj, ctx.store, ctx.log, ctx)
    rub = next(s for s in res.signals if s.id.endswith(".rubric"))
    assert rub.value == 4, rub.detail  # 2 production use cases, 1 quantified, investment disclosed, governance+board -> L4 (quantified < 2 for L5)
    assert rub.tier.value == "T2"
    kinds = {c.kind.value for c in res.claims}
    assert {"quote", "number"} <= kinds
    src = ctx.store.lookup_url(url)
    assert src and src["text_extract"] and "rolled out across all branches" in src["text_extract"]  # shim wrote the text back to the store
    report = Verifier(fetcher=ctx.fetcher, store=ctx.store, log=ctx.log, tier_rules=ctx.tier_rules).run(list(res.claims))
    assert report.build_pass, [(g.claim_id, g.reasons) for g in report.gap_register]
    ctx.store.close()


def test_missing_local_pdf_is_a_gap_not_a_crash(tmp_path):
    url = "https://ir.pdfco.example/annual-report-2025.pdf"
    subj = Subject(slug="pdfco", name="PDF Co", short_name="PDF Co", sector="banks", listing={"exchange": "X"}, latest_fy=2025,
                   documents=[Document(kind="annual_report", fy=2025, url=url, local_file="ar-2025.pdf")])
    ctx = RunContext.build(subj, tmp_path / "out", tmp_path / "data", offline=True, as_of=AS_OF)
    res = annual_report.run(subj, ctx.store, ctx.log, ctx)
    assert not res.data_available and any("local file missing" in g.detail for g in res.gaps)
    assert ctx.budget("annual-report").calls == 0  # no fetch attempted for a declared-but-absent local file
    ctx.store.close()
