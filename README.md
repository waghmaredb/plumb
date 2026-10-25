# PLUMB — Peer-ranked · Load-bearing · Upstream-verified · Maturity · Benchmark

**PLUMB** is the Verified Enterprise AI Journey Assessment. The name is the method: every score is **Peer-ranked** against a documented peer set; every **Load-bearing** number carries two independent **Upstream** sources; the **Maturity** instrument is calibrated so leaders are 5–10% of the **Benchmark**. A plumb line is how you check that something is actually true.

**Status:** v0.1 — G0 design-freeze candidate. Nothing here has been run on a real client. Every file carries its own status header and change-log.

**Change log:** 2026-10-25 — present-tense quality claims replaced with the design target and the measured state (red-team review 2026-10-25, Blocker 5 / §2.1); retainer renamed (review §4.5).

An AI-first consulting methodology and tool that researches a client and its competitors from public sources, scores enterprise AI maturity against peers, and produces three outputs:

1. **Why they exist** — the 3–5 distinctive capabilities that pass a six-criterion right-to-win test, tagged for the AI era.
2. **Where to improve** — the 3–5 value pools (make money / save money / avoid risk) from a driver tree and a 2–5 domain rule.
3. **Exactly which AI use cases** — scored, gated, tiered for risk, with a business case and an audit-ready evidence pack.

**Design target (not yet met):** every number in the deck traces to a fetched, hashed source, or it is not in the deck; every quotation string-matches its source; every load-bearing number has two independent upstreams; claims that cannot be verified are listed in the gap register, not hidden. **Current measured state** — first real run (`runs/great-eastern/2026-10-25-ar-attached/`): citation resolution 0.2 (1 of 5 sources, an unreconciled attachment), 1 extractor defect (leadership-title lexicon missed the client's MD of Data & AI), 4 of 5 peer-size claims withheld; no deck has yet passed QA gate 3 with a named independent reviewer. Until one has, the sentence we can stand behind is: *every claim we could not verify is listed, not hidden.*

The differentiator is not the AI; it is the **verification pipeline** (fetch-and-hash store, quotation string-match, two-independent-upstream rule, block-not-flag with a gap register) and the **compliance layer** (ISO 42001 / NIST AI RMF / MAS AIRM / EU AI Act / OWASP / ATLAS woven into scoring, gating and deliverables).

## Repository layout

```
docs/          Research reports that justify the design (3 files, ~350 sources)
methodology/   The engagement IP: maturity instrument, right-to-win kit, value & use-case kit
compliance/    Risk tiers & gates, evidence-pack templates, regulatory status map,
               control-library schema + CSV (CSA AICM v1.1-keyed crosswalk)
pipeline/      Verification pipeline spec + code: plumbverify (verification layer, 99 tests)
               and plumbresearch (Phase 1 outside-in modules + orchestrator, 46 tests)
instrument/    Maturity instrument as YAML + plumbscore scorer (46 tests)
runs/          Real-subject runs (internal artefacts; see each README's "Released / Withheld" line)
catalogue/     Use-case catalogue schema + 25 seed rows (APAC-weighted, with outcome metrics)
commercial/    Pricing ladder, engagement charter, engagement-letter clauses, DPA outline,
               conflict-check procedure
```

## Read in this order

| # | File | What it is |
|---|---|---|
| 1 | `docs/Next steps and path to GA gate.md` | Stage gates G0→GA, exit criteria, 30-day plan, decisions needed |
| 1b | `docs/product-next-steps.md` | Claude's product queue P1–P10 (runs without founder input) |
| 1a | `docs/founder-checklist.md` | Actions only the founder can do (identity, money, signature, network); product work lives everywhere else |
| 2 | `docs/AI first consulting engagement framework.md` | Why the methodology is shaped this way (maturity, right-to-win, value pools, use cases, deep-research failure modes, business model) |
| 3 | `docs/AI framework compliance standards layer.md` | Standards and regulation as of Oct 2026; tiering; evidence pack; the firm's own attestation path |
| 4 | `methodology/maturity-instrument.md` | 8 dims × 6 items × 5 levels + 4-item value axis; weights, bands, variance, outside-in proxies, κ test subset |
| 5 | `methodology/right-to-win-kit.md` | Six-criterion test, AI-era tag, hollowing check, 3 interview guides, LLM-mining protocol, output template |
| 6 | `methodology/value-and-use-case-kit.md` | Driver tree, domain screen, two-band sizing, use-case matrix (40/25/10/10/10 + hard gates), business-case template, failure-rate table |
| 7 | `compliance/risk-tiers-and-gates.md` | T0–T4 tiers, overrides, agent gate (reversibility classes, lethal trifecta), GO/NO-GO, signable checklist |
| 8 | `compliance/evidence-pack-templates.md` | 10 artefacts mapped to ISO 42001 / EU AI Act / MAS / NIST / AI Verify; transparency summary; AI-use disclosure wording |
| 9 | `compliance/regulatory-status-map.md` | ~95 instruments, binding / dated / voluntary / draft, with [VERIFY] flags |
| 10 | `compliance/control-library-schema.md` + `.csv` | Single AICM-keyed library with mapping columns; 40 seed controls (24 for the research agent, 16 for client agentic use cases) |
| 11 | `pipeline/verification-pipeline-spec.md` | Control objective PI-CV, 16 components, G1/GA thresholds, vendor rules, 30-claim reviewer sampling protocol |
| 12 | `catalogue/use-case-catalogue-seed.csv` | Schema + 25 seed rows |
| 13 | `methodology/ghost-deck-template.md` | Storyline rules, 34-slide ghost deck, QA gate 3 reviewer checklist, titles-only example |
| 14 | `commercial/` | Pricing ladder (Tier 1 Phase A / Phase B, Benchmark Refresh retainer), charter, letter clauses, DPA outline, conflict check (see its README) |
| 15 | `docs/red-team-review-2026-10-25.md` | Independent red-team review of the customer journey; the product-side fixes are applied across the files above and cited by finding number in each change log |

## Evidence discipline (applies to every file)

- Five source tiers (T1 regulator/primary/RCT → T5 aggregator, discovery only).
- Every URL in this repo was mechanically checked against the research notes; none were introduced from memory.
- Items the research could not confirm from a primary source are marked **[VERIFY]**, never silently estimated. The current [VERIFY] register is in `compliance/regulatory-status-map.md`.
- Numeric anchors marked "working value" (realisation discounts, intake-score thresholds) are placeholders to be recalibrated after three engagements.

## G0 exit checklist

- [x] Maturity instrument v0.1 written
- [x] Right-to-win kit v0.1 written
- [x] Value & use-case kit v0.1 written
- [x] Tier table, agent gate, gate checklist v0.1 written
- [x] Evidence pack templates v0.1 written
- [x] Regulatory status map v0.1 written
- [x] Control library schema + seed CSV v0.1 written
- [x] Verification pipeline spec v0.1 written
- [x] Use-case catalogue schema + seed written
- [x] Storyline ghost-deck template (action titles, horizontal-flow test)
- [x] Engagement charter, AI-use disclosure and engagement-letter clauses (`commercial/`)
- [x] Pricing ladder one-pager (`commercial/`)
- [ ] Decisions: wedge segment, build-vs-licence verification layer, G1 independent reviewer, attestation budget, entity
- [x] Verification: MAS AIRM primary text (7 Oct 2026 PDF) — section refs corrected across compliance/
- [~] Verification: AICM v1.1 — 18 domains/prefixes confirmed; 28/40 objective IDs confirmed from v1.0.3 rendering, 12 candidate; spreadsheet needs CSA login
- [ ] Verifications remaining: SS 680 / EDGE with Enterprise Singapore; AI TAP application requirements; LLM vendor Singapore routes + ZDR in writing

## Code status (G1 build)

| Package | What works | Fixture-only / stubbed |
|---|---|---|
| `pipeline/plumbverify` 0.4.0 | fetch+hash store, URL health, quote (exact) and claim matching, number normalisation, two-upstream independence, tiering, block-not-flag, build profiles (C2a: client builds withhold unreconciled attachments), hash-chained log, PDF extraction w/ OCR flag, Wayback, upstream tracing, reviewer report | semantic matcher (qualitative claims pass through a stub, so only number and quotation claims are machine-verified today), AI-gen classifier, OCR engine, 24h re-check job |
| `pipeline/plumbresearch` | annual-report rubric + competitor/leadership extraction (lexicon-based; one known miss, see runs/), peer funnel 0.3x–3x, postings share, call density, KPI percentiles, C10 cap/checkpoint, orchestrator → claims/report/peer-set/signals/gap register, `--profile client|internal` | posting/transcript/patent collection (CSV), economic profit until cost_of_equity set, funnel text-similarity step |
| `instrument/plumbscore` | cap rule, σ flags, ExCo gap, value axis, peer percentile (n≥15, within one population only), rank-within-named-peers when n<15, weighted κ, Markdown scorecard | Tier-0 web form |

Run the alphas: place the annual-report PDFs under `pipeline/plumbresearch/data/<subject>/` (file names in the subject YAML), then `plumbresearch run plumbresearch/subjects/maybank.yaml --out out --data-dir data`. Sandbox runs without egress use `--profile internal` and are internal artefacts; nothing is shown externally until a run has been executed with egress and `plumbverify reconcile` returns MATCH on every attachment.

## Top open items before G1 (alpha)

1. Log in to CSA, download the AICM v1.1 spreadsheet, confirm the 28 objective IDs and resolve the 12 `TBD [candidate]` rows in `control-library.csv`.
2. ~~Fetch the MAS AIRM PDF and correct section numbering~~ Done 2026-10-25. Residual: confirm the response-to-feedback paper qualifier (lifecycle controls for high-risk use cases "as soon as possible").
3. Confirm Singapore endpoints and zero-data-retention in writing for each LLM vendor before any client data enters the pipeline.
4. Pick the two alpha companies and build their peer sets per the documented funnel.
5. Run the 20-item κ subset of the maturity instrument with two raters.

## Licence

Proprietary — all rights reserved until decided otherwise.
