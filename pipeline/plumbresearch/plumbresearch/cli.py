"""plumbresearch run <subject.yaml> --out DIR [--data-dir DIR] [--fixtures] [--cap N] [--modules a,b] [--as-of YYYY-MM-DD] [--offline] [--profile client|internal]
plumbresearch ingest <subject.yaml> --file PATH --doc <document-key> [--out DIR] [--supplied-by NAME]

Change log: 2026-10-25 — `--profile` pass-through (spec C2a, red-team review Blocker 2)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from plumbverify.policy import BUILD_PROFILES, DEFAULT_BUILD_PROFILE, present_outcome

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
    r.add_argument("--profile", choices=list(BUILD_PROFILES), default=DEFAULT_BUILD_PROFILE,
                   help="build profile (spec C2a): 'client' (default) withholds every claim whose only support is an attached document "
                        "with reconciliation != MATCH; 'internal' releases them with the attached label (drafts and sandbox runs only)")

    i = sub.add_parser("ingest", help="attach a local copy of a declared subject document (annual report PDF) into the run's evidence store "
                                      "under the document's publisher URL; withheld in client builds / labelled in internal builds until reconciled")
    i.add_argument("subject", help="subject YAML")
    i.add_argument("--file", required=True, help="the attached file (PDF or HTML)")
    i.add_argument("--doc", required=True, help="document key from the subject YAML: '<kind>-<fy>' (e.g. annual_report-2025), an explicit `key:`, the URL or the local_file name")
    i.add_argument("--out", default="out", help="output root the later `run` will use; the store is <out>/<slug>/evidence")
    i.add_argument("--supplied-by", default=None, help="who supplied the file (recorded in provenance)")
    return p


def ingest_document(subject_path: str | Path, file: str | Path, doc_key: str, out_root: str | Path = "out",
                    supplied_by: str | None = None) -> dict:
    """Map an attached file to a subject document entry and ingest it into
    ``<out>/<slug>/evidence`` under the document's declared URL (plumbverify
    0.3 ``ingest_local``). Returns a JSON-able summary."""
    from plumbverify.fetch import EvidenceStore
    from plumbverify.ingest import ingest_local
    from plumbverify.tier import load_tier_rules

    subject = load_subject(subject_path)
    d = subject.find_document(doc_key)
    if d is None:
        keys = ", ".join(x.document_key for x in subject.documents)
        raise KeyError(f"no document matching {doc_key!r} in {subject.slug}; declared keys: {keys}")
    store_dir = Path(out_root) / subject.slug / "evidence"
    store = EvidenceStore(store_dir)
    try:
        rules = load_tier_rules(overrides={"tiers": {k: {"domains": v} for k, v in subject.tier_overrides.items()}}) \
            if subject.tier_overrides else load_tier_rules()
        src = ingest_local(file, d.url, store, supplied_by=supplied_by, document_key=d.document_key, tier_rules=rules,
                           provenance={"subject": subject.slug, "document_kind": d.kind, "document_fy": d.fy})
    finally:
        store.close()
    return {
        "subject": subject.slug, "document_key": d.document_key, "kind": d.kind, "fy": d.fy, "url": d.url,
        "store": str(store_dir), "state": src.state.value, "sha256": src.sha256, "tier": src.tier.value,
        "page_count": src.page_count, "needs_ocr": src.needs_ocr, "text_chars": len(src.text_extract or ""),
        "label": src.attached_label, "provenance": src.provenance, "error": src.error,
        "next": [f"plumbresearch run {subject_path} --out {out_root} --offline --profile internal   # draft: claims carry the attached label",
                 f"plumbverify reconcile --store {store_dir}   # when egress is available: MATCH lifts the label, MISMATCH blocks",
                 f"plumbresearch run {subject_path} --out {out_root}   # client build (default): unreconciled attachments are withheld (C2a)"],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "ingest":
        try:
            out = ingest_document(args.subject, args.file, args.doc, args.out, args.supplied_by)
        except (KeyError, FileNotFoundError, ValueError) as e:
            print(f"ingest refused: {e}", file=sys.stderr)
            return 2
        print(json.dumps(out, indent=2, default=str))
        return 0 if not out["needs_ocr"] and not out["error"] else 1
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
                          as_of=date.fromisoformat(args.as_of) if args.as_of else None, offline=args.offline,
                          build_profile=args.profile)
        m = out.report.metrics
        print(f"{subject.slug} [{out.report.build_profile} build]: {len(out.modules)} modules, {len(out.claims)} claims, {m.get('blocked_claims')} BLOCKED, "
              f"{len(out.signals)} signals, build {'PASS' if out.report.build_pass else 'FAIL'} -> {out.out_dir}")
        print("  " + present_outcome(len(out.claims), m.get("blocked_claims", 0), m.get("withheld_awaiting_reconciliation", 0)))
        for g in out.report.gap_register:
            print(f"  BLOCKED {g.claim_id}: {g.text[:80]}")
        for e in out.escalations:
            print(f"  ESCALATED {e}")
        return 0 if out.report.build_pass else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
