# instrument/ — machine-readable maturity instrument + scorer

**Status: v0.1, mirrors `methodology/maturity-instrument.md` v0.1 (2026-10-25).** The YAML is a transcription, not a second source of truth: when the markdown changes, regenerate or re-diff the YAML (`tests/test_instrument_yaml.py` fails if questions, anchors, evidence classes, weights or the κ subset drift).

Change log: 2026-10-25 — benchmark `population` flag, no-pooling rule and rank-within-named-peers exhibit (red-team review 2026-10-25, Blocker 3); 46 tests.

```
instrument/
├── instrument-v0.1.yaml      48 capability items, 4 value items, weights, bands, scoring rules, κ subset
├── plumbscore/               Python package (pydantic + pyyaml; numpy not required)
│   ├── instrument.py         load + validate the YAML
│   ├── responses.py          load respondent CSV
│   ├── scoring.py            cap rule, item/dimension/total, bands, variance, value axis
│   ├── benchmark.py          peer percentile (n≥15 rule, population split, rank-within-named-peers fallback, disclosure)
│   ├── kappa.py              quadratic-weighted Cohen's κ on the 20-item subset
│   ├── scorecard.py          Markdown scorecard (S08–S11)
│   └── cli.py                `plumbscore score …`, `plumbscore kappa …`
├── examples/                 synthetic, clearly fictional inputs and the outputs they produce
├── tests/                    pytest (46 tests)
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
| `score` | integer 1–5 for D items; for V items the band code / level on that item's scale (`A/B/C`, `<12%`/`12–39%`/`40–61%`/`≥62%`, 1–5, 0–4) |
| `evidence_class` | `D`, `S`, `I`, `O`, `none`; two classes joined with `+` (e.g. `D+S`) when the item's Ev≥4 column requires both |
| `evidence_ref` | artefact id in the evidence register |

**Benchmark CSV** — `org_id, sector, size_band, [region], D1…D8, total, [evidence_gated 0/1], [as_of], [population self|evidenced]`. Dimension scores and total on 0–100.

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

## Scorer decisions where the markdown is silent or ambiguous

Each is also recorded as a `note:` in the YAML.

1. **Band edges.** The band table is integer-edged (0–25 / 26–50 / 51–75 / 76–100) but §5.1 assigns the band on the unrounded value, so the scorer uses upper-inclusive edges: ≤25 Stagnating, ≤50 Emerging, ≤75 Scaling, >75 Leading. This matches the worked check (50.0 = top of Emerging; Scaling needs an average above level 3) but conflicts with "Leading (≥76)" for 75 < C < 76.
2. **Cap applied per response.** §5.4 speaks of the "consensus self-report"; §1 of "self-reported scores". The scorer caps each row before averaging (the stricter reading, and what the web form must do). σ is computed on raw levels before the cap, as §5.3 requires.
3. **Consensus = mean of capped rows.** The markdown never says how 10–30 respondents become one item score. Value-axis consensus is the mode of recorded values, ties to the lower band.
4. **Percentile rank = mid-rank**: 100 × (below + 0.5 × equal) / n.
5. **An item is "scored"** for the ≥4-of-6 rule if it has at least one response.
6. **"I (≥2)"** cannot be verified from one row; an `I` in `evidence_class` is the assessor's record that two independent interviewees agreed and both references are logged.

## What the free Tier-0 web form must enforce (§5.4, §9 item 5)

The self-scored web version has no evidence register, so:

- Every item is displayed and stored at **min(self-report, 3)**. A respondent may pick 4 or 5, but the recorded and displayed level is 3 and the row is flagged `capped`.
- The same applies to the value axis: V1 is recorded Band A "not evidenced"; V2 at most `12–39%`; V3 at most 3; V4 at most 2.
- Capability score is therefore ≤ 50.0 and the band ≤ Emerging for any self-only entry; the scorecard prints **"self-report-dominant"** (evidence coverage 0%).
- Outside-in proxies may pre-populate a draft score or challenge it downward; they never lift above 3.
- Entries from the free form are stored in the benchmark with `evidence_gated = 0`, so the §5.5 disclosure ("share of peer entries evidence-gated vs self-scored") stays honest.
- Variance outputs need ≥5 respondents from the same organisation; below that, show the min–max range, not σ.

## Examples

All example data is synthetic. **Harbourline Mutual Bank does not exist.** `examples/generate_examples.py` (seed 20261025) writes:

- `responses_harbourline_fictional.csv` — 12 respondents (5 ExCo, 7 operating) × 48 items + V1–V4. Built so that ExCo over-rate D2/D4/D5 (gap > 0.75), several items cross σ > 1.0, ExCo claim 4–5 without evidence (cap), two-class items carry only one class (still capped: D1.4 D-only, D2.6 D-only, D4.4 I-only), and a handful of items carry qualifying evidence (lift). Result: 42.6 / Emerging, evidence coverage 25% (self-report-dominant), V1 A (not evidenced) · V2 12–39% · V3 3 · V4 2.
- `benchmark_synthetic_40.csv` — 40 fictional organisations. Stratified by target band 6 / 18 / 13 / 3 (15% / 45% / 32.5% / 7.5%, Leading inside the 5–10% window). Per organisation: a latent total drawn uniformly inside the band, dimension scores = latent + N(0, 9) clipped to 0–100 and rounded to 0.1, total recomputed exactly as the §2 weighted sum; redraw if the recomputed total leaves the band. 17 rows are `banking × large × SG`, all `population = evidenced`, so the example peer set clears n ≥ 15 inside the evidenced population; `--sector insurance --size-band mid` demonstrates the rank-within-named-peers fallback. The remaining rows are ~40% `evidenced`, the rest `self`.
- `rater_a.csv`, `rater_b.csv` — 12 fictional organisations × the 20 κ-subset items; rater B disagrees by one level ~18% of the time (~45% on D1.1, D4.1, D7.3).
- `scorecard_harbourline.md` / `.json` — the outputs of the command above.
