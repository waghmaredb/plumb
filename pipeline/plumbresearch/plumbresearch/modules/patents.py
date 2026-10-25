"""Patents module: AI-related patent counts for the subject and its core
peers (instrument D4.2, D1.5 proxies; BCG: future-built file 3.5x patents).

``PatentSource`` protocol with three implementations:

* ``CsvPatentSource`` — fixture / offline: columns assignee, number, title,
  abstract, filing_date, grant_date, url, office, cpc.
* ``PatentsViewSource`` — USPTO PatentsView Search API client. Implemented
  against the documented POST shape (``/api/v1/patent/`` with a JSON ``q`` on
  ``assignees.assignee_organization`` and ``patent_date``) but **untested
  against the live API** and requires an API key; treat as a stub until a
  live run is recorded in the engagement file.
* ``EpoOpsSource`` — EPO Open Patent Services: interface only (OAuth client
  credentials, CQL ``pa=`` applicant search). Raises NotImplementedError.

alpha-targets §4: expect near-zero patents for ASEAN banks and insurers;
report "0 found" as a finding, never as instrument level 1.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Protocol

import httpx

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import PeerRole, Subject
from ..textutil import AI_RE, AI_RE_CS

MODULE = "patents"
MAX_CLAIMS = 8
AI_CPC = re.compile(r"^(?:G06N|G06F\s?40|G06F\s?18|G06V|G10L\s?15|G06Q\s?(?:20|40))", re.I)


@dataclass
class PatentRecord:
    assignee: str
    number: str
    title: str
    abstract: str
    filing_date: Optional[date]
    grant_date: Optional[date]
    url: Optional[str]
    office: str = "USPTO"
    cpc: str = ""

    @property
    def ai_related(self) -> bool:
        text = f"{self.title}\n{self.abstract}"
        return bool(AI_RE.search(text) or AI_RE_CS.search(text) or any(AI_CPC.match(c.strip()) for c in self.cpc.split(";") if c.strip()))


class PatentSource(Protocol):
    def search(self, assignee_patterns: Iterable[str], since: date, until: date) -> list[PatentRecord]: ...


def _d(s: Optional[str]) -> Optional[date]:
    try:
        return date.fromisoformat(s[:10]) if s else None
    except Exception:
        return None


class CsvPatentSource:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def search(self, assignee_patterns: Iterable[str], since: date, until: date) -> list[PatentRecord]:
        pats = [p.lower() for p in assignee_patterns]
        out: list[PatentRecord] = []
        if not self.path.exists():
            return out
        with self.path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if pats and not any(p in (row.get("assignee") or "").lower() for p in pats):
                    continue
                fd, gd = _d(row.get("filing_date")), _d(row.get("grant_date"))
                ref = fd or gd
                if ref and not (since <= ref <= until):
                    continue
                out.append(PatentRecord(assignee=row["assignee"], number=row.get("number", ""), title=row.get("title", ""),
                                        abstract=row.get("abstract", ""), filing_date=fd, grant_date=gd, url=row.get("url") or None,
                                        office=row.get("office") or "CSV", cpc=row.get("cpc") or ""))
        return out


class PatentsViewSource:
    """USPTO PatentsView Search API (https://search.patentsview.org). UNTESTED
    against the live service; requires ``api_key``. Fields and endpoint follow
    the public documentation at the time of writing."""

    ENDPOINT = "https://search.patentsview.org/api/v1/patent/"

    def __init__(self, api_key: str, client: Optional[httpx.Client] = None):
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=30.0)

    def search(self, assignee_patterns: Iterable[str], since: date, until: date) -> list[PatentRecord]:
        out: list[PatentRecord] = []
        for pat in assignee_patterns:
            q = {"_and": [{"_contains": {"assignees.assignee_organization": pat}},
                          {"_gte": {"patent_date": since.isoformat()}}, {"_lte": {"patent_date": until.isoformat()}}]}
            body = {"q": q, "f": ["patent_id", "patent_title", "patent_abstract", "patent_date", "assignees.assignee_organization", "cpc_current.cpc_group_id"],
                    "o": {"size": 100}}
            r = self.client.post(self.ENDPOINT, json=body, headers={"X-Api-Key": self.api_key})
            r.raise_for_status()
            for p in r.json().get("patents", []) or []:
                out.append(PatentRecord(assignee=pat, number=p.get("patent_id", ""), title=p.get("patent_title", ""),
                                        abstract=p.get("patent_abstract", "") or "", filing_date=None, grant_date=_d(p.get("patent_date")),
                                        url=f"https://patents.google.com/patent/US{p.get('patent_id', '')}", office="USPTO",
                                        cpc=";".join(c.get("cpc_group_id", "") for c in (p.get("cpc_current") or []))))
        return out


class EpoOpsSource:
    """STUB: EPO Open Patent Services (OAuth2 client-credentials; CQL applicant
    search ``pa="<name>"``). Not implemented."""

    def __init__(self, consumer_key: str = "", consumer_secret: str = ""):
        self.consumer_key, self.consumer_secret = consumer_key, consumer_secret

    def search(self, assignee_patterns: Iterable[str], since: date, until: date) -> list[PatentRecord]:
        raise NotImplementedError("EpoOpsSource: not implemented; export OPS results to CSV and use CsvPatentSource")


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None,
        source: Optional[PatentSource] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    source = source or CsvPatentSource(ctx.subject_dir / "patents.csv")
    cp = ctx.checkpoint(MODULE)
    gaps: list[Gap] = []
    since = date(ctx.as_of.year - 5, 1, 1)  # five filing years: ASEAN FIs file rarely, so a 24-month window is mostly empty
    if not cp.has("_counts"):
        try:
            ctx.charge(MODULE, "patent_source", source=type(source).__name__, since=str(since), until=str(ctx.as_of))
            subj = source.search(subject.patterns(), since, ctx.as_of)
            peers = {p.name: source.search(p.name_patterns or [p.name], since, ctx.as_of) for p in subject.peers_by_role(PeerRole.core)}
        except NotImplementedError as e:
            gaps.append(Gap(module=MODULE, topic="patent source", detail=str(e), instrument_items=["D4.2"]))
            return ModuleResult(module=MODULE, subject_slug=subject.slug, gaps=gaps, data_available=False, tool_calls=ctx.budget(MODULE).calls)
        cp.put("_counts", {
            "subject": {"total": len(subj), "ai": sum(1 for r in subj if r.ai_related),
                        "records": [r.__dict__ | {"filing_date": str(r.filing_date), "grant_date": str(r.grant_date), "ai": r.ai_related} for r in subj]},
            "peers": {n: {"total": len(rs), "ai": sum(1 for r in rs if r.ai_related)} for n, rs in peers.items()},
            "source_available": True,
        })
    counts = cp.get("_counts")
    claims: list[ResearchClaim] = []
    ai_recs = [r for r in counts["subject"]["records"] if r["ai"] and r.get("url")][:MAX_CLAIMS]
    for r in ai_recs:
        key = f"p:{r['number']}"
        if cp.has(key):
            claims.extend(ResearchClaim.model_validate(c) for c in cp.get(key)["claims"])
            continue
        src = ctx.fetch(MODULE, r["url"])
        c = ResearchClaim(id=f"{subject.slug}.patent.{re.sub(r'[^A-Za-z0-9]+', '-', r['number'])}", module=MODULE, text=r["title"],
                          kind=ClaimKind.fact, load_bearing=False, sources=[r["url"]], passage=r["title"], tier=src.tier,
                          confidence_label=confidence_for_tier(src.tier), instrument_items=["D4.2", "D1.5"],
                          signal_ids=[f"{subject.slug}.patents.ai_count"], period=r.get("grant_date") or r.get("filing_date"),
                          note=f"{r['office']} {r['number']} assignee {r['assignee']}")
        cp.put(key, {"claims": [c.model_dump(mode="json")]})
        claims.append(c)
    src_desc = f"{type(source).__name__} ({getattr(source, 'path', '')})" if hasattr(source, "path") else type(source).__name__
    s = counts["subject"]
    signals = [
        Signal(id=f"{subject.slug}.patents.ai_count", module=MODULE, name="AI-related patents (5 filing years)", instrument_items=["D4.2", "D1.5"],
               value=s["ai"], unit="patents", source=src_desc, confidence_label=ConfidenceLabel.model_inferred,
               evidence_claim_ids=[c.id for c in claims], detail={"total_patents": s["total"], "peers": counts["peers"]},
               note="zero is a finding, not level 1 (ASEAN FIs rarely file); hiring and patent evidence outweigh narrative (P3/P9)"),
        Signal(id=f"{subject.slug}.patents.peer_ratio", module=MODULE, name="AI patents: subject vs core-peer median", instrument_items=["D4.2"],
               value=_ratio(s["ai"], [v["ai"] for v in counts["peers"].values()]), unit="x median", source=src_desc,
               confidence_label=ConfidenceLabel.model_inferred, detail={"peer_ai_counts": {n: v["ai"] for n, v in counts["peers"].items()}},
               note="BCG P4: future-built 3.5x patents"),
    ]
    if s["total"] == 0:
        gaps.append(Gap(module=MODULE, topic="no patents found", detail=f"no patents for {subject.patterns()} in {src_desc} since {since}; "
                        "confirm with IPOS / MyIPO / Google Patents before treating as zero", instrument_items=["D4.2"], verify_flag=True))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        data_available=counts.get("source_available", False), tool_calls=ctx.budget(MODULE).calls, detail=counts)


def _ratio(v: int, peers: list[int]) -> Optional[float]:
    if not peers:
        return None
    srt = sorted(peers)
    med = srt[len(srt) // 2] if len(srt) % 2 else (srt[len(srt) // 2 - 1] + srt[len(srt) // 2]) / 2
    if med == 0:
        return None  # ratio undefined when the peer median is zero; the detail dict carries the raw counts
    return round(v / med, 2)
