# PLUMB Pricing Ladder (one-pager)

**Status: v0.2 draft** (red-team review 2026-10-25 applied; see change log)
**Owner:** Founder (Commercial workstream)
**Purpose:** The four-tier ladder plus add-ons and design-partner terms, with the market evidence each number rests on. Numbers labelled *working value* are placeholders to recalibrate after three engagements; items marked **[VERIFY]** have no primary source yet.
**Selling rule:** Sold on verification rigour, speed and disclosure, never on "AI-generated". Clients price AI involvement as a discount, not a premium (Source Global survey: 70% would not trust an AI-produced consultancy report — [ResultSense](https://www.resultsense.com/news/2026-08-04-consultancy-clients-distrust-ai-reports/)).

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Founder | Initial draft from business-model section of the engagement-framework report, GA-gate plan and consulting-landscape research note |
| v0.2 | 2026-10-25 | Product | Red-team review 2026-10-25 applied: present-tense quality claims removed, measured state stated (Blocker 5 / §2.1); Tier 1 split into Phase A (public data, instrument, interviews; base price; no slippage penalty) and Phase B (post-onboarding confidential data; day-5 cut-off applies only here) (Blocker 4 / §1(a) step 4); "peer percentile" replaced by "rank within named peers (n disclosed)" where core peer n < 15 and the two benchmark populations never pooled (Blocker 3 / §2.3); Big-4 S$400K anchor replaced by the Singapore evidence band, UK day-rate derivation kept as a footnote (Major / §1(b)); retainer renamed "Benchmark Refresh" (§4.5); quality undertaking cross-referenced to the refund-on-fabrication clause (Major / §3.5) |

---

## 1. The ladder at a glance

| Tier | Name | Price (S$) | Duration | Buyer moment | Converts to |
|---|---|---|---|---|---|
| 0 | Free self-scored benchmark | 0 | 30–45 min self-serve | "Where do we stand?" | Tier 1 (lead magnet); builds the *self-scored* benchmark population (never pooled with engagement scores, §2) |
| 1A | PLUMB Assessment — Phase A (public data, instrument, interviews) | 25K–85K by size band (the base) | 12 working days | Board/ExCo wants a defensible AI plan; procurement can approve a public-information advisory engagement with no confidential data and no system access | Phase B; Tier 2 or 3; fee credited within 90 days |
| 1B | PLUMB Assessment — Phase B (confidential extracts) | Priced per §3.2 as an option on Phase A | +8 working days after onboarding clears | Client's third-party onboarding (NDA/DPA, information-security questionnaire, SOC 2 or equivalent evidence) has cleared | Tier 2 or 3 |
| 2 | Outcome-priced implementation | 60–70% base + 30–40% performance, **or** 15–25% of verified savings | Per use case, 3–12 months | Use cases from Tier 1 with a measurement design | Tier 3 |
| 3 | Benchmark Refresh retainer | 5K–12K / month | Rolling, quarterly review | Client wants the scorecard to stay current as regulation moves | Renewal; Tier 2 top-ups |
| Add-ons | MAS AIRM gap, AU DTA supplier pack, ISO 42001 readiness, AI TAP-method testing | Priced per section 6 | 1–3 weeks each | Regulatory clock | Any tier |

**What PLUMB can say about quality today (review Blocker 5).** No present-tense quality claim in this file may exceed what `runs/` shows. First real run (Great Eastern, 2026-10-25): citation resolution 0.2, one extractor defect, four of five peer-size claims withheld, no deck yet signed by a named independent reviewer. The design target (every number traces to a fetched, hashed source or it is not in the deck) is stated as a target; the sentence that is already true is *"every claim we could not verify is listed, not hidden."*

---

## 2. Tier 0 — Free self-scored benchmark

| Item | Content |
|---|---|
| What the client gets | Self-scored capability score (0–100, four bands) on the 48-item instrument shown as **self-view and evidence-capped view side by side**, value-axis profile (V1–V4), compliance sub-dimension score, percentile within the *self-scored* population where n ≥ 15 (otherwise labelled), one-page PDF with the cap rule stated on screen one |
| What it collects | Industry, APAC sub-region, size band, listed/unlisted, 48 item self-scores, 4 value-axis answers, 8 compliance sub-dimension answers, respondent role, contact (optional), consent to anonymised benchmark reuse |
| **Cap at level 3 rule** | Self-reported scores are capped at level 3 per item unless an artefact of the item's required evidence class is logged. The free instrument has no evidence upload, so every Tier 0 entry's *evidenced view* is ≤ 3 per item and cannot land above the Emerging band (C ≤ 50). The rule is shown on the first screen before any answer is given, and the output leads with the uncapped self-view beside the capped view with the one-line explanation "levels 4–5 are evidence levels; this is the to-do list that would move them". Rationale: self-report must not lift a score above the production boundary without evidence (`methodology/maturity-instrument.md` §5.4; review §1(a) step 2, §2.2) |
| Benchmark population | Tier-0 entries form the **self-scored population** (`population = self` in `instrument/plumbscore`). Engagement scores form the **evidenced population**. The two are never pooled into one percentile and a Tier-0 pool is never presented to an FI as its peer set (review §2.3, §2.9, §4.3). Expect the free pool to be suppliers and mid-market; label it so |
| Benchmark disclosure | Percentile output prints n, population, peer-set definition date and the share of entries that are self-scored only vs evidence-gated |
| What it does not include | Peer-set construction, outside-in research, interviews, right-to-win test, value pools, use cases, evidence pack, any verification statement |
| Why free | Seeds the proprietary benchmark database, which is the moat PwC advertises (500+ organisations, percentile ranking) and the GA criterion (n ≥ 30). Free self-scored scorecards are the observed lead-magnet pattern ([Summit Trails](https://summittrails.com/blog/ai-readiness-assessment-cost/)) |
| Conversion hook | Output page shows which items would move with evidence, and the Tier 1 size-band price |

---

## 3. Tier 1 — PLUMB Assessment (fixed fee), Phase A and Phase B

Tier 1 is sold in two phases (review Blocker 4). **Phase A** uses public data, the instrument and interviews only; no confidential extract leaves the client; procurement can approve it as a *public-information advisory engagement, no confidential data, no system access*, which is the light onboarding tier at most FIs. **Phase B** starts only after the client's third-party onboarding has cleared (NDA/DPA signed; information-security questionnaire answered; SOC 2 or equivalent evidence provided; LLM-vendor ZDR confirmed in writing per charter §4) and adds the confidential extracts. Phase A is priced and sold alone; Phase B is a written option at list.

### 3.1 Price by client size band (Phase A = the base)

| Client size (staff) | Phase A fixed fee (S$) | Phase B option (S$) | Singapore market band for AI readiness assessments (S$) | Market duration | Notes |
|---|---|---|---|---|---|
| < 100 | 25K–35K | +8K–12K | 15K–35K (2–3 wks) | 2–3 weeks | Floor is 25K: below that the verification pipeline and independent review cannot be covered (kill criterion in GA plan: "fee pressure below S$25K for mid-size clients") |
| 100–1,000 | 40K–65K | +12K–20K | 40K–85K (3–4 wks) | 3–4 weeks | Core band; GA margin test is delivered cost ≤ 35% of fee at the 40–85K band |
| > 1,000 | 65K–85K | +20K–30K | 90K–200K (4–6 wks) | 4 weeks | Under the market band; larger peer sets and more interviews are absorbed by the amortised stack. Above 85K + Phase B only with scope extension (section 3.4) |

Phase B option prices are *working values* **[VERIFY]** against the first three quotes. Market bands: Pertama Partners Singapore/SEA pricing guide, 8 Feb 2026, updated 15 Mar 2026 ([Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide)). The guide's figures are internally inconsistent in places (general range vs tiered table); the tiered table is used here.

### 3.2 What is in

**Phase A — days 1–12 — public data, instrument, interviews. No confidential extracts.**

| Phase | Days | Included |
|---|---|---|
| 0 Scoping and acceptance | 1–2 | Conflict check, engagement charter, peer-set protocol, storyline hypothesis tree, ghost deck, AI-use disclosure |
| 1 Outside-in research sprint | 2–8 | Nine research modules on public sources; peer set of 5–12 core plus secondary tier; outside-in maturity signals; QA gate 1 (automated: URL health, claim-to-passage match, two-upstream check, aggregator trace, AI-page rejection); run executed with egress and every attachment reconciled before anything is shown |
| 2 Instrument and interviews | 5–12 | 48-item self-assessment to 10–30 leaders (cap rule shown on screen one; self-view and evidenced view side by side); 6–10 executive interviews; external interviews only from public reviews and agent-channel sources unless contracted as an add-on (§3.3); QA gate 2 (leadership-perception variance; quote verification) |
| 3A Synthesis on Phase A inputs | 10–12 | Two-axis maturity score (self-view vs evidenced view); **rank within the named core peers (n disclosed)** on the outside-in signals that were computed, with each peer's value shown — a peer *percentile* is reported only where the evidenced peer population has n ≥ 15; right-to-win exhibit "executive-stated, corpus-corroborated" (C1–C5); value pools sized in two bands from public financials; use-case list gated and tiered from public information; MAS-mapped evidence-pack skeleton; QA gate 3 (independent reviewer, line-by-line) |
| 4A Delivery | 12 | Phase A board read-out: storyline deck; evidence appendix with source log and confidence labels; gap register ("removed, not footnoted"); AI-use disclosure; engagement file; 30/60/90 plan for Phase B and the first controls |

**Phase B — post-onboarding, +8 working days — confidential extracts.** Starts on the day onboarding clears, not before.

| Phase | Days (from onboarding clearance) | Included |
|---|---|---|
| 2B Client data | 1–5 | KPI extracts into the driver tree (D1, D2); win/loss and churn records (D3); customer contact list for external interviews (D4); AI inventory, governance papers, vendor contracts, incident log (D6–D11); 8–12 external win/loss/churn interviews. **Day-5 data cut-off applies here and only here** |
| 3B Synthesis | 4–8 | Value pools re-sized on client KPIs; use cases with business cases on system-measured baselines; measurement design; full 10-artefact evidence pack; QA gate 3 re-run on every changed number |
| 4B Delivery | 8 | Full board deck superseding the Phase A read-out; 6/12-month roadmap; measurement design; engagement file closed; anonymised update of the evidenced benchmark population |

### 3.3 What is out

| Excluded | Available as |
|---|---|
| Implementation of any use case | Tier 2 |
| Vendor selection, RFP drafting, architecture design | Tier 2 or separately scoped |
| Regulatory legal opinions | Client's counsel; PLUMB produces a regulatory-exposure map, not advice |
| Primary consumer research (surveys, panels) | Scope extension |
| External win/loss/churn interviews in Phase A (contacts are D3/D4 confidential data) | Phase B, or a priced interview add-on (review §2.4) |
| More than 12 peers in the core set, more than 10 executive interviews, more than 12 external interviews | Scope extension |
| Technical testing of a client AI system (Moonshot / AI Verify toolkit) | AI TAP-method testing add-on |
| Any work after Phase B day 8 | Tier 3 retainer |

### 3.4 Commercial terms

| Term | Rule |
|---|---|
| Payment | Design partners: 30% on charter sign-off, 40% at the QA gate 2 read-out, 30% on delivery of the Phase A deck (review §1(b)). Phase B invoiced on its own delivery. List clients: 50% on charter sign-off, 50% on delivery |
| Fee credit | 100% of the Tier 1 fee is credited against Tier 2 or Tier 3 work contracted within 90 days of the final deliverable. Pattern observed in market: WorkWise US$12,500 sprint credited against a US$25K+ engagement within 90 days ([Summit Trails](https://summittrails.com/blog/ai-readiness-assessment-cost/)) |
| Scope extension | Priced per additional module/interview block; never exceeds 85K + Phase B without moving the client to a bespoke SOW |
| Phase A condition | Client makes interviewees and instrument respondents available by day 10. **No slippage penalty attaches to client data in Phase A**: Phase A needs no confidential extract, so there is nothing for the client to be late with. Interview slippage extends the timeline day-for-day |
| Phase B condition | The day-5 data cut-off (charter §4) applies to Phase B only and counts from onboarding clearance; slippage past it extends the Phase B timeline, not the fee, up to 10 working days, after which a change order applies |
| Quality undertaking | Design target: every citation resolves; every quote string-matches its source; every load-bearing number has two independent upstreams or is labelled single-sourced; claims that cannot be verified are removed and listed in the gap register. Independent reviewer, named in the charter, signs QA gate 3. **Refund on fabrication:** any citation in a delivered deck that does not resolve to the stored source, or any quotation that does not match it, triggers the stated per-instance fee refund and re-issue of the deck under `engagement-letter-clauses.md` §3.6 (model wording, counsel review). Measured state as of 2026-10-25 is in `runs/`; this undertaking is not a claim that the target has been met |

---

## 4. Tier 2 — Outcome-priced implementation

### 4.1 Structures

| Structure | Split | When used | Market evidence |
|---|---|---|---|
| A. Base + performance | 60–70% base fee (milestones) + 30–40% performance bonus against agreed metrics | Default for save-money and avoid-risk use cases where a baseline exists | Singapore market structure ([Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide)) |
| B. Savings share | 15–25% of verified cost savings over an agreed measurement window (12 months default), no base fee or a reduced base | Only where the measurement design (below) is signed and data access is contractual | Singapore market: cost-savings share 15–25%; revenue-uplift share 10–20% ([Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide)) |
| Direction of market | McKinsey: about a third of revenue underwriting outcomes, target over half ([HBR IdeaCast](https://hbr.org/podcast/2026/01/where-mckinsey-and-consulting-go-from-here)); BCG: ~75% of largest AI cases on variable fees; 73% of buyers prefer outcome-tied pricing ([WebProNews](https://www.webpronews.com/consultants-put-skin-in-the-ai-game-as-clients-demand-proof-of-results/)) | | |

### 4.2 Measurement-design preconditions (all required before signing structure A or B)

| # | Precondition | Source of rule |
|---|---|---|
| 1 | Use case passed the Tier 1 hard gates: data rights, named owner, baseline, measurement plan, safety boundary | Use-case matrix gates (`methodology/value-and-use-case-kit.md`) |
| 2 | Baseline measured over ≥ 3 months (or one full business cycle) before go-live, from system records not estimates | Phase 4 measurement design |
| 3 | Control group or counterfactual method agreed in writing (holdout, pre/post with seasonality adjustment, or synthetic control) | Phase 4 measurement design |
| 4 | Metric owner on the client side named; data extract cadence and format agreed; PLUMB read access contractual | Gate "owner" |
| 5 | Stop conditions and re-baseline triggers defined (volume shift > X%, scope change, model change) | Phase 4 "stop conditions" |
| 6 | Realisation discount applied to the business-case ceiling; the performance target is set on the discounted figure | Value & use-case kit failure-rate table |
| 7 | Dispute mechanism agreed (see `engagement-letter-clauses.md` §11) | |
| 8 | Risk tier T0–T2 only for savings-share; T3+ use cases use structure A with the compliance checklist costed into base | `compliance/risk-tiers-and-gates.md` |

### 4.3 Guardrails

| Guardrail | Rule |
|---|---|
| Cap on performance fee | Performance component capped at 150% of what the base would have been at list, so the firm is never incentivised to overstate savings |
| Floor | Base covers delivered cost; performance is margin |
| Tier 1 credit | Applied to the base component |

---

## 5. Tier 3 — Benchmark Refresh retainer

| Item | Content |
|---|---|
| Price | S$5K–12K per month, 12-month minimum, quarterly review. Market band for retainers at 10 hours/month is S$5K–12K ([Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide)) |
| 5K tier | Quarterly benchmark refresh (re-score against updated peer set and n); regulatory-status-map update for the client's jurisdictions; one 90-minute review call per quarter |
| 8K tier | 5K tier + control-library resync applied to the client's use-case inventory each quarter (ATLAS monthly, OWASP, NIST RMF revision, MAS text); re-tiering of use cases where the map moved; evidence-pack artefact updates |
| 12K tier | 8K tier + annual re-run of the 48-item instrument with evidence, updated scorecard and leadership-variance exhibit; standing access to the engagement lead (up to 10 hours/month); procurement-stage AI disclosure support for the client's own tenders |
| Why it exists | Converts the assessment into recurring revenue on a high-fixed, low-marginal cost base; the regulatory window (Dec 2026 – Oct 2028) means a scorecard dated today is stale within a quarter |
| Name | "Benchmark Refresh": the benchmark, the peer set and the regulation all move; the retainer keeps the client's position current. (Renamed from "Moving Goalpost" per review §4.5: that phrase reads in a Singapore boardroom as "changing the rules after the fact") |

---

## 6. Add-ons

Prices below are *working values* with no direct market evidence in the notes; **[VERIFY]** against first three quotes.

| Add-on | Scope | Indicative price (S$) | Duration | Buyer | Evidence base |
|---|---|---|---|---|---|
| MAS AIRM gap assessment | Inventory with MAS fields, materiality rating, s.3–4 (Oct 2027) and s.5–6 (Oct 2028) gap list, remediation roadmap. Section numbering **[VERIFY]** against the MAS PDF | 20K–45K | 2–3 weeks | Singapore FIs and their suppliers | Wedge segment in GA plan; MAS clock |
| Australian DTA supplier pack | AI register entry, impact assessment, ATRS-style transparency statement (Tier 1 + Tier 2) in the DTA format, ahead of 30 Apr 2027 | 15K–35K | 1–2 weeks | Suppliers to Australian agencies | [ACS](https://membership.acs.org.au/member-insight/2025-12-9-Version-2-0-Policy-for-the-Responsible-Use-of-AI-in-Government,.html) |
| ISO/IEC 42001 readiness | Clause 4–10 and Annex A gap assessment, statement of applicability draft, evidence-pack mapping, certification-body shortlist (TÜV SÜD PSB under SAC in Singapore) | 25K–50K | 2–3 weeks | Any client pursuing certification; EDGE-eligible if rules confirmed **[VERIFY]** | Compliance-layer report |
| AI TAP-method testing | Benchmarking of one client AI system using Project Moonshot and IMDA LLM/agentic starter kits across the five risk areas; report in the evidence-pack artefact 5 format | 20K–40K per system | 2–3 weeks | FIs (MAS independent-evidence expectation), public-sector suppliers | [LittleBigRedDot](https://littlebigreddot.com/imda-ai-agent-testing-kit-accredited-ai-testers-fairs-2026/); accreditation not yet held, sold as "AI TAP-method" until lodged **[VERIFY]** wording with AI Verify Foundation |

---

## 7. Design-partner terms (G2 beta, 3–5 clients)

| Term | Rule |
|---|---|
| What is sold | **Phase A at list** (S$25K–85K by band) with a written option on Phase B at list, rather than a discount on a 20-day scope the firm cannot yet staff (review §4.4). Where a discount is needed to close, 40–50% off the Phase A price (net S$15K–45K) |
| In exchange for (all four) | (1) 10–30 leaders on the instrument and the executive-interview roster by day 10; (2) start third-party onboarding for Phase B within 10 working days of charter sign-off (no data is due until it clears); (3) a named reference or approved quote at GA; (4) a measured-outcome follow-up at 6 months on at least one use case |
| Fee credit | Same 90-day credit; credit is calculated on the fee paid |
| Quality | No reduction in verification standard; design partners receive the full evidence pack, the gap register and the blocked-claim list, and independent-reviewer sign-off |
| Benchmark | Anonymised scores enter the evidenced benchmark population (consent clause in engagement letter) |
| Exit | If PLUMB misses Phase A day 12 by more than 10 working days for reasons within its control, partner may terminate and pay only for Phase 1–2 outputs delivered |

---

## 8. Anchors and comparables

| Anchor | Figure | Use in positioning | Source |
|---|---|---|---|
| Singapore AI readiness assessment, >1,000-staff band (the Big-4 / large-firm comparison) | **S$90K–200K**, 4–6 weeks | The number PLUMB is priced against for a >1,000-staff FI: Phase A at S$65K–85K sits at or under the bottom of the band, with a gap register and an independent reviewer the incumbents do not publish. Claim "under the Singapore band", never "5–15× lower" (review §1(b)). To be re-anchored on two real Singapore Big-4 quotes via F21 contacts **[VERIFY]** | [Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide) |
| Internal alternative | ~6 weeks of a 3-person data office at loaded cost | The CFO's real alternative; what it cannot produce is the peer evidence log and independent sign-off | Working estimate; **[VERIFY]** with first design partner |
| Singapore AI readiness assessment bands | S$15K–35K (<100 staff); S$40K–85K (100–1,000); S$90K–200K (1,000+) | Tier 1 bands | [Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide) |
| Singapore 6–12 week strategy work | S$50K–280K | Ceiling PLUMB stays under even with add-ons | [Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide) |
| Singapore retainers | S$5K–12K/month (10 hrs) to S$50K–150K/month | Tier 3 band | [Pertama Partners](https://www.pertamapartners.com/insights/ai-consulting-pricing-guide) |
| UK public-sector AI readiness / strategy awards | £27K–104K | Public-buyer corridor; Australian agencies likely similar | [ConsultingDemand](https://consultingdemand.com/blog/consultant-day-rates-2024/) |
| Boutique productised assessments | US$1.5K–55K; AIDOLS Sprint US$15–25K, Build US$75–150K with refund-if-no-ROI | Shows refund-if-no-ROI and sprint-credit patterns are market-accepted | [AIDOLS](https://aidolsgroup.com/en/blog/category/research-report/ai-consulting-statistics-2026/); [Summit Trails](https://summittrails.com/blog/ai-readiness-assessment-cost/) |
| Deloitte Australia DEWR report | A$440K; partial refund after fabricated citations | The failure case the quality undertaking is written against | [Fortune](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund) |
| Australian federal redistribution | Big 4 down A$800M; non-Big-4 up to A$1.7B | Regional tailwind for mid-tier pricing | [Canberra Times](https://www.canberratimes.com.au/story/9061287/rise-of-mid-tier-consultancies-amid-big-four-contract-cuts/) |

Footnote — UK day-rate derivation (kept for reference, not used as the anchor): a Big-4 three-person, four-week assessment at G-Cloud 14 list day rates of £1,050–2,855 ([ConsultingDemand](https://consultingdemand.com/blog/consultant-day-rates-2024/)) comes to roughly £250K–350K (S$400K+). The red-team reviewer's estimate is that Singapore Big-4 AI-readiness proposals seen by CFOs run S$150K–250K (unsourced; **[VERIFY]**), so the UK figure overstates the local comparison and was withdrawn as the anchor (review §1(b)).

---

## 9. Grant note (Singapore EDGE) — **[VERIFY]**

| Item | What the notes say | Status |
|---|---|---|
| Scheme | EDGE Grant (Enterprise Singapore) in effect from 30 Sep 2026, replacing EDG, MRA and PSG | Secondary source only ([Twenty Eight Eleven](https://twentyeighteleven.sg/blog/edge-grant-ai-projects-singapore)) |
| Support level | SMEs up to 50% for the AI routes; non-SMEs up to 30%; most activities under a S$100K annual cap; ≥ 30% local shareholding; project must not have started or been paid for | **[VERIFY]** with Enterprise Singapore |
| Strategy-only work | No standalone "AI strategy" activity; may fit "Business Strategic Planning", whose application asks for the consultant's SS 680 certification | **[VERIFY]** whether a Tier 1 assessment is claimable at all |
| ISO 42001 projects | Require an SS 680-certified consultant and an accredited certification body | **[VERIFY]**; sources conflict (grant-advisor sites vs official FAQ) |
| Positioning rule | Do not use "EDGE-eligible" in any client-facing material until confirmed in writing by Enterprise Singapore. Until then: "we will support your EDGE application where the activity qualifies" | Standing |

---

## 10. Open items for v0.2

| Item | Action | Owner |
|---|---|---|
| Add-on prices | Replace working values with first three quotes | Founder |
| Phase B option prices | Working values; confirm against delivered cost of D1–D11 handling and onboarding effort on the first design partner | Founder |
| Singapore Big-4 anchor | Obtain two real Singapore Big-4 AI-readiness quotes via F21 contacts; replace the Pertama band with them in §8 | Founder |
| Tier 2 repositioning | Measurement-design-first (base fee builds baseline and counterfactual; savings share switches on after); bar holdouts on customer-facing T3+ use cases (review §1(c), §2.5, rank 9) — not yet applied in §4 | Product + counsel |
| EDGE eligibility and SS 680 | Written confirmation from Enterprise Singapore | Founder |
| Tier 2 performance-fee cap and savings-window length | Test with first design partner; counsel review of structure B | Founder + counsel |
| Delivered cost per engagement | Log at G1 to confirm the ≤ 35% margin test at the 40–85K band | Founder |
| Public pricing page | Publish at GA only (GA plan section 6) | Founder |
