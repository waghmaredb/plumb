"""End-to-end verification run (spec section 3.3, steps S2-S5).

S2 fetch + hash + health + tier + AI-gen/farm score
S3 match claims to passages, quotation check
S4 independence check for load-bearing numbers
S5 block-not-flag, gap register
Every step is written to the hash-chained log as a tool call.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import match as m
from . import semantic as sem
from .fetch import EvidenceStore, Fetcher
from .extract import page_of, split_passages_paged
from .log import HashChainLog
from .models import (
    Citation, CitationStatus, Claim, ClaimKind, HealthClass, Source, SourceState, Tier,
    VerificationReport,
)
from .policy import BUILD_PROFILES, DEFAULT_BUILD_PROFILE, BuildProfile, build_gate, decide
from .tier import TierRules, aigen_score, assign_tier, load_tier_rules
from .upstream import count_independent_upstreams, is_aggregator, trace_upstream

MODEL_ID = "plumbverify-rules"
MODEL_VERSION = "0.5.0"  # 0.4: build_profile / C2a (red-team review 2026-10-25, Blocker 2); 0.5: C4 fact verification (semantic.py)


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
        build_profile: BuildProfile = DEFAULT_BUILD_PROFILE,
    ):
        if build_profile not in BUILD_PROFILES:
            raise ValueError(f"build_profile must be one of {BUILD_PROFILES}, got {build_profile!r}")
        self.store = store
        self.fetcher = fetcher or Fetcher(store=store)
        self.log = log
        self.rules = tier_rules or load_tier_rules()
        self.semantic = semantic
        # 0.5: fact claims go through the C4 verifier (nli -> embedding -> offline, plus contradiction rules).
        # `semantic` may be None (default chain), a C4Verifier, a C4 backend, or a plain score-only SemanticMatcher.
        self.c4 = sem.C4Verifier.from_matcher(semantic, supported=supported_threshold, partial=partial_threshold)
        self.region = region
        self.quote_threshold = quote_threshold
        self.supported_threshold = supported_threshold
        self.partial_threshold = partial_threshold
        # C2a: "client" (default) blocks claims whose only support is an unreconciled attachment;
        # "internal" keeps the labelled path for drafts and sandbox runs
        self.build_profile: BuildProfile = build_profile
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
        c = self._cite(claim, src)
        if src.attached_label and c.status != CitationStatus.blocked:
            # 0.3: attached evidence is citable but visibly weaker until the publisher hash is reconciled
            c.labels.append(src.attached_label)
        return c

    def _cite(self, claim: Claim, src: Source) -> Citation:
        url = src.url
        if not src.citable:
            why = f"source not citable: state={src.state.value} health={src.health_class.value}"
            if src.reconciliation is not None and src.reconciliation.value == "MISMATCH":
                why = f"attached document does not match the publisher's bytes (reconcile MISMATCH; attached {(src.sha256 or '')[:16]}, publisher {(src.reconciled_sha256 or '')[:16]})"
            return Citation(claim_id=claim.id, source_url=url, status=CitationStatus.blocked,
                            reasons=[why + (f" ({src.error})" if src.error and "MISMATCH" not in why else "")])
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
            # 0.5: match number claims against sentence windows that contain the claim's figures
            # (layout lines split "SGD739.7" from "million" and starve the context score); fall back to passages
            win = _number_windows(claim.text, src.text_extract)
            if win:
                page_index = {**page_index, **{w: pg for w, pg in win if w not in page_index}}
            cand = [w for w, _ in win] or passages
            nm = m.number_claim_match(claim.text, cand, self.semantic if not isinstance(self.semantic, sem.C4Verifier) else None,
                                      self.supported_threshold)
            if nm.label == "unsupported" and win:
                nm = m.number_claim_match(claim.text, passages, None, self.supported_threshold)
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
            # 0.5: the C4 contradiction rules also apply to the passage the number matched in
            # ("reduced by 75%" vs "aims to reduce by approximately 75%", "grew 15%" vs "a decline of 15%")
            rules: list = []
            if nm.passage and status != CitationStatus.unverified:
                # evaluate on the sentence window that carries the claim's numbers, not on a layout line
                ctx = _number_context(claim.text, nm.passage, src.text_extract)
                rules = sem.contradiction_rules(claim.text, ctx)
            if any(r.effect == "contradiction" for r in rules):
                status = CitationStatus.unverified
                reasons.append("C4 contradiction rule(s): " + "; ".join(str(r) for r in rules if r.effect == "contradiction"))
            elif rules and status == CitationStatus.verified:
                status = CitationStatus.partial
                reasons.append("C4 rule(s) cap at PARTIAL: " + "; ".join(str(r) for r in rules))
            return Citation(claim_id=claim.id, source_url=url, passage=nm.passage, page=page_index.get(nm.passage),
                            match_score=round(nm.score, 4), status=status, reasons=reasons,
                            matcher="number-gate", rules_fired=[str(r) for r in rules])
        # 0.5: fact claims - C4 verifier over sentence windows (layout lines are too short to carry a claim)
        windows = sem.sentence_windows(src.text_extract)
        if not windows:
            windows = [(p.text, p.page) for p in paged]
        a = self.c4.best(claim.text, windows)
        status = {"supported": CitationStatus.verified, "partial": CitationStatus.partial,
                  "unsupported": CitationStatus.unverified}[a.label]
        if status != CitationStatus.verified:
            reasons.append(f"C4 {a.matcher} score {a.score:.2f} (raw {a.raw_score:.2f}; supported >= {self.supported_threshold}, "
                           f"partial >= {self.partial_threshold})")
            reasons.extend(f"C4 rule {r}" for r in a.rules)
        page = a.page if a.page is not None else (page_index.get(a.passage) or (
            page_of(src.text_extract, a.passage, m.normalize) if a.passage else None))
        return Citation(claim_id=claim.id, source_url=url, passage=a.passage, page=page,
                        match_score=round(a.score, 4), status=status, reasons=reasons, matcher=a.matcher,
                        backend_scores=a.backend_scores, rules_fired=a.rules_fired, decomposition=a.decomposition)

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
                        "score": c.match_score, "matcher": c.matcher, "backend_scores": c.backend_scores,
                        "rules_fired": c.rules_fired} for c in cites],
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
            d = decide(claim, cites, ind, pairs, build_profile=self.build_profile)
            decisions.append(d)
            self._log(run_id, "pipeline.policy", claim.text,
                      [{"tool": "block_not_flag", "claim_id": claim.id, "blocked": d.blocked, "reasons": d.reasons,
                        "build_profile": self.build_profile}],
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
            # 0.3: attached evidence. "unreconciled" = still ATTACHED (no MATCH yet); "mismatch" = publisher bytes differ
            "attached_sources": sum(1 for s in sources if s.provenance is not None),
            "attached_unreconciled": sum(1 for s in sources if s.state == SourceState.ATTACHED),
            "attached_mismatch": sum(1 for s in sources if s.reconciliation is not None and s.reconciliation.value == "MISMATCH"),
            "claims_on_unreconciled_attachments": len({c.claim_id for c in citations if any(
                l.startswith("attached;") for l in c.labels) and c.status != CitationStatus.blocked}),
            # 0.4 / C2a: claims a client build withheld solely because their attachment is unreconciled
            "withheld_awaiting_reconciliation": gate.withheld_awaiting_reconciliation,
            "released_claims": len(claims) - gate.blocked_count,
        }
        report = VerificationReport(run_id=run_id, generated_at=datetime.now(timezone.utc), build_profile=self.build_profile,
                                    sources=sources, claims=claims, citations=citations, decisions=decisions,
                                    gap_register=gate.gap_register, build_pass=gate.passed, metrics=metrics)
        self._log(run_id, "pipeline.run", run_id, [{"tool": "build_gate", "passed": gate.passed,
                                                    "blocked": gate.blocked_count, "build_profile": self.build_profile}],
                  outcome="PASS" if gate.passed else "FAIL", metrics=metrics)
        return report


def _number_windows(claim: str, text: str) -> list[tuple[str, object]]:
    """Sentence windows that contain every number literal of the claim (cheap prefilter before parsing)."""
    lits = [re.sub(r"[^\d.]", "", t.raw.split()[0] if t.raw.split() else t.raw).rstrip(".") for t in m.parse_numbers(claim)]
    lits = [re.sub(r"^[^\d]+", "", x) for x in lits if x]
    if not lits:
        return []
    out = []
    for w, page in sem.sentence_windows(text):
        flat = w.replace(",", "")
        if all(x in flat for x in lits):
            out.append((w, page))
    return out


def _number_context(claim: str, passage: str, text: str) -> str:
    """Sentence window around a number claim's matched passage: among windows that
    contain every claim number (and overlap the matched passage), the one with the
    best offline key-term score. Falls back to the passage itself."""
    norm_p = m.normalize(passage)[:60]
    best, best_s = passage, -1.0
    for w, _page in sem.sentence_windows(text):
        if norm_p not in m.normalize(w):
            continue
        if not m.number_in_passage(claim, w).passed:
            continue
        s = sem.key_term_recall(claim, w)[0]
        if s > best_s:
            best, best_s = w, s
    return best


def _rate(decisions) -> float:
    if not decisions:
        return 1.0
    return round(sum(1 for d in decisions if not d.blocked) / len(decisions), 4)


def load_claims(path: str | Path) -> list[Claim]:
    import json
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data["claims"] if isinstance(data, dict) else data
    return [Claim.model_validate(it) for it in items]
