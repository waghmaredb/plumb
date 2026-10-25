"""Renderer-neutral slide model: an exhibit builder produces blocks; Markdown and
PPTX renderers draw the same blocks, so the two outputs cannot drift."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class Para:
    text: str
    style: str = "normal"  # normal | lead | muted | strong | withheld


@dataclass
class Bullets:
    items: list[str]


@dataclass
class Table:
    header: list[str]
    rows: list[list[str]]
    widths: Optional[list[float]] = None  # relative column widths
    font_pt: int = 10
    rows_per_slide: int = 14  # PPTX pagination


@dataclass
class Bar:
    label: str
    value: float
    note: str = ""


@dataclass
class Bars:
    """Capability bars on a 0..100 scale with band ticks and a boundary line."""
    bars: list[Bar]
    ticks: list[tuple[float, str]] = field(default_factory=list)
    boundary: Optional[float] = None
    boundary_label: str = ""


@dataclass
class Cells:
    """A small grid of labelled value cells (value axis V1-V4)."""
    cells: list[tuple[str, str, str]]  # (label, value, note)
    columns: int = 2


@dataclass
class Columns:
    left: list["Block"]
    right: list["Block"]
    ratio: float = 0.6


Block = Union[Para, Bullets, Table, Bars, Cells, Columns]

KINDS = ("cover", "disclosure", "data", "register", "placeholder")


@dataclass
class Slide:
    id: str
    section: str
    kind: str  # cover | disclosure | data | register | placeholder
    title: str
    blocks: list[Block] = field(default_factory=list)
    so_what: Optional[str] = None
    source_line: Optional[str] = None
    banner: Optional[str] = None
    footer: str = ""
    placeholder_reason: Optional[str] = None  # "requires engagement data" | "withheld"
    bound_claims: list[str] = field(default_factory=list)
    withheld_claims: list[str] = field(default_factory=list)
    optional: bool = False
    title_exempt: bool = False  # cover: rule R3 does not apply

    @property
    def is_data(self) -> bool:
        return self.kind in ("data", "register")
