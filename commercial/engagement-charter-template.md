# Engagement Charter Template (Phase 0 output)

**Status: v0.1 draft**
**Owner:** Engagement lead
**Purpose:** The single document produced by Phase 0 (days 1–2) that fixes scope, peer-set protocol, data requests, interviewees, the storyline hypothesis, QA ownership, AI-use disclosure and the 20-working-day timeline. It is the first artefact in the engagement file and the document the client signs before Phase 1 starts. Bracketed fields are filled per engagement; nothing bracketed may be left blank at sign-off.
**Related:** `engagement-letter-clauses.md` (the contract this charter sits under), `conflict-check-procedure.md` (must be complete before this charter is issued), `compliance/evidence-pack-templates.md` §12 (disclosure wording).

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Engagement lead | Initial template from Phase 0 definition in the engagement-framework report |

---

## 0. Charter control block

| Field | Entry |
|---|---|
| Engagement ID | [PLUMB-YYYY-NNN] |
| Charter version | [v0.x] — charter is re-versioned on any change to sections 2, 3, 6 or 10 |
| Client legal entity | [Name, UEN / registration no., registered address] |
| Client sponsor | [Name, role] |
| Client day-to-day contact | [Name, role, email] |
| PLUMB engagement lead | [Name] |
| PLUMB independent reviewer | [Name] — must not run the research agents on this engagement |
| PLUMB signing partner | [Name] |
| Conflict check | Completed [date], outcome [clear / clear with conditions / declined], reference [CC-ID] |
| Engagement letter | Signed [date], reference [EL-ID] |
| Tier | [Tier 1 fixed fee / design partner] — fee [S$] — size band [<100 / 100–1,000 / >1,000] |
| Charter sign-off | Client sponsor [signature, date]; PLUMB signing partner [signature, date] |

---

## 1. Client identity and segments

| Field | Entry | Evidence class |
|---|---|---|
| Trading name and group structure | [ ] | D (registry extract, annual report) |
| Listed / unlisted; exchange and ticker | [ ] | D |
| Headquarters; operating jurisdictions | [ ] | D |
| Sector and sub-sector (seed codes) | [SSIC / GICS / NAICS codes] | D |
| Staff headcount (for size band) | [ ] | D or S |
| Revenue, last FY, currency | [ ] | D (filed) or client statement (labelled) |
| Business segments in scope | [Segment 1, 2, 3 …] with share of revenue | D or client extract |
| Segments explicitly out of scope | [ ] and reason | |
| Regulatory exposure (initial) | Jurisdictions × sectors; binding instruments today; dated instruments inside 12-month horizon (from `compliance/regulatory-status-map.md`) | |
| Known AI initiatives (client-stated) | [list, status] — treated as self-report until evidenced | I |

---

## 2. Value lenses and outputs in scope

| Value lens | In scope (Y/N) | Client's stated priority (1–3) | Notes |
|---|---|---|---|
| Make money (revenue, pricing, new products) | [ ] | [ ] | |
| Save money (cost, productivity, working capital) | [ ] | [ ] | |
| Avoid risk (compliance, resilience, reputation) | [ ] | [ ] | |

| Output | Standard quantity | Agreed for this engagement |
|---|---|---|
| Two-axis maturity scorecard with peer percentile and leadership-perception variance | 1 | [ ] |
| Right-to-win capabilities with AI-era tag and evidence pack | 3–5 | [ ] |
| Value pools sized in two bands (technical potential; realised to date) | 3–5 | [ ] |
| Domains after screen | 2–5 (two core + one support default) | [ ] |
| Use cases with business case, technique-ladder position and RAI tier | 9–15 | [ ] |
| Compliance sub-dimension score and regulatory-exposure map | 1 | [ ] |
| 10-artefact evidence pack | 1 | [ ] |
| 30/60/90-day plan; 6/12-month roadmap; measurement design | 1 each | [ ] |
| Add-ons contracted | [none / MAS AIRM gap / DTA pack / 42001 readiness / AI TAP-method test] | |

---

## 3. Peer-set protocol (agreed)

| Step | Rule | Agreed for this engagement |
|---|---|---|
| Seed | Client's sector codes plus competitors named by the client sponsor (max 10) | [codes]; [named competitors] |
| Expansion | TNIC-style text similarity on business descriptions; exited peers included | [method/tool] |
| Size filter | 0.3× – 3× client revenue or headcount | [band applied] |
| Core set | 5–12 companies; secondary tier for breadth | [target n core], [target n secondary] |
| Geography | APAC sub-region default; global peers added only where the client competes globally | [ ] |
| Exclusions | Client affiliates; companies subject to a conflict (see conflict check) | [ ] |
| Client veto | Client may object to a peer with a written reason; PLUMB records the objection and decides; the decision log (section 11) records it | |
| Disclosure | Peer-set definition, date and n printed on every benchmark exhibit; benchmark falls back to global with label if n < 15 | Standing |

Peer-set candidates named here are run through the conflict check before Phase 1 starts (`conflict-check-procedure.md` §2).

---

## 4. Client data requests

Target: all items received by **day 5**. Items not received by day 5 move the timeline, not the fee (see `pricing-ladder.md` §3.4). Every item gets a confidence label on receipt.

| # | Data item | Purpose | Format | Owner (client) | Due | Received | Confidence label |
|---|---|---|---|---|---|---|---|
| D1 | P&L by segment, last 3 FY | Driver tree; economic-profit comparison | xlsx | [ ] | Day 5 | [ ] | filed / client extract |
| D2 | KPI extracts (volume, price, cost, cycle time, churn) by segment | Driver tree population; baselines | xlsx / system export | [ ] | Day 5 | [ ] | S |
| D3 | Win/loss and churn records, last 24 months | Right-to-win test; external interview sampling | csv | [ ] | Day 5 | [ ] | S |
| D4 | Customer list for external interviews (won, lost, churned, switched) | 8–12 external interviews | contact list with consent status | [ ] | Day 5 | [ ] | |
| D5 | Org chart, leadership roster, headcount by function | Instrument distribution; talent signals | pdf / HRIS extract | [ ] | Day 3 | [ ] | S |
| D6 | AI/data initiative inventory (any format) | Maturity instrument evidence; use-case screen | any | [ ] | Day 5 | [ ] | D |
| D7 | Existing AI policy, governance papers, board reporting on AI | Governance items (ISO 42001 Annex A, NIST RMF) | pdf | [ ] | Day 5 | [ ] | D |
| D8 | Vendor list for AI/analytics tools; contracts' data terms where available | Third-party and supply-chain sub-dimension | list | [ ] | Day 8 | [ ] | D |
| D9 | Technology landscape summary (data platforms, cloud, integration) | Feasibility scoring | any | [ ] | Day 8 | [ ] | D or I |
| D10 | Prior strategy or consulting reports on AI/digital (last 3 years) | Avoid re-work; hypothesis tree | pdf | [ ] | Day 5 | [ ] | D |
| D11 | Incident log for AI/automation (if any) | Monitoring and incident sub-dimension | any | [ ] | Day 8 | [ ] | S |
| D12 | [engagement-specific] | | | | | | |

Handling: all items land in the engagement's Singapore-region store; no client data enters any LLM route until the vendor's ZDR/retention terms are confirmed in writing for this engagement (`data-processing-addendum-outline.md`).

---

## 5. Interviewee and respondent list

### 5.1 Self-assessment instrument (48 items + value axis)

| Target | Rule | Agreed |
|---|---|---|
| Respondents | 10–30 leaders across functions and levels; must include CEO/CFO/COO-level, function heads for in-scope segments, and the AI/data lead | [n], [names/roles] |
| Distribution | Day 5; close day 9 | |
| Output | Per-item consensus and σ; leadership-perception variance exhibit (QA gate 2) | |

### 5.2 Executive interviews (6–10, "state it / live it" and three-circles guides)

| # | Name | Role | Topics (right-to-win / value pools / maturity evidence) | Scheduled | Done | Transcript verified |
|---|---|---|---|---|---|---|
| E1 | [ ] | CEO | | | | |
| E2 | [ ] | CFO | | | | |
| E3 | [ ] | COO / segment head | | | | |
| E4 | [ ] | CIO / CDO / AI lead | | | | |
| E5 | [ ] | CRO / compliance / risk | | | | |
| E6–E10 | [ ] | | | | | |

### 5.3 External interviews (8–12, win/loss/switch/churn timeline protocol)

| # | Type (won / lost / churned / switched / channel) | Company (anonymised in deck) | Sourced from | Scheduled | Done | Transcript verified |
|---|---|---|---|---|---|---|
| X1–X12 | [ ] | [ ] | D3/D4 | | | |

Rule: every quotation used in a deliverable is string-matched against the recording or transcript; anecdotes are separated from repeated patterns (≥ 3 interviews) before anything affects a score.

---

## 6. Storyline hypothesis tree (placeholder)

Written by the engagement lead **before** any AI synthesis runs (BCG/HBS RCT: outside the frontier, AI users were 19 points less likely to reach the correct recommendation; the human forms the hypothesis first — [Lakhani](https://professorkl.substack.com/p/discovering-ais-jagged-frontier-and)).

| Level | Hypothesis | Confidence (day 2) | What would falsify it | Module / data that tests it |
|---|---|---|---|---|
| Governing thought | [One sentence: where the client stands, why, and what to do] | [L/M/H] | | |
| H1 (why they exist) | [3–5 candidate distinctive capabilities] | | | Right-to-win test; E1–E10; X1–X12 |
| H2 (where to improve) | [candidate value pools by lens] | | | Driver tree; D1–D2; peer KPIs |
| H3 (which use cases) | [candidate domains, two core + one support] | | | Domain screen; catalogue |
| H4 (maturity position) | [expected band and peer percentile] | | | Instrument; outside-in signals |
| H5 (compliance exposure) | [binding and dated instruments that gate H3] | | | Regulatory-status map |

Hypothesis tree is re-versioned at day 8 (after Phase 1) and day 12 (after Phase 2); each version is kept in the engagement file.

---

## 7. Ghost-deck reference

| Item | Entry |
|---|---|
| Ghost deck file | [path / ID], version [v0.1], authored [date] by [engagement lead] |
| Standard | Action titles under 15 words; horizontal-flow test (titles alone read as the argument); source line on every data slide; independent partner review ([Deckary](https://deckary.com/blog/consulting-quality-slides)) |
| Section skeleton | 1 Executive summary · 2 Where you stand (two-axis scorecard, peer percentile, leadership variance) · 3 Why you exist (3–5, AI-era tag) · 4 Where to improve (value pools, driver tree) · 5 What to do (use cases, tiers, business cases) · 6 What it takes (30/60/90, roadmap, measurement design, compliance programme) · Appendix: evidence, source log, AI-use disclosure |
| Rule | AI synthesis may propose slides; it may not change an action title without the engagement lead's recorded decision (section 11) |

---

## 8. QA gate owners

| Gate | When | What | Owner | Sign-off record |
|---|---|---|---|---|
| QA gate 1 (automated) | Continuous in Phase 1; report at day 8 | URL health; claim-to-passage match; two-upstream check on load-bearing numbers; aggregator trace-back; AI-generated-page rejection; bounded tool-call depth; block-not-flag | Engagement lead (operates pipeline) | Pipeline report [ID] |
| QA gate 2 (human + automated) | Day 12 | Leadership-perception variance computed and shown; every interview quote verified against transcript; anecdote vs pattern separation | Engagement lead | Checklist signed |
| QA gate 3 (independent) | Day 16–18 | Horizontal-flow test; so-what test; line-by-line verification of every number and quotation in the executive summary; ≥ 30-claim sample across the deck | **Independent reviewer** (did not run the agents) | Reviewer signature; defect log |
| Partner sign | Day 19 | Signs each finding; accepts residual [VERIFY] items; approves AI-use disclosure | **Signing partner** | Signature on deck and engagement file |

| Role | Name | Confirms independence |
|---|---|---|
| Engagement lead | [ ] | n/a |
| Independent reviewer | [ ] | [Y] — did not operate the pipeline or draft the storyline on this engagement |
| Signing partner | [ ] | [Y] — conflict check cleared |

---

## 9. AI-use disclosure (engagement-level)

The deliverable-level statement in `compliance/evidence-pack-templates.md` §12.1 is attached to every output. The engagement-level disclosure below is agreed at charter and sent with any procurement response.

| Field | Entry |
|---|---|
| Statement | PLUMB intends to use AI tools in delivering this engagement for research and source retrieval, first-draft text, data analysis and summarisation. All outputs will be reviewed and approved by named professionals who remain fully responsible for the work regardless of whether generative AI is used. |
| Models and tools | [Vendor / model / version] via [platform], region [Singapore endpoint], retention [ZDR / 30-day / other] confirmed in writing on [date] — one row per tool |
| Client data in AI routes | [Y/N per data item D1–D12]; personal data [Y/N]; if Y, DPA signed [date] |
| Agent action classes | Searches and reads: autonomous. Draft outputs: notify. Any send, publish or write to a client system: human approval. No AI tool executes actions in client systems. |
| Verification commitment | Citation resolution, quote string-match, two-upstream rule, aggregator trace-back, AI-page rejection, block-not-flag; independent reviewer sample ≥ 30 claims |
| Client AI-use clauses | [Client's own AI-use approval or disclosure clauses, if any, referenced here] **[VERIFY]** against client's procurement terms |
| Acknowledged by client sponsor | [signature, date] |

---

## 10. Timeline (20 working days)

| Day | Phase | Milestone | Client dependency | PLUMB owner |
|---|---|---|---|---|
| 1 | 0 | Kick-off; conflict check confirmed; data requests issued | Sponsor available | Engagement lead |
| 2 | 0 | **Charter signed**; hypothesis tree v0.1; ghost deck v0.1; disclosure acknowledged; 50% invoice | Sponsor signature | Signing partner |
| 2–8 | 1 | Nine research modules run; peer set built; outside-in signals computed | Named competitors (D-seed) | Engagement lead |
| 5 | 1/2 | **Data cut-off** for D1–D12; instrument distributed to respondents | All data items | Client contact |
| 5–12 | 2 | Executive interviews E1–E10; external interviews X1–X12 | Interviewees scheduled by day 10 | Engagement lead |
| 8 | 1 | QA gate 1 report; hypothesis tree v0.2 | | Engagement lead |
| 9 | 2 | Instrument closes | Respondents | Client contact |
| 10–16 | 3 | Synthesis: scorecard, right-to-win, value pools, use cases, tiers, business cases | KPI extracts validated | Engagement lead |
| 12 | 2 | **QA gate 2** signed; hypothesis tree v0.3; interim read-out to sponsor (optional) | | Engagement lead |
| 16–18 | 3 | **QA gate 3** independent review; defect log closed | | Independent reviewer |
| 19 | 4 | Partner sign; AI-use disclosure finalised; evidence pack assembled | | Signing partner |
| 20 | 4 | **Board deck delivered**; roadmap; measurement design; engagement file closed; benchmark DB updated; 50% invoice | Board/ExCo slot | Engagement lead |
| +90 days | — | Fee-credit window closes | | Founder |

Slippage rule: client-side delays past day 5 (data) or day 10 (interviews) extend the timeline day-for-day up to 10 working days; beyond that a change order applies.

---

## 11. Decision log

Every scope, peer-set, hypothesis, action-title and [VERIFY]-acceptance decision is logged here; the log is part of the engagement file (ISQM-style: who accepted what).

| # | Date | Decision | Options considered | Decided by | Client informed (Y/N, date) | Charter version affected |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

---

## 12. Open items for v0.2

| Item | Action |
|---|---|
| Client procurement AI-use clause wording | Obtain actual clause text (APS / DTA ClauseBank; California GenAI special provisions) and add a mapping row to section 9 **[VERIFY]** |
| Instrument distribution tooling | Decide survey platform; confirm Singapore hosting and retention for respondent data |
| Interview consent wording | Counsel to draft; add to section 5 |
