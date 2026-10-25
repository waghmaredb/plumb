"""plumbreport build --spec S --run R --storyline J --research M --out D [--strict] [--source-pdf P]

Exit codes: 0 built and lint clean; 1 lint failed (no PDF left behind); 2 the spec asks
for something the evidence does not allow, or an input is missing.
"""
from __future__ import annotations

import argparse
import sys

from .build import build
from .data import InputError
from .spec import BindingError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="plumbreport", description="PLUMB deep-dive report generator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="render report.html, report.pdf and lint.json")
    b.add_argument("--spec", required=True)
    b.add_argument("--run", required=True, help="research run folder (claims.json, report.json)")
    b.add_argument("--storyline", required=True, help="resolved.json from the executive deck")
    b.add_argument("--research", help="RESEARCH.md from an update run (section 5)")
    b.add_argument("--out", required=True)
    b.add_argument("--strict", action="store_true",
                   help="omit the 'awaiting source check' section entirely")
    b.add_argument("--source-pdf", help="re-check every quotation word for word against this PDF")
    b.add_argument("--html-only", action="store_true", help="skip the PDF (lint still runs)")
    a = ap.parse_args(argv)

    try:
        res = build(a.spec, a.run, a.storyline, a.research, a.out, strict=a.strict,
                    source_pdf=a.source_pdf, pdf=not a.html_only)
    except (BindingError, InputError) as e:
        print(f"plumbreport: {e}", file=sys.stderr)
        return 2
    lint = res.lint
    bnd = lint["binding"]
    print(f"Statements printed: {len(bnd['verified_bound'])} verified"
          + (f"; {len(bnd['not_verified_in_awaiting'])} shown only as awaiting source check"
             if bnd["not_verified_in_awaiting"] else ""))
    if bnd["not_verified_unaccounted"]:
        print("Not verified and not accounted for in open items: " + ", ".join(bnd["not_verified_unaccounted"]))
    if res.pages:
        print(f"Pages: {res.pages}  ->  {res.out / 'report.pdf'}")
    for e in lint["errors"]:
        print(f"lint: {e['where']}: {e['rule']}: {e['match']!r} ... {e['context']}", file=sys.stderr)
    for s in lint.get("sections_not_located", []):
        print(f"contents: section {s} not located in the PDF", file=sys.stderr)
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
