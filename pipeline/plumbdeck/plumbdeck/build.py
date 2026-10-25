"""Assemble the deck: spec + run + optional scorecard + optional sign-off -> slides -> files."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import __version__
from .exhibits import BUILDERS, Exhibit, withheld_text
from .interlock import Interlock, compute_interlock
from .model import Bullets, Para, Slide
from .runio import RunData
from .spec import DeckSpec, SlideSpec, load_spec

WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
TOKEN = re.compile(r"\{(\w+)(?:\|(\w+))?\}")


def fill(template: str, tokens: dict[str, Any], withheld: set[str]) -> tuple[str, bool]:
    """Fill {token} / {token|word} / {token|Word}; returns (text, used_a_withheld_token)."""
    hit = False

    def sub(m: re.Match) -> str:
        nonlocal hit
        name, flt = m.group(1), m.group(2)
        if name in withheld:
            hit = True
            return "[withheld]"
        v = tokens.get(name)
        if v is None:
            return f"[{name}]"
        if flt in ("word", "Word") and isinstance(v, int) and 0 <= v < len(WORDS):
            w = WORDS[v]
            return w.capitalize() if flt == "Word" else w
        return str(v)

    return TOKEN.sub(sub, template), hit


@dataclass
class Deck:
    spec: DeckSpec
    run: RunData
    interlock: Interlock
    slides: list[Slide]
    scorecard_path: Optional[str]
    deliverable_id: str
    deliverable_version: str

    @property
    def draft(self) -> bool:
        return not self.interlock.passed

    @property
    def stem(self) -> str:
        return "deck-DRAFT" if self.draft else "deck"


def _footer(il: Interlock, ctx: dict, models: list[str]) -> str:
    did, ver = ctx["deliverable_id"], ctx["deliverable_version"]
    if not il.passed:
        return f"DRAFT — not for board use. Deliverable {did} v{ver}."
    firm = ctx["deliverable"].get("firm") or "[Firm]"
    appr = il.approver or il.reviewer
    role = il.approver_role or ""
    who = f"{appr}, {role}" if role else appr
    m = ", ".join(ctx["deliverable"].get("tools") or []) or ", ".join(models) or "[model register]"
    return (f"AI-assisted; human-reviewed and approved by {who}, {il.signoff_date}. Models: {m}. "
            f"All citations fetched and verified; unverified items marked [VERIFY]. {firm} takes full responsibility "
            f"for this content. Deliverable {did} v{ver}.")


def _make_slide(ss: SlideSpec, ex: Exhibit, ctx: dict, il: Interlock) -> Slide:
    tokens = {**ctx["tokens"], **ex.tokens}
    sl = Slide(id=ss.id, section=ss.section, kind=ss.kind, title="", optional=ss.optional,
               bound_claims=list(ex.bound), withheld_claims=list(ex.withheld), title_exempt=(ss.kind == "cover"))
    if ex.requires is not None or ss.kind == "placeholder":
        sl.kind = "placeholder"
        sl.placeholder_reason = "requires engagement data"
        sl.title, _ = fill(ss.title, tokens, set())
        if not sl.title.startswith("[H]"):
            sl.title = "[H] " + sl.title
        need = ex.requires or ss.requires or ["engagement data"]
        sl.blocks = [Para("Placeholder — requires engagement data", "strong"), Bullets(need)]
        if ss.exhibit_note:
            sl.blocks.append(Para(f"Exhibit when built: {ss.exhibit_note}", "muted"))
        if ss.optional:
            sl.blocks.append(Para("Optional slide: delete the ID if unused (IDs are stable; gaps are not renumbered).", "muted"))
        return sl
    if ex.all_withheld:
        sl.kind = "placeholder"
        sl.placeholder_reason = "withheld"
        tpl = ss.title_withheld or f"[H] {ss.title}"
        sl.title, _ = fill(tpl, tokens, ex.withheld_tokens | set(ex.tokens))
        sl.blocks = [
            Para(withheld_text(ex.extra_signal_gaps), "withheld"),
            Para("Every item bound to this slide is withheld, so the slide is a placeholder until the gap register items close (block-not-flag, pipeline C11).", "muted"),
        ]
        if ss.exhibit_note:
            sl.blocks.append(Para(f"Exhibit when built: {ss.exhibit_note}", "muted"))
        return sl
    title, hit = fill(ss.title, tokens, ex.withheld_tokens)
    if (hit or (ss.exhibit == "disclosure" and not il.passed)) and ss.title_withheld:
        title, _ = fill(ss.title_withheld, tokens, ex.withheld_tokens)
    sl.title = title
    sl.blocks = list(ex.blocks)
    sl.source_line = ex.source_line
    if ss.so_what:
        sl.so_what, _ = fill(ss.so_what, tokens, ex.withheld_tokens)
    return sl


def build_deck(spec_path: Path, run_dir: Path, scorecard: Optional[Path] = None, signoff: Optional[Path] = None) -> Deck:
    spec = load_spec(spec_path)
    run = RunData(run_dir)
    il = compute_interlock(run, signoff)
    sc = json.loads(Path(scorecard).read_text(encoding="utf-8")) if scorecard else None
    d = spec.deliverable
    base_ctx = {"subject_slug": run.slug, "run_id": run.run_id, "client": run.client, "client_full": run.client_full,
                "date": run.generated_date, "fy": run.subject.get("latest_fy")}
    did = str(d.get("id") or "PLUMB-{subject_slug}-{run_id}").format(**base_ctx)
    ver = str(d.get("version") or "0.1")
    ctx = {**base_ctx, "deliverable": d, "deliverable_id": did, "deliverable_version": ver, "claim_usage": {}}
    ctx["tokens"] = {**base_ctx, "n_released": il.released, "n_withheld": il.withheld,
                     "deliverable_id": did, "deliverable_version": ver}
    models = run.models_used()
    footer = _footer(il, ctx, models)

    exhibits: dict[str, Exhibit] = {}
    deferred = [s for s in spec.slides if s.exhibit == "evidence_log"]
    for ss in spec.slides:
        if ss in deferred:
            continue
        exhibits[ss.id] = BUILDERS[ss.exhibit](ss, run, il, ctx, sc)
    usage: dict[str, list[str]] = {}
    for sid, ex in exhibits.items():
        for cid in ex.bound:
            if cid in run.claims and run.claims[cid].released and ex.requires is None and not ex.all_withheld:
                usage.setdefault(cid, []).append(sid)
    ctx["claim_usage"] = usage
    for ss in deferred:
        exhibits[ss.id] = BUILDERS[ss.exhibit](ss, run, il, ctx, sc)

    slides = []
    for ss in spec.slides:
        sl = _make_slide(ss, exhibits[ss.id], ctx, il)
        sl.banner = il.banner
        sl.footer = footer
        slides.append(sl)
    return Deck(spec=spec, run=run, interlock=il, slides=slides, scorecard_path=str(scorecard) if scorecard else None,
                deliverable_id=did, deliverable_version=ver)


def titles_markdown(deck: Deck) -> str:
    lines = [f"# Horizontal-flow export — {deck.run.client_full}", "",
             f"Titles only, in order (ghost deck R4). Deliverable {deck.deliverable_id} v{deck.deliverable_version}.", ""]
    if deck.draft:
        lines += [f"> **{deck.interlock.banner}**", ""]
    lines += ["| ID | Section | Action title | Words | State |", "|---|---|---|---|---|"]
    from .lint import title_words
    for s in deck.slides:
        state = s.placeholder_reason or s.kind
        wc = "cover (R3 n/a)" if s.title_exempt else str(title_words(s.title))
        lines.append(f"| {s.id} | {s.section} | {s.title} | {wc} | {state} |")
    return "\n".join(lines) + "\n"


def write_outputs(deck: Deck, out: Path) -> dict[str, Any]:
    from .lint import lint_dir
    from .render_md import render_markdown
    from .render_pptx import render_pptx

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    # never leave a stale final deck beside a draft (or vice versa)
    for old in ("deck.md", "deck.pptx", "deck-DRAFT.md", "deck-DRAFT.pptx"):
        p = out / old
        if p.exists():
            p.unlink()
    md_path = out / f"{deck.stem}.md"
    pptx_path = out / f"{deck.stem}.pptx"
    md_path.write_text(render_markdown(deck), encoding="utf-8")
    render_pptx(deck, pptx_path)
    (out / "titles.md").write_text(titles_markdown(deck), encoding="utf-8")
    manifest = {
        "plumbdeck_version": __version__,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "spec": str(Path(deck.spec.path).resolve()),
        "run_dir": str(deck.run.run_dir.resolve()),
        "scorecard": str(Path(deck.scorecard_path).resolve()) if deck.scorecard_path else None,
        "signoff": str(Path(deck.interlock.signoff_path).resolve()) if deck.interlock.signoff_path else None,
        "deliverable_id": deck.deliverable_id,
        "deliverable_version": deck.deliverable_version,
        "draft": deck.draft,
        "deck_md": md_path.name,
        "deck_pptx": pptx_path.name,
        "titles_md": "titles.md",
        "interlock": deck.interlock.to_dict(),
        "slides": [
            {"id": s.id, "section": s.section, "kind": s.kind, "title": s.title, "title_exempt": s.title_exempt,
             "placeholder_reason": s.placeholder_reason, "is_data": s.is_data, "source_line": s.source_line,
             "bound_claims": s.bound_claims, "withheld_claims": s.withheld_claims, "optional": s.optional}
            for s in deck.slides
        ],
        "gap_ids": {cid: deck.run.claims[cid].gap_id for cid in deck.run.withheld_ids},
    }
    (out / "build.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    report = lint_dir(out)
    return report
