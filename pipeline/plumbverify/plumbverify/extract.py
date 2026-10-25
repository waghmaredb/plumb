"""Main-text extraction and passage splitting (feeds spec C3/C4)."""
from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

try:  # optional, better boilerplate removal
    import trafilatura  # type: ignore
except Exception:  # pragma: no cover
    trafilatura = None

_WS = re.compile(r"\s+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")


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


def extract_main_text(raw: bytes | str, content_type: Optional[str] = None) -> str:
    """Return the main text of a document. HTML goes through trafilatura when
    available (falls back to a bs4 block extractor); other text types are
    decoded as-is. PDF extraction is not implemented (stub: returns '')."""
    if isinstance(raw, bytes):
        if content_type and "pdf" in content_type.lower():
            return ""  # STUB: PDF text extraction not wired in v0.1
        text = raw.decode("utf-8", errors="replace")
    else:
        text = raw
    is_html = (content_type and "html" in content_type.lower()) or re.search(r"<\s*(html|body|p|div)\b", text, re.I)
    if not is_html:
        return normalize_text(text)
    if trafilatura is not None:
        try:
            out = trafilatura.extract(text, include_comments=False, include_tables=True, favor_recall=True)
            if out and len(out) > 80:
                return normalize_text(out)
        except Exception:
            pass
    return normalize_text(_bs4_text(text))


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
    windows for long paragraphs. Short fragments are merged forward."""
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
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
