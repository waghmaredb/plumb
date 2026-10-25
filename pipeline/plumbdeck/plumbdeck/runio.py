"""Load a plumbresearch run folder (report.json, claims.json) into one read-only view.

The JSON written by plumbresearch / plumbverify is the contract; this module only
reads it. Nothing here decides whether a deck is final: see ``interlock.py``.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

ATTACHED_LABEL = "attached; publisher hash unreconciled"


class RunError(Exception):
    pass


@dataclass
class Claim:
    id: str
    text: str
    kind: str
    module: str
    confidence_label: Optional[str]
    tier: Optional[str]
    sources: list[str]
    page: Optional[int]
    released: bool
    labels: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    awaiting_reconciliation: bool = False
    gap_id: Optional[str] = None  # "G-n" when withheld
    attrs: dict[str, Any] = field(default_factory=dict)  # module metadata (plumbresearch findings: category, stage, …)
    note: Optional[str] = None


@dataclass
class Source:
    url: str
    tier: Optional[str]
    fetched_at: Optional[str]
    sha256: Optional[str]
    state: Optional[str]
    health_class: Optional[str]
    reconciliation: Optional[str]
    supplied_by: Optional[str]

    @property
    def date(self) -> Optional[str]:
        return self.fetched_at[:10] if self.fetched_at else None


def find_report(run: Path) -> Path:
    """Accept the folder holding report.json, or a parent with exactly one such subfolder."""
    run = Path(run)
    if run.is_file() and run.name == "report.json":
        return run
    if (run / "report.json").is_file():
        return run / "report.json"
    found = sorted(p for p in run.glob("*/report.json"))
    if len(found) == 1:
        return found[0]
    if not found:
        raise RunError(f"no report.json in {run}")
    raise RunError(f"several report.json under {run}: {[str(p) for p in found]}; pass one folder")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


class RunData:
    def __init__(self, run: Path):
        self.report_path = find_report(run)
        self.run_dir = self.report_path.parent
        self.report: dict[str, Any] = json.loads(self.report_path.read_text(encoding="utf-8"))
        claims_path = self.run_dir / "claims.json"
        self.claims_doc: dict[str, Any] = (
            json.loads(claims_path.read_text(encoding="utf-8")) if claims_path.is_file() else {}
        )
        self.verification: dict[str, Any] = self.report.get("verification") or {}
        self.metrics: dict[str, Any] = self.verification.get("metrics") or {}
        self.subject: dict[str, Any] = self.report.get("subject") or {}
        self.signals: list[dict[str, Any]] = list(self.report.get("signals") or [])
        f = self.report.get("findings") or {}
        # P5: observations (a search record, never a claim) and questions for management (shown only on released basis)
        self.observations: list[dict[str, Any]] = list(f.get("observations") or [])
        self.questions: list[dict[str, Any]] = list(f.get("questions") or [])
        self._load_sources()
        self._load_claims()

    # ------------------------------------------------------------------ basics
    @property
    def run_id(self) -> str:
        return str(self.report.get("run_id") or self.verification.get("run_id") or "unknown-run")

    @property
    def build_profile(self) -> Optional[str]:
        return self.report.get("build_profile") or self.verification.get("build_profile")

    @property
    def generated_date(self) -> str:
        g = self.report.get("generated_at") or self.verification.get("generated_at") or ""
        return g[:10] or "undated"

    @property
    def client(self) -> str:
        return self.subject.get("short_name") or self.subject.get("name") or "Client"

    @property
    def client_full(self) -> str:
        return self.subject.get("name") or self.client

    @property
    def slug(self) -> str:
        return self.subject.get("slug") or _slug(self.client)

    # ----------------------------------------------------------------- sources
    def _load_sources(self) -> None:
        self.sources: dict[str, Source] = {}
        for s in self.verification.get("sources") or []:
            prov = s.get("provenance") or {}
            src = Source(
                url=s.get("url"),
                tier=s.get("tier"),
                fetched_at=s.get("fetched_at"),
                sha256=s.get("sha256"),
                state=s.get("state"),
                health_class=s.get("health_class"),
                reconciliation=s.get("reconciliation"),
                supplied_by=prov.get("supplied_by"),
            )
            self.sources[src.url] = src
            if s.get("url_final"):
                self.sources.setdefault(s["url_final"], src)
        self.attached: list[dict[str, Any]] = list(self.report.get("attached_documents") or [])

    def doc_label(self, url: Optional[str]) -> str:
        if not url:
            return "unattributed source"
        for d in self.subject.get("documents") or []:
            if d.get("url") == url:
                kind = (d.get("kind") or "document").replace("_", " ")
                fy = f" FY{d['fy']}" if d.get("fy") else ""
                return f"{self.client_full} {kind}{fy}"
        for a in self.attached:
            if a.get("url") == url:
                kind = (a.get("kind") or a.get("document_key") or "document").replace("_", " ")
                fy = f" FY{a['fy']}" if a.get("fy") else ""
                return f"{self.client_full} {kind}{fy}"
        p = urlparse(url)
        tail = unquote(p.path.rstrip("/").rsplit("/", 1)[-1]) or p.netloc
        return f"{p.netloc} {tail}".strip()

    # ------------------------------------------------------------------ claims
    def _load_claims(self) -> None:
        extra = {c["id"]: c for c in (self.claims_doc.get("claims") or []) if "id" in c}
        pages: dict[str, int] = {}
        for c in self.verification.get("citations") or []:
            if c.get("page") is not None and c.get("claim_id") not in pages:
                pages[c["claim_id"]] = c["page"]
        decisions = {d["claim_id"]: d for d in self.verification.get("decisions") or []}
        released = set(self.report.get("released_claim_ids") or [])
        if not released and decisions:
            released = {k for k, d in decisions.items() if not d.get("blocked")}
        self.claims: dict[str, Claim] = {}
        base = self.verification.get("claims") or list(extra.values())
        for c in base:
            cid = c["id"]
            e = extra.get(cid, {})
            d = decisions.get(cid, {})
            srcs = list(c.get("sources") or e.get("sources") or [])
            tier = e.get("tier") or c.get("tier")
            if not tier and srcs and srcs[0] in self.sources:
                tier = self.sources[srcs[0]].tier
            self.claims[cid] = Claim(
                id=cid,
                text=c.get("text") or e.get("text") or "",
                kind=c.get("kind") or e.get("kind") or "claim",
                module=c.get("module") or e.get("module") or "",
                confidence_label=c.get("confidence_label") or e.get("confidence_label"),
                tier=tier,
                sources=srcs,
                page=pages.get(cid),
                released=(cid in released) and not d.get("blocked", False),
                labels=list(d.get("labels") or []),
                reasons=list(d.get("reasons") or []),
                awaiting_reconciliation=bool(d.get("withheld_awaiting_reconciliation")),
                attrs=dict(e.get("attrs") or c.get("attrs") or {}),
                note=e.get("note") or c.get("note"),
            )
        # gap numbering: order of the run's gap register, then any other withheld claim
        order: list[str] = []
        for g in (self.report.get("gap_register") or {}).get("blocked_claims") or []:
            if g.get("claim_id") not in order:
                order.append(g["claim_id"])
        for g in self.verification.get("gap_register") or []:
            if g.get("claim_id") not in order:
                order.append(g["claim_id"])
        for cid, cl in self.claims.items():
            if not cl.released and cid not in order:
                order.append(cid)
        self.gap_reasons: dict[str, list[str]] = {}
        for g in ((self.report.get("gap_register") or {}).get("blocked_claims") or []) + list(
            self.verification.get("gap_register") or []
        ):
            self.gap_reasons.setdefault(g["claim_id"], list(g.get("reasons") or []))
        self.withheld_ids: list[str] = [cid for cid in order if cid in self.claims and not self.claims[cid].released]
        for i, cid in enumerate(self.withheld_ids, 1):
            self.claims[cid].gap_id = f"G-{i}"
        self.released_ids: list[str] = [cid for cid, c in self.claims.items() if c.released]

    def claims_with_prefix(self, prefix: str) -> list[str]:
        """Claim ids starting with ``prefix`` in run order."""
        return [cid for cid in self.claims if cid.startswith(prefix)]

    def question(self, qid: str) -> Optional[dict[str, Any]]:
        return next((q for q in self.questions if q.get("id") == qid or str(q.get("id", "")).endswith("." + qid)), None)

    def observation(self, oid: str) -> Optional[dict[str, Any]]:
        return next((o for o in self.observations if o.get("id") == oid or str(o.get("id", "")).endswith("." + oid)), None)

    def claim(self, cid: str) -> Optional[Claim]:
        return self.claims.get(cid)

    def gap_ids(self, cids) -> list[str]:
        out = []
        for cid in cids:
            c = self.claims.get(cid)
            if c and c.gap_id and c.gap_id not in out:
                out.append(c.gap_id)
        return out

    # ----------------------------------------------------------------- signals
    def signal(self, sid: str) -> Optional[dict[str, Any]]:
        for s in self.signals:
            if s.get("id") == sid:
                return s
        return None

    def signal_by_suffix(self, suffix: str) -> Optional[dict[str, Any]]:
        for s in self.signals:
            if str(s.get("id", "")).endswith(suffix):
                return s
        return None

    def signal_withheld(self, s: dict[str, Any]) -> bool:
        if s.get("status") == "blocked":
            return True
        ev = s.get("evidence_claim_ids") or []
        return bool(ev) and all(self.claims.get(c) is not None and not self.claims[c].released for c in ev)

    # ---------------------------------------------------------------- peers
    def peers(self, role: Optional[str] = None) -> list[dict[str, Any]]:
        ps = self.subject.get("peers") or []
        return [p for p in ps if role is None or p.get("role") == role]

    def peer_for_claim(self, cid: str) -> Optional[dict[str, Any]]:
        m = re.search(r"\.peer\.size\.(.+)$", cid)
        if not m:
            return None
        for p in self.peers():
            if _slug(p.get("name", "")) == m.group(1):
                return p
        return None

    def claim_descriptor(self, cid: str) -> str:
        """A label for a claim that never repeats the claim's text or figures."""
        c = self.claims.get(cid)
        p = self.peer_for_claim(cid)
        if p:
            return f"Peer size: {p['name']}"
        if c is None:
            return cid
        if c.attrs.get("category") == "regulatory":
            return f"Regulatory clock: {c.attrs.get('instrument_short') or 'instrument'} ({c.attrs.get('clock') or 'milestone'})"
        tail = cid.rsplit(".", 1)[-1]
        page = f" (p. {c.page})" if c.page else ""
        kind = {"quote": "quotation", "number": "figure"}.get(c.kind, c.kind)
        return f"{c.module or 'run'} {kind} {tail}{page}"

    # ------------------------------------------------------------- run log
    def models_used(self) -> list[str]:
        """Model ids and regions from the run's inference log, when it can be found."""
        log = self.report.get("log")
        cands: list[Path] = [self.run_dir / "inference.jsonl"]
        if log:
            lp = Path(log)
            cands += [lp, self.run_dir / lp.name]
            for anc in [self.run_dir, *self.run_dir.parents]:
                cands.append(anc / "pipeline" / "plumbresearch" / lp)
                cands.append(anc / lp)
        for p in cands:
            try:
                if p.is_file():
                    seen: dict[str, set] = {}
                    for line in p.read_text(encoding="utf-8").splitlines():
                        try:
                            r = json.loads(line)
                        except ValueError:
                            continue
                        if r.get("run_id") not in (None, self.run_id):
                            continue
                        key = f"{r.get('model_id')} {r.get('model_version') or ''}".strip()
                        if r.get("model_id"):
                            seen.setdefault(key, set()).add(r.get("region_asserted") or "region not asserted")
                    if seen:
                        return [f"{k} ({', '.join(sorted(v))})" for k, v in sorted(seen.items())]
            except OSError:
                continue
        return []
