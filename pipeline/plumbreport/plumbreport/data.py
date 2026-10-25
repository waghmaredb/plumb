"""Loaders for the inputs a report is bound to.

* run folder  - claims.json (statements, exact quotations, PDF page) and report.json
                (verification decisions, observations, questions for management)
* storyline   - resolved.json from the executive deck (synthesis sentences + support)
* research    - RESEARCH.md from an update run (tables keyed by row number "4.1")
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VERIFIED = "verified"


class InputError(Exception):
    """An input file is missing or malformed."""


# --------------------------------------------------------------------------- run

@dataclass
class Claim:
    id: str
    text: str
    kind: str
    status: str                 # decision status: verified / blocked / missing
    reasons: list[str]
    pdf_page: int | None
    sources: list[str]
    attrs: dict[str, Any]

    @property
    def verified(self) -> bool:
        return self.status == VERIFIED


@dataclass
class Run:
    path: Path
    subject: str
    claims: dict[str, Claim]
    observations: dict[str, dict]
    questions: dict[str, dict]
    gaps: list[dict] = field(default_factory=list)

    def claim(self, cid: str) -> Claim:
        try:
            return self.claims[cid]
        except KeyError:
            raise InputError(f"statement {cid!r} is not in {self.path / 'claims.json'}") from None


def _read_json(p: Path) -> Any:
    if not p.exists():
        raise InputError(f"missing input: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise InputError(f"{p}: not valid JSON ({e})") from None


def load_run(run_dir: str | Path) -> Run:
    run_dir = Path(run_dir)
    cj = _read_json(run_dir / "claims.json")
    rj = _read_json(run_dir / "report.json")
    decisions = {d["claim_id"]: d for d in rj.get("verification", {}).get("decisions", [])}
    claims: dict[str, Claim] = {}
    for c in cj.get("claims", []):
        d = decisions.get(c["id"])
        status = d["status"] if d else "missing"
        if d and d.get("blocked"):
            status = "blocked"
        attrs = c.get("attrs") or {}
        page = attrs.get("page_expected")
        claims[c["id"]] = Claim(
            id=c["id"], text=c["text"], kind=c.get("kind", ""), status=status,
            reasons=list(d.get("reasons", [])) if d else ["no verification decision recorded"],
            pdf_page=int(page) if page else None, sources=list(c.get("sources", [])), attrs=attrs,
        )
    f = rj.get("findings") or {}
    obs = {o["id"]: o for o in f.get("observations", [])}
    qs = {q["id"]: q for q in f.get("questions", [])}
    gaps = rj.get("gap_register") or []
    if isinstance(gaps, dict):
        gaps = [gaps]
    return Run(path=run_dir, subject=cj.get("subject", ""), claims=claims,
               observations=obs, questions=qs, gaps=gaps)


# --------------------------------------------------------------------- storyline

@dataclass
class Storyline:
    path: Path
    data: dict

    @property
    def final(self) -> bool:
        return bool((self.data.get("_status") or {}).get("final"))

    @property
    def marker(self) -> str:
        return (self.data.get("_status") or {}).get("marker") or ("" if self.final else "Discussion draft")

    def get(self, ref: str) -> Any:
        """Resolve 'exec-summary.points[0].body' -> node."""
        parts = ref.split(".")
        slide_id, rest = parts[0], parts[1:]
        node: Any = next((s for s in self.data.get("slides", []) if s.get("id") == slide_id), None)
        if node is None:
            raise InputError(f"storyline has no slide {slide_id!r} (ref {ref!r})")
        for part in rest:
            m = re.fullmatch(r"([\w-]+)(?:\[(\d+)\])?", part)
            if not m:
                raise InputError(f"bad storyline ref {ref!r}")
            key, idx = m.group(1), m.group(2)
            if not isinstance(node, dict) or key not in node:
                raise InputError(f"storyline ref {ref!r}: no key {key!r}")
            node = node[key]
            if idx is not None:
                try:
                    node = node[int(idx)]
                except (IndexError, TypeError):
                    raise InputError(f"storyline ref {ref!r}: index {idx} out of range") from None
        return node


def load_storyline(p: str | Path) -> Storyline:
    p = Path(p)
    return Storyline(path=p, data=_read_json(p))


# ---------------------------------------------------------------------- research

_URL = re.compile(r"https?://[^\s;|)]+")


@dataclass
class ResearchRow:
    id: str
    section: str
    cells: dict[str, str]
    urls: list[str]
    confidence: str

    def get(self, *names: str) -> str:
        for n in names:
            for k, v in self.cells.items():
                if k.startswith(n):
                    return v
        return ""


@dataclass
class Research:
    path: Path
    text: str
    rows: dict[str, ResearchRow]

    def row(self, rid: str) -> ResearchRow:
        try:
            return self.rows[str(rid)]
        except KeyError:
            raise InputError(f"research row {rid!r} is not in {self.path}") from None


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def load_research(p: str | Path) -> Research:
    p = Path(p)
    if not p.exists():
        raise InputError(f"missing input: {p}")
    text = p.read_text(encoding="utf-8")
    all_urls = [u.rstrip(".,") for u in _URL.findall(text)]
    rows: dict[str, ResearchRow] = {}
    section = ""
    header: list[str] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            section, header = line[3:].strip(), None
            continue
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = _split_row(line)
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if not header or header[0] != "#" or not re.fullmatch(r"\d+\.\d+", cells[0]):
            continue
        cmap = dict(zip(header, cells))
        url_cell = cmap.get("url", "")
        urls = [u.rstrip(".,") for u in _URL.findall(url_cell)]
        # bare file names "x.pdf (above)" -> the full URL elsewhere in the document
        for name in re.findall(r"([\w%.-]+\.pdf)\b", url_cell):
            if not any(u.endswith(name) for u in urls):
                full = next((u for u in all_urls if u.endswith(name)), None)
                if full:
                    urls.append(full)
        conf = cmap.get("confidence", "")
        if not conf and section.startswith("5."):
            conf = "confirmed-from-primary"
        rows[cells[0]] = ResearchRow(id=cells[0], section=section, cells=cmap, urls=urls, confidence=conf)
    # "as 4.1" inherits the URLs of the referenced row
    for r in rows.values():
        m = re.fullmatch(r"as (\d+\.\d+)", r.cells.get("url", "").strip())
        if m and not r.urls and m.group(1) in rows:
            r.urls = list(rows[m.group(1)].urls)
    return Research(path=p, text=text, rows=rows)
