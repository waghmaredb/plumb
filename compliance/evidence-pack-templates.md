# Evidence Pack Templates (10 artefacts + transparency summary + deliverable disclosure)

**Status: v0.1 draft**
**Owner:** Methodology lead
**Principle:** A requirement with no evidence is not met (SecurityScientist; Schellman; GAICC). Every artefact carries a named owner, a version, a retention rule and a pointer to the clauses it satisfies. Artefacts are produced in the client's own template so they drop directly into an ISO/IEC 42001 certification file, an EU Annex IV technical file or a MAS supervisory inventory.
**Design note:** The impact assessment and the inventory are the two controls GRC platforms automate worst (aiactindex.eu review of Vanta: model inventory, impact assessment and lifecycle controls remain manual checklists); they are the two the engagement produces by hand.

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Methodology lead | Initial draft from compliance-layer research report and notes |
| v0.1.1 | 2026-10-25 | Methodology lead | All MAS AIRM references reconciled to the MAS PDF: section headings and paragraph numbers added in the mapping key and every artefact row; inventory field 9 renamed "model review status" (4.7); "Impact × Complexity × Reliance" replaced with the Guidelines' wording (4.10–4.12); unsupported "count of material use cases on one provider in risk appetite" replaced with 5.11(c) concentration-risk consideration; "audit trails available to MAS" replaced with 5.17 (documentation sufficient for an independent party) and 3.6 (demonstrate oversight to MAS); agentic clauses pinned to 1.11, fn 25, 5.15, 5.23(a) and (d), 5.3; artefact 9 corrected to state that the Guidelines contain no incident-notification-to-MAS clause; s.5 sub-heading list corrected (no separate "validation" or "decommissioning" heading; decommissioning sits at 5.26 under Change Management). [VERIFY] flags on section numbering and agentic clauses removed; per-regime incident clocks and the response-paper qualifier remain [VERIFY]. Primary URL added. |

---

## 0. Mapping key

| Column | Vocabulary used |
|---|---|
| ISO 42001 | Clause numbers (4.3, 5.2, 6.1.1–6.1.4, 6.2, 7.2, 8.2–8.4, 9.1–9.3, 10.2) and Annex A control IDs (A.2.2 … A.10.4; 38 controls in 9 areas) |
| EU AI Act | Articles as amended by Regulation (EU) 2026/1744; Annex III obligations apply 2 Dec 2027, Annex I 2 Aug 2028, Art 50 live since 2 Aug 2026 |
| MAS AIRM | MAS Guidelines on Artificial Intelligence Risk Management (issued 7 Oct 2026; https://www.mas.gov.sg/-/media/mas-media-library/regulation/guidelines/bd/guidelines-on-artificial-intelligence-risk-management-for-financial-institutions/guidelines-on-artificial-intelligence-risk-management.pdf). Sections: 1 Introduction; 2 Application of the Guidelines (2.1–2.5); 3 AI Oversight (3.1–3.6); 4 Key AI Risk Management Systems, Policies and Procedures (4.1–4.13: AI Identification 4.2–4.4, AI Inventory 4.5–4.9, AI Risk Materiality Assessment 4.10–4.13); 5 AI Life Cycle Controls (5.1–5.26); 6 AI Capability & Capacity (6.1–6.3). Para 1.8: Guidelines take effect 7 Oct 2027; FIs may meet s.3–4 from 7 Oct 2027 and s.5–6 by 7 Oct 2028. Verified against the MAS PDF on 2026-10-25. One secondary source reports that the response-to-feedback paper (para 13.5) asks FIs to apply lifecycle controls to high-risk use cases as soon as possible rather than waiting for Oct 2028 — the response paper was not reachable at verification **[VERIFY]** |
| NIST AI RMF | Functions GOVERN / MAP / MEASURE / MANAGE (AI RMF 1.0; 19 categories, 72 subcategories); AI 600-1 risk names where relevant. RMF is under revision; vocabulary may change |
| AI Verify | 11 principles: Transparency, Explainability, Reproducibility, Safety, Security, Robustness, Fairness, Data Governance, Accountability, Human Agency & Oversight, Inclusive Growth / Societal / Environmental Well-being (106 process checks) |
| Sampling | What an ISO 42001 Stage 2 auditor, an EU notified body or a MAS supervisor would pull, and the minimum sample the engagement must be able to produce |

Retention default: 10 years for AI documentation (KPMG controls guide); Korea safety-and-trust dossier 5 years; Colorado SB 26-189 3 years; Thailand draft six-month logs. Use the longest applicable.

---

## Artefact 1 — AI inventory record (per use case)

| Field | Content |
|---|---|
| Purpose | Single source of truth for what AI exists, what it is approved to do, how material it is and where its evidence lives. Unit of materiality is the use case (MAS 4.10; the inventory itself covers use cases, systems and models, 4.5). Populates MAS inventory, AU DTA use-case register, Korea dossier index, ATRS Tier 1 |
| Template outline | 1. Use-case ID, name, value pool · 2. Purpose and intended use (ISO A.9.4) · 3. Approved scope (jurisdictions, user groups, channels, exclusions) · 4. Model type and provider (foundation model, fine-tune, RAG, agent; version pinned) · 5. Data (sources, personal-data flag, special-category flag, residency, transfer basis) · 6. Dependencies (vendors, APIs, connectors, MCP servers, subservice organisations) · 7. Lifecycle status (design / pilot / production / retired) · 8. Materiality rating and tier (T0–T4) with override IDs · 9. Model review status (MAS 4.7 wording; record last review or validation, reviewer, independence) · 10. Roles (accountable executive, use-case owner, validator, operator) · 11. Agent fields where applicable (agent identifier, owner, expiry, tool allowlist, action classes, kill-switch owner, last kill-switch test) · 12. Links to documentation (artefacts 2–10) · 13. Review dates and re-tier triggers · 14. Concentration flag (counts toward material use cases on a single provider) |
| ISO 42001 | 4.3 scope; A.4.2 resource documentation; A.4.3 data resources; A.4.4 tooling resources; A.6.2.7 technical documentation; A.9.4 intended use; A.10.2 allocating responsibilities |
| EU AI Act | Art 11 / Annex IV (technical documentation index); Art 26 deployer records; Art 49 registration where high-risk; Art 25 supplier agreements |
| MAS AIRM | s.4 Key AI Risk Management Systems, Policies and Procedures: identification (4.2–4.4), inventory (4.5–4.9), materiality (4.10–4.13). Para 4.7 attributes the inventory "may include": purpose and description; approved scope of use (e.g. jurisdiction); model type; data used; dependencies; lifecycle status; assigned risk materiality rating; model review status; key roles and responsibilities; links to essential documentation. Fn 25: agent attributes may include identifiers, accessible tools and systems, components, guardrails. 4.8: inventory design reviewed for new technologies and third-party AI. Concentration risk is a third-party onboarding consideration (5.11(c)), not an inventory field |
| NIST AI RMF | GOVERN 1 (policies, inventory); MAP 1 (context), MAP 3 (capabilities, targeted usage) |
| AI Verify | Accountability; Transparency; Data Governance |
| Owner | Use-case owner (content); AI governance / control function (final arbiter of what counts as AI per MAS 4.3; approves each materiality assessment per 4.13; independently checks inventory accuracy and completeness per 4.9) |
| Sampling expectation | ISO Stage 2: full register plus 3–5 records traced end-to-end to artefacts 2–9. MAS 7 Oct 2027 milestone (s.3–4): identification process, inventory and materiality ratings for all FI use cases. Auditor will test that every production AI system in the CMDB appears in the inventory (reconciliation) |

## Artefact 2 — Impact assessment

| Field | Content |
|---|---|
| Purpose | Formal, documented evaluation of potential consequences for individuals, groups and society; drives the tier and the control checklist. One assessment, four regimes: Canada AIA-style scoring, ISO A.5 individual and societal sections, DPIA where personal data, FRIA where EU-exposed or Korea high-impact |
| Template outline | 1. Scope and system description (reuse artefact 1) · 2. Stakeholders and affected groups (incl. vulnerable groups, minors) · 3. Intake score C1–C5 and complexity modifier; provisional tier · 4. Overrides checked; final tier · 5. Impact on individuals (rights, access, money, health, employment; procedural fairness; contestability) · 6. Societal impact (discrimination at scale, information integrity, environmental) · 7. DPIA section (lawful basis, necessity, proportionality, transfer basis PDPA s.26 / GDPR Ch. V, data-subject rights, automated-decision rights under PIPA / APP 1.7–1.9 / Colorado) · 8. Fundamental-rights section (EU Art 27 structure; Korea best-efforts FRIA) · 9. Mitigations and residual risk against appetite · 10. Human-oversight design summary (cross-ref artefact 6) · 11. Sign-off (assessor, legal / privacy, use-case owner; T3+ governance committee) · 12. Retention rule and re-assessment triggers (design, before production, on scope change) |
| ISO 42001 | 6.1.4 AI system impact assessment; 8.4 results; A.5.2 process; A.5.3 documentation; A.5.4 impact on individuals or groups; A.5.5 societal impacts; ISO/IEC 42005:2025 method |
| EU AI Act | Art 27 fundamental-rights impact assessment (deployers of Annex III systems); Art 9 risk management input; Art 10(5) special-category data for bias detection |
| MAS AIRM | s.4 AI Risk Materiality Assessment (4.10–4.13): inherent (pre-control) and residual (post-control) materiality, rated on at least Impact, Complexity and Reliance (4.12) — no formula or threshold prescribed; residual materiality within risk appetite before deployment (4.11); control function sets the framework and approves each assessment (4.13) |
| NIST AI RMF | MAP 1, MAP 5 (impacts); MEASURE 2 (trustworthiness evaluation); GOVERN 5 (stakeholder engagement) |
| AI Verify | Fairness; Inclusive Growth / Societal / Environmental Well-being; Human Agency & Oversight; Accountability |
| Owner | Impact assessor (engagement) with legal / privacy co-sign; AIMS lead owns the procedure (A.5.2) |
| Sampling expectation | ISO Stage 2: the approved procedure with triggers and thresholds, plus completed assessments for every T2+ use case with sign-off and retention rule. EU notified body: FRIA for each Annex III deployment. Canada-style publication expected for public-sector T4 (Open Government Portal pattern; AU DTA residual risk reported) |

## Artefact 3 — Risk register entry

| Field | Content |
|---|---|
| Purpose | Records the tier, treatment and residual risk per use case against the organisation's AI risk appetite; links to the firm-level register and the Statement of Applicability |
| Template outline | 1. Risk ID, use-case ID, tier · 2. Risk sources (ISO Annex C: complexity, lack of transparency, automation level, ML risks, hardware, lifecycle, technology readiness) · 3. Threat scenarios (OWASP LLM 2026 / ASI IDs; ATLAS technique IDs; NIST AI 600-1 risk names) · 4. Inherent likelihood and impact · 5. Treatment (avoid / reduce / transfer / accept) with control IDs from artefact 4 · 6. Residual risk vs appetite · 7. Risk owner and acceptance authority (T4: named executive and board committee) · 8. Concentration risk contribution (single-provider dependency) · 9. Review date and triggers |
| ISO 42001 | 6.1.1 risk assessment; 6.1.2 methodology; 6.1.3 SoA and treatment plan; 8.2–8.3 operational risk results; 10.2 corrective action linkage |
| EU AI Act | Art 9 risk-management system (continuous, iterative; known and foreseeable risks; residual risk acceptable) |
| MAS AIRM | s.3 AI Oversight: board approves AI governance approach and risk appetite (3.4); senior management escalates material issues (3.5); s.4 materiality (4.10–4.13); s.5 Pre-Deployment Reviews (5.18–5.21) |
| NIST AI RMF | MAP 5; MEASURE 1; MANAGE 1 (prioritisation), MANAGE 2 (treatment) |
| AI Verify | Safety; Security; Robustness; Accountability |
| Owner | Risk function (register); use-case owner (entry content); accountable executive (acceptance) |
| Sampling expectation | ISO Stage 2: methodology, full register, SoA, and 3–5 entries traced to treatment evidence. MAS: residual materiality shown to sit within appetite before deployment (4.11); concentration risk on key providers considered at onboarding (5.11(c)). EU: Art 9 records showing iteration across the lifecycle |

## Artefact 4 — Control checklist per tier

| Field | Content |
|---|---|
| Purpose | The tier's required controls with owner and evidence pointer for each; the per-use-case slice of the firm's AICM-keyed control library. Doubles as the use-case Statement of Applicability |
| Template outline | 1. Use-case ID, tier, override IDs · 2. Control table: control ID (AICM v1.1 objective) · control statement · applicability (yes / no with justification) · owner · evidence pointer (document, system, log query) · status (designed / implemented / tested) · last test date · mapping columns (ISO A.x; EU Art; MAS s.; NIST subcategory; AI Verify check; OWASP LLM/ASI; ATLAS; EN 18286 Art 17 element) · 3. Agent Gate section (identity, privilege, action classes, tool classes, kill switch) · 4. Gaps and remediation plan with dates · 5. Reviewer sign-off |
| ISO 42001 | 6.1.3 Statement of Applicability; Annex A (all 38 controls as applicable); A.6.1.3 processes for responsible design and development |
| EU AI Act | Art 17 QMS elements (13, (a)–(m)) via EN 18286:2026; Arts 9–15 as applicable |
| MAS AIRM | s.5 AI Life Cycle Controls, sub-headings in document order: Data Management (5.4); Transparency and Explainability (5.5–5.6); Fairness (5.7–5.8); Human Oversight (5.9); Third-Party AI Management (5.10–5.11); Selection (5.12–5.13); Evaluation and Testing (5.14–5.15); Technology and Cybersecurity Risks (5.16); Reproducibility and Auditability (5.17); Pre-Deployment Reviews (5.18–5.22); Post-Deployment Monitoring and Review (5.23–5.24); Change Management (5.25–5.26, with decommissioning at 5.26). Overview 5.1–5.3 covers proportionality and contingency / kill-switch protocols |
| NIST AI RMF | GOVERN 1; MANAGE 1–4 |
| AI Verify | All 11 principles (checklist selects the applicable process checks) |
| Owner | Engagement compliance lead (template); control owners named per row |
| Sampling expectation | ISO Stage 2: SoA with justification for every excluded control; auditor samples 5–10 "implemented" controls and asks for the evidence at the pointer. CSA STAR for AI Level 2: AI-CAIQ answers reconcile to this checklist. EN 18286 presumption only for elements the standard covers |

## Artefact 5 — Test records and release criteria

| Field | Content |
|---|---|
| Purpose | Evidence that the system was tested for what matters in context before release and on change; defines the Responsible Release Criteria that must be met. Covers the IMDA Starter Kit five risks and MAS GenAI test scope |
| Template outline | 1. Release criteria per intended use (pass thresholds; unfit intended uses removed) · 2. Test plan: hallucination / inaccuracy; bias in decision-making (fairness metrics such as equalised-odds difference, FPR / TPR by group); undesirable content; data leakage; adversarial prompts and injection per input channel (with FP / FN rates); robustness to prompt variation (SFC); task adherence, intent resolution, tool-calling accuracy for agents · 3. Test data provenance (own test data expected; off-the-shelf benchmarks rarely sufficient per Global AI Assurance Pilot) · 4. Method (human review, LLM-as-judge with human calibration, red team) · 5. Results, deviations, retest · 6. Independence of validator (peer at T1–T2; independent at T3+; two reviews at T4) · 7. Red-team report (T4; agentic T3+) · 8. Release decision, approver, date · 9. Regression suite and re-test triggers |
| ISO 42001 | A.6.2.4 verification and validation; A.6.2.5 deployment; 7.2 competence of testers; 9.1 monitoring inputs |
| EU AI Act | Art 15 accuracy, robustness, cybersecurity; Art 9(6)–(8) testing; Art 10 data governance for test data; Art 13 instructions reflect tested limits |
| MAS AIRM | s.5 Selection (5.12–5.13: weigh hallucination, opacity, security exposure of newer systems); Evaluation and Testing (5.14: measurable thresholds agreed by business, developers and reviewers; out-of-sample / out-of-time, sensitivity, sub-population, stress and adversarial testing on data representative of the FI's context; 5.15: controls and guardrails in place before deployment, GenAI and agent testing covers key failure modes and whether guardrails work; fn 46 GenAI priorities: hallucinations, toxic or biased content, data leakage, vulnerability to adversarial attacks); formal independent validation for high materiality (5.19); other documented reviews such as peer review for lower materiality (5.20); in-context testing of third-party AI with the FI's own data and compensatory testing where disclosures are inadequate (5.10); red teaming, penetration testing and vulnerability assessment in the pre-production technology review (5.22(b)) |
| NIST AI RMF | MEASURE 2 (evaluated for trustworthiness), MEASURE 3, MEASURE 4; AI 600-1 "pre-deployment testing" consideration; Confabulation, Information Security risks |
| AI Verify | Safety; Robustness; Fairness; Reproducibility; Security |
| Owner | Validation lead (independent of build team at T3+); use-case owner approves release |
| Sampling expectation | ISO Stage 2: test plan, results and release decision for each production system; auditor checks validator independence against the tier. MAS 7 Oct 2028 milestone (s.5): evidence that third-party models were tested in context (5.10) and that high-materiality use cases were independently validated (5.19). SFC: robustness-test records for advice use cases. AI TAP-accredited tester report where used |

## Artefact 6 — Logging and human-oversight design

| Field | Content |
|---|---|
| Purpose | Documents what is logged, for how long, who can override, how a human interrupts, and how automation bias is monitored; includes the override and kill-switch procedure |
| Template outline | 1. Logging schema: instructions / prompt (or hash), retrieved context, model version, tool calls and parameters, results, reviewer identity, human approvals and overrides, timestamps, caller identity, token counts · 2. Retention and tamper-evidence (append-only / WORM / hashing; ≥ 90 days for per-input injection scores; six-month decision reconstruction; 10-year documentation) · 3. Human-oversight design: intervention points, who can override, what information the overseer sees (raw action, reasoning, impact, history), fail-safe timeouts, explanation delivered per decision (T3+) · 4. Automation-bias monitoring: override rate, response time, sampling plan · 5. Kill switch: owner, procedure, credential revocation, test schedule, last test and time-to-halt · 6. Pause and fallback scenarios; offline fallback · 7. Access to logs for the regulator / auditor |
| ISO 42001 | A.6.2.8 recording of event logs; A.6.2.6 operation and monitoring; A.9.2 processes for responsible use; A.3.2 roles |
| EU AI Act | Art 12 record-keeping; Art 14 human oversight (incl. 14(4)(e) interruption / stop); Art 26 deployer oversight by competent natural persons; Art 19 logs kept by deployer |
| MAS AIRM | s.5 Human Oversight (5.9: roles and escalation; competence and authority to intervene; systems designed to escalate to human review on pre-defined conditions; logs of development, deployment, monitoring and incidents; regular review of oversight decisions, incidents and near misses; automation bias and decision fatigue named); Reproducibility and Auditability (5.17: documentation sufficient for an independent party to understand and replicate); 3.6 local management must be able to demonstrate oversight to MAS; agentic: fn 25 inventory attributes (identifiers, accessible tools and systems, components, guardrails), 5.23(a) monitor reasoning processes, actions taken and tools used across AI workflows, 5.23(d) log prompts, responses, model versions and reasoning for GenAI and agents, strict control and logging of access to models, data, pipelines and configurations; kill switch: 5.3 activation protocols tested regularly where a kill switch exists (fn 29), 5.23(b) consider kill switches or override for high materiality |
| NIST AI RMF | GOVERN 1 (human oversight policies); MANAGE 2 (mechanisms to supersede, disengage, deactivate); MEASURE 2 |
| AI Verify | Human Agency & Oversight; Transparency; Reproducibility; Accountability |
| Owner | Platform lead (logging settings); use-case owner (oversight design); kill-switch owner named |
| Sampling expectation | ISO Stage 2: logging settings, retention rules and sample logs for 2–3 systems; kill-switch test records at the tier cadence. EU: Art 12 design and evidence logs are retained for the period required. IMDA agentic: override-rate dashboard. ISACA context: 56% cannot state time-to-halt; this artefact must |

## Artefact 7 — Supplier and LLM-vendor assessment

| Field | Content |
|---|---|
| Purpose | Evidence beyond a vendor logo: residency, retention, training opt-out, audit rights, change-notification rights, subservice-organisation treatment, EU establishment, Code of Practice status, and whether the vendor's SOC 2 scope actually covers AI controls |
| Template outline | 1. Vendor and service (model, endpoint region pinned, deployment route) · 2. Certifications held with scope statements (SOC 2 Type II: does the system description scope model lineage, inference logging, drift monitoring and AI subprocessors? ISO 27001; ISO 42001 with accreditation status; HITRUST AI; STAR for AI level) · 3. Data terms: residency (in-region processing), retention (default vs ZDR applied and verified in writing), abuse-monitoring logs, training opt-out, sharing with model provider on partner platforms · 4. Transfer basis (PDPA s.26, GDPR Ch. V) · 5. Contract rights: audit, change notification, incident notification, indemnity, exit and portability, testing rights (OMB M-25-22 pattern), EU model clauses / Art 25 written agreement · 6. EU establishment and lead authority; GPAI Code of Practice signatory status · 7. Concentration flag · 8. In-context test reference (artefact 5) · 9. Responsibility split (ISO A.10.2; TQA 9561 inclusive / carve-out) · 10. Residual risk and approval |
| ISO 42001 | A.10.2 allocating responsibilities; A.10.3 suppliers; A.10.4 customers; A.4.4 tooling resources; A.7.3 data acquisition |
| EU AI Act | Art 25 responsibilities along the value chain and written agreements; Arts 53–55 GPAI provider duties (vendor side); Art 50 provider marking duties |
| MAS AIRM | s.5 Third-Party AI Management (5.10: contracts give risk-appropriate visibility into AI introduction and subsequent updates; in-context testing with own data; compensatory testing; documented suitability. 5.11: FI retains primary accountability; limit, suspend or replace where residual risk exceeds appetite; (a) independent certifications or external assessments over self-attestations, compensating controls for gaps; (b) supply-chain provenance, data integrity, known vulnerabilities of models, datasets and dependencies incl. open source; (c) concentration risk, direct or indirect; (d) post-deployment change notifications; (e) contingency for provider failure or discontinued support; (f) legal agreements with performance guarantees, data protection, right to audit, notification of AI introduction or updates, FI approval before new AI is incorporated; (g) staff capability; (h) deeper assessment for complex services). Also 1.10(d) over-reliance on dominant providers and 5.16(c) plugins and APIs |
| NIST AI RMF | GOVERN 6 (third-party risk); MAP 4 (third-party components); AI 600-1 Value Chain and Component Integration |
| AI Verify | Accountability; Security; Data Governance |
| Owner | Procurement / vendor risk (assessment); legal (contract terms); engagement lead (in-context test linkage) |
| Sampling expectation | ISO Stage 2: supplier assessments and contract clauses for every model vendor; responsibility matrix. SOC 2 (firm's own report): each LLM vendor documented as a subservice organisation with retention configuration. MAS 7 Oct 2028 milestone: evidence of in-context testing (5.10), independent certifications or external assessments rather than self-attestations (5.11(a)), supply-chain provenance checks (5.11(b)), change notifications received and assessed (5.11(d)), and contract terms per 5.11(f) for material third-party AI. Written ZDR confirmation on file |

## Artefact 8 — Monitoring plan

| Field | Content |
|---|---|
| Purpose | Defines KPIs and KRIs, cadences, drift thresholds, alerting, regression testing and the six-month decision-reconstruction capability; feeds the quarterly system-owner review |
| Template outline | 1. KPIs (task accuracy, resolution, cost) and KRIs (hallucination rate, injection detections, leakage events, override rate, drift metrics, fairness metrics by group, error rate, latency, budget burn, agent action counts) · 2. Thresholds and alert routing · 3. Cadence by tier (yearly / quarterly / monthly; continuous at T4) · 4. Drift detection and regression suite with alert history · 5. Decision reconstruction: versioning of model, prompt, retrieval corpus and tool configuration so any decision in the last six months can be reproduced · 6. Change management and reversible deployments (model change log, rollback proof) · 7. Review meeting: system owner quarterly KPI / KRI review; governance committee for T3+ · 8. Decommissioning criteria |
| ISO 42001 | 9.1 monitoring, measurement, analysis, evaluation; A.6.2.6 operation and monitoring; 9.3 management review input; 10.2 corrective action |
| EU AI Act | Art 72 post-market monitoring; Art 26 deployer monitoring; Art 9 lifecycle iteration |
| MAS AIRM | s.5 Post-Deployment Monitoring and Review (5.23: metrics and thresholds for robustness, stability, data quality and fairness; tiered early-warning thresholds; data, concept and model drift; agent reasoning, actions and tools; incident and issue management with retrain / adjust / redevelop / decommission remedies; accountable person for monitoring; records; staff and user training; 5.24: regular independent re-validation for high materiality and trigger-based review); Change Management (5.25: significance assessment, review and re-approval, version control over code, data, parameters and hyperparameters, traceability and rollback, strict justification for dynamic or automatic updates); decommissioning (5.26) |
| NIST AI RMF | MEASURE 3, MEASURE 4; MANAGE 3, MANAGE 4 |
| AI Verify | Robustness; Safety; Reproducibility; Accountability |
| Owner | System owner (review); platform / MLOps lead (instrumentation) |
| Sampling expectation | ISO Stage 2: monitoring report for the period, KRI dashboard, alert history, minutes of quarterly review. MAS: drift-monitoring evidence (5.23(a)), monitoring and incident records (5.23(d)) and senior-management reporting (3.5). Procurement buyers now ask for human-override logging and six-month reconstruction (CoreLine) |

## Artefact 9 — Incident and user-communication procedure

| Field | Content |
|---|---|
| Purpose | Defines what counts as an AI incident, who is told, in what order, by when, and how affected users and regulators are informed; includes the external concern-reporting channel |
| Template outline | 1. Incident definitions and severity (incl. serious-incident definition, near misses) · 2. Detection sources (monitoring alerts, user reports, A.8.3 external channel) · 3. Escalation path and roles · 4. Regulatory timelines register: EU Art 73 serious-incident reporting; India DPDP breach "without delay, update within 72 hours"; India SGI three-hour takedown (platforms); Vietnam incident reporting; Thailand draft; MAS — the AIRM Guidelines contain no incident-notification-to-MAS clause (5.23(b) is internal reporting, tracking and escalation; 3.5 escalation to senior management and board); incident-notification duties under existing MAS technology-risk notices apply separately; Korea corrective orders; AU OAIC notifiable data breach **[VERIFY per-regime clocks, incl. the MAS TRM notice timing]** · 5. User communication templates (plain language; what happened, what it means, remedy, contest route) · 6. Pause / rollback decision and kill-switch invocation · 7. Post-incident review, corrective action, re-tier trigger · 8. Drill schedule and records |
| ISO 42001 | A.8.3 external reporting (concern channel); A.8.4 communication of incidents; A.3.3 reporting of concerns; 10.2 nonconformity and corrective action |
| EU AI Act | Art 73 serious-incident reporting; Art 26 deployer duty to inform provider / authority; Art 86 right to explanation |
| MAS AIRM | s.5 5.23(b) incident and issue management (report, track, escalate, resolve; user reporting channel) and 5.9(d) review of incidents and near misses; s.3 3.5 senior-management escalation of material issues and board updates. No MAS-notification clause in the Guidelines |
| NIST AI RMF | MANAGE 4 (incident response, communication); GOVERN 4 (culture, reporting); AI 600-1 "incident disclosure" consideration |
| AI Verify | Accountability; Safety; Transparency |
| Owner | Incident manager; legal (reporting-obligations register); communications |
| Sampling expectation | ISO Stage 2: procedure, incident register, notices sent, drill records, public reporting route and intake log. Deloitte APAC found two in five organisations lack an AI incident mechanism; Schellman found 44% with documented AI incident response. Auditor will ask for the last incident or drill end-to-end |

## Artefact 10 — AI-use disclosure and verification statement (for the deliverable itself)

| Field | Content |
|---|---|
| Purpose | Establishes human editorial responsibility for every deliverable, names the models and tools used, and records the verification steps, so the firm meets procurement disclosure expectations and keeps the EU Art 50 editorial-responsibility exemption. The Deloitte Australia refund (fabricated citations; A$440,000 report; supplier review; Senate hearing; new APS clauses within three months) is the control's failure case |
| Template outline | See section 12 (wording). Fields: deliverable ID and version; models and tools used (vendor, model, version, region, retention setting); scope of AI assistance (research, drafting, analysis, translation); human reviewers and sign-off; verification steps performed (citation resolution, quote matching, two-source rule for load-bearing numbers, aggregator trace-back, AI-generated-page rejection); known limitations; contact for corrections |
| ISO 42001 | A.8.2 system documentation and information for users; A.8.5 information for interested parties; A.9.2 responsible use; firm's own 6.1.4 for the research tool |
| EU AI Act | Art 50(4) AI-generated text exemption where under human editorial responsibility; Art 50 provider disclosure (where the firm's tool is user-facing) |
| MAS AIRM | s.5 Transparency and Explainability (5.5–5.6) and Reproducibility and Auditability (5.17), where the deliverable is used by an FI as model documentation |
| NIST AI RMF | GOVERN 4 (transparency, documentation); MAP 1; AI 600-1 Information Integrity |
| AI Verify | Transparency; Accountability; Explainability |
| Owner | Engagement lead (signs); quality / Processing Integrity control owner (verifies) |
| Sampling expectation | Firm's SOC 2: Processing Integrity control sampled per deliverable (citation log with fetched-source hashes). Client procurement: APS RFQ-stage disclosure; California GenAI disclosure language; DTA ClauseBank buyer approval of AI use. Every deliverable carries the statement; no exceptions |

---

## 11. ATRS-style tiered public transparency summary

Modelled on the UK Algorithmic Transparency Recording Standard (mandatory across UK central government since 6 Feb 2024; records required at Beta / Pilot and Production). Gives public-sector and consumer-facing clients a ready artefact for the Australian DTA transparency-statement regime (30 of 92 agencies missed the accountable-official deadline; more than half missed the 28 Feb 2025 statement deadline), Canada AIA publication, Korea procurement preference and Vietnam portal registration. Fields the client cannot publish are marked EXEMPT with the exemption ground, never deleted.

### Tier 1 — Plain-language public record (one page)

| Field | Guidance |
|---|---|
| Name of the tool / use case | As in inventory |
| Organisation and accountable owner | Role, not person, unless the regime requires a name (AU DTA accountable official) |
| What it does, in one paragraph | Audience is a member of the public |
| Why the organisation uses it | Benefit sought; what it replaces (DTA statement standard: "why the agency uses AI") |
| How it is used in a decision or service | Usage pattern and domain classification (DTA standard); whether the public interacts directly or is significantly affected without human review |
| Human involvement | Who reviews, when, and how to reach a human |
| How to contest or ask for an explanation | Route and timeline (Korea meaningful explanation; Colorado 30-day adverse-decision explanation; PIPA human-review right) |
| Status and dates | Pilot / production; first deployed; last reviewed (annual review minimum) |
| Link to Tier 2 | |

### Tier 2 — Technical and governance disclosure

| Section | Content |
|---|---|
| 2.1 Owner and responsibility | Accountable executive; operating team; external suppliers and their role; responsibility split (ISO A.10.2) |
| 2.2 Description and scope | Intended use and exclusions; jurisdictions; user groups; model type and provider; agent capabilities and tool classes if agentic |
| 2.3 Decision and oversight | Where in the process it sits; action classes (autonomous / notify / approve); intervention points; override statistics summary |
| 2.4 Data | Categories; sources; personal-data and special-category flags; residency; retention; transfer basis; training-data position of the vendor |
| 2.5 Risk tier and impact assessment | Tier (T0–T4) and overrides; impact-assessment summary; DPIA / FRIA completed (date); residual risk statement |
| 2.6 Testing and performance | What was tested (five IMDA risks; fairness metrics by group; robustness; red team); headline results; validator independence; retest cadence |
| 2.7 Risks and mitigations | Top risks with mitigations (OWASP / ATLAS IDs may be cited); known limitations |
| 2.8 Monitoring and incidents | KRIs monitored; drift thresholds; incident route; incidents in period (count, severity) |
| 2.9 Compliance overview | Instruments engaged from the regulatory-status map; certifications held with scope; standards aligned (ISO 42001 clause set, NIST functions, AI Verify principles) |
| 2.10 Change history | Versions, material changes, re-assessment dates |

---

## 12. AI-use disclosure and verification statement (wording for every deliverable)

Place on the inside cover or final page of every report, deck, memo and data file. Do not abbreviate below the short form.

### 12.1 Full form (reports and decks)

> **AI-assisted, human-accountable.** This deliverable was prepared with the assistance of artificial-intelligence tools and reviewed, edited and approved by named members of [Firm], who take full editorial and professional responsibility for its content regardless of the use of generative AI.
>
> **Tools and models used.** [Vendor / model / version], accessed via [platform], processed in [region], with [zero-data-retention / 30-day retention / other] confirmed in writing on [date]. [Repeat per tool.] Scope of AI assistance: [research and source retrieval / first-draft text / data analysis / translation / summarisation]. No AI tool executed actions in client systems; all external communications and writes were human-approved.
>
> **Verification performed.** Every citation in this deliverable resolves to a source that was fetched and stored with a content hash on [date range]. Every direct quotation has been string-matched against the stored source. Every load-bearing number has at least two independent upstream sources, or is marked as single-sourced. Claims that could not be verified were removed rather than flagged. Aggregator and secondary sources were traced to the original where available; items that could not be traced are marked [VERIFY]. AI-generated web pages were excluded as sources. Items marked [VERIFY] in this deliverable are stated as unconfirmed and should not be relied on without further confirmation.
>
> **Limitations.** AI tools may produce plausible but incorrect content. The verification steps above reduce but do not eliminate this risk. Information is current as at [date]; regulatory positions in [jurisdictions] change frequently and the regulatory-status map should be refreshed before decisions are taken.
>
> **Reviewed and approved by:** [Name, role] on [date]. **Verification control owner:** [Name, role]. **Corrections:** [contact]. Deliverable ID [ID], version [v].

### 12.2 Short form (memos, data files, slide footers)

> AI-assisted; human-reviewed and approved by [Name, role], [date]. Models: [list]. All citations fetched and verified; unverified items marked [VERIFY]. [Firm] takes full responsibility for this content. Deliverable [ID] v[v].

### 12.3 Procurement-stage disclosure (RFQ / proposal)

> [Firm] intends to use AI tools in delivering this engagement for [research, drafting, analysis]. All outputs will be reviewed and approved by named professionals who remain fully responsible for the work regardless of whether generative AI is used. Models and processing regions: [list]. Client data will be processed [in-region] under [zero-data-retention / stated retention] terms, with no vendor training on client data. [Firm] will provide the AI-use and verification statement with every deliverable and will comply with the buyer's AI-use approval clauses. **[VERIFY]** against the specific panel's clause wording (APS AI Plan / DTA ClauseBank; California GenAI Special Provisions; OMB M-25-22 where US federal).

### 12.4 Why the wording is shaped this way

| Phrase | Reason |
|---|---|
| "take full editorial and professional responsibility ... regardless of the use of generative AI" | Mirrors the APS AI Plan responsibility clause (providers fully responsible regardless of GenAI use) and preserves the EU Art 50 human-editorial-responsibility exemption |
| Names models, regions and retention | PDPA s.26 transfer basis; MAS third-party AI expectations; California disclosure language; Deloitte corrected report named its toolchain only after the fact |
| Citation resolution, quote matching, two-source rule, removal not flagging | Written as a Processing Integrity control objective for the firm's SOC 2; deep-research agents hallucinate 3–13% of URLs and only 24–77% of citations support the attributed fact (earlier research) |
| "No AI tool executed actions in client systems" | Agent Gate lethal-trifecta rule applied to the firm's own tool |
| [VERIFY] convention | Makes the unverified set visible to the reader instead of silently asserting it |

---

## 13. Which artefacts each assessor samples first

| Assessor / milestone | Artefacts sampled first | Notes |
|---|---|---|
| ISO/IEC 42001 Stage 1 (1–2 days) | 1, 2 (procedure), 3 (methodology, SoA), 4 | Design and readiness; scope (4.3), AI policy (5.2), objectives (6.2) also required from the firm-level AIMS |
| ISO/IEC 42001 Stage 2 (1–3 weeks) | 2, 3, 4, 5, 6, 7, 8, 9 traced from 3–5 inventory records in 1 | Operating effectiveness; interviews; internal audit (9.2) and management review (9.3) must have run |
| MAS AIRM 7 Oct 2027 (s.3 AI Oversight; s.4 Key AI Risk Management Systems, Policies and Procedures) | 1, 2 (materiality), 3 (appetite) | Board-approved governance approach and risk appetite (3.4); identification process with control-function ownership (4.2–4.3); inventory complete with 4.7 attributes; inherent and residual materiality per 4.10–4.13 |
| MAS AIRM 7 Oct 2028 (s.5 AI Life Cycle Controls; s.6 AI Capability & Capacity) | 4, 5, 6, 7, 8, 9 | Formal independent validation for high materiality (5.19), in-context third-party testing (5.10), kill-switch protocol tests (5.3), monitoring metrics and drift (5.23), change control (5.25), competence and infrastructure (6.1–6.3) |
| EU notified body / market surveillance (Annex III from 2 Dec 2027) | 2 (FRIA), 3 (Art 9), 4 (Art 17 via EN 18286), 5 (Art 15), 6 (Arts 12, 14), 7 (Art 25), 8 (Art 72), 9 (Art 73) | Technical file per Annex IV assembled from 1, 4, 5, 6 |
| AU DTA (30 Apr 2027) | 1 (register), 2 (impact assessment), 11 (transparency statement) | Residual risk for high-risk cases reported to DTA |
| SFC (advice use cases) | 5 (robustness), 6 (human review), 7 (third-party), 9 (notification of significant change) | Circular 24EC55 |
| CSA STAR for AI Level 2 | 4 (AI-CAIQ reconciliation) plus ISO 42001 certificate | Provisional level built on 42001 + scored AI-CAIQ |
| Firm's own SOC 2 Type II | 7 (subservice organisations), 10 (Processing Integrity), 6 (per-call logging) | TQA 9561 treatment of AI providers |

---

## 14. Open items for v0.2

| Item | Action |
|---|---|
| MAS section numbering and the agentic clauses | **Resolved 2026-10-25** against the MAS PDF. Remaining: response-to-feedback paper para 13.5 qualifier **[VERIFY]**; MAS 2027 agentic consultation to track |
| Per-regime incident clocks in artefact 9 | **[VERIFY]** Vietnam decree thresholds, MAS technology-risk notice timing (not in the AIRM Guidelines), Thailand draft |
| Procurement clause wording (APS / DTA ClauseBank, California SIMM 5305-F) | **[VERIFY]** no source found requiring consultants to disclose AI use in deliverables beyond APS RFQ-stage disclosure; obtain the actual clause text |
| AI Verify process-check IDs per artefact | Map the 106 checks to artefacts once the toolkit summary report is obtained |
| NIST subcategory IDs | Pin to AI RMF 1.0 Tables 1–4; re-map on RMF revision |
