# RIGHT-TO-WIN KIT

**Status: v0.1 draft, untested**

| Field | Value |
|---|---|
| Methodology step | Step 1 of the engagement framework: "Why they exist" |
| Output | The "3–5 reasons this company exists" exhibit (Section 6) feeding the domain screen (Step 2) |
| Owner | Methodology lead |
| Sources | `/home/claude/reports/AI first consulting engagement framework.md` (section "Why they exist needs a six-part test and an AI-era tag"); `/home/claude/research_notes/AI first consulting engagement framework/right_to_win_frameworks.md` |
| Evidence caveat | Every performance claim cited here (coherence premium, 80% return variance, 2.7x odds) is firm-produced and correlational. Say so in client documents. |

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Methodology drafting | First draft from research notes. Untested on a live engagement. |
| v0.2 | — | — | (reserved: first pilot findings, anchor recalibration, κ figures from our own coder-vs-LLM test) |

---

## 0. How the kit fits together

| Stage | Input | Tool in this kit | Output |
|---|---|---|---|
| A. Generate | Research corpus + executive interviews | Section 3 (candidate protocol), Section 4 (interview guides), Section 5 (LLM mining) | Long list of 8–15 candidate strengths, each with a provisional evidence pack |
| B. Test | Long list | Section 1 (six-criterion test, 0–2 scoring, evidence classes) | Scored candidates; pass / temporary edge / fail; incoherence flag |
| C. Tag | Passing candidates | Section 2 (AI-era tag + hollowing check) | strengthened / eroding / hollowing per strength |
| D. Report | Tagged strengths | Section 6 (output template) | 3–5 "reasons this company exists" blocks, each with an implication for the domain screen |

Decision rules in one line each:

| Rule | Statement |
|---|---|
| R1 Right to win | A candidate scoring 2 on all six criteria is a right-to-win capability. |
| R2 Temporary edge | A candidate passing only criteria 1–3 (benefit, barrier, organised) and failing 4–6 is a temporary edge; report it, do not headline it. |
| R3 Incoherence flag | If more than six candidates pass R1, raise the incoherence flag: the list is not yet a system. Re-run the few/mutually-reinforcing test until ≤ 6 remain, and record the flag in the exhibit. |
| R4 Headline count | The exhibit carries 3–5 reasons. Fewer than 3 passing is itself a finding ("adrift"); 6 is the ceiling. |
| R5 Hollowing becomes a value pool | Any strength tagged hollowing or eroding is handed to Step 2 as a candidate value pool, not dropped. |

---

## 1. The six-criterion test

### 1.1 Definitions and lineage

| # | Criterion | Precise definition (what must be true) | Lineage | Source URL(s) |
|---|---|---|---|---|
| 1 | **Benefit** | The capability produces a material, customer-recognised improvement in value (price, quality, speed, risk, access) that is better than named competitors *and* better for the company's own economics. "Material" = enough to tilt a purchase decision or a margin line, not a nicety. | Helmer "benefit"; Prahalad & Hamel "significant contribution to perceived customer benefit"; VRIO "valuable" | https://podscripts.co/podcasts/acquired/7-powers-with-hamilton-helmer ; https://www.valuebasedmanagement.net/methods_corecompetence.html ; https://strategicmanagementinsight.com/tools/vrio/ |
| 2 | **Barrier** | A mechanism that stops motivated and capable rivals (direct, functional, existing and potential) from replicating the benefit within the planning horizon. Named mechanism required: scale economies, network economies, switching costs, branding, cornered resource, process power, counter-positioning (partial), or Morningstar's intangible asset / efficient scale. Rarity is a precondition: if more than one named competitor already holds it, there is no barrier. | Helmer "barrier"; VRIO "rare" + "costly to imitate"; Morningstar five moat sources; Porter trade-offs | https://podscripts.co/podcasts/acquired/7-powers-with-hamilton-helmer ; https://www.lennysnewsletter.com/p/business-strategy-with-hamilton-helmer ; https://strategicmanagementinsight.com/tools/vrio/ ; https://www.morningstar.com/stocks/how-measure-companys-competitive-advantage |
| 3 | **Organised** | The company is structured to capture the value: the capability is named in budgets, roles, management processes, incentives and reviews; leaders can describe how it works ("Do we live it?"). A capability nobody owns or funds fails. | VRIO "organised"; Strategy& "Do we live it?"; Martin & Lafley "management systems" | https://strategicmanagementinsight.com/tools/vrio/ ; https://www.strategyand.pwc.com/gx/en/insights/2002-2013/coherence-premium/hbr-coherence-premium.pdf ; https://www.antoinebuteau.com/playing-to-win-book-summary/ |
| 4 | **Few / mutually reinforcing** | The capability is one of a system of three to six, and it demonstrably strengthens at least one other capability in the set (second-order fit). A strength that stands alone, or belongs to a list of more than six, fails. | Strategy& "system of three to six capabilities"; Porter second- and third-order fit ("a chain as strong as its strongest link") | https://www.strategyand.pwc.com/gx/en/insights/2002-2013/coherence-premium/hbr-coherence-premium.pdf ; https://maaw.info/ArticleSummaries/ArtSumPorter96.htm |
| 5 | **Trade-off / fit** | Keeping the capability requires the company to *not* do something a competitor does (a visible trade-off), and the capability is used across most of the portfolio (product/service fit). Evidence of the trade-off: a market, feature or segment deliberately foregone. | Porter trade-offs ("more of one thing necessitates less of another"); Strategy& product/service fit (Wal-Mart not selling furniture); Martin "where to play / how to win" | https://maaw.info/ArticleSummaries/ArtSumPorter96.htm ; https://www.strategyand.pwc.com/gx/en/insights/2002-2013/coherence-premium/hbr-coherence-premium.pdf ; https://www.antoinebuteau.com/playing-to-win-book-summary/ |
| 6 | **Customer-stated** | Customers name the capability unprompted as a reason they chose, stayed or switched, in the decision/pull phase of their timeline, not only when asked to rate it. Internal belief without external voice fails. | JTBD switch interview (Moesta & Spiek); Clozd win/loss; Umbrex core-competence evidence (win/loss reasons, NPS, retention) | https://jobstobedone.org/switch-interview/ ; https://www.clozd.com/blog/a-framework-for-creating-the-right-win-loss-analysis-questions ; https://umbrex.com/resources/frameworks/strategy-frameworks/core-competence-framework/ |

Note on Collins: the three circles (passion, best-in-world, economic denominator) are used in this kit for candidate generation (Section 3) and the executive guide (Section 4a), not as a scoring criterion. Source: https://jimcollins.com/media_topics/YourCompanysThreeCircles.html

### 1.2 Scoring anchors (0–2 per criterion)

| # | Criterion | 0 — Fails | 1 — Partial | 2 — Passes |
|---|---|---|---|---|
| 1 | Benefit | No customer-recognised difference, or difference exists but not reflected in any economic line (price, share, retention). | Customers recognise it but economics are flat vs peers, or economics show it but customers do not name it. | Customer-recognised and visible in at least one of: price premium, relative share, retention/NPS gap vs named peers. |
| 2 | Barrier | ≥ 2 named competitors already hold it, or it can be bought/hired within 12 months. No mechanism named. | One competitor holds it, or mechanism named but weak (counter-positioning alone; operational excellence; brand without pricing power). | No named competitor holds it; a specific mechanism is named and evidenced (patent, flow data, network, switching cost, process power, cornered resource); expected to hold ≥ 5 years. |
| 3 | Organised | No owner, no budget line, not mentioned in executive interviews unprompted. | Owner exists but capability absent from budgets, incentives or reviews; executives name it inconsistently. | Named owner, funded, appears in performance management and new-offer/acquisition screening; ≥ 70% of interviewed executives name it in their 3–6 list. |
| 4 | Few / mutually reinforcing | Appears in a list of > 6 "strengths", or no documented link to any other candidate. | In a list of ≤ 6 but reinforcement link is asserted, not evidenced. | In a system of 3–6; at least one concrete mechanism by which it strengthens another candidate is documented (e.g. data from A trains B). |
| 5 | Trade-off / fit | No foregone market/feature/segment identifiable; capability used by < 50% of revenue. | Trade-off identifiable but recently breached, or capability used by 50–80% of revenue. | Clear, maintained trade-off a competitor does not make; capability underpins ≥ 80% of revenue (competence-to-offering matrix). |
| 6 | Customer-stated | Not named in any external source; appears only in company materials. | Named when prompted (rating questions, survey lists) or by < 20% of interviewees/documents. | Named unprompted in the decision/pull phase by ≥ 30% of win/switch interviewees, or by ≥ 20% of review/transcript documents coding as "reason to choose". |

Thresholds marked with percentages are v0.1 working anchors with no published consulting source; the notes record that no public template specifies numeric NPS, retention or price-premium gaps (gap noted under KQ2 of the research notes). McKinsey's gross-margin top-30% and Bain's 5.5% real growth / cost-of-equity are the only published hard thresholds and are used in 1.3. Recalibrate after the first three engagements.

### 1.3 Evidence class per cell

Every score cell carries an evidence class. The class, not the score, is what a partner reviews first.

| Class code | Evidence class | Definition | Weight in confidence |
|---|---|---|---|
| F | Filed | Audited financials, regulatory filings, registries (ACRA, DART, EDINET, DBD), patents, signed contracts, earnings-call transcripts (verbatim). | Highest |
| V | Vendor-estimate | Third-party analyst or data-vendor numbers (market share, NPS benchmarks, review aggregates) with stated methodology. | High |
| M | Model-inferred | Our own derivation: LLM-coded frequencies, peer-set ratios we computed, driver-tree inferences. Must carry the method and the reliability figures in Section 5. | Medium |
| I | Interview-anecdote | Statements from executive, win/loss or switch interviews, uncoded or n < 5. | Lowest alone; becomes M once coded across ≥ 8 interviews |

Minimum evidence mix for a score of 2: at least one F or V item plus one I or M item. A 2 resting only on I evidence is downgraded to 1.

### 1.4 Quantitative evidence expected per criterion

| # | Criterion | Primary quantitative evidence | Bar / comparator | Typical class | Source of bar |
|---|---|---|---|---|---|
| 1 | Benefit | Price premium or gross margin vs peer median; relative market share or #1/#2 position in the segment where the capability is deployed | Gross margin in top 30% of industry = "differentiation" (McKinsey); #1 position in core (Bain SVCs) | F, V | https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategy-to-beat-the-odds ; https://www.bain.com/insights/profit-from-the-core-strong-message-for-korean-companies/ |
| 2 | Barrier | ROIC vs peers over ≥ 5 years; rarity count (number of named competitors holding it); durability horizon | Sustained ROIC above peers for ≥ 5 years; Morningstar narrow ≥ 10 years, wide ≥ 20 years expected | F, V, M | https://www.morningstar.com/stocks/how-measure-companys-competitive-advantage ; https://strategicmanagementinsight.com/tools/vrio/ |
| 3 | Organised | Share of capex/opex and headcount explicitly allocated; presence in incentive plans; executive naming consistency | ≥ 70% of executives name it (v0.1 anchor); Strategy& baseline: only 20% of companies agree on key capabilities, 13% reflect them in budgets and reviews | F, I | https://www.strategyand.pwc.com/gx/en/unique-solutions/cds/the-strategy-crisis.pdf |
| 4 | Few / mutually reinforcing | Count of passing candidates; Capabilities Coherence Score (capabilities common across all segments served) | 3–6 (Strategy&); 3–5 (Umbrex) | M | https://www.strategyand.pwc.com/gx/en/insights/2002-2013/coherence-premium/hbr-coherence-premium.pdf ; https://umbrex.com/resources/frameworks/strategy-frameworks/core-competence-framework/ |
| 5 | Trade-off / fit | Share of revenue in competence-to-offering matrix; contribution margin concentration; share of wallet in core customers | ≥ 80% of revenue drawing on the capability (v0.1 anchor); Bain: 20–30% of offerings/customers often drive most economic profit | F, M | https://umbrex.com/resources/frameworks/organization-frameworks/bain-profit-from-the-core-model/ |
| 6 | Customer-stated | Retention / NPS vs peers; share of wallet; share of win/switch interviews and review documents naming the capability as reason to choose | Unprompted naming ≥ 30% of interviewees or ≥ 20% of documents (v0.1 anchor); retention/NPS gap positive vs named peers | V, M, I | https://www.clozd.com/blog/a-framework-for-creating-the-right-win-loss-analysis-questions ; https://jobstobedone.org/switch-interview/ |

Absence of price-premium/gross-margin (criterion 1) and ROIC (criterion 2) evidence is the signal that the candidate is table stakes, whatever the interviews say.

### 1.5 Scorecard layout (one row per candidate)

| Candidate | C1 Benefit (score / class) | C2 Barrier | C3 Organised | C4 Few/reinforcing | C5 Trade-off/fit | C6 Customer-stated | Total /12 | Verdict (R1–R3) |
|---|---|---|---|---|---|---|---|---|
| e.g. "Same-day replenishment across ASEAN cold chain" | 2 / F | 2 / V | 1 / I | 2 / M | 2 / F | 2 / M | 11 | Right to win (C3 to close) |

Verdict logic: all six at 2 = right to win; C1–C3 at 2 with any of C4–C6 below 2 = temporary edge; any of C1–C3 at 0 = fail; > 6 right-to-win rows = incoherence flag.

---

## 2. The AI-era tag

Source for the tag taxonomy and the hollowing check: BCG, "Who Will Win as AI Rewrites Competitive Advantage?" (Aug 2026), https://web-assets.bcg.com/pdf-src/prod-live/which-companies-capture-value-from-ai.pdf . Supporting: Barney & Reeves (2024) https://www.bcg.com/publications/2024/ai-wont-give-you-a-new-sustainable-advantage ; McKinsey (Apr 2026) https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/where-ai-will-create-value-and-where-it-wont ; BCG Executive Perspectives (June 2025) https://www.bcg.com/assets/2025/executive-perspectives-ai-first-companies-win-the-future-10june.pdf

### 2.1 Tag definitions and decision rules

| Tag | Definition | Decision rule (apply in order) | Asset types that typically earn it (BCG / McKinsey) |
|---|---|---|---|
| **Strengthened** | AI increases the benefit or raises the barrier of this capability. | Underlying asset is one that AI amplifies rather than substitutes: flow data (continuously generated by the product and feeding a model that improves the product), network scale, physical assets, trusted relationships / direct customer access, brand trust, owned IP; AND margin and pricing power are stable or rising. | Flow data (VisaNet > 257bn transactions/yr), network scale, physical assets, trusted relationships; proprietary data that improves with use; AI embedded in workflows raising switching costs; ecosystem breadth |
| **Eroding** | AI lets rivals (incl. AI-native attackers) replicate the benefit, so the barrier weakens and the economics are already showing it. | Underlying asset is knowledge/expertise, stock data, operational excellence or headcount scale; AND at least one of share, retention, margin or pricing power is declining vs peers. | Knowledge and expertise, stock data, operational excellence, headcount scale, large back-office or customer-service teams, diffused expertise, expensive content production |
| **Hollowing** | Headline metrics (share, revenue, retention) still look intact, but margin and pricing power are draining: the capability "looks intact internally while weakening externally". | Headline share/retention flat or up, BUT hollowing check (2.2) fails on margin or pricing power. Tag hollowing even if the asset type is on the "strengthened" list. | Any capability whose benefit is being competed away to customers (McKinsey "performance paradox"); regulatory position (narrowing); capital (durable but protects less) |

Tie-breaks:

| Situation | Rule |
|---|---|
| Asset type on "strengthened" list but hollowing check fails | Tag hollowing. The check overrides the taxonomy. |
| Asset type on "eroding" list but all economics stable | Tag eroding (watch), note "economics not yet showing it", set a review date. The taxonomy overrides optimism. |
| The capability *is* "we use AI" or "we adopted AI early" | Not a capability. Barney & Reeves: GenAI access is a benefit without a barrier. Fails C2 unless coupled to a cornered resource, process power, network economies or switching costs. |
| Foundation-model dependence | Assume model-layer parity within 2–3 years; durable advantage "migrates downward" to assets beneath the technology. Score the asset beneath, not the model. |

### 2.2 The hollowing check

Run for every passing candidate before tagging. Comparator is the named peer set from the engagement (5–12 core peers).

| Check | Metric | Pass | Fail (hollowing signal) | Class |
|---|---|---|---|---|
| H1 Headline | Relative market share and retention in the segment where the capability is deployed, 3-year trend | Flat or rising | Falling (this is eroding, not hollowing) | F / V |
| H2 Margin | Gross margin (or contribution margin for the relevant offerings) vs peer median, 3-year trend | Stable or widening gap in company's favour | Narrowing or negative gap while H1 passes | F |
| H3 Pricing power | Price realisation / discount depth / price per unit vs peers; frequency of price-led losses in win/loss | Stable or rising realisation; price rarely the stated loss reason | Realisation falling, discounting rising, or price is the modal loss reason while H1 passes | F / V / M |
| H4 Market narrative | Valuation multiple vs sector peers (listed) or last-round / transaction multiple (private) | At or above peers | Below peers while H1 passes | V |
| H5 Attacker map | Each AI-native competitor and the highest-margin slice of this capability's revenue it could unbundle | No credible attacker on the highest-margin slice | Named attacker already pricing against the highest-margin slice | M / I |

Tag logic: H1 pass + (H2 fail or H3 fail) = **hollowing**. H1 fail + (H2 or H3 fail) = **eroding**. All pass + strengthened-type asset = **strengthened**. H4 and H5 are corroborating; two corroborating fails upgrade a "watch" to the harder tag.

### 2.3 How the tag feeds the domain screen (Step 2)

| Tag | Hand-off to Step 2 | Why |
|---|---|---|
| Strengthened | Candidate *invest* domain: the capability is the anchor for AI-powered moat-building (data flywheel, workflow embedding, faster test-learn-scale). | McKinsey: durable value comes from combining a reinforcing set of AI-powered moats around existing advantage. |
| Eroding | Candidate *defend or reshape* domain: the value pool is the margin already lost plus the cost base of the eroding asset (expertise, headcount scale, operational excellence). | BCG: eroding assets are where AI-native attackers price against the incumbent. |
| Hollowing | Mandatory value-pool entry. The gap between headline share and draining margin is sized as a value pool; the domain is the process or journey where the margin leaks. | Report framework: "an eroding strength is a value pool." A hollowing strength is the highest-priority one because the client cannot yet see it in its own dashboards. |

Each exhibit block (Section 6) ends with a one-line "implication for the domain screen" that names the domain type (invest / defend / reshape), the metric that defines the value pool, and the evidence class of that sizing.

---

## 3. Candidate-generation protocol

Goal: a long list of 8–15 candidate strengths, each phrased as a capability (something the company *does*, combining people, knowledge, tools and process), not a department, product or adjective. Expect most to fail: "most candidates will fail one or more tests, and that is the point" (Umbrex, https://umbrex.com/resources/frameworks/strategy-frameworks/core-competence-framework/).

### 3.1 Phrasing rules

| Rule | Bad | Good |
|---|---|---|
| Capability, not asset | "Our brand" | "Converting brand trust into first-call access to CFOs in Japan" |
| Capability, not department | "Our R&D team" | "Reformulating regulated products for Rx-to-OTC switch in < 18 months" |
| Includes the customer and the comparator | "Great service" | "Same-day replacement parts across six ASEAN markets where rivals quote 5 days" |
| ≤ 20 words | — | — |

### 3.2 Corpus sources and what each yields

| Source | What to extract | Extraction method | Class of resulting evidence | Volume target |
|---|---|---|---|---|
| Earnings-call transcripts (company + 5–12 peers, last 8 quarters) | Management's own claimed differentiators; analyst questions probing margin, pricing, churn; competitor mentions | LLM deductive coding (Section 5), human-verified quotes | F (verbatim) / M (frequency) | All available quarters |
| Annual reports, filings, prospectuses | Named competitors; capex allocation; segment margins; risk factors that reveal trade-offs | Manual + LLM citation retrieval | F | Last 3 years |
| Customer reviews (G2, Trustpilot, app stores, Google, industry portals) | Reasons to choose / stay / leave stated by customers; comparisons to named rivals | LLM deductive coding, saturation over 7–10 runs | M | ≥ 200 reviews or full corpus if smaller; peers too |
| Win/loss records and transcripts (CRM, sales notes, prior interviews) | Decision reasons; where each vendor excelled / fell short; price vs value | LLM coding + Section 4b interviews | M / I | All closed deals last 12 months |
| Analyst notes, broker research, industry reports | Outside-in view of moat; relative share; margin vs peers | Manual reading + citation retrieval | V | 5–10 notes |
| Job postings (company + peers, last 12 months) | Which capabilities the company is funding with headcount; AI-fluent talent; skills rivals are buying | LLM classification of roles to candidate capabilities | M | All postings |
| Patents, trademarks, licences, regulatory approvals | Cornered-resource and intangible-asset barriers | Registry search | F | Full |
| NPS verbatims, churn-reason fields, support tickets | Unprompted customer language about what works | LLM deductive coding | M | Full export |

### 3.3 Executive-side generation (three circles + state it / live it)

| Step | Who | Instrument | Output |
|---|---|---|---|
| E1 | 6–10 executives, interviewed individually before any group session | Section 4a guide | Each executive's unprompted 3–6 list; passion / best-in-world / economic-denominator answers |
| E2 | Methodology team | Tally | Naming-consistency matrix: which capabilities ≥ 70% of executives name (feeds C3) |
| E3 | Three working groups (Collins) | Group 1: passion; Group 2: best-in-world (both "things we do that we cannot be best at" and "things we don't do that we could be best at"); Group 3: economic denominator (profit per customer / employee / transaction / unit) | Brutal-facts list per circle |
| E4 | Fourth group | Overlap | Three lists: current activities failing the test (stop), passing (continue), not yet pursued that might pass (start) |
| E5 | Methodology team | Martin & Lafley "what would have to be true" | For each candidate: the conditions that must hold, the least likely one, the test to run first |

Source for E3–E4: https://jimcollins.com/media_topics/YourCompanysThreeCircles.html ; Source for E5: https://www.antoinebuteau.com/playing-to-win-book-summary/

### 3.4 Merge and de-duplicate

| Step | Rule |
|---|---|
| M1 | Union of corpus candidates (3.2) and executive candidates (3.3). |
| M2 | Merge candidates that name the same mechanism and the same customer benefit; keep the better-phrased statement; record both origins (corpus / executive / both). |
| M3 | A candidate that appears in corpus sources but in no executive list is kept and flagged "customer-visible, not owned" (likely C3 fail, high interest). |
| M4 | A candidate that appears only in executive lists is kept and flagged "internal belief" (likely C6 fail). |
| M5 | Stop at 8–15. If > 15, drop candidates with no F or V evidence and no unprompted customer mention. If < 8, widen the corpus (peers' reviews, older calls) before proceeding. |
| M6 | Build the competence-to-offering matrix (candidates × revenue lines, % of revenue drawing on each) for C5. |

---

## 4. Interview guides

General rules for all three: open-ended; no rating scales in live interviews (Clozd); record and transcribe with consent; two interviewers where possible (one asks, one tracks the timeline); practise internally before the first client interview.

### 4a. Executive guide: "state it / live it" + three circles (45–60 min)

Source: Strategy& Coherence Test, https://www.strategyand.pwc.com/gx/en/insights/2002-2013/coherence-premium/hbr-coherence-premium.pdf ; Collins, https://jimcollins.com/media_topics/YourCompanysThreeCircles.html

| # | Block | Question | Feeds criterion / circle |
|---|---|---|---|
| 1 | Way to play | In one sentence, how does this company create value for customers that competitors do not? | C1, "state it" |
| 2 | Capabilities system | Name the three to six things this company does better than anyone that make that possible. Do not list products. | C4, naming matrix (C3) |
| 3 | Reinforcement | Pick two of those. How does one make the other stronger? Give a concrete example from the last year. | C4 |
| 4 | Barrier | For your top capability: which competitor is closest to copying it, and what stops them? How long would it take a well-funded entrant? | C2 |
| 5 | Trade-off | What does this company deliberately *not* do, or which customers does it turn away, in order to protect those capabilities? When was that last tested? | C5 |
| 6 | Live it: money | Where do these capabilities show up in the budget, in incentive plans, and in how new products or acquisitions are approved? | C3 |
| 7 | Live it: fit | What share of revenue genuinely draws on these capabilities? Which products or units do not? | C5 |
| 8 | Circle: best in world | What could this company be the best in the world at (even if it is not yet)? What does it do today that it can never be best at? | Collins best-in-world |
| 9 | Circle: economic engine | If you could pick one ratio (profit per customer, per employee, per transaction, per site) to drive, which would it be and why? | Collins economic denominator |
| 10 | Circle: passion + AI | What are people here genuinely obsessed with? And of your 3–6, which would an AI-native entrant find easiest to copy in two years? | Collins passion; AI-era tag |

Close: ask for three documents that prove answers 6 and 7 (budget, incentive plan, offer-approval criteria).

### 4b. Win/loss guide (Clozd-style, 30–45 min)

Source: https://www.clozd.com/blog/a-framework-for-creating-the-right-win-loss-analysis-questions

| # | Topic area | Opening (broad, open-ended) | Drill-downs (use only if not covered) |
|---|---|---|---|
| 0 | Story | What prompted the evaluation? How did you find the vendors? How did you run the process? What was the final decision and why was it the right one? | Let them tell it end to end before any topic question. |
| 1 | Product / solution | Which capabilities mattered most to you? | Where was each vendor strongest and weakest? Which capability would you not give up? |
| 2 | Sales experience | What was it like working with each vendor's team through the process? | Who understood your business best? What did they do that others did not? |
| 3 | Pricing and packaging | How did price compare across vendors, and how did you assess value or ROI? | Was anyone's premium justified? By what? |
| 4 | Competitive landscape | Which vendors did you evaluate? | Where did each excel or fall short? How clear was it what set the chosen vendor apart? Did your perception of any brand change during the evaluation? |
| 5 | Buying committee | Who was involved and who had the final say? | Whose concerns changed the decision? |
| 6 | Implementation expectations | What did you expect after signing, and how did that affect the choice? | What risks worried you most? |
| 7 | Decision timeline | Walk me through the key dates from first conversation to decision. | What slowed or accelerated it? |
| W | Win-specific | Which vendor offered the strongest alternative, and what nearly made you choose them? | — |
| L | Loss-specific | Which vendor did you choose, and why? What would we have had to do differently to win? | How clear was it what set them apart from us? |

Coding note: any capability named in blocks 0, 1, 3 or L *before* the interviewer introduces it counts as "unprompted" for C6.

### 4c. Switch / churn timeline guide (Moesta & Spiek, 45–90 min)

Source: https://jobstobedone.org/switch-interview/

Recruit: customers who switched to the company, switched away, or almost switched, in the last 30–90 days. Walk the timeline with concrete events; never ask about the four forces directly, let them emerge.

| Phase | Timeline question | Follow-ups | Force usually surfaced |
|---|---|---|---|
| First thought | When did you first start thinking you might need something different? Where were you? What had just happened? | Who was with you? What did you do right after? | Push (of the current situation) |
| Passive looking | After that first thought, what did you notice that you had not noticed before? | What did you read, hear, or see? From whom? | Push, early Pull |
| Event(s) | What happened that turned noticing into actually looking? | Dates, people, numbers. "And then what happened?" | Push (triggering event) |
| Active looking | What did you compare? What did you rule out and why? | What did you try, trial, or ask for a demo of? What were you afraid would go wrong? | Pull (of the new), Anxiety (about the new) |
| Decision | What was the moment you decided? What tipped it? | Who else had to agree? What almost stopped you? | Pull vs Anxiety |
| Purchase / switch | What did you have to give up or stop doing to make the switch? What did you keep doing out of habit? | How long between decision and actually switching? Why that long? | Habit (of the present) |
| Afterwards | What is better now, in your words? What is worse? | If you had to explain to a peer why you chose [company], what would you say? | Pull (confirmed) → C6 evidence |

Techniques (from the source): play dumb; deliberately misstate the sequence so they correct you; treat contradictions as refinements, not errors; interview in pairs.

Coding note: a capability counts as "named in the pull/decision phase" for C6 only if it appears in the Active-looking or Decision rows unprompted.

---

## 5. LLM-mining protocol for reviews and transcripts

Reliability basis (all from the research notes):

| Finding | Number | Source | Control it justifies |
|---|---|---|---|
| Deductive coding of concrete constructs reaches human agreement; interpretive constructs do not | κ ≥ 0.70 for 25 of 34 constructs; best κ 0.91–0.95; worst κ 0.10–0.12 | Liu, Zambrano, Baker et al., JLA 2025, https://www.learning-analytics.info/index.php/JLA/article/download/8575/7877 | Deductive codebook of concrete codes (5.1); construct-level κ check (5.6) |
| Few-shot raises recall but overgeneralises; negative examples improve precision | Qualitative finding, same paper | JLA 2025 | Few-shot with negative examples (5.2) |
| Inductive thematic analysis alters or truncates quotes | Quote consistency with themes 64–87% and 33–79%; strongly supportive quotes 36–67% and 18–55%; themes saturate after 7–10 runs; sycophancy when questioned | Mehta et al., Scientific Reports 2025, https://www.nature.com/articles/s41598-025-18969-w | Citation-grounded output (5.3); string-match quote fidelity (5.4); 7–10 saturation runs; no conversational "are you sure?" merges |
| Earnings-call claim extraction misses citations and fabricates when evidence is absent | Citation precision 0.972, recall 0.714, F1 0.820; claim precision 0.630, recall 0.666; hallucinated a specific answer 48.3% of the time when evidence removed | Zhao et al., arXiv 2610.00969, https://arxiv.org/html/2610.00969v1 | Abstention instruction and abstention test (5.5); human recall audit on a sample because recall 0.71 means ~3 in 10 supporting passages are missed |
| Financial-text classification depends heavily on prompting; weak on rare categories and vagueness | Best 3-class accuracy 0.83, 5-class 0.61; vagueness recall 0.471; few-shot and chain-of-thought improved results | KC Fed RWP 23-12, https://www.kansascityfed.org/documents/9862/rwp23-12cookkazinnikhansenmcadam.pdf | Few codes, binary where possible; report frequencies not sentiment (5.7) |
| AI gains for strategy teams are consistent only in market intelligence and research | BCG survey, Mar 2026 | https://www.bcg.com/publications/2026/the-corporate-strategy-function-in-an-ai-first-world | Scope: LLM does retrieval and first-pass coding; humans score the six criteria |

### 5.1 Deductive codebook (v0.1)

Codes are concrete and binary per document segment. No sentiment codes.

| Code | Definition | Applies to | Feeds |
|---|---|---|---|
| BENEFIT_NAMED | Segment states a specific thing the company does better, with the customer outcome | Reviews, win/loss, switch, calls | C1, candidate generation |
| COMPARATOR_NAMED | Segment names a competitor and a dimension of comparison | All | C2 rarity, C6 |
| REASON_TO_CHOOSE | Segment gives a reason the customer chose / renewed / switched to the company | Reviews, win/loss, switch | C6 |
| REASON_TO_LEAVE | Segment gives a reason the customer left / chose a rival | Reviews, loss, churn | C6 (negative), hollowing H3 |
| PRICE_JUSTIFIED | Segment states the premium was worth it, and why | Reviews, win | C1, H3 |
| PRICE_LOSS | Segment states price was the deciding reason against | Loss, churn | H3 |
| BARRIER_CLAIMED | Management or analyst names a mechanism that protects the advantage | Calls, analyst notes | C2 |
| TRADEOFF_STATED | Management states something deliberately not done / a segment exited | Calls, filings | C5 |
| MARGIN_PRESSURE | Analyst question or management answer about margin, pricing, discounting | Calls | H2, H3 |
| CAPABILITY_FUNDED | Segment links spend, hiring or org change to a named capability | Calls, filings, job postings | C3 |

Each code carries a `candidate_id` field mapping to the long list (or `NEW` if the segment proposes an unlisted capability).

### 5.2 Prompting standard

| Element | Requirement |
|---|---|
| Mode | Deductive: the codebook above is supplied in full; the model does not invent codes except `NEW` with a proposed statement |
| Few-shot | ≥ 3 positive examples per code from the client's own corpus (not synthetic) |
| Negative examples | ≥ 2 per code showing near-miss segments that must NOT be coded (e.g. generic praise without a specific capability; a competitor named without a comparison dimension) |
| Temperature | 0 for coding runs; 0.7 cap for any theme-proposal run (Mehta et al. observed nonsense at ≥ 1.5) |
| Context window | Segment plus the preceding and following segment only; JLA found context helps multi-line constructs and hurts single-line ones, so test both and record which is used per code |
| Runs | 7–10 independent passes over the corpus for the `NEW` channel until no new candidate emerges in two consecutive runs; single pass at temperature 0 for fixed codes |
| Forbidden | Asking the model to "reconsider" or merge codes conversationally (sycophancy risk); asking for sentiment scores; asking for summaries without citations |

### 5.3 Citation-grounded output schema

Every coded item is emitted as one record; records without a verbatim span are rejected at ingest.

| Field | Content |
|---|---|
| `doc_id` | Source document identifier (URL, transcript id, review id) |
| `segment_id` | Position within the document |
| `code` | One code from 5.1 |
| `candidate_id` | Long-list id or `NEW` |
| `quote` | Verbatim span, copied exactly, ≤ 60 words |
| `char_start`, `char_end` | Offsets in the source text |
| `competitor` | Named competitor if any |
| `confidence` | Model's own 0–1 (recorded, not trusted) |
| `abstain` | `true` if the segment does not support any code |

### 5.4 Quote fidelity verification (string match)

| Step | Rule | Reason |
|---|---|---|
| Q1 | Exact substring match of `quote` against the source at `char_start:char_end` after whitespace normalisation only | Mehta et al.: quotes altered or truncated in ways that changed meaning; fidelity only 33–87% |
| Q2 | Any mismatch → record rejected, logged, not repaired by the model | Repair invites a second fabrication |
| Q3 | Fidelity rate reported per run; run accepted only if ≥ 98% of records pass Q1 | Target set well above the 33–87% baseline because every surviving quote may appear in a client exhibit |
| Q4 | Of passing records, a 10% random sample is read by a human against the source for *meaning* (not just string) | String match does not catch a correct quote attached to the wrong code |

### 5.5 Abstention test

| Step | Rule | Reason |
|---|---|---|
| A1 | Prompt instructs: "If the segment does not contain evidence for a code, set `abstain: true` and emit no quote." | Zhao et al.: without evidence, models produced a specific answer 48.3% of the time |
| A2 | Before each engagement run, inject a control set: ≥ 50 segments with the supporting evidence removed or replaced with unrelated text from the same corpus | Tests that abstention actually fires |
| A3 | Pass threshold: ≥ 95% abstention on the control set; any fabricated number or competitor name on a control segment fails the run | Numbers and names are what end up in exhibits |
| A4 | Also inject ≥ 50 segments that DO contain evidence to confirm recall is not destroyed by the abstention instruction; record recall | Benchmark recall was 0.714; we expect to miss passages and must size the human audit accordingly |

### 5.6 Reliability check against human coders

| Step | Rule |
|---|---|
| K1 | Two human coders code a stratified sample of ≥ 100 segments per source type using the same codebook |
| K2 | Compute Cohen's κ human-vs-human and LLM-vs-human-consensus per code |
| K3 | A code is used in evidence class M only if LLM-vs-consensus κ ≥ 0.70 (JLA threshold); below 0.70 the code's output is demoted to class I and must be re-read by a human before use |
| K4 | Codes where humans themselves disagree (κ < 0.60) are rewritten for concreteness before any further LLM run (JLA: constructs humans disagree on are also hard for the model) |
| K5 | Report the κ table in the engagement appendix; this is the reliability disclosure a Big-4 reviewer will ask for |

### 5.7 Reporting rules

| Rule | Statement |
|---|---|
| Frequencies, not sentiment | Report "share of documents coding REASON_TO_CHOOSE for candidate X" with n and the source mix; never a sentiment score |
| Missed-evidence disclosure | State that citation recall in the published benchmark was 0.71 and that a human audit of the sample found [n] additional supporting passages |
| Every exhibit quote | Must trace to a record that passed Q1–Q4 |
| Peers coded identically | The same codebook is run over peer reviews and calls so that C2 rarity and C6 are comparative, not absolute |

---

## 6. Output template: "3–5 reasons this company exists"

One block per reason. 3–5 blocks. If the incoherence flag (R3) was raised, say so above the blocks with the number of candidates that passed and how the list was reduced.

### 6.1 Block template

| Field | Content | Rule |
|---|---|---|
| **Reason #** | 1–5 | Ordered by total six-criterion score, then by economic weight |
| **Statement** | ≤ 20 words, capability phrasing (Section 3.1) | Must name the customer benefit and the comparator |
| **Evidence pack** | 3–5 cited facts, each with: fact, source, evidence class (F/V/M/I) | At least one F or V. Quotes must have passed 5.4. Numbers must trace to a filed or vendor source or be labelled M with method. |
| **Six-criterion scores** | C1–C6, each as score / class, plus total /12 | From Section 1.5 |
| **Verdict** | Right to win / temporary edge | Per R1–R2 |
| **AI-era tag** | Strengthened / eroding / hollowing, with the hollowing-check row results (H1–H5) | Per Section 2 |
| **Implication for domain screen** | One line: domain type (invest / defend / reshape), the process or journey, the metric that defines the value pool, and the evidence class of the sizing | Per Section 2.3 |
| **Open items** | What would raise any criterion to 2; the Martin "what would have to be true" test still outstanding | Keeps v0.1 honest |

### 6.2 Worked skeleton (illustrative structure only; no client data)

| Field | Example content |
|---|---|
| Reason # | 2 |
| Statement | Same-day spare-part replenishment across six ASEAN markets where named rivals quote five working days. |
| Evidence pack | (1) Segment gross margin 4.2 pp above peer median, 3-yr avg — filed accounts, peer set of 7 — **F**. (2) Relative market share 1.6x next competitor in ASEAN aftermarket — analyst note — **V**. (3) 34% of 212 coded reviews code REASON_TO_CHOOSE on delivery speed; peers 9–14% — LLM coding, κ 0.81 vs human consensus — **M**. (4) 7 of 9 win interviews named delivery speed in the decision phase unprompted — interviews — **I→M**. (5) Capex to regional hubs disclosed as a named programme, 3 consecutive years — filing — **F**. |
| Six-criterion scores | C1 2/F · C2 2/V · C3 2/F · C4 2/M · C5 1/M · C6 2/M · **Total 11/12** |
| Verdict | Right to win, conditional on C5 (two product lines, 23% of revenue, do not use the hub network). |
| AI-era tag | **Strengthened** — physical assets + flow data (parts telemetry). Hollowing check: H1 pass, H2 pass, H3 pass, H4 pass, H5 one attacker on consumables slice (watch). |
| Implication for domain screen | Invest domain: predictive replenishment on the parts-telemetry flow; value pool defined by inventory days and stock-out rate vs peers; sizing class M (driver-tree estimate). |
| Open items | C5: decide whether to move the two off-network lines onto the hubs or exit them. Test first: does hub economics hold at those lines' volumes? |

### 6.3 Exhibit header and footer

| Element | Content |
|---|---|
| Header | Company; date; peer set (names, n); corpus sizes by source; interview counts (executive / win / loss / switch-churn); incoherence flag status |
| Footer | Reliability disclosure: κ table summary, quote-fidelity rate, abstention-test result, benchmark recall 0.71 and audit finding; statement that performance correlations cited are firm-produced and correlational |

---

## 7. Known gaps carried from the notes (do not paper over)

| Gap | Effect on this kit | Mitigation |
|---|---|---|
| No published numeric thresholds for NPS, retention or price-premium gaps | All percentage anchors in 1.2 and 1.4 are v0.1 working values | Recalibrate after three engagements; disclose as "working anchors" |
| Prahalad & Hamel primary text not retrieved | "3–5" count relies on secondary summaries | Count rule rests on Strategy& 3–6 (primary) |
| Morningstar ROIC-vs-WACC threshold not stated in fetched source | C2 durability bar uses years, not a ROIC spread | Add spread once a primary source is filed |
| No paper tested "reason for choosing vendor" as an LLM construct | Expected high reliability is an inference | 5.6 κ check is mandatory, not optional |
| Helmer's own view on AI not retrieved; only third-party 7 Powers × AI mappings | AI-era tag rests on BCG/McKinsey, not Helmer | Do not attribute AI-era claims to Helmer |
| No independent replication of the coherence premium | Business case for the step is correlational | State it as such in every client document |
