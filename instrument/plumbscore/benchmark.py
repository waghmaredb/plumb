"""Peer percentile against an anonymised benchmark CSV (§5.5).

Benchmark columns: org_id, sector, size_band, [region], D1..D8, total,
[evidence_gated 0/1], [as_of].
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel

from .instrument import Instrument

DIM_IDS = [f"D{i}" for i in range(1, 9)]


class BenchmarkRow(BaseModel):
    org_id: str
    sector: str = ""
    size_band: str = ""
    region: str = ""
    dims: dict[str, float]
    total: float
    evidence_gated: Optional[bool] = None
    as_of: str = ""


def load_benchmark(path: Union[str, Path]) -> list[BenchmarkRow]:
    rows: list[BenchmarkRow] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            dims = {d: float(r[d]) for d in DIM_IDS if r.get(d) not in (None, "")}
            eg = r.get("evidence_gated")
            rows.append(
                BenchmarkRow(
                    org_id=r["org_id"],
                    sector=(r.get("sector") or "").strip(),
                    size_band=(r.get("size_band") or "").strip(),
                    region=(r.get("region") or "").strip(),
                    dims=dims,
                    total=float(r["total"]),
                    evidence_gated=None if eg in (None, "") else str(eg).strip().lower() in {"1", "true", "yes", "y"},
                    as_of=(r.get("as_of") or "").strip(),
                )
            )
    return rows


def percentile_rank(value: float, population: list[float]) -> Optional[float]:
    """Mid-rank percentile: 100 × (below + 0.5 × equal) / n.

    The md says only "percentile rank of C within the set"; mid-rank is the
    scorer's choice (noted in the YAML).
    """
    n = len(population)
    if n == 0:
        return None
    below = sum(1 for p in population if p < value)
    equal = sum(1 for p in population if p == value)
    return 100.0 * (below + 0.5 * equal) / n


def peer_percentile(
    instrument: Instrument,
    rows: list[BenchmarkRow],
    total: float,
    dim_scores: dict[str, Optional[float]],
    sector: Optional[str] = None,
    size_band: Optional[str] = None,
    region: Optional[str] = None,
    peer_set_date: str = "",
) -> dict:
    """Return percentile block for the scorecard (§5.5 disclosure rules)."""
    min_n = instrument.scoring.peer_percentile.min_n
    filters = {k: v for k, v in {"sector": sector, "size_band": size_band, "region": region}.items() if v}
    peers = [r for r in rows if all(getattr(r, k).lower() == v.lower() for k, v in filters.items())] if filters else []
    n_peer = len(peers)
    if filters and n_peer >= min_n:
        used, label, scope = peers, f"peer set n={n_peer}", "peer"
    else:
        used, scope = rows, "global"
        label = instrument.scoring.peer_percentile.fallback_label if filters else "global (no peer filters given)"
        label += f", n={len(used)}"
        if filters:
            label += f" (peer n={n_peer} < {min_n})"
    n_used = len(used)
    eg_known = [r for r in used if r.evidence_gated is not None]
    eg_share = (sum(1 for r in eg_known if r.evidence_gated) / len(eg_known)) if eg_known else None
    out = {
        "scope": scope,
        "label": label,
        "n": n_used,
        "n_peer_candidates": n_peer,
        "peer_n_sufficient": bool(filters and n_peer >= min_n),
        "min_n": min_n,
        "filters": filters,
        "peer_set_date": peer_set_date or (sorted({r.as_of for r in used if r.as_of})[-1] if any(r.as_of for r in used) else ""),
        "evidence_gated_share": eg_share,
        "total_percentile": percentile_rank(total, [r.total for r in used]) if n_used else None,
        "dimension_percentiles": {},
        "peer_median_by_dimension": {},
        "global_median_by_dimension": {},
    }
    for d in DIM_IDS:
        s = dim_scores.get(d)
        pop = [r.dims[d] for r in used if d in r.dims]
        out["dimension_percentiles"][d] = percentile_rank(s, pop) if (s is not None and pop) else None
        out["peer_median_by_dimension"][d] = _median(pop) if pop else None
        gpop = [r.dims[d] for r in rows if d in r.dims]
        out["global_median_by_dimension"][d] = _median(gpop) if gpop else None
    out["global_median_total"] = _median([r.total for r in rows]) if rows else None
    out["set_median_total"] = _median([r.total for r in used]) if used else None
    return out


def _median(xs: list[float]) -> float:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
