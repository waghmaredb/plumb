"""End-to-end verification run (spec section 3.3, steps S2-S5).

S2 fetch + hash + health + tier + AI-gen/farm score
S3 match claims to passages, quotation check
S4 independence check for load-bearing numbers
S5 block-not-flag, gap register
Every step is written to the hash-chained log as a tool call.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import match as m
from .fetch import EvidenceStore, Fetcher
from .extract import page_of, split_passages_paged
from .log import HashChainLog
from .models import (
    Citation, CitationStatus, Claim, ClaimKind, HealthClass, Source, SourceState, Tier,
    VerificationReport,
)
from .policy import build_gate, decide
from .tier import TierRules, aigen_score, assign_tier, load_tier_rules
from .upstream import count_independent_upstreams, is_aggregator, trace_upstream

MODEL_ID = "plumbverify-rules"
MODEL_VERSION = "0.2.0"


class Verifier:
    def __init__(
        self,
        fetcher: Optional[Fetcher] = None,
        store: Optional[EvidenceStore] = None,
        log: Optional[HashChainLog] = None,
        tier_rules: Optional[TierRules] = None,
        semantic: Optional[m.SemanticMatcher] = None,
        region: Optional[str] = "asia-southeast1",
        quote_threshold: float = m.QUOTE_THRESHOLD,
        supported_threshold: float = m.SUPPORTED_THRESHOLD,
        partial_threshold: float = m.PARTIAL_THRESHOLD,
    ):
        self.store = store
        self.fetcher = fetcher or Fetcher(store=store)
        self.log = log
        self.rules = tier_rules or load_tier_rules()
        self.semantic = semantic
        self.region = region
        self.quote_threshold = quote_threshold
        self.supported_threshold = supported_threshold
        self.partial_threshold = partial_threshold
        self._source_cache: dict[str, Source] = {}

    # -- logging helper ------------------------------------------------------
    def _log(self, run_id: str, caller: str, prompt: str, tool_calls: list[dict], outcome: str, **extra):
        if self.log is None:
            return
        self.log.log_inference(
            run_id=run_id, model_id=MODEL_ID, model_version=MODEL_VERSION, caller=caller,
            prompt=prompt, tool_calls=tool_calls, outcome=outcome, region_asserted=self.region,
            extra=extra or None,
        )

    # -- S2 ------------------------------------------------------------------
    def resolve_source(self, url: str, run_id: str) -> Source:
        if url in self._source_cache:
            return self._source_cache[url]
        src = self.fetcher.fetch(url)
        src.tier = assign_tier(src.url_final or url, self.rules).tier
        if src.state in (SourceState.FETCHED, SourceState.ARCHIVED):
            raw = self.store.get_raw(src.sha256) if (self.store and src.sha256) else None
            html = raw.decode("utf-8", errors="replace") if raw else None
            ag = aigen_score(src.url_final or url, html=html, text=src.text_extract, rules=self.rules, tier=src.tier)
            src.aigen_score, src.farm_score = ag.aigen_score, ag.farm_score
            if ag.rejected:
                src.state = SourceState.REJECTED_FARM if ag.signals.get("known_farm") or ag.farm_score >= ag.aigen_score else SourceState.REJECTED_AIGEN
                src.error = f"rejected (C7): {ag.reason}"
            elif not src.upstream_of and (is_aggregator(src.url_final or url) or src.tier == Tier.T5):
                # C6: surface ranked originals for the reviewer; they do not count until fetched+hashed
                tr = trace_upstream(src, html=html, rules=self.rules)
                src.upstream_candidates = [c.url for c in tr.candidates[:5]]
        self._log(run_id, "pipeline.resolve_source", url,
                  [{"tool": "fetch", "url": url, "status": src.http_status, "sha256": src.sha256,
                    "health": src.health_class.value, "tier": src.tier.value, "state": src.state.value}],
                  outcome=src.state.value)
        self._source_cache[url] = src
        return src

    # -- S3 ------------------------------------------------------------------
    def cite(self, claim: Claim, src: Source) -> Citation:
        url = src.url
        if not src.citable:
            return Citation(claim_id=claim.id, source_url=url, status=CitationStatus.blocked,
                            reasons=[f"source not citable: state={src.state.value} health={src.health_class.value}"
                                     + (f" ({src.error})" if src.error else "")])
        if src.needs_ocr:
            return Citation(claim_id=claim.id, source_url=url, status=CitationStatus.unverified,
                            reasons=[f"PDF ({src.page_count or '?'} pages) has no text layer; needs OCR before the claim can match (C1/C4)"])
        if not src.text_extract:
            return Citation(claim_id=claim.id, source_url=url, status=CitationStatus.unverified,
                            reasons=["source has no text extract (parse failure); claim cannot match (C1/C3)"])
        if claim.kind == ClaimKind.quote:
            q = m.quote_match(claim.text, src.text_extract, self.quote_threshold)
            status = CitationStatus.verified if q.passed else CitationStatus.blocked
            reasons = [] if q.passed else [f"quotation match {q.score:.3f} < {self.quote_threshold} (C5)"]
            if q.omitted_spans:
                reasons.append(f"ellipsis omitted spans logged: {q.omitted_spans}")
            page = page_of(src.text_extract, q.matched_text, m.normalize) if q.passed and q.matched_text else None
            return Citation(claim_id=claim.id, source_url=url, passage=q.matched_text, page=page, match_score=q.score,
                            status=status, reasons=reasons)
        paged = split_passages_paged(src.text_extract)
        passages = [p.text for p in paged]
        page_index = {p.text: p.page for p in paged}
        reasons: list[str] = []
        if claim.kind == ClaimKind.number:
            nm = m.number_claim_match(claim.text, passages, self.semantic, self.supported_threshold)
            if nm.check is None or not nm.check.claim_numbers:
                reasons.append("claim tagged as number but no number parsed from its text")
                status = CitationStatus.unverified
            elif nm.label == "unsupported":
                reasons.append("number(s) not found in any passage after normalisation: "
                               + ", ".join(t.raw for t in nm.check.missing) + " (C4)")
                status = CitationStatus.unverified
            elif nm.label == "partial":
                status = CitationStatus.partial
                reasons.append(f"number present but context overlap {nm.context_score:.2f} below "
                               f"{m.NUMBER_CONTEXT_THRESHOLD} and no semantic support")
            else:
                status = CitationStatus.verified
            return Citation(claim_id=claim.id, source_url=url, passage=nm.passage, page=page_index.get(nm.passage),
                            match_score=round(nm.score, 4), status=status, reasons=reasons)
        pm = m.claim_match(claim.text, passages, self.semantic, self.supported_threshold, self.partial_threshold)
        status = {"supported": CitationStatus.verified, "partial": CitationStatus.partial,
                  "unsupported": CitationStatus.unverified}[pm.label]
        if status != CitationStatus.verified:
            reasons.append(f"passage match {pm.score:.2f} (supported >= {self.supported_threshold}, partial >= {self.partial_threshold})")
        return Citation(claim_id=claim.id, source_url=url, passage=pm.passage, page=page_index.get(pm.passage),
                        match_score=round(pm.score, 4), status=status, reasons=reasons)

    # -- run -----------------------------------------------------------------
    def run(self, claims: list[Claim], run_id: Optional[str] = None) -> VerificationReport:
        run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        citations: list[Citation] = []
        decisions = []
        for claim in claims:
            srcs = [self.resolve_source(u, run_id) for u in claim.sources]
            cites = [self.cite(claim, s) for s in srcs]
            citations.extend(cites)
            self._log(run_id, "pipeline.cite", claim.text,
                      [{"tool": "match", "claim_id": claim.id, "source": c.source_url, "status": c.status.value,
                        "score": c.match_score} for c in cites],
                      outcome="matched")
            # S4
            ind = 0
            pairs = []
            if claim.kind == ClaimKind.number and claim.load_bearing:
                verified_srcs = [s for s, c in zip(srcs, cites) if c.status == CitationStatus.verified]
                uc = count_independent_upstreams(verified_srcs)
                ind, pairs = uc.count, uc.pairs
                self._log(run_id, "pipeline.upstream", claim.text,
                          [{"tool": "independence", "claim_id": claim.id, "independent_upstreams": ind,
                            "accepted": uc.accepted}], outcome="counted")
            # S5
            d = decide(claim, cites, ind, pairs)
            decisions.append(d)
            self._log(run_id, "pipeline.policy", claim.text,
                      [{"tool": "block_not_flag", "claim_id": claim.id, "blocked": d.blocked, "reasons": d.reasons}],
                      outcome="BLOCKED" if d.blocked else d.status.value)
        gate = build_gate(claims, decisions)
        sources = list(self._source_cache.values())
        lb_numbers = [d for d, c in zip(decisions, claims) if c.kind == ClaimKind.number and c.load_bearing]
        metrics = {
            "claims": len(claims),
            "sources": len(sources),
            "citations": len(citations),
            "blocked_claims": gate.blocked_count,
            "citation_resolution_rate": round(sum(1 for s in sources if s.citable) / len(sources), 4) if sources else 1.0,
            "quotation_pass_rate": _rate([d for d, c in zip(decisions, claims) if c.kind == ClaimKind.quote]),
            "two_upstream_coverage": round(sum(1 for d in lb_numbers if d.independent_upstreams >= 2) / len(lb_numbers), 4) if lb_numbers else 1.0,
            "aigen_or_farm_cited": sum(1 for s in sources if s.state in (SourceState.REJECTED_AIGEN, SourceState.REJECTED_FARM)
                                       and any(c.source_url == s.url and c.status == CitationStatus.verified for c in citations)),
        }
        report = VerificationReport(run_id=run_id, generated_at=datetime.now(timezone.utc), sources=sources,
                                    claims=claims, citations=citations, decisions=decisions,
                                    gap_register=gate.gap_register, build_pass=gate.passed, metrics=metrics)
        self._log(run_id, "pipeline.run", run_id, [{"tool": "build_gate", "passed": gate.passed,
                                                    "blocked": gate.blocked_count}],
                  outcome="PASS" if gate.passed else "FAIL", metrics=metrics)
        return report


def _rate(decisions) -> float:
    if not decisions:
        return 1.0
    return round(sum(1 for d in decisions if not d.blocked) / len(decisions), 4)


def load_claims(path: str | Path) -> list[Claim]:
    import json
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data["claims"] if isinstance(data, dict) else data
    return [Claim.model_validate(it) for it in items]
