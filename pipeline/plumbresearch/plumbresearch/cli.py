"""plumbresearch run <subject.yaml> --out DIR [--data-dir DIR] [--fixtures] [--cap N] [--modules a,b] [--as-of YYYY-MM-DD] [--offline]"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .orchestrator import MODULE_ORDER, run_subject
from .subject import load_subject

FIXTURES_DIR = Path(__file__).with_name("fixtures")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plumbresearch")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the Phase 1 modules for one subject and verify every claim")
    r.add_argument("subject", help="subject YAML (e.g. plumbresearch/subjects/maybank.yaml)")
    r.add_argument("--out", required=True, help="output root; files land in <out>/<slug>/")
    r.add_argument("--data-dir", default="data", help="root holding <slug>/ with annual reports, postings.csv, transcripts/, patents.csv, financials.csv")
    r.add_argument("--fixtures", action="store_true", help="offline run: serve the fixture web from <data-dir>/<slug>/web.yaml (defaults data-dir to the bundled fixtures)")
    r.add_argument("--offline", action="store_true", help="no network even outside fixture mode (unknown URLs classify DEAD)")
    r.add_argument("--cap", type=int, default=40, help="C10 tool-call cap per module run (default 40; hard ceiling 60)")
    r.add_argument("--modules", default=None, help="comma-separated subset of: " + ",".join(MODULE_ORDER))
    r.add_argument("--as-of", default=None, help="window end date (default today)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "run":
        if args.cap > 60:
            print("cap above the hard ceiling of 60 (spec C10) — refusing; record an override to raise it", file=sys.stderr)
            return 2
        subject = load_subject(args.subject)
        data_dir = Path(args.data_dir)
        if args.fixtures and args.data_dir == "data":
            data_dir = FIXTURES_DIR
        mods = [m.strip() for m in args.modules.split(",")] if args.modules else None
        bad = [m for m in (mods or []) if m not in MODULE_ORDER]
        if bad:
            print(f"unknown module(s): {bad}", file=sys.stderr)
            return 2
        out = run_subject(subject, Path(args.out) / subject.slug, data_dir, fixtures=args.fixtures, cap=args.cap, modules=mods,
                          as_of=date.fromisoformat(args.as_of) if args.as_of else None, offline=args.offline)
        m = out.report.metrics
        print(f"{subject.slug}: {len(out.modules)} modules, {len(out.claims)} claims, {m.get('blocked_claims')} BLOCKED, "
              f"{len(out.signals)} signals, build {'PASS' if out.report.build_pass else 'FAIL'} -> {out.out_dir}")
        for g in out.report.gap_register:
            print(f"  BLOCKED {g.claim_id}: {g.text[:80]}")
        for e in out.escalations:
            print(f"  ESCALATED {e}")
        return 0 if out.report.build_pass else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
