# Gap register — Great Eastern Holdings Limited

Blocked claims never appear in client-facing material; they are disclosed here (spec C11). Module gaps are data the sprint could not obtain. [VERIFY] items are carried from the candidate screen and the subject file.

## 1. Blocked claims (4)

| Claim | Module | Text | Reasons |
|---|---|---|---|
| great-eastern.peer.size.prudential-assurance-co-singapore-i527l | peer-set | Prudential Assurance Co Singapore (I527L) S$66.3 billion under management as at 31 December 2025 (AU... | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/i527l/2025/2025.xlsx: source not citable: state=DEAD health=DEAD |
| great-eastern.peer.size.income-insurance-ltd-i585c | peer-set | Income Insurance Ltd (I585C) Total Assets S$44.7 billion (PY24 S$43.4 billion) | no citation reaches the support threshold (C4); https://www.income.com.sg/getContentAsset/f39850fb-3691-42e4-b8b9-bfb476d651f8/05c6012c-3879-4f1c-b994-00e61e65c363/Income-Insurance-%E2%80%93-Annual-Report-2025.pdf?language=en: source not citable: state=DEAD health=DEAD |
| great-eastern.peer.size.singapore-life-ltd-singlife-i518c | peer-set | Singapore Life Ltd (Singlife, I518C) total assets over S$16 billion (newsroom, undated) | no citation reaches the support threshold (C4); https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i518c/2025/2025.xlsx: source not citable: state=DEAD health=DEAD |
| great-eastern.peer.size.aia-group-whole | peer-set | AIA Group (whole) total assets US$345,423 million at 31 December 2025 | no citation reaches the support threshold (C4); https://www.aia.com/content/dam/group-wise/en/docs/investor-relations/2025/AIA%202025%20annual%20report_EN.pdf: source not citable: state=DEAD health=DEAD |

## 2. Module data gaps (19)

| Module | Topic | Detail | Items | [VERIFY] |
|---|---|---|---|---|
| annual-report | results_release FY2025 | local file missing: data/great-eastern/geh-fy2025-media-release.pdf (download the PDF and place it there, or attach it: plumbresearch ingest <subject.yaml> --file <pdf> --doc results_release-2025) | D1.1 | yes |
| annual-report | annual_report FY2024 | local file missing: data/great-eastern/geh-annual-report-fy2024.pdf (download the PDF and place it there, or attach it: plumbresearch ingest <subject.yaml> --file <pdf> --doc annual_report-2024) | D1.1 | yes |
| peer-set | peer size unverified | AIA Singapore Pte Ltd (I566C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Prudential Assurance Co Singapore (I527L): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Income Insurance Ltd (I585C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Singapore Life Ltd (Singlife, I518C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Manulife (Singapore) Pte Ltd (I522L): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | HSBC Life (Singapore) (I544C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Tokio Marine Life Insurance Singapore (I517L): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | Etiqa Insurance Singapore (I570C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | peer size unverified | China Taiping Insurance (Singapore) (I579C): size needed to apply the 0.3x–3x band |  | yes |
| peer-set | exited peer unsourced | Aviva Singapore → Singlife: Consolidated — no fetched source |  | yes |
| peer-set | exited peer unsourced | AXA Insurance Singapore → HSBC: Consolidated — no fetched source |  | yes |
| peer-set | exited peer unsourced | Zurich Life Singapore exit: Exit — no fetched source |  | yes |
| peer-set | funnel warning | named in the subject's own report but not in the declared long list (add or reject with reason): NEA |  |  |
| postings | no postings in window | no postings for ['Great Eastern', 'Great Eastern Life', 'Great Eastern General', 'GEH'] between 2024-11-01 and 2026-10-25 in CsvPostingsSource (data/great-eastern/postings.csv); alpha-targets §6 item 5: 24-month posting series not yet collected | D4.1 | yes |
| earnings-calls | no transcripts | no earnings-call transcripts for Great Eastern between 2024-10-01 and 2026-10-25 (alpha-targets §4: availability [VERIFY]; GEH has no calls — proxy-by-parent must be declared with a label) | D1.1, D8.6 | yes |
| patents | no patents found | no patents for ['Great Eastern', 'Great Eastern Life', 'Great Eastern General', 'GEH'] in CsvPatentSource (data/great-eastern/patents.csv) since 2021-01-01; confirm with IPOS / MyIPO / Google Patents before treating as zero | D4.2 | yes |
| financials | no financials | data/great-eastern/financials.csv missing or empty; populate from segment disclosures / MAS returns (alpha-targets §5.1: value axis reported as Band A 'not evidenced') | V1, D8.3 | yes |

## 3. [VERIFY] items from the subject file (26)

- OCBC % in GEH: resolved on paper as 88.19% voting (443,608,028/503,030,110) and 93.72% economic after the 19 Aug 2025 bonus issue; 88.44% was the pre-May-2024-offer holding — confirm from the hashed Form 3 PDF (20250819-form-3.pdf), checking the file is the form and not the SGXNet wrapper
- Great Eastern General Insurance MAS code I703C (from the MAS insurer-returns index) — confirm the I703C return downloads
- Annual-report AI paragraph count and governance wording — extract text locally from the greateasternlife.com AR2025 PDF (~19 'AI' mentions per a page summary)
- Earnings calls: GEH holds none (financial calendar lists announcements, AGM/EGM, dividends only; no webcast/briefing). Proxy-by-parent = OCBC FY2025 (25 Feb 2026) and 1H2026 (7 Aug 2026) results decks + YouTube briefing recordings; no official transcript exists. Every claim from them carries label 'proxy-by-parent: OCBC' (transcripts/index.yaml)
- Expense lines in AR for disclosed technology spend
- Job-posting volumes (Great Eastern Life / GE General) over 24 months — MyCareersFuture API (POST api.mycareersfuture.gov.sg/v2/search) gives current postings only; LinkedIn needs a logged-in count; series requires repeated snapshots
- Management AI/data titles; OCBC group CDO/CTO roles
- FEAT/Veritas participation; MAS enforcement history
- Every MAS-return total-assets figure for the nine core entities + GE Life + GE General — XLSX URLs located (7 confirmed, 4 inferred: I516L, I703C, I544C, I579C); none read yet
- Patents: Google Patents / IPOS count for assignee 'Great Eastern' not confirmable from the sandbox (robots-disallowed); fetch-datapack.sh pulls the Google Patents JSON; expect 0
- Founder conflict declaration (C6) for OCBC/GEH
- subject size (total_assets): S$122,639.1m per FY25 SGX announcement and AR2025 (page summaries, [VERIFY] on hash); USD at ≈1.29 S$/US$ is ours; profit attributable S$1,207.1m (+21%); NBEV S$739.7m; band ≈ US$28bn–285bn. Second upstream: https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-website/annual-report/great-eastern-holdings-limited-ar-2025.pdf
- peer size for AIA Singapore Pte Ltd (I566C): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]; group AR2025 segment: Singapore VONB US$530m (+14%), OPAT US$721m (+5%)
- peer size for Prudential Assurance Co Singapore (I527L): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]; factsheet AUM is a proxy only; latest full AR is 2024
- peer size for Income Insurance Ltd (I585C): AR2025 per page summary [VERIFY on hash]; supersedes the Wikipedia S$47.2bn; USD conversion ours; second upstream = MAS return 2025 XLSX; Profit After Tax S$118.9m
- peer size for Singapore Life Ltd (Singlife, I518C): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]; Singapore Life Holdings FY2025 audited FS PDF for corroboration; public disclosure FY25 net income $45,663k per MAS returns
- peer size for Manulife (Singapore) Pte Ltd (I522L): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]; company factsheet gives no Singapore figures (Tier 1 insurer ⇒ ≥S$5bn total assets)
- peer size for HSBC Life (Singapore) (I544C): MAS return 2025 — URL pattern inferred (index page unreadable from sandbox) [VERIFY]; Allianz release: operating profit €80m (2025), comprehensive equity €1.2bn; no total assets
- peer size for Tokio Marine Life Insurance Singapore (I517L): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]
- peer size for Etiqa Insurance Singapore (I570C): MAS return 2025 XLSX (URL confirmed) — total assets not yet read [VERIFY]; Notice 124 supplementary info FY2025 has no total-assets line
- peer size for China Taiping Insurance (Singapore) (I579C): MAS return 2025 — URL pattern inferred (index page unreadable from sandbox) [VERIFY]; public disclosure FY2025: capital available S$480m, balance sheet deferred to MAS returns
- peer size for AIA Group (whole): AR2025 consolidated statement of financial position (page summary; [VERIFY] on hash). Second upstream: HTML press release 19 Mar 2026 — the aia.com.sg PDF the pipeline marked DEAD is linked from it
- peer size for Allianz Malaysia Bhd; Syarikat Takaful Malaysia Keluarga; Hong Leong Assurance (via HLFG): [VERIFY sizes]
- peer Aviva Singapore → Singlife: Aviva Singapore → Singlife
- peer AXA Insurance Singapore → HSBC: AXA Insurance Singapore → HSBC
- peer Zurich Life Singapore exit: Zurich Life Singapore exit

## 5. Attached documents awaiting publisher reconciliation (1 of 1)

A person attached these documents instead of the pipeline fetching them. Each is stored and cited under the declared publisher URL. `pending` / `UNAVAILABLE` = the publisher hash is unreconciled and every claim from the document is released with the label `attached; publisher hash unreconciled`; `MATCH` = the publisher's bytes are identical and the document now counts as fetched; `MISMATCH` = the attachment is not the published document and every claim citing it is BLOCKED. Run `plumbverify reconcile --store <out>/<slug>/evidence` when egress is available.

| Document | Declared URL | File | Supplied by | Supplied at | SHA-256 (attached) | State | Reconciliation | SHA-256 (publisher) | Claims released / blocked |
|---|---|---|---|---|---|---|---|---|---|
| annual_report-2025 | https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-... | 19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf | Deepak Waghmare | 2026-10-25T12:10 | `ae320cb3ffa250f3869545c9c02f5cf0505a09494c7735068569d9a143606488` | ATTACHED | pending | — | 5 / 0 |
- annual_report-2025: publisher hash unreconciled; 5 released claim(s) carry the attached label until `plumbverify reconcile` returns MATCH.
