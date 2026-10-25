"""Client-face lint: internal QA vocabulary must never reach the report.

Runs on the rendered HTML (including attribute values and the CSS that carries the
running header and footer) and, as a second net, on the text extracted from the PDF.
Any hit fails the build.
"""
from __future__ import annotations

import re

# (pattern, flags, plain description) - claim ids are matched by shape, not by subject
FORBIDDEN: list[tuple[str, int, str]] = [
    (r"\b[a-z][a-z0-9-]*\.(?:findings|ar|peer|reg|obs|q)\.[a-z0-9_.-]+", 0, "statement id"),
    (r"\bclaim[ _-]?ids?\b", re.I, "claim id"),
    (r"\bwithheld\b", re.I, "withheld"),
    (r"\bgap[ _-]register\b", re.I, "gap register"),
    (r"\bG-\d+\b", 0, "gap number (G-n)"),
    (r"\bT[1-5]\b", 0, "source tier label"),
    (r"\btier[ -]?[1-5]\b", re.I, "source tier label"),
    (r"\bhash(es|ed)?\b", re.I, "hash"),
    (r"\bsha-?256\b", re.I, "hash"),
    (r"\bunreconciled\b", re.I, "unreconciled"),
    (r"\binterlock\b", re.I, "interlock"),
    (r"\bQA[ -]?gate\b", re.I, "QA gate"),
    (r"\bplumb(verify|research|deck|report)\b", re.I, "tool name"),
    (r"\bbuild[ _-]profile\b", re.I, "build profile"),
    (r"\blocated-not-fetched\b", re.I, "research confidence label"),
    (r"\bconfirmed-from-primary\b", re.I, "research confidence label"),
    (r"\bC4\b", 0, "rule number"),
    (r"\[\[", 0, "unfilled placeholder"),
    (r"\bred-team\b", re.I, "internal review name"),
]

_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")


def lint_text(text: str, where: str) -> list[dict]:
    errs = []
    for pat, flags, desc in FORBIDDEN:
        for m in re.finditer(pat, text, flags):
            a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
            errs.append({"where": where, "rule": desc, "match": m.group(0),
                         "context": re.sub(r"\s+", " ", text[a:b])})
    for m in _EMOJI.finditer(text):
        errs.append({"where": where, "rule": "emoji", "match": m.group(0), "context": ""})
    return errs


def lint_html(html: str) -> list[dict]:
    return lint_text(html, "report.html")
