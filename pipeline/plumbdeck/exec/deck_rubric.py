"""Editorial rubric for executive decks — the cold CXO review of 2026-10-26, made repeatable.

Runs on a resolved storyline (resolve_storyline.py output). Hard rules fail the build;
soft rules are scored and reported. The layout audit (render_exec.js) covers geometry;
this covers what a sceptical Group CEO noticed about content and structure.

Usage: python deck_rubric.py resolved.json [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

CURRENCY = re.compile(r"(S\$|US\$|\$|€|£)\s?\d|\bfee\b", re.I)
HEADLINE_NUM = re.compile(r"(?:S\$|US\$)?\d[\d,.]*\s?(?:%|bn|m)\b|\b\d+ of \d+\b")
FEAR_WORDS = re.compile(r"\b(urgent|deadline looms|before (?:MAS|the regulator) asks|fall behind|risk falling|wake-up)\b", re.I)
HYPE_WORDS = re.compile(r"\b(revolutioni[sz]e|transformational journey|unlock(?:ing)? (?:massive|huge)|game[- ]chang|cutting[- ]edge|best[- ]in[- ]class|world[- ]class)\b", re.I)


def texts(node):
    if isinstance(node, dict):
        if "kind" in node and "text" in node:
            yield node
        for v in node.values():
            yield from texts(v)
    elif isinstance(node, list):
        for v in node:
            yield from texts(v)


def evaluate(story: dict) -> dict:
    slides = story["slides"]
    content = [s for s in slides if s["layout"] != "cover"]
    hard: list[str] = []
    soft: list[tuple[str, bool, str]] = []

    # H1 every slide that states a finding or a figure carries a source footnote
    for s in content:
        states = any(e["kind"] in ("synthesis", "quote", "derived", "observation") for e in texts(s)) or s.get("figures")
        if states and not s.get("_pending") and not s.get("_source"):
            hard.append(f"{s['id']}: states findings but has no source footnote")

    # H2 derived value is labelled as illustrative / not a forecast on the same slide
    for s in content:
        if any(e["kind"] == "derived" for e in texts(s)):
            straps = " ".join(e["text"] for e in texts(s) if e["kind"] in ("method", "label"))
            if "not a forecast" not in straps.lower():
                hard.append(f"{s['id']}: derived value without a 'not a forecast' qualifier on the slide")

    # H7 a value calculation must rest on a base AI can actually move (2026-10-26: "every 1% of
    # total claims and benefits" priced contractual policyholder benefits as a cost to cut)
    for s in content:
        for e in texts(s):
            if e["kind"] != "derived":
                continue
            d = e.get("derived", {})
            ids = d.get("sum") or [d.get("figure")]
            for f in s.get("figures", []):
                if f["id"] in ids and not (f.get("addressable") is True and f.get("basis")):
                    hard.append(f"{s['id']}: value rests on '{f['label']}' without an addressable basis")

    # H3 the ask is a meeting, not a price (fees belong in the cover note)
    for s in content:
        ask = s.get("ask")
        if ask and CURRENCY.search(re.sub(r"\[\[FOUNDER: [^\]]+\]\]", "", ask.get("text", ""))):
            hard.append(f"{s['id']}: the ask quotes a fee or amount")

    # H4 credentials come early: who we are sits within the first three slides
    about = [i for i, s in enumerate(slides) if s["id"] == "about" or s["layout"] in ("about", "about_min")]
    if about and about[0] > 2:
        hard.append(f"credentials appear on slide {about[0] + 1}; move them to slide 2")

    # H5 pending slides never pre-rank or pre-fill peers (no bar widths implying an order)
    for s in content:
        if s.get("_pending") and s["layout"] == "pending_bars":
            hard.append(f"{s['id']}: placeholder bars imply a ranking before the data exists; use a table")

    # H6 no fear-selling or hype on the face
    for s in slides:
        for e in texts(s):
            if FEAR_WORDS.search(e["text"]) or HYPE_WORDS.search(e["text"]):
                hard.append(f"{s['id']}: tone — '{e['text'][:70]}'")

    # S1 headline syntax varies: at most a third of titles hinge on a semicolon contrast
    titles = [s["title"]["text"] for s in content]
    semis = sum(";" in t for t in titles)
    soft.append(("title syntax varies", semis <= max(1, len(titles) // 3), f"{semis} of {len(titles)} titles use 'X; Y'"))

    # S2 one headline number is not repeated across many slides
    nums = Counter()
    for s in content:
        found = set()
        for e in texts(s):
            found |= set(HEADLINE_NUM.findall(e["text"]))
        for tl in s.get("tiles", []):
            found.add(tl["big"])
        nums.update(found)
    over = {n: c for n, c in nums.items() if c > 2}
    soft.append(("no number on more than two slides", not over, ", ".join(f"{n} ×{c}" for n, c in over.items()) or "ok"))

    # S3 the client's own numbers anchor the value story
    has_value = any(s.get("figures") for s in content)
    soft.append(("value anchored on the client's own reported figures", has_value, "verified table figures present" if has_value else "no verified figures"))

    # S4 hypotheses are statements that could be proven wrong, not questions
    hyp = [c for s in content for c in s.get("cards", []) if s["id"] == "hypotheses"]
    qs = [c["text"] for c in hyp if c["text"].rstrip().endswith("?")]
    soft.append(("hypotheses are falsifiable statements", bool(hyp) and not qs, f"{len(qs)} phrased as questions" if qs else "ok"))

    # S5 decorative icons are not on every slide
    icon_slides = sum(1 for s in content if re.search(r'"Lu[A-Z]', json.dumps(s)))
    soft.append(("icons used with restraint", icon_slides <= len(content) * 0.6, f"icons on {icon_slides} of {len(content)} content slides"))

    # S6 deck length fits a pre-read
    soft.append(("pre-read length 8–12 slides", 8 <= len(slides) <= 12, f"{len(slides)} slides"))

    score = sum(ok for _, ok, _ in soft)
    return {"hard_failures": hard, "soft": [{"rule": r, "pass": ok, "detail": d} for r, ok, d in soft],
            "soft_score": f"{score}/{len(soft)}", "passed": not hard}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("resolved", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = evaluate(json.loads(a.resolved.read_text()))
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"rubric: {'PASS' if res['passed'] else 'FAIL'} — soft {res['soft_score']}")
        for h in res["hard_failures"]:
            print(f"  HARD  {h}")
        for s in res["soft"]:
            print(f"  {'ok  ' if s['pass'] else 'warn'}  {s['rule']}: {s['detail']}")
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
