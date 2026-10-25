# Enterprise AI Maturity Instrument v0.2

**Status: v0.2 draft — the 12 scorer ambiguities resolved by decision (§5.6); anchors not yet κ-tested (§7)** | Owner: Methodology | Classification: Firm IP, shareable with clients under engagement terms | Date: 2026-10-25

Purpose: a two-axis, evidence-gated maturity score (capability 0–100 in four bands; value axis reported separately, never merged) with published anchors, published weights, perception-variance output and peer percentile. Designed to be (a) completable by 10–30 leaders as a self-assessment in Phase 2, (b) re-scored by an assessor against an evidence register, and (c) pre-populated outside-in by a research agent in Phase 1.

Design constraints inherited from the research base: leader share in the top band must land at ≈5–10% of the benchmark; the production boundary must sit at the 50 line; self-report must not lift a score above level 3 without evidence; governance items must trace to ISO/IEC 42001 Annex A, NIST AI RMF, MAS AIRG materiality and the OWASP agentic governance ladder.

## What changed for respondents (v0.2)

> **If you are answering this instrument, five things are different from v0.1:**
>
> - **Your own 4 or 5 needs evidence.** Any answer of 4 or 5 is recorded as 3 unless you name or attach the artefact that shows it. This now applies to each person's answer, not only to the group's combined answer.
> - **Your organisation's answer to each question is the middle answer, not the average.** With 10–30 people answering, one or two very high or very low answers no longer pull the result. The average is still shown beside it.
> - **You will see two scores.** Your "self-view" (what everyone answered) and the "evidenced view" (after the evidence rule) are shown side by side, with the list of artefacts that would close the gap.
> - **Interviews count as evidence only when two people agree.** A single conversation is not enough; two separate interviewees must be recorded.
> - **Two agent questions now ask different things.** D3.5 asks about the technical controls on AI agents (their identity, logs, kill switch); D6.6 asks about how agents are governed (policy, who is accountable, which actions need human approval). Answer each on its own terms.
>
> The score bands have exact edges: a score of exactly 25, 50 or 75 belongs to the lower band, so 50.0 is still Emerging and Scaling starts above 50.

---

## 0. Change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1 | 2026-10-25 | Initial draft: 48 capability items, 4 value items, scoring spec, calibration, κ subset | Methodology |
| v0.1.1 | 2026-10-25 | Cap-rule transparency: rule shown to respondents on screen one and in the invitation email; scorecards show self-view and evidenced view side by side (red-team review 2026-10-25, Major / §2.2). Peer percentile only within one population (self vs evidenced, never pooled) and replaced by rank within named peers when n < 15 (Blocker 3 / §2.3) | Product |
| v0.2 | 2026-10-25 | The 12 ambiguities logged by the scorer transcription resolved by decision (§5.6): upper-inclusive band edges on unrounded scores and "Leading (≥76)" corrected to >75; cap rule per response; organisation item score = median of capped responses (mean secondary); proxies stated as 1–4 per item with single-proxy items marked and the D8.1/D8.2 row split; D4.4 follows its Ev≥4 column; mid-rank percentile ties; region optional as a peer filter but required in benchmark rows; V2 edges upper-inclusive; band target shares restated to sum to 100% with the BCG order fixed; V1↔D8.4 kept as the only cross-item dependency; I (≥2) verifiable from evidence rows; D3.5 (technical controls) and D6.6 (governance of agents) re-anchored to remove the overlap. Machine-readable copy: `instrument/instrument-v0.2.yaml` (v0.1 file kept for history). "What changed for respondents" box added | Methodology |
| v0.3 | — | Planned: anchors revised after κ test on ≥10 organisations; weights re-fitted after n≥100 benchmark entries | — |

---

## 1. Structure at a glance

| Element | Spec |
|---|---|
| Capability axis | 8 dimensions × 6 items = 48 items, each 5 anchored levels (1–5) |
| Value axis | 4 items (V1–V4), reported as a profile beside the capability score, never averaged into it |
| Level semantics | L1 absent · L2 ad hoc / pilot · **L3 in production with owner, budget, controls (production boundary)** · L4 scaled, measured, standardised · L5 embedded in decisions/products, externally evidenced or independently assured |
| Evidence classes | **D** document (policy, board paper, assessment report) · **S** system record (logs, dashboards, HRIS/LMS/finance extracts, inventory) · **I** interview (≥2 independent interviewees agree; counts only when verifiable from the evidence rows as ≥2 distinct interview references or an interviewee count ≥2, §5.4) · **O** observation (assessor sees the system, workflow or artefact live) |
| Cap rule | Applied **per response** (v0.2 decision 2): each respondent's self-report above 3 is recorded at 3 unless an artefact of the item's required evidence class is logged against that response (§5.4). **Shown to respondents before they answer:** screen one of the instrument (web form and engagement survey alike) and the invitation email state "a self-report above 3 is recorded at 3 unless an evidence class is logged; levels 4–5 are evidence levels — choose them, then name or attach the artefact" (wording: `commercial/engagement-charter-template.md` §5.1) |
| Organisation item score | **Median** of the respondents' capped responses; the mean is shown beside it as a secondary statistic (v0.2 decision 3, §5.1) |
| Scorecard views | Every scorecard shows the **self-view** (median of raw self-reports, uncapped) and the **evidenced view** (median of capped responses) side by side; the difference is listed per item as the artefacts that would move it. The evidenced view is the score of record |
| Outside-in proxies | 1–4 per item (the 10 single-proxy items are marked † in §3); corroborate only, never lift a score (§5.4) |
| Output | Weighted 0–100 capability score and band (self-view and evidenced view); value-axis profile; per-item σ with flags; peer percentile with n disclosed where the peer set has n ≥ 15 within one population, otherwise rank within named peers (§5.5); evidence coverage % |

Evidence class codes in item tables: the class listed is the **minimum** required to score 4 or 5. Where two are listed (e.g. "D+S"), both are required.

---

## 2. Capability axis: dimensions, weights and justification

| # | Dimension | Weight | Justification (short) |
|---|---|---|---|
| D1 | Strategy & ambition | 10 | Necessary but widely "highly prepared" already (Deloitte: 42% rate strategy highly prepared); IDC: "strategy is outpacing delivery" [S6] |
| D2 | Data foundations | 12 | Bain tracks data unreadiness as the growing roadblock; Accenture DM&G is a core capability [S3] |
| D3 | Technology & platform (incl. LLMOps/agent infra) | 12 | Held below people/process weights deliberately; 2021 review found technology over-weighted at 46% of model attention [S10] |
| D4 | Talent & skills | 10 | Accenture front-runners show 4x talent maturity; part of the "70% people/process" effort share [S3][S1] |
| D5 | Operating model & workflow redesign | 14 | Strongest single discriminator: McKinsey high performers 2.8x as likely to have redesigned workflows (55% vs 20%) [S4] |
| D6 | Governance, risk & compliance | 16 | IDC split governance into its own dimension in 2026; MAS AIRG makes it regulatory for FIs from Oct 2027; only 20% have mature agent governance [S6][S14][S7] |
| D7 | Culture & adoption | 10 | Gartner: BU trust 57% vs 14% between high and low maturity; completes the 70% people/process share with D4+D5 [S5] |
| D8 | Value management | 16 | Outcome-anchored cuts (McKinsey >5% EBIT; PwC top 20%) are the only ones tied to financials; BCG future-built >60% rigorously track value vs 17% of stagnating [S4][S8][S1] |
| | **Total** | **100** | D4+D5+D7 = 34; D6+D8 = 32; D2+D3 = 24; D1 = 10 |

Weights are a priori (set in v0.1, unchanged in v0.2). They are to be re-fitted once the benchmark holds n≥100 scored organisations with an independent outcome measure (value axis V1–V3), following BCG's practice of validating weights statistically [S1].

---

## 3. Capability items

Column key: **Q** = question as asked to a leader (self-assessment wording, answered by picking the level that is true today). **Ev≥4** = evidence class required to score 4 or 5. In the proxy tables, **†** marks an item with a single outside-in proxy (v0.2 decision 4: D1.6, D4.5, D4.6, D5.1, D8.1, D8.2, D8.3, D8.4, D8.5, D8.6); a † item's outside-in pre-score rests on one signal and is labelled so in Phase 1 output.

### D1 Strategy & ambition

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D1.1 | Which statement best describes your organisation's AI ambition? | No written AI ambition; AI appears only in IT plans | AI referenced in corporate strategy without targets or timeline | Approved AI strategy naming priority use cases and a 12-month plan, with a named sponsor | Multi-year (≥3 yr) ambition with quantified financial targets, reviewed by the board at least annually | AI targets disclosed in investor materials or external guidance and linked to executive remuneration | D (board paper / strategy doc) |
| D1.2 | Who is accountable for AI outcomes at the top of the organisation? | No one named | An IT or digital lead by default, no mandate letter | A named executive owner of AI in role ≥6 months with written mandate | Chief AI Officer or equivalent reporting to CEO/COO, with budget authority and a central team | CAIO plus every BU head carrying AI targets in their scorecard | D (org chart + mandate) |
| D1.3 | How is the AI portfolio focused? | No portfolio view exists | >15 unconnected use cases, no prioritisation record | Prioritised use-case list with an owner per item | 2–5 defined domains, each with a sized value pool and domain owner | Portfolio rebalanced at least quarterly on realised value; kill decisions recorded | D (portfolio register) |
| D1.4 | How is AI funded? | No dedicated budget | Funded project-by-project from BU discretionary budgets | Annual AI budget line approved centrally | Multi-year funding with stage gates and documented reallocation between initiatives | AI investment share at or above peer top quartile and disclosed | D+S (budget record) |
| D1.5 | Where does AI sit in your products and services? | Not in any customer offering | Discussed or prototyped, nothing live | At least one AI-enabled feature live in a customer-facing offering | AI features priced, measured and roadmapped across ≥2 product lines | AI capabilities sold as services or embedded in all core decisions (MIT CISR Stage 4 marker) | O (live product) + D |
| D1.6 | How does the AI roadmap connect to financial plans? | No roadmap | Roadmap with no value attached | Roadmap items with owners, dates and a stated expected benefit | Every roadmap item tied to a P&L line on a driver tree | Roadmap reforecast quarterly against realised value with finance sign-off | D (roadmap) + S (finance) |

**D1 outside-in proxies**

| ID | Proxy signals a research agent can gather | Validation source |
|---|---|---|
| D1.1 | Annual report / 10-K AI paragraph scored on the 1–5 Yu et al. rubric (L1 mention → L5 deep integration); investor-day AI targets; earnings-call AI semantic density | [P2] sector corr. 0.76 with Census, 0.87 with Ramp; [P3] AIR Index |
| D1.2 | CAIO/CDO on leadership page or LinkedIn; reporting line stated in announcements; tenure | [P4] future-built 3x as likely to have CAIO, 2x CDO; [P5] 91% of high-maturity orgs have dedicated AI leaders |
| D1.3 | Count of distinct AI initiatives named in press releases over 12 months (scatter vs focus); recurrence of the same 2–5 themes | BCG AI Radar: leaders prioritise ~3.5 use cases vs 6.1 [P10]; no firm-level validation |
| D1.4 | Disclosed AI spend or share of IT budget; capex/opex commentary on AI in results calls | [P4] avg ~5% of IT budget (APAC 5.2%); [P6] leaders invest 2.5x more of revenue |
| D1.5 | AI features in product pages; trademarks and product patents; app-store release notes | [P1] growth via product innovation (trademarks, product patents); [P4] 3.5x patents |
| D1.6 † | Quantified AI-attributed financials in guidance or results (e.g. "5–10% of FY EBIT") | [P2] rubric L4 = "expected financial outcomes"; [P3] |

### D2 Data foundations

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D2.1 | Who owns your critical data? | No named owners | IT owns data by default | Named business data owners for the priority AI domains | Enterprise data-owner register with stewardship SLAs covering all critical data domains | Data-ownership KPIs in executive scorecards and reviewed quarterly | D (register) |
| D2.2 | How is data quality measured? | Not measured | Checked manually when problems arise | Quality rules monitored for datasets feeding production AI | Quality dashboards with thresholds, alerts and a data-incident process | Quality SLAs enforced contractually, including with external data suppliers | S (dashboard / incident log) |
| D2.3 | How accessible is governed data? | Silos; extracts by request | Partial warehouse/lake, no catalogue | Governed catalogue covering priority domains with access workflow | Self-serve access with lineage for >70% of critical datasets | Proprietary "flow" data products generated continuously by operations/products feed models | S (catalogue coverage) |
| D2.4 | How ready is your unstructured content for GenAI? | Not curated | Ad hoc document dumps into a tool | Curated, access-controlled corpus serving ≥1 production retrieval application | Enterprise document governance (classification, retention, access) feeding retrieval for all production GenAI | Usage feedback loops measurably improve corpora (retrieval quality tracked) | S (retrieval eval) |
| D2.5 | Can you trace the provenance of data used by production AI? (ISO 42001 A.7) | No | Manual notes for some models | Lineage and provenance records for data of priority production systems | Automated lineage and provenance records for all production AI (A.7.5) | Lineage used as audit evidence (internal audit or certification) | S (lineage) |
| D2.6 | How are personal data and cross-border transfers controlled for AI? | No AI-specific controls | Policy statement only | DPIAs completed for AI uses of personal data | Per-system residency and transfer register with enforced endpoint allowlists | Independently audited (e.g. ISO 27701 / external review) | D (DPIA) + S (register) |

**D2 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D2.1 | CDO presence; data-governance titles on LinkedIn | [P4] future-built 2x as likely to have a CDO |
| D2.2 | Job postings for data-quality / data-steward roles; data-quality tooling in technographics | [P1] postings method; no quality-specific validation |
| D2.3 | Data-platform technographics (BuiltWith); hyperscaler data-platform case studies naming the firm | No published validation |
| D2.4 | Postings for knowledge-management / retrieval / "RAG" roles; enterprise search vendor case studies | No published validation |
| D2.5 | ISO 42001 or ISO 27001 certification announcements; lineage tooling in technographics | No published validation |
| D2.6 | Privacy certifications (ISO 27701); privacy-notice language on AI; regulator enforcement history | No published validation |

### D3 Technology & platform (incl. LLMOps / agent infrastructure)

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D3.1 | Where does production AI run? | Nowhere; experiments on laptops or consumer SaaS | Team-level cloud accounts, no SLAs | Production AI on managed infrastructure with SLAs and on-call ownership | Shared AI platform (model gateway, vector store, evaluation service) used by ≥3 business units | Platform cost/performance benchmarked; multi-model routing in place | O (platform) + S |
| D3.2 | How mature are your LLM operations? | None | Prompts edited by hand in production | Versioned prompts and models with CI for ≥1 production application | Evaluation suites, regression tests and drift monitoring across all production GenAI | Automated rollback and continuous evaluation with sampled human review | S (eval + deployment logs) |
| D3.3 | Do you reuse AI components? | No | Informal copy of code between teams | Shared catalogue of ≥5 reusable components (connectors, prompts, agents, guardrails) | >50% of new builds reuse catalogued components | Components have owners, SLAs and usage metrics | S (catalogue + usage) |
| D3.4 | How is AI integrated with systems of record? | Not integrated | Copy/paste between tools | ≥1 production AI reads systems of record through governed APIs | AI writes to systems of record under change control and logging | AI embedded in core transaction workflows with event-level audit logs | S (integration logs) |
| D3.5 | What technical controls run on your AI agents (identity, credentials, logging, kill switch)? | No agents, or agents with no technical controls | Agents run on human or shared credentials | Per-agent identity, tool allowlist and action logs for every production agent | Short-lived task-scoped credentials, sandboxed execution, kill switch tested in the last 6 months | Cryptographic agent identity, tamper-evident audit trails and runtime anomaly detection that contains an agent automatically (OWASP GML Level 4 technical controls) | O (kill-switch test) + S (logs) |
| D3.6 | How are AI systems secured against AI-specific threats? | Not considered | Generic infosec only | Threat model and prompt-injection controls documented per input channel for production systems | Red-team before deployment of material systems; per-inference logs retained ≥90 days | Continuous adversarial testing with measured false-positive/negative rates | D (threat model) + S (logs) |

**D3 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D3.1 | Hyperscaler partnership announcements; technographics; postings for ML-platform engineers | [P1] AI-skill share of postings |
| D3.2 | Postings naming LLMOps / evaluation / observability tooling; conference talks by engineers | [P1]; Accenture names LLMOps as a gen-AI essential [S3] |
| D3.3 | Public engineering blogs describing internal platforms; open-source releases | PwC leaders 2.4x reusable catalogued components [S8]; no outside-in validation |
| D3.4 | Vendor case studies naming core-system integration; API marketplace presence | No published validation |
| D3.5 | Postings for agent-platform / agent-identity engineers; vendor announcements on agent deployments naming identity or kill-switch controls | [P8] 20% mature agent governance; [P11] BCG 5% full control set |
| D3.6 | Security certifications; bug-bounty scope including AI; CISO statements on AI security | BCG: 72% report unmanaged AI-security risks [S1]; no outside-in validation |

### D4 Talent & skills

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D4.1 | Do you have an AI talent strategy? | No | Hiring reacts to projects | Documented AI role taxonomy and 12-month hiring plan | Strategic workforce plan with quantified skill gaps, funded, covering role redesign | Plan reforecast annually with redesign outcomes tracked (roles changed, hours redeployed) | D (workforce plan) |
| D4.2 | How deep is your in-house specialist bench? | No in-house specialists | Fully vendor-dependent | In-house team covering data science, ML/LLM engineering and AI product | Bench sized to the portfolio with attrition at or below peer | Externally recognised (publications, patents, open-source, speaking) | S (HRIS) |
| D4.3 | How broad is workforce upskilling? | None | Optional self-paced content | Role-based curriculum completed by >25% of workforce | >50% completed with assessed competence (not just attendance) | Competence requirements by role, refreshed annually and tied to performance | S (LMS) |
| D4.4 | How AI-literate is the top team? | No exposure | One-off briefing | Board and ExCo completed a structured AI programme in the last 24 months | ExCo members use AI tools in their own workflow (observable) and challenge AI proposals on evidence | Board includes AI-competent director(s); AI is a standing board agenda item | I (≥2) + O |
| D4.5 | Who translates business need into AI product? | No one | Analysts informally | Named AI product owner for each production use case | Defined product-owner / translator career path with BU-embedded roles | Product owners carry P&L-linked AI targets | D (role charter) |
| D4.6 | How are AI outcomes incentivised and specialists retained? | Not addressed | Ad hoc retention payments | AI roles placed in compensation bands benchmarked to market | AI outcomes in BU leader incentive plans | Executive long-term incentives linked to AI targets | D (remuneration policy) |

**D4 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D4.1 | AI-skill share of job postings over 24 months; AI title growth on LinkedIn | [P1] postings/resumes predict sales, employment, market value; [P7] WTI LinkedIn data |
| D4.2 | Patents; open-source repos under company org; conference talks; Kaggle/arXiv affiliations | [P4] 3.5x patents; GitHub validation is a known gap |
| D4.3 | Public upskilling commitments ("train X% of staff"); LinkedIn Learning certificate counts | [P4] future-built plan to upskill >50% vs 20%; no outside-in validation |
| D4.4 | Board bios; annual-report governance section on AI oversight; director AI committee seats | No published validation |
| D4.5 † | Postings for "AI product manager" / "analytics translator" | [P1] |
| D4.6 † | Remuneration report / proxy statement mentions of AI metrics in incentive plans | No published validation |

### D5 Operating model & workflow redesign

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D5.1 | Have you redesigned work around AI or layered tools onto existing processes? | Nothing changed | Tools added to unchanged processes | ≥1 end-to-end process redesigned around AI and running in production | Standard redesign method with before/after process maps applied across domains | Processes designed agent-first with human roles explicitly redefined | D (process maps) + O |
| D5.2 | How is AI organised? | No function | Informal community of practice | Central AI function with written mandate over standards, platform and governance | Hub-and-spoke: central enablement plus BU pods with shared funding | BU P&L owners run AI delivery; central function measured as an enabler | D (operating model doc) |
| D5.3 | How is AI delivered? | Waterfall or none | Pilots run as one-off projects | Persistent product teams releasing production AI at least monthly | Cycle time measured and improving; stage gates with explicit kill criteria | Continuous delivery with an experimentation platform | S (release records) |
| D5.4 | How do pilots reach production? | No pilots | Pilots with no defined path | Written gate criteria: owner, baseline, measurement plan, safety boundary | Time-to-production tracked; median ≤12 months | >60% of initiatives started in the last 24 months are in production | S (portfolio tracker) |
| D5.5 | How is human oversight designed into AI workflows? | Not designed | Ad hoc review | Human-in-the-loop points documented per production use case | Approval tiers by reversibility/impact (autonomous / notify / approve) encoded in policy and tooling | Override rates and response times monitored for automation bias | D (tier policy) + S |
| D5.6 | How is change managed for AI-driven process change? | No change effort | Communications only | Named process owner and adoption plan per redesigned workflow | Change budget proportional to the people/process share of effort; adoption KPIs tracked | Continuous reinvention cadence with workforce transition plans | D (change plan) + S (KPIs) |

**D5 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D5.1 † | Case studies / results commentary describing "redesigned" or "reinvented" processes vs "assistant deployed" | McKinsey 55% vs 20% redesign [S4]; no outside-in validation |
| D5.2 | Postings naming "AI Centre of Excellence"; org announcements | [P5] ~60% of high-maturity centralise strategy, governance, data, infra |
| D5.3 | Engineering blog release cadence; app release notes frequency | No published validation |
| D5.4 | Ratio of "pilot" to "deployed/production" language in press over 24 months; 10-K rubric L3 vs L4 | [P2] rubric distinguishes Pilot (3) from Production (4); [P4] 62% vs 12% deployed |
| D5.5 | Public statements on human oversight; regulator disclosures (ATRS-style records where applicable) | No published validation |
| D5.6 | Restructuring / role-redesign announcements; workforce-transition programmes in annual report | No published validation |

### D6 Governance, risk & compliance

Item bank mapping: ISO/IEC 42001 clauses and Annex A categories [S15][S16]; NIST AI RMF functions Govern / Map / Measure / Manage [S9]; MAS AIRG materiality (Impact / Complexity / Reliance) [S14][S17]; OWASP Agentic Governance Maturity Levels 0–4 [S13].

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D6.1 | Do you run an AI management system? (ISO 42001 cl. 5.2, A.2, A.3; NIST Govern) | No AI policy | Draft principles, not approved | Approved AI policy and acceptable-use policy; roles and concern-reporting route defined and communicated | Full AIMS: risk methodology, Statement of Applicability, internal audit and management review completed in the last 12 months | Third-party ISO/IEC 42001 certification or equivalent independent assurance | D (policy, SoA, audit report) |
| D6.2 | Do you keep an AI inventory with risk tiering? (ISO A.4, A.10; MAS inventory fields; NIST Map) | No inventory | Partial spreadsheet | Inventory of all production AI with purpose, approved scope, model type, data, dependencies, materiality rating, validation status, owner; third-party AI included | Materiality (impact / complexity / reliance) drives control depth; re-rated on change; rule-based overrides for employment, credit, biometrics | Inventory is a system of record integrated with CMDB; control function signs off ratings | S (inventory extract) |
| D6.3 | Are impact and risk assessments performed before deployment? (ISO cl. 6.1.4, A.5; NIST Map) | Never | Ad hoc for some systems | Impact assessment with individual and societal sections completed for every material system pre-deployment | Documented methodology with triggers and thresholds; reassessment on scope or model change | Assessments published or independently reviewed | D (assessments) |
| D6.4 | How are AI systems tested and validated? (NIST Measure; MAS validation; AI Verify) | Not tested beyond dev | Developer testing only | Pre-deployment tests for accuracy, fairness, robustness and hallucination documented for material systems | Independent validation for high-materiality systems, periodic re-validation, red-team before release | External assurance or testing (e.g. AI Verify process checks, third-party audit) | D (test reports) + S |
| D6.5 | How are production AI systems monitored and incidents handled? (NIST Manage; ISO A.6.2.8, A.8) | Not monitored | Ad hoc checks | Production monitoring with retained logs; internal AI incident reporting channel exists and is used | KPI/KRI review cadence per system owner; incident runbooks; change control with re-vetting triggers | Incident metrics reported to the board; external adverse-impact reporting route; incident communication plan tested | S (logs, incident register) |
| D6.6 | How are your AI agents governed (policy, accountability, approval of agent actions)? (OWASP GML 0–4 governance controls; MAS agentic expectations) | Agents in use are unknown to governance (GML 0) | Agents piloted under the general AI policy only; no agent-specific approval (GML 1) | Published agent policy; named accountable executive per production agent; agent register (AI-BOM) recording purpose, owner and permitted actions; mandatory human approval for high-impact actions (GML 2) | Approval tiers by action reversibility and impact (autonomous / notify / approve) set per agent in machine-readable policy; register re-reviewed on change; agent incidents run through the AI incident process (GML 3) | Agent governance independently assured; tiers re-set on observed agent behaviour with control-function sign-off; agent risk reported to the board (GML 4) | D (agent policy, register) + S (approval records) |

**D6 coverage check**

| Framework | Covered by |
|---|---|
| ISO 42001 Annex A: A.2 policies, A.3 roles | D6.1 |
| A.4 resources, A.10 supplier/customer | D6.2 |
| A.5 impact assessment | D6.3 |
| A.6 lifecycle (V&V, logging), A.8 information/incident | D6.4, D6.5 |
| A.7 data | D2.5, D2.6 |
| A.9 responsible use | D5.5, D7.6 |
| NIST AI RMF Govern / Map / Measure / Manage | D6.1 / D6.2–D6.3 / D6.4 / D6.5 |
| MAS AIRG materiality, inventory, independent validation, agentic | D6.2 / D6.2 / D6.4 / D6.6 |
| OWASP Agentic GML 0–4 | Split without overlap (v0.2 decision 12): D6.6 governance controls (policy, accountability, approval tiers, register); D3.5 technical controls (identity, credentials, logging, sandbox, kill switch) |

**D6 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D6.1 | ISO 42001 certification announcement (accredited body named); published RAI principles page; RAI mentioned in annual report risk section | BCG/MIT SMR: 25% fully mature RAI frameworks [S18]; cert registries not validated as maturity proxy |
| D6.2 | Regulator disclosures (ATRS-style records, AIA publications); postings for AI risk / model risk roles | No published validation |
| D6.3 | Published impact assessments; DPIA references in privacy notices | No published validation |
| D6.4 | AI Verify / third-party testing participation; bias-audit publications (e.g. NYC LL144) | No published validation |
| D6.5 | Entries in public AI incident databases; regulator actions; incident disclosure in annual report | Deloitte APAC: 2 in 5 lack an incident reporting mechanism [S7] |
| D6.6 | Public statements on agent deployments with/without governance language (policy, accountable owner, human approval); postings for agent governance roles | [P8] 20% mature agent governance; [P11] BCG 5% full control set |

### D7 Culture & adoption

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D7.1 | What share of employees use sanctioned AI tools? | <10% monthly | 10–25% monthly | >25% monthly on sanctioned tools with telemetry | >50% weekly active | >75% weekly active; usage part of role expectations | S (usage telemetry) |
| D7.2 | How ready are business units to use AI? | BUs resist or ignore | Isolated champions | ≥50% of BUs sponsor an AI use case in production | BU leaders request and co-fund AI initiatives | BU leaders are accountable for AI outcomes in their scorecards | I (≥2 BU leaders) + D |
| D7.3 | How does the organisation experiment and learn? | No experimentation | Ad hoc trials, learnings not captured | Defined experiment process with documented learnings, including failures | Failed experiments reviewed without penalty; stop decisions recorded | Experiment velocity and learning metrics tracked and reported | D (experiment log) + I |
| D7.4 | How is unsanctioned ("shadow") AI handled? | Unknown | Banned, not monitored | Sanctioned tools offered, policy published, discovery in place | Shadow use measured and converted to sanctioned tools | Near-zero shadow use with continuous discovery | S (discovery tooling) |
| D7.5 | How does user feedback shape AI systems? | No channel | Complaints only | Feedback routed to product teams with response SLAs | User feedback and model performance jointly reviewed on a cadence | Human and AI learning loops both measured (MIT SMR "augmented learner" pattern) | S (feedback records) |
| D7.6 | How transparent is AI use toward employees and customers? | No communication | One-way announcements | Employees informed when AI affects their work; AI interaction disclosed to customers | Employee AI-trust pulse measured and acted on | Co-design with workforce; published commitments with reporting | S (pulse) + D |

**D7 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D7.1 | Employee review sites mentioning AI tools; vendor seat-count announcements | [P7] WTI uses M365 telemetry; no firm-level public validation |
| D7.2 | BU-level AI announcements (not just corporate); regional/business-line case studies | [P5] 57% vs 14% BU trust |
| D7.3 | Hackathon / innovation programme publicity; engineering blog post-mortems | No published validation |
| D7.4 | Public policy on tool use; news of bans or sanctioned rollouts | No published validation |
| D7.5 | App-store review response rates; public product feedback channels | No published validation |
| D7.6 | Published AI transparency statements; union/works-council agreements on AI | No published validation |

### D8 Value management

| ID | Q (leader wording) | L1 | L2 | L3 | L4 | L5 | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D8.1 | Do you baseline before deploying AI? | Never | Anecdotal "before" descriptions | System-measured baseline captured before every production deployment | Baselines reviewed and signed by finance | Baselines reused for reforecast and post-implementation review | S (baseline records) |
| D8.2 | Do you use control groups or counterfactuals? | No | Before/after comparison only | Control group or holdout for ≥1 material use case | Standard for all material use cases where feasible; exceptions documented | Experimentation platform with causal methods; results audited | D (method) + S (results) |
| D8.3 | How is AI value tracked? | Not tracked | Ad hoc claims | Quarterly tracking per production use case with a named owner | Value ledger reconciled with finance in three buckets: revenue, cost, risk avoided | Value reported in board pack or externally with audit trail | S (ledger) |
| D8.4 | How is value attributed to AI vs other drivers? | No rule | Claimed by project teams | Documented attribution rule separating AI from other drivers | Finance-approved methodology including haircuts and double-count checks | Independently reviewed (internal audit or external) | D (methodology) |
| D8.5 | Do you stop initiatives on evidence? | Nothing has ever been stopped | Informal | Stop conditions defined per use case at approval | ≥1 initiative stopped on evidence in the last 12 months with funds reallocated | Portfolio managed on realised return with regular pruning | D (decision records) |
| D8.6 | Do you know the full cost of running AI? | Unknown | Build cost only | 3-year TCO including run and token costs per use case | Unit economics monitored (cost per transaction or outcome) | Cost per outcome benchmarked and optimised (e.g. model routing) | S (cost dashboard) |

**D8 outside-in proxies**

| ID | Proxy signals | Validation source |
|---|---|---|
| D8.1 † | Investor-day or results language on "measured against baseline" | DBS example [P12]; no cross-firm validation |
| D8.2 † | Investor-day or results language on "control groups" (e.g. DBS reports value in three buckets against control groups) | DBS example [P12]; no cross-firm validation |
| D8.3 † | Quantified AI value in results or investor day (e.g. S$ value, % EBIT) | [P2] rubric L4/L5; [P3] AIR Index |
| D8.4 † | Audit-committee or CFO statements on AI benefit measurement | No published validation |
| D8.5 † | Announced discontinuations or portfolio pruning | No published validation |
| D8.6 † | Commentary on AI run costs / token spend in results calls | [P2] notes AI bought as opex; no capex signal |

---

## 4. Value axis (reported separately; never merged into the capability score)

| ID | Question | Scale | Evidence required | Calibration anchor |
|---|---|---|---|---|
| V1 | What share of EBIT in the last fiscal year is attributable to AI, under a finance-approved attribution rule? | Band A: none / not measured · Band B: >0 and <5% · Band C: ≥5% | S (finance extract) + D (attribution rule, with the D8.4 organisation item score ≥3 in the evidenced view); otherwise recorded as Band A "not evidenced". This is the instrument's only cross-item dependency (v0.2 decision 10) | McKinsey high performers = >5% EBIT + significant value ≈ 6% of respondents; 39% attribute any EBIT impact, most <5% [S4] |
| V2 | Of AI initiatives started in the last 24 months, what share is in production (live, owned, with users)? | <12% · 12–39% · 40–61% · ≥62%, on the unrounded share p with upper-inclusive edges (v0.2 decision 8): p < 12 · 12 ≤ p ≤ 39 · 39 < p ≤ 61 · p > 61 | S (portfolio tracker); self-report capped at the 12–39% band | BCG future-built 62% deployed vs 12% laggards [S1]; Gartner high-maturity 45% of projects ≥3 yrs in production [S5] |
| V3 | How rigorous is value tracking? | 1 none · 2 anecdotal · 3 self-reported metric per use case · 4 system-measured baseline, finance-reconciled · 5 control groups + finance sign-off + audit trail | S (ledger) for ≥4 | BCG >60% of future-built rigorously track vs 17% of stagnating [S1]; PwC leaders 80% more likely to systematically track [S8]; DBS three-bucket, control-group model [P12] |
| V4 | What is your agent control maturity? | OWASP Governance Maturity Level 0–4 on the full GML ladder (governance and technical controls together; D6.6 and D3.5 each score one half of it as capability items, V4 records the whole as an outcome and is assessed on its own evidence, with no scoring dependency on either item) | O (kill-switch test) + S (logs) for ≥3 | Deloitte: 20% mature agent governance [S7]; BCG: 5% have the full control set for agents with decision authority [P11] |

Output format: a four-cell profile (e.g. "V1 B · V2 40–61% · V3 4 · V4 2") displayed beside the capability band. A **value gap flag** is raised when capability band is Scaling or Leading but V1 = Band A or V3 ≤ 2.

---

## 5. Scoring specification

### 5.1 Item to dimension to total

| Step | Rule |
|---|---|
| Response score | Integer 1–5 per respondent per item, after the cap rule (§5.4), which is applied to each response before any aggregation (v0.2 decision 2) |
| Organisation item score | **Median** of the capped responses for the item (with an even number of responses, the midpoint of the two middle values, so half-levels such as 2.5 occur); the **mean** of the capped responses is reported beside it as a secondary statistic and never used in the total (v0.2 decision 3). Assessor adjustment (§5.4 "Down-scoring") applies to the organisation item score |
| Dimension mean | m_d = mean of the organisation item scores of scored items in dimension d; requires ≥4 of 6 items scored (an item is scored when it has at least one response), otherwise dimension marked "not scored" and its weight renormalised across scored dimensions, with a flag on the output |
| Dimension score (0–100) | s_d = (m_d − 1) / 4 × 100 |
| Capability score | C = Σ w_d × s_d / 100, using weights in §2 |
| Self-view | The same steps run on the **raw** (uncapped) responses give the self-view score; the evidenced view above is the score of record (§1 "Scorecard views") |
| Rounding | Report C to one decimal; band assigned on the unrounded value |

Worked check: all 48 items at level 3 → every organisation item score = 3 → every s_d = 50 → C = 50.0 → top of Emerging. Crossing into Scaling requires a weighted dimension mean above level 3, i.e. above the production boundary. Leading (C > 75) requires a weighted dimension mean above 4.0; all items at exactly 4 give C = 75.0, the top of Scaling.

Why the median (decision 3): an organisation item score is formed from 10–30 respondents, and in groups that small one to three enthusiasts (or sceptics) at the extremes move a mean by up to half a level on a five-level scale. The median moves only when the middle of the leadership team moves. The mean stays visible because a mean well above the median is itself a finding (a minority claiming more than the team will support), and σ (§5.3) is still computed on raw levels.

### 5.2 Bands

Bands are closed on the upper edge and applied to the **unrounded** C (v0.2 decision 1).

| Band | Score | Meaning | Target share of benchmark |
|---|---|---|---|
| Stagnating | 0 ≤ C ≤ 25 | Mostly absent or ad hoc; no production AI with an owner | 15% |
| Emerging | 25 < C ≤ 50 | Pilots and first production systems; controls and value tracking partial | 45% |
| Scaling | 50 < C ≤ 75 | Majority of items above the production boundary; standardised methods and measurement | 32.5% (window 30–35%) |
| Leading | 75 < C ≤ 100 | Embedded in decisions and products, independently evidenced | **7.5% (window 5–10%)** |

The **production boundary is the 50 line**: a score of exactly 50.0 is Emerging, and any score above it is Scaling or Leading. Upper-inclusive edges are used because the worked check (§5.1) places 50.0 at the top of Emerging, and because the band is assigned on the unrounded score, so an integer-edged table ("26–50") would leave 25–26, 50–51 and 75–76 unassigned. A reported score of "75.0" can therefore sit in Leading only when the unrounded value is above 75 (e.g. 75.04); the scorecard prints the band beside the rounded score so the two are never read apart.

Target shares sum to 100% (15 + 45 + 32.5 + 7.5; v0.2 decision 9). The Leading window is 5–10% and Scaling takes the complement of Leading within the top 40%, so the two windows move together. Shares follow the BCG 2025 distribution, which in this table's order (Stagnating → Leading) is 14 / 46 / 35 / 5, and the IDC 2026 finding that 61.3% sit in the bottom two stages [S1][S6]. Thresholds are fixed for v0.2; after n≥100 benchmark entries, thresholds (not anchors) are adjusted so Leading = 5–10%.

### 5.3 Leadership-perception variance

| Output | Rule |
|---|---|
| Respondents | 10–30 leaders per organisation; minimum 5 for variance statistics (below 5, report min–max range instead of σ) |
| Per-item σ | Population standard deviation of raw self-reported levels across respondents, computed **before** the cap rule |
| Item flag | σ > 1.0 → "perception divergence" flag; item listed in the deliverable with the respondent roles at each extreme (roles, not names) |
| Dimension alignment index | Share of items in the dimension flagged; ≥50% flagged → dimension marked "leadership not aligned" |
| ExCo vs operating gap | mean(ExCo respondents) − mean(operating-manager respondents) per dimension; |gap| > 0.75 flagged, sign reported (ExCo-optimistic or ExCo-pessimistic) |
| Rationale | IDC: only ~1 in 6 self-identified "thrivers" scored Managed/Optimized on re-scoring [S6]; Strategy&: only 20% of executives agree on which capabilities are key [S19] |

### 5.4 Evidence cap rule

| Rule | Detail |
|---|---|
| Cap | Applied **per response** (v0.2 decision 2): any respondent's self-report of 4 or 5 on an item is **recorded at 3** unless an artefact of the item's Ev≥4 class is logged against that response in the evidence register with an artefact ID, date and reviewer. Where two classes are listed (e.g. "D+S"), both must be logged. The organisation item score is then the median of the recorded responses (§5.1). The rule is disclosed to respondents on screen one and in the invitation email (§1), and both views are reported (§1 "Scorecard views") |
| Why per response | The free web form has no consensus to cap, so per-response capping is the only rule both channels can apply identically; capping a consensus would also let a few evidenced 5s carry unevidenced 4s and 5s from the rest of the team into the score. One logged artefact may be linked to every response it supports |
| Lift | With the required artefact logged, the response is scored at the level the artefact supports (which may be below the self-report) |
| Interview evidence | Where Ev≥4 is D or S, interview agreement alone lifts to at most 3. Where Ev≥4 includes I (D4.4, D7.2, D7.3), the I class counts only when two independent interviewees are **verifiable from the evidence rows** (v0.2 decision 11): either ≥2 distinct interview references are logged on the item's rows, or a row's `interviewees` count is ≥2 (one reference covering a joint record of two interviews). A single interview reference does not lift and does not count toward evidence coverage |
| Outside-in signals | Corroborate only. A proxy can be cited to **challenge** a self-report downward or to pre-populate a draft score, never to lift above 3 |
| Down-scoring | Assessor may score below self-report at any level with a written reason; the respondent median and assessor score are both retained |
| Evidence coverage | Deliverable reports % of items with qualifying evidence logged; engagements below 60% coverage report the capability score as "self-report-dominant" |

### 5.5 Peer percentile

| Output | Rule |
|---|---|
| Peer set | Industry × size band, with region (APAC sub-region) as an **optional** third filter; built by the documented peer-set funnel used in Phase 1. Region is a **required field in every benchmark row** (v0.2 decision 7) so that the filter is always available, even where it is not applied |
| Minimum n | n ≥ 15 for a peer percentile; otherwise report the **rank within the named peers** with each peer's value shown, labelled "global, peer n insufficient", and no percentile |
| Populations | Tier-0 self-scored entries (capped ≤ 3, `population = self`) and evidence-gated engagement entries (`population = evidenced`) are different populations and are never pooled into one percentile (`instrument/README.md`) |
| Percentile | Mid-rank percentile of C within the set (v0.2 decision 6): 100 × (number below + 0.5 × number equal) / n, so tied organisations share one value and a set of identical scores places everyone at the 50th percentile; also reported per dimension and for V2/V3 |
| Disclosure | n, peer-set definition date and the share of peer entries that are evidence-gated vs self-scored only (free instrument entries) are printed on the scorecard |

### 5.6 Decisions resolved in v0.2

Each of the 12 ambiguities logged by the scorer transcription (appendix) is resolved below. The decision is binding on the markdown, `instrument/instrument-v0.2.yaml` and `instrument/plumbscore` together.

| # | Topic | Decision | Rationale (one line) | Where |
|---|---|---|---|---|
| 1 | Band edges | Upper-inclusive closed intervals on the unrounded score: Stagnating ≤25 · Emerging >25–≤50 · Scaling >50–≤75 · Leading >75; "Leading (≥76)" corrected to >75 | Matches the worked check (50.0 = top of Emerging) and leaves no score unassigned | §5.1, §5.2 |
| 2 | Cap scope | Per response, before aggregation | The web form has no consensus to cap; one rule for both channels, and the stricter one | §1, §5.4 |
| 3 | Organisation item score | Median of capped responses; mean shown as secondary | Robust to a few enthusiasts or sceptics in a group of 10–30; the mean–median gap remains visible | §5.1 |
| 4 | Proxy count | Kept as written; §1 now says 1–4 per item; the 10 single-proxy items are marked †; the shared D8.1/D8.2 row split into two | States what exists rather than promising proxies no source yet supports | §1, §3 |
| 5 | D4.4 evidence | Follow the Ev≥4 column, I (≥2) + O; §7 text corrected | The anchor's L4 ("observable" tool use) needs observation, not interviews alone | §3, §7 |
| 6 | Percentile ties | Mid-rank: 100 × (below + 0.5 × equal) / n | Tied organisations get one value and the statistic is symmetric | §5.5 |
| 7 | Region | Optional peer filter; required field in every benchmark row | Most SG/APAC peer sets fall below n = 15 with region applied, but the field must exist to apply it later | §5.5 |
| 8 | V2 edges | Upper-inclusive on the unrounded share: p < 12 · 12 ≤ p ≤ 39 · 39 < p ≤ 61 · p > 61 | Same convention as the capability bands; band codes and labels unchanged | §4 |
| 9 | Band target shares | 15 / 45 / 32.5 / 7.5 = 100%; BCG reference restated in table order as 14 / 46 / 35 / 5 | Shares must sum to 100% and be read in the same order as the bands | §5.2 |
| 10 | V1 ↔ D8.4 | Kept: V1 counts as evidenced only if the D8.4 organisation item score (evidenced view) is ≥3; documented as the instrument's only cross-item dependency | An EBIT share without a documented attribution rule is not evidence of value | §4 |
| 11 | I (≥2) | Two interview references (or an `interviewees` count ≥2) must be visible in the evidence rows before the I class counts | Makes the "two independent interviewees" rule checkable rather than an attestation | §1, §5.4 |
| 12 | D3.5 vs D6.6 | Both kept, not merged. D6.6 scores governance of agents (policy, accountable executive, register, approval tiers); D3.5 scores technical controls (identity, credentials, logging, sandbox, kill switch). Anchors rewritten so no control appears in both | Each half of the OWASP ladder is scored once, so agent controls are no longer double-counted | §3 (D3.5, D6.6), D6 coverage check, §4 V4 |

---

## 6. Calibration references

Leader-share anchors for the Leading band (target 5–10%):

| Source | Leader definition | Share | Year / n | URL |
|---|---|---|---|---|
| BCG Widening AI Value Gap | Future-built (>75 on 0–100) | 5% | 2025 / 1,250 | https://media-publications.bcg.com/The-Widening-AI-Value-Gap-Sept-2025.pdf |
| Accenture Front-runners | Reinvention-ready and scaled multiple strategic bets | 8% | 2025 (2024 fieldwork) / 2,000 | https://www.accenture.com/content/dam/accenture/final/accenture-com/document-3/Accenture-Front-Runners-Guide-Scaling-AI-2025-POV.pdf |
| MIT CISR | Stage 4 "AI future-ready" | 7% | 2024–25 / 721 (2022 survey) | https://mitsloan.mit.edu/ideas-made-to-matter/whats-your-companys-ai-maturity-level |
| McKinsey State of AI | >5% EBIT from AI + significant value | ~6% | 2025 / 1,993 | https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/the-state-of-ai-in-2025-vf.pdf |
| IDC MaturityScape | Optimized (stage 5) · top two stages | 3.1% · 12.8% | 2026 / 1,900 | https://www.idc.com/resource-center/blog/ambition-is-everywhere-maturity-is-rare-inside-idcs-2026-ai-maturityscape-benchmark/ |

Secondary calibration points: Gartner high-maturity organisations average 4.2–4.5 on a 1–5 scale, low-maturity 1.6–2.2 [S5]; IDC global mean 2.43 on 1–5 [S6]; PwC leaders = top 20% by AI-attributable financial performance, capturing 74% of returns [S8]. Any configuration of this instrument that places >15% of the benchmark in Leading is out of line with every published source and must be re-calibrated.

---

## 7. Inter-rater reliability test subset (κ)

| Parameter | Spec |
|---|---|
| Items | 20 (below), chosen to cover every dimension and all four evidence classes, weighted toward items most dependent on judgement |
| Design | Two assessors score independently from the same evidence pack for ≥10 organisations (≥200 paired ratings) |
| Statistic | Quadratic-weighted Cohen's κ per item (ordinal scale); plus exact-agreement % |
| Thresholds | κw ≥ 0.70 accept (human-level agreement benchmark used in the coding-reliability literature, [S20]); 0.50–0.69 rewrite anchors; <0.50 rewrite or drop item |
| Exit criterion for v0.3 | ≥16 of 20 items at κw ≥ 0.70, no item <0.50 (v0.2 resolved scoring ambiguities only; it did not run the κ test) |

| # | Item | Why in subset |
|---|---|---|
| 1 | D1.1 | Distinguishing "strategy" from "ambition with targets" is judgement-heavy |
| 2 | D1.3 | Domain focus vs use-case scatter |
| 3 | D1.5 | Live product boundary (O evidence) |
| 4 | D2.3 | Coverage percentage judgement |
| 5 | D2.5 | Provenance completeness (S evidence) |
| 6 | D3.2 | LLMOps anchors are technical; tests assessor skill variance |
| 7 | D3.5 | Agent infrastructure (O evidence) |
| 8 | D4.1 | "Strategy" vs "plan" judgement |
| 9 | D4.4 | Interview + observation item (I (≥2) + O evidence; the only subset item whose Ev≥4 includes both) |
| 10 | D5.1 | Redesign vs tool insertion — most important discriminator |
| 11 | D5.4 | Pipeline gate criteria |
| 12 | D5.5 | Approval-tier anchors |
| 13 | D6.1 | AIMS completeness |
| 14 | D6.2 | Inventory field completeness |
| 15 | D6.4 | Test vs independent validation boundary |
| 16 | D6.6 | OWASP ladder mapping |
| 17 | D7.2 | Interview-based (I evidence) |
| 18 | D7.3 | Culture judgement |
| 19 | D8.2 | Control-group feasibility judgement |
| 20 | D8.4 | Attribution rule quality |

---

## 8. Source key

Sources cited by code above. All URLs are taken from the firm's research notes; none introduced here.

| Code | Source | URL |
|---|---|---|
| S1 | BCG, The Widening AI Value Gap (Sept 2025) | https://media-publications.bcg.com/The-Widening-AI-Value-Gap-Sept-2025.pdf |
| S2 | BCG press release, 30 Sep 2025 | https://www.bcg.com/press/30september2025-ai-leaders-outpace-laggards-revenue-growth-cost-savings |
| S3 | Accenture, Front-runners' Guide to Scaling AI (2025) | https://www.accenture.com/content/dam/accenture/final/accenture-com/document-3/Accenture-Front-Runners-Guide-Scaling-AI-2025-POV.pdf |
| S4 | McKinsey, State of AI 2025 | https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/the-state-of-ai-in-2025-vf.pdf |
| S5 | Gartner press release, 30 Jun 2025 | https://www.gartner.com/en/newsroom/press-releases/2025-06-30-gartner-survey-finds-forty-five-percent-of-organizations-with-high-artificial-intelligence-maturity-keep-artificial-intelligence-projects-operational-for-at-least-three-years |
| S6 | IDC, 2026 AI MaturityScape Benchmark blog | https://www.idc.com/resource-center/blog/ambition-is-everywhere-maturity-is-rare-inside-idcs-2026-ai-maturityscape-benchmark/ |
| S7 | Deloitte, State of AI in the Enterprise 2026; Deloitte APAC "AI at a crossroads" | https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html ; https://www.deloitte.com/cn/en/about/press-room/apac-trustworthy-ai-report.html |
| S8 | PwC, AI Performance Study 2026 | https://www.pwc.nl/en/insights-and-publications/themes/digitalization/want-returns-from-ai-accelerate-your-growth.html |
| S9 | NIST AI RMF / ISO 42001 comparison (Balanced Security) | https://blog.balancedsec.com/p/nist-ai-rmf-or-iso-42001 |
| S10 | Sadiq et al., systematic review of AI maturity models (PeerJ CS 2021) | https://pmc.ncbi.nlm.nih.gov/articles/PMC8409328/ |
| S11 | MIT Sloan, MIT CISR Enterprise AI Maturity Model | https://mitsloan.mit.edu/ideas-made-to-matter/whats-your-companys-ai-maturity-level |
| S12 | MIT CISR Talking Points | https://cisr.mit.edu/publication/TalkingPoints_ChallengesMaturingEntAI |
| S13 | CSA research note on OWASP Agentic AI Governance Maturity Model v2 | https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-agentic-ai-governance-maturity-v2-20/ |
| S14 | MAS consultation paper, Guidelines on AI Risk Management (Nov 2025) | https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/bd/2025/final_consultation_paper_on_guidelines_on_ai_risk_management_forrelease.pdf |
| S15 | GAICC, ISO 42001 Annex A controls and evidence | https://gaicc.org/blog/iso-42001-annex-a-controls/ |
| S16 | Advisera, ISO 42001 mandatory documents | https://advisera.com/articles/iso-42001-mandatory-documents/ |
| S17 | MAS final AIRG commentary (secondary) | https://lukesoon.substack.com/p/mas-finalises-ai-risk-guidelines |
| S18 | BCG, Responsible AI Needs More Than Good Intentions (2026) | https://www.bcg.com/publications/2026/responsible-ai-needs-more-than-good-intentions |
| S19 | Strategy&, The Strategy Crisis | https://www.strategyand.pwc.com/gx/en/unique-solutions/cds/the-strategy-crisis.pdf |
| S20 | JLA 2025, LLM vs human coding agreement (κ ≥ 0.70 benchmark) | https://www.learning-analytics.info/index.php/JLA/article/download/8575/7877 |
| P1 | Babina, Fedyk, He, Hodson (NBER) — AI skill share in postings/resumes | https://conference.nber.org/conf_papers/f160998/f160998.slides.pdf |
| P2 | Yu, Fleming, Hampton, Combemale, Thompson (arXiv 2607.08920) — 10-K AI rubric | https://arxiv.org/pdf/2607.08920 |
| P3 | Federal Reserve FEDS — AIR Index (earnings-call AI density) | https://www.federalreserve.gov/econres/feds/research-in-commotion-measuring-ai-research-and-development-through-conference-call-transcripts.htm |
| P4 | BCG 2025 — CAIO 3x, CDO 2x, patents 3.5x, budget share, 62% vs 12% deployed | https://media-publications.bcg.com/The-Widening-AI-Value-Gap-Sept-2025.pdf |
| P5 | Gartner 2025 — 91% dedicated AI leaders, 57% vs 14% BU trust, ~60% centralise | https://www.gartner.com/en/newsroom/press-releases/2025-06-30-gartner-survey-finds-forty-five-percent-of-organizations-with-high-artificial-intelligence-maturity-keep-artificial-intelligence-projects-operational-for-at-least-three-years |
| P6 | PwC 2026 — leaders invest 2.5x more of revenue in AI | https://www.pwc.nl/en/insights-and-publications/themes/digitalization/want-returns-from-ai-accelerate-your-growth.html |
| P7 | Microsoft Work Trend Index 2025 (LinkedIn + telemetry method) | https://news.microsoft.com/source/asia/2025/05/02/microsoft-work-trend-index-2025-report-reveals-the-frontier-firms-is-born-a-new-organization-blueprint-is-emerging/ |
| P8 | Deloitte 2026 — 20% mature agent governance | https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html |
| P9 | Fed FEDS Note — survey wording and social-desirability bias (caution on self-report) | https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html |
| P10 | BCG AI Radar 2025 — leaders prioritise ~3.5 use cases vs 6.1 | https://web-assets.bcg.com/0b/f6/c2880f9f4472955538567a5bcb6a/ai-radar-2025-slideshow-jan-2025-r.pdf |
| P11 | BCG press release, 30 Sep 2026 — 5% have full agent control set | https://www.bcg.com/press/30september2026-ai-starting-to-pay-off-companies-generate-value |
| P12 | Forrester — DBS three-bucket, control-group value measurement | https://www.forrester.com/blogs/dbs-banks-billion-dollar-ai-dream-realized |

Known limits of the proxy layer (carry into every outside-in pre-score): firm-level precision of outside-in composites is unproven; narrative signals inflate under "AI-washing" so hiring and patent evidence outweigh narrative [P3][P9]; no study validates outside-in composites against a consulting maturity score for the same firms; no inter-rater reliability figures exist for any consulting maturity assessment (which is why §7 exists).

---

## 9. Open items for v0.3

| # | Item |
|---|---|
| 1 | Run the κ test (§7) on ≥10 organisations; revise anchors failing 0.70 (D3.5 and D6.6 anchors were rewritten in v0.2 and are both in the κ subset, so their first κ result is on the v0.2 wording) |
| 2 | Re-fit weights and band thresholds once n≥100 benchmark entries with V1–V3 evidence |
| 3 | Add APAC regulatory overlays as scoring notes (MAS AIRG dates; Korea AI Basic Act; IMDA agentic MGF) without changing anchors |
| 4 | Add a second outside-in proxy to the 10 † items where a validated signal exists; until then they stay marked |
| 5 | Build the free self-scored web version with the cap rule enforced (all self-only entries display ≤3 per item) |

Resolved in v0.2: the former open item "decide whether D3.5 and D6.6 are merged" (decision 12, §5.6).

## Appendix — v0.1 ambiguities raised by the scorer transcription (2026-10-25), resolved in v0.2

Found while transcribing to `instrument/instrument-v0.1.yaml`. Every row is now closed by a decision recorded in §5.6 and applied in the body; this table is kept as the audit trail of what the v0.1 scorer did in the meantime.

| # | Ambiguity | v0.1 scorer interim choice | v0.2 decision (§5.6) |
|---|---|---|---|
| 1 | Band edges are integer-stated (0–25, 26–50 …) but scored on unrounded values; 25–26, 50–51, 75–76 undefined; "Leading (≥76)" conflicts with upper-inclusive reading | Upper-inclusive edges: ≤25 / ≤50 / ≤75 / >75 | Adopted; table and §5.1 text corrected |
| 2 | Cap rule scope: §1 per response vs §5.4 consensus | Per response (stricter) | Per response; §5.4 rewritten |
| 3 | No rule for organisation-level item score across 10–30 respondents | Mean of capped rows | **Changed:** median of capped responses, mean secondary |
| 4 | §1 promises 2–4 proxies per item; D1.6, D4.5, D4.6, D5.1, D8.3–8.6 have one; D8.1/8.2 share a row | As written; add proxies in v0.2 | §1 says 1–4; † marks; D8.1/D8.2 split |
| 5 | §7 calls D4.4 interview-only but Ev≥4 column says I(≥2)+O | Follow the Ev≥4 column | Adopted; §7 text corrected |
| 6 | Percentile rank undefined for ties | Mid-rank | Adopted; formula in §5.5 |
| 7 | §5.5 peer set includes region; benchmark CSV has no region column | Region optional | Optional filter; **required field** in benchmark rows |
| 8 | V2 band edges leave 39–40% and 61–62% undefined | Upper-inclusive | Adopted; intervals in §4 |
| 9 | §5.2 target band shares sum to 95–105%; BCG reference listed in reverse order | Fix text in v0.2 | 15 / 45 / 32.5 / 7.5; BCG 14 / 46 / 35 / 5 |
| 10 | V1 evidence rule depends on D8.4 ≥3 — only cross-item dependency | Implemented as stated | Kept and documented in §4 |
| 11 | "I (≥2 independent interviewees)" not verifiable from one evidence row | Treated as assessor attestation | **Changed:** ≥2 interview refs or `interviewees` ≥2 required |
| 12 | Open item: merge D3.5 and D6.6 (agent controls double-count) | Scored separately | Kept separate; anchors rewritten to remove overlap |
