"""Load and validate the instrument YAML (pydantic models). Default: instrument-v0.2.yaml.

Change log: v0.2 (2026-10-25) — default instrument v0.2; band intervals; V2 share
intervals (decision 8); interview minimum (decision 11); decisions register (md §5.6).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

INSTRUMENT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INSTRUMENT_PATH = INSTRUMENT_DIR / "instrument-v0.2.yaml"
V0_1_INSTRUMENT_PATH = INSTRUMENT_DIR / "instrument-v0.1.yaml"  # kept for history

EvidenceClass = Literal["D", "S", "I", "O"]


class Proxy(BaseModel):
    signal: str
    validation: str


class Item(BaseModel):
    id: str
    dimension: str
    question: str
    anchors: dict[int, str]
    evidence_class_required: list[EvidenceClass]
    evidence_class_required_text: str
    kappa_subset: bool
    kappa_reason: Optional[str] = None
    note: Optional[str] = None
    framework_map: list[str] = Field(default_factory=list)
    outside_in_proxies: list[Proxy] = Field(default_factory=list)

    @field_validator("anchors")
    @classmethod
    def _five_levels(cls, v: dict[int, str]) -> dict[int, str]:
        if set(v) != {1, 2, 3, 4, 5}:
            raise ValueError("anchors must cover levels 1–5")
        return v


class Dimension(BaseModel):
    id: str
    name: str
    weight: float
    justification: str = ""


class Band(BaseModel):
    name: str
    low: float
    high: float
    interval: str = ""  # v0.2: upper-inclusive, e.g. "25 < C ≤ 50"
    meaning: str = ""
    target_share: str = ""


class ValueItem(BaseModel):
    id: str
    question: str
    scale_type: Literal["band", "level"]
    scale: list[Union[str, int]]
    scale_labels: Union[dict, str, None] = None
    evidence_required: str
    evidence_class_required: list[EvidenceClass]
    self_report_cap: Union[str, int, None] = None
    unevidenced_value: Union[str, int, None] = None
    unevidenced_label: Optional[str] = None
    dependency: Optional[dict] = None
    calibration_anchor: str = ""
    note: Optional[str] = None
    share_intervals: Optional[list[dict]] = None  # V2 only (v0.2 decision 8)

    def band_for_share(self, share: float) -> str:
        """Map an unrounded share (0–100) to its band code using upper-inclusive
        edges (v0.2 decision 8): p < 12 · 12 ≤ p ≤ 39 · 39 < p ≤ 61 · p > 61."""
        if not self.share_intervals:
            raise ValueError(f"{self.id}: no share intervals defined")
        if not 0 <= share <= 100:
            raise ValueError(f"{self.id}: share {share} outside 0–100")
        for iv in self.share_intervals:
            lo, hi = iv.get("low"), iv.get("high")
            lo_ok = lo is None or (share >= lo if iv.get("low_inclusive") else share > lo)
            hi_ok = hi is None or (share <= hi if iv.get("high_inclusive") else share < hi)
            if lo_ok and hi_ok:
                return str(iv["code"])
        raise ValueError(f"{self.id}: share {share} not covered by the intervals")  # pragma: no cover

    def rank(self, value: Union[str, int]) -> int:
        """Position of a value on the ordinal scale (0 = lowest)."""
        sv = [str(s) for s in self.scale]
        return sv.index(str(value))


class VarianceSpec(BaseModel):
    min_respondents_for_sigma: int = 5
    sigma_flag_threshold: float = 1.0
    alignment_not_aligned_share: float = 0.5
    exco_gap_flag_abs: float = 0.75


class CapSpec(BaseModel):
    self_report_cap: int = 3
    scope: str = "per_response"
    interview_min_independent: int = 2  # v0.2 decision 11
    evidence_coverage_self_report_dominant_below: float = 0.60


class PeerSpec(BaseModel):
    min_n: int = 15
    fallback_label: str = "global, peer n insufficient"


class ScoringSpec(BaseModel):
    item_scale: dict[str, int]
    dimension_items: int = 6
    dimension_min_items_scored: int = 4
    rounding_decimals: int = 1
    cap_rule: CapSpec
    variance: VarianceSpec
    peer_percentile: PeerSpec

    @model_validator(mode="before")
    @classmethod
    def _defaults(cls, data):
        data = dict(data)
        data.setdefault("rounding_decimals", 1)
        return data


class KappaSpec(BaseModel):
    items_count: int = 20
    subset: list[str]
    thresholds: dict
    exit_min_items_accept: int = 16


class Instrument(BaseModel):
    instrument: dict
    scoring: ScoringSpec
    bands: dict
    dimensions: list[Dimension]
    items: list[Item]
    value_axis: dict
    kappa: KappaSpec
    decisions_v0_2: list[dict] = Field(default_factory=list)

    # ---- derived helpers -------------------------------------------------
    @property
    def version(self) -> str:
        return str(self.instrument.get("version", "?"))

    @property
    def band_list(self) -> list[Band]:
        return [Band(**b) for b in self.bands["list"]]

    @property
    def production_boundary(self) -> float:
        return float(self.bands.get("production_boundary", 50))

    @property
    def weights(self) -> dict[str, float]:
        return {d.id: d.weight for d in self.dimensions}

    @property
    def dimension_by_id(self) -> dict[str, Dimension]:
        return {d.id: d for d in self.dimensions}

    @property
    def item_by_id(self) -> dict[str, Item]:
        return {i.id: i for i in self.items}

    @property
    def items_by_dimension(self) -> dict[str, list[Item]]:
        out: dict[str, list[Item]] = {d.id: [] for d in self.dimensions}
        for it in self.items:
            out[it.dimension].append(it)
        return out

    @property
    def value_items(self) -> list[ValueItem]:
        return [ValueItem(**v) for v in self.value_axis["items"]]

    @property
    def value_item_by_id(self) -> dict[str, ValueItem]:
        return {v.id: v for v in self.value_items}

    @property
    def kappa_subset(self) -> list[str]:
        return list(self.kappa.subset)

    @model_validator(mode="after")
    def _consistency(self) -> "Instrument":
        if abs(sum(d.weight for d in self.dimensions) - 100) > 1e-9:
            raise ValueError("dimension weights must sum to 100")
        dims = {d.id for d in self.dimensions}
        for it in self.items:
            if it.dimension not in dims:
                raise ValueError(f"{it.id}: unknown dimension {it.dimension}")
        ids = [i.id for i in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate item ids")
        flagged = {i.id for i in self.items if i.kappa_subset}
        if flagged != set(self.kappa.subset):
            raise ValueError("kappa_subset flags do not match kappa.subset list")
        return self


def load_instrument(path: Union[str, Path, None] = None) -> Instrument:
    p = Path(path) if path else DEFAULT_INSTRUMENT_PATH
    with open(p, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return Instrument(**raw)
