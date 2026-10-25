# plumbresearch

Phase 1 outside-in research modules for PLUMB (framework Phase 1, "outside-in
research sprint"; instrument `methodology/maturity-instrument.md` outside-in
proxies; verification spec `pipeline/verification-pipeline-spec.md` C10/C12).
Each module gathers one proxy-signal family for a subject, computes the derived
figure in code, and emits the evidence behind it as `plumbverify` claims with
provenance. The orchestrator runs every module under the C10 tool-call cap,
pushes every claim through `plumbverify.Verifier`, and writes the claim store,
signal table, peer-set exhibit and gap register. Rule-based, no model calls,
fully testable offline.

```
pip install -e ../plumbverify && pip install -e ".[test]"      # pyproject pins plumbverify by absolute path; see note below
plumbresearch run plumbresearch/fixtures/acme-bank/subject.yaml --out out --fixtures   # offline demo
pytest                                                          # 30 tests, no network
```

Exit code follows plumbverify: 0 when the build gate passes (zero BLOCKED
claims), 1 otherwise, 2 on usage errors (including `--cap` above the C10 hard
ceiling of 60).

## Layout

| Path | What it is |
|---|---|
| `subject.py` | `Subject`, `Peer`, `PeerSet`, `Document` models; YAML loader; `[VERIFY]` flags kept as `verify: true` fields and collected by `Subject.all_verify_items()` |
| `subjects/maybank.yaml`, `subjects/great-eastern.yaml` | the two G1 alpha subjects pre-filled from `docs/alpha-targets.md` (listing, tickers, IR URLs, FY, documents, size, core / secondary / exited peers with every `[VERIFY]` preserved) |
| `models.py` | `ResearchClaim` (plumbverify `Claim` + passage, tier, instrument items, signal ids), `Signal`, `Gap`, `ModuleResult`, `confidence_for_tier` |
| `context.py` | `RunContext` (store, log, fetcher, data dir, budget per module), `ToolBudget` / `ToolCapExceeded` (C10), `Checkpoint`, `ResearchFetcher` (plumbverify Fetcher + PDF line unwrapping), `LocalDocTransport` (serves local PDFs under their IR URL, and the fixture web) |
| `textutil.py` | AI-term lexicon, sentence splitter that unwraps hard-wrapped lines, NER-lite for organisation names, competitor-context patterns |
| `modules/annual_report.py` | 1–5 AI disclosure rubric, named-competitor extraction, leadership-structure extraction |
| `modules/postings.py` | AI-skill share of postings (24-month window, peer comparison), `PostingsSource` protocol, CSV implementation, lexicon |
| `modules/earnings_calls.py` | AI mentions per 1,000 words, prepared vs Q&A, `TranscriptSource` protocol, file implementation |
| `modules/patents.py` | AI patent counts, `PatentSource` protocol, CSV implementation, PatentsView client (untested), EPO OPS stub |
| `modules/peerset.py` | the funnel (size band, core/secondary, exited retained) and the Markdown protocol exhibit |
| `modules/financials.py` | KPI percentiles vs core peers from a CSV, economic-profit placeholder with explicit assumptions |
| `orchestrator.py` | module loop with cap / checkpoint / escalation, Verifier pass, signal status, output writers |
| `cli.py` | `plumbresearch run <subject.yaml> --out DIR [--data-dir DIR] [--fixtures] [--offline] [--cap N] [--modules a,b] [--as-of DATE]` |
| `fixtures/acme-bank/` | synthetic subject, fixture web (`web.yaml` → HTML/text files), postings.csv, transcripts/, patents.csv, financials.csv |
| `tests/` | rubric 1/3/5, postings arithmetic, call density, funnel, financials, PDF path, orchestrator end to end, C10 cap, CLI |

## Module → instrument items → spec criteria

| Module | Instrument proxy rows it implements | Signals (code-computed) | Claims it emits for the Verifier | Spec criteria touched |
|---|---|---|---|---|
| annual-report | D1.1 (annual-report 1–5 rubric, Yu et al. P2), D1.2 / D2.1 / D5.2 (CAIO/CDO titles), D1.4 (disclosed AI/technology spend), D5.4 (pilot vs production language), D6.1 (governance statements), D8.3 / D1.6 (quantified outcomes), D4.4 (board oversight), peer-seed step 1 (named competitors) | rubric level with component vector, mentions per 1,000 words, competitor names, leadership titles, spend statements | quotation claims for the sentences that triggered each rubric component, competitor sentences and leadership sentences (C5 exact match); number claims for disclosed investment figures (C4) | C1/C2 via plumbverify fetch, C4, C5, C8, C9 |
| postings | D4.1 (AI-skill share, Babina et al. P1), D2.2 / D2.3 (data-engineering postings), D3.1 / D3.2 (LLM, MLOps), D4.5 (AI product / translator), D6.2 (AI risk / governance roles) | 24-month share, first-12 vs last-12 months, monthly series, sub-lexicon counts, percentile vs core peers | up to 5 exemplar AI postings as fact claims (title) against the posting URL | C4, C9, C10 |
| earnings-calls | D1.1, D8.6 (earnings-call AI density, Fed AIR Index P3) | per-call and aggregate density, prepared vs Q&A split, Q&A share of mentions | up to 2 quotation claims per transcript (Q&A first) | C4, C5 |
| patents | D4.2, D1.5 (patents; BCG P4 3.5x) | AI-related count over 5 filing years, ratio to core-peer median | one fact claim per AI patent (title) against its URL | C4 |
| peer-set | instrument §5.5 peer set and n disclosure; framework funnel steps 4–6 | core count, band, demotions | number claims for peer sizes that have a source and an as-reported figure | — (no network; exhibit only) |
| financials | framework module 7 (KPI decomposition vs peers), ranking exhibit on economic profit; V1 context | percentile per KPI, economic profit per entity | number claims for every KPI value with a source; the subject's are load-bearing (C3 scorecard default) and therefore need two independent upstreams | C3 (load-bearing default), C4, C6, C9 |
| orchestrator | — | signal status from claim verdicts | — | C10 (cap 40, hard ceiling 60, checkpoint restart, escalation on second hit), C11 (gap register, build gate), C12/C13 (every module call logged to the hash chain with region asserted) |

Signals are not claims. Spec 3.1: "derived figures are computed in code, not
by the model". A signal's `status` is set by the orchestrator from the
Verifier's verdict on its evidence claims (`released`, `partial (k/n)`,
`blocked`, `computed` for a figure with no evidence claim of its own,
`not-available`). Instrument §5.4 applies to all of it: proxies corroborate,
never lift an item above level 3, and the alpha output is an "outside-in
pre-score, self-report absent".

### The annual-report rubric, exactly

Components extracted from the document text (AI sentences = sentences containing
a term from `textutil.AI_TERMS_*`):

| Component | Rule |
|---|---|
| mentions, density | count of AI-term matches; per 1,000 words (reported, not used for the level) |
| specificity | AI sentence naming a concrete function or use case (underwriting, claims, fraud, onboarding, contact centre, chatbot, pilot, …) |
| production | AI sentence with deployment language (rolled out, deployed, in production, live, scaled, embedded in …); pilot / PoC / exploring language without a deployment verb counts as `pilot_only` instead |
| quantified | AI sentence containing a number (%, currency, or a figure ≥ 10) and an outcome word (saving, reduced, productivity, revenue, hours, turnaround, …) |
| governance | AI sentence with responsible-AI / model-risk / FEAT / ISO 42001 / fairness / human-oversight language |
| ownership | AI sentence naming the board, a C-level AI/data title, the Group CEO, remuneration, KPI/scorecard or dated targets |
| investment | AI sentence with a currency amount and invest/spend/budget/commit language |

Level (first rule that fits): **L5** production ≥ 2 and quantified ≥ 2 and
governance ≥ 1 and ownership ≥ 1 · **L4** production ≥ 1 and specificity ≥ 2
and (quantified ≥ 1 or investment) · **L3** specificity ≥ 1 · **L2** mentions
≥ 3 · **L1** otherwise. The component vector and the triggering sentences are
written to `report.json` so two raters can run the instrument §7 κ test on the
same evidence pack. Tests pin three synthetic excerpts to 1, 3 and 5.

### Confidence labels (C9)

`confidence_for_tier`: T1/T2 → `filed`; T3 → `filed` (a figure a named
publisher reported; extension of the spec rule, documented here); T4 →
`vendor-estimate`; T5 or untiered → `model-inferred`. Every computed signal is
`model-inferred`.

## Real vs fixture-only

| Piece | Status |
|---|---|
| Rubric scoring, competitor and leadership extraction | real (regex/NER-lite rules over extracted text; no model) |
| HTML and PDF ingestion | real: plumbverify 0.2 fetch + hash + page-aware PDF extraction; this layer unwraps hard-wrapped PDF lines and writes the unwrapped text back to the evidence store (hash unchanged). Scanned PDFs (`needs_ocr`) surface as a gap |
| Local documents | real: a PDF placed in `data/<slug>/<local_file>` is served under its declared IR URL by `LocalDocTransport`; the citation of record stays the URL. Everything else goes to the network unless `--offline` |
| Postings share arithmetic, lexicon, window, peer percentile | real; **collection is fixture-only** (`CsvPostingsSource`). `MyCareersFutureSource` and `LinkedInJobsSource` raise `NotImplementedError` |
| Call density arithmetic, Q&A split | real; **transcripts are supplied as local text files** (`FileTranscriptSource` reading `transcripts/index.yaml`); no live provider |
| Patent counting, AI tagging (terms + CPC G06N/G06F40/G06V…) | real; `CsvPatentSource` is the working source; `PatentsViewSource` is written against the documented API shape but **untested against the live service**; `EpoOpsSource` is interface-only |
| Peer funnel steps 4–6, exhibit | real; steps 1–3 (seed, coverage lists, text similarity) are judgement recorded in the subject YAML per peer, plus step-1 names extracted from the annual report and flagged if missing from the long list |
| KPI percentiles, economic profit | real arithmetic; inputs are a hand-prepared CSV; no currency conversion (mixed-currency money KPIs are skipped with a gap); economic profit stays `not-available` until `EconomicProfitAssumptions.cost_of_equity` is set |
| C10 cap, checkpoints, restart, escalation | real (`ToolBudget`, `Checkpoint`, `run_module_with_cap`); tested with a synthetic over-budget module (spec T-08 in miniature) |
| Verification, gap register, hash-chain log | real, delegated to plumbverify (`Verifier`, `HashChainLog`) |
| Prompt-injection screening of ingested pages (C14), action classes (C15) | not implemented here; no model reads the pages, so no instruction channel exists in this layer |

Fixture web: `fixtures/acme-bank/web.yaml` maps URLs to local files; unknown
URLs return 404 so plumbverify classifies them DEAD. Zeta Bank's results page
is deliberately absent, which is why the end-to-end test expects exactly its
four KPI claims to be BLOCKED and everything else released.

## Running the two alpha subjects

1. Download the primary documents to `data/<slug>/` under the file names the
   subject YAML declares (`documents[].local_file`); they are served under the
   declared URL, so the citation of record is the IR URL, not the local path:

   ```
   data/maybank/maybank-integrated-annual-report-2025.pdf        # BankTrack mirror URL in the YAML is [VERIFY]: re-point to the maybank.com primary before release
   data/maybank/maybank-4q-fy2025-analyst-presentation.pdf
   data/maybank/maybank-integrated-ar-2024-part-2.pdf
   data/great-eastern/geh-annual-report-fy2025.pdf                # links.sgx.com returns 403 from the sandbox: download from a desktop
   data/great-eastern/geh-annual-report-fy2024.pdf
   ```

   Optional inputs in the same folder: `postings.csv` (columns `id, company,
   title, description, posted_at, url, location, source`), `transcripts/index.yaml`
   plus text files (rows `url, date, quarter, file, label`; use `label:
   "proxy-by-parent: OCBC"` for GEH), `patents.csv`, `financials.csv`
   (`entity, role, fy, currency, revenue, npat, total_assets, equity,
   cost_income, roe, source_urls, note`, money in millions, optional
   `<kpi>_as_reported` columns).

2. Run (network on for everything not local; results-release pages and peer
   size sources are fetched live):

   ```
   plumbresearch run plumbresearch/subjects/maybank.yaml --out out --data-dir data
   plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out --data-dir data
   ```

   Add `--offline` to see the gap register without touching the network, or
   `--modules annual-report,peer-set` to run a subset. Outputs land in
   `out/<slug>/`: `claims.json`, `report.json`, `peer-set.md`, `signals.md`,
   `gap-register.md`, `kpi-percentiles.md`, `inference.jsonl` (hash chain;
   check with `plumbverify verify-log out/<slug>/inference.jsonl`),
   `evidence/` (plumbverify store), `checkpoints/`.

3. Expect the build to FAIL on the first real run: peer size claims and
   KPI claims with a single upstream block by design, and every `[VERIFY]`
   item from alpha-targets prints in section 3 of the gap register. The
   alpha's G1 purpose is the pipeline and κ test, not a maturity result.

## Dependency note

`pyproject.toml` declares `plumbverify @ file:///home/claude/plumb/pipeline/plumbverify`
because PEP 508 direct references must be absolute. On another checkout run
`pip install -e ../plumbverify` first and the editable install satisfies the
requirement. Python 3.11+, pydantic 2, httpx, pyyaml; `pypdf` (or
`pdfminer.six`) is needed for PDFs and is also plumbverify 0.2's engine.

## Deviations and open items

1. `ResearchFetcher` rewrites `text_extract` for PDFs (unwrapped lines). The
   stored bytes and SHA-256 are untouched; the reviewer re-fetching per spec
   6.2 P4 compares the hash, not the extract. Fold the unwrapping into
   `plumbverify.extract` and delete the shim.
2. T3 figures are labelled `filed`; the spec names only T1/T2 for that label.
3. Peer-size claims and peer KPI claims are non-load-bearing ("directional");
   the subject's KPI claims are load-bearing and need two independent
   upstreams, so a single-source subject row blocks. That is the intended
   behaviour of the ranking exhibit, not a bug.
4. Posting, transcript and patent collection remain file-based; live sources
   need the data annex licences and a recorded terms-of-use check.
5. The funnel's text-similarity step (TNIC-style) is not computed; the
   subject YAML carries the reasoning per peer.
