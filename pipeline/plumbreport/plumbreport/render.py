"""HTML (Jinja2) and PDF (Playwright Chromium) rendering, with a two-pass contents page."""
from __future__ import annotations

import io
import re
import subprocess
from pathlib import Path

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

TEMPLATES = Path(__file__).parent / "templates"


def _inline_md(text: str) -> Markup:
    """Light inline Markdown (emphasis, links) without wrapping <p>."""
    html = md.markdown(str(escape(text)).replace("&#39;", "'").replace("&#34;", '"'),
                       extensions=["smarty"])
    html = re.sub(r"^<p>(.*)</p>$", r"\1", html.strip(), flags=re.S)
    return Markup(html)


def _typo(text: str) -> str:
    """Typographic quotes and dashes for authored text."""
    t = re.sub(r"(^|[\s(\[])\"", "\\1\u201c", text)
    t = t.replace('"', "\u201d")
    t = re.sub(r"(^|[\s(\[])'", "\\1\u2018", t)
    t = t.replace("'", "\u2019").replace(" -- ", " \u2013 ").replace(" - ", " \u2013 ")
    return t


def _url(u: str) -> Markup:
    """Display a long URL with break opportunities after / and before ?&."""
    shown = re.sub(r"^https?://", "", u)
    shown = str(escape(shown))
    shown = re.sub(r"([/_.-])", "\\1\u200b", shown)
    return Markup(f'<a href="{escape(u)}">{shown}</a>')


def environment() -> Environment:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)),
                      autoescape=select_autoescape(["html", "j2"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["md"] = lambda s: _inline_md(_typo(s or ""))
    env.filters["typo"] = lambda s: _typo(s or "")
    env.filters["url"] = _url
    return env


def render_html(model: dict, toc_pages: dict[str, int] | None = None) -> str:
    env = environment()
    css = (TEMPLATES / "report.css").read_text(encoding="utf-8")
    r = model["report"]
    header = f"{r['client']} \u00b7 {r['title']}"
    footer_left = " \u00b7 ".join(x for x in [r.get("prepared_by", ""), r.get("status", "")] if x)
    css = (css.replace("__HEADER__", _css_str(header)).replace("__FOOTER__", _css_str(footer_left)))
    return env.get_template("report.html.j2").render(m=model, r=r, css=Markup(css),
                                                      toc_pages=toc_pages or {})


def _css_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def html_to_pdf(html: str, out_pdf: Path, base_dir: Path) -> None:
    from playwright.sync_api import sync_playwright
    tmp = base_dir / ".render.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page()
            page.goto(tmp.resolve().as_uri())
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(out_pdf), format="A4", prefer_css_page_size=True,
                     print_background=True, display_header_footer=False)
            b.close()
    finally:
        tmp.unlink(missing_ok=True)


def pdf_pages_text(pdf: Path) -> list[str]:
    from pypdf import PdfReader
    return [(pg.extract_text() or "") for pg in PdfReader(str(pdf)).pages]


def find_section_pages(pdf: Path, sections: list[dict], start: int = 2) -> dict[str, int]:
    """1-based page of each section: from the PDF's named destinations (Chromium writes one
    per linked id), falling back to a whitespace-insensitive search for the heading."""
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    found: dict[str, int] = {}
    try:
        for name, dest in reader.named_destinations.items():
            key = str(name).lstrip("/")
            page = reader.get_destination_page_number(dest)
            if page is not None and page >= 0:
                found[key] = page + 1
    except Exception:  # pragma: no cover - destinations are a convenience
        found = {}
    out = {s["id"]: found[s["id"]] for s in sections if s["id"] in found}
    if len(out) == len(sections):
        return out
    texts = [re.sub(r"\s+", " ", (pg.extract_text() or "")) for pg in reader.pages]
    for s in sections:
        if s["id"] in out:
            continue
        title = re.sub(r"\s+", " ", s["title"]).strip()
        for i in range(start, len(texts)):
            if title in texts[i]:
                out[s["id"]] = i + 1
                break
    return out


def check_quotes(quotes: list[dict], source_pdf: Path) -> list[str]:
    """Re-read every quotation from the source PDF page; word-for-word after whitespace and
    quote-mark normalisation."""
    def norm(s: str) -> str:
        s = (s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"')
             .replace("\u201d", '"'))
        s = re.sub(r"-\s*\n\s*", "", s)
        return re.sub(r"\s+", " ", s).strip()
    cache: dict[int, str] = {}
    errs = []
    for q in quotes:
        p = q["pdf_page"]
        if p not in cache:
            out = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(source_pdf), "-"],
                                 capture_output=True, text=True, check=True).stdout
            cache[p] = norm(out)
        if norm(q["text"]) not in cache[p]:
            errs.append(f"{q['where']}: quotation not found word for word on PDF page {p}: "
                        f"{q['text'][:70]}...")
    return errs
