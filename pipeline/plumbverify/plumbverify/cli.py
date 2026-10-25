"""Command-line entry points.

  plumbverify verify claims.json --out report.json [--store DIR] [--log FILE] [--tiers tiers.yaml]
  plumbverify check-url <url> [--archive]
  plumbverify verify-log <log.jsonl>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .fetch import EvidenceStore, Fetcher, NullArchive, WaybackArchive
from .log import HashChainLog
from .pipeline import Verifier, load_claims
from .tier import assign_tier, load_tier_rules


def _cmd_verify(args: argparse.Namespace) -> int:
    store = EvidenceStore(args.store)
    log = HashChainLog(args.log)
    rules = load_tier_rules(args.tiers) if args.tiers else None
    archive = WaybackArchive() if args.archive else NullArchive()
    fetcher = Fetcher(store=store, archive=archive)
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
    archive = WaybackArchive() if args.archive else NullArchive()
    fetcher = Fetcher(archive=archive)
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


def _cmd_verify_log(args: argparse.Namespace) -> int:
    v = HashChainLog(args.log).verify()
    print(json.dumps({"ok": v.ok, "records": v.records, "broken_at": v.broken_at, "detail": v.detail}, indent=2))
    return 0 if v.ok else 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plumbverify", description="PLUMB verification layer (PI-CV v0.1)")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify", help="verify a claims.json file and write a report")
    v.add_argument("claims")
    v.add_argument("--out", required=True)
    v.add_argument("--store", default=".plumbverify/evidence")
    v.add_argument("--log", default=".plumbverify/inference.jsonl")
    v.add_argument("--tiers", default=None, help="override tier rules YAML")
    v.add_argument("--archive", action="store_true", help="enable Wayback fallback (network)")
    v.set_defaults(func=_cmd_verify)

    c = sub.add_parser("check-url", help="health-check and tier a single URL")
    c.add_argument("url")
    c.add_argument("--archive", action="store_true")
    c.set_defaults(func=_cmd_check_url)

    l = sub.add_parser("verify-log", help="verify hash-chain integrity of a JSONL log")
    l.add_argument("log")
    l.set_defaults(func=_cmd_verify_log)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
