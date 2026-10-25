# Engagement Charter Template (Phase 0 output)

**Status: v0.2 draft** (red-team review 2026-10-25 applied; see change log)
**Owner:** Engagement lead
**Purpose:** The single document produced by Phase 0 (days 1–2) that fixes scope, peer-set protocol, data requests, interviewees, the storyline hypothesis, QA ownership, AI-use disclosure and the timeline. It is the first artefact in the engagement file and the document the client signs before Phase 1 starts. Bracketed fields are filled per engagement; nothing bracketed may be left blank at sign-off. **The independent reviewer (§0, §8) is a named real person with an agreed per-deck fee, or the charter cannot be issued** (review Blocker 4 / §2.8; founder checklist F4).
**Related:** `engagement-letter-clauses.md` (the contract this charter sits under), `conflict-check-procedure.md` (must be complete before this charter is issued), `compliance/evidence-pack-templates.md` §12 (disclosure wording).

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Engagement lead | Initial template from Phase 0 definition in the engagement-framework report |
| v0.2 | 2026-10-25 | Product | Red-team review 2026-10-25 applied: Tier 1 split into Phase A (public data, instrument, interviews; days 1–12; no confidential extracts; no data-slippage penalty) and Phase B (post-onboarding confidential data; day-5 cut-off applies only there) in §0, §4, §10 (Blocker 4 / §1(a) step 4, §1(d)); cap-rule transparency added to the respondent brief with the invitation-email paragraph, scorecards show self-view and evidenced view side by side (Major / §2.2); "peer percentile" replaced by "rank within named peers (n disclosed)" where evidenced peer n < 15 (Blocker 3); present-tense quality claims in §9 restated as the design target with the measured state (Blocker 5); reviewer named as a precondition to issue (Blocker / §2.8) |

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
| PLUMB independent reviewer | [Name, real person, CV on file] — must not run the research agents on this engagement — per-deck fee [S$] agreed [date]. **Charter cannot be issued with this field blank or "TBD"** |
| PLUMB signing partner | [Name] |
| Conflict check | Completed [date], outcome [clear / clear with conditions / declined], reference [CC-ID]; founder employer-clearance basis recorded in `docs/decisions.md` D7 |
| Engagement letter | Signed [date], reference [EL-ID] |
| Tier | [Tier 1 Phase A / Phase A + Phase B option / design partner] — Phase A fee [S$] — Phase B option [S$] — size band [<100 / 100–1,000 / >1,000] |
| Phase B trigger | Phase B starts on the date the client confirms third-party onboarding has cleared: NDA/DPA signed [date]; information-security questionnaire answered [date]; SOC 2 or equivalent evidence provided [date]; LLM-vendor ZDR confirmed in writing for this engagement [date]. Until then no item in §4 Phase B is requested or received |
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
| Two-axis maturity scorecard (self-view and evidenced view side by side) with rank within the named core peers (n disclosed; a peer *percentile* only where the evidenced peer population has n ≥ 15) and leadership-perception variance | 1 | [ ] |
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
| Disclosure | Peer-set definition, date and n printed on every benchmark exhibit; where the evidenced peer population has n < 15 the exhibit is a rank within the named peers with each peer's value shown, labelled "peer n insufficient"; no percentile is substituted, and the Tier-0 self-scored pool is never used as this client's peer set | Standing |

Peer-set candidates named here are run through the conflict check before Phase 1 starts (`conflict-check-procedure.md` §2).

---

## 4. Client data requests

Phase A requests nothing confidential. **Phase B items are requested only after the Phase B trigger in §0 has cleared**; their day-5 cut-off counts from that date (review Blocker 4). Items not received by Phase B day 5 move the Phase B timeline, not the fee (see `pricing-ladder.md` §3.4). Every item gets a confidence label on receipt.

### 4.1 Phase A — public and non-confidential inputs (days 1–12)

| # | Data item | Purpose | Format | Owner (client) | Due | Received | Confidence label |
|---|---|---|---|---|---|---|---|
| A1 | Named competitors (max 10) and segments in scope | Peer-set seed; scope | list | [ ] | Day 1 | [ ] | client statement |
| A2 | Respondent list for the instrument (roles, no HR data) and executive-interview roster | §5 | names and roles | [ ] | Day 3 | [ ] | |
| A3 | Pointers to public documents PLUMB may have missed (annual reports, investor decks, published AI policy, press) | Outside-in modules; every document is fetched and hashed by PLUMB, never emailed as an attachment where a public URL exists | URLs | [ ] | Day 3 | [ ] | D (public) |
| A4 | Client's own statement of known AI initiatives (status only, no documents) | Hypothesis tree; treated as self-report | list | [ ] | Day 5 | [ ] | I |

No item in 4.1 is confidential; none requires onboarding; none enters an LLM route. Executives may name documents in interviews; the documents themselves are Phase B.

### 4.2 Phase B — confidential extracts (after onboarding clears)

| # | Data item | Purpose | Format | Owner (client) | Due (from Phase B start) | Received | Confidence label |
|---|---|---|---|---|---|---|---|
| D1 | P&L by segment, last 3 FY | Driver tree; economic-profit comparison | xlsx | [ ] | Day 5 | [ ] | filed / client extract |
| D2 | KPI extracts (volume, price, cost, cycle time, churn) by segment | Driver tree population; baselines | xlsx / system export | [ ] | Day 5 | [ ] | S |
| D3 | Win/loss and churn records, last 24 months | Right-to-win test; external interview sampling | csv | [ ] | Day 5 | [ ] | S |
| D4 | Customer list for external interviews (won, lost, churned, switched) | 8–12 external interviews | contact list with consent status | [ ] | Day 5 | [ ] | |
| D5 | Org chart, leadership roster, headcount by function | Talent signals; instrument evidence | pdf / HRIS extract | [ ] | Day 3 | [ ] | S |
| D6 | AI/data initiative inventory (any format) | Maturity instrument evidence; use-case screen | any | [ ] | Day 5 | [ ] | D |
| D7 | Existing AI policy, governance papers, board reporting on AI | Governance items (ISO 42001 Annex A, NIST RMF) | pdf | [ ] | Day 5 | [ ] | D |
| D8 | Vendor list for AI/analytics tools; contracts' data terms where available | Third-party and supply-chain sub-dimension | list | [ ] | Day 5 | [ ] | D |
| D9 | Technology landscape summary (data platforms, cloud, integration) | Feasibility scoring | any | [ ] | Day 5 | [ ] | D or I |
| D10 | Prior strategy or consulting reports on AI/digital (last 3 years) | Avoid re-work; hypothesis tree | pdf | [ ] | Day 5 | [ ] | D |
| D11 | Incident log for AI/automation (if any) | Monitoring and incident sub-dimension | any | [ ] | Day 5 | [ ] | S |
| D12 | [engagement-specific] | | | | | | |

Handling: all Phase B items land in the engagement's Singapore-region store; no client data enters any LLM route until the vendor's ZDR/retention terms are confirmed in writing for this engagement (`data-processing-addendum-outline.md`). Until that confirmation exists, the proposal says so and no client data of any class enters the pipeline (review rank 6).

---

## 5. Interviewee and respondent list

### 5.1 Self-assessment instrument (48 items + value axis)

Respondents: link the invitation email to `methodology/maturity-instrument.md` → "What changed for respondents (v0.2)".

| Target | Rule | Agreed |
|---|---|---|
| Respondents | 10–30 leaders across functions and levels; must include CEO/CFO/COO-level, function heads for in-scope segments, and the AI/data lead | [n], [names/roles] |
| Distribution | Day 5; close day 9 | |
| Cap rule shown before answering | Screen one of the instrument and the invitation email (below) state the rule: **a self-reported level of 4 or 5 is recorded at 3 unless an artefact of the item's evidence class is logged**. Levels 4–5 are evidence levels; respondents choose them, then name or attach the artefact. The cap is a to-do list the client owns, not a verdict PLUMB imposes (review §2.2; `methodology/maturity-instrument.md` §1, §5.4) | Standing |
| Output | Per-item consensus and σ; **scorecard shows the self-view (uncapped) and the evidenced view (capped) side by side** on S08; leadership-perception variance exhibit (QA gate 2) | |

**Invitation-email paragraph (verbatim, sent with every respondent link):**

> You will score 48 items from level 1 to 5. Levels 4 and 5 are evidence levels: if you choose one, please name or attach the document, system record, interview reference or live demonstration that shows it, using the field under the question. Where no artefact is logged, a 4 or 5 is recorded at 3 on the evidenced scorecard. Your scorecard will show both views side by side, your self-view and the evidenced view, so that the gap between them is a list of artefacts to gather, not a mark against you. Your individual answers are not shown to anyone at [Client]; only consensus and spread by role group are reported.

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
| X1–X12 | [ ] | [ ] | D3/D4 (Phase B) or public reviews and agent-channel sources (Phase A) | | | |

Rule: every quotation used in a deliverable is string-matched against the recording or transcript; anecdotes are separated from repeated patterns (≥ 3 interviews) before anything affects a score. External interviews drawn from D3/D4 are Phase B; in Phase A the right-to-win exhibit is "executive-stated, corpus-corroborated" (C1–C5) and C6 is scored from public sources unless interviews are contracted as an add-on (review §2.4).

---

## 6. Storyline hypothesis tree (placeholder)

Written by the engagement lead **before** any AI synthesis runs (BCG/HBS RCT: outside the frontier, AI users were 19 points less likely to reach the correct recommendation; the human forms the hypothesis first — [Lakhani](https://professorkl.substack.com/p/discovering-ais-jagged-frontier-and)).

| Level | Hypothesis | Confidence (day 2) | What would falsify it | Module / data that tests it |
|---|---|---|---|---|
| Governing thought | [One sentence: where the client stands, why, and what to do] | [L/M/H] | | |
| H1 (why they exist) | [3–5 candidate distinctive capabilities] | | | Right-to-win test; E1–E10; X1–X12 |
| H2 (where to improve) | [candidate value pools by lens] | | | Driver tree; D1–D2; peer KPIs |
| H3 (which use cases) | [candidate domains, two core + one support] | | | Domain screen; catalogue |
| H4 (maturity position) | [expected band and rank within named peers] | | | Instrument; outside-in signals |
| H5 (compliance exposure) | [binding and dated instruments that gate H3] | | | Regulatory-status map |

Hypothesis tree is re-versioned at day 8 (after Phase 1) and day 12 (after Phase 2); each version is kept in the engagement file.

---

## 7. Ghost-deck reference

| Item | Entry |
|---|---|
| Ghost deck file | [path / ID], version [v0.1], authored [date] by [engagement lead] |
| Standard | Action titles under 15 words; horizontal-flow test (titles alone read as the argument); source line on every data slide; independent partner review ([Deckary](https://deckary.com/blog/consulting-quality-slides)) |
| Section skeleton | 1 Executive summary · 2 Where you stand (two-axis scorecard self-view vs evidenced view, rank within named peers, leadership variance) · 3 Why you exist (3–5, AI-era tag) · 4 Where to improve (value pools, driver tree) · 5 What to do (use cases, tiers, business cases) · 6 What it takes (30/60/90, roadmap, measurement design, compliance programme) · Appendix: evidence, source log, gap register ("removed, not footnoted"), AI-use disclosure |
| Rule | AI synthesis may propose slides; it may not change an action title without the engagement lead's recorded decision (section 11) |

---

## 8. QA gate owners

| Gate | When | What | Owner | Sign-off record |
|---|---|---|---|---|
| QA gate 1 (automated) | Continuous in Phase 1; report at day 8 | URL health; claim-to-passage match; two-upstream check on load-bearing numbers; aggregator trace-back; AI-generated-page rejection; bounded tool-call depth; block-not-flag; client build profile (C2a); reviewer human-read of the management-team and governance pages signed in the run README | Engagement lead (operates pipeline); Independent reviewer (human-read line) | Pipeline report [ID] |
| QA gate 2 (human + automated) | Phase A day 10 | Leadership-perception variance computed and shown; self-view vs evidenced view exhibit; every interview quote verified against transcript; anecdote vs pattern separation | Engagement lead | Checklist signed |
| QA gate 3 (independent) | Phase A days 10–11; re-run in Phase B | Horizontal-flow test; so-what test; line-by-line verification of every number and quotation in the executive summary; ≥ 30-claim sample across the deck | **Independent reviewer** (did not run the agents) | Reviewer signature; defect log |
| Partner sign | Phase A day 12; Phase B day 8 | Signs each finding; accepts residual [VERIFY] items; approves AI-use disclosure or the DRAFT banner | **Signing partner** | Signature on deck and engagement file |

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
| Verification commitment | Design target: citation resolution 100%, quote string-match, two-upstream rule, aggregator trace-back, AI-page rejection, block-not-flag with the gap register delivered to the client; independent reviewer sample ≥ 30 claims. The S02 statement renders only when the build report shows resolution = 1.0 and every attached document reconciled MATCH; otherwise the deck carries a "DRAFT — not for board use" banner. Measured state before this engagement: [resolution rate, reviewer-signed decks to date] from `runs/` — stated, not implied |
| Build profile | Client-facing builds run `--profile client` (spec C2a): a claim resting only on an attached document whose publisher hash is unreconciled is withheld and listed in the gap register as "awaiting publisher reconciliation" |
| Client AI-use clauses | [Client's own AI-use approval or disclosure clauses, if any, referenced here] **[VERIFY]** against client's procurement terms |
| Acknowledged by client sponsor | [signature, date] |

---

## 10. Timeline — Phase A (12 working days) and Phase B (8 working days after onboarding clears)

### 10.1 Phase A

| Day | Phase | Milestone | Client dependency | PLUMB owner |
|---|---|---|---|---|
| 1 | 0 | Kick-off; conflict check confirmed; Phase A inputs (§4.1) requested; onboarding for Phase B started by the client | Sponsor available | Engagement lead |
| 2 | 0 | **Charter signed** (reviewer named); hypothesis tree v0.1; ghost deck v0.1; disclosure acknowledged; first invoice | Sponsor signature | Signing partner |
| 2–8 | 1 | Nine research modules run on public sources with egress; attachments reconciled; peer set built; outside-in signals computed | Named competitors (A1) | Engagement lead |
| 5 | 2 | Instrument distributed to respondents with the cap-rule invitation paragraph (§5.1) | Respondent list (A2) | Client contact |
| 5–12 | 2 | Executive interviews E1–E10 | Interviewees scheduled by day 10 | Engagement lead |
| 8 | 1 | QA gate 1 report (released / withheld counts, gap register); hypothesis tree v0.2; reviewer human-read of leadership and governance pages signed | | Engagement lead; Independent reviewer |
| 9 | 2 | Instrument closes | Respondents | Client contact |
| 10 | 2 | **QA gate 2** signed; hypothesis tree v0.3; design-partner middle invoice | | Engagement lead |
| 10–11 | 3A | Synthesis on Phase A inputs; **QA gate 3** independent review; defect log closed | | Independent reviewer |
| 12 | 4A | Partner sign; **Phase A read-out delivered** with gap register; AI-use disclosure or DRAFT banner per build report; final Phase A invoice | Board/ExCo slot | Signing partner; Engagement lead |

Phase A slippage rule: client-side interview or respondent delays past day 10 extend the timeline day-for-day up to 10 working days; beyond that a change order applies. **There is no data-slippage rule in Phase A** because Phase A requests no confidential data.

### 10.2 Phase B (counts from the §0 Phase B trigger date)

| Day | Phase | Milestone | Client dependency | PLUMB owner |
|---|---|---|---|---|
| 0 | — | Onboarding cleared (NDA/DPA, InfoSec questionnaire, SOC 2 or equivalent, ZDR in writing); Phase B data requests (§4.2) issued | Client vendor-risk sign-off | Engagement lead |
| 5 | 2B | **Data cut-off** for D1–D12; external interviews X1–X12 sampled from D3/D4 | All Phase B items | Client contact |
| 4–8 | 3B | Synthesis on client data; business cases on system baselines; measurement design; evidence pack; QA gate 3 re-run on changed numbers | KPI extracts validated | Engagement lead; Independent reviewer |
| 8 | 4B | Partner sign; **full board deck delivered**; roadmap; engagement file closed; evidenced benchmark population updated; Phase B invoice | Board/ExCo slot | Signing partner; Engagement lead |
| +90 days | — | Fee-credit window closes (from the last deliverable) | | Founder |

Phase B slippage rule: client-side delays past Phase B day 5 (data) extend the Phase B timeline day-for-day up to 10 working days; beyond that a change order applies.

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
