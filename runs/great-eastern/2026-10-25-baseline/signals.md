# Outside-in proxy signals — Great Eastern Holdings Limited

Run research-b053876078f4. Status is set from plumbverify's verdict on each signal's evidence claims: `released` = all evidence claims released; `partial` = some blocked; `blocked` = none released; `computed` = derived figure with no evidence claim of its own; `not-available` = no data. Proxies corroborate only and never lift an item above level 3 (instrument §5.4). Capability scores from these are an **outside-in pre-score, self-report absent**, not a maturity result.

| Signal | Instrument items | Value | Unit | Source | Tier | Confidence | Status | Note |
|---|---|---|---|---|---|---|---|---|
| Core peer count after funnel | §5.5 | 9 | peers | subject YAML long list + annual-report competitor names | — | model-inferred | blocked | n = 9 core (+7 secondary): below the instrument §5.5 minimum of 15; the scorecard must print "global, peer n insufficient" |
| AI-skill share of job postings (24 months) | D4.1 | — | % | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | not-available | Babina et al. method; numerator = postings matching the AI lexicon (ml/llm/mlops/ai_governance/ai_product) |
| AI-skill share: percentile vs core peers | D4.1 | — | percentile | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | not-available | peer n below the instrument's 15 threshold: directional only |
| Postings mentioning data_eng skills (24 months) | D2.2, D2.3 | 0 | postings | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | computed |  |
| Postings mentioning mlops skills (24 months) | D3.2 | 0 | postings | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | computed |  |
| Postings mentioning ai_product skills (24 months) | D4.5 | 0 | postings | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | computed |  |
| Postings mentioning ai_governance skills (24 months) | D6.2 | 0 | postings | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | computed |  |
| Postings mentioning llm skills (24 months) | D3.1 | 0 | postings | CsvPostingsSource (data/great-eastern/postings.csv) | — | model-inferred | computed |  |
| AI-related patents (5 filing years) | D4.2, D1.5 | 0 | patents | CsvPatentSource (data/great-eastern/patents.csv) | — | model-inferred | computed | zero is a finding, not level 1 (ASEAN FIs rarely file); hiring and patent evidence outweigh narrative (P3/P9) |
| AI patents: subject vs core-peer median | D4.2 | — | x median | CsvPatentSource (data/great-eastern/patents.csv) | — | model-inferred | not-available | BCG P4: future-built 3.5x patents |

## Module runs (C10)

| Module | Tool calls | Restarts | Escalated | Claims | Signals | Data available |
|---|---|---|---|---|---|---|
| annual-report | 1 | 0 | no | 0 | 0 | no |
| peer-set | 0 | 0 | no | 1 | 1 | yes |
| postings | 1 | 0 | no | 0 | 7 | no |
| earnings-calls | 1 | 0 | no | 0 | 0 | no |
| patents | 1 | 0 | no | 0 | 2 | yes |
| financials | 0 | 0 | no | 0 | 0 | no |

Verification: 1 claims, 1 BLOCKED, build FAIL; citation resolution 0.0, quotation pass rate 1.0, two-upstream coverage 1.0, AI/farm pages cited 0.