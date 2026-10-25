"""Report spec: load the YAML and bind every block to the run, storyline and research.

The binding rule (the reason this module exists):

* Any quotation or fact printed in the report body comes from a statement whose
  verification decision is ``verified``. Binding a blocked or undecided statement
  anywhere else raises :class:`BindingError` and the build stops.
* Blocked statements and research rows (located at the publisher, not yet checked
  against a stored copy) may be bound only inside a section of ``kind: awaiting``,
  which renders as "Developments since the annual report - awaiting source check".
  Under ``strict`` that section is dropped before binding, so nothing from it is
  printed and its documents are not listed in the sources appendix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .data import Claim, InputError, Research, Run, Storyline
from .pages import Folio


class BindingError(Exception):
    """The spec asks for something the evidence does not allow."""


@dataclass
class Document:
    key: str
    title: str
    short: str
    publisher: str
    published: str
    url: str
    folio: Folio
    page_overrides: dict[str, int]
    note: str = ""
    used_pdf_pages: set[int] = field(default_factory=set)


@dataclass
class AwaitingSource:
    label: str
    url: str
    date: str


@dataclass
class Context:
    run: Run
    storyline: Storyline
    research: Research | None
    documents: dict[str, Document]
    strict: bool
    awaiting: bool = False
    section_id: str = ""
    notes: list[str] | None = None            # footnote texts for the current section
    quotes: list[dict] = field(default_factory=list)       # for word-for-word re-check
    awaiting_sources: list[AwaitingSource] = field(default_factory=list)
    accounted: set[str] = field(default_factory=set)       # non-verified ids accounted for
    bound: set[str] = field(default_factory=set)


# ----------------------------------------------------------------------- helpers

def load_spec(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise InputError(f"missing spec: {p}")
    spec = yaml.safe_load(p.read_text(encoding="utf-8"))
    for k in ("report", "documents", "sections"):
        if k not in spec:
            raise InputError(f"{p}: spec needs a top-level {k!r}")
    return spec


def _norm(s: str) -> str:
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"')
         .replace("”", '"').replace(" ", " "))
    return re.sub(r"\s+", " ", s).strip()


def use_claim(ctx: Context, cid: str, where: str) -> Claim:
    """Every claim reference goes through here: the verified-only rule."""
    c = ctx.run.claim(cid)
    if not c.verified and not ctx.awaiting:
        raise BindingError(
            f"[{ctx.section_id}] {where}: statement {cid} has status '{c.status}' "
            f"({'; '.join(c.reasons) or 'no reason recorded'}). Only verified statements may be "
            f"printed; unverified items belong in the 'awaiting source check' section."
        )
    ctx.bound.add(cid)
    if not c.verified:
        ctx.accounted.add(cid)
    return c


def doc_for(ctx: Context, c: Claim) -> Document:
    for d in ctx.documents.values():
        if d.url in c.sources:
            return d
    raise BindingError(f"[{ctx.section_id}] statement {c.id}: none of its sources is a document "
                       f"declared in the spec ({', '.join(c.sources)})")


def pdf_page(ctx: Context, c: Claim, doc: Document) -> int:
    p = c.pdf_page or doc.page_overrides.get(c.id)
    if not p:
        raise BindingError(f"[{ctx.section_id}] statement {c.id} has no page; add it under "
                           f"documents.{doc.key}.pages in the spec")
    return int(p)


def cite(ctx: Context, cids: list[str], where: str) -> dict:
    """Pages for a set of supporting statements, grouped by document."""
    by_doc: dict[str, set[int]] = {}
    for cid in cids:
        c = use_claim(ctx, cid, where)
        d = doc_for(ctx, c)
        p = pdf_page(ctx, c, d)
        d.used_pdf_pages.add(p)
        by_doc.setdefault(d.key, set()).add(p)
    parts = [f"{ctx.documents[k].short}, {ctx.documents[k].folio.labels(v)}" for k, v in by_doc.items()]
    return {"text": "; ".join(parts), "pages": {k: sorted(v) for k, v in by_doc.items()}}


def _support_of(node: Any) -> list[str]:
    return list(node.get("support", [])) if isinstance(node, dict) else []


def _text_of(node: Any) -> str:
    return node.get("text", "") if isinstance(node, dict) else str(node)


def _citation(ctx: Context, cids: list[str], where: str) -> dict | None:
    """Return {'note': n} (footnote mode) or {'inline': text}."""
    if not cids:
        return None
    c = cite(ctx, cids, where)
    if ctx.notes is not None:
        ctx.notes.append(c["text"] + ".")
        return {"note": len(ctx.notes)}
    return {"inline": c["text"]}


# ------------------------------------------------------------------------ blocks

def _text_block(ctx, b, where):
    if "storyline" in b:
        node = ctx.storyline.get(b["storyline"])
        text, support = _text_of(node), _support_of(node)
    else:
        text, support = b["text"], list(b.get("support", []))
    return {"type": b["type"], "text": text, "cite": _citation(ctx, support, where)}


def _message(ctx, b, where):
    node = ctx.storyline.get(b["storyline"])          # a point: {head, body}
    head, body = node["head"], node["body"]
    support = list(dict.fromkeys(_support_of(head) + _support_of(body)))
    return {"type": "message", "head": _text_of(head), "text": _text_of(body),
            "cite": _citation(ctx, support, where)}


def _quote(ctx, b, where):
    cids = b["claims"] if "claims" in b else [b["claim"]]
    claims = [use_claim(ctx, cid, where) for cid in cids]
    docs = {doc_for(ctx, c).key for c in claims}
    if len(docs) != 1:
        raise BindingError(f"[{ctx.section_id}] {where}: a pull quote must come from one document")
    doc = ctx.documents[docs.pop()]
    pages = {pdf_page(ctx, c, doc) for c in claims}
    if len(pages) != 1:
        raise BindingError(f"[{ctx.section_id}] {where}: joined sentences must be on one page")
    page = pages.pop()
    doc.used_pdf_pages.add(page)
    full = " ".join(c.text for c in claims)
    shown = full
    if b.get("excerpt"):
        frags = b["excerpt"]
        pos = 0
        for f in frags:
            i = _norm(full).find(_norm(f), pos)
            if i < 0:
                raise BindingError(f"[{ctx.section_id}] {where}: excerpt fragment not in the quotation, "
                                   f"or out of order: {f[:60]!r}")
            pos = i + len(_norm(f))
        shown = " … ".join(f.strip() for f in frags)
    ctx.quotes.append({"doc": doc.key, "pdf_page": page, "text": full, "where": where})
    return {"type": "quote", "label": b.get("label", ""), "text": shown,
            "source": f"{doc.short}, {doc.folio.label(page)}"}


def _uses_table(ctx, b, where):
    rows = []
    for i, r in enumerate(b["rows"]):
        c = use_claim(ctx, r["claim"], f"{where} row {i + 1}")
        doc = doc_for(ctx, c)
        page = pdf_page(ctx, c, doc)
        doc.used_pdf_pages.add(page)
        word = r.get("match", r["status"]).lower()
        if word not in c.text.lower():
            raise BindingError(f"[{ctx.section_id}] {where} row {i + 1}: status '{r['status']}' must use "
                               f"the company's own wording; '{word}' is not in the quotation")
        rows.append({"stage": r["stage"], "use": r["use"], "status": r["status"],
                     "market": r.get("market", ""), "page": doc.folio.label(page).replace("p. ", "")})
    return {"type": "uses_table", "caption": b.get("caption", ""), "rows": rows,
            "head": b.get("head", ["Stage", "Use", "Status", "Market", "Page"]),
            "note": b.get("note", "")}


def _figures(ctx, b, where):
    items = []
    for i, f in enumerate(b["items"]):
        c = use_claim(ctx, f["claim"], f"{where} figure {i + 1}")
        if f["figure"] not in c.text:
            raise BindingError(f"[{ctx.section_id}] {where} figure {i + 1}: '{f['figure']}' is not in "
                               f"the quotation it cites")
        doc = doc_for(ctx, c)
        page = pdf_page(ctx, c, doc)
        doc.used_pdf_pages.add(page)
        items.append({**{k: f.get(k, "") for k in ("value", "tag", "label", "detail", "tone")},
                      "source": f"{doc.short}, {doc.folio.label(page)}"})
    return {"type": "figures", "items": items}


def _table(ctx, b, where):
    support = list(b.get("support", []))
    c = _citation(ctx, support, where) if support else None
    return {"type": "table", "head": b["head"], "rows": b["rows"], "caption": b.get("caption", ""),
            "cite": c, "widths": b.get("widths")}


def _search_method(ctx, b, where):
    o = ctx.run.observations.get(b["observation"])
    if not o:
        raise BindingError(f"[{ctx.section_id}] {where}: no search record {b['observation']!r} in the run")
    s = o["search"]
    terms = [t["term"] for t in s["ai_governance_terms"]]
    hits = sum(int(t.get("hits", 0)) for t in s["ai_governance_terms"])
    doc = ctx.documents[b["document"]]
    if s.get("document_url") and s["document_url"] != doc.url:
        raise BindingError(f"[{ctx.section_id}] {where}: search record is for another document")
    pages = s.get("pages_searched", "").replace("–", "–")
    return {"type": "search_method", "head": b.get("head", "How we searched"), "terms": terms,
            "n_terms": len(terms), "hits": hits, "pages": pages, "document": doc.short,
            "result": b["result"].format(n=len(terms), hits=hits, pages=pages, document=doc.short),
            "scope": b.get("scope", "").format(n=len(terms), pages=pages, document=doc.short),
            "limitations": b["limitations"]}


def _hypotheses(ctx, b, where):
    node = ctx.storyline.get(b["storyline"])
    rows = []
    for i, r in enumerate(node["rows"]):
        c = cite(ctx, r.get("support", []), f"{where} row {i + 1}")
        rows.append({"topic": r["topic"], "text": r["text"], "how": r["how"], "basis": c["text"]})
    return {"type": "hypotheses", "head": b.get("head") or node.get("col_heads"), "rows": rows}


def _questions(ctx, b, where):
    items = []
    for qid in b["items"]:
        q = ctx.run.questions.get(qid)
        if not q:
            raise BindingError(f"[{ctx.section_id}] {where}: no question {qid!r} in the run")
        c = cite(ctx, q.get("basis_claim_ids", []), f"{where} {qid}")
        items.append({"text": q["text"], "basis": c["text"]})
    return {"type": "questions", "head": b.get("head", ""), "items": items}


def _phases(ctx, b, where):
    node = ctx.storyline.get(b["storyline"])
    return {"type": "phases", "head": b.get("head", ""), "intro": b.get("intro", ""),
            "columns": node.get("columns", []), "phases": node.get("phases", [])}


def _awaiting(ctx, b, where):
    if not ctx.awaiting:
        raise BindingError(f"[{ctx.section_id}] {where}: 'awaiting' items may appear only in the "
                           f"awaiting-source-check section")
    items = []
    for i, it in enumerate(b["items"]):
        w = f"{where} item {i + 1}"
        urls: list[str] = []
        if "claim" in it:
            c = use_claim(ctx, it["claim"], w)
            urls = list(c.sources)
        for rid in ([it["research"]] if isinstance(it.get("research"), str) else it.get("research", [])):
            if ctx.research is None:
                raise BindingError(f"[{ctx.section_id}] {w}: research row {rid} bound but no --research given")
            urls += ctx.research.row(rid).urls
        url = it.get("url") or (urls[0] if urls else "")
        if it.get("url"):
            known = (ctx.research.text if ctx.research else "") + " ".join(urls)
            if it["url"] not in known:
                raise BindingError(f"[{ctx.section_id}] {w}: url is not traceable to the research notes "
                                   f"or the statement's sources: {it['url']}")
        if not url:
            raise BindingError(f"[{ctx.section_id}] {w}: every item needs a source address")
        if not it.get("source_type"):
            raise BindingError(f"[{ctx.section_id}] {w}: every item needs a source_type")
        ctx.awaiting_sources.append(AwaitingSource(it.get("source_label", it["source_type"]), url,
                                                   it.get("date", "")))
        items.append({"text": it["text"], "source_type": it["source_type"], "date": it.get("date", ""),
                      "url": url, "status": it.get("status", "To be confirmed")})
    return {"type": "awaiting", "head": b.get("head", ""), "intro": b.get("intro", ""), "items": items}


def _open_items(ctx, b, where):
    for cid in b.get("accounts_for", []):
        ctx.run.claim(cid)          # must exist; content is not printed
        ctx.accounted.add(cid)
    items = []
    for it in b["items"]:
        for cid in it.get("accounts_for", []):
            ctx.run.claim(cid)
            ctx.accounted.add(cid)
        items.append({"head": it["head"], "text": it["text"], "next": it.get("next", "")})
    return {"type": "open_items", "items": items}


def _plain(ctx, b, where):
    return {k: v for k, v in b.items()}


BLOCKS = {
    "lead": _text_block, "para": _text_block, "message": _message, "quote": _quote,
    "uses_table": _uses_table, "figures": _figures, "table": _table,
    "search_method": _search_method, "hypotheses": _hypotheses, "questions": _questions,
    "phases": _phases, "awaiting": _awaiting, "open_items": _open_items,
    "subhead": _plain, "note": _plain, "observations": _plain, "callout": _plain,
    "method": _plain, "sources": _plain,
}


# -------------------------------------------------------------------------- bind

def bind(spec: dict, run: Run, storyline: Storyline, research: Research | None, *, strict: bool) -> dict:
    documents = {}
    for key, d in spec["documents"].items():
        f = d.get("folio") or {}
        documents[key] = Document(
            key=key, title=d["title"], short=d["short"], publisher=d.get("publisher", ""),
            published=d.get("published", ""), url=d["url"], note=d.get("note", ""),
            folio=Folio(offset=int(f.get("offset", 0)), first_pdf=int(f.get("first_pdf", 1)),
                        last_pdf=int(f.get("last_pdf", 10 ** 6))),
            page_overrides={k: int(v) for k, v in (d.get("pages") or {}).items()},
        )
    ctx = Context(run=run, storyline=storyline, research=research, documents=documents, strict=strict)

    sections = []
    number = 0
    for s in spec["sections"]:
        kind = s.get("kind", "body")
        if kind == "awaiting" and strict:
            continue
        ctx.awaiting = kind == "awaiting"
        ctx.section_id = s["id"]
        ctx.notes = [] if s.get("citations") == "notes" else None
        if kind in ("body", "awaiting"):
            number += 1
            label = str(number)
        else:
            label = s.get("letter", "")
        blocks = []
        for i, b in enumerate(s.get("blocks", [])):
            fn = BLOCKS.get(b.get("type"))
            if fn is None:
                raise InputError(f"[{s['id']}] block {i + 1}: unknown type {b.get('type')!r}")
            blocks.append(fn(ctx, b, f"block {i + 1} ({b['type']})"))
        for n, mb in enumerate((x for x in blocks if x["type"] == "message"), 1):
            mb["n"] = n
        sections.append({"id": s["id"], "kind": kind, "label": label, "title": s["title"],
                         "kicker": s.get("kicker", ""), "blocks": blocks, "notes": ctx.notes or [],
                         "page_break": s.get("page_break", True)})
    ctx.awaiting = False

    # Appendix A data
    sources_main = []
    for d in documents.values():
        if not d.used_pdf_pages:
            continue
        sources_main.append({"title": d.title, "publisher": d.publisher, "published": d.published,
                             "url": d.url, "note": d.note, "pages": d.folio.labels(d.used_pdf_pages)})
    seen, sources_awaiting = set(), []
    for a in ctx.awaiting_sources:
        if a.url in seen:
            continue
        seen.add(a.url)
        sources_awaiting.append({"label": a.label, "url": a.url, "date": a.date})

    not_verified = sorted(cid for cid, c in run.claims.items() if not c.verified)
    status = storyline.marker
    r = spec["report"]
    return {
        "report": {**r, "status": status, "final": storyline.final, "strict": strict},
        "sections": sections,
        "sources_main": sources_main,
        "sources_awaiting": sources_awaiting,
        "quotes": ctx.quotes,
        "binding": {
            "verified_bound": sorted(c for c in ctx.bound if run.claims[c].verified),
            "not_verified_in_awaiting": sorted(c for c in ctx.bound if not run.claims[c].verified),
            "not_verified_in_run": not_verified,
            "not_verified_unaccounted": sorted(set(not_verified) - ctx.accounted),
        },
    }
