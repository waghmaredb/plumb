"""Financial and KPI decomposition scaffold (framework Phase 1 module 7:
"financial and KPI decomposition versus peers"; competitive ranking exhibit
on economic profit and KPI percentiles).

Input: ``<subject_dir>/financials.csv`` with one row per entity and fiscal
year. Monetary columns are in **millions of the row's currency**; ratios in
percent. Columns:

    entity, role (subject|core|secondary), fy, currency,
    revenue, npat, total_assets, equity, cost_income, roe,
    source_urls (';'-separated), note,
    optional <kpi>_as_reported columns holding the figure exactly as the
    source prints it (e.g. "RM10.51bn") so the claim text matches the passage.

Outputs: percentile rank of the subject on each KPI against core peers in
the same FY (share of peers at or below; direction noted for cost-income),
number claims for every KPI value that has a source (the subject's are
load-bearing: scorecards are load-bearing by default, spec C3, so they need
two independent upstreams or they block), and the economic-profit
placeholder EP = NOPAT − capital charge with every assumption as an explicit
field. Currency conversion is NOT performed: percentiles are only computed on
ratios (ROE, cost-income) and on absolute KPIs when every row shares a
currency; otherwise the KPI is reported with a gap.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import Subject

MODULE = "financials"
KPIS = {  # column -> (label, kind, higher_is_better)
    "revenue": ("revenue", "money", True),
    "npat": ("net profit", "money", True),
    "total_assets": ("total assets", "money", True),
    "equity": ("shareholders' equity", "money", True),
    "cost_income": ("cost-to-income ratio", "pct", False),
    "roe": ("return on equity", "pct", True),
}
CURRENCY_PREFIX = {"SGD": "S$", "MYR": "RM", "USD": "US$", "HKD": "HK$", "AUD": "A$", "GBP": "£", "EUR": "€", "THB": "THB ", "IDR": "IDR "}


@dataclass
class FinRow:
    entity: str
    role: str
    fy: int
    currency: str
    values: dict[str, float] = field(default_factory=dict)
    as_reported: dict[str, str] = field(default_factory=dict)
    source_urls: list[str] = field(default_factory=list)
    note: str = ""


def load_financials(path: str | Path) -> list[FinRow]:
    path = Path(path)
    rows: list[FinRow] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            vals: dict[str, float] = {}
            rep: dict[str, str] = {}
            for k in KPIS:
                v = (r.get(k) or "").strip()
                if v:
                    try:
                        vals[k] = float(v.replace(",", ""))
                    except ValueError:
                        pass
                ar = (r.get(f"{k}_as_reported") or "").strip()
                if ar:
                    rep[k] = ar
            rows.append(FinRow(entity=r["entity"].strip(), role=(r.get("role") or "core").strip().lower(), fy=int(r["fy"]),
                               currency=(r.get("currency") or "").strip().upper(), values=vals, as_reported=rep,
                               source_urls=[u.strip() for u in (r.get("source_urls") or "").split(";") if u.strip()], note=r.get("note") or ""))
    return rows


def percentile(value: float, peers: list[float], higher_is_better: bool = True) -> Optional[float]:
    """Percentile rank of the subject among peers: share of peers the subject
    beats or ties, in percent. For lower-is-better KPIs the comparison flips so
    100 always means 'best in set'."""
    if not peers:
        return None
    if higher_is_better:
        return round(100.0 * sum(1 for v in peers if v <= value) / len(peers), 1)
    return round(100.0 * sum(1 for v in peers if v >= value) / len(peers), 1)


class EconomicProfitAssumptions(BaseModel):
    """Every input to EP = NOPAT − capital charge, explicit. For banks and
    insurers NOPAT is taken as NPAT (interest is operating income, not a
    financing cost), and the capital base is shareholders' equity, so
    EP = NPAT − cost_of_equity × equity. Nothing is defaulted silently."""

    cost_of_equity: Optional[float] = None  # decimal, e.g. 0.10; must be set by the engagement lead with a CAPM note
    capital_base: str = "equity"  # column used as the capital base
    nopat_basis: str = "npat"  # 'npat' for FIs; 'ebit_after_tax' for corporates (not implemented)
    tax_rate: Optional[float] = None  # only used when nopat_basis != 'npat'
    rationale: Optional[str] = None


class EconomicProfit(BaseModel):
    entity: str
    fy: int
    currency: str
    nopat: Optional[float]
    capital_base_value: Optional[float]
    capital_charge: Optional[float]
    economic_profit: Optional[float]
    assumptions: EconomicProfitAssumptions
    status: str  # computed | missing-assumption | missing-input


def economic_profit(row: FinRow, a: EconomicProfitAssumptions) -> EconomicProfit:
    nopat = row.values.get("npat") if a.nopat_basis == "npat" else None
    cap = row.values.get(a.capital_base)
    if a.cost_of_equity is None:
        return EconomicProfit(entity=row.entity, fy=row.fy, currency=row.currency, nopat=nopat, capital_base_value=cap, capital_charge=None,
                              economic_profit=None, assumptions=a, status="missing-assumption: cost_of_equity not set")
    if nopat is None or cap is None:
        return EconomicProfit(entity=row.entity, fy=row.fy, currency=row.currency, nopat=nopat, capital_base_value=cap, capital_charge=None,
                              economic_profit=None, assumptions=a, status=f"missing-input: {'npat' if nopat is None else a.capital_base}")
    charge = a.cost_of_equity * cap
    return EconomicProfit(entity=row.entity, fy=row.fy, currency=row.currency, nopat=nopat, capital_base_value=cap, capital_charge=round(charge, 2),
                          economic_profit=round(nopat - charge, 2), assumptions=a, status="computed")


def _fmt(row: FinRow, k: str) -> str:
    if k in row.as_reported:
        return row.as_reported[k]
    v = row.values[k]
    if KPIS[k][1] == "pct":
        return f"{v:g}%"
    pre = CURRENCY_PREFIX.get(row.currency, row.currency + " ")
    return f"{pre}{v:,.1f} million"


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None,
        assumptions: Optional[EconomicProfitAssumptions] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    path = ctx.subject_dir / "financials.csv"
    rows = load_financials(path)
    gaps: list[Gap] = []
    if not rows:
        gaps.append(Gap(module=MODULE, topic="no financials", detail=f"{path} missing or empty; populate from segment disclosures / MAS returns "
                        "(alpha-targets §5.1: value axis reported as Band A 'not evidenced')", instrument_items=["V1", "D8.3"], verify_flag=True))
        return ModuleResult(module=MODULE, subject_slug=subject.slug, gaps=gaps, data_available=False)
    ctx.log_call(MODULE, "load_csv", str(path), "ok", rows=len(rows))
    a = assumptions or EconomicProfitAssumptions()
    fy = max(r.fy for r in rows if r.role == "subject") if any(r.role == "subject" for r in rows) else max(r.fy for r in rows)
    subj = next((r for r in rows if r.role == "subject" and r.fy == fy), None)
    core = [r for r in rows if r.role == "core" and r.fy == fy]
    claims: list[ResearchClaim] = []
    signals: list[Signal] = []
    for r in rows:
        if not r.source_urls:
            gaps.append(Gap(module=MODULE, topic="unsourced KPI row", detail=f"{r.entity} FY{r.fy}: no source_urls; KPIs cannot be verified", verify_flag=True))
            continue
        tier = ctx.tier_of(r.source_urls[0])
        for k in r.values:
            label, kind, _ = KPIS[k]
            text = f"{r.entity} {label} of {_fmt(r, k)} in FY{r.fy}"
            claims.append(ResearchClaim(id=f"{subject.slug}.fin.{_slug(r.entity)}.{r.fy}.{k}", module=MODULE, text=text, kind=ClaimKind.number,
                                        load_bearing=(r.role == "subject"), sources=list(r.source_urls), tier=tier,
                                        confidence_label=confidence_for_tier(tier), instrument_items=["KPI"], signal_ids=[f"{subject.slug}.fin.pct.{k}"],
                                        value=r.values[k], unit=("%" if kind == "pct" else f"{r.currency} m"), period=f"FY{r.fy}",
                                        note=("scorecard figure: load-bearing, two independent upstreams required (C6)" if r.role == "subject" else "peer figure: directional")))
    pct_table: dict[str, dict] = {}
    if subj is None:
        gaps.append(Gap(module=MODULE, topic="subject row missing", detail=f"no role=subject row for FY{fy}", instrument_items=["KPI"]))
    else:
        for k, (label, kind, hib) in KPIS.items():
            if k not in subj.values:
                continue
            peers = [r for r in core if k in r.values]
            if kind == "money" and any(r.currency != subj.currency for r in peers):
                gaps.append(Gap(module=MODULE, topic=f"{label} percentile", detail="mixed currencies in peer rows; conversion not performed, percentile skipped"))
                continue
            p = percentile(subj.values[k], [r.values[k] for r in peers], hib)
            pct_table[k] = {"subject": subj.values[k], "percentile": p, "peer_n": len(peers), "higher_is_better": hib,
                            "peers": {r.entity: r.values[k] for r in peers}}
            signals.append(Signal(id=f"{subject.slug}.fin.pct.{k}", module=MODULE, name=f"{label} — percentile vs core peers (FY{fy})",
                                  instrument_items=["KPI", "V1-context"], value=p, unit="percentile", source=str(path),
                                  confidence_label=ConfidenceLabel.model_inferred,
                                  evidence_claim_ids=[c.id for c in claims if c.signal_ids == [f"{subject.slug}.fin.pct.{k}"]],
                                  detail=pct_table[k], status="computed" if p is not None else "not-available",
                                  note=f"peer n = {len(peers)}" + ("; below §5.5 minimum of 15: directional" if len(peers) < 15 else "")))
        ep = economic_profit(subj, a)
        signals.append(Signal(id=f"{subject.slug}.fin.economic_profit", module=MODULE, name=f"Economic profit placeholder (FY{fy})",
                              instrument_items=["ranking-exhibit"], value=ep.economic_profit, unit=f"{subj.currency} m", source=str(path),
                              confidence_label=ConfidenceLabel.model_inferred, detail=ep.model_dump(mode="json"), status="computed" if ep.status == "computed" else "not-available",
                              note=ep.status))
        if ep.status != "computed":
            gaps.append(Gap(module=MODULE, topic="economic profit", detail=ep.status + " — set EconomicProfitAssumptions (cost_of_equity with CAPM rationale) before the ranking exhibit",
                            instrument_items=["ranking-exhibit"]))
        for r in core:
            signals.append(Signal(id=f"{subject.slug}.fin.economic_profit.{_slug(r.entity)}", module=MODULE, name=f"Economic profit placeholder — {r.entity} (FY{fy})",
                                  instrument_items=["ranking-exhibit"], value=economic_profit(r, a).economic_profit, unit=f"{r.currency} m", source=str(path),
                                  confidence_label=ConfidenceLabel.model_inferred, detail=economic_profit(r, a).model_dump(mode="json"), note=economic_profit(r, a).status))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        exhibits={"kpi-percentiles.md": _exhibit(subject, fy, pct_table, subj, core)}, data_available=True,
                        detail={"fy": fy, "rows": len(rows), "percentiles": pct_table})


def _exhibit(subject: Subject, fy: int, pct: dict, subj: Optional[FinRow], core: list[FinRow]) -> str:
    L = [f"# KPI percentiles vs core peers — {subject.name} FY{fy}", ""]
    if not pct:
        L.append("No percentiles computed (see gap register).")
        return "\n".join(L)
    L.append("| KPI | Subject | Peer n | Percentile (100 = best) | Peer values |")
    L.append("|---|---|---|---|---|")
    for k, d in pct.items():
        label = KPIS[k][0]
        unit = "%" if KPIS[k][1] == "pct" else f" {subj.currency} m"
        peers = "; ".join(f"{n}: {v:,.1f}" for n, v in d["peers"].items())
        L.append(f"| {label} | {d['subject']:,.1f}{unit} | {d['peer_n']} | {d['percentile'] if d['percentile'] is not None else '—'} | {peers} |")
    L.append("")
    L.append("Percentile = share of core peers the subject beats or ties; cost-to-income is inverted so 100 is best. "
             "Peer n below 15 is directional (instrument §5.5). Figures are load-bearing for the subject and need two independent upstreams before release.")
    return "\n".join(L)


def _slug(s: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
