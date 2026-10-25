"""Main-text extraction and passage splitting (feeds spec C3/C4).

v0.2 adds PDF support: pypdf first (pure Python), pdfminer.six as a
fallback when installed. PDF text is page-aware so a citation can carry
``p. N``; pages are joined with PAGE_SEP (form feed) inside ``text_extract``
and recovered by :func:`split_passages_paged`. A PDF with no text layer
(scanned) is reported with ``needs_ocr=True`` instead of an empty string.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

try:  # optional, better boilerplate removal
    import trafilatura  # type: ignore
except Exception:  # pragma: no cover
    trafilatura = None

try:  # preferred PDF engine (pure Python)
    import pypdf  # type: ignore
except Exception:  # pragma: no cover
    pypdf = None

try:  # fallback PDF engine
    from pdfminer.high_level import extract_text as _pdfminer_extract_text  # type: ignore
    from pdfminer.pdfpage import PDFPage as _PDFPage  # type: ignore
except Exception:  # pragma: no cover
    _pdfminer_extract_text = None
    _PDFPage = None

_WS = re.compile(r"\s+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")

PAGE_SEP = "\f"
#: average characters of real text per page below which a PDF is treated as scanned
OCR_MIN_CHARS_PER_PAGE = 20


# --------------------------------------------------------------------------
# Content-type detection (magic bytes first, declared header second)
# --------------------------------------------------------------------------
_MAGIC: list[tuple[bytes, str]] = [
    (b"%PDF-", "application/pdf"),
    (b"\x1f\x8b", "application/gzip"),
    (b"PK\x03\x04", "application/zip"),
    (b"\x89PNG", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF8", "image/gif"),
]
_HTML_HINT = re.compile(rb"<\s*(!doctype\s+html|html|head|body|p|div|main|article)\b", re.I)


def sniff_content_type(raw: bytes | str, declared: Optional[str] = None) -> str:
    """Return the effective media type. Magic bytes win over the declared
    header (servers mislabel PDFs as text/html often enough to matter for
    spec C1 evidence integrity); the header breaks ties for text types."""
    if isinstance(raw, str):
        head = raw[:4096].encode("utf-8", errors="ignore")
    else:
        head = raw[:4096]
    lead = head.lstrip(b"\xef\xbb\xbf \t\r\n")
    for magic, mt in _MAGIC:
        if lead.startswith(magic):
            return mt
    # some generators put junk before %PDF-; scan the first 1 KiB
    if b"%PDF-" in head[:1024]:
        return "application/pdf"
    base = (declared or "").split(";")[0].strip().lower()
    if base == "application/pdf":
        return "text/html" if _HTML_HINT.search(lead) else "application/octet-stream"
    if _HTML_HINT.search(lead):
        return "text/html"
    if base:
        return base
    return "text/plain"


# --------------------------------------------------------------------------
# PDF extraction
# --------------------------------------------------------------------------
@dataclass
class PageText:
    page: int  # 1-based
    text: str


@dataclass
class PdfExtraction:
    pages: list[PageText] = field(default_factory=list)
    page_count: int = 0
    needs_ocr: bool = False
    engine: Optional[str] = None
    error: Optional[str] = None

    @property
    def text(self) -> str:
        """Page-aware text: pages joined with PAGE_SEP (wrapped in newlines so
        :func:`split_passages` still sees a paragraph break)."""
        return f"\n{PAGE_SEP}\n".join(p.text for p in self.pages)

    @property
    def char_count(self) -> int:
        return sum(len(p.text) for p in self.pages)


def _pypdf_pages(raw: bytes) -> list[PageText]:
    reader = pypdf.PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            pass
    out: list[PageText] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        out.append(PageText(page=i, text=normalize_text(txt)))
    return out


def _pdfminer_pages(raw: bytes) -> list[PageText]:
    n = sum(1 for _ in _PDFPage.get_pages(io.BytesIO(raw)))
    out: list[PageText] = []
    for i in range(n):
        try:
            txt = _pdfminer_extract_text(io.BytesIO(raw), page_numbers=[i]) or ""
        except Exception:
            txt = ""
        out.append(PageText(page=i + 1, text=normalize_text(txt)))
    return out


def extract_pdf(raw: bytes, min_chars_per_page: int = OCR_MIN_CHARS_PER_PAGE) -> PdfExtraction:
    """Extract text per page. pypdf is tried first; pdfminer.six when pypdf is
    missing, fails, or yields no text. A document whose text layer averages
    fewer than ``min_chars_per_page`` characters per page is flagged
    ``needs_ocr`` (scanned or image-only PDF) rather than returned as ''."""
    result = PdfExtraction()
    errors: list[str] = []
    engines = []
    if pypdf is not None:
        engines.append(("pypdf", _pypdf_pages))
    if _pdfminer_extract_text is not None and _PDFPage is not None:
        engines.append(("pdfminer", _pdfminer_pages))
    if not engines:
        result.error = "no PDF engine installed (pip install pypdf or pdfminer.six)"
        result.needs_ocr = False
        return result
    for name, fn in engines:
        try:
            pages = fn(raw)
        except Exception as e:  # corrupt file or engine failure: try the next engine
            errors.append(f"{name}: {type(e).__name__}: {e}")
            continue
        result.pages, result.page_count, result.engine = pages, len(pages), name
        if result.char_count >= min_chars_per_page * max(1, len(pages)):
            break  # good enough; do not pay for the fallback
    if result.engine is None:
        result.error = "; ".join(errors) or "PDF extraction failed"
        return result
    if result.page_count == 0 or result.char_count < min_chars_per_page * result.page_count:
        result.needs_ocr = True
    if errors:
        result.error = "; ".join(errors)
    return result


# --------------------------------------------------------------------------
# Generic document extraction
# --------------------------------------------------------------------------
@dataclass
class Extraction:
    text: str
    content_type: str
    needs_ocr: bool = False
    page_count: Optional[int] = None
    engine: Optional[str] = None
    error: Optional[str] = None


def _bs4_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "form", "iframe"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    blocks: list[str] = []
    for el in main.find_all(["p", "h1", "h2", "h3", "h4", "li", "td", "th", "blockquote", "pre"]):
        t = el.get_text(" ", strip=True)
        if t:
            blocks.append(t)
    if not blocks:
        blocks = [main.get_text(" ", strip=True)]
    return "\n\n".join(blocks)


def _html_text(text: str) -> str:
    if trafilatura is not None:
        try:
            out = trafilatura.extract(text, include_comments=False, include_tables=True, favor_recall=True)
            if out and len(out) > 80:
                return normalize_text(out)
        except Exception:
            pass
    return normalize_text(_bs4_text(text))


def extract_document(raw: bytes | str, content_type: Optional[str] = None) -> Extraction:
    """Full extraction result with detected media type, OCR flag and page count."""
    detected = sniff_content_type(raw, content_type)
    if detected == "application/pdf":
        data = raw if isinstance(raw, bytes) else raw.encode("latin-1", errors="ignore")
        pdf = extract_pdf(data)
        return Extraction(text="" if pdf.needs_ocr else pdf.text, content_type=detected, needs_ocr=pdf.needs_ocr,
                          page_count=pdf.page_count, engine=pdf.engine, error=pdf.error)
    if detected.startswith(("image/", "application/zip", "application/gzip", "application/octet-stream")):
        return Extraction(text="", content_type=detected, error=f"binary content ({detected}) has no text layer")
    text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
    if detected == "text/html":
        return Extraction(text=_html_text(text), content_type=detected)
    return Extraction(text=normalize_text(text), content_type=detected)


def extract_main_text(raw: bytes | str, content_type: Optional[str] = None) -> str:
    """Return the main text of a document (backwards-compatible wrapper around
    :func:`extract_document`). HTML goes through trafilatura when available
    (bs4 block extractor otherwise); PDFs return page-aware text joined with
    PAGE_SEP; scanned PDFs return '' (check ``extract_document(...).needs_ocr``)."""
    return extract_document(raw, content_type).text


def normalize_text(text: str) -> str:
    lines = [_WS.sub(" ", ln).strip() for ln in text.split("\n")]
    out: list[str] = []
    for ln in lines:
        if ln:
            out.append(ln)
        elif out and out[-1] != "":
            out.append("")
    return "\n".join(out).strip()


def split_passages(text: str, max_chars: int = 600, min_chars: int = 40) -> list[str]:
    """Split extracted text into passages: paragraphs first, then sentence
    windows for long paragraphs. Short fragments are merged forward. Page
    separators are treated as paragraph breaks."""
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n|" + PAGE_SEP, text) if p.strip()]
    passages: list[str] = []
    buf = ""
    for p in paras:
        if len(p) <= max_chars:
            chunks = [p]
        else:
            chunks, cur = [], ""
            for s in _SENT_SPLIT.split(p):
                if cur and len(cur) + len(s) + 1 > max_chars:
                    chunks.append(cur)
                    cur = s
                else:
                    cur = f"{cur} {s}".strip()
            if cur:
                chunks.append(cur)
        for c in chunks:
            if buf:
                c = f"{buf} {c}"
                buf = ""
            if len(c) < min_chars:
                buf = c
            else:
                passages.append(c)
    if buf:
        passages.append(buf)
    return passages


@dataclass(frozen=True)
class Passage:
    text: str
    page: Optional[int] = None  # 1-based; None for non-paginated sources


def split_pages(text: str) -> list[PageText]:
    """Recover per-page text from a PAGE_SEP-joined extract. A text without
    separators is a single page numbered 1 only if it came from a PDF; callers
    that do not know should use :func:`split_passages_paged`."""
    if PAGE_SEP not in text:
        return [PageText(page=1, text=text)]
    return [PageText(page=i, text=t.strip()) for i, t in enumerate(text.split(PAGE_SEP), start=1)]


def split_passages_paged(text: str, max_chars: int = 600, min_chars: int = 40) -> list[Passage]:
    """Page-aware passage split. Texts with no PAGE_SEP yield ``page=None``."""
    if not text:
        return []
    if PAGE_SEP not in text:
        return [Passage(text=p) for p in split_passages(text, max_chars, min_chars)]
    out: list[Passage] = []
    for pg in split_pages(text):
        for p in split_passages(pg.text, max_chars, min_chars):
            out.append(Passage(text=p, page=pg.page))
    return out


def page_of(text: str, fragment: str, normalizer=None) -> Optional[int]:
    """Locate the page that contains ``fragment`` (after optional normalisation).
    Returns None when the text is not paginated or the fragment is not found."""
    if not text or not fragment or PAGE_SEP not in text:
        return None
    norm = normalizer or (lambda s: s)
    frag = norm(fragment)
    for pg in split_pages(text):
        if frag and frag in norm(pg.text):
            return pg.page
    return None
