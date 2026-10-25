"""Command line: `plumbscore score ...` and `plumbscore kappa ...`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import load_benchmark, peer_percentile
from .instrument import load_instrument
from .kappa import kappa_report, load_ratings, render_kappa_markdown
from .responses import load_responses
from .scorecard import render_scorecard
from .scoring import score_responses


def _build() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plumbscore", description="PLUMB maturity instrument scorer (v0.1)")
    p.add_argument("--instrument", help="path to instrument YAML (default: bundled instrument-v0.1.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("score", help="score a response CSV and render a scorecard")
    s.add_argument("responses", help="CSV: respondent_id, role_group, item_id, score, evidence_class, evidence_ref[, role]")
    s.add_argument("--benchmark", help="benchmark CSV: org_id, sector, size_band[, region], D1..D8, total[, evidence_gated, as_of]")
    s.add_argument("--sector", help="peer-set filter")
    s.add_argument("--size-band", dest="size_band", help="peer-set filter")
    s.add_argument("--region", help="peer-set filter (APAC sub-region)")
    s.add_argument("--peer-set-date", dest="peer_set_date", default="", help="peer-set definition date to print on the scorecard")
    s.add_argument("--org", default="", help="label for the organisation (use a fictional / anonymised name in outputs)")
    s.add_argument("--out", help="write Markdown scorecard here (default: stdout)")
    s.add_argument("--json", dest="json_out", help="write JSON result here")

    k = sub.add_parser("kappa", help="quadratic-weighted Cohen's κ for two raters on the §7 subset")
    k.add_argument("rater_a", help="CSV: org_id, item_id, score")
    k.add_argument("rater_b", help="CSV: org_id, item_id, score")
    k.add_argument("--all-items", action="store_true", help="include items outside the 20-item subset")
    k.add_argument("--json", dest="json_out", help="write JSON report here")
    k.add_argument("--out", help="write Markdown report here (default: stdout)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build().parse_args(argv)
    inst = load_instrument(args.instrument)

    if args.cmd == "score":
        responses = load_responses(args.responses)
        res = score_responses(inst, responses, org_label=args.org)
        if args.benchmark:
            rows = load_benchmark(args.benchmark)
            res.percentile = peer_percentile(
                inst,
                rows,
                total=res.capability_score if res.capability_score is not None else float("nan"),
                dim_scores={d.id: d.score for d in res.dimensions},
                sector=args.sector,
                size_band=args.size_band,
                region=args.region,
                peer_set_date=args.peer_set_date,
            )
        md = render_scorecard(inst, res)
        if args.out:
            Path(args.out).write_text(md, encoding="utf-8")
        else:
            sys.stdout.write(md)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(res.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
        if args.out:
            print(f"capability {res.capability_score_rounded} · {res.band} · {res.value_profile} · scorecard → {args.out}", file=sys.stderr)
        return 0

    if args.cmd == "kappa":
        a = load_ratings(args.rater_a)
        b = load_ratings(args.rater_b)
        rep = kappa_report(inst, a, b, subset_only=not args.all_items)
        md = render_kappa_markdown(rep)
        if args.out:
            Path(args.out).write_text(md, encoding="utf-8")
        else:
            sys.stdout.write(md)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
