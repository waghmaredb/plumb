"""Main-text extraction and passage splitting (feeds spec C3/C4).

v0.2 adds PDF support: pypdf first (pure Python), pdfminer.six as a
fallback when installed. PDF text is page-aware so a citation can carry
``p. N``; pages are joined with PAGE_SEP (form feed) inside ``text_extract``
and recovered by :func:`split_passages_paged`. A PDF with no text layer
(scanned) is reported with ``needs_ocr=True`` instead of an empty string.

v0.3.1 adds a layout-aware path for multi-column PDFs (annual reports are
mostly two-column): ``pdftotext -layout`` (poppler) when the binary is on
PATH, else pdfplumber when installed, else pypdf / pdfminer as before. The
layout engines keep the horizontal geometry of each line, which lets
:func:`split_columns` detect pages whose lines share a wide interior gap at a
stable x-offset and re-order them left column first, then right column, so
sentences from adjacent columns no longer interleave (a C5 quotation lifted
from a two-column page then exact-matches the stored text). The engine that
produced the text is reported in ``Extraction.engine`` / ``PdfExtraction.engine``.
"""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

try:  # optional, better boilerplate removal
    import trafilatura  # type: ignore
except Exception:  # pragma: no cover
    trafilatura = None

try:  # layout-aware PDF engine (pure Python); second choice after pdftotext
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    pdfplumber = None

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


# ---- column handling for layout-preserving engines ---------------------
#: a run of at least this many spaces inside a line is a candidate column gutter
COLUMN_GAP_MIN_SPACES = 6
#: share of a page's non-blank lines that must show the gutter at the same x-offset
COLUMN_MIN_LINE_SHARE = 0.40
#: the same share for a gutter inside an already split column (third column, pull quote)
COLUMN_INNER_LINE_SHARE = 0.25
#: a column must be at least this wide (characters) to be split off
COLUMN_MIN_WIDTH = 12
_GAP_RE = re.compile(r" {%d,}" % COLUMN_GAP_MIN_SPACES)
_LINE_GAP_RE = re.compile(r" {2,}")


def _tab_expand(line: str) -> str:
    return line.expandtabs(8).rstrip("\r\n")


def find_column_gutter(lines: list[str], min_share: float = COLUMN_MIN_LINE_SHARE) -> Optional[int]:
    """Return the x-offset where the right column starts, or None.

    Two kinds of line vote for a gutter position: a line with text on both
    sides of a run of >= COLUMN_GAP_MIN_SPACES spaces votes for every x inside
    that run, and a line that is indented by at least ``2 * COLUMN_MIN_WIDTH``
    spaces (a right-column-only line: the left column's lines sit at other
    y-positions, which is the common case in a two-column layout dump) votes
    for every x up to its first character. The best x wins when at least
    ``min_share`` of the non-blank lines vote for it; it is then snapped to
    the most common first-character position of the right column."""
    nonblank = [ln for ln in lines if ln.strip()]
    if len(nonblank) < 3:
        return None
    votes: dict[int, int] = {}
    for ln in nonblank:
        seen: set[int] = set()
        indent = len(ln) - len(ln.lstrip(" "))
        if indent >= 2 * COLUMN_MIN_WIDTH:
            for x in range(COLUMN_MIN_WIDTH, indent + 1):
                seen.add(x)
                votes[x] = votes.get(x, 0) + 1
            continue
        for m in _GAP_RE.finditer(ln):
            if m.start() < COLUMN_MIN_WIDTH or m.end() >= len(ln):
                continue  # too far left to be a column, or trailing padding
            if not ln[: m.start()].strip() or not ln[m.end():].strip():
                continue
            for x in range(m.start() + 1, m.end() + 1):
                if x not in seen:
                    seen.add(x)
                    votes[x] = votes.get(x, 0) + 1
    if not votes:
        return None
    best_x = max(votes, key=lambda x: (votes[x], x))
    if votes[best_x] < max(3, int(min_share * len(nonblank) + 0.999)):
        return None
    # snap to the right column's first character among the voting lines
    starts: dict[int, int] = {}
    for ln in nonblank:
        if len(ln) > best_x and ln[best_x - 1] == " " and ln[best_x:].strip():
            s = best_x + (len(ln[best_x:]) - len(ln[best_x:].lstrip()))
            starts[s] = starts.get(s, 0) + 1
    if not starts:
        return None
    # the right column's left edge is the smallest well-supported start: numbered paragraphs and
    # bullets begin at the edge while the bulk of the lines are indented a few characters further
    support = max(2, int(0.05 * sum(starts.values()) + 0.999))
    x = min(s for s, n in starts.items() if n >= support) if any(n >= support for n in starts.values()) \
        else max(starts, key=lambda s: (starts[s], -s))
    # the left column must hold real text too, else this is an indented single column
    left_chars = sum(len(ln[:x].strip()) for ln in nonblank)
    right_chars = sum(len(ln[x:].strip()) for ln in nonblank)
    if left_chars < COLUMN_MIN_WIDTH * 3 or right_chars < COLUMN_MIN_WIDTH * 3:
        return None
    return x


def _split_point(ln: str, x: int) -> Optional[int]:
    """Where the right column starts on this line, given the page gutter at
    x; None when the line crosses the gutter (full-width heading, table row).
    Blank and left-only lines split at their end, right-only lines at their
    first character. A line whose gutter run is a few characters off x (a
    quote mark or bullet at the start of the right column, a hanging indent)
    still splits at the end of its own gap."""
    if not ln.strip() or len(ln) <= x:
        return len(ln)
    if not ln[:x].strip():
        return x  # right-only line; slicing at x keeps the column's own geometry for a recursive split
    # once the page's gutter is known, a narrower run of spaces at the gutter is enough for an
    # individual line: pdftotext -layout squeezes a long left-column line to within 2-5 spaces of
    # the right column
    for m in _LINE_GAP_RE.finditer(ln):
        if m.start() <= x - 2 and m.end() >= x - 3:
            return min(m.end(), x) if m.end() >= x else m.end()
    return None


def split_columns(page_text: str, depth: int = 2, min_share: Optional[float] = None) -> str:
    """Re-order a layout-preserved page into reading order.

    Lines are grouped into blocks: runs of lines that respect the detected
    gutter (two-column text) and runs that cross it (full-width headings,
    tables, captions). Full-width blocks stay in place; inside a two-column
    block the left column is emitted first, then the right column. Each
    column is split again (``depth`` - 1) so a three-column management page
    comes out column by column. Pages without a stable gutter are returned
    unchanged apart from tab expansion."""
    lines = [_tab_expand(ln) for ln in page_text.split("\n")]
    # a column that is itself split (three-column pages, pull quotes) shows its inner gutter on
    # fewer lines, so the share threshold is relaxed below the page level
    x = find_column_gutter(lines, min_share if min_share is not None else COLUMN_MIN_LINE_SHARE) if depth > 0 else None
    if x is None:
        return "\n".join(ln.rstrip() for ln in lines)
    out: list[str] = []
    block: list[tuple[str, Optional[int]]] = []
    block_split: Optional[bool] = None

    def flush() -> None:
        nonlocal block
        if not block:
            return
        if block_split:
            left = [ln[:sp].rstrip() for ln, sp in block]
            right = [ln[sp:].rstrip() for ln, sp in block if sp is not None and len(ln) > sp]
            if any(l.strip() for l in left) and any(r.strip() for r in right):
                out.extend(_strip_blank_edges(split_columns("\n".join(left), depth - 1, COLUMN_INNER_LINE_SHARE).split("\n")))
                out.append("")
                out.extend(_strip_blank_edges(split_columns("\n".join(right), depth - 1, COLUMN_INNER_LINE_SHARE).split("\n")))
                out.append("")
            else:  # text on one side only: indented or short lines, keep as is
                out.extend(ln.strip() for ln, _ in block)
        else:
            out.extend(ln.rstrip() for ln, _ in block)
        block = []

    for ln in lines:
        sp = _split_point(ln, x)
        if not ln.strip():
            block.append((ln, sp))  # blank lines belong to the current block
            continue
        is_split = sp is not None
        if block_split is None or is_split == block_split:
            block.append((ln, sp))
            block_split = is_split
        else:
            flush()
            block = [(ln, sp)]
            block_split = is_split
    flush()
    return "\n".join(out)


def _strip_blank_edges(lines: list[str]) -> list[str]:
    a, b = 0, len(lines)
    while a < b and not lines[a].strip():
        a += 1
    while b > a and not lines[b - 1].strip():
        b -= 1
    return lines[a:b]


def _layout_pages(page_texts: list[str]) -> list[PageText]:
    return [PageText(page=i, text=normalize_text(split_columns(t))) for i, t in enumerate(page_texts, start=1)]


def pdftotext_available() -> bool:
    return shutil.which("pdftotext") is not None


def _pdftotext_pages(raw: bytes) -> list[PageText]:
    """poppler ``pdftotext -layout``: one form feed per page; the geometry of
    each line is preserved so the column splitter can work."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(raw)
        proc = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=300)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext exit {proc.returncode}: {proc.stderr.decode('utf-8', 'replace').strip()[:200]}")
    text = proc.stdout.decode("utf-8", errors="replace")
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]  # pdftotext ends the last page with a form feed
    if not pages:
        raise RuntimeError("pdftotext returned no pages")
    return _layout_pages(pages)


def _pdfplumber_pages(raw: bytes) -> list[PageText]:
    texts: list[str] = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            try:
                texts.append(page.extract_text(layout=True) or "")
            except Exception:
                texts.append("")
    return _layout_pages(texts)


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


ENGINE_PDFTOTEXT = "pdftotext-layout"
ENGINE_PDFPLUMBER = "pdfplumber-layout"
ENGINE_PYPDF = "pypdf"
ENGINE_PDFMINER = "pdfminer"


def available_pdf_engines(layout: bool = True) -> list[tuple[str, object]]:
    """Engines in preference order: layout-aware first (pdftotext -layout,
    pdfplumber), then the plain text engines (pypdf, pdfminer.six)."""
    engines: list[tuple[str, object]] = []
    if layout and pdftotext_available():
        engines.append((ENGINE_PDFTOTEXT, _pdftotext_pages))
    if layout and pdfplumber is not None:
        engines.append((ENGINE_PDFPLUMBER, _pdfplumber_pages))
    if pypdf is not None:
        engines.append((ENGINE_PYPDF, _pypdf_pages))
    if _pdfminer_extract_text is not None and _PDFPage is not None:
        engines.append((ENGINE_PDFMINER, _pdfminer_pages))
    return engines


def extract_pdf(raw: bytes, min_chars_per_page: int = OCR_MIN_CHARS_PER_PAGE, layout: bool = True) -> PdfExtraction:
    """Extract text per page. Layout-aware engines first (``pdftotext
    -layout`` when the poppler binary is on PATH, else pdfplumber) with
    column splitting; pypdf, then pdfminer.six, when neither is available or
    the layout engine fails / yields no text. ``layout=False`` skips the
    layout engines. A document whose text layer averages fewer than
    ``min_chars_per_page`` characters per page is flagged ``needs_ocr``
    (scanned or image-only PDF) rather than returned as ''. The engine that
    produced the text is in ``engine``."""
    result = PdfExtraction()
    errors: list[str] = []
    engines = available_pdf_engines(layout)
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
