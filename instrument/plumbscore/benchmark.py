"""Peer percentile against an anonymised benchmark CSV (§5.5).

Benchmark columns: org_id, sector, size_band, [region], D1..D8, total,
[evidence_gated 0/1], [as_of], [population self|evidenced].

Populations (red-team review 2026-10-25, Blocker 3 / §2.3): the free Tier-0
pool is self-scored and capped at level 3 per item (``population=self``);
engagement scores are evidence-gated (``population=evidenced``). They are
different populations and are never pooled into one percentile. When the
column is absent, ``population`` is derived from ``evidence_gated``
(1 -> evidenced, 0 -> self). ``peer_percentile`` refuses a mixed set unless a
population is chosen, and when the peer candidates fall below the §5.5
minimum it returns a **rank within the named peers** (n disclosed) instead of
a percentile.

Change log: 2026-10-25 — population flag, no-pooling rule, rank-within-named-peers (review Blocker 3).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, field_validator

from .instrument import Instrument

DIM_IDS = [f"D{i}" for i in range(1, 9)]
POPULATIONS = ("self", "evidenced")


class BenchmarkRow(BaseModel):
    org_id: str
    sector: str = ""
    size_band: str = ""
    region: str = ""
    dims: dict[str, float]
    total: float
    evidence_gated: Optional[bool] = None
    as_of: str = ""
    population: Optional[str] = None  # "self" (Tier-0 self-scored, capped) or "evidenced" (engagement, evidence-gated)

    @field_validator("population", mode="before")
    @classmethod
    def _norm_population(cls, v):
        if v in (None, ""):
            return None
        s = str(v).strip().lower()
        if s not in POPULATIONS:
            raise ValueError(f"population must be one of {POPULATIONS}, got {v!r}")
        return s

    def model_post_init(self, __context) -> None:
        # derive the population from evidence_gated when the CSV predates the column
        if self.population is None and self.evidence_gated is not None:
            self.population = "evidenced" if self.evidence_gated else "self"


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
                    population=r.get("population"),
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


def select_population(rows: list[BenchmarkRow], population: Optional[str]) -> tuple[list[BenchmarkRow], dict]:
    """Apply the no-pooling rule. Returns (rows in the chosen population, composition note).

    ``population=None`` is accepted only when the set is homogeneous (or untagged);
    a mixed self/evidenced set must be split by naming the population.
    """
    present = sorted({r.population for r in rows if r.population is not None})
    untagged = sum(1 for r in rows if r.population is None)
    if population is not None:
        if population not in POPULATIONS:
            raise ValueError(f"population must be one of {POPULATIONS}, got {population!r}")
        chosen = [r for r in rows if r.population == population]
    else:
        if len(present) > 1:
            raise ValueError(
                "benchmark mixes self-scored and evidence-gated entries; pass population='self' or 'evidenced' "
                "— the two are never pooled into one percentile (instrument §5.5, review 2026-10-25 §2.3)"
            )
        chosen, population = rows, (present[0] if present else None)
    note = {
        "population": population,
        "n_in_population": len(chosen),
        "n_excluded_other_population": len(rows) - len(chosen) - (untagged if population is not None else 0),
        "n_untagged": untagged,
        "populations_present": present,
    }
    return chosen, note


def rank_within_peers(total: float, peers: list[BenchmarkRow]) -> dict:
    """Rank within the named peers (n disclosed), each peer's value shown — the
    exhibit that replaces a percentile when n < min_n (ghost deck S09)."""
    ordered = sorted(peers, key=lambda r: r.total, reverse=True)
    above = sum(1 for r in peers if r.total > total)
    return {
        "rank": above + 1,
        "n": len(peers),
        "label": f"rank {above + 1} of {len(peers) + 1} within named peers (n={len(peers)}; peer n insufficient for a percentile)",
        "peers": [{"org_id": r.org_id, "total": r.total, "dims": dict(r.dims)} for r in ordered],
    }


def peer_percentile(
    instrument: Instrument,
    rows: list[BenchmarkRow],
    total: float,
    dim_scores: dict[str, Optional[float]],
    sector: Optional[str] = None,
    size_band: Optional[str] = None,
    region: Optional[str] = None,
    peer_set_date: str = "",
    population: Optional[str] = None,
) -> dict:
    """Return percentile block for the scorecard (§5.5 disclosure rules).

    ``population`` selects the benchmark population ("self" or "evidenced");
    self-scored and evidence-gated entries are never pooled (see module docstring).
    """
    min_n = instrument.scoring.peer_percentile.min_n
    rows, pop_note = select_population(rows, population)
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
    if pop_note["population"]:
        label += f"; population: {pop_note['population']}"
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
        "population": pop_note,
        # rank within the named peers when a percentile is not allowed (review Blocker 3)
        "peer_rank": rank_within_peers(total, peers) if (filters and peers and n_peer < min_n) else None,
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
