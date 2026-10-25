# plumbverify 0.2.0

PLUMB's verification layer (decision D2: build in-house). Implements the
engineering side of `../verification-pipeline-spec.md` (PI-CV v0.1) as a
pip-installable Python package. Rule-based, offline-testable, no model calls.

```
pip install -e .            # or: pip install -e ".[test,extract,pdf-fallback]"
plumbverify verify claims.json --out report.json [--store DIR] [--log FILE] [--tiers tiers.yaml] [--archive] [--archive-save]
plumbverify check-url https://example.org/page [--archive] [--archive-save]
plumbverify verify-log .plumbverify/inference.jsonl
plumbverify report report.json --format md [--out report.md] [--seed N] [--sample-min 30]
pytest                      # 84 tests, fully offline (httpx.MockTransport)
```

`report --format md` renders the reviewer-facing Markdown: a claim table
(claim, module, kind, load-bearing, status, score, tier, independent upstreams,
source locator with `p. N` for PDFs, reasons), the gap register, the source
table (hash, pages / needs-OCR, 24 h re-check deadline, upstream candidates)
and the section 6.2 sampling worksheet skeleton (P1 eligibility, P4 per-claim
rows, P5 C7 agreement, P6 totals, P7 decision). The sample is stratified per
P3 and drawn with a recorded random seed, so `--seed N` reproduces it.
`--format json` pretty-prints the report. Exit code mirrors the build gate.

### What changed in 0.2.0

- PDF text extraction (pypdf, pdfminer.six fallback), page-aware passages, `Citation.page` / `Citation.locator` ("p. N"), `Source.needs_ocr` for scanned PDFs, magic-byte content-type detection (`Source.detected_content_type`).
- `WaybackArchive`: real availability-API lookup with the 24-month window, opt-in Save Page Now (`save_missing=True` / `--archive-save`), injectable `httpx.Client`; `recheck_after` (24 h, spec C2) on `ArchiveSnapshot`, `HealthResult` and `Source`.
- `upstream.trace_upstream` / `find_upstream_candidates`: crawl-based aggregator tracing from outbound links and attribution patterns ("according to", "source:", "study by"...), ranked, with a `max_hops=2` guard; the pipeline records `Source.upstream_candidates` for aggregator / T5 pages (advisory, never counted until fetched and hashed).
- `plumbverify report` subcommand and `report.py` (`render_markdown`, `build_sample`).

`verify` exits 0 when the build gate passes (zero BLOCKED claims) and 1 otherwise;
blocked claims and their reasons are printed and written to `gap_register` in the report.
See `examples/claims.json` for the input shape.

## Modules

| Module | Purpose | Spec component |
|---|---|---|
| `models.py` | `Source`, `Claim`, `Citation`, `ClaimDecision`, `VerificationReport`, enums for tier / health / state / confidence label | 3.1 state model |
| `fetch.py` | `Fetcher` (20 s timeout, 3 retries at 2/8/32 s, 25 MB cap, declared UA), `EvidenceStore` (sqlite index + raw bytes keyed by SHA-256, immutable), `check_health` (HEAD then GET, LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED, `recheck_after` = +24 h), `ArchiveProvider` interface with `NullArchive` and `WaybackArchive` (availability API, 24-month window, opt-in save) | C1, C2 |
| `extract.py` | `sniff_content_type` (magic bytes beat headers), HTML main-text extraction (trafilatura when installed, bs4 fallback), PDF extraction (`extract_pdf`: pypdf then pdfminer.six, per-page text, `needs_ocr` for scanned files), `extract_document`, page-aware `split_passages_paged` and `page_of` | feeds C1/C3/C4 |
| `match.py` | quotation exact / near-exact match with ellipsis handling; claim-to-passage lexical match with `SemanticMatcher` plug-in; number parsing and number-in-passage check (commas, %, currency prefixes, k/m/bn/tn scale words); number-claim matcher | C4, C5 |
| `upstream.py` | registrable-domain logic, aggregator list, independence test (domain, content hash, near-duplicate text, upstream terminus), greedy independent-upstream count, `find_upstream_candidates` (outbound links + attribution patterns, ranked), `trace_upstream` (max 2 hops, terminus must be non-aggregator T1-T3), `trace_to_original` (declared `upstream_of` first, crawl second) | C6 |
| `tier.py` | T1-T5 assignment from `tiers.yaml` (overridable by path or dict), AI-generated / content-farm heuristic scorer | C7, C8 |
| `policy.py` | block-not-flag decision, build gate, gap register, confidence-label lint | C9, C11 |
| `log.py` | append-only JSONL with SHA-256 chaining, `log_inference` (model version, prompt hash, tool calls, outcome, region), `verify()` | C12, C13 |
| `pipeline.py` | `Verifier.run()` orchestrates S2-S5 and logs each step | 3.3 |
| `report.py` | `render_markdown` (reviewer table + 6.2 worksheet), `build_sample` (seeded, stratified a/b/c/d per P3, RELEASED frame only) | C16, 6.2 |
| `cli.py` | `verify`, `check-url`, `verify-log`, `report` | - |

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
| `TRACE_DEPTH_CAP` | 3 | hops allowed when walking *declared* `upstream_of` chains with a resolver (spec C6 cap) |
| `MAX_TRACE_HOPS` | 2 | pages the crawl-based tracer may follow from an aggregator (stricter than the spec cap because each hop fetches an untrusted page) |
| `RECHECK_WINDOW` | 24 h | spec C2: a LIVE / ARCHIVED classification is stale after `recheck_after`; the S6 pre-release re-check must run inside this window |
| `ARCHIVE_MAX_AGE_DAYS` | 730 | Wayback snapshot must be within 24 months |
| `OCR_MIN_CHARS_PER_PAGE` | 20 | PDFs averaging fewer text characters per page are flagged `needs_ocr` |
| `SAMPLE_MIN` / `MIN_PER_MODULE` / `MIN_QUALITATIVE` | 30 / 2 / 5 | 6.2 P3 sample composition |

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
| C2 URL health + retry + archive | CL-002 | working: HEAD then GET, 3 retries with 2/8/32 s backoff, LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED, DEAD and LIKELY_HALLUCINATED never citable; Wayback availability lookup with 24-month window and opt-in Save Page Now (`WaybackArchive`, MockTransport-tested, off by default); `recheck_after` (24 h) recorded on every LIVE / ARCHIVED result. Stubbed: two-egress-IP retry, the S6 scheduled re-check job itself (the deadline is recorded, nothing runs it yet) | `fetch.Fetcher.check_health`, `fetch.WaybackArchive`, `fetch.recheck_deadline`, `models.Source.citable` |
| C3 Claim extraction | CL-003 | not implemented: claims arrive pre-extracted in `claims.json` with `kind` and `load_bearing` set by the caller. The load-bearing default rules (exec summary, scorecards, value pools, business cases) are not coded yet | - |
| C4 Claim-to-passage match | CL-003 | working (lexical): rapidfuzz partial_ratio with 0.85 / 0.70 bands; number claims gated on number presence with unit; `SemanticMatcher` protocol defaults to `None`; passages are page-aware for PDFs so citations carry `page` | `match.claim_match`, `match.number_claim_match`, `match.number_in_passage`, `extract.split_passages_paged` |
| C5 Quotation exact match | CL-004 | working: normalisation, exact substring, ellipsis fragments with omitted spans logged; failure routes to BLOCKED not UNSUPPORTED | `match.quote_match`, `policy.decide` |
| C6 Two-independent-upstream | CL-005, CL-006 | working: independence by registrable domain, content hash, near-duplicate ratio and upstream terminus; aggregators (statista, wikipedia, PR wires, market-report mills) and T5 never count until traced; crawl-based tracing ranks outbound links by attribution context, tier and URL shape, follows at most 2 hops, accepts only a non-aggregator T1-T3 terminus. Partial: the pipeline records ranked `upstream_candidates` on aggregator sources but does not yet auto-fetch and hash the terminus to promote it to the citation of record (a declared `upstream_of` is still the only way a terminus counts) | `upstream.trace_upstream`, `upstream.find_upstream_candidates`, `pipeline.Verifier.resolve_source` |
| C7 AI-gen / content-farm rejection | CL-007 | stub: hard signals work (self-declared AI generation, known-farm list); soft signals (author, outbound references, ad/affiliate density, boilerplate ratio) are weighted heuristics; AI-text classifier, publication velocity, domain age and duplicate ratio are recorded as `-1` (not implemented). Soft rejection applies to T4/T5 only | `tier.aigen_score` |
| C8 Source tier | CL-008 | working: YAML rule table, longest-domain-match-wins, host and path patterns, overridable | `tier.assign_tier`, `tiers.yaml` |
| C9 Confidence labels | CL-009 | partial: label is a typed field on `Claim`; a number claim without a label is blocked (export lint). Automatic label derivation from tier (T1/T2 = filed, T4 = vendor-estimate) and `causal_label` are not implemented | `models.ConfidenceLabel`, `policy.decide` |
| C10 Bounded tool-call depth | CL-010 | not implemented (belongs to the agent runtime, not this layer) | - |
| C11 Block-not-flag | CL-011 | working: BLOCKED claims fail the build, gap register written, released set excludes them; no warning-footnote path exists | `policy.decide`, `policy.build_gate`, `policy.released_claims` |
| C12 Per-inference logging | CL-012 | working for this layer's own calls: model id/version, caller, prompt SHA-256 (raw prompt never written), tool calls, outcome, `region_asserted`. Sentence-level traceability of a deck is out of scope here | `log.HashChainLog.log_inference`, `pipeline.Verifier._log` |
| C13 Tamper-evident retention | CL-013 | working: append-only JSONL (O_APPEND + fsync), SHA-256 chain, `verify()` detects edit, deletion and reorder. Stubbed: daily segment seal, 90-day retention policy, separate write-only credentials | `log.py`, `plumbverify verify-log` |
| C14 Prompt-injection controls | CL-014 | not implemented | - |
| C15 Action classes / lethal trifecta | CL-015, CL-016 | not implemented (gateway concern) | - |
| C16 Independent reviewer protocol | CL-022 | partial: `plumbverify report --format md` renders the claim table and the 6.2 worksheet skeleton (P1, P4, P5, P6, P7 sections) with a seeded, stratified 30-claim sample from the RELEASED frame; the reviewer's live re-fetch, hash check and labelling remain manual, and the signed worksheet is filed outside this package | `report.render_markdown`, `report.build_sample` |
| V1-V8 vendor rules | CL-017 to CL-021, CL-023, CL-024 | out of scope for this package; `region_asserted` is logged per record as the hook for CL-017 | `log.py` |

Test IDs from spec section 6.1 covered in miniature: T-01 (hash determinism, redirect capture, magic-byte type detection), T-02 (LIVE / DEAD / ARCHIVED / LIKELY_HALLUCINATED on fixtures, Wayback lookup / stale / save paths), T-04 (altered and paraphrased quotations fail), T-05 (shared-upstream pairs rejected, independent pairs accepted, aggregator traced to a T1 original, max-hops guard), T-07 (tier rules), T-09 (one blocked claim fails the build and appears in the gap register), T-11 (out-of-band edit detected), plus PDF page-tagged citations and a scanned PDF routed to `needs_ocr`. T-03, T-06, T-08, T-10, T-12 to T-15 need labelled sets or runtime components that do not exist yet.

## Deliberate deviations from the spec

1. **Quotation threshold is 1.0 (spec-strict).** Exact substring after Unicode/whitespace/smart-quote normalisation is required. A looser threshold can be passed to `quote_match(..., threshold=)` or `Verifier(quote_threshold=)` for exploratory runs only; release runs must use 1.0.
2. **Unclassified domains default to T5, not T4.** Spec C8 says unclassifiable domains default to T4 pending reviewer decision; the brief said "else T5". T5 is the safer default because T5 can never be a citation of record. Change `default:` in `tiers.yaml` to `T4` to follow the spec.
3. **Number-claim context score.** Spec C4 gates number claims on number presence plus a semantic match at 0.85. With no embedding model chosen (open item 2) the lexical partial_ratio scores paraphrased number claims around 0.6, so the scaffold uses number presence (hard) plus keyword recall >= 0.60 (soft) when no `SemanticMatcher` is configured. When one is configured, semantic >= 0.85 applies.
4. **Soft C7 signals do not reject T1-T3 pages.** Spec rejects any page at or above 0.70. The soft heuristics are too crude to stay inside the 5% false-rejection budget for T1-T3, so only hard signals apply there until the classifier exists.
5. **Claim status names.** The brief's `verified | partial | unverified | blocked` are used for `Citation.status` and `ClaimDecision.status`; they correspond to the spec's SUPPORTED / PARTIAL / UNSUPPORTED / BLOCKED.

## Working vs stubbed (0.2.0)

| Area | Status | Notes |
|---|---|---|
| Fetch, hash, immutable store | working | C1 |
| Health classes, retry/backoff | working | C2 |
| Wayback lookup (24-month window) | working, off by default | `--archive`; `WaybackArchive(client=...)` for tests |
| Wayback save | working, double opt-in | `--archive-save` / `save_missing=True` |
| 24 h re-check rule | recorded only | `recheck_after` on Source / HealthResult / ArchiveSnapshot; no scheduler runs the S6 re-check |
| Two-egress-IP retry | not implemented | single client |
| HTML extraction | working | trafilatura optional |
| PDF extraction, page tags | working | pypdf (core dep), pdfminer.six fallback (`pdf-fallback` extra) |
| Scanned PDFs | flagged | `needs_ocr=True`; no OCR engine is wired in |
| Content-type sniffing | working | magic bytes for PDF/HTML/images/zip/gzip |
| Quotation match | working | threshold 1.0 |
| Claim / number match | working (lexical) | `SemanticMatcher` protocol only |
| Tier rules | working | `tiers.yaml` |
| AI-gen / farm | hard signals only | soft signals heuristic; classifier, velocity, domain age, duplicate ratio = -1 |
| Independence test | working | |
| Aggregator tracing | working from HTML/text | ranked candidates, max 2 hops; pipeline stores `upstream_candidates` but does not auto-fetch the terminus |
| Block-not-flag, gap register | working | C11 |
| Hash-chained log | working | segment sealing, retention, write-only creds not implemented |
| Reviewer Markdown + 6.2 worksheet | working (skeleton) | seeded stratified sample; reviewer labels are filled by hand |
| C3 claim extraction, C10 depth cap, C14 injection controls, C15 action classes | not implemented | outside this layer |

## Input format

```json
{"claims": [
  {"id": "exec-01", "module": "executive-summary", "text": "...", "kind": "number|quote|fact",
   "load_bearing": true, "confidence_label": "filed|vendor-estimate|model-inferred|interview-anecdote",
   "sources": ["https://...", "https://..."]}
]}
```

Report: `VerificationReport` JSON with `sources` (url, url_final, fetched_at, sha256, tier, content_type, detected_content_type, page_count, needs_ocr, recheck_after, health_class, state, archived_url, aigen_score, farm_score, upstream_of, upstream_candidates), `citations` (claim_id, source_url, passage, page, match_score, status, reasons), `decisions`, `gap_register`, `build_pass`, `metrics`. Render it for reviewers with `plumbverify report report.json --format md`.
