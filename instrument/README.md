# instrument/ — machine-readable maturity instrument + scorer

**Status: v0.2, mirrors `methodology/maturity-instrument.md` v0.2 (2026-10-25).** The YAML is a transcription, not a second source of truth: when the markdown changes, regenerate or re-diff the YAML (`tests/test_instrument_yaml.py` fails if questions, anchors, evidence classes, weights, the κ subset, the † single-proxy marks or the §5.6 decision register drift). The scorer reads `instrument-v0.2.yaml` by default; `instrument-v0.1.yaml` is kept for history (`--instrument instrument-v0.1.yaml` loads it, but the v0.2 scoring rules below apply to either file).

Change log:
- 2026-10-25 — benchmark `population` flag, no-pooling rule and rank-within-named-peers exhibit (red-team review 2026-10-25, Blocker 3); 46 tests.
- 2026-10-25 — **v0.2** (product item P2): the 12 transcription ambiguities resolved as instrument decisions (md §5.6, YAML `decisions_v0_2`). Scorer: organisation item score = **median** of capped responses (mean secondary); I class counts only with ≥2 verifiable interviewees (`interviewees` column or ≥2 distinct interview refs); self-view computed beside the evidenced view; V2 numeric shares mapped with upper-inclusive edges; region required in benchmark rows. D3.5/D6.6 re-anchored (technical vs governance). Harbourline example 42.6 → 43.6 (Emerging both); 75 tests.

```
instrument/
├── instrument-v0.2.yaml      48 capability items, 4 value items, weights, bands, scoring rules, κ subset, v0.2 decisions (default)
├── instrument-v0.1.yaml      v0.1 transcription, kept for history
├── plumbscore/               Python package (pydantic + pyyaml; numpy not required)
│   ├── instrument.py         load + validate the YAML
│   ├── responses.py          load respondent CSV
│   ├── scoring.py            per-response cap rule, I(≥2) check, median item score, self-view/evidenced view, bands, variance, value axis
│   ├── benchmark.py          peer percentile (n≥15 rule, population split, rank-within-named-peers fallback, disclosure)
│   ├── kappa.py              quadratic-weighted Cohen's κ on the 20-item subset
│   ├── scorecard.py          Markdown scorecard (S08 incl. self-view vs evidenced view, S09–S11)
│   └── cli.py                `plumbscore score …`, `plumbscore kappa …`
├── examples/                 synthetic, clearly fictional inputs and the outputs they produce
├── tests/                    pytest (75 tests)
└── pyproject.toml
```

## Run

```bash
cd instrument
pip install -e ".[test]"            # or just: pip install pydantic pyyaml
plumbscore score examples/responses_harbourline_fictional.csv \
    --benchmark examples/benchmark_synthetic_40.csv \
    --sector banking --size-band large --region SG \
    --org "Harbourline Mutual Bank (fictional)" \
    --out scorecard.md --json scorecard.json
plumbscore kappa examples/rater_a.csv examples/rater_b.csv
python -m pytest -q
```

`python -m plumbscore …` works without installing.

## Input formats

**Responses CSV** — one row per respondent × item.

| column | values |
|---|---|
| `respondent_id` | pseudonymous id (never a name) |
| `role_group` | `exco` or `operating` |
| `role` (optional) | job title used for the "roles at each extreme" output (§5.3) |
| `item_id` | `D1.1`…`D8.6`, or `V1`…`V4` |
| `score` | integer 1–5 for D items; for V items the band code / level on that item's scale (`A/B/C`, `<12%`/`12–39%`/`40–61%`/`≥62%`, 1–5, 0–4). V2 also accepts a numeric share (`45.5` or `45.5%`), mapped with upper-inclusive edges p < 12 · 12 ≤ p ≤ 39 · 39 < p ≤ 61 · p > 61 (decision 8) |
| `evidence_class` | `D`, `S`, `I`, `O`, `none`; two classes joined with `+` (e.g. `D+S`) when the item's Ev≥4 column requires both |
| `evidence_ref` | artefact id in the evidence register |
| `interviewees` (optional) | integer: independent interviewees covered by the row's interview reference. An `I` class counts only when the item's rows show ≥2 interviewees — this column ≥2, or ≥2 distinct `evidence_ref` values on rows carrying `I` (v0.2 decision 11) |

**Benchmark CSV** — `org_id, sector, size_band, region, D1…D8, total, [evidence_gated 0/1], [as_of], [population self|evidenced]`. Dimension scores and total on 0–100. `region` is required in every row (v0.2 decision 7) even though it is only an optional peer filter; the loader refuses a file without it.

| `population` | Who is in it | How it was scored |
|---|---|---|
| `self` | Tier-0 free web-form entries | Self-scored, every item capped at 3, no evidence register, respondent self-selected |
| `evidenced` | Engagement entries | Evidence-gated by an assessor against a logged evidence register (§5.4) |

**These are two different populations and must never be pooled into one percentile** (red-team review 2026-10-25, Blocker 3 / §2.3). A `self` entry cannot exceed C = 50, so pooling would push every evidenced organisation up the distribution and make a capped pool look like a peer set. `peer_percentile` raises if the set is mixed and no population is named; `plumbscore score --population` defaults to `evidenced` (the engagement case). When the column is absent the loader derives it from `evidence_gated` (1 → `evidenced`, 0 → `self`); untagged rows belong to neither population and are excluded when one is named.

**Peer n below 15.** A percentile is not reported. The scorecard's S09 instead shows the **rank within the named peers (n disclosed)**, each peer's capability and dimension values visible, and the standing line "global, peer n insufficient". No global percentile is substituted. This is the Tier-1 exhibit for Singapore FI peer sets (typically n = 9) until the evidenced benchmark reaches n ≥ 15 for the segment.

**Rater CSVs (κ)** — `org_id, item_id, score`, one file per rater.

## Mapping to the instrument sections

| Instrument section | Where it lives |
|---|---|
| §1 structure, level semantics, evidence classes | `yaml: structure, level_semantics, evidence_classes, evidence_class_rule` |
| §2 dimensions and weights | `yaml: dimensions` (sum validated = 100 at load) |
| §3 48 items: Q, L1–L5, Ev≥4, κ membership, outside-in proxies | `yaml: items[]` — `question`, `anchors`, `evidence_class_required` (+ verbatim `_text`), `kappa_subset`, `outside_in_proxies[{signal, validation}]` |
| §4 value axis V1–V4, value gap flag | `yaml: value_axis`; `scoring._score_value_axis` |
| §5.1 item → dimension → total, ≥4-of-6 rule, renormalisation, rounding | `scoring.score_responses` |
| §5.2 bands, 50-line production boundary | `yaml: bands`; `scoring.band_for` |
| §5.3 σ before cap, σ>1.0 flag, roles at extremes, alignment index, ExCo gap | `scoring.score_responses` (ItemResult / DimensionResult) |
| §5.4 cap rule, interview rule, evidence coverage, self-report-dominant | `scoring.apply_cap`; `evidence_coverage` on the result |
| §5.5 peer percentile, n≥15, fallback label, disclosure | `benchmark.peer_percentile` |
| §7 κ subset, κw thresholds, exit criterion | `yaml: kappa`; `kappa.kappa_report` |
| Ghost deck S08 / S09 / S10 / S11 | `scorecard.render_scorecard` sections (S12 is regulatory, not instrument-derived) |

## v0.2 decisions as implemented

The v0.1 scorer carried interim choices for 12 ambiguities. v0.2 makes each an instrument rule (md §5.6; YAML `decisions_v0_2`); the scorer implements them as follows.

| # | Decision | Scorer |
|---|---|---|
| 1 | Band edges upper-inclusive on the unrounded score: ≤25 · >25–≤50 · >50–≤75 · >75 | `scoring.band_for`; YAML `bands.list[].interval` |
| 2 | Cap per response, before aggregation | `scoring.apply_cap` on every row; σ still on raw levels (§5.3) |
| 3 | Organisation item score = median of capped responses (even n → midpoint, e.g. 2.5); mean secondary | `ItemResult.score` (median capped), `score_self` (median raw), `mean_capped` / `mean_raw` (secondary); dimension mean = mean of item medians |
| 4 | 1–4 proxies; 10 single-proxy items marked †; D8.1/D8.2 split | YAML `structure.single_proxy_items`; test checks the † marks |
| 5 | D4.4 follows Ev≥4: I (≥2) + O | YAML `evidence_class_required: [I, O]` |
| 6 | Percentile ties mid-rank | `benchmark.percentile_rank` |
| 7 | Region optional filter, required in benchmark rows | `benchmark.load_benchmark` raises without it |
| 8 | V2 edges upper-inclusive | `ValueItem.band_for_share`; numeric V2 responses mapped |
| 9 | Target shares 15 / 45 / 32.5 / 7.5 = 100% | YAML `bands.list[].target_share`; example benchmark 6 / 18 / 13 / 3 matches |
| 10 | V1 ↔ D8.4 kept (only cross-item dependency) | checked on the D8.4 organisation item score (median) |
| 11 | I (≥2) verifiable from rows | `scoring.interview_count`; unverified `I` neither lifts nor counts toward evidence coverage |
| 12 | D3.5 technical controls, D6.6 governance of agents; no overlap | anchors in YAML; test checks no technical term in D6.6 and no governance term in D3.5 |

Remaining scorer conventions (not instrument rules): an item is "scored" for the ≥4-of-6 rule if it has at least one response; value-axis consensus is the mode of recorded values, ties to the lower band.

## What the free Tier-0 web form must enforce (§5.4, §9 item 5)

The self-scored web version has no evidence register, so:

- Every item is displayed and stored at **min(self-report, 3)** (per response, decision 2). A respondent may pick 4 or 5, but the recorded and displayed level is 3 and the row is flagged `capped`. Screen one states the rule and links the "What changed for respondents (v0.2)" box in the instrument.
- The same applies to the value axis: V1 is recorded Band A "not evidenced"; V2 at most `12–39%`; V3 at most 3; V4 at most 2.
- Capability score is therefore ≤ 50.0 and the band ≤ Emerging for any self-only entry; the scorecard prints **"self-report-dominant"** (evidence coverage 0%).
- Outside-in proxies may pre-populate a draft score or challenge it downward; they never lift above 3.
- Entries from the free form are stored in the benchmark with `evidence_gated = 0`, so the §5.5 disclosure ("share of peer entries evidence-gated vs self-scored") stays honest.
- Variance outputs need ≥5 respondents from the same organisation; below that, show the min–max range, not σ.

## Examples

All example data is synthetic. **Harbourline Mutual Bank does not exist.** `examples/generate_examples.py` (seed 20261025) writes:

- `responses_harbourline_fictional.csv` — 12 respondents (5 ExCo, 7 operating) × 48 items + V1–V4. Built so that ExCo over-rate D2/D4/D5 (gap > 0.75), several items cross σ > 1.0, ExCo claim 4–5 without evidence (cap), two-class items carry only one class (still capped: D1.4 D-only, D2.6 D-only, D4.4 I-only), and a handful of items carry qualifying evidence (lift). Result under v0.2: **43.6 / Emerging** (evidenced view; self-view 47.7 / Emerging), evidence coverage 25% (self-report-dominant), V1 A (not evidenced) · V2 12–39% · V3 3 · V4 2. Under the v0.1 scorer (mean of capped rows) the same responses scored 42.6; the +1.0 is entirely the median rule (D2 +6.9, D3 +3.1, D4 +1.7, D5 +6.2, D6 −1.4, D7 +1.4, D8 −7.3, D1 −0.3 points). The CSV is unchanged from v0.1 apart from the new `interviewees` column (D4.4 records two interviewees; still capped because O is missing).
- `benchmark_synthetic_40.csv` — 40 fictional organisations. Stratified by target band 6 / 18 / 13 / 3 (15% / 45% / 32.5% / 7.5%, Leading inside the 5–10% window). Per organisation: a latent total drawn uniformly inside the band, dimension scores = latent + N(0, 9) clipped to 0–100 and rounded to 0.1, total recomputed exactly as the §2 weighted sum; redraw if the recomputed total leaves the band. 17 rows are `banking × large × SG`, all `population = evidenced`, so the example peer set clears n ≥ 15 inside the evidenced population; `--sector insurance --size-band mid` demonstrates the rank-within-named-peers fallback. The remaining rows are ~40% `evidenced`, the rest `self`.
- `rater_a.csv`, `rater_b.csv` — 12 fictional organisations × the 20 κ-subset items; rater B disagrees by one level ~18% of the time (~45% on D1.1, D4.1, D7.3).
- `scorecard_harbourline.md` / `.json` — the outputs of the command above.
