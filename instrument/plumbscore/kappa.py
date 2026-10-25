"""Quadratic-weighted Cohen's κ for two raters on the 20-item subset (§7).

Rater CSV columns: org_id, item_id, score (1–5). κ is computed per item across
organisations (the md design: ≥10 organisations, ≥200 paired ratings) and
pooled across all paired ratings; exact-agreement % is reported alongside.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Optional, Union

from .instrument import Instrument


def weighted_kappa(a: list[int], b: list[int], k_min: int = 1, k_max: int = 5) -> Optional[float]:
    """Cohen's κ with quadratic weights over a fixed ordinal scale k_min..k_max.

    κw = 1 − Σ w_ij O_ij / Σ w_ij E_ij, with w_ij = (i−j)² / (k−1)²,
    O the observed joint distribution and E the product of the marginals.
    Returns None when undefined (no pairs, or both raters constant so that
    expected disagreement is zero).
    """
    if len(a) != len(b):
        raise ValueError("rater vectors differ in length")
    n = len(a)
    if n == 0:
        return None
    cats = list(range(k_min, k_max + 1))
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    for x in a + b:
        if x not in idx:
            raise ValueError(f"score {x} outside {k_min}–{k_max}")
    O = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        O[idx[x]][idx[y]] += 1
    ra = [sum(O[i][j] for j in range(k)) for i in range(k)]
    rb = [sum(O[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = ((i - j) ** 2) / ((k - 1) ** 2)
            num += w * O[i][j] / n
            den += w * (ra[i] * rb[j]) / (n * n)
    if den == 0:
        return None
    return 1.0 - num / den


def exact_agreement(a: list[int], b: list[int]) -> Optional[float]:
    if not a:
        return None
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def load_ratings(path: Union[str, Path]) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            key = ((r.get("org_id") or "").strip(), (r.get("item_id") or "").strip())
            if not key[1]:
                continue
            out[key] = int(float(r["score"]))
    return out


def classify(kappa: Optional[float], thresholds: dict) -> str:
    if kappa is None or math.isnan(kappa):
        return "undefined"
    if kappa >= thresholds.get("accept", 0.70):
        return "accept"
    if kappa >= thresholds.get("rewrite_anchors_low", 0.50):
        return "rewrite anchors"
    return "rewrite or drop"


def kappa_report(
    instrument: Instrument,
    ratings_a: dict[tuple[str, str], int],
    ratings_b: dict[tuple[str, str], int],
    subset_only: bool = True,
) -> dict:
    thresholds = instrument.kappa.thresholds
    subset = set(instrument.kappa_subset)
    keys = sorted(set(ratings_a) & set(ratings_b))
    if subset_only:
        keys = [k for k in keys if k[1] in subset]
    by_item: dict[str, tuple[list[int], list[int]]] = defaultdict(lambda: ([], []))
    pooled_a: list[int] = []
    pooled_b: list[int] = []
    for key in keys:
        by_item[key[1]][0].append(ratings_a[key])
        by_item[key[1]][1].append(ratings_b[key])
        pooled_a.append(ratings_a[key])
        pooled_b.append(ratings_b[key])
    items = []
    for item_id in sorted(by_item, key=_item_sort_key):
        a, b = by_item[item_id]
        kw = weighted_kappa(a, b)
        items.append(
            {
                "item_id": item_id,
                "n_pairs": len(a),
                "kappa_w": kw,
                "exact_agreement": exact_agreement(a, b),
                "verdict": classify(kw, thresholds),
            }
        )
    missing = sorted(subset - set(by_item), key=_item_sort_key) if subset_only else []
    n_accept = sum(1 for i in items if i["verdict"] == "accept")
    n_below_low = sum(1 for i in items if i["verdict"] == "rewrite or drop")
    n_orgs = len({k[0] for k in keys})
    exit_ok = (
        not missing
        and n_accept >= instrument.kappa.exit_min_items_accept
        and n_below_low == 0
        and all(i["kappa_w"] is not None for i in items)
    )
    return {
        "n_pairs": len(pooled_a),
        "n_orgs": n_orgs,
        "n_items": len(items),
        "pooled_kappa_w": weighted_kappa(pooled_a, pooled_b),
        "pooled_exact_agreement": exact_agreement(pooled_a, pooled_b),
        "items": items,
        "missing_subset_items": missing,
        "n_accept": n_accept,
        "n_rewrite_or_drop": n_below_low,
        "exit_criterion_met": exit_ok,
        "exit_criterion": instrument.kappa.model_dump().get("exit_criterion_v0_2", "≥16 of 20 items at κw ≥ 0.70, no item <0.50"),
        "design_note": "md design: ≥10 organisations (≥200 paired ratings)" + ("" if n_orgs >= 10 else f"; only {n_orgs} organisations in this run"),
    }


def _item_sort_key(item_id: str):
    try:
        d, i = item_id[1:].split(".")
        return (int(d), int(i))
    except Exception:
        return (99, item_id)


def render_kappa_markdown(rep: dict) -> str:
    def f(x):
        return "n/a" if x is None else f"{x:.2f}"

    lines = [
        "# Inter-rater reliability (quadratic-weighted Cohen's κ) — §7 subset",
        "",
        f"Paired ratings: {rep['n_pairs']} across {rep['n_orgs']} organisations, {rep['n_items']} items. {rep['design_note']}.",
        f"Pooled κw = {f(rep['pooled_kappa_w'])}; pooled exact agreement = {f(rep['pooled_exact_agreement'])}.",
        "",
        "| Item | n pairs | κw | Exact agreement | Verdict |",
        "|---|---|---|---|---|",
    ]
    for i in rep["items"]:
        lines.append(f"| {i['item_id']} | {i['n_pairs']} | {f(i['kappa_w'])} | {f(i['exact_agreement'])} | {i['verdict']} |")
    lines += [
        "",
        f"Items at κw ≥ 0.70: {rep['n_accept']}; items < 0.50: {rep['n_rewrite_or_drop']}.",
        f"Exit criterion for v0.2 ({rep['exit_criterion']}): **{'met' if rep['exit_criterion_met'] else 'not met'}**.",
    ]
    if rep["missing_subset_items"]:
        lines.append(f"Subset items with no paired ratings: {', '.join(rep['missing_subset_items'])}.")
    return "\n".join(lines) + "\n"
