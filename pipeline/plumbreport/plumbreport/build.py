"""Build: bind -> (re-check quotations) -> HTML -> lint -> PDF (two passes for contents)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import lint as lintmod
from .data import load_research, load_run, load_storyline
from .render import (check_quotes, find_section_pages, html_to_pdf, pdf_pages_text,
                     render_html)
from .spec import BindingError, bind, load_spec


@dataclass
class BuildResult:
    ok: bool
    out: Path
    pages: int
    lint: dict


class LintFailed(Exception):
    pass


def build(spec_path, run_dir, storyline_path, research_path, out_dir, *, strict=False,
          source_pdf=None, pdf=True) -> BuildResult:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spec = load_spec(spec_path)
    run = load_run(run_dir)
    story = load_storyline(storyline_path)
    research = load_research(research_path) if research_path else None

    model = bind(spec, run, story, research, strict=strict)     # raises BindingError

    quote_errors = check_quotes(model["quotes"], Path(source_pdf)) if source_pdf else []
    if quote_errors:
        raise BindingError("quotations do not match the source document:\n  " + "\n  ".join(quote_errors))

    html = render_html(model)
    errors = lintmod.lint_html(html)
    report = {
        "ok": False, "strict": strict, "errors": errors,
        "binding": model["binding"],
        "quotations_checked_against_source": len(model["quotes"]) if source_pdf else 0,
        "sections": [{"id": s["id"], "label": s["label"], "title": s["title"]} for s in model["sections"]],
    }
    if errors or not pdf:
        (out / "report.html").write_text(html, encoding="utf-8")
        report["ok"] = not errors
        (out / "lint.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return BuildResult(ok=not errors, out=out, pages=0, lint=report)

    pdf_path = out / "report.pdf"
    toc: dict[str, int] = {}
    pages_text: list[str] = []
    for _ in range(3):                     # contents numbers settle in two passes
        html = render_html(model, toc)
        html_to_pdf(html, pdf_path, out)
        pages_text = pdf_pages_text(pdf_path)
        found = find_section_pages(pdf_path, model["sections"])
        if found == toc:
            break
        toc = found
    missing = [s["id"] for s in model["sections"] if s["id"] not in toc]

    errors = lintmod.lint_html(html)
    for i, t in enumerate(pages_text, 1):
        errors += lintmod.lint_text(t, f"report.pdf page {i}")
    report.update({"ok": not errors and not missing, "errors": errors, "pages": len(pages_text),
                   "section_pages": toc, "sections_not_located": missing})
    (out / "report.html").write_text(html, encoding="utf-8")
    (out / "lint.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        pdf_path.unlink(missing_ok=True)   # a failed lint never leaves a client PDF behind
    return BuildResult(ok=report["ok"], out=out, pages=len(pages_text), lint=report)
