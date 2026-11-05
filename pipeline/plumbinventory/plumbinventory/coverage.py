"""Coverage report: which checklist items a hashed document covers, and on which pages.

Reports "not found in this document" for misses, never "does not exist". External items are listed
with the sources the run actually used (from candidates.yaml secondary_sources), so a reviewer can see
what was and was not looked at.

Usage: python -m plumbinventory.coverage <checklist.yaml> <candidates.yaml> --out <coverage.md>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from .build import load_pages, norm


def scan(pages: list[str], terms: list[str], offset: int) -> list[int]:
    hits: set[int] = set()
    for t in terms:
        # short all-caps acronyms match as whole words, case-sensitive; everything else case-insensitive
        pat = re.compile(r"\b" + re.escape(t) + r"\b") if (t.isupper() and len(t) <= 5) else re.compile(re.escape(t), re.I)
        hits.update(i + 1 for i, p in enumerate(pages) if pat.search(norm(p)))
    printed = sorted(h + offset for h in hits if h + offset >= 1)
    # pages before printed page 1 (cover, inside cover) are reported once as front matter
    front = ["front matter"] if any(h + offset < 1 for h in hits) else []
    return printed + front


def fmt_pages(pp: list[int], limit: int = 10) -> str:
    if not pp:
        return "not found in this document"
    shown = ", ".join(str(p) for p in pp[:limit])
    return f"{len(pp)} pages: {shown}" + (" …" if len(pp) > limit else "")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("checklist", type=Path)
    ap.add_argument("candidates", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cl = yaml.safe_load(a.checklist.read_text())
    spec = yaml.safe_load(a.candidates.read_text())
    root = a.candidates.resolve().parents[3]
    prim = spec["primary_source"]
    pages, sha = load_pages(root / spec["run"], prim["url"])
    off = prim.get("printed_page_offset", 0)
    used = spec.get("secondary_sources", [])

    lines = [f"# Coverage — {spec['client']} ({spec['as_of']})", "",
             f"Document: {prim['title']} · {len(pages)} PDF pages · SHA-256 `{sha[:12]}…` · printed page numbers shown.",
             f"Checklist: `catalogue/coverage/{a.checklist.name}` ({cl['industry']}).", "",
             "| Area | What a CXO reader expects us to have read | In the annual report |", "|---|---|---|"]
    for it in cl["items"]:
        if it.get("external"):
            continue
        lines.append(f"| {it['area']} | {it['ask']} | {fmt_pages(scan(pages, it['terms'], off))} |")
    lines += ["", "## Outside the annual report", "", "| Source class | Used in this run |", "|---|---|"]
    by_kind = {"x-jobs": ["foundit"], "x-vendor-cases": ["pega", "digicon"], "x-app": ["coverager.com/great-eastern-introduces"],
               "x-press": ["coverager.com/pand", "1h2026"], "x-group": ["ocbc"], "x-regulator": ["mas.gov.sg", "beri.net"]}
    for it in cl["items"]:
        if not it.get("external"):
            continue
        hit = [s["title"] for s in used if any(k in s["url"] for k in by_kind.get(it["id"], []))]
        lines.append(f"| {it['ask']} | {'; '.join(hit) if hit else '**not yet searched**'} |")
    lines += ["", "A page hit means the terms occur there; a human still reads the page. A miss means the terms do not occur in this document, not that the thing does not exist."]
    a.out.write_text("\n".join(lines) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
