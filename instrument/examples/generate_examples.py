"""Generate the synthetic example files. Deterministic (seed 20261025).

Everything here is FICTIONAL. "Harbourline Mutual Bank" does not exist; the
benchmark rows are random draws, not real organisations.

    python examples/generate_examples.py   # from instrument/

Outputs:
  examples/responses_harbourline_fictional.csv   12 respondents × 48 items + V1–V4
  examples/benchmark_synthetic_40.csv            40 fictional organisations
  examples/rater_a.csv, examples/rater_b.csv     12 fictional orgs × 20 κ-subset items

Benchmark calibration: organisations are drawn stratified by target band
(6 Stagnating / 18 Emerging / 13 Scaling / 3 Leading = 15% / 45% / 32.5% /
7.5%), matching the §5.2 target shares with Leading inside the 5–10% window.
For each organisation a latent total is drawn uniformly inside its band, each
dimension score is the latent total plus N(0, 9) noise clipped to 0–100, and
the published total is recomputed exactly as the §2 weighted sum. Draws whose
recomputed total leaves the intended band are rejected and redrawn, so the
band mix is exact by construction.
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from plumbscore import load_instrument  # noqa: E402

rng = random.Random(20261025)
inst = load_instrument()
W = inst.weights


def band_of(total: float) -> str:
    return inst.band_list[0].name if total <= 25 else "Emerging" if total <= 50 else "Scaling" if total <= 75 else "Leading"


# ---------------------------------------------------------------------------
# 1. Responses for a fictional FI
# ---------------------------------------------------------------------------
EXCO = [("R01", "CEO"), ("R02", "CFO"), ("R03", "COO"), ("R04", "CRO"), ("R05", "CIO")]
OPER = [
    ("R06", "Head of Data"),
    ("R07", "Head of Digital Lending"),
    ("R08", "Head of Operations"),
    ("R09", "Head of Model Risk"),
    ("R10", "Head of HR"),
    ("R11", "Head of Payments"),
    ("R12", "Head of Analytics"),
]
# (operating "truth" level, ExCo uplift) per dimension — tuned so that D2 and D5
# show an ExCo-optimistic gap > 0.75 and several items cross σ > 1.0.
DIM_PROFILE = {
    "D1": (3.0, 0.5),
    "D2": (2.2, 1.4),
    "D3": (2.8, 0.3),
    "D4": (2.3, 0.6),
    "D5": (2.4, 1.1),
    "D6": (2.7, 0.2),
    "D7": (2.9, 0.4),
    "D8": (2.0, 0.3),
}
# Evidence actually logged in the (fictional) register, by item → (classes, ref)
EVIDENCE = {
    "D6.1": ("D", "EV-014 AI policy v3 + AUP, approved 2026-03"),
    "D6.2": ("S", "EV-021 inventory extract 2026-09"),
    "D6.3": ("D", "EV-022 impact assessments ×4"),
    "D2.6": ("D", "EV-030 DPIA register"),  # D only; item needs D+S → still capped at 3
    "D1.4": ("D", "EV-004 budget paper FY26"),  # D only; item needs D+S → capped
    "D3.2": ("S", "EV-041 eval + deploy logs"),
    "D7.1": ("S", "EV-050 M365 Copilot telemetry"),
    "D4.4": ("I", "EV-060 interviews CEO, CRO"),  # I only; item needs I+O → capped
    "D1.1": ("D", "EV-001 board paper 2026-02"),
    "D5.5": ("D+S", "EV-071 tier policy + approval logs"),
    "D8.6": ("S", "EV-080 FinOps cost dashboard"),
    "D1.5": ("O+D", "EV-005 live chatbot demo + product roadmap"),
    "D3.4": ("S", "EV-044 API gateway logs"),
}
# Items where ExCo claim 4–5 (so caps bite), beyond what the profile gives.
EXCO_CLAIMS = {"D1.1": 4, "D1.2": 4, "D2.1": 4, "D2.3": 5, "D5.1": 4, "D6.1": 4, "D7.2": 4, "D1.4": 4, "D4.4": 4, "D2.6": 4}
OPER_CLAIMS = {"D6.2": 4, "D3.2": 4, "D7.1": 4, "D5.5": 4, "D8.6": 4, "D6.1": 4, "D1.5": 4}


def _level(mu: float) -> int:
    v = int(round(rng.gauss(mu, 0.55)))
    return max(1, min(5, v))


def gen_responses(path: Path) -> None:
    rows = []
    for item in inst.items:
        truth, uplift = DIM_PROFILE[item.dimension]
        for rid, role in EXCO:
            s = _level(truth + uplift)
            if item.id in EXCO_CLAIMS and rng.random() < 0.7:
                s = EXCO_CLAIMS[item.id]
            rows.append((rid, "exco", role, item.id, s))
        for rid, role in OPER:
            s = _level(truth)
            if item.id in OPER_CLAIMS and rng.random() < 0.6:
                s = OPER_CLAIMS[item.id]
            rows.append((rid, "operating", role, item.id, s))
    out = []
    for rid, grp, role, iid, s in rows:
        ev, ref = EVIDENCE.get(iid, ("none", ""))
        # evidence is only attached to the respondent who owns the artefact
        owner = {"exco": ["R02", "R04", "R05"], "operating": ["R06", "R09", "R12"]}
        if ev != "none" and s >= 4 and rid in owner[grp]:
            out.append((rid, grp, role, iid, s, ev, ref))
        else:
            out.append((rid, grp, role, iid, s, "none", ""))
    # value axis, entered once by the CFO
    out += [
        ("R02", "exco", "CFO", "V1", "B", "S", "EV-090 finance extract FY25"),  # no attribution rule (D) → Band A not evidenced
        ("R02", "exco", "CFO", "V2", "40–61%", "none", ""),  # self-report → capped at 12–39%
        ("R02", "exco", "CFO", "V3", "3", "none", ""),
        ("R04", "exco", "CRO", "V4", "2", "none", ""),
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["respondent_id", "role_group", "role", "item_id", "score", "evidence_class", "evidence_ref"])
        w.writerows(out)


# ---------------------------------------------------------------------------
# 2. Benchmark of 40 fictional organisations
# ---------------------------------------------------------------------------
BANDS = [("Stagnating", 8, 25, 6), ("Emerging", 26, 50, 18), ("Scaling", 51, 75, 13), ("Leading", 76, 90, 3)]
SECTORS = ["banking", "insurance", "asset_management", "telco", "healthcare"]
REGIONS = ["SG", "HK", "AU", "JP", "IN"]
SIZES = ["large", "mid"]


def gen_benchmark(path: Path) -> None:
    rows = []
    for band, lo, hi, count in BANDS:
        for _ in range(count):
            while True:
                latent = rng.uniform(lo, hi)
                dims = {d: round(max(0.0, min(100.0, latent + rng.gauss(0, 9))), 1) for d in W}
                total = round(sum(W[d] * dims[d] for d in W) / 100, 2)
                if band_of(total) == band:
                    break
            rows.append({**{d: f"{dims[d]:.1f}" for d in W}, "total": f"{total:.2f}"})
    rng.shuffle(rows)
    out = []
    for i, r in enumerate(rows, start=1):
        # the first 16 (after shuffling) are banking × large × SG, so the example
        # shows a valid peer set (n ≥ 15) with a representative band mix
        if i <= 16:
            sector, size, region = "banking", "large", "SG"
        else:
            sector, size, region = rng.choice(SECTORS), rng.choice(SIZES), rng.choice(REGIONS)
        out.append(
            {
                "org_id": f"ORG-{i:03d}",
                "sector": sector,
                "size_band": size,
                "region": region,
                **r,
                "evidence_gated": 1 if rng.random() < 0.4 else 0,
                "as_of": "2026-10-01",
            }
        )
    rows = out
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bands = [band_of(float(r["total"])) for r in rows]
    print("benchmark band mix:", {b: bands.count(b) for b in ["Stagnating", "Emerging", "Scaling", "Leading"]})


# ---------------------------------------------------------------------------
# 3. Two raters on the κ subset for 12 fictional organisations
# ---------------------------------------------------------------------------
def gen_raters(path_a: Path, path_b: Path) -> None:
    subset = inst.kappa_subset
    a_rows, b_rows = [], []
    for o in range(1, 13):
        org = f"KORG-{o:02d}"
        for item in subset:
            true = rng.choice([1, 2, 2, 3, 3, 3, 4, 4, 5])
            a = true
            # rater B disagrees more on judgement-heavy culture / strategy items
            p_dis = 0.45 if item in {"D7.3", "D1.1", "D4.1"} else 0.18
            b = max(1, min(5, true + rng.choice([-1, 1]))) if rng.random() < p_dis else true
            a_rows.append((org, item, a))
            b_rows.append((org, item, b))
    for p, rows in ((path_a, a_rows), (path_b, b_rows)):
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["org_id", "item_id", "score"])
            w.writerows(rows)


if __name__ == "__main__":
    gen_responses(HERE / "responses_harbourline_fictional.csv")
    gen_benchmark(HERE / "benchmark_synthetic_40.csv")
    gen_raters(HERE / "rater_a.csv", HERE / "rater_b.csv")
    print("written to", HERE)
