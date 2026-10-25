# G1 alpha targets: candidate screen, recommendation, peer sets and signal plan

**Status: v0.1 draft** | Owner: Methodology | Date: 2026-10-25 | Implements decisions D1 (wedge = Singapore FIs) and D5 (one mid-cap/regional bank + one insurer; MAS-regulated, listed, public data). Not committed.

Purpose: name the two G1 alpha subjects, show the screen that produced them, build each subject's peer set by the documented funnel (seed by industry codes and named competitors → text similarity → 0.3x–3x size band → 5–12 core peers plus a labelled secondary tier → exited peers included), and set out which outside-in maturity proxies from `methodology/maturity-instrument.md` can actually be gathered for an engagement that has no client.

Evidence discipline: every URL below was returned by a search or fetched during this screen on 2026-10-25; none were introduced from memory. Figures I could not confirm from a primary or T2 source are marked **[VERIFY]**. Fiscal years are calendar (31 Dec) unless stated. Currency as reported by the source.

---

## 0. Change log

| Version | Date | Change |
|---|---|---|
| v0.1 | 2026-10-25 | Initial candidate screen (4 banks, 3 insurers + 5 screened-out), recommendation, two peer sets, signal plan, Phase 2 simulation plan |

---

## 1. Candidate list

Screen criteria (from D5): MAS-regulated entity in Singapore; the entity or its parent is listed on SGX, HKEX, Bursa, ASX or LSE; if the parent is listed, Singapore must be a material, separately reported segment; rich public data. Data-richness score 1–5 is a judgement on five inputs: (a) annual report depth on AI, (b) Singapore-level financials, (c) results-call or analyst-briefing transcripts, (d) press-release and job-posting volume, (e) regulator-published returns.

### 1.1 Banks

| # | Candidate | Listing | MAS status | FY | Size (latest FY) | Latest annual report | Public AI disclosures found | Data richness |
|---|---|---|---|---|---|---|---|---|
| B1 | **Malayan Banking Berhad (Maybank)** — Singapore via Maybank Singapore Limited | Bursa Malaysia (MAYBANK, 1155) | Foreign full bank + Qualifying Full Bank (QFB), locally incorporated community financial services since the 2018 MAS approval ([Wikipedia list of banks in Singapore](https://en.wikipedia.org/wiki/List_of_banks_in_Singapore); [Asian Private Banker](https://asianprivatebanker.com/private-banking-wealth-management/maybank-wins-mas-approval-singapore-incorporation-community-financial-services/)) | Dec | Group net profit RM10.51bn, PBT RM14.33bn, net operating income RM30.38bn, ROE 11.7% ([The Edge Singapore via Yahoo, 25 Feb 2026](https://sg.finance.yahoo.com/news/maybank-fy2025-net-profit-gains-005205385.html)). **Maybank Singapore: PBT S$711.30m (+1.3%), net income S$1,370.11m (+6.1%), loans S$54.3bn (+5.0%), deposits S$60.4bn; ≈25.9% of group PBT and ≈18.3% of group net operating income** ([Maybank 4Q FY2025 analyst presentation, 26 Feb 2026](https://www.maybank.com/iwov-resources/documents/pdf/quarterly-report/2025/maybank-group-analyst-presentation-fy2025-4q.pdf)). Group total assets ≈ RM1.1 trillion **[VERIFY — not in the sources fetched; take from the FY2025 audited balance sheet]** | Integrated Annual Report 2025: mirror at [BankTrack](https://www.banktrack.org/download/annual_report_2025_28) (binary, not text-extractable via fetch); primary copy on maybank.com / maybank.listedcompany.com **[VERIFY exact URL]**; FY2024 IAR Part 2 at [maybank.listedcompany.com](https://maybank.listedcompany.com/newsroom/Maybank_Integrated_AR_2024_Part_2_20250326.pdf) | ROAR30 strategy (2026–2030) with **RM10bn five-year technology, data and AI investment**; ROE target 13–14% by 2030 ([Fintech News Malaysia, 21 Jan 2026](https://fintechnews.my/56126/banking/maybank-roar30-strategy-rm10-billion-technology-investment/); [The Asian Banker](https://www.theasianbanker.com/press-releases/maybank-launches-roar30-targets-roe-of-13-14-by-2030)). **RM1bn five-year Microsoft partnership (Aug 2025): Azure as a primary cloud, Microsoft 365 Copilot to 44,000 employees** ([DCD, 11 Aug 2025](https://www.datacenterdynamics.com/en/news/microsoft-scores-2364m-deal-with-malaysian-financial-group-maybank/)). Digital KPIs in the 4Q25 deck: 10.81m 3-month active digital users, 59% digital penetration, "harnessing AI" as a ROAR30 pillar; no AI use-case counts. Digital sales 78% of total ([Tech Wire Asia, 19 Dec 2025](https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/)). Oct 2026 press on AI for resilience ([NST](https://www.nst.com.my/amp/business/corporate/2026/10/1559475/maybank-taps-ai-strengthen-regional-banking-resilience) — robots-blocked, unread). Job-posting volume **[VERIFY — count via MyCareersFuture + LinkedIn over 24 months]** | **4** |
| B2 | **CIMB Group Holdings** — Singapore via CIMB Bank Berhad Singapore branch | Bursa Malaysia (CIMB, 1023) | Foreign full bank (not QFB; branch, not locally incorporated) ([Wikipedia list](https://en.wikipedia.org/wiki/List_of_banks_in_Singapore)) | Dec | Net profit RM7.9bn, PBT RM10.7bn, ROE 11.3% ([CIMB release, 2 Mar 2026](https://www.cimb.com/en/newsroom/2026/cimb-delivers-net-profit-of-rm7-9-billion-with-roe-at-11-3-percent-strengthens-long-term-value-creation-for-shareholders.html)); total assets MYR 778.7bn (≈US$164bn), tech spend MYR 1.7bn, opex MYR 10.6bn ([The Asian Banker, 27 Feb 2026](https://www.theasianbanker.com/press-releases/cimb-posts-fy2025-net-profit-of-1-7b-as-forward30-execution-progresses)). **Singapore = 14% of group PBT in 1Q25 (11% in 1Q24)** ([finews.asia, 23 Jul 2025](https://www.finews.asia/finance/43676-cimb-malaysia-bank-singapore-wealth-treasury-johor-sez-novan-amirudin-victor-lee-asean)); FY2025 Singapore PBT **[VERIFY from 4Q25 analyst deck]** | 2025 Integrated Annual Report (cimb.com investor-relations; 2024 financial statements at [cimb.com](https://www.cimb.com/content/dam/cimb/group/documents/investor-relations/annual-reports/2024/cimb-financial-statement-2024.pdf)) **[VERIFY 2025 URL]** | Forward30: >MYR 100m on AI training/upskilling in 2025; GenAI in transaction monitoring, onboarding, risk modelling, RM tools ([The Asian Banker](https://www.theasianbanker.com/press-releases/cimb-posts-fy2025-net-profit-of-1-7b-as-forward30-execution-progresses)); EVA chatbot (Pand.ai, Singapore) 94% email-response accuracy, 120k chats, +23% satisfaction; OctoBiz approvals +191%; WhatsApp AI advisory in Singapore ([Tech Wire Asia](https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/)) | **4** (Singapore segment thinner than Maybank's; branch structure means no separately published Singapore financial statements **[VERIFY]**) |
| B3 | **Hong Leong Finance Limited** | SGX Mainboard (S41) | Finance company licensed by MAS under the Finance Companies Act **[VERIFY licence class on the MAS Financial Institutions Directory]** | Dec | Total interest income and hiring charges S$444.7m (−25%), net profit S$62.7m (−39.7%), net loans S$12.10bn, deposits S$12.30bn ([iTiger, FY2025 results](https://www-web.itiger.com/news/1157586943)); total assets ≈ S$16bn **[VERIFY]** | [Annual Report 2025 (SGX)](https://links.sgx.com/1.0.0/corporate-announcements/YEVJ5R1L4F4E2JZJ/880350_Hong%20Leong%20Finance%20Annual%20Report%202025.pdf); FY results at [hlf.com.sg](https://www.hlf.com.sg/downloads/financial_result/2025/fh2025fy.pdf) | "HLF Digital" platform rollout; next-generation branch at Punggol Coast Mall; **no AI mention** in results ([iTiger](https://www-web.itiger.com/news/1157586943)) | **2** — a true SGX mid-cap and MAS-regulated, but too little public AI signal to exercise the instrument, and no analyst calls |
| B4 | **United Overseas Bank (UOB)** — fallback | SGX (U11) | Local full bank | Dec | Total assets S$572bn (+6%), operating profit S$7.7bn (−4%), net fee income S$2.6bn ([UOB AR2025 microsite](https://www.uobgroup.com/AR2025/index.html)); net profit ≈ S$4.7bn after pre-emptive provisions, IT expenses S$1.136bn (+7%) ([The Asian Banker, 27 Feb 2026](https://www.theasianbanker.com/updates-and-articles/uob-reports-5-7-billion-net-profit-after-pre-emptive-provisions-as-fee-income-reaches-record)) | [UOB Annual Report 2025 PDF](https://www.uobgroup.com/investor-relations/assets/pdfs/investor/annual/uob-annual-report-2025.pdf); [AGM 2026 CEO presentation](https://links.sgx.com/1.0.0/corporate-announcements/71HKOVYDZ716XVWQ/884581_UOB%20AGM%202026%20-%20CEO%20presentation.pdf) | AR2025 highlights page has no AI statement; CFO frames AI as a productivity lever; TMRW digital wealth sales more than doubled ([The Asian Banker](https://www.theasianbanker.com/updates-and-articles/uob-reports-5-7-billion-net-profit-after-pre-emptive-provisions-as-fee-income-reaches-record)) | **5** (quarterly results calls with transcripts, SGX filings, heavy press and hiring) |

Screened out: DBS and OCBC (excluded by the D5 preference for a non-big-three subject; both appear in the peer set and DBS is the anchor for the "Leading" band); Standard Chartered Singapore (Singapore profit "nears S$1bn" in H1 2025 per [Fintech News Singapore](https://fintechnews.sg/118482/fintech/stanchart-singapore-profit/) but the group is >3x Maybank's size and UK-headquartered, so it sits in the secondary tier); Sing Investments & Finance and Singapura Finance (SGX finance companies, thinner than Hong Leong Finance); digital full banks GXS, MariBank, Trust (unlisted subsidiaries).

### 1.2 Insurers

| # | Candidate | Listing | MAS status | FY | Size (latest FY) | Latest annual report | Public AI disclosures found | Data richness |
|---|---|---|---|---|---|---|---|---|
| I1 | **Great Eastern Holdings (GEH)** | SGX Mainboard (G07). **Listing status confirmed after the OCBC offers:** trading suspended July 2024 after OCBC reached ~93.7%; OCBC's S$30.15 exit offer lapsed when only 63.49% of minorities voted for delisting on 8 Jul 2025 (75% needed); OCBC said no further offers "in the foreseeable future" ([The Independent SG, 9 Jul 2025](https://theindependent.sg/great-eastern-to-resume-trading-after-less-than-75-voted-in-favour-of-delisting-proposal-ocbc-says-no-further-offers-in-the-foreseeable-future/)); one-for-one bonus issue with OCBC electing Class C non-voting shares, allotted 19 Aug 2025; **trading resumed 21 Aug 2025**; OCBC's ordinary-share holding reported as 88.19–88.44% (sources conflict) with free float ≥10% ([Caproasia, 15 Aug 2025](https://www.caproasia.com/2025/08/15/singapore-insurance-giant-great-eastern-holdings-to-resume-trading-on-singapore-exchange-sgx-on-21st-august-2025-after-shareholders-voted-to-resume-trading-restore-free-float-requirement-new-non/); [TipRanks](https://www.tipranks.com/news/company-announcements/great-eastern-holdings-resumes-trading-and-announces-dividend-increase); [OCBC statement](https://www.ocbc.com/group/media/release/2025/ocbc-statement-on-the-approval-of-great-eastern-holdings-resolutions-b-and-c.page)). Market cap ≈ S$12.2bn at resumption ([TipRanks](https://www.tipranks.com/news/company-announcements/great-eastern-holdings-resumes-trading-and-announces-dividend-increase)) **[VERIFY exact OCBC % from the SGX shareholding announcement]** | Direct life insurer: The Great Eastern Life Assurance Co Ltd (MAS code I516L); general: Great Eastern General Insurance **[VERIFY code]** ([MAS insurance company returns](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns)) | Dec | Profit attributable S$1,207.1m (+21%, record); NBEV S$739.7m (+19%); TWNS −15%; "over S$122 billion in assets"; FY dividend 55c post-bonus ([GEH FY-25 results release, 24 Feb 2026](https://www.greateasternlife.com/sg/en/about-us/media-centre/media-releases/fy-25-financial-results.html)) | [GEH Annual Report FY2025 (SGX, 27 Mar 2026)](https://links.sgx.com/1.0.0/corporate-announcements/LNEPNAAMA9G4OO20/880681_GEH%20Annual%20Report%20FY2025.pdf) (announcement: [greateasternlife.com](https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/20260327-ar-fy2025-announcement.pdf)); FY2024 AR at [greateasternlife.com](https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/20250328-annual-report-fy2024-sgx.pdf) | FY25 release names: **AI-enabled advisory platform targeting ~75% cut in adviser preparation time; proprietary AI-powered medical claims automation platform rolled out; AI solution for complex underwriting under test; "expanded digital and AI capabilities across advisory and service delivery"** ([FY-25 release](https://www.greateasternlife.com/sg/en/about-us/media-centre/media-releases/fy-25-financial-results.html)). Annual-report AI paragraph count and governance wording **[VERIFY — PDF fetch returned binary; extract text locally]**. Parent OCBC's AR2025 frames an "AI, Digital and Data (ADD)" strategy and agentic AI at Bank of Singapore ([OCBC Group CEO perspectives](https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page)) | **4** (SGX filings + MAS returns + quarterly releases; no earnings calls **[VERIFY]**; thin sell-side coverage since the suspension) |
| I2 | **AIA Group** — Singapore via AIA Singapore Pte Ltd | HKEX (1299) | Direct life insurer (MAS code I566C) ([MAS returns](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns)) | Dec | Group VONB US$5,516m (+15%), OPAT US$7,136m, total assets US$345bn, EV equity US$79.7bn; **AIA Singapore VONB +14%, OPAT +5% (absolute figures in the AR segment tables)** ([AIA results release, 19 Mar 2026](https://www.aia.com.sg/content/dam/sg-wise/en/docs/about-aia/press-release/2026/aia-delivers-record-results-in-2025.pdf)) | AIA Annual Report 2025 ([aia.com investor filings](https://aia.gcs-web.com/static-files/884813c0-dc66-4696-9023-bbf7f8253e62) **[VERIFY this is the AR]**) | Release speaks of a "Technology, Data and Analytics (TDA)" strategy (iPOS+, iSMART+, iRecruit+, AIA+ super app); **no AI/GenAI wording in the results release** ([AIA release](https://www.aia.com.sg/content/dam/sg-wise/en/docs/about-aia/press-release/2026/aia-delivers-record-results-in-2025.pdf)) | **5** at group level (calls, transcripts, segment disclosure); Singapore is one of ~18 segments and >3x GEH in size |
| I3 | **Prudential plc** — Singapore via Prudential Assurance Co Singapore | LSE / HKEX (secondary SGX) | Direct life insurer **[VERIFY MAS code]** | Dec | Group NBP US$2.8bn (+12%), OPAT +7%; **Singapore NBP +2%, sales +5%, agency new sales +27% in H2, bancassurance NBP flat**; AI: PRUServices 90% straight-through on 1.5m interactions, PRUAction +15% productivity in Singapore, AI claims controls cut fraud/waste/abuse by >US$100m in 2025; 2026 capability programme US$300–350m ([FY2025 results presentation transcript](https://www.prudentialplc.com/content/dam/prudential-plc/newsroom/company-news/2026/Presentation%20transcript.pdf)) | Prudential plc Annual Report 2025 (prudentialplc.com) **[VERIFY URL]**; [Q1 2026 update](https://www.prudentialplc.com/en/newsroom/company-news/2026/prudential-plc-q1-business-performance-update/) | As left; GenAI not named ([transcript](https://www.prudentialplc.com/content/dam/prudential-plc/newsroom/company-news/2026/Presentation%20transcript.pdf)) | **5** at group level; Singapore segment is reported (APE, NBP) but is ~1/8 of the group |

Screened out, with reason:

| Candidate | Status | Reason |
|---|---|---|
| Manulife (Singapore) | Parent TSX/NYSE/HKEX (945); Singapore not broken out — Asia core earnings +18% only ([Insurance Business, 12 Feb 2026](https://www.insurancebusinessmag.com/us/news/life-insurance/manulife-sets-record-2025-core-earnings-as-asia-and-global-wam-power-growth-565136.aspx)) | Fails the "separately reported segment" test |
| Singlife | Unlisted; 100% Sumitomo Life since 2024 at a S$4.6bn valuation ([Insurance Business Asia, 16 Oct 2026](https://www.insurancebusinessmag.com/asia/news/breaking-news/giant-japanese-insurer-looking-south-and-to-the-us-for-deals-593771.aspx)) | Fails "listed"; stays in the peer set via MAS returns |
| Income Insurance | Public non-listed company; NTUC Enterprise majority; Allianz withdrew its ~S$2.2bn offer Dec 2024 after the Government blocked it; total assets S$47.2bn ([Wikipedia](https://en.wikipedia.org/wiki/Income_Insurance); [Insurance Journal, 24 Jul 2026](https://www.insurancejournal.com/news/international/2026/07/24/878902.htm)) | Fails "listed"; MAS return I585C available 2022–2025 ([MAS](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i585c)) |
| United Overseas Insurance (UOI) | SGX (U13); general insurer; insurance revenue S$115.4m, net profit S$32.3m; no AI mention ([iTiger](https://www-web.itiger.com/news/1172397258)); [AR 2025](https://links.sgx.com/1.0.0/corporate-announcements/10HJ7VSC02FVI5Z4/881515_UOI%20Annual%20Report%202025.pdf) | Listed and MAS-regulated but too small and too thin on AI to exercise the instrument (richness 2) |
| FWD Group | HKEX (1828) since 7 Jul 2025; AUM ≈US$62.4bn; OPAT US$499m 2025; exited Singapore group medical in 2020 ([Wikipedia](https://en.wikipedia.org/wiki/FWD_Group)) | Singapore is small and not separately reported; goes to the secondary tier |

---

## 2. Recommendation

**Bank: Malayan Banking Berhad (Maybank), assessed at group level with Maybank Singapore Limited as the MAS-regulated anchor.**
**Insurer: Great Eastern Holdings Limited (GEH).**

Reasoning:

1. **Data richness without the big-three problem.** Maybank is the only regional bank in the screen whose Singapore business is both locally incorporated under a QFB licence and separately reported at ≈26% of group PBT, and it has the most quantified public AI commitments of the non-DBS set (RM10bn ROAR30 technology/AI envelope; RM1bn Microsoft agreement with Copilot for 44,000 staff). GEH is the only MAS-regulated insurer that is itself SGX-listed with a free float, files its own annual report and quarterly releases, and has named AI deployments (advisory, claims, underwriting) that can be scored on the instrument.
2. **Both sector overlays get tested** (D5): a bank under MAS AIRM with a Malaysian home regulator (BNM) layered on top, and a life-and-general insurer whose returns MAS publishes per entity.
3. **Conflict with the founder's employer.** Per `commercial/conflict-check-procedure.md` C6, the founder's employer, its customers and suppliers where the founder has had material involvement are in scope. No public Dell–Maybank or Dell–Great Eastern customer story was found in the search run (the only bank case studies returned were Emirates NBD and REYL ([Dell](https://www.delltechnologies.com/asset/en-hk/products/storage/customer-stories-case-studies/emirates-nbd-bank-written-case-study.pdf))). **Soft conflict flags, not blockers:** (a) any bank of this size in APJC is likely an enterprise-infrastructure customer of the founder's employer **[VERIFY by founder declaration, logged on the CC form]**; (b) GEH is an 88%-owned subsidiary of OCBC, so the OCBC relationship must be declared as well; (c) Maybank's Microsoft partnership is a competitor-adjacent relationship for an enterprise-tech employer. The DBS/UOB/OCBC fallback carries the same soft conflict at larger scale, which is a second reason to prefer Maybank.
4. **Why not the alternatives.** CIMB is close (richness 4) but its Singapore business is a branch at ~14% of PBT and the subject would be hard to anchor to MAS AIRM; keep it as core peer #1. Hong Leong Finance is the purest "SGX mid-cap, MAS-regulated" fit but publishes no AI signal, so the alpha would score an empty instrument. AIA and Prudential would make better *global* subjects but Singapore is a minority segment and both exceed the 3x size band relative to every Singapore-domiciled peer, which breaks the peer-set protocol for the subject itself; both are core peers for GEH.
5. **Fallback.** If Maybank's Singapore disclosures prove too thin for the Singapore-level view (e.g. Maybank Singapore Limited's statutory financial statements are not public **[VERIFY]**), fall back to UOB (richness 5) and re-run the conflict check.

---

## 3. Peer sets

Funnel applied (from `docs/AI first consulting engagement framework.md`, Phase 1, and `research_notes/.../competitor_benchmarking.md` KQ3): (1) seed from industry codes and the subject's own named competitors; (2) add rivals named by competitors and in sell-side coverage lists; (3) LLM text-similarity on business descriptions (TNIC-style); (4) filter 0.3x–3x size, same regulatory regime, similar model; (5) keep 5–12 core and a labelled secondary set; (6) include exited and consolidated peers.

### 3.1 Maybank peer set

**Seed.** SSIC 64110 (central/commercial banking) → GICS 4010 Banks; competitors named in Maybank's own reporting are not quoted here because the 2025 IAR text could not be extracted **[VERIFY — pull the "competitive landscape" and risk sections]**; sell-side coverage universes (Kenanga, RHB Research, CGS) group Maybank with CIMB, Public Bank, RHB, Hong Leong Bank, AMMB in Malaysia ([Kenanga 4Q25 note](https://www.kenanga.com.my/wp-content/uploads/2026/02/MAYBANK-260227-4Q25-RN-Kenanga.pdf)); MAS licence list supplies the Singapore-present ASEAN banks ([Wikipedia list](https://en.wikipedia.org/wiki/List_of_banks_in_Singapore)). Long list: 19.

**Size filter.** Subject total assets ≈ RM1.1tn ≈ US$250bn **[VERIFY]** → band US$75bn–750bn. Text-similarity rule: universal/commercial bank, ASEAN home market, Singapore licence, listed.

**Core peers (n = 8)**

| # | Peer | Listing | Size metric | Why included | Data sources available |
|---|---|---|---|---|---|
| 1 | CIMB Group | Bursa (1023) | Total assets MYR 778.7bn ≈ US$164bn ([The Asian Banker](https://www.theasianbanker.com/press-releases/cimb-posts-fy2025-net-profit-of-1-7b-as-forward30-execution-progresses)) | Closest analogue: Malaysian universal bank, Singapore foreign full bank, Forward30 ≈ ROAR30 | IAR, quarterly analyst decks, Bursa filings, AI press ([Tech Wire Asia](https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/)) |
| 2 | UOB | SGX (U11) | Total assets S$572bn ([UOB AR2025](https://www.uobgroup.com/AR2025/index.html)) | ASEAN-wide retail franchise; Citi consumer acquisition; same MAS regime | AR, results-call transcripts, SGX filings |
| 3 | OCBC | SGX (O39) | Net profit S$7.42bn, PBT S$9.12bn ([OCBC AR2025](https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page)); total assets **[VERIFY]** | MAS regime; explicit "ADD" AI strategy; also parent of the insurer subject (note the linkage) | [AR2025 PDF](https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/annual-reports/2025/2025-annual-report-en.pdf), results calls |
| 4 | DBS | SGX (D05) | Total assets **[VERIFY]**; AI: >1,500 models / 370 use cases, ~S$750m economic value 2024, S$1bn target 2025 ([Tech Wire Asia](https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/)) | Leading-band anchor; three-bucket control-group value method [P12 in instrument] | AR, calls, Forrester case |
| 5 | Public Bank | Bursa (1295) | Total assets **[VERIFY ≈ US$120bn]** | Malaysian coverage universe; no Singapore bank licence → tests whether the "Singapore licence" rule should be hard | AR, Bursa filings |
| 6 | RHB Bank | Bursa (1066) | Total assets **[VERIFY ≈ US$80bn, near the 0.3x floor]** | Malaysian universal bank with Singapore foreign full bank licence | AR, Bursa filings |
| 7 | Bangkok Bank | SET (BBL) | Total assets **[VERIFY ≈ US$130bn]** | Thai universal bank; Singapore foreign full bank; Indonesia via Permata — same multi-country ASEAN shape | AR, SET filings, English analyst decks |
| 8 | Bank Mandiri | IDX (BMRI) | Total assets **[VERIFY ≈ US$140bn]** | Indonesian universal bank; Singapore foreign full bank; competes with Maybank Indonesia at home | AR, IDX filings, English results decks |

**Secondary tier (labelled, n = 9)**

| Peer | Why secondary | Note |
|---|---|---|
| Standard Chartered (Singapore) | Group >3x band; UK HQ | Singapore QFB; Singapore H1-25 profit ≈ S$1bn ([Fintech News SG](https://fintechnews.sg/118482/fintech/stanchart-singapore-profit/)); [investor overview Feb 2026](https://www.sc.com/en/uploads/sites/66/content/docs/standard-chartered-investor-overview-february-2026.pdf) |
| HSBC (Singapore) | Group far above band; Singapore not separately reported | QFB |
| Citibank Singapore | Group above band | QFB; retained Singapore consumer when it sold ASEAN consumer to UOB |
| Hong Leong Bank | Below 0.3x floor **[VERIFY]** | Malaysian; Singapore foreign full bank |
| Bank Negara Indonesia (BNI) | Near/below floor **[VERIFY]** | Singapore foreign full bank |
| Kasikornbank | No Singapore licence | Regional AI/tech reference (KBTG) |
| ANZ | Group above band; exited Asia retail | QFB (institutional only) |
| Hong Leong Finance / Sing Investments & Finance / Singapura Finance | SGX finance companies, far below floor | Singapore-only mid-cap reference points for a future SME-bank peer set |
| GXS Bank, MariBank, Trust Bank | Unlisted digital full banks | AI-native challengers; no financial comparability |

**Exited / consolidated peers (survivorship control)** — all **[VERIFY dates and terms from the acquirers' announcements; none of these were fetched in this run]**

| Event | Relevance |
|---|---|
| Citi's consumer businesses in Malaysia, Thailand, Indonesia and Vietnam sold to UOB (announced 2022) | Removes a direct ASEAN retail competitor; inflates UOB's digital metrics post-2022 |
| ANZ's Asia retail and wealth businesses (incl. Singapore) sold to DBS (announced 2016) | Exit of a QFB retail franchise |
| Barclays Asia wealth business sold to OCBC / Bank of Singapore (2016); ING Asia Private Bank sold to OCBC (2009) | Wealth consolidation into Singapore banks |
| ABN AMRO / RBS Singapore retail wind-down (c. 2010–11) | Foreign retail exit |
| Allianz–Income (insurance, 2024) and HSBC Life Singapore → Allianz (2026) | Bancassurance partner changes that affect bank fee lines (see 3.2) |

Peer-percentile note: §5.5 of the instrument requires n ≥ 15 scored peers; this set yields at most 8 core + 9 secondary, and only the core will be scored in G1. **The alpha scorecard must print "global, peer n insufficient".**

### 3.2 Great Eastern Holdings peer set

**Seed.** SSIC 65110 (life insurance) / 65120 (general insurance) → GICS 4030 Insurance; MAS insurer directory for Singapore-present entities ([MAS insurance company returns](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns)); LIA membership and industry statistics (TWNBP S$6.53bn in 2025, +11.3% ([LIA, 11 Feb 2026](https://www.lia.org.sg/news-room/industry-performance/2025/singapore-s-life-insurance-sector-achieves-113-growth-for-2025-with-s-653-billion-total-weighted-new-business-premiums))); competitors named in GEH's AR **[VERIFY — extract text]**; Malaysian coverage universe for GE Malaysia (Allianz Malaysia, Syarikat Takaful Malaysia, AIA Bhd unlisted). Long list: 18.

**Size filter.** Subject: "over S$122bn" assets ≈ US$90bn; profit S$1.2bn. Band ≈ US$27bn–270bn assets. Because most Singapore competitors are subsidiaries, the set is built in two layers: **core = Singapore operating entities compared on MAS-return metrics (assets, gross premiums, new business)**, so that unlisted peers are not dropped; **secondary = listed parent groups** used for AI-disclosure benchmarking.

**Core peers (n = 9, Singapore operating entities; size from MAS returns [VERIFY each])**

| # | Peer (Singapore entity) | Parent / listing | Size metric | Why included | Data sources available |
|---|---|---|---|---|---|
| 1 | AIA Singapore Pte Ltd (I566C) | AIA Group, HKEX 1299 | Segment VONB +14%, OPAT +5% ([AIA release](https://www.aia.com.sg/content/dam/sg-wise/en/docs/about-aia/press-release/2026/aia-delivers-record-results-in-2025.pdf)); MAS return assets **[VERIFY]** | #1/#2 Singapore life insurer by new business; agency-led like GE | MAS return, AIA AR segment tables, AIA calls |
| 2 | Prudential Assurance Co Singapore | Prudential plc, LSE/HKEX | Singapore NBP +2%, sales +5% ([transcript](https://www.prudentialplc.com/content/dam/prudential-plc/newsroom/company-news/2026/Presentation%20transcript.pdf)) | Agency + UOB/SCB bancassurance; most explicit AI operating metrics in the set | MAS return, Pru AR segment, calls |
| 3 | Income Insurance Ltd (I585C) | Unlisted (NTUC Enterprise) | Total assets S$47.2bn ([Wikipedia](https://en.wikipedia.org/wiki/Income_Insurance)) | Composite (life + general) like GEH; Singapore-only | [MAS return 2022–2025](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i585c), AGM slides |
| 4 | Singapore Life Ltd (Singlife) | Unlisted (Sumitomo Life) | MAS return assets **[VERIFY]** | Digital-first challenger; absorbed Aviva SG | MAS return, press |
| 5 | Manulife (Singapore) Pte Ltd (I522L) | Manulife, TSX/NYSE/HKEX 945 | MAS return assets **[VERIFY]** | DBS bancassurance partner | MAS return; parent AR (Singapore not broken out) |
| 6 | HSBC Life (Singapore) | HSBC → Allianz (announced 28 Jul 2026, ≈€2bn, completion 1H27, 15-year distribution deal ([Atlas Magazine](https://atlas-mag.net/en/articles/allianz-acquire-hsbc-life-singapore))) | MAS return assets **[VERIFY]** | In-flight consolidation; ex-AXA Singapore | MAS return |
| 7 | Tokio Marine Life Insurance Singapore | Tokio Marine Holdings, TSE | MAS return assets **[VERIFY]** | Agency-led life insurer | MAS return |
| 8 | Etiqa Insurance Singapore | Maybank (Bursa) | MAS return assets **[VERIFY]** | Bank-owned composite; links the two alpha subjects (Maybank owns Etiqa; OCBC owns GE) | MAS return, Maybank IAR |
| 9 | China Taiping Insurance (Singapore) | China Taiping Insurance Holdings, HKEX 966 | MAS return assets **[VERIFY]** | Composite; growing life book | MAS return |

**Secondary tier (listed groups and regional comparators, labelled)**

| Peer | Listing | Why secondary |
|---|---|---|
| AIA Group (whole) | HKEX 1299 | Total assets US$345bn = 3.8x subject, above band; AI-disclosure benchmark only |
| Prudential plc (whole) | LSE/HKEX | Above band at group level; AI-disclosure benchmark |
| FWD Group | HKEX 1828 (listed 7 Jul 2025) | AUM ≈ US$62.4bn, in band; Singapore business small ([Wikipedia](https://en.wikipedia.org/wiki/FWD_Group)) |
| Manulife, Sun Life, Allianz SE, Tokio Marine Holdings, Sumitomo Life (mutual) | TSX / TSX / Xetra / TSE / unlisted | Parents of core peers; used only for AI-governance and spend disclosures |
| Allianz Malaysia Bhd; Syarikat Takaful Malaysia Keluarga; Hong Leong Assurance (via HLFG) | Bursa | GE Malaysia's listed competitors; in-band on a Malaysia-entity basis **[VERIFY sizes]** |
| Thai Life Insurance; Bangkok Life Assurance | SET | ASEAN listed life insurers for the regional percentile when n is short |
| United Overseas Insurance | SGX U13 | SGX-listed general insurer; below floor; general-business comparator only |

**Exited / consolidated peers (survivorship control)**

| Event | Status | Source |
|---|---|---|
| Aviva Singapore → Singlife (2020) | Consolidated | **[VERIFY]** |
| AXA Insurance Singapore → HSBC (2022) | Consolidated | **[VERIFY]** |
| Allianz's offer for ≥51% of Income Insurance withdrawn (Dec 2024) after Government block (Oct 2024) | Failed consolidation | [Wikipedia](https://en.wikipedia.org/wiki/Income_Insurance); [Insurance Journal](https://www.insurancejournal.com/news/international/2026/07/24/878902.htm) |
| HSBC Life Singapore → Allianz (announced Jul 2026) | Pending | [Atlas Magazine](https://atlas-mag.net/en/articles/allianz-acquire-hsbc-life-singapore) |
| Sumitomo Life takes 100% of Singlife (2024) | Ownership change | [Insurance Business Asia](https://www.insurancebusinessmag.com/asia/news/breaking-news/giant-japanese-insurer-looking-south-and-to-the-us-for-deals-593771.aspx) |
| FWD exits Singapore group medical (2020) | Line exit | [Wikipedia](https://en.wikipedia.org/wiki/FWD_Group) |
| Zurich Life Singapore exit (c. 2015) | Exit | **[VERIFY]** |
| OCBC's two offers for GEH (2024, 2025); delisting failed | Subject's own near-exit | §1.2 sources |

Peer-percentile note: 9 core entities, of which only ~4 have any public AI disclosure; **n < 15, so the scorecard prints "global, peer n insufficient"**. The MAS per-insurer returns make the *financial* KPI percentile (assets, premium growth, expense ratio) feasible on n = 9; the *maturity* percentile is not.

---

## 4. Outside-in maturity signal plan

Rules carried from the instrument §5.4: proxies corroborate only, never lift above level 3; narrative signals are outweighed by hiring and patent evidence. Each proxy below is tagged with the dimension(s) it feeds and the source to use for each subject.

| Proxy (instrument reference) | Maybank — source | GEH — source | Feasibility in G1 |
|---|---|---|---|
| Annual-report AI paragraph scored on the Yu et al. 1–5 rubric (D1.1, D5.4, D8.3) | 2025 IAR — mirror at [BankTrack](https://www.banktrack.org/download/annual_report_2025_28) (download and run text extraction locally; fetch returned binary) + 4Q25 deck ([Maybank](https://www.maybank.com/iwov-resources/documents/pdf/quarterly-report/2025/maybank-group-analyst-presentation-fy2025-4q.pdf)) | [AR FY2025 (SGX)](https://links.sgx.com/1.0.0/corporate-announcements/LNEPNAAMA9G4OO20/880681_GEH%20Annual%20Report%20FY2025.pdf) (links.sgx.com was 403 from this sandbox — download from a desktop) + [FY-25 release](https://www.greateasternlife.com/sg/en/about-us/media-centre/media-releases/fy-25-financial-results.html) | Yes — needs a local PDF text pass; two raters score the rubric for the κ test |
| Earnings-call AI semantic density (D1.1, D8.6) | Quarterly analyst briefings; transcripts **[VERIFY availability — Maybank publishes decks; Q&A transcripts not confirmed]** | **No earnings calls found [VERIFY]** — substitute OCBC's results-call Q&A on GE and GEH quarterly releases | Partial for Maybank; proxy-by-parent for GEH (label as such) |
| Investor-day / strategy AI targets (D1.1, D1.4, D1.6) | ROAR30 (RM10bn tech/data/AI over five years; ROE 13–14% by 2030) ([Fintech News MY](https://fintechnews.my/56126/banking/maybank-roar30-strategy-rm10-billion-technology-investment/)) | None found; OCBC "ADD" strategy at parent ([OCBC](https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page)) | Yes / parent-only |
| Disclosed AI spend or IT-budget share (D1.4) | RM10bn envelope; RM1bn Microsoft deal ([DCD](https://www.datacenterdynamics.com/en/news/microsoft-scores-2364m-deal-with-malaysian-financial-group-maybank/)); IT opex line in IAR **[VERIFY]** | Not disclosed; expense lines in AR **[VERIFY]** | Yes / no |
| AI-skill share of job postings over 24 months (D4.1, D2.2, D3.2, D4.5, D6.2) | MyCareersFuture (Maybank Singapore Ltd), LinkedIn Jobs, maybank.com careers; count postings with AI/ML/LLM/data-science terms ÷ total, monthly | MyCareersFuture (Great Eastern Life / GE General), LinkedIn, GE careers site | Yes, with scraping budget (Bright Data metered, per the data annex); volumes **[VERIFY]** |
| Leadership structure: CAIO/CDO, reporting line, tenure (D1.2, D2.1, D5.2) | IAR leadership pages; LinkedIn; press on Group Chief Technology/Data roles **[VERIFY titles]** | AR management pages; LinkedIn; OCBC group CDO/CTO roles **[VERIFY]** | Yes |
| Patents, open-source, conference talks (D4.2, D1.5) | Google Patents / MyIPO / IPOS search on "Malayan Banking"; GitHub org; SFF / Money20/20 Asia speaker lists | IPOS search on "Great Eastern Life"; SFF speaker lists | Yes; expect near-zero patents (banks rarely file in ASEAN) — report as such, not as L1 |
| Hyperscaler / vendor announcements and technographics (D3.1, D3.4) | Microsoft Azure + Copilot ([DCD](https://www.datacenterdynamics.com/en/news/microsoft-scores-2364m-deal-with-malaysian-financial-group-maybank/)); BuiltWith on maybank2u.com.sg | BuiltWith on greateasternlife.com; vendor case studies **[VERIFY]** | Yes |
| Pilot-vs-production language ratio in press over 24 months (D5.4) | Maybank newsroom ([maybank.com/en/news](https://www.maybank.com/en/news/2025/02/26.page)); Maybank Singapore newsroom ([maybank2u.com.sg](https://www.maybank2u.com.sg/en/personal/about_us/maybank-singapore/newsroom/2025/26-may-2025.page)) | GE media centre ([greateasternlife.com](https://www.greateasternlife.com/sg/en/about-us/media-centre/media-releases/fy-25-financial-results.html)) — FY25 release already distinguishes "rolled out" (claims) from "being tested" (underwriting) | Yes |
| RAI policy, ISO 42001, AI Verify participation, incident disclosures (D6.1–D6.6) | IAR risk section; BNM/MAS enforcement history; AI Verify Foundation member list **[VERIFY]** | AR risk section; MAS enforcement; FEAT/Veritas participation **[VERIFY]** | Yes (document evidence class D — the one proxy that *can* lift D6.1 above 3 if a published policy qualifies) |
| Regulator-published returns for financial KPIs (value axis context) | MAS does not publish per-bank returns; use Maybank Singapore Limited statutory accounts **[VERIFY public]** + BNM data | [MAS per-insurer returns](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns) (I516L etc.), LIA quarterly releases ([4Q2025](https://www.lia.org.sg/media/4789/20260211_lia-4q2025-results_media-release.pdf)) | Partial / yes |
| Employee-review sentiment on AI tools, app-store release cadence (D7.1, D7.5, D5.3) | Glassdoor/JobStreet reviews; MAE and Maybank2u SG app release notes | Glassdoor; GE app release notes | Yes, estimate-grade; label "vendor-estimate / model-inferred" |

Expected ceiling: with no client, every item is capped at level 3 (§5.4) except where a public document of the required class exists (e.g. D6.1 policy, D1.1 board-approved strategy). The alpha capability scores will therefore cluster at or below 50 and must be reported as **"outside-in pre-score, self-report absent"**, not as a maturity result.

---

## 5. Data the alpha does not need, and how Phase 2 is simulated

### 5.1 Client data requests that are skipped (no client exists)

From the Phase 0 list in the framework and the evidence classes in the instrument:

| Data request (normal engagement) | Instrument items it unlocks | Alpha treatment |
|---|---|---|
| P&L and KPI extracts by segment; driver-tree inputs | V1, D8.1–D8.6 | Replaced by segment disclosures (Maybank Singapore PBT/net income; GEH NBEV/TWNS) — value axis reported as "not evidenced" (Band A) |
| Portfolio register / use-case inventory with owners | D1.3, D5.4, D6.2, V2 | Reconstructed from press and AR; V2 capped at the 12–39% band by rule |
| AI policy, acceptable-use policy, SoA, internal-audit reports | D6.1, D6.3 | Only if published; else L≤3 |
| Model inventory extract, lineage, eval/deployment logs | D2.5, D3.2, D6.2, D6.5 | Not obtainable; items scored on proxies only and flagged "no S evidence" |
| HRIS / LMS extracts (bench size, upskilling completion) | D4.2, D4.3 | Job-posting share and public upskilling pledges only |
| Usage telemetry for sanctioned AI tools | D7.1, D7.4 | Copilot seat count (Maybank 44,000) is a *deployment* signal, not usage; scored ≤2 |
| Finance-approved attribution rule and value ledger | D8.3, D8.4, V3 | DBS-style public value statements exist for peers, not for the subjects; V3 ≤ 2 |
| Customer lists for win/loss, switch and churn interviews | Right-to-win kit | Not run; see 5.2 |
| 10–30 leader self-assessment | §5.3 variance, every item's self-report | Not run; σ, alignment index and ExCo-vs-operating gap **cannot be produced** |

### 5.2 Phase 2 simulation

| Phase 2 input | Simulated by | Limits |
|---|---|---|
| 6–10 executive interviews ("state it / live it", three circles) | Public CEO/CTO interviews and briefings: Maybank Group CEO statements on ROAR30 and the Microsoft deal ([DCD](https://www.datacenterdynamics.com/en/news/microsoft-scores-2364m-deal-with-malaysian-financial-group-maybank/); [Fintech News MY](https://fintechnews.my/56126/banking/maybank-roar30-strategy-rm10-billion-technology-investment/)); CIMB Singapore CEO briefing as a peer comparator ([finews.asia](https://www.finews.asia/finance/43676-cimb-malaysia-bank-singapore-wealth-treasury-johor-sez-novan-amirudin-victor-lee-asean)); GEH quarterly release narrative; OCBC Group CEO perspectives ([OCBC](https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page)); conference talks (SFF, Money20/20 Asia) **[VERIFY availability of recordings]** | One-directional, PR-filtered; cannot probe; no "≥2 independent interviewees agree" (I evidence) → items with Ev≥4 = I (D4.4, D7.2, D7.3) stay ≤3 and are flagged "I evidence unavailable" |
| Analyst Q&A | Maybank quarterly briefings (if transcripts exist **[VERIFY]**); AIA and Prudential results calls as peer Q&A; OCBC results-call questions on GE | Sell-side questions rarely touch operating-model or governance items (D5, D6); density proxy only |
| 8–12 win/loss, switch and churn interviews | Not simulated. Substitute: app-store reviews, Glassdoor, LIA market-share movement, NPS Prism banking benchmark if licensed (data annex) | Anecdote-grade; no timeline protocol; label "interview-anecdote" per the data-confidence scheme |
| Leader self-assessment (10–30 respondents) | **Not simulated.** Two PLUMB raters score the 20-item κ subset from the same public evidence pack instead (instrument §7) | This converts the alpha from a maturity assessment into an **inter-rater reliability and pipeline test**, which is its real G1 purpose. The perception-variance output is untestable until a design partner supplies respondents |
| QA gate 2 (quote-to-transcript verification) | Every quote string-matched to the fetched page or PDF; URL health-checked | Works as designed; this is the part of the pipeline the alpha genuinely exercises |

**Honest statement for the G1 review.** The alpha can validate the verification pipeline, the peer-set funnel, the outside-in proxy layer and rater agreement on public evidence. It cannot validate the instrument's self-report cap rule, the variance statistics, the value axis, or the evidence-coverage threshold (60%) — those require a client or design partner, which is the G2 exit criterion.

---

## 6. Main data gaps carried forward

1. Full-text extraction of both 2025 annual reports (SGX and BankTrack PDFs returned binary / 403 in this sandbox) — needed for the rubric score, named-competitor seed and leadership-structure proxy.
2. Maybank group total assets, OCBC/DBS/Public Bank/RHB/Bangkok Bank/Mandiri total assets, and every MAS-return asset figure for the nine insurer entities (all marked [VERIFY]) — needed to apply the 0.3x–3x filter numerically rather than by recollection.
3. Whether Maybank Singapore Limited's statutory financial statements and any Maybank briefing transcripts are public.
4. Exact post-bonus OCBC ordinary-share percentage in GEH (88.19% vs 88.44% in secondary sources).
5. Job-posting volumes (24-month series) for both subjects — not yet collected.
6. Founder's conflict declaration (C6) for Maybank, OCBC/GEH and the Microsoft relationship.
7. Dates and terms of the exited-peer events listed without a fetched source (Citi→UOB, ANZ→DBS, Barclays/ING→OCBC, Aviva→Singlife, AXA→HSBC, Zurich exit).

---

## 7. Source list (fetched or returned by search on 2026-10-25)

- Great Eastern: [FY-25 results release](https://www.greateasternlife.com/sg/en/about-us/media-centre/media-releases/fy-25-financial-results.html); [AR FY2025 (SGX)](https://links.sgx.com/1.0.0/corporate-announcements/LNEPNAAMA9G4OO20/880681_GEH%20Annual%20Report%20FY2025.pdf); [AR announcement](https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/20260327-ar-fy2025-announcement.pdf); [The Independent SG](https://theindependent.sg/great-eastern-to-resume-trading-after-less-than-75-voted-in-favour-of-delisting-proposal-ocbc-says-no-further-offers-in-the-foreseeable-future/); [Caproasia](https://www.caproasia.com/2025/08/15/singapore-insurance-giant-great-eastern-holdings-to-resume-trading-on-singapore-exchange-sgx-on-21st-august-2025-after-shareholders-voted-to-resume-trading-restore-free-float-requirement-new-non/); [TipRanks](https://www.tipranks.com/news/company-announcements/great-eastern-holdings-resumes-trading-and-announces-dividend-increase); [OCBC statement on resolutions B and C](https://www.ocbc.com/group/media/release/2025/ocbc-statement-on-the-approval-of-great-eastern-holdings-resolutions-b-and-c.page)
- Maybank: [FY2025 results (Edge/Yahoo)](https://sg.finance.yahoo.com/news/maybank-fy2025-net-profit-gains-005205385.html); [4Q FY2025 analyst presentation](https://www.maybank.com/iwov-resources/documents/pdf/quarterly-report/2025/maybank-group-analyst-presentation-fy2025-4q.pdf); [The Asian Banker FY25](https://www.theasianbanker.com/press-releases/maybank-fy25-roe-rises-to-11-7-as-net-profit-reaches-2-3b-and-casa-ratio-strengthens-to-40-5); [ROAR30 (Fintech News MY)](https://fintechnews.my/56126/banking/maybank-roar30-strategy-rm10-billion-technology-investment/); [ROAR30 (Asian Banker)](https://www.theasianbanker.com/press-releases/maybank-launches-roar30-targets-roe-of-13-14-by-2030); [Microsoft deal (DCD)](https://www.datacenterdynamics.com/en/news/microsoft-scores-2364m-deal-with-malaysian-financial-group-maybank/); [Tech Wire Asia ASEAN bank AI](https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/); [MAS incorporation approval (APB)](https://asianprivatebanker.com/private-banking-wealth-management/maybank-wins-mas-approval-singapore-incorporation-community-financial-services/); [2025 IAR mirror (BankTrack)](https://www.banktrack.org/download/annual_report_2025_28); [Kenanga 4Q25 note](https://www.kenanga.com.my/wp-content/uploads/2026/02/MAYBANK-260227-4Q25-RN-Kenanga.pdf)
- CIMB: [FY2025 release](https://www.cimb.com/en/newsroom/2026/cimb-delivers-net-profit-of-rm7-9-billion-with-roe-at-11-3-percent-strengthens-long-term-value-creation-for-shareholders.html); [The Asian Banker FY2025](https://www.theasianbanker.com/press-releases/cimb-posts-fy2025-net-profit-of-1-7b-as-forward30-execution-progresses); [finews.asia Singapore briefing](https://www.finews.asia/finance/43676-cimb-malaysia-bank-singapore-wealth-treasury-johor-sez-novan-amirudin-victor-lee-asean)
- Hong Leong Finance: [AR 2025 (SGX)](https://links.sgx.com/1.0.0/corporate-announcements/YEVJ5R1L4F4E2JZJ/880350_Hong%20Leong%20Finance%20Annual%20Report%202025.pdf); [FY2025 results (iTiger)](https://www-web.itiger.com/news/1157586943); [hlf.com.sg FY results](https://www.hlf.com.sg/downloads/financial_result/2025/fh2025fy.pdf)
- UOB: [AR2025 microsite](https://www.uobgroup.com/AR2025/index.html); [AR2025 PDF](https://www.uobgroup.com/investor-relations/assets/pdfs/investor/annual/uob-annual-report-2025.pdf); [The Asian Banker FY2025](https://www.theasianbanker.com/updates-and-articles/uob-reports-5-7-billion-net-profit-after-pre-emptive-provisions-as-fee-income-reaches-record)
- OCBC: [AR2025 Group CEO perspectives](https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page); [AR2025 PDF](https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/annual-reports/2025/2025-annual-report-en.pdf)
- Standard Chartered: [Fintech News SG Singapore profit](https://fintechnews.sg/118482/fintech/stanchart-singapore-profit/); [Investor overview Feb 2026](https://www.sc.com/en/uploads/sites/66/content/docs/standard-chartered-investor-overview-february-2026.pdf)
- AIA: [2025 results release](https://www.aia.com.sg/content/dam/sg-wise/en/docs/about-aia/press-release/2026/aia-delivers-record-results-in-2025.pdf); [AIA filing](https://aia.gcs-web.com/static-files/884813c0-dc66-4696-9023-bbf7f8253e62)
- Prudential: [FY2025 presentation transcript](https://www.prudentialplc.com/content/dam/prudential-plc/newsroom/company-news/2026/Presentation%20transcript.pdf); [Q1 2026 update](https://www.prudentialplc.com/en/newsroom/company-news/2026/prudential-plc-q1-business-performance-update/)
- Manulife: [Insurance Business 2025 results](https://www.insurancebusinessmag.com/us/news/life-insurance/manulife-sets-record-2025-core-earnings-as-asia-and-global-wam-power-growth-565136.aspx)
- Singlife / Sumitomo: [Insurance Business Asia, 16 Oct 2026](https://www.insurancebusinessmag.com/asia/news/breaking-news/giant-japanese-insurer-looking-south-and-to-the-us-for-deals-593771.aspx)
- Income: [Wikipedia](https://en.wikipedia.org/wiki/Income_Insurance); [MAS return I585C](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i585c); [Insurance Journal, 24 Jul 2026](https://www.insurancejournal.com/news/international/2026/07/24/878902.htm)
- HSBC Life SG → Allianz: [Atlas Magazine](https://atlas-mag.net/en/articles/allianz-acquire-hsbc-life-singapore)
- UOI: [FY2025 (iTiger)](https://www-web.itiger.com/news/1172397258); [AR 2025 (SGX)](https://links.sgx.com/1.0.0/corporate-announcements/10HJ7VSC02FVI5Z4/881515_UOI%20Annual%20Report%202025.pdf)
- FWD: [Wikipedia](https://en.wikipedia.org/wiki/FWD_Group)
- Regulator / industry: [MAS insurance company returns](https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns); [MAS annual insurance statistics](https://www.mas.gov.sg/Statistics/Insurance-Statistics.aspx); [LIA 2025 industry results](https://www.lia.org.sg/news-room/industry-performance/2025/singapore-s-life-insurance-sector-achieves-113-growth-for-2025-with-s-653-billion-total-weighted-new-business-premiums); [LIA 4Q2025 release PDF](https://www.lia.org.sg/media/4789/20260211_lia-4q2025-results_media-release.pdf); [Wikipedia list of banks in Singapore](https://en.wikipedia.org/wiki/List_of_banks_in_Singapore)
- Conflict screen: [Dell Emirates NBD case study (only bank story returned)](https://www.delltechnologies.com/asset/en-hk/products/storage/customer-stories-case-studies/emirates-nbd-bank-written-case-study.pdf)
