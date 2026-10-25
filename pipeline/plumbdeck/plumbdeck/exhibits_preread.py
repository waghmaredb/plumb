"""Exhibit builders for the outside-in pre-read (product item P5).

Same rules as ``exhibits.py`` (ghost deck R6, R8), plus three of their own:

  * **Claim-bound, not typed.** A slide's content is the verbatim text of released claims
    (bound by id or id prefix), or a structured observation / question emitted by
    ``plumbresearch``. The spec may carry labels, column headers and method notes; it never
    carries a finding.
  * **Questions are not findings.** An observation (e.g. a keyword search that found nothing)
    renders only through the ``questions`` exhibit, labelled as a question with its search
    record and limitations. A question renders only when every basis claim is released;
    otherwise its row reads "Withheld — see gap register G-n".
  * **Offer text is labelled.** The ``offer`` exhibit carries static commercial text and is
    allowed only on a slide of kind ``offer`` (spec loader), headed "Offer — not a finding".

Common ``bind`` keys:
  title_requires: [claim ids]   if any is withheld, the slide uses its ``title_withheld``
"""
from __future__ import annotations

import re
from typing import Any, Optional

from .interlock import Interlock
from .model import Block, Boxes, Bullets, Columns, Para, Table
from .runio import RunData
from .spec import SlideSpec

OFFER_LABEL = "Offer — not a finding"
OBS_LABEL = "Observation, not a finding"


def _ids(run: RunData, ss: SlideSpec, ctx: dict, key: str = "claims", prefix_key: str = "prefix") -> list[str]:
    """Claim ids bound to the slide: explicit ids, then every claim under the prefix(es), in run order."""
    out: list[str] = []
    for cid in ss.bind.get(key) or []:
        cid = str(cid).format(**ctx)
        if cid not in out:
            out.append(cid)
    prefixes = ss.bind.get(prefix_key) or []
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    for p in prefixes:
        for cid in run.claims_with_prefix(str(p).format(**ctx)):
            if cid not in out:
                out.append(cid)
    return out


def _guard_title(ex, run: RunData, ss: SlideSpec, ctx: dict) -> None:
    req = [str(c).format(**ctx) for c in ss.bind.get("title_requires") or []]
    if any(c not in run.claims or not run.claims[c].released for c in req):
        ex.title_withheld_flag = True


def _page(run: RunData, cid: str) -> str:
    c = run.claims.get(cid)
    return f"p. {c.page}" if c and c.page else "—"


def _quote(run: RunData, cid: str, with_page: bool = True) -> str:
    c = run.claims[cid]
    return f"“{c.text}”" + (f" ({_page(run, cid)})" if with_page and c.page else "")


def _gap(run: RunData, cids: list[str]) -> str:
    from .exhibits import withheld_text

    return withheld_text(run.gap_ids(cids))


def _slug(v: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(v).lower()).strip("_")


# ================================================================== claim list
def claim_list(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]):
    """Table of bound claims, verbatim, one row each.

    bind: claims / prefix (ids), exclude_categories, quote_header, attr_columns {attr: header},
          context (append claims whose attrs.of == row id), counts_by [attr], tokens {name: {attr, where}},
          title_requires, font_pt, rows_per_slide, note (method note, muted)."""
    from .exhibits import Exhibit, source_line

    excl = set(ss.bind.get("exclude_categories") or [])
    bound = [c for c in _ids(run, ss, ctx) if c in run.claims and run.claims[c].attrs.get("category") not in excl]
    ex = Exhibit(bound=list(bound), withheld=[c for c in bound if not run.claims[c].released])
    if not bound:
        ex.requires = list(ss.requires or ["claims from the plumbresearch findings module for this slide"])
        return ex
    attr_cols: dict[str, str] = dict(ss.bind.get("attr_columns") or {})
    with_ctx = bool(ss.bind.get("context"))
    ctx_claims = {}
    if with_ctx:
        for cid, c in run.claims.items():
            of = c.attrs.get("of")
            if of in bound:
                ctx_claims.setdefault(of, []).append(cid)
                if cid not in ex.bound:
                    ex.bound.append(cid)
                    if not c.released:
                        ex.withheld.append(cid)
    rows: list[list[str]] = []
    released: list[str] = []
    counts: dict[str, int] = {}
    for i, cid in enumerate(bound, 1):
        c = run.claims[cid]
        if not c.released:
            rows.append([str(i), _gap(run, [cid])] + ["—"] * len(attr_cols) + ["—"])
            continue
        released.append(cid)
        txt = f"“{c.text}”"
        pages = [c.page] if c.page else []
        for x in ctx_claims.get(cid, []):
            if run.claims[x].released:
                txt += f" … “{run.claims[x].text}”"
                released.append(x)
                if run.claims[x].page and run.claims[x].page not in pages:
                    pages.append(run.claims[x].page)
            else:
                txt += f" [{_gap(run, [x])}]"
        also = c.attrs.get("also_reported_on_pages") or []
        page_txt = ("p. " + ", ".join(str(p) for p in pages)) if pages else "—"
        if also:
            page_txt += " (also p. " + ", ".join(str(p) for p in also if p) + ")"
        rows.append([str(i), txt] + [str(c.attrs.get(a) or "—") for a in attr_cols] + [page_txt])
        for a in ss.bind.get("counts_by") or []:
            v = c.attrs.get(a)
            if v is not None:
                k = f"n_{a}_{_slug(v)}"
                counts[k] = counts.get(k, 0) + 1
    if not released:
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(ex.bound)
        return ex
    for a in ss.bind.get("counts_by") or []:  # zero counts for values the spec names
        for v in (ss.bind.get("count_values") or {}).get(a, []):
            counts.setdefault(f"n_{a}_{_slug(v)}", 0)
    ex.tokens.update(counts)
    for a in ss.bind.get("distinct_by") or []:
        ex.tokens[f"n_distinct_{a}"] = len({run.claims[c].attrs.get(a) for c in bound
                                             if run.claims[c].released and run.claims[c].attrs.get(a) is not None})
    ex.tokens["n_rows"] = len(bound)
    ex.tokens["n_rows_released"] = len([c for c in bound if run.claims[c].released])
    for name, spec in (ss.bind.get("tokens") or {}).items():
        where = spec.get("where") or {}
        hit = next((run.claims[c] for c in bound if run.claims[c].released
                    and all(run.claims[c].attrs.get(k) == v for k, v in where.items()) and run.claims[c].attrs.get(spec["attr"])), None)
        if hit is None:
            ex.withheld_tokens.add(name)
        else:
            ex.tokens[name] = hit.attrs[spec["attr"]]
    if ex.withheld and ss.bind.get("title_requires_all"):
        ex.title_withheld_flag = True
    _guard_title(ex, run, ss, ctx)
    header = ["#", ss.bind.get("quote_header") or "What the source says (verbatim)"] + list(attr_cols.values()) + ["Page"]
    widths = [0.3, 6.4] + [1.3] * len(attr_cols) + [1.25]
    ex.blocks = [Table(header, rows, widths=widths, font_pt=int(ss.bind.get("font_pt", 10)),
                       rows_per_slide=int(ss.bind.get("rows_per_slide", 8)))]
    if ss.bind.get("note"):
        ex.blocks.append(Para(str(ss.bind["note"]).format(**ctx), "muted"))
    ex.source_line = source_line(run, released)
    return ex


# ======================================================================= SCQA
def scqa(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]):
    """Situation / Complication / Question / Answer built from released claims only.

    bind.boxes: [{label, claims: [ids], question: <question id or suffix>, offer: <static text>}]
    A box whose claim is withheld shows a placeholder sentence with the gap id instead of the claim.
    ``offer`` text is printed with the "Offer — not a finding" label."""
    from .exhibits import Exhibit, source_line

    ex = Exhibit()
    boxes: list[tuple[str, list[Para]]] = []
    released: list[str] = []
    for b in ss.bind.get("boxes") or []:
        paras: list[Para] = []
        for cid in b.get("claims") or []:
            cid = str(cid).format(**ctx)
            if cid not in run.claims:
                paras.append(Para("Placeholder — the claim this box needs was not produced by the run.", "withheld_inline"))
                continue
            ex.bound.append(cid)
            if run.claims[cid].released:
                paras.append(Para(_quote(run, cid), "normal"))
                released.append(cid)
            else:
                ex.withheld.append(cid)
                paras.append(Para(f"Placeholder for a withheld claim: {_gap(run, [cid])}.", "withheld_inline"))
        if b.get("question"):
            q = run.question(str(b["question"]))
            if q is None:
                paras.append(Para("Placeholder — question not produced by the run.", "withheld_inline"))
            else:
                basis = list(q.get("basis_claim_ids") or [])
                ex.bound += [c for c in basis if c not in ex.bound]
                if all(c in run.claims and run.claims[c].released for c in basis):
                    paras.append(Para(q["text"], "strong"))
                    released += basis
                else:
                    ex.withheld += [c for c in basis if c in run.claims and not run.claims[c].released]
                    paras.append(Para(f"Placeholder for a question whose basis is withheld: {_gap(run, basis)}.", "withheld_inline"))
        if b.get("offer"):
            paras.append(Para(f"{OFFER_LABEL}: {b['offer']}", "muted"))
        boxes.append((str(b.get("label") or ""), paras))
    if not released:
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(ex.bound)
        return ex
    _guard_title(ex, run, ss, ctx)
    ex.blocks = [Boxes(boxes, columns=2)]
    if ss.bind.get("note"):
        ex.blocks.append(Para(str(ss.bind["note"]), "muted"))
    ex.source_line = source_line(run, list(dict.fromkeys(released)))
    return ex


# ================================================================== questions
def _search_summary(o: dict[str, Any]) -> str:
    se = o.get("search") or {}
    terms = se.get("ai_governance_terms") or []
    hits = sum(int(t.get("hits") or 0) for t in terms)
    broad = [t for t in se.get("broad_governance_terms") or [] if t.get("hits")]
    broad_txt = ", ".join(f"“{t['term']}” {t['hits']} ({t.get('hits_with_ai_term', 0)} with an AI term)" for t in broad)
    return (f"{OBS_LABEL} — search record: {se.get('document', 'the document')}, SHA-256 {str(se.get('sha256') or '')[:12]}…, "
            f"pp. {se.get('pages_searched', '?')}, engine {se.get('extraction_engine', 'not recorded')}; "
            f"{hits} hits for {len(terms)} AI-specific governance terms"
            + (f"; broader terms: {broad_txt}" if broad_txt else "") + ".")


def questions(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]):
    """Questions for management: observations first (as questions, with the search record), then the
    run's questions. A question whose basis is withheld shows the gap id, not its text.

    bind: max (rows), limitations (bool: print the observation's limitations), font_pt."""
    from .exhibits import Exhibit, source_line

    ex = Exhibit()
    if not run.questions and not run.observations:
        ex.requires = list(ss.requires or ["observations and questions from the plumbresearch findings module"])
        return ex
    obs_by_id = {o.get("id"): o for o in run.observations}
    ordered = sorted(run.questions, key=lambda q: 0 if q.get("kind") == "observation" else 1)
    rows: list[list[str]] = []
    released: list[str] = []
    shown = 0
    notes: list[Block] = []
    for i, q in enumerate(ordered[: int(ss.bind.get("max", 8))], 1):
        basis = [c for c in q.get("basis_claim_ids") or [] if c in run.claims]
        ex.bound += [c for c in basis if c not in ex.bound]
        ok = all(run.claims[c].released for c in basis)
        o = obs_by_id.get(q.get("observation_id"))
        label = f"Q{i}" + (" (observation)" if o else "")
        if not ok:
            ex.withheld += [c for c in basis if not run.claims[c].released]
            rows.append([label, _gap(run, basis), "basis withheld — listed in the gap register"])
            continue
        shown += 1
        released += basis
        pages = sorted({run.claims[c].page for c in basis if run.claims[c].page})
        why = ("Quoted: " + ", ".join(f"p. {p}" for p in pages)) if pages else ""
        if q.get("basis_note") and not o:
            why = (why + "; " if why else "") + str(q["basis_note"])
        if o:
            terms = (o.get("search") or {}).get("ai_governance_terms") or []
            hits = sum(int(t.get("hits") or 0) for t in terms)
            # the observation's own evidence (sentences pairing AI with governance language, board references) is bound
            # too: shown by page when released, never required for the question itself
            extra = [c for c in o.get("evidence_claim_ids") or [] if c in run.claims and c not in basis]
            ex.bound += [c for c in extra if c not in ex.bound]
            ex.withheld += [c for c in extra if not run.claims[c].released and c not in ex.withheld]
            xp = sorted({run.claims[c].page for c in extra if run.claims[c].released and run.claims[c].page})
            released += [c for c in extra if run.claims[c].released]
            why = (f"{OBS_LABEL}: {hits} hits for {len(terms)} AI-specific governance terms in "
                   f"{(o.get('search') or {}).get('pages_searched', '?')} pp."
                   + (f"; {why}" if why else "")
                   + (("; board AI references quoted: " + ", ".join(f"p. {p}" for p in xp)) if xp else ""))
            notes.append(Para(_search_summary(o), "muted"))
            if ss.bind.get("limitations", True):
                lims = o.get("limitations_short") or o.get("limitations") or []
                notes.append(Para("Limitations: " + "; ".join(f"({k}) {l}" for k, l in enumerate(lims, 1))
                                  + ". Full search record and limitations: gap register §6.", "muted"))
        rows.append([label, q["text"], why or "—"])
    if not shown:
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(ex.bound)
        return ex
    ex.tokens["n_questions"] = len(rows)
    ex.tokens["n_questions_shown"] = shown
    ex.blocks = [Table(["#", "Question for management", "Why we ask"], rows, widths=[0.95, 5.6, 4.4],
                       font_pt=int(ss.bind.get("font_pt", 10)), rows_per_slide=int(ss.bind.get("rows_per_slide", 8)))] + notes
    _guard_title(ex, run, ss, ctx)
    ex.source_line = source_line(run, list(dict.fromkeys(released)))
    return ex


# ============================================================== rubric detail
COMPONENT_RULES = [
    ("specificity", "AI sentence naming a concrete use case"),
    ("production", "AI sentence with deployment language"),
    ("pilot_only", "pilot / test language without a deployment verb"),
    ("quantified", "AI sentence with a number tied to an outcome"),
    ("ownership", "AI sentence naming board, C-level AI/data title or targets"),
    ("governance", "AI sentence with responsible-AI / model-risk lexicon"),
]


def rubric_detail(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]):
    """The annual-report rubric level with its component counts and what the level can and cannot
    tell the reader. bind: signal_suffix (default .rubric), can [..], cannot [..] (method notes),
    question_components {component: question id} (a component rendered as a question, not a score)."""
    from .exhibits import Exhibit, _signal_has_citable_source, source_line, withheld_text

    sig = run.signal_by_suffix(ss.bind.get("signal_suffix", ".rubric"))
    ex = Exhibit()
    if sig is None:
        ex.requires = ["annual-report rubric signal"]
        return ex
    ev = list(sig.get("evidence_claim_ids") or [])
    ex.bound = ev
    if run.signal_withheld(sig) or not _signal_has_citable_source(sig) or sig.get("value") is None:
        ex.withheld = [c for c in ev if c in run.claims and not run.claims[c].released]
        ex.all_withheld = True
        ex.extra_signal_gaps = run.gap_ids(ev)
        return ex
    d = sig.get("detail") or {}
    ex.tokens["rubric_level"] = sig.get("value")
    qcomp = {k: str(v) for k, v in (ss.bind.get("question_components") or {}).items()}
    rows = []
    for comp, rule in COMPONENT_RULES:
        v = d.get(comp)
        if comp in qcomp:
            q = run.question(qcomp[comp])
            qi = next((i for i, x in enumerate(sorted(run.questions, key=lambda x: 0 if x.get("kind") == "observation" else 1), 1)
                       if q is not None and x.get("id") == q.get("id")), None)
            note = f"lexicon hits {v}: not a score; asked as Q{qi} on the questions slide" if qi else f"lexicon hits {v}: not a score"
            rows.append([comp, rule, "see note", note])
        else:
            rows.append([comp, rule, "—" if v is None else str(v), ""])
    rows.append(["mentions", "AI-term mentions per 1,000 words", f"{d.get('density_per_1000', '—')}", f"{d.get('mentions', '—')} mentions"])
    rule = str(d.get("rule") or "")
    can = list(ss.bind.get("can") or [])
    cannot = list(ss.bind.get("cannot") or [])
    left: list[Block] = [Table(["Component", "Rule (exact)", "Count", "Note"], rows, widths=[1.1, 2.9, 0.6, 2.4], font_pt=9),
                         Para(f"Level rule met: {rule}.", "muted")]
    right: list[Block] = []
    if can:
        right += [Para("What the level can tell you (method note)", "strong"), Bullets(can)]
    if cannot:
        right += [Para("What it cannot tell you (method note)", "strong"), Bullets(cannot)]
    ex.blocks = [Columns(left=left, right=right, ratio=0.62)] if right else left
    _guard_title(ex, run, ss, ctx)
    ex.source_line = source_line(run, [], signal_refs=[sig])
    return ex


# ====================================================================== offer
def offer(ss: SlideSpec, run: RunData, il: Interlock, ctx: dict, sc: Optional[dict]):
    """Static offer text (allowed only on kind: offer slides). bind: columns [{heading, items}], source, note."""
    from .exhibits import Exhibit

    cols = ss.bind.get("columns") or []
    blocks: list[Block] = [Para(f"{OFFER_LABEL}. " + str(ss.bind.get("lead") or "What a PLUMB assessment would establish."), "strong")]
    parts: list[list[Block]] = []
    for c in cols:
        parts.append([Para(str(c.get("heading") or ""), "strong"), Bullets([str(x) for x in c.get("items") or []])])
    if len(parts) == 2:
        blocks.append(Columns(left=parts[0], right=parts[1], ratio=0.5))
    else:
        for p in parts:
            blocks += p
    if ss.bind.get("note"):
        blocks.append(Para(str(ss.bind["note"]), "muted"))
    if ss.bind.get("source"):
        blocks.append(Para(f"Offer source: {ss.bind['source']}", "muted"))
    return Exhibit(blocks=blocks)
