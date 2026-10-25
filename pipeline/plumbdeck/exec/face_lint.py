"""Face-text lint for executive decks: internal QA vocabulary must never reach a client slide."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

FORBIDDEN = [
    r"\bclaims? (released|withheld)\b", r"\bwithheld\b", r"\bgap register\b", r"\bG-\d+\b", r"\bT[1-5]\b",
    r"\bresolution\b", r"\bhash\b", r"\bunreconciled\b", r"\binterlock\b", r"\[H\]", r"\bplumbverify\b",
    r"\bplumbresearch\b", r"\bconfidence: ", r"\bC4\b", r"\bbuild profile\b", r"\bQA gate\b",
]

def face_texts(resolved: dict):
    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k.startswith("_") and k != "_source":
                    continue
                yield from walk(v)
        elif isinstance(n, list):
            for v in n:
                yield from walk(v)
        elif isinstance(n, str):
            yield n
    for s in resolved["slides"]:
        for k, v in s.items():
            if k in ("id", "layout") or (k.startswith("_") and k != "_source"):
                continue
            yield from ((s["id"], t) for t in walk(v) if isinstance(t, str))

def lint(resolved: dict) -> list[str]:
    errs = []
    for sid, txt in face_texts(resolved):
        for pat in FORBIDDEN:
            if re.search(pat, txt, re.I):
                errs.append(f"{sid}: internal vocabulary {pat!r} in face text: {txt[:80]}")
    return errs

if __name__ == "__main__":
    e = lint(json.loads(Path(sys.argv[1]).read_text()))
    print("\n".join(e) or "face lint: ok")
    raise SystemExit(1 if e else 0)
