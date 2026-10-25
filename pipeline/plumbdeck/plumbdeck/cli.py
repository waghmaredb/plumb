"""plumbdeck CLI.

    plumbdeck build --spec specs/plumb-assessment-v0.1.yaml --run <run_dir> [--scorecard <json>] [--signoff <yaml>] --out <dir>
    plumbdeck lint <out_dir>

There is no --force, --final or --profile option, and no environment variable is
read: whether the deck is final is decided only by the build report and the QA
gate 3 sign-off file (see interlock.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .build import build_deck, write_outputs
from .interlock import BANNER
from .lint import lint_dir
from .runio import RunError
from .spec import SpecError

PKG_ROOT = Path(__file__).resolve().parent.parent


def _resolve_spec(p: str) -> Path:
    path = Path(p)
    if path.is_file():
        return path
    alt = PKG_ROOT / p
    return alt if alt.is_file() else path


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="plumbdeck", description=__doc__.split("\n\n")[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="render deck.md / deck.pptx (or deck-DRAFT.*), titles.md, build.json, lint.json", allow_abbrev=False)
    b.add_argument("--spec", required=True)
    b.add_argument("--run", required=True, help="run folder holding report.json (and claims.json)")
    b.add_argument("--scorecard", help="plumbscore scorecard JSON")
    b.add_argument("--signoff", help="QA gate 3 sign-off YAML")
    b.add_argument("--out", required=True)
    l = sub.add_parser("lint", help="re-lint a built deck folder", allow_abbrev=False)
    l.add_argument("out_dir")
    return ap


def _print_lint(rep: dict) -> None:
    for e in rep["errors"]:
        print(f"  ERROR   [{e['check']}] {e.get('slide') or '-'}: {e['message']}")
    for w in rep["warnings"]:
        print(f"  warning [{w['check']}] {w.get('slide') or '-'}: {w['message']}")
    print(f"lint: {'ok' if rep['ok'] else 'FAILED'} ({len(rep['errors'])} errors, {len(rep['warnings'])} warnings)")


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.cmd == "build":
        try:
            deck = build_deck(_resolve_spec(args.spec), Path(args.run),
                              Path(args.scorecard) if args.scorecard else None,
                              Path(args.signoff) if args.signoff else None)
        except (SpecError, RunError, OSError, json.JSONDecodeError) as e:
            print(f"plumbdeck: {e}", file=sys.stderr)
            return 2
        rep = write_outputs(deck, Path(args.out))
        il = deck.interlock
        print(il.outcome_sentence)
        if il.passed:
            print("Interlock passed: verification statement rendered on S02.")
        else:
            print(f"{BANNER}: {'; '.join(il.reasons)}")
        print(f"wrote {Path(args.out) / (deck.stem + '.md')}, {Path(args.out) / (deck.stem + '.pptx')}, titles.md, build.json, lint.json")
        _print_lint(rep)
        return 0 if rep["ok"] else 1
    if args.cmd == "lint":
        rep = lint_dir(Path(args.out_dir))
        _print_lint(rep)
        return 0 if rep["ok"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
