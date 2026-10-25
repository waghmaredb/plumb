"""Command-line entry points.

  plumbverify verify claims.json --out report.json [--store DIR] [--log FILE] [--tiers tiers.yaml]
  plumbverify check-url <url> [--archive]
  plumbverify verify-log <log.jsonl>
  plumbverify report report.json --format md [--out report.md] [--seed N]
  plumbverify ingest <file> --url <declared_url> --store DIR [--supplied-by NAME] [--doc KEY]
  plumbverify reconcile --store DIR [--url URL] [--archive]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .fetch import EvidenceStore, Fetcher, NullArchive, WaybackArchive
from .ingest import ingest_local, reconcile_all
from .log import HashChainLog
from .models import Reconciliation, VerificationReport
from .pipeline import Verifier, load_claims
from .report import render_markdown
from .tier import assign_tier, load_tier_rules


def _archive(args: argparse.Namespace):
    if getattr(args, "archive", False) or getattr(args, "archive_save", False):
        return WaybackArchive(save_missing=bool(getattr(args, "archive_save", False)))
    return NullArchive()


def _cmd_verify(args: argparse.Namespace) -> int:
    store = EvidenceStore(args.store)
    log = HashChainLog(args.log)
    rules = load_tier_rules(args.tiers) if args.tiers else None
    fetcher = Fetcher(store=store, archive=_archive(args), reconcile_on_fetch=bool(getattr(args, "reconcile", False)))
    verifier = Verifier(fetcher=fetcher, store=store, log=log, tier_rules=rules)
    claims = load_claims(args.claims)
    report = verifier.run(claims)
    Path(args.out).write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(f"run {report.run_id}: {report.metrics['claims']} claims, {report.metrics['blocked_claims']} BLOCKED, "
          f"build {'PASS' if report.build_pass else 'FAIL'} -> {args.out}")
    for g in report.gap_register:
        print(f"  BLOCKED {g.claim_id}: {g.text[:80]}")
        for r in g.reasons:
            print(f"      - {r}")
    return 0 if report.build_pass else 1


def _cmd_check_url(args: argparse.Namespace) -> int:
    fetcher = Fetcher(archive=_archive(args))
    h = fetcher.check_health(args.url)
    tier = assign_tier(h.url_final or args.url)
    out = {
        "url": args.url, "health_class": h.health_class.value, "http_status": h.http_status,
        "url_final": h.url_final, "redirects": h.redirects, "archived_url": h.archived_url,
        "attempts": h.attempts, "error": h.error, "tier": tier.tier.value, "tier_rule": tier.rule,
        "citable": h.health_class.value in ("LIVE", "ARCHIVED"),
    }
    print(json.dumps(out, indent=2))
    return 0 if out["citable"] else 1


def _make_fetcher(args: argparse.Namespace, store: EvidenceStore) -> Fetcher:
    """Separated so tests can swap in a MockTransport-backed Fetcher."""
    return Fetcher(store=store, archive=_archive(args))


def _cmd_ingest(args: argparse.Namespace) -> int:
    store = EvidenceStore(args.store)
    rules = load_tier_rules(args.tiers) if args.tiers else None
    try:
        src = ingest_local(args.file, args.url, store, supplied_by=args.supplied_by, document_key=args.doc, tier_rules=rules)
    except (FileNotFoundError, ValueError) as e:
        print(f"ingest refused: {e}", file=sys.stderr)
        return 2
    finally:
        store.close()
    out = {
        "url": src.url, "state": src.state.value, "sha256": src.sha256, "tier": src.tier.value,
        "content_type": src.detected_content_type or src.content_type, "page_count": src.page_count, "needs_ocr": src.needs_ocr,
        "text_chars": len(src.text_extract or ""), "recheck_after": src.recheck_after.isoformat() if src.recheck_after else None,
        "provenance": src.provenance, "citable": src.citable, "label": src.attached_label, "error": src.error,
        "next": f"plumbverify reconcile --store {args.store} --url {src.url}  (when egress is available)",
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if src.citable and not src.needs_ocr else 1


def _cmd_reconcile(args: argparse.Namespace) -> int:
    store = EvidenceStore(args.store)
    try:
        if args.url is None and not store.list_attachments():
            print("no attached documents in the store", file=sys.stderr)
            return 2
        fetcher = _make_fetcher(args, store)
        try:
            results = reconcile_all(store, fetcher, url=args.url, include_reconciled=args.all)
        except KeyError as e:
            print(f"reconcile refused: {e}", file=sys.stderr)
            return 2
        rows = []
        for url, outcome in results:
            att = store.get_attachment(url) or {}
            rows.append({"url": url, "reconciliation": outcome.value, "state": att.get("state"),
                         "sha256_attached": att.get("sha256"), "sha256_publisher": att.get("reconciled_sha256"),
                         "reconciled_at": att.get("reconciled_at"), "error": att.get("error")})
    finally:
        store.close()
    print(json.dumps(rows, indent=2))
    if any(r["reconciliation"] == Reconciliation.MISMATCH.value for r in rows):
        return 1  # a MISMATCH blocks every claim citing that document
    return 0


def _cmd_verify_log(args: argparse.Namespace) -> int:
    v = HashChainLog(args.log).verify()
    print(json.dumps({"ok": v.ok, "records": v.records, "broken_at": v.broken_at, "detail": v.detail}, indent=2))
    return 0 if v.ok else 2


def _cmd_report(args: argparse.Namespace) -> int:
    report = VerificationReport.model_validate_json(Path(args.report).read_text(encoding="utf-8"))
    if args.format == "md":
        text = render_markdown(report, seed=args.seed, sample_min=args.sample_min)
    else:
        text = report.model_dump_json(indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0 if report.build_pass else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plumbverify", description="PLUMB verification layer (PI-CV v0.1)")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify", help="verify a claims.json file and write a report")
    v.add_argument("claims")
    v.add_argument("--out", required=True)
    v.add_argument("--store", default=".plumbverify/evidence")
    v.add_argument("--log", default=".plumbverify/inference.jsonl")
    v.add_argument("--tiers", default=None, help="override tier rules YAML")
    v.add_argument("--archive", action="store_true", help="enable Wayback availability lookup (network)")
    v.add_argument("--archive-save", action="store_true", help="also save missing pages via Wayback Save Page Now (implies --archive)")
    v.add_argument("--reconcile", action="store_true", help="re-fetch attached documents' declared URLs during this run and reconcile hashes (network); "
                                                           "default: use attachments as stored, labelled")
    v.set_defaults(func=_cmd_verify)

    c = sub.add_parser("check-url", help="health-check and tier a single URL")
    c.add_argument("url")
    c.add_argument("--archive", action="store_true")
    c.add_argument("--archive-save", action="store_true")
    c.set_defaults(func=_cmd_check_url)

    r = sub.add_parser("report", help="render a report.json for reviewers (Markdown table + 6.2 sampling worksheet)")
    r.add_argument("report")
    r.add_argument("--format", choices=["md", "json"], default="md")
    r.add_argument("--out", default=None, help="write to this file instead of stdout")
    r.add_argument("--seed", type=int, default=None, help="random seed for the sampling worksheet (recorded in the output)")
    r.add_argument("--sample-min", type=int, default=30)
    r.set_defaults(func=_cmd_report)

    i = sub.add_parser("ingest", help="attach a local document under its declared publisher URL (state ATTACHED, citable with a visible label until reconciled)")
    i.add_argument("file", help="local file (PDF or HTML) the person attached")
    i.add_argument("--url", required=True, help="the publisher's canonical URL this file claims to be (citation of record; tier comes from its domain)")
    i.add_argument("--store", default=".plumbverify/evidence")
    i.add_argument("--supplied-by", default=None, help="who supplied the file (recorded in provenance)")
    i.add_argument("--doc", default=None, help="optional document key (plumbresearch subject document mapping)")
    i.add_argument("--tiers", default=None, help="override tier rules YAML")
    i.set_defaults(func=_cmd_ingest)

    rc = sub.add_parser("reconcile", help="re-fetch attached documents' declared URLs and compare hashes (MATCH flips to LIVE/ARCHIVED; MISMATCH blocks)")
    rc.add_argument("--store", default=".plumbverify/evidence")
    rc.add_argument("--url", default=None, help="reconcile only this declared URL (default: every attachment not yet at MATCH)")
    rc.add_argument("--all", action="store_true", help="also re-check attachments already at MATCH")
    rc.add_argument("--archive", action="store_true", help="fall back to a Wayback snapshot when the live URL fails (network)")
    rc.add_argument("--archive-save", action="store_true")
    rc.set_defaults(func=_cmd_reconcile)

    l = sub.add_parser("verify-log", help="verify hash-chain integrity of a JSONL log")
    l.add_argument("log")
    l.set_defaults(func=_cmd_verify_log)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
