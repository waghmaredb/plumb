"""Render inventory.json into a single self-contained HTML page (the click-any-number view).

Refuses to render if the inventory has any failed source check: a page never shows a claim the build
could not match. Usage: python -m plumbinventory.page <inventory.json> --out <page.html>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).with_name("page_template.html")


def render(inv: dict, title: str) -> str:
    if inv["summary"]["failures"]:
        raise SystemExit("refusing to render: inventory has failed source checks")
    data = json.dumps(inv, ensure_ascii=False).replace("</", "<\\/")
    return (TEMPLATE.read_text()
            .replace("__TITLE__", title)
            .replace("__CLIENT__", inv["client"])
            .replace("__DATA__", data))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inventory", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--title", default=None)
    a = ap.parse_args(argv)
    inv = json.loads(a.inventory.read_text())
    a.out.write_text(render(inv, a.title or f"{inv['client']} AI Inventory Starter"))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
