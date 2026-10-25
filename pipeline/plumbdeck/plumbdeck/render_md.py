"""Markdown renderer. Each slide is delimited by an HTML comment marker that the
lint pass parses: ``<!-- plumbdeck:slide id=S06 kind=data -->``."""
from __future__ import annotations

from .model import Bars, Block, Boxes, Bullets, Cells, Columns, Para, Slide, Table


def _esc(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _bar(value: float, width: int = 40, boundary: float | None = None) -> str:
    filled = int(round(max(0.0, min(100.0, value)) / 100 * width))
    cells = ["█" if i < filled else "░" for i in range(width)]
    if boundary is not None:
        b = int(round(boundary / 100 * width))
        if 0 <= b < width:
            cells[b] = "┃"
    return "".join(cells)


def _block(b: Block) -> list[str]:
    if isinstance(b, Para):
        t = b.text
        if b.style in ("lead", "strong"):
            t = f"**{t}**"
        elif b.style == "muted":
            t = f"_{t}_"
        elif b.style in ("withheld", "withheld_inline"):
            t = f"**{t}**"
        return [t, ""]
    if isinstance(b, Bullets):
        return [f"- {i}" for i in b.items] + [""]
    if isinstance(b, Table):
        out = ["| " + " | ".join(_esc(h) for h in b.header) + " |", "|" + "---|" * len(b.header)]
        out += ["| " + " | ".join(_esc(c) for c in r) + " |" for r in b.rows]
        return out + [""]
    if isinstance(b, Bars):
        out = ["```"]
        for bar in b.bars:
            out.append(f"{bar.label:<28} {_bar(bar.value, boundary=b.boundary)} {bar.value:5.1f}  {bar.note}")
        if b.boundary is not None:
            out.append(f"{'':<28} ┃ = {b.boundary_label} ({b.boundary:g}); bands: " + " · ".join(t for _, t in b.ticks))
        out.append("```")
        return out + [""]
    if isinstance(b, Cells):
        out = ["| Item | Recorded | Note |", "|---|---|---|"]
        out += [f"| {_esc(l)} | {_esc(v)} | {_esc(n)} |" for l, v, n in b.cells]
        return out + [""]
    if isinstance(b, Boxes):
        out = []
        for label, paras in b.boxes:
            out.append(f"**{label}.** " + " ".join(_block(p)[0] for p in paras))
            out.append("")
        return out
    if isinstance(b, Columns):
        out: list[str] = []
        for x in b.left + b.right:
            out += _block(x)
        return out
    raise TypeError(type(b))


def render_slide(s: Slide) -> str:
    lines = [f"<!-- plumbdeck:slide id={s.id} kind={s.kind} -->"]
    if s.banner:
        lines += [f"> **{s.banner}**", ""]
    tag = f" · {s.placeholder_reason}" if s.placeholder_reason else ""
    lines += [f"**{s.id} · {s.section}**{tag}", "", f"## {s.title}", ""]
    for b in s.blocks:
        lines += _block(b)
    if s.so_what:
        lines += [f"> **So what:** {s.so_what}", ""]
    if s.source_line:
        lines += [s.source_line, ""]
    if s.footer:
        lines += [f"_{s.footer}_", ""]
    lines += ["---", ""]
    return "\n".join(lines)


def render_markdown(deck) -> str:
    il = deck.interlock
    head = [
        f"# {deck.run.client_full} — {deck.spec.name}",
        "",
        f"Deliverable {deck.deliverable_id} v{deck.deliverable_version} · run `{deck.run.run_id}` · spec `{deck.spec.path.name}` · "
        + ("**DRAFT**" if deck.draft else "final (interlock passed)"),
        "",
        il.outcome_sentence,
        "",
        "---",
        "",
    ]
    return "\n".join(head) + "".join(render_slide(s) for s in deck.slides)
