# plumbverify

First working scaffold of PLUMB's verification layer (decision D2: build in-house).
Implements the engineering side of `../verification-pipeline-spec.md` (PI-CV v0.1)
as a pip-installable Python package. Rule-based, offline-testable, no model calls.

```
pip install -e .            # or: pip install -e ".[test,extract]"
plumbverify verify claims.json --out report.json [--store DIR] [--log FILE] [--tiers tiers.yaml] [--archive]
plumbverify check-url https://example.org/page [--archive]
plumbverify verify-log .plumbverify/inference.jsonl
pytest                      # 59 tests, fully offline (httpx.MockTransport)
```

`verify` exits 0 when the build gate passes (zero BLOCKED claims) and 1 otherwise;
blocked claims and their reasons are printed and written to `gap_register` in the report.
See `examples/claims.json` for the input shape.

## Modules

| Module | Purpose | Spec component |
|---|---|---|
| `models.py` | `Source`, `Claim`, `Citation`, `ClaimDecision`, `VerificationReport`, enums for tier / health / state / confidence label | 3.1 state model |
| `fetch.py` | `Fetcher` (20 s timeout, 3 retries at 2/8/32 s, 25 MB cap, declared UA), `EvidenceStore` (sqlite index + raw bytes keyed by SHA-256, immutable), `check_health` (HEAD then GET, LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED), `ArchiveProvider` interface with `NullArchive` and a `WaybackArchive` stub | C1, C2 |
| `extract.py` | main-text extraction (trafilatura when installed, bs4 fallback), passage splitting | feeds C3/C4 |
| `match.py` | quotation exact / near-exact match with ellipsis handling; claim-to-passage lexical match with `SemanticMatcher` plug-in; number parsing and number-in-passage check (commas, %, currency prefixes, k/m/bn/tn scale words); number-claim matcher | C4, C5 |
| `upstream.py` | registrable-domain logic, aggregator list, independence test (domain, content hash, near-duplicate text, upstream terminus), greedy independent-upstream count, `trace_to_original` placeholder | C6 |
| `tier.py` | T1-T5 assignment from `tiers.yaml` (overridable by path or dict), AI-generated / content-farm heuristic scorer | C7, C8 |
| `policy.py` | block-not-flag decision, build gate, gap register, confidence-label lint | C9, C11 |
| `log.py` | append-only JSONL with SHA-256 chaining, `log_inference` (model version, prompt hash, tool calls, outcome, region), `verify()` | C12, C13 |
| `pipeline.py` | `Verifier.run()` orchestrates S2-S5 and logs each step | 3.3 |
| `cli.py` | `verify`, `check-url`, `verify-log` | - |

## Thresholds (v0.1 defaults, G1 calibration pending)

| Constant | Value | Meaning |
|---|---|---|
| `QUOTE_THRESHOLD` | 1.0 | rapidfuzz ratio for a quotation; exact substring after Unicode/whitespace/smart-quote normalisation scores 1.0 |
| `SUPPORTED_THRESHOLD` | 0.85 | claim-to-passage score at or above which a citation is `verified` (spec SUPPORTED) |
| `PARTIAL_THRESHOLD` | 0.70 | 0.70-0.85 is `partial`; below is `unverified` |
| `NUMBER_CONTEXT_THRESHOLD` | 0.60 | keyword recall required around a found number when no semantic matcher is set |
| `CONTENT_SIMILARITY_THRESHOLD` | 0.90 | two sources whose text ratio is at or above this are treated as one upstream |
| `REJECT_THRESHOLD` | 0.70 | combined AI-gen or farm score at or above this rejects the page (hard signals reject regardless) |
| `MIN_INDEPENDENT_UPSTREAMS` | 2 | required for every load-bearing number |
| `TRACE_DEPTH_CAP` | 3 | hops allowed when tracing an aggregator to its original |

### G1 alpha exit thresholds this scaffold reports against (spec section 4)

| Metric | G1 | Where it comes from |
|---|---|---|
| Citation resolution rate | 100% | `metrics.citation_resolution_rate` (share of fetched sources that are citable) |
| Quotation exact-match | 100% | `metrics.quotation_pass_rate` |
| Two-upstream coverage | >= 90% | `metrics.two_upstream_coverage` |
| AI-generated or farm pages cited | 0 | `metrics.aigen_or_farm_cited` |
| Log integrity | pass | `plumbverify verify-log` |
| Blocked-claim overrides | reported | not implemented: no override path exists in v0.1, so the count is 0 by construction |
| Fact-support rate (load-bearing) >= 95%, (all) >= 90% | reviewer sampling | reviewer worksheet, outside this package |

## How the package maps to spec criteria C1-C16 and control rows CL-001 to CL-024

| Spec | Control row | Status in v0.1 | Where |
|---|---|---|---|
| C1 Fetcher + hash store | CL-001 | working: SHA-256 over raw bytes, final URL after redirects, fetch timestamp, immutable raw store, sqlite index, hash re-verification | `fetch.Fetcher.fetch`, `fetch.EvidenceStore` |
| C2 URL health + retry + archive | CL-002 | working: HEAD then GET, 3 retries with 2/8/32 s backoff, LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED, DEAD and LIKELY_HALLUCINATED never citable. Stubbed: Wayback lookup (`WaybackArchive`, interface only, untested), two-egress-IP retry, 24 h pre-release re-check job | `fetch.Fetcher.check_health`, `models.Source.citable` |
| C3 Claim extraction | CL-003 | not implemented: claims arrive pre-extracted in `claims.json` with `kind` and `load_bearing` set by the caller. The load-bearing default rules (exec summary, scorecards, value pools, business cases) are not coded yet | - |
| C4 Claim-to-passage match | CL-003 | working (lexical): rapidfuzz partial_ratio with 0.85 / 0.70 bands; number claims gated on number presence with unit; `SemanticMatcher` protocol defaults to `None` | `match.claim_match`, `match.number_claim_match`, `match.number_in_passage` |
| C5 Quotation exact match | CL-004 | working: normalisation, exact substring, ellipsis fragments with omitted spans logged; failure routes to BLOCKED not UNSUPPORTED | `match.quote_match`, `policy.decide` |
| C6 Two-independent-upstream | CL-005, CL-006 | working: independence by registrable domain, content hash, near-duplicate ratio and upstream terminus; aggregators (statista, wikipedia, PR wires, market-report mills) and T5 never count until traced. Placeholder: `trace_to_original` only reads a declared `upstream_of` list, does not follow citations in the page | `upstream.py` |
| C7 AI-gen / content-farm rejection | CL-007 | stub: hard signals work (self-declared AI generation, known-farm list); soft signals (author, outbound references, ad/affiliate density, boilerplate ratio) are weighted heuristics; AI-text classifier, publication velocity, domain age and duplicate ratio are recorded as `-1` (not implemented). Soft rejection applies to T4/T5 only | `tier.aigen_score` |
| C8 Source tier | CL-008 | working: YAML rule table, longest-domain-match-wins, host and path patterns, overridable | `tier.assign_tier`, `tiers.yaml` |
| C9 Confidence labels | CL-009 | partial: label is a typed field on `Claim`; a number claim without a label is blocked (export lint). Automatic label derivation from tier (T1/T2 = filed, T4 = vendor-estimate) and `causal_label` are not implemented | `models.ConfidenceLabel`, `policy.decide` |
| C10 Bounded tool-call depth | CL-010 | not implemented (belongs to the agent runtime, not this layer) | - |
| C11 Block-not-flag | CL-011 | working: BLOCKED claims fail the build, gap register written, released set excludes them; no warning-footnote path exists | `policy.decide`, `policy.build_gate`, `policy.released_claims` |
| C12 Per-inference logging | CL-012 | working for this layer's own calls: model id/version, caller, prompt SHA-256 (raw prompt never written), tool calls, outcome, `region_asserted`. Sentence-level traceability of a deck is out of scope here | `log.HashChainLog.log_inference`, `pipeline.Verifier._log` |
| C13 Tamper-evident retention | CL-013 | working: append-only JSONL (O_APPEND + fsync), SHA-256 chain, `verify()` detects edit, deletion and reorder. Stubbed: daily segment seal, 90-day retention policy, separate write-only credentials | `log.py`, `plumbverify verify-log` |
| C14 Prompt-injection controls | CL-014 | not implemented | - |
| C15 Action classes / lethal trifecta | CL-015, CL-016 | not implemented (gateway concern) | - |
| C16 Independent reviewer protocol | CL-022 | not implemented; the report gives the reviewer the claim store, passages, hashes and tiers the protocol needs | `VerificationReport` |
| V1-V8 vendor rules | CL-017 to CL-021, CL-023, CL-024 | out of scope for this package; `region_asserted` is logged per record as the hook for CL-017 | `log.py` |

Test IDs from spec section 6.1 covered in miniature: T-01 (hash determinism, redirect capture), T-02 (LIVE / DEAD / ARCHIVED / LIKELY_HALLUCINATED on fixtures), T-04 (altered and paraphrased quotations fail), T-05 (shared-upstream pairs rejected, independent pairs accepted), T-07 (tier rules), T-09 (one blocked claim fails the build and appears in the gap register), T-11 (out-of-band edit detected). T-03, T-06, T-08, T-10, T-12 to T-15 need labelled sets or runtime components that do not exist yet.

## Deliberate deviations from the spec

1. **Quotation threshold is 1.0 (spec-strict).** Exact substring after Unicode/whitespace/smart-quote normalisation is required. A looser threshold can be passed to `quote_match(..., threshold=)` or `Verifier(quote_threshold=)` for exploratory runs only; release runs must use 1.0.
2. **Unclassified domains default to T5, not T4.** Spec C8 says unclassifiable domains default to T4 pending reviewer decision; the brief said "else T5". T5 is the safer default because T5 can never be a citation of record. Change `default:` in `tiers.yaml` to `T4` to follow the spec.
3. **Number-claim context score.** Spec C4 gates number claims on number presence plus a semantic match at 0.85. With no embedding model chosen (open item 2) the lexical partial_ratio scores paraphrased number claims around 0.6, so the scaffold uses number presence (hard) plus keyword recall >= 0.60 (soft) when no `SemanticMatcher` is configured. When one is configured, semantic >= 0.85 applies.
4. **Soft C7 signals do not reject T1-T3 pages.** Spec rejects any page at or above 0.70. The soft heuristics are too crude to stay inside the 5% false-rejection budget for T1-T3, so only hard signals apply there until the classifier exists.
5. **Claim status names.** The brief's `verified | partial | unverified | blocked` are used for `Citation.status` and `ClaimDecision.status`; they correspond to the spec's SUPPORTED / PARTIAL / UNSUPPORTED / BLOCKED.

## Stubbed or placeholder (summary)

- `fetch.WaybackArchive` (interface implemented, untested, off by default; `--archive` enables it)
- `upstream.trace_to_original` (reads declared `upstream_of`; does not crawl citations)
- `tier.aigen_score` classifier signals (`ai_classifier`, `publication_velocity`, `domain_age`, `duplicate_ratio` reported as -1)
- `extract.extract_main_text` for PDFs (returns empty string, so PDF-backed claims cannot match yet)
- `match.SemanticMatcher` (protocol only; default `None`)
- C3 claim extraction, C10 depth cap, C14 injection controls, C15 action classes, C16 reviewer worksheet, 24 h pre-release re-check, retention/segment sealing

## Input format

```json
{"claims": [
  {"id": "exec-01", "module": "executive-summary", "text": "...", "kind": "number|quote|fact",
   "load_bearing": true, "confidence_label": "filed|vendor-estimate|model-inferred|interview-anecdote",
   "sources": ["https://...", "https://..."]}
]}
```

Report: `VerificationReport` JSON with `sources` (url, url_final, fetched_at, sha256, tier, health_class, state, archived_url, aigen_score, farm_score), `citations` (claim_id, source_url, passage, match_score, status, reasons), `decisions`, `gap_register`, `build_pass`, `metrics`.
