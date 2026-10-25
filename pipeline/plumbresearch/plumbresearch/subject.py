"""Subject and peer-set models plus the YAML loader.

The YAML shape mirrors `docs/alpha-targets.md`: name, listing, tickers, IR
URLs, fiscal year, declared documents, and the peer long-list split into
core / secondary / exited roles. Every figure or URL that alpha-targets marks
**[VERIFY]** keeps that flag as a field (`verify: true`) so the gap register
can carry it forward instead of losing it.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class PeerRole(str, Enum):
    core = "core"
    secondary = "secondary"
    exited = "exited"


class Listing(BaseModel):
    exchange: str
    ticker: Optional[str] = None
    code: Optional[str] = None
    verify: bool = False


class IRLink(BaseModel):
    label: str
    url: str
    verify: bool = False
    note: Optional[str] = None


class Document(BaseModel):
    """A primary document the annual-report module should read.

    ``url`` is the citation of record. ``local_file`` (relative to
    ``data/<slug>/``) lets a PDF that cannot be fetched from the sandbox be
    served under that URL by the local-document transport."""

    kind: str  # annual_report | results_release | analyst_deck | strategy_doc
    fy: Optional[int] = None
    url: str
    local_file: Optional[str] = None
    key: Optional[str] = Field(default=None, description="explicit document key for `plumbresearch ingest --doc`; defaults to '<kind>-<fy>'")
    verify: bool = False
    note: Optional[str] = None

    @property
    def document_key(self) -> str:
        return self.key or (f"{self.kind}-{self.fy}" if self.fy else self.kind)

    def matches_key(self, key: str) -> bool:
        k = (key or "").strip()
        return k in {self.document_key, self.url, self.local_file or "", f"{self.kind}:{self.fy}", f"{self.kind}_{self.fy}"}


class SizeMetric(BaseModel):
    metric: str = "total_assets"
    value_usd_bn: Optional[float] = None
    as_reported: Optional[str] = None
    verify: bool = False
    source_url: Optional[str] = None
    note: Optional[str] = None


class Peer(BaseModel):
    name: str
    role: PeerRole
    listing: Optional[str] = None
    entity: Optional[str] = None  # operating entity when the peer is a subsidiary
    size: SizeMetric = Field(default_factory=SizeMetric)
    why: Optional[str] = None
    reason_secondary: Optional[str] = None
    event: Optional[str] = None  # exited peers: what happened
    event_year: Optional[int] = None
    status: Optional[str] = None  # exited peers: Consolidated | Pending | Failed consolidation | Exit
    sources: list[str] = Field(default_factory=list)
    data_sources: Optional[str] = None
    verify: bool = False
    name_patterns: list[str] = Field(default_factory=list, description="strings that identify the peer in postings / patents / filings")


class Subject(BaseModel):
    slug: str
    name: str
    short_name: str
    sector: str  # banks | insurers | ...
    industry_codes: list[str] = Field(default_factory=list)
    listing: Listing
    tickers: list[str] = Field(default_factory=list)
    regulator_status: Optional[str] = None
    regulated_entity: Optional[str] = None
    fiscal_year_end: str = "12-31"
    latest_fy: int
    home_market: Optional[str] = None
    ir_urls: list[IRLink] = Field(default_factory=list)
    documents: list[Document] = Field(default_factory=list)
    size: SizeMetric = Field(default_factory=SizeMetric)
    name_patterns: list[str] = Field(default_factory=list)
    peers: list[Peer] = Field(default_factory=list)
    seed_description: Optional[str] = None
    tier_overrides: dict[str, list[str]] = Field(default_factory=dict, description="Tier -> extra domains for plumbverify tier rules")
    verify_flags: list[str] = Field(default_factory=list, description="[VERIFY] items carried from the candidate screen")
    org_aliases: dict[str, list[str]] = Field(default_factory=dict, description="Organisation aliases by role: subject, subject_subsidiary, parent; used to attribute leadership titles")
    notes: Optional[str] = None

    @field_validator("name_patterns", mode="before")
    @classmethod
    def _default_patterns(cls, v, info):
        return v or []

    def patterns(self) -> list[str]:
        base = list(self.name_patterns) or [self.short_name, self.name]
        if self.short_name not in base:
            base.append(self.short_name)
        return base

    def find_document(self, key: str) -> Optional[Document]:
        """Resolve `--doc KEY` (document key, URL or local_file) to a declared document."""
        hits = [d for d in self.documents if d.matches_key(key)]
        return hits[0] if hits else None

    def peers_by_role(self, role: PeerRole) -> list[Peer]:
        return [p for p in self.peers if p.role == role]

    def all_verify_items(self) -> list[str]:
        items = list(self.verify_flags)
        if self.size.verify:
            items.append(f"subject size ({self.size.metric}): {self.size.note or 'confirm from audited balance sheet'}")
        for d in self.documents:
            if d.verify:
                items.append(f"document URL [{d.kind} FY{d.fy}]: {d.url} — {d.note or 'confirm exact URL'}")
        for l in self.ir_urls:
            if l.verify:
                items.append(f"IR link '{l.label}': {l.url} — {l.note or 'confirm'}")
        for p in self.peers:
            if p.size.verify:
                items.append(f"peer size for {p.name}: {p.size.note or 'confirm'}")
            if p.verify:
                items.append(f"peer {p.name}: {p.event or p.why or 'confirm details'}")
        return items


class PeerSet(BaseModel):
    """Output of the funnel (modules/peerset.py)."""

    subject_slug: str
    subject_size_usd_bn: Optional[float]
    band_low_usd_bn: Optional[float]
    band_high_usd_bn: Optional[float]
    seed_count: int
    core: list[Peer] = Field(default_factory=list)
    secondary: list[Peer] = Field(default_factory=list)
    exited: list[Peer] = Field(default_factory=list)
    demoted: list[tuple[str, str]] = Field(default_factory=list, description="(peer name, reason) moved core -> secondary by the size filter")
    retained_unverified: list[str] = Field(default_factory=list, description="core peers kept with unverified size")
    warnings: list[str] = Field(default_factory=list)
    percentile_note: str = ""


def load_subject(path: str | Path) -> Subject:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Subject.model_validate(data)


def builtin_subject_path(slug: str) -> Path:
    return Path(__file__).with_name("subjects") / f"{slug}.yaml"
