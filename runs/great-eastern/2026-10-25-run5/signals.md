# Outside-in proxy signals — Great Eastern Holdings Limited

Run research-e0bc54685dce. Status is set from plumbverify's verdict on each signal's evidence claims: `released` = all evidence claims released; `partial` = some blocked; `blocked` = none released; `computed` = derived figure with no evidence claim of its own; `not-available` = no data. Proxies corroborate only and never lift an item above level 3 (instrument §5.4). Capability scores from these are an **outside-in pre-score, self-report absent**, not a maturity result.

| Signal | Instrument items | Value | Unit | Source | Tier | Confidence | Status | Note |
|---|---|---|---|---|---|---|---|---|
| Annual-report AI rubric level (annual_report FY2025) | D1.1, D5.4, D8.3 | 4 | level 1-5 | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | T2 | model-inferred | released | L4: production language with >=2 specific use cases and a quantified outcome or disclosed investment; corroborates only, never lifts above L3 (instrument §5.4) |
| AI mentions per 1,000 words (annual_report FY2025) | D1.1 | 0.24 | per 1,000 words | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | T2 | model-inferred | computed |  |
| Named competitors / peers in the report | peer-seed | 0 | names | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | T2 | model-inferred | computed |  |
| AI / data leadership titles found (subject, present or in transition) | D1.2, D2.1, D5.2 | 3 | titles | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | T2 | model-inferred | released | value counts D1.2 proxy titles (AI / data / analytics / digital scope) held at the subject or a subject subsidiary and not vacated: 2 present (Division Head, Group & Digital Affinity (Wynn Chew Ai Ling); Division Head, Marketing and Digital Transformation (Lucy Loo Liuxi)), 1 seat(s) in transition (Managing Director, Group Data and AI (Zhao Jingyuan) [expected to join Oversea-Chinese Banking Corporation Limited (“OCBC”); successor to be named in due course, March 2026]). Not counted: 1 departed/former (Managing Director, Group Customer and Digital (Ryan Cheong) [left the Group, 2025]); 1 parent-group title(s), reported as parent-group context (Head of the Group Data Office [joining Oversea-Chinese Banking Corporation Limited, March 2026]); CTO/CIO-type titles are listed as 'other'. CAIO/CDO presence is the D1.2 proxy (BCG: future-built 3x CAIO, 2x CDO) |
| Parent-group AI / data titles (context, not counted for D1.2) | D1.2-context | 1 | titles | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | T2 | model-inferred | released | titles the report attributes to the parent group (e.g. a subject executive moving to the parent); parent-group context only, never subject D1.2 evidence |
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
| annual-report | 1 | 0 | no | 11 | 5 | yes |
| peer-set | 0 | 0 | no | 4 | 1 | yes |
| postings | 1 | 0 | no | 0 | 7 | no |
| earnings-calls | 1 | 0 | no | 0 | 0 | no |
| patents | 1 | 0 | no | 0 | 2 | yes |
| financials | 0 | 0 | no | 0 | 0 | no |
| findings | 1 | 0 | no | 21 | 0 | yes |

## Run outcome

**Released: 29 claims. Withheld: 7 claims (listed in the gap register).** Build profile: `internal` (internal draft: claims resting on an unreconciled attachment are released with the attached label; not for client use).

Removed, not footnoted:

| Claim | Source attempted | Reason | What would resolve it |
|---|---|---|---|
| great-eastern.peer.size.prudential-assurance-co-singapore-i527l | https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insura... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annua | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.peer.size.income-insurance-ltd-i585c | https://www.income.com.sg/getContentAsset/f39850fb-3691-42e4-b8b9-bfb476d651f8/05c6012c... | no citation reaches the support threshold (C4); https://www.income.com.sg/getContentAsset/f39850fb-3691-42e4-b8b9-bfb476d651f8/05c6012c-3879-4f1c-b994-00e61e65c | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.peer.size.singapore-life-ltd-singlife-i518c | https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-busine... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i518c/2025/2025.xlsx:  | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.peer.size.aia-group-whole | https://www.aia.com/content/dam/group-wise/en/docs/investor-relations/2025/AIA%202025%2... | no citation reaches the support threshold (C4); https://www.aia.com/content/dam/group-wise/en/docs/investor-relations/2025/AIA%202025%20annual%20report_EN.pdf:  | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.findings.reg.sg-mas-airm.issued | https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence- | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.findings.reg.sg-mas-airm.effective | https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence- | re-run from a machine with egress, or attach the document under its publisher URL |
| great-eastern.findings.reg.sg-mas-airm.lifecycle | https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence- | re-run from a machine with egress, or attach the document under its publisher URL |

Footer: run `research-e0bc54685dce` · citation resolution 0.1429 · quotation pass rate 1.0 · two-upstream coverage 1.0 · AI/farm pages cited 0 · reviewer human-read: not yet recorded.

## Attached documents (reconciliation status)

A person attached these documents instead of the pipeline fetching them. Each is stored and cited under the declared publisher URL. `pending` / `UNAVAILABLE` = the publisher hash is unreconciled: in a **client** build every claim resting only on the document is withheld (gap register: awaiting publisher reconciliation, spec C2a); in an **internal** build it is released with the label `attached; publisher hash unreconciled`. `MATCH` = the publisher's bytes are identical and the document now counts as fetched; `MISMATCH` = the attachment is not the published document and every claim citing it is BLOCKED in any profile. Run `plumbverify reconcile --store <out>/<slug>/evidence` when egress is available.

| Document | Declared URL | File | Supplied by | Supplied at | SHA-256 (attached) | State | Reconciliation | SHA-256 (publisher) | Claims released / blocked |
|---|---|---|---|---|---|---|---|---|---|
| annual_report-2025 | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | 19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf | Deepak Waghmare | 2026-10-25T13:47 | `ae320cb3ffa250f3869545c9c02f5cf0505a09494c7735068569d9a143606488` | ATTACHED | pending | — | 29 / 0 |