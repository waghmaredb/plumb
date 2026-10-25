"""C4 calibration harness (spec T-03 in miniature; open item 1). Added in 0.5.

    plumbverify calibrate calibration/geh_c4_v1.jsonl [--split heldout|dev|all] [--target-false-support 0.02] [--json out.json]

Input: JSONL, one claim-passage pair per line:
    {"id", "split": "dev"|"heldout", "claim", "passage", "page", "label": "supported"|"partial"|"unsupported", "category"}

For every backend that is live on this machine (plus the pre-0.5 lexical
matcher as a reference row) it reports SUPPORTED precision / recall / F1,
3-way accuracy and - the number that matters for block-not-flag - the
false-SUPPORT rate: gold UNSUPPORTED or PARTIAL pairs the matcher would
release as SUPPORTED, with a Wilson 95% upper bound because the sets are
small. It also sweeps the SUPPORTED threshold and suggests the lowest one
that keeps false-SUPPORT at or under the target.

Labels in calibration/geh_c4_v1.jsonl are author-assigned; they are not
acceptance evidence until the independent reviewer has re-labelled them.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from . import match as m
from .semantic import C4Verifier, EmbeddingBackend, NLIBackend, OfflineBaseline

LABELS = ("supported", "partial", "unsupported")


@dataclass
class Pair:
    id: str
    claim: str
    passage: str
    label: str
    split: str = "heldout"
    category: str = ""
    page: Optional[int] = None


def load_pairs(path: str | Path, split: str = "heldout") -> list[Pair]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("label") not in LABELS:
            raise ValueError(f"{d.get('id')}: label must be one of {LABELS}")
        p = Pair(id=d["id"], claim=d["claim"], passage=d["passage"], label=d["label"], split=d.get("split", "heldout"),
                 category=d.get("category", ""), page=d.get("page"))
        if split == "all" or p.split == split:
            out.append(p)
    return out


def wilson_upper(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    phat = k / n
    denom = 1 + z * z / n
    centre = phat + z * z / (2 * n)
    margin = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    return min(1.0, (centre + margin) / denom)


@dataclass
class Prediction:
    pair: Pair
    label: str
    score: float
    raw: float
    rules: list[str] = field(default_factory=list)
    has_rule: bool = False
    contradiction: bool = False


@dataclass
class BackendResult:
    backend: str
    n: int
    confusion: dict[str, dict[str, int]]
    precision: float
    recall: float
    f1: float
    accuracy: float
    false_support: int
    non_supported: int
    false_support_rate: float
    false_support_upper95: float
    false_support_from_unsupported: int
    false_support_from_partial: int
    suggested_supported_threshold: Optional[float]
    suggested_partial_threshold: Optional[float]
    recall_at_suggested: Optional[float]
    false_support_ids: list[str]
    predictions: list[Prediction] = field(default_factory=list, repr=False)

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "predictions"}
        d["per_pair"] = [{"id": p.pair.id, "gold": p.pair.label, "pred": p.label, "score": p.score, "raw": p.raw,
                          "rules": p.rules, "category": p.pair.category} for p in self.predictions]
        return d


def _predict_lexical(pairs: Sequence[Pair], supported: float, partial: float) -> list[Prediction]:
    out = []
    for p in pairs:
        pm = m.claim_match(p.claim, [p.passage], None, supported, partial)
        out.append(Prediction(p, pm.label, pm.score, pm.score))
    return out


def _predict(verifier: C4Verifier, pairs: Sequence[Pair]) -> list[Prediction]:
    out = []
    for p in pairs:
        a = verifier.assess(p.claim, p.passage)
        out.append(Prediction(p, a.label, a.score, a.raw_score, a.rules_fired, bool(a.rules),
                              any(r.effect == "contradiction" for r in a.rules)))
    return out


def _metrics(name: str, preds: list[Prediction], target: float, supported: float, partial: float) -> BackendResult:
    conf = {g: {q: 0 for q in LABELS} for g in LABELS}
    for p in preds:
        conf[p.pair.label][p.label] += 1
    tp = conf["supported"]["supported"]
    fp_u, fp_p = conf["unsupported"]["supported"], conf["partial"]["supported"]
    fp = fp_u + fp_p
    fn = conf["supported"]["partial"] + conf["supported"]["unsupported"]
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    acc = sum(conf[g][g] for g in LABELS) / len(preds) if preds else 0.0
    neg = sum(1 for p in preds if p.pair.label != "supported")
    # threshold sweep on the raw (pre-cap) score; any fired rule still vetoes SUPPORTED
    grid = [round(0.50 + 0.01 * i, 2) for i in range(50)]
    sug, sug_rec = None, None
    pos = sum(1 for p in preds if p.pair.label == "supported")
    for t in grid:
        fs = sum(1 for p in preds if p.pair.label != "supported" and p.raw >= t and not p.has_rule)
        if neg and fs / neg <= target:
            sug = t
            sug_rec = (sum(1 for p in preds if p.pair.label == "supported" and p.raw >= t and not p.has_rule) / pos) if pos else 0.0
            break
    sug_partial = None
    if sug is not None:
        best = -1.0
        for pt in [round(0.30 + 0.01 * i, 2) for i in range(int((sug - 0.30) * 100))]:
            ok = 0
            for p in preds:
                if p.contradiction:
                    lab = "unsupported"
                elif p.raw >= sug and not p.has_rule:
                    lab = "supported"
                elif min(p.raw, m.SUPPORTED_THRESHOLD - 1e-9 if p.has_rule else p.raw) >= pt:
                    lab = "partial"
                else:
                    lab = "unsupported"
                ok += lab == p.pair.label
            if ok > best:
                best, sug_partial = ok, pt
    return BackendResult(
        backend=name, n=len(preds), confusion=conf, precision=round(prec, 4), recall=round(rec, 4), f1=round(f1, 4),
        accuracy=round(acc, 4), false_support=fp, non_supported=neg,
        false_support_rate=round(fp / neg, 4) if neg else 0.0, false_support_upper95=round(wilson_upper(fp, neg), 4),
        false_support_from_unsupported=fp_u, false_support_from_partial=fp_p,
        suggested_supported_threshold=sug, suggested_partial_threshold=sug_partial,
        recall_at_suggested=round(sug_rec, 4) if sug_rec is not None else None,
        false_support_ids=[p.pair.id for p in preds if p.pair.label != "supported" and p.label == "supported"],
        predictions=preds,
    )


def calibrate(pairs: Sequence[Pair], backends: Optional[Sequence] = None, target_false_support: float = 0.02,
              supported: float = m.SUPPORTED_THRESHOLD, partial: float = m.PARTIAL_THRESHOLD,
              include_lexical: bool = True) -> tuple[list[BackendResult], list[dict]]:
    """Evaluate each live backend on its own (each always paired with the
    deterministic rules). Returns (results, backend status rows)."""
    backends = list(backends) if backends is not None else [NLIBackend(), EmbeddingBackend(), OfflineBaseline()]
    status = []
    results: list[BackendResult] = []
    if include_lexical:
        results.append(_metrics("lexical (pre-0.5 rapidfuzz)", _predict_lexical(pairs, supported, partial),
                                target_false_support, supported, partial))
    for b in backends:
        ok = b.available()
        status.append({"backend": b.name, "available": ok, "reason": None if ok else getattr(b, "unavailable_reason", None)})
        if not ok:
            continue
        v = C4Verifier(backends=[b] if isinstance(b, OfflineBaseline) else [b, OfflineBaseline()],
                       supported=supported, partial=partial)
        results.append(_metrics(b.name, _predict(v, pairs), target_false_support, supported, partial))
    return results, status


def format_table(results: list[BackendResult], status: list[dict], split: str, target: float) -> str:
    lines = [f"C4 calibration on split={split} (target false-SUPPORT <= {target:.0%})", ""]
    lines.append("| backend | n | SUPPORTED P | R | F1 | 3-way acc | false-SUPPORT (k/n) | rate | 95% upper | from unsup / partial | suggested thr (supported / partial) | recall @ suggested |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        sug = (f"{r.suggested_supported_threshold:.2f} / {r.suggested_partial_threshold:.2f}"
               if r.suggested_supported_threshold is not None and r.suggested_partial_threshold is not None else "none meets target")
        rec = f"{r.recall_at_suggested:.2f}" if r.recall_at_suggested is not None else "-"
        lines.append(f"| {r.backend} | {r.n} | {r.precision:.2f} | {r.recall:.2f} | {r.f1:.2f} | {r.accuracy:.2f} | "
                     f"{r.false_support}/{r.non_supported} | {r.false_support_rate:.1%} | {r.false_support_upper95:.1%} | "
                     f"{r.false_support_from_unsupported} / {r.false_support_from_partial} | {sug} | {rec} |")
    lines.append("")
    for s in status:
        if not s["available"]:
            lines.append(f"- {s['backend']}: not evaluated ({s['reason']})")
    for r in results:
        if r.false_support_ids:
            lines.append(f"- {r.backend} false-SUPPORT pairs: {', '.join(r.false_support_ids)}")
    lines.append("")
    lines.append("Labels are author-assigned; re-label with the independent reviewer before using these numbers as acceptance evidence.")
    return "\n".join(lines)
