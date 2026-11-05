"""Source red-team engine: no internet-facing claim reaches a page unless someone other than its
collector has checked it against the live page.

Three commands:

  prompt   Write the brief for an independent checker (agent or person) from candidates.yaml: the URLs
           and the exact claims, nothing else. The checker never sees the collector's reasoning.
  merge    Add a checker's JSON verdicts (one round) to the run's source_checks.json.
  refetch  Mechanical second line, run where the shell has internet egress: re-download each page and
           confirm every SUPPORTED excerpt appears in it. Records MATCH / MISMATCH / UNREACHABLE.

Verdicts: SUPPORTED | PARTIAL | NOT_SUPPORTED | WRONG_ENTITY | UNREACHABLE. Only SUPPORTED lets a claim
through. The build (build.py) withholds any entry, or any page statement, that rests on a claim without
a SUPPORTED verdict, and lists it under "Removed, not footnoted". In the client profile it additionally
requires a refetch MATCH for every claim it uses.

Usage:
  python -m plumbinventory.redteam prompt  <candidates.yaml> --out brief.md
  python -m plumbinventory.redteam merge   <candidates.yaml> <checker.json>
  python -m plumbinventory.redteam refetch <candidates.yaml>
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .build import norm

PASS = "SUPPORTED"
VERDICTS = {"SUPPORTED", "PARTIAL", "NOT_SUPPORTED", "WRONG_ENTITY", "UNREACHABLE"}

BRIEF_HEAD = """You are an independent source auditor. Another agent collected the web sources below and wrote
claims about what each says. Try to PROVE THEM WRONG: assume any claim may be hallucinated, overstated,
misdated, or about the wrong organisation. You have not seen that agent's reasoning and must not guess it.

For each source, fetch the exact URL. For each claim give a verdict — SUPPORTED (quote a verbatim
excerpt, 5–40 words, that supports it), PARTIAL (say what is not supported), NOT_SUPPORTED, WRONG_ENTITY
(page is about a different organisation than {client}), or UNREACHABLE. Report the page title, the date
shown on the page (or "no date shown") and the organisation the page is about. Excerpts are copied, never
paraphrased. When unsure, choose the more conservative verdict.

Return ONLY JSON: {{"checker":"<who>","checked_at":"<ISO date>","sources":[{{"key":"<source key>","url":"...",
"fetched":true,"page_title":"...","page_date":"...","about_org":"...","claims":[{{"id":"c1","verdict":"...",
"excerpt":"...","note":"..."}}]}}]}}
"""


def checks_path(candidates: Path, spec: dict) -> Path:
    return candidates.parent / spec.get("source_checks", "source_checks.json")


def load_checks(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"rounds": [], "refetch": {}}


def latest(checks: dict) -> dict[str, dict]:
    """Collapse rounds into {source_key: {"meta": {...}, "claims": {cid: claim}}}; later rounds win."""
    out: dict[str, dict] = {}
    for rnd in checks.get("rounds", []):
        for s in rnd.get("sources", []):
            key = s.get("key")
            slot = out.setdefault(key, {"meta": {}, "claims": {}})
            for k in ("url", "fetched", "page_title", "page_date", "about_org"):
                if k in s:
                    slot["meta"][k] = s[k]
            slot["meta"]["checker"] = rnd.get("checker")
            for c in s.get("claims", []):
                slot["claims"][c["id"]] = {**c, "checker": rnd.get("checker"),
                                           "checked_at": rnd.get("checked_at"), "round": rnd.get("round", 1)}
    return out


def claim_status(view: dict, refetch: dict, key: str, cid: str, profile: str) -> tuple[bool, str, dict | None]:
    """Is source `key` claim `cid` allowed on a page? Returns (ok, reason, claim record)."""
    slot = view.get(key)
    if not slot:
        return False, "not red-teamed", None
    c = slot["claims"].get(cid)
    if not c:
        return False, f"claim {cid} not red-teamed", None
    if c["verdict"] != PASS:
        return False, f"red team: {c['verdict']} — {c.get('note', '')}".strip(" —"), c
    if profile == "client":
        r = refetch.get(key, {}).get(cid)
        if r != "MATCH":
            return False, f"no mechanical re-fetch match ({r or 'not run'})", c
    return True, "", c


# ---------------------------------------------------------------- commands
def cmd_prompt(candidates: Path, out: Path) -> None:
    spec = yaml.safe_load(candidates.read_text())
    lines = [BRIEF_HEAD.format(client=spec["client"]), "SOURCES AND CLAIMS", ""]
    for s in spec.get("secondary_sources", []):
        lines.append(f"{s['id']} — {s['url']}")
        for cid, text in (s.get("claims") or {}).items():
            lines.append(f"  {cid}: {text}")
        lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


def cmd_merge(candidates: Path, checker_json: Path) -> None:
    spec = yaml.safe_load(candidates.read_text())
    path = checks_path(candidates, spec)
    checks = load_checks(path)
    rnd = json.loads(checker_json.read_text())
    if rnd.get("checker") in (None, "", spec.get("collector")):
        raise SystemExit("refusing: checker must be named and must not be the collector")
    for s in rnd.get("sources", []):
        for c in s.get("claims", []):
            if c.get("verdict") not in VERDICTS:
                raise SystemExit(f"bad verdict {c.get('verdict')!r} in {s.get('key')}/{c.get('id')}")
            if c["verdict"] == PASS and c.get("excerpt") and len(c["excerpt"].split()) > 60:
                raise SystemExit(f"excerpt too long in {s.get('key')}/{c['id']}")
    rnd.setdefault("round", len(checks["rounds"]) + 1)
    checks["rounds"].append(rnd)
    path.write_text(json.dumps(checks, indent=1, ensure_ascii=False))
    print(f"merged round {rnd['round']} into {path}")


def page_text(raw: bytes, ctype: str) -> str:
    if "pdf" in ctype or raw[:4] == b"%PDF":
        try:
            from pypdf import PdfReader  # optional dependency
            import io
            return " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
        except Exception:
            return ""
    t = raw.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def cmd_refetch(candidates: Path, timeout: int = 30) -> None:
    spec = yaml.safe_load(candidates.read_text())
    path = checks_path(candidates, spec)
    checks = load_checks(path)
    view = latest(checks)
    res: dict = {}
    for s in spec.get("secondary_sources", []):
        key, url = s["id"], s["url"]
        res[key] = {}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "plumb-redteam/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = norm(page_text(r.read(), r.headers.get("content-type", ""))).lower()
        except Exception as e:  # network refused, 4xx/5xx, timeout
            for cid in (s.get("claims") or {}):
                res[key][cid] = "UNREACHABLE"
            res[key]["_error"] = type(e).__name__
            continue
        for cid, c in view.get(key, {}).get("claims", {}).items():
            ex = norm(c.get("excerpt") or "").lower()
            res[key][cid] = "MATCH" if ex and ex in body else ("NO_EXCERPT" if not ex else "MISMATCH")
    checks["refetch"] = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **res}
    path.write_text(json.dumps(checks, indent=1, ensure_ascii=False))
    n = sum(v == "MATCH" for r in res.values() for k, v in r.items() if not k.startswith("_"))
    print(f"refetch: {n} excerpt matches recorded in {path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt"); p.add_argument("candidates", type=Path); p.add_argument("--out", type=Path, required=True)
    m = sub.add_parser("merge"); m.add_argument("candidates", type=Path); m.add_argument("checker_json", type=Path)
    r = sub.add_parser("refetch"); r.add_argument("candidates", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "prompt":
        cmd_prompt(a.candidates, a.out)
    elif a.cmd == "merge":
        cmd_merge(a.candidates, a.checker_json)
    else:
        cmd_refetch(a.candidates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
