# Risk Tiers and Gates (T0–T4 + Agent Gate)

**Status: v0.1 draft**
**Owner:** Methodology lead
**Applies to:** Every value pool and use case entering the recommendation deck; every agentic use case additionally passes the Agent Gate.
**Source basis:** Canada Algorithmic Impact Assessment (Levels I–IV, Appendix C), MAS Guidelines on Artificial Intelligence Risk Management (issued 7 Oct 2026; risk materiality assessed as inherent and residual on at least three dimensions — Impact, Complexity, Reliance — para 4.12, with no formula or threshold prescribed; primary text: https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions/guidelines-on-artificial-intelligence-risk-management.pdf), EU AI Act Arts 9–15 and Annex III (post Regulation (EU) 2026/1744), EY Confidence Index review cadences, OWASP Agentic Top 10 (ASI01–ASI10) and State of Agentic Security and Governance v2.01 (AT0–AT8, maturity levels 0–4), IMDA Model AI Governance Framework for Agentic AI, AWS Agentic Lens AGENTREL02-BP05, SmartSuite GRC tiering template.

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Methodology lead | Initial draft from compliance-layer research report and notes |
| v0.1.1 | 2026-10-25 | Methodology lead | MAS references reconciled to the MAS PDF: "Impact × Complexity × Reliance" replaced with the Guidelines' wording (three dimensions, inherent and residual, no formula, para 4.12); Complexity definition corrected to 4.12 (technology, novelty of application, data, explainability, third-party visibility); rule-based/RPA exclusion confirmed (1.3, fn 6) and [VERIFY] removed; "basic track" renamed to the basic policies and procedures route (2.3–2.5) and [VERIFY] removed; kill-switch expectation confirmed (5.3, fn 29, 5.23(b)) and [VERIFY] removed; paragraph numbers added for independent validation (5.19), in-context third-party testing (5.10), explainability for credit/underwriting (5.6), red teaming (5.22(b)), agent testing (5.15), agent inventory attributes (fn 25), least privilege (5.22(a)), human escalation conditions (5.9(c)), vendor contract rights (5.11(f)); "MAS material change" removed from the T4 regulator-notification list because the Guidelines contain no MAS notification duty. Open item on MAS in section 8 closed. |

---

## 1. Intake scoring (five criteria, 0–3 each, max 15)

Scored at intake by the engagement lead with the client use-case owner. Scores drive the provisional tier; overrides in section 3 can only raise the tier, never lower it.

| # | Criterion | 0 | 1 | 2 | 3 | Source anchor |
|---|---|---|---|---|---|---|
| C1 | People impact and consequentiality | No effect on any individual's rights, access, money, health or employment | Minor inconvenience; easily corrected | Material effect on individuals (service eligibility, pricing, prioritisation) with human decision between model and outcome | Consequential decision on legal status, life opportunities, health, money or liberty; or affects vulnerable groups / minors | Canada AIA impact questions; Microsoft Sensitive Uses triggers; EU Annex III |
| C2 | Data sensitivity | No personal data; public or synthetic data only | Personal data, low volume, non-sensitive | Personal data at scale, or confidential business data | Special-category / sensitive personal data (biometric, health, financial, children's), or cross-border sensitive data at scale | MAS "Impact" (para 4.12: consequences of failure, malfunction or poor performance for the FI, customers and other stakeholders, incl. fairness and consumer protection; nature and sensitivity of data processed); PDPA; SmartSuite template |
| C3 | Autonomy and reliance | Human authors output; AI is a suggestion only | Human reviews every output before use | Human reviews by exception (sampling, thresholds); AI output used directly in most cases | Fully automated action or decision; no alternative process; agent acts without per-action approval | MAS "Reliance" (para 4.12: degree of reliance on the AI, incl. third-party AI, for a decision or output; autonomy granted; level of human involvement or oversight; fn 26 dependencies between interacting AI systems); IMDA agentic autonomy level |
| C4 | External exposure | Internal, single team | Internal, enterprise-wide | Customer-, citizen- or counterparty-facing with disclosure | External-facing to the public, regulators or markets; or multi-agent / cross-boundary (OWASP AT7–AT8) | SmartSuite "external exposure"; OWASP adoption tiers |
| C5 | Reversibility of actions | Read-only / draft (reversible) | Proposes changes that a human applies (reviewable) | Writes to systems of record with tested rollback | Irreversible actions: delete, move funds, rotate secrets, send externally, change physical state | NHI action-risk tiering (reversible / reviewable / irreversible); AWS autonomous / notify / approve; OpenAI "reversibility" practice |

Complexity (the third MAS dimension, para 4.12: complexity of the AI technology, novelty of the application, the data used and how explainable the outputs are; for third-party AI, the level of visibility into the technology or data) is recorded as a modifier, not a scored criterion: a use case built on a frontier model with RAG, fine-tuning or multi-agent orchestration adds +1 to the total (cap 15). Tools whose outputs come solely from predefined rules or fixed formulae, and RPA without a learning component, are outside the MAS definition of AI (para 1.3 and fn 6 of the Guidelines). Note that MAS requires both inherent (pre-control) and residual (post-control) materiality to be rated and residual materiality to sit within risk appetite before deployment (4.11); this intake score is the inherent rating, and the gate decision in section 5 is where residual materiality is judged.

---

## 2. Tier table (T0–T4)

Score bands: T1 = 0–5, T2 = 6–10, T3 = 11–15 without an override, T4 = 16+ (only reachable through the complexity modifier plus an override) or any T4 override. T0 is override-only.

| Tier | Trigger (score or override) | Examples | Required controls before go-live | Testing / validation cadence | Decision authority | Review cycle and monitoring | Analogues |
|---|---|---|---|---|---|---|---|
| **T0 Prohibited** | Any EU Art 5 practice; new Art 5 nudifier / CSAM generation ban (applies 2 Dec 2026); China or Vietnam Art 7 prohibited acts; Thailand / Malaysia draft Tier 1 "unacceptable"; social scoring; subliminal manipulation; real-time public biometric identification without legal basis; Texas TRAIGA prohibited uses | Nudification apps; emotion inference in hiring; social-credit scoring of citizens; covert behavioural manipulation | None. Use case is rejected and logged with reason and the instrument that prohibits it | n/a | Rejected by engagement lead; logged in the regulatory-exposure map | n/a | EU Art 5; Vietnam Law 134/2025 Art 7; Indonesia draft "unacceptable" tier; Malaysia draft Tier 1 |
| **T1 Low** | Score 0–5. Internal productivity; no personal data; human edits all output; read-only or draft tools only | Meeting summarisation of internal notes; code-completion with developer review; internal knowledge search over public documents | Inventory record (MAS fields + tier); acceptable-use policy; AI-use disclosure to staff; vendor on approved list with retention and residency terms; prompt and model-version logging | Peer review at intake; annual re-check | Use-case owner | Review every 3 years (EY Low); monitor yearly; re-tier on data, model, platform, regulatory, scope or usage change | Canada AIA Level I; EY Low; SmartSuite Low (0–5); MAS basic policies and procedures route (paras 2.3–2.5: where poor performance or unavailability of the AI is unlikely to have a material adverse impact; minimum: accountable senior manager, permitted and prohibited uses with human-review rules, approved-tool list, staff education, compliance checks, periodic review; 2.4 examples are drafting and proofreading, internal summarisation, internal document review, chart generation, marketing images, internal policy chatbots) |
| **T2 Moderate** | Score 6–10. Personal data present, or customer-facing content, with human review before release | Customer-service drafting with agent review; marketing copy generation; HR policy chatbot for staff; document classification with human confirmation | T1 plus: DPIA / PIA; impact assessment (ISO 42001 A.5 / 42005); output disclaimers and AI-interaction disclosure (EU Art 50, Korea notice, IMDA chatbot guidelines); hallucination and data-leakage testing per IMDA LLM Starter Kit five risks; logging of prompts, retrieved context, model version and reviewer identity; synthetic-content marking where media is generated | Peer review plus documented test results; biennial re-validation; quarterly KRIs | Function head with risk-function sign-off | Review every 2 years (EY Medium); monitor quarterly | Canada AIA Level II (one expert review, meaningful explanation on request); EY Medium; SmartSuite Moderate (6–12) |
| **T3 High** | Score 11–15, **or** any override in section 3 marked T3: regulated eligibility, health, financial / investment advice (SFC), minors, EU Annex III domain, Korea high-impact domain, Vietnam high-risk list, Australia "substantially automated" significant decision (APP 1.7–1.9) | Insurance underwriting support; clinical decision support; loan pre-screening with adviser override; investment-research copilot (SFC high-risk); student assessment support | T2 plus: formal independent validation before deployment (MAS 5.19 for high materiality: validators competent, independent of development and deployment, covering conceptual soundness, data suitability, implementation, metrics and testing, explainability and fairness, assumptions and limitations; regular independent re-validation per 5.24); fairness and robustness testing with documented metrics (MAS 5.8, 5.14); Annex IV-style technical file (MAS 5.17 documentation sufficient for independent replication); human-in-the-loop with specific intervention points and meaningful explanation per decision (Canada Level III; MAS 5.9(c) escalation to human review on pre-defined conditions); contingency plan with fallback and rollback (MAS 5.3 for high-risk use cases); six-month decision reconstruction (model, prompt, retrieval-corpus versioning); incident procedure with timelines (EU Art 73, Vietnam, Thailand draft); in-context testing of third-party models with client data (MAS 5.10); logging design per EU Art 12; SFC notification of significant changes where applicable | Independent expert review before go-live; annual independent re-validation; monthly monitoring against KRIs and drift thresholds | AI governance committee with recorded risk acceptance | Review yearly (EY High); monitor monthly; re-validate on any material change | Canada AIA Level III; MAS high materiality; EU Arts 9–15, 26; Korea high-impact obligations; SmartSuite High (13–20) |
| **T4 Critical** | Score 16+ (with complexity modifier) **or** any hard-coded T4 override: employment screening, credit decisioning, autonomous production actions, irreversible external actions by agents, cross-border sensitive data at scale, critical infrastructure, biometric identification | Automated CV screening or ranking; automated credit limit or approval; agent that executes payments or trades; agent that modifies production configuration; biometric access control; OT control in energy, water, transport | T3 plus: two independent reviews (Canada Level IV); publication of an assessment summary where a regime requires it (Canada, AU DTA, Korea procurement preference); red-team before deployment (MAS agentic expectation; OWASP); kill switch tested on schedule with test records; executive risk acceptance signed; regulator notification where applicable (SFC, MAS material change, Vietnam portal registration, Korea high-impact self-assessment); contractual indemnity, audit rights and change-notification rights with vendors (MAS third-party, EU Art 25); approved contingency plan before operation; retention of screening and configuration records (Mobley v. Workday lesson); AU APP 1.7–1.9 privacy-policy disclosure where AU personal information | Independent re-validation every cycle; continuous monitoring; override-rate and response-time monitoring as automation-bias check (IMDA) | Named accountable executive **and** board committee; risk acceptance recorded in minutes | Review yearly minimum; continuous monitoring; event-triggered re-tier | Canada AIA Level IV; EU Annex III (employment, credit, biometrics, critical infrastructure); Korea high-impact (hiring, loan screening, biometrics, energy, water, nuclear, transport); SmartSuite Critical (21+) |

Each value pool inherits the highest tier of the use cases inside it. The value-by-feasibility score from the engagement methodology is penalised by tier so that a T3 or T4 use case needs more value to rank.

---

## 3. Rule-based overrides (apply regardless of score)

An override sets a floor tier. Where two overrides fire, the higher wins. Record the override ID on the inventory record and the gate checklist.

| ID | Trigger | Floor tier | Why hard-coded | Instrument(s) |
|---|---|---|---|---|
| OV-01 | Employment or HR screening, ranking, shortlisting, promotion or termination support | **T4** | Top tier in every scheme reviewed; Mobley v. Workday conditionally certified a nationwide collective (1.1 billion rejected applications represented); NYC LL144 bias-audit duty; Illinois HB 3773; Colorado SB 26-189 | EU Annex III; Korea high-impact (hiring); Mobley v. Workday; NYC LL144; IL HB 3773; CO SB 26-189 (1 Jan 2027); Singapore Workplace Fairness Act (expected end-2027) and TAFEP guidance |
| OV-02 | Credit decisioning, credit scoring, loan screening, insurance underwriting or pricing | **T4** | MAS names credit decisioning and insurance underwriting as needing more exacting explainability; Korea lists loan screening as high-impact; EU Annex III | MAS AIRM; Korea AI Basic Act Art 2(4); EU Annex III; CO SB 26-189 (lending, insurance) |
| OV-03 | Anything touching minors (users, data subjects or content directed at under-18s) | **T3 minimum; T4 if any decision or action** | China anthropomorphic measures (parental consent under 14; no intimate-relationship services to minors); Garante actions on age verification (Replika, Character.AI); DPDP children's data penalty tier (INR 200 crore) | China Interim Measures on Anthropomorphic AI (15 Jul 2026); India DPDP Rules; eSafety actions (AU); EU Art 5 |
| OV-04 | Biometric identification, categorisation or emotion recognition | **T4** (T0 if real-time public identification without legal basis) | Prohibited or high-risk in EU; Korea high-impact; Clearview fines in four EU states; Worldcoin HK enforcement | EU Art 5 / Annex III / Art 50 deployer duty; Korea high-impact (biometrics); PCPD Worldcoin order; Indonesia draft "unacceptable" |
| OV-05 | Critical infrastructure (energy, water, nuclear, transport, telecoms, utilities) or OT control | **T4** | Korea high-impact domains; Thailand draft royal-decree list; EU Annex III; IEC 62443 security levels apply | Korea Art 2(4); Thailand draft AI Act; EU Annex III; CSA agentic addendum |
| OV-06 | Korea high-impact domain not already listed (healthcare and medical devices, public services, student evaluation, assessment of individual rights) and the system reaches Korean users or markets | **T3** | Extraterritorial; pre-deployment self-assessment, explanation, user-protection plan, human oversight, five-year dossier; fines deferred but suspension power live | Korea AI Basic Act (in force 22 Jan 2026) |
| OV-07 | Generative AI touching investment recommendations, advice or research for an SFC-licensed corporation (or equivalent MAS / ASIC / FSC advisory context) | **T3** | SFC circular treats this as high-risk: validation, human review of output, robustness testing against prompt variations, user disclosure, SFC notification of significant changes | SFC circular 24EC55 (12 Nov 2024, effective immediately); MAS AIRM; Korea FSC conduct standards (22 Jun 2026) |
| OV-08 | Health or clinical use (diagnosis, triage, treatment support, direct-to-consumer health AI) | **T3** (T4 if automated decision) | MOH/HSA AIHGle 2.0; HSA SaMD; TGA ARTG; EU Annex I (2 Aug 2028) for device-embedded AI; Vietnam 18-month transition for healthcare | AIHGle 2.0 (10 Mar 2026); HSA SaMD guidelines; TGA; Vietnam Law 134/2025 |
| OV-09 | Regulated eligibility decision (benefits, licences, immigration, education admission, essential services) | **T3** (T4 if fully automated) | Robodebt (470,000 wrong debts, A$1.872bn settlement); Dutch childcare benefits; Canada AIA Levels III–IV require human final decision | Canada AIA; EU Annex III; AU APP 1.7–1.9 (10 Dec 2026); Indonesia draft high tier |
| OV-10 | Autonomous production action or any irreversible external action by an agent (C5 = 3 with C3 ≥ 2) | **T4** | Agent gate rule: no autonomous operation of irreversible tools above T1; MAS kill-switch and red-team expectations | OWASP ASI02/ASI03/ASI10; IMDA agentic MGF; AWS "Approve" tier; MAS AIRM agentic expectations |
| OV-11 | Cross-border transfer of sensitive personal data at scale, or any model route outside the client's jurisdiction without a documented transfer basis | **T3** | PDPA s.26 transfer limitation; DeepSeek blocked in Italy and suspended in Korea on transfer grounds; vendor EU establishment determines lead authority (Garante annulment) | PDPA s.26; GDPR; PIPC and Garante actions |
| OV-12 | Use case already deployed by the client when an override fires | **Escalate** (see section 6) | Governance committee must decide remediation, pause or risk acceptance within a fixed window | SmartSuite "escalate" decision; MAS existing-use inventory expectation |
| OV-13 | Jurisdiction map shows a binding prohibition or a filing regime the client cannot satisfy (e.g., China algorithm filing / security assessment without a local partner; Vietnam pre-market certification without commercial presence) | **NO-GO** until capability exists | Gate on local-partner filing capability rather than attempt direct compliance | China GenAI Interim Measures, labelling measures, CSL; Vietnam Law 134/2025 |

---

## 4. The Agent Gate

Layered on top of the tier for any use case where a model can call tools, take actions or orchestrate other agents (OWASP AT3 and above). The tier captures the decision; the Agent Gate captures the action.

### 4.1 Agent identity and privilege

| Requirement | Standard | Evidence |
|---|---|---|
| Unique identity per agent, tied to a supervising human or agent; no reuse of human credentials | OWASP ASI03; NIST AASI / NCCoE concept paper (OAuth 2.0 extensions for non-human principals); IMDA agentic MGF; MAS (agent identifiers recorded) | Identity register entry; IdP configuration export |
| Short-lived, task-scoped credentials; independent revocation; access reviews on the human cadence | OWASP ASI03; CSA note on NIST AASI | Credential TTL setting; last access review record |
| Least-privilege tool and data allowlist; deny-by-default egress; whitelist trusted servers; sandboxed code execution | OWASP ASI02, ASI05; IMDA; CSA Securing Agentic AI addendum; MAS (least privilege for agents with tool access) | Tool allowlist; egress policy; sandbox configuration |
| Owner and expiry per agent | OWASP (Cycode mitigations) | Inventory record fields "owner" and "expiry" |
| AIBOM / AgBOM with signed provenance for tools, connectors and MCP servers | OWASP ASI04; OWASP Agent Control Standard v0.1 (AgBOM in CycloneDX/SWID/SPDX); ATLAS AML.T0010.005, AML.T0110, AML.T0109 | AIBOM file; connector approval log |

### 4.2 Action classes (approval tiers)

| Class | Definition | Permitted tool classes | Approval requirement | Logging | Source |
|---|---|---|---|---|---|
| **Autonomous** | Low risk, reversible; execute without human involvement | Reversible only (read, search, draft, summarise) | None; policy check at gateway | Full action log | AWS Agentic Lens "Autonomous"; IMDA; OpenAI "log-only" |
| **Notify** | Medium risk; proceed and inform a named human | Reversible, and reviewable where a human applies the change (propose edits, create draft records, open tickets) | Post-hoc notification within a defined window; human can reverse | Full action log plus notification receipt | AWS "Notify"; NHI "reviewable" |
| **Approve** | High-impact or irreversible; explicit human approval before execution | Irreversible (delete, move funds, rotate secrets, send externally, change production or physical state) and any reviewable action at T3+ | Approval request must show the **raw action**, agent reasoning, impact assessment and execution history; timeout fails safe; reviewer identity, rationale and timestamp logged | Immutable log of request, approval and outcome | AWS "Approve"; OWASP (confirmations show raw action, not summary); EU Art 14(4)(e) interruption; MAS human approval for higher-risk actions |

### 4.3 Tool classes

| Tool class | Examples | Lowest tier at which autonomous use is permitted | Notes |
|---|---|---|---|
| **Reversible** | Read, search, retrieve, draft, summarise, classify into a staging area | T1–T4 (always permitted as Autonomous, subject to data-access rules) | Retrieved content is untrusted input (OWASP ASI01, ASI06; LLM01) |
| **Reviewable** | Propose edits, create draft records, stage configuration changes, open tickets, queue messages for human send | T1–T2 as Notify; T3+ as Approve | Must have a tested human-apply step |
| **Irreversible** | Delete, move funds or execute trades, rotate or create secrets, send externally (email, API, publish), modify production configuration, actuate physical systems | **Never autonomous above T1**; Approve class at every tier; at T4 a second control check and restricted access path | NHI "irreversible"; OWASP ASI02, ASI10; MAS kill switch; ATLAS AML.T0086, AML.T0101 |

### 4.4 Lethal-trifecta rule

Any single agent session that combines **(a)** access to private or client data, **(b)** exposure to untrusted content (web pages, retrieved documents, inbound email, tool outputs from third parties), and **(c)** the ability to communicate externally or write to an external system **requires human approval** for every external action in that session, regardless of tier. No high-impact tool may be reachable from untrusted indirect input without a human gate. Source: OWASP Agentic AI Governance Maturity Model (CSA note); OWASP LLM01 guidance. The firm's own research agent falls under this rule.

### 4.5 Kill switch and circuit breakers

| Requirement | Evidence |
|---|---|
| A documented kill switch that halts the agent and revokes its credentials, owned by a named role | Procedure document; owner on inventory record |
| Tested on a schedule (T2 annually; T3 quarterly; T4 monthly or per release) with time-to-halt recorded | Test log with date, tester, time-to-halt, result |
| Circuit breakers on budget, action count, error rate and anomaly score; blast-radius isolation between agents | Configuration export; alert history |
| Behavioural baseline and anomaly detection (OWASP maturity level 3) | Monitoring dashboard screenshot or export |

Context: ISACA 2026 found 56% do not know how long it would take to halt an AI system and 39% do not know whether a documented shutdown process exists; MAS expects kill switches to be maintained and regularly tested (**[VERIFY]** against MAS PDF).

### 4.6 OWASP ASI01–ASI10 mapping to gate controls

| ASI | Risk | Gate control(s) | ATLAS anchor |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | Treat retrieved content as untrusted; per-channel injection detection with measured FP/FN; lethal-trifecta rule | AML.T0080 context poisoning |
| ASI02 | Tool Misuse and Exploitation | Tool classes and action classes (4.2–4.3); least-agency allowlist; immutable tool-call logs | AML.T0053, AML.T0086, AML.T0101 |
| ASI03 | Identity and Privilege Abuse | Unique identity, short-lived task-scoped credentials, no human-credential reuse, access reviews | AML.T0083 credentials from agent configuration |
| ASI04 | Agentic Supply Chain Vulnerabilities | AIBOM / AgBOM with signed provenance; connector approval; MCP server whitelist | AML.T0010.005, AML.T0110, AML.T0109 |
| ASI05 | Unexpected Code Execution | Sandboxed execution; deny-by-default egress; no code execution above AT4 without Approve class | — |
| ASI06 | Memory and Context Poisoning | Ephemeral per-user/task memory; memory write controls; threat model for memory poisoning (IMDA) | AML.T0080.000 memory, .001 thread |
| ASI07 | Insecure Inter-Agent Communication | Mutual authentication between agents; AT7–AT8 use cases default to T3+ | ATLAS gap: no lateral-movement tactic (CSA gap analysis) |
| ASI08 | Cascading Failures | Blast-radius isolation; circuit breakers; staged rollout | — |
| ASI09 | Human-Agent Trust Exploitation | Approve-class confirmations show the raw action; override-rate and response-time monitoring for automation bias (IMDA) | — |
| ASI10 | Rogue Agents | Owner and expiry per agent; behavioural baselines; tested kill switch; budget limits | — |

### 4.7 OWASP adoption-tier ladder (AT0–AT8) and gate posture

| AT | Description | Default gate posture |
|---|---|---|
| AT0 | Shadow AI | Not permitted; discover and inventory; treat as OV-12 escalation if found in production |
| AT1 | Vendor-embedded assistant | T1–T2 by tier; vendor assessment (evidence-pack artefact 7) |
| AT2 | Platform-integrated | T1–T2 by tier; data-residency and retention terms confirmed |
| AT3 | Citizen-developer agent | Agent Gate applies; reversible tools only unless re-tiered |
| AT4 | Code-executing agent | Sandbox mandatory; Approve class for any write |
| AT5 | Custom in-house agent | Full Agent Gate; AIBOM; kill switch tested |
| AT6 | Externally-extended agent (external tools / MCP) | Lethal-trifecta rule presumed to apply; T3 minimum where client data present |
| AT7 | Multi-agent orchestration | T3 minimum; mutual authentication; cascading-failure controls |
| AT8 | Federated / cross-boundary | T4 by default; executive risk acceptance |

Governance maturity levels 0–4 (Unaware; Experimentation without guardrails; Policy-defined and human-in-the-loop; Integrated and continuous oversight; Adaptive and self-regulating) are used in the maturity assessment, not as a gate; the gate requires at least level 2 behaviours for T2 and level 3 behaviours (working kill switch, real-time anomaly detection, machine-readable policy) for T4 agentic use cases.

---

## 5. GO / CONDITIONAL / NO-GO rules

| Decision | Rule |
|---|---|
| **GO** | All of: (1) named accountable owner recorded; (2) tier assigned, overrides checked, control checklist for that tier costed into the business case; (3) no unresolved T0 flag; (4) data-rights and residency basis documented for every data source and model route (PDPA s.26 or equivalent); (5) baseline and measurement plan exist; (6) for T3+, a validation path that does not depend solely on vendor attestations (in-context testing with client data planned); (7) for agentic use cases, Agent Gate sections 4.1–4.5 complete and no irreversible tool in the Autonomous class above T1 |
| **CONDITIONAL** | Controls exist on paper but not in evidence (policy without logs, kill switch without test record, DPIA without sign-off); or a required artefact is scheduled but not yet produced. The use case may enter the recommendation deck flagged "conditional" with named conditions, owners and dates. It may not go live until conditions clear |
| **ESCALATE** | An override fires on a use case the client has already deployed (OV-12); or the reviewer and use-case owner disagree on the tier. Goes to the AI governance committee within the engagement's escalation window with a recommended action (pause, remediate, risk-accept) |
| **NO-GO** | Any of: (1) T0 flag confirmed; (2) regulatory-exposure map shows a binding prohibition or a filing regime the client cannot satisfy (OV-13); (3) a T4 use case with no named executive willing to sign risk acceptance; (4) an agentic use case requiring autonomous irreversible action; (5) third-party model route with no obtainable residency, retention or audit-rights terms where the tier requires them |

Decisions are recorded as approve / condition / reject / escalate with date, reviewer and rationale on the gate checklist and the inventory record.

---

## 6. Review and re-tier triggers

Re-tier on any of: data or model change; incident; platform or vendor change (including vendor retention or residency terms); regulatory change in the exposure map; strategy shift; expanded usage, scope or jurisdiction (EY re-vetting triggers; Canada AIA re-assessment at design, before production and on scope change). The regulatory-exposure map is regenerated at each benchmark refresh and at minimum quarterly.

---

## 7. One-page gate checklist (signed per use case)

```
AI USE-CASE GATE CHECKLIST                                  Status: v0.1 draft
Client: ____________________   Engagement: ____________________
Use case ID: _________  Name: _______________________________________
Value pool: ______________________  Use-case owner (named): _______________

A. INTAKE SCORE (0–3 each)
   C1 People impact ___  C2 Data sensitivity ___  C3 Autonomy/reliance ___
   C4 External exposure ___  C5 Reversibility ___  Complexity modifier (+1) ___
   Total ___ / 15 (+1)        Provisional tier: T__

B. OVERRIDES (tick all that fire; record floor tier)
   [ ] OV-01 HR/employment  [ ] OV-02 Credit/underwriting  [ ] OV-03 Minors
   [ ] OV-04 Biometrics     [ ] OV-05 Critical infra       [ ] OV-06 Korea high-impact
   [ ] OV-07 SFC/advice     [ ] OV-08 Health/clinical      [ ] OV-09 Regulated eligibility
   [ ] OV-10 Autonomous/irreversible agent action          [ ] OV-11 Cross-border sensitive
   [ ] OV-12 Already deployed (ESCALATE)  [ ] OV-13 Unsatisfiable filing regime (NO-GO)
   Final tier: T__          T0 flag: [ ] none  [ ] raised — instrument: ___________

C. JURISDICTIONS AND INSTRUMENTS (from regulatory-status map)
   Operating / selling into: __________________________________________
   Binding instruments engaged: _______________________________________
   Dated obligations within 24 months: ________________________________

D. CONTROL CHECKLIST FOR TIER (evidence pointer, not promise)
   [ ] Inventory record (MAS fields + tier)          Evidence: __________
   [ ] Acceptable-use / AI policy reference          Evidence: __________
   [ ] Vendor on approved list; residency + retention terms   Evidence: ______
   [ ] DPIA / PIA (T2+)                              Evidence: __________
   [ ] Impact assessment ISO A.5 / 42005 (T2+)       Evidence: __________
   [ ] Disclosure: AI interaction / synthetic marking (T2+)   Evidence: ______
   [ ] Testing: hallucination, leakage, bias, adversarial (T2+)  Evidence: ___
   [ ] Logging: prompt, context, model version, reviewer (T2+) Evidence: _____
   [ ] Independent validation (T3+)                  Evidence: __________
   [ ] Technical file / Annex IV-style (T3+)         Evidence: __________
   [ ] Human-in-the-loop design + explanation (T3+)  Evidence: __________
   [ ] Contingency / rollback plan (T3+)             Evidence: __________
   [ ] Incident procedure with timelines (T3+)       Evidence: __________
   [ ] In-context test of third-party model (T3+)    Evidence: __________
   [ ] Two independent reviews (T4)                  Evidence: __________
   [ ] Red-team report pre-deployment (T4)           Evidence: __________
   [ ] Kill-switch test record (T4; agentic T2+)     Evidence: __________
   [ ] Executive risk acceptance (T4)                Evidence: __________
   [ ] Regulator notification / registration (T4 where applicable)  Evidence: __
   [ ] Vendor indemnity, audit and change-notice rights (T4)  Evidence: ______

E. AGENT GATE (agentic use cases only)
   OWASP adoption tier: AT__      Governance maturity level observed: __
   [ ] Unique agent identity; no human-credential reuse
   [ ] Short-lived task-scoped credentials; owner and expiry recorded
   [ ] Least-privilege tool allowlist; deny-by-default egress; sandbox
   [ ] AIBOM / connector approvals
   Tool classes present:  [ ] Reversible  [ ] Reviewable  [ ] Irreversible
   Action classes assigned: Autonomous: ______  Notify: ______  Approve: ______
   [ ] No irreversible tool in Autonomous class (mandatory above T1)
   [ ] Lethal trifecta present? [ ] No  [ ] Yes → human approval on every external action
   [ ] Kill switch documented, owner named, last test date: ________ time-to-halt: ____
   [ ] ASI01–ASI10 coverage reviewed (attach mapping)

F. BUSINESS CASE LINKAGE
   [ ] Tier control costs included in business case
   [ ] Baseline and measurement plan attached
   [ ] Validation path independent of vendor attestations (T3+)

G. DECISION
   [ ] GO   [ ] CONDITIONAL (conditions, owners, dates attached)   [ ] ESCALATE   [ ] NO-GO
   Rationale: ___________________________________________________________
   Next review date: __________   Re-tier triggers noted: [ ]

Reviewer (name, role): ______________________  Signature: ________  Date: ______
Use-case owner acknowledgement: ______________  Signature: ________  Date: ______
Risk / governance sign-off (T2+): ____________  Signature: ________  Date: ______
Executive risk acceptance (T4): ______________  Signature: ________  Date: ______
```

---

## 8. Open items for v0.2

| Item | Action |
|---|---|
| MAS final text: proportionality thresholds, "basic track" definition, agentic clauses | Verify against the MAS guidelines PDF; currently rests on Baker McKenzie, Allen & Gledhill and one practitioner commentary **[VERIFY]** |
| Canada Directive Appendix C per-level testing, monitoring and approval-to-operate cells | Primary text not fetched; cells drawn from secondary summaries **[VERIFY]** |
| Korea grace-period end date and per-article fine schedule | Not confirmed from law.go.kr **[VERIFY]** |
| Vietnam high-risk list and implementing decrees | Pending; re-check before any VN use case is tiered |
| Australia "Australian Standards for AI" tiers | No bill tabled; re-check Q1 2027 |
| Malaysia and Thailand bill passage and penalty amounts | Both targeted end-2026; add rows to overrides when enacted |
