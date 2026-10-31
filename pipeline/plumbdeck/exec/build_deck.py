"""One command for an executive deck, with every gate in order. Any failure stops the build.

  1. resolve   every face sentence against released evidence; figures against the hashed PDF
  2. rubric    editorial rules from the CXO review (deck_rubric.py)
  3. lint      no internal vocabulary on the face (face_lint.py)
  4. render    PowerPoint, with the layout audit (overflow, off-slide, orphan titles, collisions)
  5. validate  the .pptx package (pptx skill validator, when PPTX_SKILL_DIR is set)
  6. pdf       PDF and page previews (when LibreOffice is available)

Usage: python build_deck.py STORYLINE.json --run RUN_DIR --out OUT_DIR [--pdf SOURCE.pdf] [--signoff YAML] [--previews]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def step(name: str, cmd: list[str], env=None) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    out = (r.stdout + r.stderr).strip()
    shown = "\n".join(ln for ln in out.splitlines() if "C4 rule hit" not in ln)
    print(f"[{name}] {'ok' if r.returncode == 0 else 'FAILED'}")
    if shown and (r.returncode != 0 or name in ("rubric",)):
        print("  " + shown.replace("\n", "\n  "))
    if r.returncode != 0:
        sys.exit(f"build stopped at {name}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("storyline", type=Path)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--signoff", type=Path)
    ap.add_argument("--name", default="deck")
    ap.add_argument("--previews", action="store_true")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    cmd = [py, str(HERE / "resolve_storyline.py"), str(a.storyline), "--run", str(a.run), "--out", str(a.out)]
    if a.pdf:
        cmd += ["--pdf", str(a.pdf)]
    if a.signoff:
        cmd += ["--signoff", str(a.signoff)]
    step("resolve", cmd)
    resolved = a.out / "resolved.json"
    step("rubric", [py, str(HERE / "deck_rubric.py"), str(resolved)])
    step("lint", [py, str(HERE / "face_lint.py"), str(resolved)])
    pptx = a.out / f"{a.name}.pptx"
    step("render", ["node", str(HERE / "render_exec.js"), str(resolved), str(pptx)], env=os.environ.copy())
    sk = os.environ.get("PPTX_SKILL_DIR")
    if sk and (Path(sk) / "scripts/office/validate.py").exists():
        step("validate", [py, str(Path(sk) / "scripts/office/validate.py"), str(pptx)])
        soffice = Path(sk) / "scripts/office/soffice.py"
        if soffice.exists():
            subprocess.run([py, str(soffice), "--headless", "--convert-to", "pdf", "--outdir", str(a.out), str(pptx)],
                           capture_output=True, text=True)
            pdf = a.out / f"{a.name}.pdf"
            print(f"[pdf] {'ok' if pdf.exists() else 'skipped (LibreOffice unavailable)'}")
            if pdf.exists() and a.previews and shutil.which("pdftoppm"):
                subprocess.run(["pdftoppm", "-jpeg", "-r", "100", str(pdf), str(a.out / "slide")], check=True)
                print("[previews] ok")
    status = json.loads(resolved.read_text())["_status"]
    print(f"built {pptx} — {'FINAL' if status['final'] else 'Discussion draft'}"
          + ("" if status["final"] else f" (founder inputs: {len(status['founder_inputs'])}, pending slides: {len(status['pending_slides'])})"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
