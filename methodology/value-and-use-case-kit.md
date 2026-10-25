# VALUE POOL & USE-CASE KIT v0.1

**Status: v0.1 draft, untested**

| Field | Value |
|---|---|
| Owner | Methodology lead (AI-first consulting firm, Singapore/APAC) |
| Scope | Steps 2 and 3 of the AI Journey Diagnostic: locate the 3–5 value pools, then select and business-case 9–15 use cases inside them |
| Upstream | `/home/claude/reports/AI first consulting engagement framework.md`; research notes `value_pool_identification.md`, `ai_use_case_libraries.md` |
| Companion file | `/home/claude/workspace/catalogue/use-case-catalogue-seed.csv` (25 seed rows) |
| Evidence rule | Every number below carries a URL from the research notes. No URL in this kit was introduced outside those notes. Vendor-reported figures are labelled T4 and are directional only. |

## Change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1 | 2026-10-25 | First draft assembled from research notes. Untested on a live engagement. | Methodology drafting |
| v0.2 | — | (reserved) First-engagement calibration: replace placeholder anchors, add client-tested weights | — |

## How the kit fits together

| Step | Tool | Output | Section |
|---|---|---|---|
| 1 | Driver tree | Where the P&L and balance sheet move, as operational KPIs with outside-in sources | 1 |
| 2 | Domain scan and screen | 10–15 candidate domains screened to 2–5; each sized in two bands | 2 |
| 3 | Use-case matrix | 3–5 gated, scored, laddered use cases per domain (9–15 per engagement) | 3 |
| 4 | Business-case template | 7-section CFO-grade case per selected use case | 4 |
| 5 | Failure-rate reference | Calibration and board-level caveats | 5 |
| 6 | Catalogue | Seed library to generate candidates inside domains | 6 |

Design rule carried from the framework report: a use case that does not sit inside one of the 2–5 domains, with an owner, a system-measured baseline and a control group, is not recommended. McKinsey's own verdict on catalogue-first work is that it "failed to scale and never showed up on the P&L" and that fewer than 10% of vertical use cases get past pilot ([McKinsey WIRED](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/wired-the-ai-playbook-top-companies-use), [McKinsey agentic](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)).

---

## 1. Driver tree template

Basis: McKinsey's ROIC driver tree for industrial transformations, which splits operating profitability (revenue, operating cost, cash generation) from capital efficiency (level and productivity of invested capital), decomposes each to operational KPIs, and excludes balance-sheet financing KPIs as non-operational ([McKinsey, Selecting P&L-linked KPIs](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/selecting-p-and-l-linked-kpis-for-industrial-transformations)). The same source found firms use only 29% of their defined KPIs in decision-making, so the tree should be pruned to leaves that have an owner. The risk branch is the kit's addition: expected loss = frequency × severity, so that "avoid risk" value sits on the same tree as revenue and cost.

Economic profit = NOPLAT − (invested capital × WACC). Outside-in source conventions: AR = annual report / SGX, ASX, EDINET, DART or ACRA filing; EC = earnings-call transcript; JP = job postings; APP = app-store ratings and reviews; REG = regulator enforcement and breach notices; IND = industry benchmark (named in the leaf).

- **Economic profit (ROIC − WACC) × invested capital**
  - **A. Revenue** (KPI: revenue growth vs peer median; source: AR segment note, EC)
    - A1. Price (KPI: price realisation / net price index vs list; source: AR gross-margin bridge, EC pricing commentary, competitor price scrapes)
      - Discounting leakage (KPI: discount % of list by channel; source: client extract; outside-in proxy from promo monitoring)
      - Pricing-power test (KPI: gross margin percentile vs peers, top-30% = differentiated; source: AR, [McKinsey power curve](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategy-to-beat-the-odds))
    - A2. Volume (KPI: units / active customers / transactions; source: AR operating statistics, regulator market-share data)
      - Acquisition (KPI: lead-to-close conversion, CAC; source: JP for sales headcount ratio, APP download rank)
      - Share of wallet (KPI: products per customer, value per customer; source: AR, EC)
    - A3. Mix (KPI: margin-weighted product/channel/region mix; source: AR segment split; digital channel share, e.g. Singtel ~50% of transactions digital, [Singtel SGX](https://links.sgx.com/1.0.0/corporate-announcements/423V7E007WOXU5ET/902534_Investor%20Day%202026%20-%20Singtel%20SG.pdf))
    - A4. Retention (KPI: churn %, NRR, NPS; source: AR churn disclosure for telcos/SaaS, APP review sentiment, NPS Prism-type proxies)
      - Benchmark anchor: Singtel 17% lower churn on main brand after AI programme ([Singtel SGX](https://links.sgx.com/1.0.0/corporate-announcements/423V7E007WOXU5ET/902534_Investor%20Day%202026%20-%20Singtel%20SG.pdf))
    - A5. New products and services (KPI: revenue from products <3 yrs old, time-to-market; source: AR, EC, patent filings, JP for product roles)
      - Benchmark anchor: BCG CPG Invent case $200M+ incremental sales; 3–6 months faster time-to-market ([BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf))
  - **B. Operating cost** (KPI: EBIT margin vs peer median; source: AR)
    - B1. COGS / cost of service (KPI: gross margin %, BOM cost per unit, OEE = availability × performance × quality, yield, logistics cost per unit, OTIFQ; source: AR, IND benchmarks; [McKinsey KPI list](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/selecting-p-and-l-linked-kpis-for-industrial-transformations))
      - Procurement (KPI: purchase price variance, % spend under management; AI ceiling 2–3% commodities / 5–10% other directs / 10–15% indirects and tail, [Activant](https://www.activantcapital.com/pdfs/ai-in-procurement.pdf))
      - Direct labour (KPI: overtime ratio, contractor ratio, freed capacity in hours, 1,800 h/yr = 1 FTE; source: JP, AR headcount note)
    - B2. SG&A by function (KPI: function cost as % of revenue vs peer; source: AR, JP headcount ratios)
      - Customer operations (KPI: cost per contact, AHT, first-contact resolution, containment rate; MGI ceiling 30–45% of function cost; RCT evidence +14% issues/hour, [NBER w31161](https://www.nber.org/papers/w31161))
      - Marketing (KPI: marketing % of revenue, agency spend, ROAS; MGI ceiling 5–15%; agency cuts 20–30%, [BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf))
      - Sales (KPI: sales cost % of revenue, quota attainment, lead qualification time; MGI ceiling 3–5%)
      - Software engineering / IT (KPI: IT cost % of revenue, ticket volume, release effort; MGI ceiling 20–45%, honest senior-dev band 0–15%, [METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), [METR update](https://evals.alignment.org/blog/2026-02-24-uplift-update/))
      - R&D (KPI: R&D % of revenue, cycle time; MGI ceiling 10–15%)
      - Finance, HR, legal, risk (KPI: close days, cost per hire, external counsel spend; MIT NANDA anchors $2–10M/yr BPO elimination, $1M/yr outsourced risk, [MIT NANDA](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf))
    - B3. Working capital (KPI: DSO, DIO, DPO, cash conversion cycle days; source: AR balance sheet)
      - Inventory (KPI: days inventory, forecast error, stock-outs; anchor Toyota ~$800M supply-chain twin, [McKinsey WIRED](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/wired-the-ai-playbook-top-companies-use))
      - Receivables and collections (KPI: DSO, overdue %, dispute cycle time)
    - B4. Capex and asset productivity (KPI: capex/sales percentile, asset turnover, utilisation; source: AR cash-flow statement; capex/sales top-20% is a McKinsey "big move" threshold, [McKinsey power curve](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategy-to-beat-the-odds))
      - Maintenance and downtime (KPI: unplanned downtime hours, MTBF; source: IND)
      - Network / plant energy (KPI: energy per unit; anchors Rakuten up-to-20% network energy projection, [Rakuten](https://rakuten.today/blog/rakuten-ai-in-2025-embracing-agentic-ai.html); Schneider 5–15% energy savings, [CIO.com/WEF](https://www.cio.com/article/4122937/davos-from-hype-to-ai-transformation-in-the-economy.html))
  - **C. Risk: expected loss = frequency × severity** (KPI: expected annual loss, loss events per year, regulatory capital or provisions; source: AR risk note, REG)
    - C1. Compliance and regulatory (KPI: fines and remediation cost, AML/KYC alert volume and false-positive rate, audit findings; anchors OCBC AML system >10,000 mostly false-positive alerts/month at ~45 min each, [Microsoft Source Asia](https://news.microsoft.com/source/asia/features/ocbcs-new-generative-ai-chatbot-is-boosting-the-banks-productivity-across-departments-and-locations/); EU AI Act fines up to €35M or 7% of turnover, [Elevate Consult](https://elevateconsult.com/insights/ai-governance-frameworks-compared-matching-nist-eu-ai-act-and-iso-42001-to-your-use-case/))
    - C2. Cyber and data (KPI: breach probability × cost; anchors $4.44M global average breach, $10.22M US, $7.42M healthcare, $1.9M saved with extensive security AI, 241-day lifecycle, +$670K with high shadow AI, [IBM via Help Net Security](https://helpnetsecurity.com/2025/08/04/ibm-cost-data-breach-report-2025))
    - C3. Fraud and scam loss (KPI: fraud loss bps of payment volume, false-positive rate; anchors CBA scam losses −50%, fraud −30%, [CFOtech AU](https://www.cfotech.com.au/story/commonwealth-bank-uses-ai-to-enhance-customer-service); Macquarie false positives −40%, [Google](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/gen-ai-business-use-cases/))
    - C4. Operational (KPI: error and exception rates, rework cost, SLA breaches, outage minutes; source: client systems; IND for outage cost)
    - C5. Reputational and AI-specific (KPI: complaint volume, media sentiment, AI incident count; anchor Klarna reversal after 700-agent claim, [eMarketer](https://www.emarketer.com/content/klarna-backtracks-ai-customer-service-plans); 51% of firms report ≥1 negative AI consequence, [McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-state-of-ai-2025))
    - C6. Agent-governance gap (KPI: share of agents with full control set; anchor only 5% of firms have it while 42% expect to grant decision authority by 2030, [BCG, Sep 2026](https://www.bcg.com/press/30september2026-ai-starting-to-pay-off-companies-generate-value))

**Tree rules**

| Rule | Detail |
|---|---|
| One KPI per leaf | A leaf with no measurable KPI is deleted, not kept as narrative |
| Source label per leaf | Each KPI tagged: filed / vendor-estimate / model-inferred / interview-anecdote (framework report, Phase 1) |
| Two-band sizing per branch | Technical-potential band (MGI ceilings) and realised-to-date band (2026 survey base) — see Section 2.4 |
| Top-line first | >50% of transformation value comes from top-line initiatives; do not let the tree collapse into a cost exercise ([McKinsey, How bold](https://www.mckinsey.de/capabilities/transformation/our-insights/how-bold-is-your-business-transformation-a-new-way-to-measure-progress)) |
| Long tail | ~55% of value comes from small initiatives each <0.5% of full potential; the pipeline behind the headline domains must be oversized (same source) |

---

## 2. Domain scan and screen

### 2.1 Definitions and counts

| Term | Definition | Source |
|---|---|---|
| Domain | "A subset of your enterprise that encapsulates a cohesive set of related activities": a customer journey, end-to-end process or organisational unit | [McKinsey, bite size](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size) |
| Count for a monoline business | ~10–15 domains | same |
| Start with | 2–5 domains; up to 80% of successful interventions in struggling transformations re-anchored on a well-defined domain | same |
| BCG equivalent | 3–5 functions or processes across Deploy / Reshape / Invent; target 2–3x ROI | [BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf) |
| BCG 2025 variant | One or two domains for end-to-end AI-first redesign; jumping to Reshape without capabilities "typically fails" | [BCG Oct 2025](https://media-publications.bcg.com/The-Widening-AI-Value-Gap-October-2025.pdf) |
| Leader behaviour | Leaders prioritise ~3.5 use cases vs 6.1 for others; pursue about half as many opportunities and scale >2x as many | [BCG AI Radar 2025](https://web-assets.bcg.com/0b/f6/c2880f9f4472955538567a5bcb6a/ai-radar-2025-slideshow-jan-2025-r.pdf), [BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value) |
| PE equivalent | ≤8–10 levers, each "named, sized, sequenced, owned, tracked" | [VCP guide](https://www.notveryprivateequity.com/what-is-a-value-creation-plan-in-private-equity/) |

### 2.2 Enumerating 10–15 candidate domains

Procedure (run in Phase 1–2, 2–3 hours of analyst time plus one client workshop):

| Step | Action | Output |
|---|---|---|
| 1 | Lay the client's business on a capability map (BIAN for banking; generic process map otherwise). BIAN 14.0 is a capability map to hang use cases on, not a use-case library ([BIAN](https://bian.org/news-room/bian-unveils-new-service-landscape-14-0-to-accelerate-ai-ready-banking-architecture/)) | Level-1 capability list |
| 2 | Cut the map three ways: customer journeys (acquire, onboard, serve, retain, recover), core operating processes (plan, source, make/deliver, maintain), support functions (finance, HR, IT, legal/risk) | Raw list, typically 18–25 |
| 3 | Merge until each domain is "large enough to be valuable and noticeable, small enough to be transformed" ([McKinsey, bite size](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size)) | 10–15 domains |
| 4 | Attach each domain to the driver-tree branches it moves (A/B/C leaves) | Domain-to-KPI map |
| 5 | Tag each domain core or support. Core = revenue-generating or primary operations; support = IT, procurement, customer service as cost centre, finance, HR | Core/support tag |
| 6 | Pull the industry first-domain heuristic (2.5) and the right-to-win "eroding / hollowing" tags from Step 1 of the diagnostic; an eroding strength is a value pool | Pre-screen flags |

Default generic domain list for a monoline business (adapt, do not copy):

| # | Domain | Type | Typical tree branches |
|---|---|---|---|
| 1 | Customer acquisition and marketing | Core | A2, A5, B2-marketing |
| 2 | Sales and pricing | Core | A1, A2, B2-sales |
| 3 | Onboarding / origination (KYC, credit, contracting) | Core | A2, B2, C1 |
| 4 | Customer service and contact centre | Core or support | A4, B2-customer ops, C5 |
| 5 | Retention, cross-sell and personalisation | Core | A3, A4 |
| 6 | Product and R&D | Core | A5, B2-R&D |
| 7 | Demand planning and supply chain | Core | B1, B3 |
| 8 | Production / service delivery / network operations | Core | B1, B4 |
| 9 | Procurement | Support | B1-procurement |
| 10 | Field service and maintenance | Core | B4, C4 |
| 11 | Fraud, financial crime and compliance | Core (regulated) / support | C1, C3 |
| 12 | Finance, close and collections | Support | B2-finance, B3 |
| 13 | Software engineering and IT operations | Support | B2-IT |
| 14 | HR and talent | Support | B2-HR |
| 15 | Cyber and AI governance | Support | C2, C6 |

### 2.3 Value × feasibility screen

Criteria are McKinsey's domain-prioritisation set ([McKinsey, bite size](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size)); anchors are this kit's and are untested.

**Value axis** (score 1–5 each; CX is "first among equals")

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Customer-experience impact | No customer touchpoint affected | Secondary touchpoint; CX metric moves indirectly | Primary journey; NPS/CSAT/churn is the headline KPI |
| Financial KPI on the driver tree | Leaf KPI is <0.5% of EBIT at full potential | 0.5–2% of EBIT at realised-to-date band | >2% of EBIT at realised-to-date band, or top-line leaf |
| Speed to value (6–36 months) | First significant value >36 months | 18–36 months | Significant value inside 6–18 months; AI-intensive opportunities pay off faster |
| Synergy across domains | Stand-alone data and platform | Shares data or platform with one other candidate | Unlocks two or more other domains (shared data product, agent platform) |

**Feasibility axis** (score 1–5 each)

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Executive sponsorship | No named C-1 owner; IT-led | Functional head sponsors; CEO aware | CEO or business-unit P&L owner sponsors and will sit on the value-tracking cadence |
| Data and technology readiness | Data unstructured, siloed, no rights clarity | Core systems API-accessible; data quality known gaps | Flow data generated in-product; integration path and vendor option exist |
| Ease of adoption | Workforce resistant; no redesign appetite | Partial redesign possible; union/regulatory constraints manageable | Frontline asked for it; redesign already sanctioned; change capacity funded (70% of effort to people/process, [BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf)) |
| Ease of scaling | Single site, bespoke | Multi-site with local variants | Standard process across the enterprise; reusable components ("factory mindset", [McKinsey COO guide](https://www.mckinsey.com/capabilities/operations/our-insights/maximizing-operational-value-the-coos-guide-to-ai-and-agentic-ai)) |

**Selection rules**

| Rule | Detail |
|---|---|
| 2–5 domain rule | Output of the screen is 2–5 domains. Fewer than 2 starves the pipeline; more than 5 "creates a lot of activity but little value" ([McKinsey, bite size](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size)) |
| Two-core-plus-one-support default | Core functions hold 62% of leaders' realised AI value and 70% of potential; IT is 13% ([BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value), [BCG Oct 2025](https://media-publications.bcg.com/The-Widening-AI-Value-Gap-October-2025.pdf)); MGI puts 75% of gen-AI value in customer ops, marketing and sales, software engineering and R&D ([MGI 2023](https://www.mckinsey.com/mgi/reports/the-economic-potential-of-generative-ai-the-next-productivity-frontier)). Default hypothesis: two core domains + one support domain |
| Fast/slow pairing | Include at least one domain with returns inside 12 months (production optimisation shows results in 8–10 months) alongside any long-tail domain (resources exploration 3–4 years) ([McKinsey COO guide](https://www.mckinsey.com/capabilities/operations/our-insights/maximizing-operational-value-the-coos-guide-to-ai-and-agentic-ai)) |
| Agent-governance workstream | Any domain that will run agents with decision authority carries a built-in "avoid risk" workstream (5% control-set maturity, [BCG Sep 2026](https://www.bcg.com/press/30september2026-ai-starting-to-pay-off-companies-generate-value)) |
| Precision | Estimates need not be precise at this stage ([McKinsey, bite size](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size)); two bands are mandatory, decimals are not |

Scoring output: Value = mean of four value scores; Feasibility = mean of four feasibility scores; plot on 2×2; select from the top-right first, then the highest-value domain in the top-left that can be made feasible inside 12 months.

### 2.4 Sizing in two bands

Every domain is sized twice. Band 1 is the ceiling. Band 2 is what survey respondents actually report in 2026. A credible value study shows both; a deliverable that shows only Band 1 is miscalibrated by roughly an order of magnitude.

**Band 1: technical potential (MGI 2023 function ceilings)**

| Function | Ceiling (share of function cost or spend) | Source |
|---|---|---|
| Customer operations | 30–45% of function cost; up to 50% fewer human-handled contacts | [MGI 2023](https://www.mckinsey.com/mgi/reports/the-economic-potential-of-generative-ai-the-next-productivity-frontier) |
| Software engineering | 20–45% of annual spend | same |
| Marketing | 5–15% of marketing spend | same |
| R&D | 10–15% | same |
| Sales | 3–5% of sales expenditure | same |
| Procurement: commodities / other directs / indirects and tail | 2–3% / 5–10% / 10–15% of category spend | [Activant](https://www.activantcapital.com/pdfs/ai-in-procurement.pdf) |
| BCG archetype ceilings | Deploy 10–15% productivity; Reshape 30–50% efficiency; Invent e.g. 3+ pts incremental sales | [BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf) |

**Band 2: realised-to-date (McKinsey State of AI 2026, n=1,719, fieldwork May–Jun 2026)**

| Measure | Value | Source |
|---|---|---|
| Cost decrease | Most reported cost decreases are ≤10%. Share reporting any decrease (share ≥20%): supply chain 41% (3%), service ops 38% (7%), manufacturing 37% (1%), marketing & sales 34% (2%), HR 33% (6%), software eng 33% (4%), strategy/finance 31% (6%), product dev 31% (5%), IT 28% (3%), risk 28% (4%), knowledge mgmt 25% (7%) | [McKinsey State of AI 2026 PDF](https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/the-state-of-ai-in-2026-on-the-road-to-roi.pdf) |
| Revenue increase | Share reporting any increase tops out at 37% in marketing & sales (7% >10%); product dev 36%; software eng 31% (11% >10%); service ops 31%; supply chain 29%; strategy/finance 26%; IT 23% | same |
| EBIT attribution | 37% attribute any EBIT impact to AI (flat); 6% high performers (≥5% of EBIT), flat for two years | same; [McKinsey State of AI 2026](https://www.mckinsey.com/capabilities/operations/our-insights/the-state-of-ai) |
| Cross-checks | 19% of C-suite report gen-AI revenue gains >5%; 23% see any favourable cost change ([McKinsey Superagency](https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/superagency-in-the-workplace-empowering-people-to-unlock-ais-full-potential-at-work)); Deloitte: 40% report cost reduction, 20% revenue increase ([Deloitte](https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-generative-ai-in-enterprise.html)); Goldman's chief economist: AI contributed "basically zero" to US GDP growth in 2025 ([Tom's Guide](https://www.tomsguide.com/ai/ai-contributed-basically-zero-to-the-us-economy-last-year-according-to-goldman-sachs)) | |
| Best-evidenced function numbers | Customer support RCT: +14% issues resolved/hour, +34% for novices, 5,179 agents ([NBER w31161](https://www.nber.org/papers/w31161)); software engineering: METR −19% for experienced devs in 2025, CI spanning zero in 2026 ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), [METR update](https://evals.alignment.org/blog/2026-02-24-uplift-update/)); back-office: $2–10M/yr BPO elimination, 30% cut in external creative spend ([MIT NANDA](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)) | |

**Band presentation rule**

| Element | Template |
|---|---|
| Domain line | "Customer service: technical potential S$X–Y (30–45% of S$Z function cost, MGI 2023); realised-to-date S$A–B (≤10% cost decrease, McKinsey 2026; +14% throughput, NBER RCT). Planning base = Band 2 at the ladder position chosen (Section 3.4)." |
| Confidence label | T1–T5 source tier per number (framework report evidence standard) and correlational/causal label |
| Oversizing | Pipeline behind the 2–5 headline domains sized at >1x target because successful transformations deliver 2.7x initial estimate and 55% of value comes from small initiatives ([McKinsey, How bold](https://www.mckinsey.de/capabilities/transformation/our-insights/how-bold-is-your-business-transformation-a-new-way-to-measure-progress)) |

### 2.5 Per-industry technical potential (MGI 2023)

Reproduced from the research notes. Row-value pairing was inferred from PDF text order; verify against Exhibit 4 before client use. Source: [MGI 2023 PDF](https://www.mckinsey.de/~/media/mckinsey/locations/europe%20and%20middle%20east/deutschland/news/presse/2023/2023-06-14%20mgi%20genai%20report%2023/the-economic-potential-of-generative-ai-the-next-productivity-frontier-vf.pdf); spotlight figures also at [MGI report page](https://www.mckinsey.com/mgi/reports/the-economic-potential-of-generative-ai-the-next-productivity-frontier).

| Industry | Gen-AI value (US$B) | % of industry revenue | First-domain heuristic (BCG function share where available, [BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value)) |
|---|---|---|---|
| High tech | 240–460 | 4.8–9.3 | Sales & marketing 31% of value in software; software engineering |
| Banking | 200–340 | 2.8–4.7 | Customer service 18%; risk / KYC / fraud |
| Pharma & medical products | 60–110 | 2.6–4.5 | R&D 27% (biopharma) |
| Education | 120–230 | 2.2–4.0 | Content and student service |
| Telecom | 60–100 | 2.3–3.7 | Sales & marketing 25%; network and IT ops |
| Healthcare | 150–260 | 1.8–3.2 | Documentation, imaging; highest breach cost $7.42M |
| Insurance | 50–70 | 1.8–2.8 | Customer service 24%; claims and underwriting |
| Media & entertainment | 60–110 | 1.5–2.6 | Sales & marketing 26% |
| Advanced manufacturing | 170–290 | 1.4–2.4 | Operations and supply chain |
| Consumer packaged goods | 160–270 | 1.4–2.3 | Personalisation 19%; supply chain |
| Advanced electronics / semiconductors | 100–170 | 1.3–2.3 | R&D, yield |
| Travel, transport & logistics | 180–300 | 1.2–2.0 | Sales & marketing 31% (travel/tourism); operations |
| Retail | 240–390 | 1.2–1.9 | Personalisation 22%; supply chain |
| Real estate | 110–180 | 1.0–1.7 | Customer service; asset ops |
| Energy | 150–240 | 1.0–1.6 | Asset ops; trading |
| Administrative & professional services | 150–250 | 0.9–1.4 | Knowledge work; delivery |
| Chemicals | 80–140 | 0.8–1.3 | Operations; R&D |
| Basic materials | 120–200 | 0.7–1.2 | Operations |
| Construction | 90–150 | 0.7–1.2 | Planning; procurement |
| Agriculture | 40–70 | 0.6–1.0 | Operations |
| Public sector | 70–110 | 0.5–0.9 | Citizen service; case processing |

Additional BCG function shares for the heuristic column: R&D = 29% of AI value in automotive, 19% medtech ([BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value)). Caveat: all industry figures are 2023 vintage; no 2025–26 refresh was found.

---

## 3. Use-case matrix

### 3.1 Scoring model

Weights follow the practitioner range that converges across sources (value 35–45%, feasibility 25–35%, time-to-value 10–15%, reuse 10–15%, strategic fit 5–10%, risk and adoption as penalties) ([Umbrex](https://umbrex.com/resources/frameworks/supply-chain-frameworks/ai-use-case-prioritization-framework/), [Okhrem](https://paul-okhrem.com/ai-use-case-prioritization-framework/), [SG Analytics](https://www.sganalytics.com/blog/framework-for-ai-use-case-prioritization/)). No Big-4 or MBB firm publishes numeric weights. Each criterion is scored 1–5 and multiplied by its weight; top scores require evidence.

| Criterion | Weight | What is scored | 1 | 3 | 5 |
|---|---|---|---|---|---|
| Value | 40 | Size × confidence of the make / save / avoid impact on a named driver-tree leaf, using Band 2 at the chosen ladder position. Split into revenue, cost and risk-avoided sub-lines as DBS does ([Forrester](https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized)) | <0.1% EBIT or confidence only from vendor claims | 0.1–0.5% EBIT with T3 benchmark | >0.5% EBIT with T1/T2 anchor or in-house measurement |
| Feasibility | 25 | Data readiness and rights, technical maturity, integration burden, buy/partner option (vendor partnerships reach deployment ~67% vs ~33% internal builds, [MIT NANDA](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)) | Data absent or unlabelled; no vendor; custom build | Data accessible with cleanup; vendor exists but needs integration | Production-grade data; packaged solution; integration path proven |
| Time-to-value | 10 | Months to first system-measured benefit | >18 months | 6–18 months | <6 months |
| Reuse | 10 | Platform, data product or agent components reusable in other domains | Single-use | Reusable within domain | Reusable across ≥2 domains |
| Strategic fit | 10 | Supports a right-to-win strength (Step 1), especially one tagged eroding or hollowing | No link | Supports a secondary capability | Directly defends or extends a core capability |
| Risk penalty | −5 to −10 | Responsible-AI tier (EU AI Act class, NIST AI RMF, ISO/IEC 42001 mapping, [Elevate Consult](https://elevateconsult.com/insights/ai-governance-frameworks-compared-matching-nist-eu-ai-act-and-iso-42001-to-your-use-case/)), reputational exposure, regulatory ambiguity | −10 for high-risk class or customer-facing autonomy | −5 for limited-risk class | 0 for minimal |
| Adoption penalty | −10 | Change burden: roles redesigned, frontline resistance, training load | −10 if redesign spans >1 function without a sponsor | −5 if redesign is within one team | 0 if tool slots into existing workflow with named champions |

Score = Σ(criterion score × weight) / 5, then minus penalties; maximum 100. Output buckets: Likely wins (≥70), Calculated risks (50–69), Marginal gains (<50), following Gartner's tiering on an 18-month horizon ([Gartner via Freshworks](https://www.freshworks.com/freshservice/resources/gartner-ai-use-case-report/)).

### 3.2 Hard gates (pass/fail before scoring)

A use case failing any gate is deferred, not scored. Gates follow the practitioner hard-stop list ([Okhrem](https://paul-okhrem.com/ai-use-case-prioritization-framework/), [SG Analytics](https://www.sganalytics.com/blog/framework-for-ai-use-case-prioritization/), [Umbrex](https://umbrex.com/resources/frameworks/supply-chain-frameworks/ai-use-case-prioritization-framework/)).

| Gate | Pass condition | Evidence required |
|---|---|---|
| G1 Data rights | Client has legal and contractual right to use the data for this purpose, including customer consent and cross-border constraints | Data inventory line, DPO or legal sign-off |
| G2 Named owner | One accountable senior business owner (not IT, not the AI team) who holds the KPI | Name, title, and the KPI in their scorecard |
| G3 System-measured baseline | Baseline for the leaf KPI pulled from systems of record for a defined period, not estimated | Extract with source system, period, volumes, handling times, error/exception rates |
| G4 Measurement plan with control group | A/B, holdout or matched control design agreed before build; DBS compares outcomes against control groups so value is measured not projected ([Forrester](https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized)) | One-page measurement design with cadence and statistical owner |
| G5 Safety boundary | Safe operating limits defined: what the system may decide alone, escalation rules, human-in-the-loop points, stop conditions | Boundary statement mapped to EU AI Act tier and NIST AI RMF Govern/Map/Measure/Manage |

### 3.3 Candidate generation inside a domain

| Step | Action |
|---|---|
| 1 | Pull seed rows for the domain from the catalogue (Section 6), filtered by industry and value lens |
| 2 | Add client-specific candidates from interviews and the KPI extract (where are exceptions, rework, waits, manual hand-offs) |
| 3 | Classify each candidate by technique and agent archetype (Customer, Employee, Creative, Code, Data, Security, per [Google](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/gen-ai-business-use-cases/)) |
| 4 | Apply the assistant / automation / agent fit test: agents for decisions, automation for routine workflows, assistants for simple retrieval; Gartner expects >40% of agentic projects cancelled by end-2027 and finds only ~130 genuine agentic vendors ([Outlook Business/Gartner](https://www.outlookbusiness.com/deeptech/artificial-intelligence/over-40-of-agentic-ai-projects-will-be-scrapped-by-2027-says-gartner)) |
| 5 | Run gates G1–G5, then score |
| 6 | Keep 3–5 use cases per domain; 9–15 per engagement across the 2–5 domains |

### 3.4 Technique ladder and realisation discount

McKinsey's illustrative call-centre ladder: assistants ~5–10% gain; agents bolted onto the old workflow 20–40% time savings; process redesigned around agents up to 80% of common incidents resolved autonomously (hypothetical) ([McKinsey agentic](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)). High performers are ~3x as likely to have fundamentally redesigned workflows ([McKinsey State of AI 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)).

**Rule: the ladder position sets the realisation discount applied to the Band 1 ceiling.** The business case uses Band 1 × discount, cross-checked against Band 2, never Band 1 alone.

| Rung | Pattern | Illustrative gain | Realisation discount on Band 1 ceiling | Typical evidence | Payback class (Section 4) |
|---|---|---|---|---|---|
| L1 Assistant | Copilot or chatbot inserted into existing tasks; horizontal tools | 5–10% | 0.10–0.25 | Gains diffuse and hard to measure; 80% report individual productivity gains while EBIT impact is flat at ~37% | Efficiency, 12–18 months |
| L2 Agent on old workflow | Agent automates steps of the current process; integration into legacy is costly | 20–40% | 0.30–0.50 | Vendor case numbers (T4); Agentforce ~85% of own queries ([CX Today](https://cxtoday.com/salesforce-resolves-85-of-its-customer-queries-with-agentforce)) | Quality, 24–36 months |
| L3 Redesigned autonomous | Process rebuilt around agents with human oversight at boundaries; new KPIs are cycle time, defect rate, NPS | up to 80% | 0.60–0.80, only with G2–G5 passed and 70% of budget on people/process | Toyota planning agent 50+ → 6–10 planners ([Deloitte](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2025/toyota-digital-transformation-ai.html)); Singtel >60% of care resolutions AI-led ([Singtel SGX](https://links.sgx.com/1.0.0/corporate-announcements/423V7E007WOXU5ET/902534_Investor%20Day%202026%20-%20Singtel%20SG.pdf)) | Transformation, 36–60 months |

Discount factors are v0.1 placeholders; recalibrate after the first three engagements. The Band 2 cross-check overrides: if Band 1 × discount exceeds the top of what survey respondents report (≤10% cost decrease for most functions), the case must state why the client is in the top decile.

### 3.5 Technique taxonomy (tagging vocabulary)

| Technique | Typical ladder rung | Notes |
|---|---|---|
| Predictive ML | L2 | Churn, fraud, demand, credit |
| Optimisation / digital twin | L2–L3 | Toyota supply-chain twin ~$800M ([McKinsey WIRED](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/wired-the-ai-playbook-top-companies-use)) |
| Computer vision | L2 | Quality, safety, documents |
| NLP / document AI | L1–L2 | Extraction, classification, summarisation |
| GenAI content | L1 | Marketing, medical writing (agency cuts 20–30%, [BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf)) |
| RAG / knowledge assistant | L1 | Help centre, policy search |
| Task copilot | L1 | Coding, office productivity |
| Autonomous agent | L2–L3 | Workflow-level, with memory, planning, orchestration |
| Multi-agent system | L3 | "System of agents" (Toyota) |
| Agentic coding | L1–L2 | 32% of firms decided against buying software because they could build it ([McKinsey State of AI 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)) |

---

## 4. Business-case template (7 sections)

Shape follows the CFO-oriented template ([AI Assembly Lines](https://aiassemblylines.com/post/ai-business-case-template-cfo-approval-guide)), extended with token/run cost (the original omits it), DBS control-group measurement and a responsible-AI tier. One case per selected use case; one page plus appendix.

| # | Section | Required content | Rules and anchors |
|---|---|---|---|
| 1 | Financial problem statement | The driver-tree leaf, its current value, the gap to peer or target in currency, the value lens (make / save / avoid), the domain it sits in | Strategic context in financial terms only; no technology description here |
| 2 | System-measured baseline | Volumes, handling times, error and exception rates, rework, quality-failure cost, loss events; source system; period; extraction owner | Gate G3. Estimated baselines are not accepted. Baseline period ≥3 months or one full seasonal cycle |
| 3 | Scope | In-scope process steps, segments, geographies, systems; explicit out-of-scope list; ladder rung (L1/L2/L3); technique and agent archetype; buy / partner / build decision | Model cost is <10–15% of total solution cost, so scope must name data, integration and change work ([McKinsey 2024 reset](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/a-generative-ai-reset-rewiring-to-turn-potential-into-value-in-2024)) |
| 4 | Three scenarios | Conservative / base / optimistic, each with annual benefits by lens, 3-year TCO, payback months, NPV, IRR. TCO lines: licensing, implementation, integration, change management, training, internal IT time, support, model refresh, **run cost including tokens and inference**, with an inference-price sensitivity | Conservative case = 80% of base benefits and 20% longer implementation. Recurring gen-AI costs can exceed build costs at scale ([McKinsey agentic](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)); ~20% of firms say operating costs incl. tokens constrain AI use ([McKinsey State of AI 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)); inference price for GPT-3.5-level fell ~280x Nov 2022–Oct 2024 ([VentureBeat](https://venturebeat.com/ai/stanfords-ai-index-5-critical-insights-reshaping-enterprise-tech-strategy)). Transformational gen-AI initiatives cost US$5–20M ([IntelligentCIO/Gartner](https://www.intelligentcio.com/apac/2024/08/05/gartner-predicts-30-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025/)) |
| 5 | Risk register | Implementation overrun, benefit shortfall, data-quality degradation, adoption failure, vendor viability, model error / hallucination, regulatory change; likelihood × impact; contingency; responsible-AI tier (EU AI Act class, NIST AI RMF function, ISO/IEC 42001 control) | Deloitte barrier data: regulatory compliance 38%, real-world mistakes 35%, value shortfall 34%, data quality 30%, loss of trust 29% ([Deloitte Q4 2025](https://www.deloitte.com/content/dam/assets-shared/docs/about/2025/quarter-4.pdf)); organisations mitigate ~4 AI risks on average, 51% report ≥1 negative consequence ([McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-state-of-ai-2025)) |
| 6 | Owner, measurement and stop triggers | Named accountable owner (G2); control-group design (G4); measurement cadence; review dates; pause and stop triggers (e.g. benefit <50% of conservative case at month 6; quality or complaint KPI breaches safety boundary) | Fund only a bounded test with acceptance criteria, review date and stop condition ([Okhrem](https://paul-okhrem.com/ai-use-case-prioritization-framework/)). New KPIs for redesigned workflows: cycle time, defect rate, NPS rather than task time saved ([ibl.ai on McKinsey](https://ibl.ai/blog/mckinsey-seizing-the-agentic-ai-advantage)) |
| 7 | Do-nothing case | Trajectory of the leaf KPI without intervention; competitor moves; eroding-strength tag from Step 1; regulatory deadlines (EU AI Act high-risk rules phase in Aug 2026 and Aug 2027) | Must be quantified on the same horizon as the scenarios |

**Payback norms by use-case type**

| Type | Payback expectation | Ladder rung | Source |
|---|---|---|---|
| Efficiency tool | 12–18 months | L1 | [AI Assembly Lines](https://aiassemblylines.com/post/ai-business-case-template-cfo-approval-guide) |
| Quality / decision improvement | 24–36 months | L2 | same |
| Strategic transformation | 36–60 months | L3 | same |
| Default caution | 70% of firms expect ≥12 months to resolve ROI challenges (55% 1–2 years, 15% >2 years); only narrow efficiency tools should promise <12 months | all | [Deloitte Q4 2025](https://www.deloitte.com/content/dam/assets-shared/docs/about/2025/quarter-4.pdf) |
| ROI reference range (self-reported) | Gartner n=822: 15.8% revenue increase, 15.2% cost savings, 22.6% productivity; use as upper reference, not planning base | — | [IntelligentCIO/Gartner](https://www.intelligentcio.com/apac/2024/08/05/gartner-predicts-30-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025/) |

**Conservative-case rule:** 80% of base-case benefits, implementation 20% longer; the conservative case must still clear the payback norm for its type or the use case drops a rung on the ladder.

---

## 5. Failure-rate reference and success factors

### 5.1 Failure-rate table (quote with the definition, never the headline alone)

| Source | Headline | What is actually measured | Denominator / caveat | URL |
|---|---|---|---|---|
| Gartner (Jul 2024) | ≥30% of gen-AI projects abandoned after PoC by end-2025 | Project-level abandonment | Causes: poor data quality, inadequate risk controls, escalating costs, unclear value | [IntelligentCIO](https://www.intelligentcio.com/apac/2024/08/05/gartner-predicts-30-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025/) |
| Gartner (Jun 2025) | >40% of agentic AI projects cancelled by end-2027 | Project-level, agentic only | Also: only ~130 genuine agentic vendors ("agent washing") | [Outlook Business/Gartner](https://www.outlookbusiness.com/deeptech/artificial-intelligence/over-40-of-agentic-ai-projects-will-be-scrapped-by-2027-says-gartner) |
| S&P Global (Mar 2025) | 42% of businesses scrapped most AI initiatives (17% a year earlier); average firm dropped 46% of PoCs | Firm-level, n>1,000 NA/Europe | Barriers: cost, data privacy, security; figures via CIO Dive | [CIO Dive](https://www.ciodive.com/news/ai-project-fail-data-spglobal/742590/) |
| IBM CEO Study (May 2025) | 25% of AI initiatives delivered expected ROI; 16% scaled enterprise-wide | Initiative-level, CEO self-report, n=2,000 | 64% invest before understanding value | [IBM](https://newsroom.ibm.com/2025-05-06-ibm-study-ceos-double-down-on-ai-while-navigating-enterprise-hurdles) |
| BCG (Oct 2024 → Oct 2025) | 74% show no tangible value (2024) → 5% "future-built" (2025) | Firm-level value creation | Definitions changed each year (26% → 25% → 5% → "nearly half" in 2026); not a trend series | [BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value), [BCG Oct 2025](https://media-publications.bcg.com/The-Widening-AI-Value-Gap-October-2025.pdf) |
| McKinsey State of AI (2025 → 2026) | 39% → 37% report any EBIT impact; 6% high performers (≥5% EBIT) both years | Firm-level EBIT attribution, n=1,993 / 1,719 | 80% report individual productivity gains in 2026 while EBIT share is flat | [McKinsey 2025](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-state-of-ai-2025), [McKinsey 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai) |
| MIT NANDA (Jul/Aug 2025) | "95% get zero return" | Share of organisations without a P&L-visible production tool; funnel 60% evaluated → 20% pilot → 5% production | Denominator not clearly defined; does not count pilots; two success definitions; self-selected interviews (52 or ~150 depending on write-up); treat as directional. Suggested citation: "5% of organisations had task-specific gen-AI tools in production" | [MIT NANDA PDF](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf), [claim check](https://www.ai-first.company/evidence/claim-checks/mit-95-percent-of-ai-pilots-fail/), [Fortune](https://www.fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo) |
| RAND (2024) | ">80% of AI projects fail" | Not RAND's measurement; cited from a 2022 Fortune article | RAND's own contribution is five root causes from 65 interviews | [RAND](https://www.rand.org/pubs/research_reports/RRA2680-1.html) |
| Deloitte (Jan 2025) | 74% of most-advanced initiatives meet or exceed expectations; ~24% fall short | Best-initiative self-report, n=2,773 | Survivorship: respondents pick their most advanced initiative | [Deloitte Q4 2025](https://www.deloitte.com/content/dam/assets-shared/docs/about/2025/quarter-4.pdf) |

Reading rule for decks: project-level (Gartner, S&P, IBM) ≠ firm-level (BCG, McKinsey) ≠ organisation-without-production-tool (MIT). Put the definition in the source line.

### 5.2 Success-factor checklist

Consistent across six independent sources (McKinsey, BCG, MIT NANDA, RAND, IBM, Toyota/Deloitte). Each selected use case and each domain plan is checked against all six; a "no" on any line is a risk-register entry.

| # | Factor | Evidence | Check in this kit |
|---|---|---|---|
| 1 | Workflow redesign, not tool insertion | High performers ~3x as likely to have fundamentally redesigned workflows (~75% vs ~25%) ([McKinsey 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)); Reshape/Invent firms: 53% vs 31% of employees save ≥1 day/week ([BCG AI at Work 2026](https://web-assets.bcg.com/e7/c7/00d913744cccb1e4f65bbf54fe86/ai-at-work-slideshow-june-2026.pdf)); Toyota "redesign rather than automate" ([Deloitte](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2025/toyota-digital-transformation-ai.html)) | Ladder rung L2+ requires a redesigned process map |
| 2 | One accountable senior owner | High performers 2–3x more likely to report senior-leader ownership ([McKinsey 2025](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-state-of-ai-2025)); McKinsey lists no CEO sponsorship among reasons vertical use cases stall ([McKinsey agentic](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)) | Gate G2 |
| 3 | Defined measurement: baseline and control group | High performers 2x as likely to have defined impact-measurement processes ([McKinsey 2026](https://www.mckinsey.com/capabilities/operations/our-insights/the-state-of-ai)); 60% of firms do not define/monitor financial AI KPIs ([BCG AI Radar 2025](https://web-assets.bcg.com/0b/f6/c2880f9f4472955538567a5bcb6a/ai-radar-2025-slideshow-jan-2025-r.pdf)); DBS control groups ([Forrester](https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized)) | Gates G3, G4 |
| 4 | Core-process focus, fewer and larger bets | 62% of leaders' value in core processes; leaders pursue ~half as many opportunities and scale >2x as many ([BCG Oct 2024](https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value)); 70% of potential in core functions ([BCG Sep 2025](https://www.bcg.com/press/30september2025-ai-leaders-outpace-laggards-revenue-growth-cost-savings)) | Two-core-plus-one-support default; 2–5 domains |
| 5 | 70 / 20 / 10 resource split | 70% people and process, 20% technology and data, 10% algorithms ([BCG CEO's Guide 2024](https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf)); Trailblazer CEOs spend 60% of AI budget on upskilling vs 24–27% ([BCG AI Radar 2026](https://www.bcg.com/press/15january2026-as-ai-investments-surge-ceos-take-lead)) | TCO lines in Section 4.4 must show ≥50% of spend outside model and licence |
| 6 | Buy or partner where a vendor exists | Vendor partnerships reach deployment ~67% vs ~33% for internal builds (self-reported, n=52) ([MIT NANDA](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf)); counter-trend: 32% build instead of buy via agentic coding ([McKinsey 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)) | Feasibility criterion; buy/partner/build decision in Section 4.3 |

Supporting root causes to test against (RAND, [RAND](https://www.rand.org/pubs/research_reports/RRA2680-1.html)): mis-specified problem or metric; insufficient high-quality data; technology-first; inadequate data and deployment infrastructure; problems beyond AI's capability. MIT NANDA adds the "learning gap" (systems that do not retain feedback) and budget misallocation to sales and marketing when back-office ROI is higher ([Fortune](https://www.fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo)).

---

## 6. Catalogue schema

Location: `/home/claude/workspace/catalogue/`. Seed file: `use-case-catalogue-seed.csv` (25 rows). The catalogue is a candidate generator for Section 3.3, not a recommendation list; every row still passes gates G1–G5 inside a client domain. Composition logic: capability map (where) × value lens (why) × technique and agent archetype (how) × Gartner-style tiering (when) ([Deloitte Dossier](https://www.deloitte.com/us/generative-ai-dossier), [Google](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/gen-ai-business-use-cases/), [Gartner via Freshworks](https://www.freshworks.com/freshservice/resources/gartner-ai-use-case-report/)).

| Column | Type | Allowed values / format | Notes |
|---|---|---|---|
| id | string | UC-001 … | Stable key |
| industry | enum | MGI industry list (Section 2.5) | One value; cross-industry rows use "Cross-industry" |
| function | enum | Customer operations; Marketing; Sales; Software engineering; IT operations; R&D; Supply chain; Manufacturing/operations; Procurement; Finance; HR; Risk & compliance; Legal; Field service; Network operations; Clinical/healthcare operations; Investment/trading | Maps to driver-tree branch |
| domain | string | End-to-end process name (Section 2.2 list or client-specific) | The domain the use case must sit inside |
| value_lens | enum | make / save / avoid | DBS three-bucket convention; one primary lens per row, secondary lens in example text |
| technique | enum | Section 3.5 taxonomy | |
| agent_archetype | enum | Customer / Employee / Creative / Code / Data / Security / n.a. (non-agentic) | Google archetypes |
| ladder_rung | enum | L1 / L2 / L3 | Sets realisation discount |
| default_risk_tier | enum | High / Limited / Minimal | Starting EU AI Act-style class; credit, employment, essential-services access and law-enforcement adjacent = High; customer-facing chat = Limited; internal productivity = Minimal. Re-assess per client |
| source_tier | enum | T1–T5 | Framework evidence standard: T2 investor materials, T3 consulting research and reputable trade press, T4 vendor content |
| source_name | string | Publisher and year | |
| source_url | url | Must be a URL present in the research notes | |
| example_company | string | | |
| example_outcome_metric | string | Quoted metric exactly as the source states it | Vendor metrics are self-reported pilot or early-rollout figures; investor-day and annual-report figures preferred for board citation |
| notes | string | Caveats, attribution limits | |

Maintenance rules: one row per company × use case; metrics never rounded away from the source; a row with no URL is not admitted; vendor (T4) rows are marked directional in any client exhibit.

---

## Appendix A. Source list used in this kit

| Tier | Source | URL |
|---|---|---|
| T1 | NBER w31161 customer-support RCT | https://www.nber.org/papers/w31161 |
| T1 | METR 2025 developer RCT | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ |
| T1 | METR 2026 update | https://evals.alignment.org/blog/2026-02-24-uplift-update/ |
| T2 | Singtel Investor Day 2026 (SGX) | https://links.sgx.com/1.0.0/corporate-announcements/423V7E007WOXU5ET/902534_Investor%20Day%202026%20-%20Singtel%20SG.pdf |
| T3 | McKinsey, Selecting P&L-linked KPIs | https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/selecting-p-and-l-linked-kpis-for-industrial-transformations |
| T3 | McKinsey, Choose the right transformation bite size | https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/choose-the-right-transformation-bite-size |
| T3 | McKinsey, How bold is your business transformation | https://www.mckinsey.de/capabilities/transformation/our-insights/how-bold-is-your-business-transformation-a-new-way-to-measure-progress |
| T3 | McKinsey, Strategy to beat the odds | https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategy-to-beat-the-odds |
| T3 | McKinsey, A generative AI reset (2024) | https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/a-generative-ai-reset-rewiring-to-turn-potential-into-value-in-2024 |
| T3 | McKinsey, Seizing the agentic AI advantage | https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage |
| T3 | McKinsey, WIRED: the AI playbook | https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/wired-the-ai-playbook-top-companies-use |
| T3 | McKinsey, COO's guide to AI and agentic AI | https://www.mckinsey.com/capabilities/operations/our-insights/maximizing-operational-value-the-coos-guide-to-ai-and-agentic-ai |
| T3 | McKinsey State of AI 2025 | https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-state-of-ai-2025 |
| T3 | McKinsey State of AI 2026 (page) | https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai ; https://www.mckinsey.com/capabilities/operations/our-insights/the-state-of-ai |
| T3 | McKinsey State of AI 2026 (PDF) | https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/the-state-of-ai-in-2026-on-the-road-to-roi.pdf |
| T3 | McKinsey Superagency | https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/superagency-in-the-workplace-empowering-people-to-unlock-ais-full-potential-at-work |
| T3 | MGI 2023 report page | https://www.mckinsey.com/mgi/reports/the-economic-potential-of-generative-ai-the-next-productivity-frontier |
| T3 | MGI 2023 PDF | https://www.mckinsey.de/~/media/mckinsey/locations/europe%20and%20middle%20east/deutschland/news/presse/2023/2023-06-14%20mgi%20genai%20report%2023/the-economic-potential-of-generative-ai-the-next-productivity-frontier-vf.pdf |
| T3 | BCG CEO's Guide to Maximizing Value from AI (Jul 2024) | https://www.bcg.com/assets/2024/executive-perspectives-ceos-guide-to-maximizing-value-from-ai-3july.pdf |
| T3 | BCG press, Oct 2024 | https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value |
| T3 | BCG AI Radar 2025 | https://web-assets.bcg.com/0b/f6/c2880f9f4472955538567a5bcb6a/ai-radar-2025-slideshow-jan-2025-r.pdf |
| T3 | BCG press, Sep 2025 | https://www.bcg.com/press/30september2025-ai-leaders-outpace-laggards-revenue-growth-cost-savings |
| T3 | BCG Widening AI Value Gap, Oct 2025 | https://media-publications.bcg.com/The-Widening-AI-Value-Gap-October-2025.pdf |
| T3 | BCG AI Radar 2026 | https://www.bcg.com/press/15january2026-as-ai-investments-surge-ceos-take-lead |
| T3 | BCG AI at Work, Jun 2026 | https://web-assets.bcg.com/e7/c7/00d913744cccb1e4f65bbf54fe86/ai-at-work-slideshow-june-2026.pdf |
| T3 | BCG press, Sep 2026 | https://www.bcg.com/press/30september2026-ai-starting-to-pay-off-companies-generate-value |
| T3 | Deloitte State of GenAI Q4 (Jan 2025) | https://www.deloitte.com/content/dam/assets-shared/docs/about/2025/quarter-4.pdf |
| T3 | Deloitte State of GenAI in the Enterprise (2025) | https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-generative-ai-in-enterprise.html |
| T3 | Deloitte Tech Trends 2025, Toyota | https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2025/toyota-digital-transformation-ai.html |
| T3 | Deloitte AI Dossier | https://www.deloitte.com/us/generative-ai-dossier |
| T3 | IBM CEO Study 2025 | https://newsroom.ibm.com/2025-05-06-ibm-study-ceos-double-down-on-ai-while-navigating-enterprise-hurdles |
| T3 | RAND RRA2680-1 | https://www.rand.org/pubs/research_reports/RRA2680-1.html |
| T3 | Gartner via Freshworks (use-case assessment) | https://www.freshworks.com/freshservice/resources/gartner-ai-use-case-report/ |
| T3 | Gartner via IntelligentCIO (30% abandonment, costs, ROI) | https://www.intelligentcio.com/apac/2024/08/05/gartner-predicts-30-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025/ |
| T3 | Gartner via Outlook Business (40% agentic) | https://www.outlookbusiness.com/deeptech/artificial-intelligence/over-40-of-agentic-ai-projects-will-be-scrapped-by-2027-says-gartner |
| T3 | S&P Global via CIO Dive | https://www.ciodive.com/news/ai-project-fail-data-spglobal/742590/ |
| T3 | MIT NANDA PDF | https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf |
| T3 | MIT NANDA via Fortune | https://www.fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo |
| T3 | MIT 95% claim check | https://www.ai-first.company/evidence/claim-checks/mit-95-percent-of-ai-pilots-fail/ |
| T3 | IBM Cost of a Data Breach 2025 via Help Net Security | https://helpnetsecurity.com/2025/08/04/ibm-cost-data-breach-report-2025 |
| T3 | Forrester on DBS | https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized |
| T3 | Computer Weekly on DBS | https://www.computerweekly.com/news/366639844/DBS-rewires-operating-models-for-AI-reasoning-era |
| T3 | TechWire Asia, ASEAN banks | https://techwireasia.com/2025/12/asean-banks-ai-strategies-dbs-maybank-cimb-jpmorgan/ |
| T3 | CFOtech AU on CBA | https://www.cfotech.com.au/story/commonwealth-bank-uses-ai-to-enhance-customer-service |
| T3 | CIO.com on WEF Proof over Promise | https://www.cio.com/article/4122937/davos-from-hype-to-ai-transformation-in-the-economy.html |
| T3 | eMarketer on Klarna | https://www.emarketer.com/content/klarna-backtracks-ai-customer-service-plans |
| T3 | Tom's Guide on Goldman Sachs | https://www.tomsguide.com/ai/ai-contributed-basically-zero-to-the-us-economy-last-year-according-to-goldman-sachs |
| T3 | VentureBeat on Stanford AI Index 2025 | https://venturebeat.com/ai/stanfords-ai-index-5-critical-insights-reshaping-enterprise-tech-strategy |
| T3 | BIAN 14.0 | https://bian.org/news-room/bian-unveils-new-service-landscape-14-0-to-accelerate-ai-ready-banking-architecture/ |
| T4 | Google Cloud gen-AI use cases (1,302) | https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/gen-ai-business-use-cases/ |
| T4 | Microsoft Source Asia on OCBC | https://news.microsoft.com/source/asia/features/ocbcs-new-generative-ai-chatbot-is-boosting-the-banks-productivity-across-departments-and-locations/ |
| T4 | Microsoft AU on Telstra | https://news.microsoft.com/en-au/?p=52359 |
| T4 | Microsoft FY25 customer stories | https://blogs.microsoft.com/blog/2025/07/28/how-microsofts-customers-and-partners-accelerated-ai-transformation-in-fy25-to-innovate-with-purpose-and-shape-their-future-success/ |
| T4 | CX Today on Salesforce Agentforce | https://cxtoday.com/salesforce-resolves-85-of-its-customer-queries-with-agentforce |
| T4 | Rakuten Today | https://rakuten.today/blog/rakuten-ai-in-2025-embracing-agentic-ai.html |
| T4 | Activant, AI in Procurement | https://www.activantcapital.com/pdfs/ai-in-procurement.pdf |
| T4 | Umbrex prioritisation framework | https://umbrex.com/resources/frameworks/supply-chain-frameworks/ai-use-case-prioritization-framework/ |
| T4 | Okhrem prioritisation framework | https://paul-okhrem.com/ai-use-case-prioritization-framework/ |
| T4 | SG Analytics prioritisation framework | https://www.sganalytics.com/blog/framework-for-ai-use-case-prioritization/ |
| T4 | AI Assembly Lines business-case template | https://aiassemblylines.com/post/ai-business-case-template-cfo-approval-guide |
| T4 | Elevate Consult, EU AI Act / NIST / ISO 42001 | https://elevateconsult.com/insights/ai-governance-frameworks-compared-matching-nist-eu-ai-act-and-iso-42001-to-your-use-case/ |
| T4 | ibl.ai summary of McKinsey agentic | https://ibl.ai/blog/mckinsey-seizing-the-agentic-ai-advantage |
| T4 | NotVeryPrivateEquity, VCP guide | https://www.notveryprivateequity.com/what-is-a-value-creation-plan-in-private-equity/ |

## Appendix B. Known gaps in v0.1

| Gap | Impact | Action |
|---|---|---|
| Screen anchors (2.3), realisation discounts (3.4) and bucket thresholds (3.1) are untested | Scores not yet calibrated | Calibrate on first three engagements; record in change log |
| MGI industry table row pairing inferred from PDF text order | Possible row/value mismatch | Verify against MGI Exhibit 4 before client use |
| No top-tier primary benchmark for finance close-time, fraud-loss %, forecast-error reduction | Band 2 thin for finance and supply chain | Flag as "client-measured only" in business cases |
| DBS S$1bn not split by revenue/cost/risk; control-group construction undisclosed | Programme anchor only | Quote as programme-level, not per-lens |
| Vendor-listed metrics (Google, Microsoft) are self-reported | Catalogue rows T4 | Mark directional; prefer investor-day figures (DBS, Singtel, CBA) |
| No token-cost-per-use-case benchmark for 2025–26 production | TCO run-cost line relies on client quotes | Collect in engagements; add to v0.2 |
