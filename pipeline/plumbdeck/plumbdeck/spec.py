"""Deck spec loader. The schema is closed: an unknown key is an error, so no spec can
smuggle in a switch that weakens the interlock (there is no such switch)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

TOP_KEYS = {"spec_version", "name", "ghost_deck", "deliverable", "slides"}
DELIVERABLE_KEYS = {"id", "version", "firm", "tools", "scope_of_ai", "corrections_contact", "verification_control_owner", "jurisdictions"}
SLIDE_KEYS = {"id", "section", "kind", "title", "title_withheld", "exhibit", "bind", "so_what", "requires", "optional", "source", "exhibit_note"}
KINDS = {"cover", "disclosure", "data", "register", "offer", "placeholder"}
EXHIBITS = {"cover", "disclosure", "peer_funnel", "signals_table", "scorecard_two_axis", "gap_register", "evidence_log", "placeholder",
            # P5 pre-read: claim-bound lists, SCQA from released claims, questions for management, rubric detail, offer text
            "claim_list", "scqa", "questions", "rubric_detail", "offer"}
SOURCE_KEYS = {"tier", "doc", "date", "confidence"}


class SpecError(Exception):
    pass


@dataclass
class SlideSpec:
    id: str
    section: str
    kind: str
    title: str
    exhibit: str
    title_withheld: Optional[str] = None
    bind: dict[str, Any] = field(default_factory=dict)
    so_what: Optional[str] = None
    requires: list[str] = field(default_factory=list)
    optional: bool = False
    source: Optional[dict[str, str]] = None
    exhibit_note: Optional[str] = None


@dataclass
class DeckSpec:
    path: Path
    name: str
    spec_version: str
    ghost_deck: str
    deliverable: dict[str, Any]
    slides: list[SlideSpec]


def _unknown(d: dict, allowed: set, where: str) -> None:
    extra = sorted(set(d) - allowed)
    if extra:
        raise SpecError(f"{where}: unknown key(s) {extra}; allowed: {sorted(allowed)}")


def load_spec(path: Path) -> DeckSpec:
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        raise SpecError(f"cannot read spec {path}: {e}") from e
    if not isinstance(raw, dict):
        raise SpecError("spec must be a mapping")
    _unknown(raw, TOP_KEYS, "spec")
    deliv = raw.get("deliverable") or {}
    _unknown(deliv, DELIVERABLE_KEYS, "deliverable")
    slides: list[SlideSpec] = []
    seen: set[str] = set()
    for i, s in enumerate(raw.get("slides") or []):
        if not isinstance(s, dict):
            raise SpecError(f"slides[{i}] is not a mapping")
        _unknown(s, SLIDE_KEYS, f"slide {s.get('id', i)}")
        for req in ("id", "section", "kind", "title"):
            if not s.get(req):
                raise SpecError(f"slide {s.get('id', i)}: missing '{req}'")
        if s["id"] in seen:
            raise SpecError(f"duplicate slide id {s['id']}")
        seen.add(s["id"])
        kind = s["kind"]
        if kind not in KINDS:
            raise SpecError(f"slide {s['id']}: kind '{kind}' not in {sorted(KINDS)}")
        exhibit = s.get("exhibit") or ("placeholder" if kind == "placeholder" else kind)
        if exhibit not in EXHIBITS:
            raise SpecError(f"slide {s['id']}: exhibit '{exhibit}' not in {sorted(EXHIBITS)}")
        if (kind == "offer") != (exhibit == "offer"):
            raise SpecError(f"slide {s['id']}: the offer exhibit goes only on an offer slide (static offer text is never mixed with claim-bound data)")
        if s.get("source") is not None:
            _unknown(s["source"], SOURCE_KEYS, f"slide {s['id']} source")
        slides.append(
            SlideSpec(
                id=str(s["id"]),
                section=str(s["section"]),
                kind=kind,
                title=str(s["title"]),
                exhibit=exhibit,
                title_withheld=s.get("title_withheld"),
                bind=dict(s.get("bind") or {}),
                so_what=s.get("so_what"),
                requires=list(s.get("requires") or []),
                optional=bool(s.get("optional", False)),
                source=s.get("source"),
                exhibit_note=s.get("exhibit_note"),
            )
        )
    ids = [s.id for s in slides]
    if "S02" not in ids:
        raise SpecError("spec has no S02: the deck cannot be exported without the disclosure slide (R9)")
    return DeckSpec(
        path=path,
        name=str(raw.get("name") or path.stem),
        spec_version=str(raw.get("spec_version") or "0"),
        ghost_deck=str(raw.get("ghost_deck") or ""),
        deliverable=deliv,
        slides=slides,
    )
