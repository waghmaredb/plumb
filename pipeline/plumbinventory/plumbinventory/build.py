"""plumbinventory — outside-in candidate AI inventory with mechanical source checks.

Reads a candidates.yaml and the stored, hashed text of the primary source (from a plumbresearch run's
report.json), then checks every quotation and figure against the stated PDF page:

  quote   → must appear on that page after whitespace/hyphen/quote-mark normalisation (exact otherwise)
  figure  → the figure string must appear on that page (row attribution is an analyst read, labelled so)

Any failure stops the build (block, not flag). The output inventory.json carries, for every check, the
page, the printed page, the source hash and the matched passage, so a page can show the reader exactly
what was matched.

Usage: python -m plumbinventory.build <candidates.yaml> --out <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})


def norm(s: str) -> str:
    """Normalise for matching: unify quote marks/dashes, rejoin 'AI- powered' style breaks, collapse space."""
    s = s.translate(QUOTE_MAP)
    s = re.sub(r"(\w)-\s+(\w)", r"\1-\2", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def load_pages(run_dir: Path, url: str) -> tuple[list[str], str]:
    report = json.loads((run_dir / "report.json").read_text())
    for src in report["verification"]["sources"]:
        if src["url"] == url:
            return src["text_extract"].split("\f"), src["sha256"]
    raise SystemExit(f"primary source {url} not in {run_dir}/report.json")


def context_window(page_norm: str, needle_norm: str, before: int = 220, after: int = 220) -> dict:
    i = page_norm.find(needle_norm)
    return {
        "before": page_norm[max(0, i - before):i],
        "match": page_norm[i:i + len(needle_norm)],
        "after": page_norm[i + len(needle_norm):i + len(needle_norm) + after],
    }


def check_quote(pages: list[str], pdf_page: int, quote: str) -> dict:
    page_norm = norm(pages[pdf_page - 1])
    q = norm(quote)
    if q in page_norm:
        return {"ok": True, "method": "string-match", **context_window(page_norm, q)}
    other = [i + 1 for i, p in enumerate(pages) if q in norm(p)]
    return {"ok": False, "method": "string-match", "found_on": other}


def check_figure(pages: list[str], pdf_page: int, value: str) -> dict:
    page_norm = norm(pages[pdf_page - 1])
    # match the figure as a whole token, so "5.9" does not match inside "15.9"
    pat = re.compile(r"(?<![\d.,])" + re.escape(value) + r"(?![\d])")
    m = pat.search(page_norm)
    if not m:
        return {"ok": False, "method": "figure-on-page"}
    return {"ok": True, "method": "figure-on-page", "row_attribution": "analyst read",
            "before": page_norm[max(0, m.start() - 160):m.start()], "match": m.group(0),
            "after": page_norm[m.end():m.end() + 160]}


def build(candidates_path: Path, out_dir: Path, profile: str = "internal") -> dict:
    spec = yaml.safe_load(candidates_path.read_text())
    root = candidates_path.resolve().parents[3]  # repo root: runs/<subject>/<run>/candidates.yaml
    prim = spec["primary_source"]
    pages, sha = load_pages(root / spec["run"], prim["url"])
    offset = prim.get("printed_page_offset", 0)
    failures: list[str] = []

    def cite(item: dict, kind: str) -> dict:
        pg = item["pdf_page"]
        res = check_quote(pages, pg, item["quote"]) if kind == "quote" else check_figure(pages, pg, item["value"])
        if not res["ok"]:
            failures.append(f"{kind} not found on PDF p.{pg}: {item.get('quote') or item.get('value')!r} {res}")
        return {**item, "printed_page": pg + offset, "check": res,
                "link": f"{prim['url']}#page={pg}"}

    # ---- red-team gate for internet-facing sources (plumbinventory.redteam)
    from .redteam import checks_path, claim_status, latest, load_checks
    rt_all = load_checks(checks_path(candidates_path, spec))
    rt_view, rt_refetch = latest(rt_all), {k: v for k, v in rt_all.get("refetch", {}).items() if k != "at"}
    sources = {s["id"]: s for s in spec.get("secondary_sources", [])}
    collector = spec.get("collector")
    withheld: list[dict] = []
    used_claims: list[dict] = []

    def gate(pairs: list[list[str]]) -> tuple[list[dict], list[str]]:
        recs, why = [], []
        for key, cid in pairs:
            src = sources.get(key)
            if not src or cid not in (src.get("claims") or {}):
                failures.append(f"unknown source claim {key}/{cid}")
                why.append(f"{key}/{cid}: unknown claim")
                continue
            meta = rt_view.get(key, {}).get("meta", {})
            if meta.get("checker") and meta.get("checker") == collector:
                failures.append(f"{key}: checked by its own collector")
            ok, reason, rec = claim_status(rt_view, rt_refetch, key, cid, profile)
            if ok:
                recs.append({"source": key, "claim_id": cid, "claim": src["claims"][cid],
                             "excerpt": rec.get("excerpt", ""), "checker_note": rec.get("note", ""),
                             "checker": rec.get("checker"), "round": rec.get("round"),
                             "page_date": meta.get("page_date"), "page_title": meta.get("page_title")})
                used_claims.append({"source": key, "claim_id": cid, "ok": True})
            else:
                why.append(f"{key}/{cid}: {reason}")
                used_claims.append({"source": key, "claim_id": cid, "ok": False})
        return recs, why

    entries = []
    for e in spec["entries"]:
        e = dict(e)
        e["evidence"] = [cite(ev, "quote") for ev in e.get("evidence", [])]
        e["figures"] = [cite(f, "figure") for f in e.get("figures", [])]
        if e["basis"] == "disclosed" and not e["evidence"]:
            failures.append(f"{e['id']}: basis 'disclosed' but no annual-report evidence")
        if e.get("secondary"):
            sec = dict(e["secondary"])
            if not sec.get("claims"):
                failures.append(f"{e['id']}: web source used without red-teamed claim ids")
                sec["claims"] = []
            recs, why = gate([[sec["source"], c] for c in sec["claims"]])
            if why:
                withheld.append({"id": e["id"], "name": e["name"], "reasons": why,
                                 "kept_on_annual_report_evidence": bool(e["evidence"])})
                if e["evidence"]:
                    e.pop("secondary")          # keep the row, drop the unverified web part
                else:
                    continue                     # nothing verified left: withhold the row
            else:
                sec["verified"] = recs
                e["secondary"] = sec
        if not e["evidence"] and not e.get("secondary"):
            failures.append(f"{e['id']}: no evidence of any kind")
        entries.append(e)

    page_claims = []
    for pc in spec.get("page_claims", []):
        recs, why = gate(pc["rests_on"])
        if why:
            withheld.append({"id": pc["id"], "name": pc["text"], "reasons": why, "kept_on_annual_report_evidence": False})
        else:
            page_claims.append({**pc, "verified": recs})

    rt_records = [c for s in rt_view.values() for c in s["claims"].values()]
    redteam_summary = {
        "profile": profile,
        "checker": sorted({r.get("checker") for r in rt_all.get("rounds", [])} - {None}),
        "rounds": len(rt_all.get("rounds", [])),
        "claims_checked": len(rt_records),
        "claims_supported": sum(c["verdict"] == "SUPPORTED" for c in rt_records),
        "claims_rejected": [{"source": k, "claim_id": cid, "claim": sources.get(k, {}).get("claims", {}).get(cid, ""),
                             "verdict": c["verdict"], "note": c.get("note", "")}
                            for k, s in rt_view.items() for cid, c in s["claims"].items() if c["verdict"] != "SUPPORTED"],
        "used": len(used_claims), "used_passed": sum(u["ok"] for u in used_claims),
        "refetch_run": bool(rt_refetch),
    }

    context = []
    for c in spec.get("context", []):
        c = dict(c)
        c["evidence"] = [cite(ev, "quote") for ev in c.get("evidence", [])]
        context.append(c)

    fq = dict(spec.get("finance_question") or {})
    if fq:
        fq["figures"] = [cite(f, "figure") for f in fq.get("figures", [])]

    checks = [ev["check"] for e in entries + context for ev in e["evidence"]] + \
             [f["check"] for e in entries for f in e["figures"]] + [f["check"] for f in fq.get("figures", [])]
    out = {
        "subject": spec["subject"],
        "client": spec["client"],
        "as_of": spec["as_of"],
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidates_sha256": hashlib.sha256(candidates_path.read_bytes()).hexdigest(),
        "primary_source": {**prim, "sha256": sha, "pages": len(pages),
                           "reconciled": False,
                           "reconciliation_note": "Hash is of the copy supplied 2026-10-25; not yet compared with a fresh publisher download."},
        "secondary_sources": spec.get("secondary_sources", []),
        "entries": entries,
        "context": context,
        "finance_question": fq,
        "ask_about": spec.get("ask_about", []),
        "page_claims": page_claims,
        "withheld": withheld,
        "redteam": redteam_summary,
        "summary": {
            "entries": len(entries),
            "disclosed": sum(e["basis"] == "disclosed" for e in entries),
            "secondary": sum(e["basis"] == "secondary" for e in entries),
            "group": sum(e["basis"] == "group" for e in entries),
            "checks": len(checks),
            "checks_passed": sum(c["ok"] for c in checks),
            "failures": failures,
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "inventory.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--profile", choices=["internal", "client"], default="internal",
                    help="client also requires a mechanical re-fetch match for every web claim used")
    a = ap.parse_args(argv)
    out = build(a.candidates, a.out, a.profile)
    s = out["summary"]
    print(f"{s['entries']} entries ({s['disclosed']} disclosed, {s['secondary']} secondary, {s['group']} group); "
          f"{s['checks_passed']}/{s['checks']} source checks passed")
    r = out["redteam"]
    print(f"red team ({r['profile']}): {r['used_passed']}/{r['used']} web claims used passed; "
          f"{r['claims_supported']}/{r['claims_checked']} supported across {r['rounds']} rounds; "
          f"{len(out['withheld'])} withheld")
    for w in out["withheld"]:
        print("WITHHELD", w["id"], "; ".join(w["reasons"]), file=sys.stderr)
    for f in s["failures"]:
        print("FAIL", f, file=sys.stderr)
    return 1 if s["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
