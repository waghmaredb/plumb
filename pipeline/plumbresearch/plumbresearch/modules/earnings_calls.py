"""Earnings-call module: AI-mention density per transcript (mentions per
1,000 words), split into prepared remarks and Q&A (instrument D1.1, D8.6;
Federal Reserve AIR Index method, instrument source P3).

A ``TranscriptSource`` supplies transcripts. ``FileTranscriptSource`` reads
``<subject_dir>/transcripts/index.yaml`` (rows: url, date, quarter, file,
label?) with plain-text transcripts split by a Q&A marker. That covers the
fixture, and the real case where a transcript PDF has been converted to text
locally and is served under its IR URL by the local-document transport.
Live providers (AlphaSense, S&P Capital IQ) are licence-gated and not
implemented; GEH has no calls (alpha-targets §4), so the module reports
"not available" rather than substituting the parent's call silently —
proxy-by-parent must be declared as a separate document with ``label``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Protocol

import yaml

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import Subject
from ..textutil import ai_sentences, mentions_per_1000

MODULE = "earnings-calls"
QA_MARKERS = re.compile(r"(?im)^\s*(?:={2,}\s*)?(?:question[- ]and[- ]answer(?: session)?|questions? (?:and|&) answers?|q\s*&\s*a(?: session)?)\s*(?:={2,})?\s*$")
MAX_QUOTES_PER_CALL = 2


@dataclass
class Transcript:
    url: str
    date: date
    quarter: str
    prepared: str
    qa: str
    label: Optional[str] = None  # e.g. "proxy-by-parent: OCBC"

    @property
    def text(self) -> str:
        return f"{self.prepared}\n\n{self.qa}".strip()


def split_qa(text: str) -> tuple[str, str]:
    m = QA_MARKERS.search(text)
    if not m:
        return text, ""
    return text[: m.start()].strip(), text[m.end():].strip()


class TranscriptSource(Protocol):
    def transcripts(self, subject: Subject, since: date, until: date) -> list[Transcript]: ...


class FileTranscriptSource:
    def __init__(self, directory: str | Path):
        self.dir = Path(directory)

    def transcripts(self, subject: Subject, since: date, until: date) -> list[Transcript]:
        idx = self.dir / "index.yaml"
        if not idx.exists():
            return []
        out: list[Transcript] = []
        for row in yaml.safe_load(idx.read_text(encoding="utf-8")) or []:
            d = date.fromisoformat(str(row["date"])[:10])
            if not (since <= d <= until):
                continue
            text = (self.dir / row["file"]).read_text(encoding="utf-8")
            prep, qa = split_qa(text)
            out.append(Transcript(url=row["url"], date=d, quarter=str(row.get("quarter", "")), prepared=prep, qa=qa, label=row.get("label")))
        return out


@dataclass
class Density:
    mentions: int
    words: int
    per_1000: float
    prepared_mentions: int
    prepared_words: int
    prepared_per_1000: float
    qa_mentions: int
    qa_words: int
    qa_per_1000: float

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def density(t: Transcript) -> Density:
    n, w, d = mentions_per_1000(t.text)
    pn, pw, pd = mentions_per_1000(t.prepared)
    qn, qw, qd = mentions_per_1000(t.qa)
    return Density(n, w, round(d, 2), pn, pw, round(pd, 2), qn, qw, round(qd, 2))


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None,
        source: Optional[TranscriptSource] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    source = source or FileTranscriptSource(ctx.subject_dir / "transcripts")
    cp = ctx.checkpoint(MODULE)
    gaps: list[Gap] = []
    since = date(ctx.as_of.year - 2, ctx.as_of.month, 1)
    ctx.charge(MODULE, "transcript_source", source=type(source).__name__, since=str(since), until=str(ctx.as_of))
    transcripts = source.transcripts(subject, since, ctx.as_of)
    if not transcripts:
        gaps.append(Gap(module=MODULE, topic="no transcripts", detail=f"no earnings-call transcripts for {subject.short_name} between {since} and {ctx.as_of} "
                        f"(alpha-targets §4: availability [VERIFY]; GEH has no calls — proxy-by-parent must be declared with a label)",
                        instrument_items=["D1.1", "D8.6"], verify_flag=True))
        return ModuleResult(module=MODULE, subject_slug=subject.slug, gaps=gaps, data_available=False, tool_calls=ctx.budget(MODULE).calls)
    for t in transcripts:
        if cp.has(t.url):
            continue
        src = ctx.fetch(MODULE, t.url)  # the stored copy is what quotations are checked against
        dens = density(t)
        claims = []
        if src.citable and src.text_extract:
            text = src.text_extract
            tier = src.tier
            label = confidence_for_tier(tier)
            # quote the Q&A AI sentences first (analyst-driven), then prepared
            # quotations are lifted from the STORED text so C5 compares like with like
            candidates = [s for s in ai_sentences(text) if 40 <= len(s) <= 600]
            qa_set = set(ai_sentences(t.qa))
            candidates.sort(key=lambda s: 0 if s in qa_set else 1)  # Q&A (analyst-driven) first
            for i, s in enumerate(candidates[:MAX_QUOTES_PER_CALL], 1):
                claims.append(ResearchClaim(id=f"{subject.slug}.call.{t.quarter}.q{i}", module=MODULE, text=s, kind=ClaimKind.quote,
                                                load_bearing=False, sources=[t.url], passage=s, tier=tier, confidence_label=label,
                                                instrument_items=["D1.1", "D8.6"], signal_ids=[f"{subject.slug}.call.{t.quarter}.density"],
                                                period=t.quarter, note=(t.label or "") or None))
            gap = None
        else:
            gap = f"transcript not readable: state={src.state.value} {src.error or ''}"
        sig = Signal(id=f"{subject.slug}.call.{t.quarter}.density", module=MODULE, name=f"Earnings-call AI density {t.quarter}",
                     instrument_items=["D1.1", "D8.6"], value=dens.per_1000, unit="mentions per 1,000 words", source=t.url, source_urls=[t.url],
                     tier=src.tier, confidence_label=ConfidenceLabel.model_inferred, evidence_claim_ids=[c.id for c in claims],
                     detail=dens.as_dict() | {"date": t.date.isoformat(), "label": t.label},
                     note=(f"{t.label}; " if t.label else "") + f"prepared {dens.prepared_per_1000}/1000, Q&A {dens.qa_per_1000}/1000")
        cp.put(t.url, {"claims": [c.model_dump(mode="json") for c in claims], "signal": sig.model_dump(mode="json"), "gap": gap, "quarter": t.quarter})
    claims: list[ResearchClaim] = []
    signals: list[Signal] = []
    per_call = []
    for p in cp.values():
        claims.extend(ResearchClaim.model_validate(c) for c in p["claims"])
        s = Signal.model_validate(p["signal"])
        signals.append(s)
        per_call.append(s.detail)
        if p.get("gap"):
            gaps.append(Gap(module=MODULE, topic=f"transcript {p['quarter']}", detail=p["gap"], instrument_items=["D1.1"]))
    if per_call:
        tot_m = sum(d["mentions"] for d in per_call)
        tot_w = sum(d["words"] for d in per_call)
        qa_m = sum(d["qa_mentions"] for d in per_call)
        qa_w = sum(d["qa_words"] for d in per_call)
        pr_m = sum(d["prepared_mentions"] for d in per_call)
        pr_w = sum(d["prepared_words"] for d in per_call)
        signals.insert(0, Signal(id=f"{subject.slug}.call.density", module=MODULE, name="Earnings-call AI density (all calls in window)",
                                 instrument_items=["D1.1", "D8.6"], value=round(tot_m / tot_w * 1000, 2) if tot_w else None,
                                 unit="mentions per 1,000 words", source=f"{len(per_call)} transcripts", source_urls=[s.source for s in signals],
                                 confidence_label=ConfidenceLabel.model_inferred, evidence_claim_ids=[c.id for c in claims],
                                 detail={"calls": len(per_call), "prepared_per_1000": round(pr_m / pr_w * 1000, 2) if pr_w else None,
                                         "qa_per_1000": round(qa_m / qa_w * 1000, 2) if qa_w else None,
                                         "qa_share_of_mentions": round(qa_m / tot_m, 3) if tot_m else None},
                                 note="Q&A density reflects analyst interest; prepared density reflects management framing (AI-washing risk, P3/P9)"))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        data_available=bool(per_call), tool_calls=ctx.budget(MODULE).calls, detail={"calls": per_call})
