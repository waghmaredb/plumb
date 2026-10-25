"""Resolve an executive storyline against a verified run.

Face text is authored, but nothing renders unless the evidence it rests on was
released by plumbverify. This step:
  * refuses the build if any supporting claim id is missing or withheld;
  * attaches page references (from the claim, or an override checked against the PDF);
  * scores every synthesis sentence against its supporting passages with the
    offline C4 matcher and flags all of them for the independent reviewer
    (offline C4 is below its 2% false-support target);
  * computes the board-use interlock and turns it into client-appropriate wording;
  * writes resolved.json (for the renderer) and qa-sheet.md (internal, never shipped).

Usage: python resolve_storyline.py STORYLINE.json --run RUN_DIR --out OUT_DIR [--pdf SOURCE.pdf] [--signoff YAML]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # plumbdeck package

from plumbdeck.interlock import compute_interlock  # noqa: E402
from plumbdeck.runio import RunData  # noqa: E402

try:
    from plumbverify.semantic import contradiction_rules, key_term_recall
except Exception:  # pragma: no cover
    contradiction_rules = key_term_recall = None

FACT_KINDS = {"synthesis", "quote"}
NON_FINDING_KINDS = {"question", "hypothesis", "offer", "method", "label", "observation"}


class StorylineError(Exception):
    pass


def load_claims(run_dir: Path) -> tuple[dict, dict]:
    claims = json.loads((run_dir / "claims.json").read_text())
    claims = claims if isinstance(claims, list) else claims["claims"]
    report = json.loads((run_dir / "report.json").read_text())
    decisions = {d["claim_id"]: d for d in report["verification"]["decisions"]}
    return {c["id"]: c for c in claims}, decisions


def page_text(pdf: Path, page: int) -> str:
    out = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    return " ".join(out.split())


def walk(node, path=""):
    """Yield (path, dict) for every text element (dict with 'kind' and 'text')."""
    if isinstance(node, dict):
        if "kind" in node and "text" in node:
            yield path, node
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


def items_with_support(node, path=""):
    """Value-chain items etc. carry 'support' without 'kind'."""
    if isinstance(node, dict):
        if "support" in node and "kind" not in node and "text" in node:
            yield path, node
        for k, v in node.items():
            yield from items_with_support(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from items_with_support(v, f"{path}[{i}]")


def shown_matches(display: str, value: float) -> bool:
    """A displayed number matches if it is the value rounded to the precision shown."""
    num = re.sub(r"[^\d.]", "", display.replace(",", ""))
    if not num:
        return False
    dec = len(num.split(".")[1]) if "." in num else 0
    return abs(float(num) - value) <= 0.5 * 10 ** (-dec) + 1e-9


def resolve(story: dict, run_dir: Path, pdf: Path | None, signoff: Path | None) -> tuple[dict, list[dict], dict]:
    claims, decisions = load_claims(run_dir)
    qa_rows: list[dict] = []
    errors: list[str] = []

    def pages_for(ids: list[str], override: list[int] | None, text: str) -> list[int]:
        pages: set[int] = set()
        for cid in ids:
            c = claims.get(cid)
            p = (c or {}).get("page") or ((c or {}).get("attrs") or {}).get("page_expected")
            if p:
                pages.add(int(p))
        if override:
            for p in override:
                if pdf:
                    # the supporting claim's text must be on the override page
                    hay = page_text(pdf, p)
                    ok = any(" ".join(claims[cid]["text"].split())[:60] in hay for cid in ids if cid in claims)
                    if not ok:
                        errors.append(f"page override p.{p} not confirmed in PDF for: {text[:60]}")
                pages.add(int(p))
        return sorted(pages)

    def check(path: str, el: dict, kind: str):
        ids = el.get("support", []) or []
        for cid in ids:
            d = decisions.get(cid)
            if cid not in claims or d is None:
                errors.append(f"{path}: support id not in run: {cid}")
            elif d.get("blocked") or d.get("status") == "blocked":
                errors.append(f"{path}: support id is WITHHELD and cannot back face text: {cid}")
        if kind in FACT_KINDS and not ids:
            errors.append(f"{path}: {kind} text has no supporting claim: {el['text'][:70]}")
        pages = pages_for(ids, el.get("pages"), el["text"])
        el["_pages"] = pages
        row = {"path": path, "kind": kind, "text": el["text"], "support": ids, "pages": pages,
               "reviewer_check": kind in ("synthesis", "observation") or bool(el.get("observation"))}
        if kind == "synthesis" and ids and contradiction_rules:
            passage = " ".join(claims[c]["text"] for c in ids if c in claims)
            rec, missing = key_term_recall(el["text"], passage)
            hits = contradiction_rules(el["text"], passage)
            row["c4_offline_recall"] = round(rec, 3)
            row["c4_missing_terms"] = missing[:8]
            row["c4_rules"] = [str(h) for h in hits]
        qa_rows.append(row)

    for path, el in walk(story["slides"]):
        if el["kind"] == "derived":
            continue  # checked against its verified figure below
        check(path, el, el["kind"])
    for path, el in items_with_support(story["slides"]):
        check(path, el, "synthesis")
    # matrix cells carry support without text: check release and collect pages
    for si, s in enumerate(story["slides"]):
        for ri, r in enumerate(s.get("rows", []) or []):
            if not isinstance(r, dict):
                continue
            for ci, c in enumerate(r.get("cells", []) or []):
                for cid in c.get("support", []) or []:
                    d = decisions.get(cid)
                    if cid not in claims or d is None or d.get("blocked") or d.get("status") == "blocked":
                        errors.append(f"[{si}].rows[{ri}].cells[{ci}]: support {cid} missing or withheld")
                c["_pages"] = pages_for(c.get("support", []) or [], None, r.get("label", ""))
                if c.get("support"):
                    qa_rows.append({"path": f"[{si}].rows[{ri}]", "kind": "synthesis", "text": f"{r['label']}: {c['state']}",
                                    "support": c["support"], "pages": c["_pages"], "reviewer_check": True})

    # ---- table figures: re-extracted from the hashed source, label and value on one printed row ----
    report = json.loads((run_dir / "report.json").read_text())
    att = {a["sha256"] for a in report.get("attached_documents", [])}
    figures: dict[str, dict] = {}
    for si, s in enumerate(story["slides"]):
        for f in s.get("figures", []):
            if not pdf:
                errors.append(f"slide {s['id']}: figure {f['id']} needs --pdf to verify")
                continue
            sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
            if sha not in att:
                errors.append(f"figure {f['id']}: --pdf hash {sha[:12]} is not the run's attached document")
                continue
            lay = subprocess.run(["pdftotext", "-f", str(f["pdf_page"]), "-l", str(f["pdf_page"]), "-layout", str(pdf), "-"],
                                 capture_output=True, text=True, check=True).stdout
            row = next((ln for ln in lay.splitlines() if re.search(rf"^\s*{re.escape(f['row'])}\b", ln)), None)
            if not row or not re.search(rf"(?<![\d,.]){re.escape(f['value'])}(?![\d])", row):
                errors.append(f"figure {f['id']}: row '{f['row']}' with value {f['value']} not found on PDF page {f['pdf_page']}")
                continue
            f["_num"] = float(f["value"].replace(",", ""))
            f["_pages"] = [f["pdf_page"]]
            f["_row"] = " ".join(row.split())
            figures[f["id"]] = f
            qa_rows.append({"path": f"[{si}].figures.{f['id']}", "kind": "figure", "text": f"{f['label']}: {f['value']} ({story.get('unit', s.get('unit',''))})",
                            "support": [f"pdf p.{f['pdf_page']} row: {f['_row'][:70]}"], "pages": [f["pdf_page"]], "reviewer_check": True})
    # tiles/bigs that cite a figure must display it correctly
    for s in story["slides"]:
        for tl in s.get("tiles", []):
            ids = tl.get("figures") or ([tl["figure"]] if "figure" in tl else [])
            if ids:
                fs = [figures.get(x) for x in ids]
                if not all(fs):
                    errors.append(f"tile '{tl['big']}': figure(s) {ids} not verified")
                else:
                    total = sum(f["_num"] for f in fs)
                    exp = total / 1000 if "bn" in tl["big"] else total
                    if not shown_matches(tl["big"], exp):
                        errors.append(f"tile '{tl['big']}' does not match verified {' + '.join(f['value'] for f in fs)} (= {exp:.1f})")
                    tl["_pages"] = sorted({p for f in fs for p in f["_pages"]})
                    qa_rows.append({"path": f"{s['id']}.tile", "kind": "derived", "text": f"{tl['big']} {tl.get('line', {}).get('text', '')}",
                                    "support": [" + ".join(f["value"] for f in fs) + f" = {total:.1f}"], "pages": tl["_pages"], "reviewer_check": True})
        # derived arithmetic in titles
        for path, el in walk(s):
            if el["kind"] == "derived":
                d = el["derived"]
                ids = d.get("sum") or [d["figure"]]
                fs = [figures.get(x) for x in ids]
                if not all(fs):
                    errors.append(f"derived '{el['text'][:50]}': figure(s) {ids} not verified"); continue
                pct = d.get("pct", 100)
                base = sum(f["_num"] for f in fs)
                val = base * pct / 100
                expr = (" + ".join(f["value"] for f in fs)) + (f" × {pct}%" if pct != 100 else "")
                if d.get("approx"):
                    shown = float(re.sub(r"[^\d.]", "", d["display"]))
                    ok = abs(shown - val) / val <= 0.05
                else:
                    ok = shown_matches(d["display"], val)
                if not ok:
                    errors.append(f"derived '{d['display']}' does not equal {expr} (= {val:.1f})")
                if d["display"] not in el["text"]:
                    errors.append(f"derived display {d['display']} not in title text")
                el["_pages"] = sorted({p for f in fs for p in f["_pages"]})
                qa_rows.append({"path": s["id"] + "." + path, "kind": "derived", "text": el["text"], "support": [f"{expr} = {val:.1f}"],
                                "pages": el["_pages"], "reviewer_check": True})

    # ---- pending slides: built, never final until their sources are fetched and verified ----
    pending = [s["id"] for s in story["slides"] if s.get("pending_sources")]
    for s in story["slides"]:
        if s.get("pending_sources"):
            s["_pending"] = True

    # ---- word budget on the face ----
    wb = story.get("word_budget") or {}
    def words(x: str) -> int:
        return len(re.sub(r"\[\[FOUNDER: [^\]]+\]\]", "X", x).split())
    for s in story["slides"]:
        if s["layout"] == "cover":
            continue
        t = s.get("title", {}).get("text", "")
        if wb.get("title") and words(t) > wb["title"]:
            errors.append(f"slide {s['id']}: title has {words(t)} words (budget {wb['title']})")
        body = [el["text"] for path, el in walk({k: v for k, v in s.items() if k not in ("title",)})]
        body += [it["text"] for _, it in items_with_support({k: v for k, v in s.items() if k != "title"})]
        for k in ("cards", "lines", "milestones", "outputs", "lanes", "rows", "stages", "tiles"):
            for x in s.get(k, []) or []:
                if isinstance(x, str):
                    body.append(x); continue
                for fld in ("text", "what", "name", "label", "head", "big"):
                    if isinstance(x.get(fld), str):
                        body.append(x[fld])
        n = sum(words(b) for b in set(body))
        s["_words"] = n
        if wb.get("body") and n > wb["body"] * (1.6 if s["layout"] in ("lifecycle", "disclosure_matrix", "plan") else 1):
            errors.append(f"slide {s['id']}: {n} words on the face (budget {wb['body']}); move text to the report")

    if errors:
        raise StorylineError("Storyline refused:\n  " + "\n  ".join(errors))

    # per-slide source footnote, in the document's PRINTED page numbers (what a reader of the
    # printed report sees), not PDF page indices (CXO review 2026-10-26)
    offset = int(story.get("printed_page_offset", 0))

    def printed(p: int) -> int:
        q = p + offset
        if pdf and offset:
            txt = page_text(pdf, p)
            if not re.search(rf"(?<!\d){q}(?!\d)", txt):
                errors.append(f"printed folio {q} not found on PDF page {p}; check printed_page_offset")
        return q

    for s in story["slides"]:
        pages = sorted({p for _, el in walk(s) for p in el.get("_pages", [])}
                       | {p for _, el in items_with_support(s) for p in el.get("_pages", [])}
                       | {p for f in s.get("figures", []) for p in f.get("_pages", [])}
                       | {p for tl in s.get("tiles", []) for p in tl.get("_pages", [])}
                       | {p for r in s.get("rows", []) or [] if isinstance(r, dict) for c in r.get("cells", []) or [] for p in c.get("_pages", [])})
        if pages:
            pp = sorted({printed(p) for p in pages})
            lab = "p." if len(pp) == 1 else "pp."
            s["_source"] = f"Source: {story['source_doc']}, {lab} {', '.join(str(p) for p in pp)}"
    if errors:
        raise StorylineError("Storyline refused:\n  " + "\n  ".join(errors))

    # founder inputs: visible "to confirm" fields; a deck containing any cannot be final
    founder = sorted(set(re.findall(r"\[\[FOUNDER: ([^\]]+)\]\]", json.dumps(story["slides"], ensure_ascii=False))))

    run = RunData(run_dir)
    lock = compute_interlock(run, signoff)
    final = lock.passed and not founder and not pending
    # the client sees one quiet footer mark while the deck is a draft; the reasons live in the QA sheet
    story["_status"] = {"final": final, "marker": None if final else "Discussion draft",
                        "founder_inputs": founder, "interlock_reasons": lock.reasons, "pending_slides": pending}
    return story, qa_rows, lock.to_dict()


def write_qa(out: Path, story: dict, rows: list[dict], lock: dict) -> None:
    L = [f"# Internal QA sheet — {story['deck_id']} v{story['version']}",
         "",
         "INTERNAL — never sent to the client. The client deck carries only page footnotes and the status line.",
         "",
         f"Interlock: {'PASSED' if lock['passed'] else 'NOT PASSED'} — " + ("; ".join(lock["reasons"]) or "all conditions met"),
         f"Founder inputs outstanding: {', '.join(story['_status']['founder_inputs']) or 'none'}",
         f"Pending slides (sources not yet fetched): {', '.join(story['_status'].get('pending_slides') or []) or 'none'}",
         f"Run outcome: {lock['outcome']}",
         "",
         "## Reviewer must-check list",
         "Every synthesis and observation sentence below is authored, not quoted. Offline C4 is below its 2% "
         "false-support target, so each one is on the mandatory check list, not the random sample. Check the "
         "sentence against the cited passages on the cited pages; tick only if fully entailed with no dropped qualifier.",
         "",
         "| # | Where | Kind | Face text | Support | Pages | C4 recall | C4 rules | Reviewer ✓ |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        if not r["reviewer_check"] and r["kind"] not in ("quote",):
            continue
        L.append(f"| {i} | {r['path']} | {r['kind']} | {r['text'].replace('|','/')} | {', '.join(x.split('.')[-1] if re.match(r'^[a-z0-9-]+\.', x) and ' ' not in x else x for x in r['support'])} | "
                 f"{', '.join(map(str, r['pages']))} | {r.get('c4_offline_recall','')} | {'; '.join(r.get('c4_rules', [])) or '—'} | ☐ |")
    L += ["", "## Not findings (questions, offers, method, labels)", ""]
    for r in rows:
        if r["kind"] in NON_FINDING_KINDS and not r.get("reviewer_check"):
            L.append(f"- **{r['kind']}** — {r['text']}")
    (out / "qa-sheet.md").write_text("\n".join(L) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("storyline", type=Path)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--signoff", type=Path)
    a = ap.parse_args(argv)
    story = json.loads(a.storyline.read_text())
    try:
        story, rows, lock = resolve(story, a.run, a.pdf, a.signoff)
    except StorylineError as e:
        print(e, file=sys.stderr)
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "resolved.json").write_text(json.dumps(story, indent=1, ensure_ascii=False))
    write_qa(a.out, story, rows, lock)
    flagged = [r for r in rows if r.get("c4_rules")]
    print(f"resolved {len(story['slides'])} slides; {len(rows)} text elements; "
          f"{sum(r['reviewer_check'] for r in rows)} on reviewer must-check list; "
          f"{len(flagged)} with C4 rule hits; status: {story['_status']['marker'] or 'FINAL'}; founder inputs: {len(story['_status']['founder_inputs'])}")
    for r in flagged:
        print(f"  C4 rule hit: {r['path']}: {r['c4_rules']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
