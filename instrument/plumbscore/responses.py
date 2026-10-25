"""Load respondent CSVs.

Columns: respondent_id, role_group [exco|operating], item_id, score,
evidence_class [D|S|I|O|none], evidence_ref. Optional: role (free text used
for the "roles at each extreme" output, §5.3 — roles, not names).

Capability items (D1.1–D8.6): score is an integer 1–5.
Value-axis items (V1–V4) may appear in the same file; their score is the band
code / level on that item's own scale (e.g. "B", "40–61%", 4, 2).

evidence_class may list several classes joined by "+" (e.g. "D+S") for items
whose Ev≥4 column requires two classes; a single response row is then the
assessor's record that both artefacts are logged.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Literal, Optional, Union

from pydantic import BaseModel, field_validator

RoleGroup = Literal["exco", "operating"]
VALID_CLASSES = {"D", "S", "I", "O"}


def parse_evidence_classes(raw: Optional[str]) -> frozenset[str]:
    if raw is None:
        return frozenset()
    s = raw.strip()
    if not s or s.lower() in {"none", "na", "n/a", "-"}:
        return frozenset()
    parts = [p.strip().upper() for p in s.replace("|", "+").replace(",", "+").split("+")]
    bad = [p for p in parts if p and p not in VALID_CLASSES]
    if bad:
        raise ValueError(f"unknown evidence class(es) {bad!r} in {raw!r}")
    return frozenset(p for p in parts if p)


class Response(BaseModel):
    respondent_id: str
    role_group: RoleGroup
    item_id: str
    score: Union[int, str]
    evidence_classes: frozenset[str] = frozenset()
    evidence_ref: str = ""
    role: str = ""

    @field_validator("role_group", mode="before")
    @classmethod
    def _norm_role(cls, v):
        if isinstance(v, str):
            v = v.strip().lower()
            if v in {"exco", "executive", "exec", "c-suite"}:
                return "exco"
            if v in {"operating", "ops", "operating-manager", "manager", "operational"}:
                return "operating"
        return v

    @property
    def is_capability(self) -> bool:
        return self.item_id.upper().startswith("D")

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence_classes)


def _coerce_score(item_id: str, raw: str) -> Union[int, str]:
    s = (raw or "").strip()
    if item_id.upper().startswith("D"):
        try:
            v = int(float(s))
        except ValueError as e:
            raise ValueError(f"{item_id}: score {raw!r} is not an integer") from e
        if not 1 <= v <= 5:
            raise ValueError(f"{item_id}: score {v} outside 1–5")
        return v
    # value-axis: keep as string; digits become int for level scales
    if s.lstrip("-").isdigit():
        return int(s)
    return s


def load_responses(path: Union[str, Path]) -> list[Response]:
    rows: list[Response] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"respondent_id", "role_group", "item_id", "score"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"responses CSV missing columns: {sorted(missing)}")
        for n, r in enumerate(reader, start=2):
            item_id = (r.get("item_id") or "").strip()
            if not item_id:
                continue
            try:
                rows.append(
                    Response(
                        respondent_id=(r.get("respondent_id") or "").strip(),
                        role_group=r.get("role_group") or "",
                        item_id=item_id,
                        score=_coerce_score(item_id, r.get("score") or ""),
                        evidence_classes=parse_evidence_classes(r.get("evidence_class")),
                        evidence_ref=(r.get("evidence_ref") or "").strip(),
                        role=(r.get("role") or "").strip(),
                    )
                )
            except Exception as e:  # re-raise with line number
                raise ValueError(f"{path}:{n}: {e}") from e
    return rows


def responses_from_records(records: Iterable[dict]) -> list[Response]:
    """Build responses from dicts (used by tests)."""
    out = []
    for r in records:
        r = dict(r)
        ec = r.pop("evidence_class", None)
        if "evidence_classes" not in r:
            r["evidence_classes"] = parse_evidence_classes(ec)
        r["score"] = _coerce_score(r["item_id"], str(r["score"]))
        out.append(Response(**r))
    return out
