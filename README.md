# PLUMB — Peer-ranked · Load-bearing · Upstream-verified · Maturity · Benchmark

**PLUMB** is the Verified Enterprise AI Journey Assessment. The name is the method: every score is **Peer-ranked** against a documented peer set; every **Load-bearing** number carries two independent **Upstream** sources; the **Maturity** instrument is calibrated so leaders are 5–10% of the **Benchmark**. A plumb line is how you check that something is actually true.

**Status:** v0.1 — G0 design-freeze candidate. Nothing here has been run on a real client. Every file carries its own status header and change-log.

An AI-first consulting methodology and tool that researches a client and its competitors from public sources, scores enterprise AI maturity against peers, and produces three outputs at Big-4 quality with every citation verified:

1. **Why they exist** — the 3–5 distinctive capabilities that pass a six-criterion right-to-win test, tagged for the AI era.
2. **Where to improve** — the 3–5 value pools (make money / save money / avoid risk) from a driver tree and a 2–5 domain rule.
3. **Exactly which AI use cases** — scored, gated, tiered for risk, with a business case and an audit-ready evidence pack.

The differentiator is not the AI; it is the **verification pipeline** (every citation resolves, every quote string-matches its source, every load-bearing number has two independent upstreams, unverifiable claims are blocked not flagged) and the **compliance layer** (ISO 42001 / NIST AI RMF / MAS AIRM / EU AI Act / OWASP / ATLAS woven into scoring, gating and deliverables).

## Repository layout

```
docs/          Research reports that justify the design (3 files, ~350 sources)
methodology/   The engagement IP: maturity instrument, right-to-win kit, value & use-case kit
compliance/    Risk tiers & gates, evidence-pack templates, regulatory status map,
               control-library schema + CSV (CSA AICM v1.1-keyed crosswalk)
pipeline/      Verification pipeline spec (Processing Integrity control + engineering spec)
catalogue/     Use-case catalogue schema + 25 seed rows (APAC-weighted, with outcome metrics)
commercial/    (empty) pricing ladder, engagement letter, AI-use disclosure — next
```

## Read in this order

| # | File | What it is |
|---|---|---|
| 1 | `docs/Next steps and path to GA gate.md` | Stage gates G0→GA, exit criteria, 30-day plan, decisions needed |
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
- [ ] Storyline ghost-deck template (action titles, horizontal-flow test)
- [ ] Engagement charter, AI-use disclosure and engagement-letter clauses (`commercial/`)
- [ ] Pricing ladder one-pager (`commercial/`)
- [ ] Decisions: wedge segment, build-vs-licence verification layer, G1 independent reviewer, attestation budget, entity
- [ ] Verifications: MAS AIRM primary text; SS 680 / EDGE with Enterprise Singapore; AI TAP application requirements; AICM v1.1 objective IDs; LLM vendor Singapore routes + ZDR in writing

## Top open items before G1 (alpha)

1. Load the CSA AICM v1.1 spreadsheet and fill the TBD objective IDs in `control-library.csv`.
2. Fetch the MAS AI Risk Management Guidelines PDF (7 Oct 2026) and correct section numbering in the tier table and evidence pack.
3. Confirm Singapore endpoints and zero-data-retention in writing for each LLM vendor before any client data enters the pipeline.
4. Pick the two alpha companies and build their peer sets per the documented funnel.
5. Run the 20-item κ subset of the maturity instrument with two raters.

## Licence

Proprietary — all rights reserved until decided otherwise.
