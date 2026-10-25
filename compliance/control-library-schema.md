# Control Library Schema (AICM v1.1-keyed crosswalk)

**Status: v0.1 draft**
**Owner:** Compliance lead (schema); Methodology lead (mappings); Pipeline lead (tool-side rows)
**Applies to:** Every control the firm (a) applies to its own research tool and (b) recommends to clients through the tier gate and agent gate. One library serves both.
**Companion file:** `control-library.csv` (header + 40 populated example rows). This document is the data dictionary and operating procedure for that file.
**Source basis:** CSA AI Controls Matrix v1.1 (247 objectives, 18 domains, June 2026); ISO/IEC 42001:2023 Annex A (38 controls, A.2–A.10); NIST AI RMF 1.0 (4 functions, 19 categories, 72 subcategories) and NIST AI 600-1 (12 GenAI risks); EN 18286:2026 Article 17 QMS elements (a)–(m); AICPA 2017 TSC with 2022 points of focus and TQA 9561; OWASP LLM Top 10 2026 and Top 10 for Agentic Applications (ASI01–ASI10); MITRE ATLAS v2026.09; AI Verify (11 principles, 106 process checks); MAS Guidelines on AI Risk Management (7 Oct 2026); IMDA Model AI Governance Framework for Agentic AI (Jan 2026, updated May 2026); HITRUST AI Security Assessment and AI Risk Management Assessment.

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Compliance lead | Initial schema, column dictionary, status-inheritance rule, resync procedure, vocabulary-layer design; 40 example rows in CSV |
| | | | |

---

## 1. Why one library, and why AICM is the key

| Design choice | Reason | Evidence |
|---|---|---|
| Single library, many mapping columns | One evidence item satisfies every framework it maps to; the same artefact serves ISO 42001 certification, STAR for AI, SOC 2 AI evidence, MAS readiness and EU technical controls | CSA positions AICM as the technical control layer under 42001 and the interim SOC 2 AI baseline; STAR for AI Level 2 = 42001 certificate + scored AI-CAIQ ([CSA](https://cloudsecurityalliance.org/blog/2025/08/20/announcing-the-ai-controls-matrix-and-iso-iec-42001-mapping-and-the-roadmap-to-star-for-ai-42001)) |
| AICM v1.1 as primary key | Largest current control set (247 objectives); CSA already publishes control-by-control mappings to ISO 42001, NIST AI 600-1, BSI AIC4 and the EU AI Act, with ISO 27001/27002 compensating controls | [CSA AICM launch](https://cloudsecurityalliance.org/blog/2025/07/10/introducing-the-csa-ai-controls-matrix-a-comprehensive-framework-for-trustworthy-ai); [CSA SOC 2 gap note](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/) |
| Layered architecture (42001 governance / EN 18286 per-system QMS / AICM technical controls) | CSA's April 2026 analysis identifies five EU AI Act areas 42001 does not fully address; the three layers are complementary, not substitutes | [CSA prEN 18286 vs 42001](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-pren-18286-iso-42001-20260428-cs/) |
| No overlap percentages quoted | Published crosswalks are qualitative; the only numeric SOC 2 to 42001 figure (62%) is from an unreviewed automated tool | [ISO42k](https://www.iso42k.com/nist-ai-rmf-and-iso-42001) |
| Vocabulary kept in its own layer | ATLAS ships monthly, OWASP shipped a new LLM list in Aug 2026, NIST RMF is under revision, MAS/MY/TH/AU texts will add rows within 12 months; re-mapping must be a column change, not a rewrite | [CSA OWASP 2026 note](https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-genai-top10-2026-agent-control-stand/); [NIST AIRC](https://airc.nist.gov/airmf-resources/airmf/0-ai-rmf-1-0) |

---

## 2. Column dictionary

Every column in `control-library.csv`, in order. "Vocabulary" columns hold identifiers from an external framework and are the ones the resync procedure (section 6) touches. "Firm" columns are owned by the firm and survive resyncs.

| # | Column | Type | Allowed values / format | Meaning | Populated by |
|---|---|---|---|---|---|
| 1 | `control_id` | Firm | `CL-nnn`, stable for life | Firm-internal primary key. Never reused, never renumbered. | Compliance lead |
| 2 | `aicm_domain` | Vocabulary | One of AICM v1.1's 18 domain names, or `TBD` with a candidate in brackets | AICM security domain the control sits in. Only domain names confirmed from a CSA source are entered without `TBD`. Confirmed in the research notes: Identity & Access Management; Data Security & Privacy Lifecycle Management; Model Security; and "Supply Chain Management, Transparency & Accountability" (the CSA launch page lists this as one string; the CSV treats it as two domains, `Supply Chain Management` and `Transparency & Accountability`, flagged `[VERIFY]` until the AICM spreadsheet confirms whether it is one domain or two). The remaining domain names were not retrieved from a CSA page and are marked `TBD` pending resync. | Compliance lead |
| 3 | `aicm_objective_id` | Vocabulary | AICM v1.1 objective identifier, or `TBD` | The AICM objective this row is keyed to. All example rows carry `TBD` because objective identifiers were not present in the notes; they are filled at the first resync from the AICM v1.1 spreadsheet. A row may map to more than one objective; split into multiple rows rather than list several IDs. | Compliance lead |
| 4 | `control_title` | Firm | Short imperative phrase | Firm-authored name. | Owner of the row |
| 5 | `control_statement` | Firm | One testable sentence | What must be true. Written so a reviewer can answer pass/fail. | Owner of the row |
| 6 | `iso42001_annexA` | Vocabulary | Annex A control IDs, `;`-separated (see section 3) | ISO/IEC 42001:2023 Annex A reference controls satisfied, wholly or partly. | Methodology lead |
| 7 | `iso42001_clause` | Vocabulary | Clause numbers 4–10, `;`-separated | Management-system clause(s) the control evidences (e.g. 6.1.4 impact assessment, 8.4 operation, 9.1 monitoring). | Methodology lead |
| 8 | `nist_airmf` | Vocabulary | `FUNCTION n.m` subcategory IDs from NIST AI 100-1 Tables 1–4, `;`-separated | NIST AI RMF 1.0 subcategory. The RMF is under revision with no draft published; subcategory IDs are pinned to the 1.0 text and will be re-mapped as a column change when the revision appears ([Vorp Labs](https://vorplabs.com/security-framework-changes/nist-ai-rmf)). | Methodology lead |
| 9 | `nist_600_1_risk` | Vocabulary | One or more of the 12 GAI risks: CBRN; Confabulation; Dangerous/Violent/Hateful Content; Data Privacy; Environmental; Harmful Bias or Homogenization; Human-AI Configuration; Information Integrity; Information Security; Intellectual Property; Obscene/Degrading/Abusive Content; Value Chain and Component Integration | The NIST AI 600-1 generative-AI risk the control mitigates ([CASRAI](https://casrai.org/guides/nist-ai-rmf-generative-ai-profile)). | Methodology lead |
| 10 | `en18286_art17` | Vocabulary | Letters `(a)`–`(m)` | EU AI Act Article 17 QMS element the control contributes to, as structured by EN 18286:2026 (13 elements). Letter labels in the CSV are paraphrased from Article 17(1) and must be checked against the EN 18286 text at first resync (the standard was not fetched). | Compliance lead |
| 11 | `soc2_tsc` | Vocabulary | 2017 TSC criteria: `CC1`–`CC9`, `A1`, `PI1.1`–`PI1.5`, `C1`, `P1`–`P8` | Trust services criterion the control evidences. No AI-specific TSC exist; TQA 9561 (11 Sep 2026) places agents inside the system description and LLM vendors as subservice organisations ([Arthur AI](https://www.arthur.ai/column/soc-2-ai-agents-aicpa-tqa-9561)). Citation-verification rows map to PI1.x by design. | Compliance lead |
| 12 | `owasp_llm2026` | Vocabulary | `LLM01`–`LLM10` (2026 numbering) | OWASP LLM Top 10 2026 ID. Note the renumbering from 2025: LLM03 is now Excessive Agency, LLM08 Hidden Context Exposure, LLM07 Misinformation ([Superwise](https://superwise.ai/learn/owasp-top-10-for-llm-applications/)). Vendor SOC 2/HITRUST mappings built on the 2025 list need translation. | Security lead |
| 13 | `owasp_asi` | Vocabulary | `ASI01`–`ASI10` | OWASP Top 10 for Agentic Applications (Dec 2025) ([Modulos](https://docs.modulos.ai/frameworks/owasp-top-10-agentic)). | Security lead |
| 14 | `mitre_atlas` | Vocabulary | Technique family in words plus technique ID where known (`AML.Tnnnn`) | MITRE ATLAS technique or family the control counters. Agentic IDs confirmed in notes: AML.T0053, T0080 (.000/.001), T0081, T0082, T0083, T0086, T0101, T0109, T0110, T0010.005 ([Speakeasy](https://www.speakeasy.com/blog/mitre-atlas-explained)). ATLAS releases monthly, so this column is pinned to a release tag in `last_synced`. | Security lead |
| 15 | `aiverify_principle` | Vocabulary | One of 11 principles, optionally with process-check group | AI Verify principle (Transparency 15 checks, Explainability 1, Reproducibility 10, Safety 17, Security 14, Robustness 10, Fairness 6, Data Governance 4, Accountability 14, Human Agency & Oversight 9, Inclusive Growth/Societal/Environmental Well-being 6) ([AI Verify Foundation](https://aiverifyfoundation.sg/what-is-ai-verify/)). Individual check IDs are `TBD` until the toolkit's process-check list is loaded. | Methodology lead |
| 16 | `mas_airm_section` | Vocabulary | `s.3 Oversight`, `s.4 Key systems, policies, procedures (incl. inventory, materiality)`, `s.5 Lifecycle controls`, `s.6 Capability and capacity`, or `n/a` | MAS Guidelines on AI Risk Management area. s.3–4 bind FIs from 7 Oct 2027, s.5–6 from 7 Oct 2028 ([Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/10/singapore-mas-issues-guidelines-on-artificial-intelligence-risk-management)). Section numbering rests on practitioner commentary; verify against the MAS PDF at first resync. | Compliance lead |
| 17 | `imda_agentic_dim` | Vocabulary | `D1 Assess and bound risks`, `D2 Meaningful human accountability`, `D3 Technical controls and processes`, `D4 End-user responsibility`, or `n/a` | IMDA agentic framework dimension ([Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2026/04/singapores-agentic-ai-framework-practical-guidance-for-market-entry)). | Methodology lead |
| 18 | `hitrust_ai` | Vocabulary | `AI Sec (ID TBD)`, `AI RM (ID TBD)`, or `n/a` | Whether the control appears in the HITRUST AI Security Assessment (up to 44 requirements, certifiable) or AI Risk Management Assessment (51 controls, non-certifiable) ([HITRUST](https://hitrustalliance.net/assessments-and-certifications/airiskmanagementassessment); [Accorian](https://www.accorian.com/hitrust-and-ai-security/)). Requirement IDs were not in the notes. | Compliance lead |
| 19 | `status_flag` | Derived | `binding` / `voluntary` / `draft` | Inherited from the status map by the rule in section 4. Never hand-edited. | Computed at resync |
| 20 | `sector_overlay` | Vocabulary | `;`-separated from: `FIN-MAS`, `FIN-SFC`, `HEALTH-AIHGle`, `HEALTH-HSA-SaMD`, `PRIVACY-27701`, `AUTO-8800`, `PUBLIC-AU-DTA`, `none` | Sector overlays that tighten or extend the control (ISO/IEC 27701:2025 automated-decision expectations; SFC and MAS for finance; AIHGle 2.0 and HSA SaMD for health; ISO/PAS 8800 for automotive) ([Linford & Co](https://linfordco.com/?p=23924); [SGS](https://www.sgs.com/news/2025/04/safeguards-04625-introducing-iso-pas-8800-functional-safety-for-ai-in-road-vehicles)). | Compliance lead |
| 21 | `evidence_artefact` | Firm | `EP-1`…`EP-10` from the 10-artefact pack (section 5), optionally with a sub-item | Which artefact in the client evidence pack (or the firm's own equivalent) proves the control. | Owner of the row |
| 22 | `test_method` | Firm | Free text, starting with one of: `inspect`, `reperform`, `observe`, `sample`, `automated` | How the control is tested, in SOC 2 test-procedure vocabulary. | Owner of the row |
| 23 | `owner` | Firm | Role name, not person | Accountable role for operating the control and producing evidence. | Compliance lead |
| 24 | `applies_to` | Firm | `tool` / `client-agentic` / `both` | Whether the row governs the firm's own research tool, a client agentic use case, or both. | Owner of the row |
| 25 | `last_synced` | Derived | `YYYY-MM-DD` plus release tags, e.g. `ATLAS v2026.09; OWASP LLM 2026; AICM v1.1` | Date and vocabulary versions the row was last checked against. | Computed at resync |

Conventions used in the CSV: `TBD` means the identifier exists in the external framework but was not available in the research notes and must not be guessed; `[VERIFY]` means a value is entered from secondary commentary and must be checked against the primary text; `n/a` means the framework has no applicable element.

---

## 3. ISO/IEC 42001:2023 Annex A reference controls (all 38)

Nine areas, A.2–A.10; counts per area A.2 = 3, A.3 = 2, A.4 = 5, A.5 = 4, A.6 = 9, A.7 = 5, A.8 = 4, A.9 = 3, A.10 = 3 ([iso42k.com](https://www.iso42k.com/); full list per [Modulos](https://docs.modulos.ai/frameworks/iso-42001/annexes-a-d.html); evidence suggestions per [GAICC](https://gaicc.org/blog/iso-42001-annex-a-controls/) and [Advisera](https://advisera.com/articles/iso-42001-mandatory-documents/)). Annex B gives implementation guidance per control; Annex C lists 11 objectives and 7 risk sources (informative); Annex D covers integration with ISO 27001, 27701 and 9001.

| Area | Control | Title | Typical evidence (firm convention) |
|---|---|---|---|
| A.2 Policies related to AI | A.2.2 | AI policy | Approved AI policy document |
| | A.2.3 | Alignment with other organizational policies | Policy cross-reference matrix (security, privacy, quality) |
| | A.2.4 | Review of the AI policy | Review minutes, at least annual |
| A.3 Internal organization | A.3.2 | AI roles and responsibilities | RACI; named accountable executive |
| | A.3.3 | Reporting of concerns | Concern-reporting channel and intake log |
| A.4 Resources for AI systems | A.4.2 | Resource documentation | Resource register |
| | A.4.3 | Data resources | Data inventory per AI system |
| | A.4.4 | Tooling resources | Tool and model inventory (incl. agent tool allowlists) |
| | A.4.5 | System and computing resources | Infrastructure and endpoint register (incl. region pinning) |
| | A.4.6 | Human resources | Competence records |
| A.5 Assessing impacts of AI systems | A.5.2 | AI system impact assessment process | Approved procedure with triggers and thresholds |
| | A.5.3 | Documentation of AI system impact assessments | Completed assessments with retention rule |
| | A.5.4 | Assessing AI system impact on individuals or groups of individuals | Individual-impact section of assessment |
| | A.5.5 | Assessing societal impacts of AI systems | Societal-impact section of assessment |
| A.6 AI system life cycle | A.6.1.2 | Objectives for responsible development of AI system | Documented development objectives |
| | A.6.1.3 | Processes for responsible design and development of AI system | Design and development procedure |
| | A.6.2.2 | AI system requirements and specification | Requirements specification |
| | A.6.2.3 | Documentation of AI system design and development | Design records, model/system cards |
| | A.6.2.4 | AI system verification and validation | Test records and release criteria |
| | A.6.2.5 | AI system deployment | Deployment plan, rollback proof |
| | A.6.2.6 | AI system operation and monitoring | Monitoring reports, KRIs |
| | A.6.2.7 | AI system technical documentation | Technical file |
| | A.6.2.8 | AI system recording of event logs | Logging settings, retention rules, sample logs |
| A.7 Data for AI systems | A.7.2 | Data for development and enhancement of AI system | Data management procedure |
| | A.7.3 | Acquisition of data | Acquisition records and rights basis |
| | A.7.4 | Quality of data for AI systems | Quality criteria and checks |
| | A.7.5 | Data provenance | Lineage records |
| | A.7.6 | Data preparation | Preparation and transformation records |
| A.8 Information for interested parties | A.8.2 | System documentation and information for users | User documentation, disclosures |
| | A.8.3 | External reporting | Public reporting route and intake log |
| | A.8.4 | Communication of incidents | Incident communication plan |
| | A.8.5 | Information for interested parties | Stakeholder information records |
| A.9 Use of AI systems | A.9.2 | Processes for responsible use of AI system | Acceptable-use and operating procedures |
| | A.9.3 | Objectives for responsible use of AI system | Documented use objectives |
| | A.9.4 | Intended use of the AI system | Intended-use statement and scope limits |
| A.10 Third-party and customer relationships | A.10.2 | Allocating responsibilities | Responsibility split (supplier/customer/firm) |
| | A.10.3 | Suppliers | Supplier assessments and contract clauses |
| | A.10.4 | Customers | Customer information and obligations |

Mandatory clause-level documents that rows may also evidence: 4.3 scope; 5.2 AI policy; 6.1.1–6.1.2 risk register and methodology; 6.1.3 Statement of Applicability; 6.1.4 AI system impact assessment; 6.2 objectives; 7.2 competence; 9.1 monitoring; 9.2 internal audit; 9.3 management review; 10.2 corrective action ([Advisera](https://advisera.com/articles/iso-42001-mandatory-documents/)).

---

## 4. Status-inheritance rule

`status_flag` is computed, not typed. Each mapping column carries an instrument status from the status map in the compliance-layer report (binding / dated-but-not-yet-binding / voluntary / draft). The rule:

| Step | Rule |
|---|---|
| 1 | Start at `voluntary`. |
| 2 | If any mapped instrument is **binding** for the client's jurisdiction and sector in scope (e.g. MAS AIRM for a Singapore FI; APP 1.7–1.9 for AU consequential decisions; EU AI Act Art 50 for EU-exposed deployments; PDPA where personal data is present), set `binding` and record the binding instrument and date in `test_method` notes. A dated-but-not-yet-binding instrument sets `binding` only if its date falls inside the client's roadmap horizon (12 months default). |
| 3 | If the **only** mappings are to draft instruments (ISO/IEC 42003, 42007, 42105, 27091; NIST IR 8596; COSIS overlays; NIST Agent Standards Initiative; OWASP Agent Control Standard v0.1; Malaysian and Thai bills; Australian Standards for AI), set `draft`. Draft rows are annotations: they appear in deliverables as direction-of-travel and are never scored in the maturity instrument or counted in gate pass/fail. |
| 4 | A row that mixes voluntary and draft mappings is `voluntary`; the draft mappings stay in their columns with a `[draft]` suffix so they are visible but unscored. |
| 5 | Weight in scoring follows the flag: binding = hard gate; voluntary = scoring rubric and evidence template; draft = not scored. |
| 6 | For the firm's own tool, jurisdiction is Singapore and sector is professional services; PDPA rows are therefore `binding` and MAS rows `voluntary` unless the engagement is for an FI client, in which case the client-side copy of the row inherits `binding`. |

Instrument statuses as of 25 Oct 2026 (abbreviated from the status map): binding today — PDPA and PDPC AI guidelines; Korea AI Basic Act; Vietnam Law 134/2025; China labelling, CSL, anthropomorphic measures; India IT Rules SGI amendment; EU AI Act Art 50 and GPAI; US state ADMT laws by state. Dated — MAS AIRM (7 Oct 2027 / 7 Oct 2028); AU Privacy Act APP 1.7–1.9 (10 Dec 2026); AU DTA policy (30 Apr 2027); India DPDP penalties (13 May 2027); EU Annex III (2 Dec 2027), Annex I (2 Aug 2028); Colorado (1 Jan 2027). Voluntary — ISO/IEC 42001, 42005, 42006, 27090, 27701:2025; NIST AI RMF 1.0 and AI 600-1; OWASP LLM 2026 and ASI; MITRE ATLAS; CSA AICM; AI Verify; IMDA frameworks; HITRUST; SOC 2. Draft — as listed in step 3.

---

## 5. Evidence artefact codes (the 10-artefact pack)

| Code | Artefact | Satisfies (abridged) |
|---|---|---|
| EP-1 | AI inventory record per use case (MAS fields plus tier) | MAS AIRM s.4; ISO A.4, A.6.2.7; AU DTA register |
| EP-2 | Impact assessment (Canada AIA-style score; ISO A.5 individual and societal; DPIA; FRIA where EU-exposed) | ISO 6.1.4 / 42005; PDPA; EU Art 27 |
| EP-3 | Risk register entry with tier, treatment, residual risk | ISO 6.1; MAS risk appetite; EU Art 9 |
| EP-4 | Control checklist per tier with owner and evidence pointer | ISO SoA; EN 18286 Art 17; AICM objectives |
| EP-5 | Test records (fairness, robustness, hallucination, data leakage, red-team) and release criteria | ISO A.6.2.4; MAS testing; IMDA Starter Kit; EU Art 15 |
| EP-6 | Logging and human-oversight design incl. override and kill-switch procedure | EU Arts 12, 14; ISO A.6.2.8; IMDA agentic; MAS agentic |
| EP-7 | Supplier and LLM-vendor assessment with residency, retention and audit-rights terms | ISO A.10; SOC 2 subservice per TQA 9561; MAS third-party; EU Art 25 |
| EP-8 | Monitoring plan with KPI/KRI cadence, drift thresholds, decision reconstruction | ISO 9.1; MAS monitoring; EU post-market |
| EP-9 | Incident and user-communication procedure with timelines | ISO A.8.4; EU Art 73; VN/TH incident duties |
| EP-10 | AI-use disclosure and verification statement for the deliverable itself | APS AI Plan clauses; EU Art 50 editorial-responsibility exemption; firm's ISO 42001 A.8 |

For the firm's own tool, EP-5 is the verification-pipeline test log, EP-6 is the pipeline logging schema, EP-7 is the subservice-organisation register, and EP-10 is the disclosure block on every deliverable (see `../pipeline/verification-pipeline-spec.md`).

---

## 6. Quarterly resync procedure

Triggered on the first working day of each quarter, or out of cycle when any of the watch-list events below fires. Target effort: one working day for the vocabulary pass, half a day for review.

| Step | Action | Output |
|---|---|---|
| R1 | Snapshot the current CSV with a git tag `control-library-vYYYY.QN-pre`. | Immutable prior version |
| R2 | Pull the current releases of each vocabulary source and record release tags: AICM (CSA), ISO 42001 (no amendment registered; check ISO catalogue), NIST AI RMF (check AIRC banner for revision), AI 600-1, EN 18286 (CEN/OJ citation), OWASP LLM and ASI lists, ATLAS (monthly; take latest tag), AI Verify toolkit, MAS AIRM (final PDF and any FAQs), IMDA agentic framework version, HITRUST CSF version. | Release-tag table appended to this file's change log |
| R3 | Diff each vocabulary against the values in the corresponding column. For renamed or renumbered IDs (e.g. OWASP 2025 to 2026 renumbering), apply a column-wide substitution; for new IDs, add candidate rows with `status_flag` per section 4; for retired IDs, keep the row and append `[retired <tag>]` so historical evidence packs remain traceable. | Column diffs; new candidate rows |
| R4 | Recompute `status_flag` for every row against the refreshed status map (section 4). Binding dates that have passed move dated instruments to binding. | Updated flags |
| R5 | Clear `TBD` cells where the source now supplies the ID (AICM objective IDs, AI Verify check IDs, HITRUST requirement IDs, EN 18286 element labels). Record any `TBD` that remains and why. | TBD burn-down list |
| R6 | Re-run the mapping consistency checks: every row has at least one `evidence_artefact`; every `binding` row has an `owner` and a `test_method`; no row maps a 2025 OWASP ID; every `mitre_atlas` ID exists in the tagged ATLAS release. | Check log |
| R7 | Methodology lead and Security lead review the diff; Compliance lead approves; tag `control-library-vYYYY.QN`. Update `last_synced` on every touched row. | Approved version |
| R8 | Propagate: regenerate the tier-gate control checklists (EP-4 templates) and the maturity-instrument governance items that cite library rows; notify engagement leads of rows whose flag changed. | Downstream updates |

Watch-list events that trigger an out-of-cycle resync: publication of the revised NIST AI RMF; any ISO/IEC 42001 amendment; a new OWASP LLM or ASI list; ISO/IEC 42105 or 27091 reaching published status; MAS issuing FAQs or amendments; Malaysia AI Governance Bill or Thailand AI Act passing; Australian Standards for AI bill tabled; AICM v1.2 or later.

---

## 7. Vocabulary-layer design

The library is two layers in one file so that external churn never forces a rewrite of firm content.

| Layer | Columns | Change discipline |
|---|---|---|
| Firm layer | `control_id`, `control_title`, `control_statement`, `evidence_artefact`, `test_method`, `owner`, `applies_to` | Changed only by a versioned edit with a change-log entry. Stable across resyncs. These are the firm's IP. |
| Vocabulary layer | `aicm_domain`, `aicm_objective_id`, `iso42001_annexA`, `iso42001_clause`, `nist_airmf`, `nist_600_1_risk`, `en18286_art17`, `soc2_tsc`, `owasp_llm2026`, `owasp_asi`, `mitre_atlas`, `aiverify_principle`, `mas_airm_section`, `imda_agentic_dim`, `hitrust_ai`, `sector_overlay` | Each column is pinned to a named release in `last_synced`. A framework revision is handled as a column-wide substitution or a new column (e.g. `owasp_llm2027` added alongside `owasp_llm2026` for one cycle, then the old column retired). Rows are never deleted because of vocabulary change. |
| Derived layer | `status_flag`, `last_synced` | Computed by the resync procedure; hand edits are rejected at review. |

Rules that keep the layers clean:

| Rule | Why |
|---|---|
| One row = one firm control, many external IDs | The firm control is the unit the reviewer tests; external IDs are labels on it. Splitting by AICM objective where needed keeps the primary key unique. |
| External IDs are stored verbatim, never paraphrased | Allows mechanical diffing at resync. |
| Framework-specific wording lives in the vocabulary columns, never in `control_statement` | Prevents a NIST or OWASP rename from invalidating a statement the client has already received. |
| Each vocabulary column records its own release tag | Columns advance independently (ATLAS monthly, ISO rarely). |
| Historical tags are kept, not overwritten | An evidence pack delivered under `ATLAS v2026.09` must remain reproducible after the next release. |

---

## 8. Open items for v0.2

| # | Item | Blocking? |
|---|---|---|
| 1 | Load AICM v1.1 spreadsheet; fill all 18 domain names and objective IDs; split rows mapping to multiple objectives | Yes, before G0 |
| 2 | Verify MAS AIRM section numbering and EN 18286 Article 17 element labels against primary texts | Yes, before first FI engagement |
| 3 | Load AI Verify process-check IDs; HITRUST requirement IDs | No |
| 4 | Confirm NIST subcategory IDs against NIST AI 100-1 Tables 1–4 and re-check once the revised RMF is published | No |
| 5 | Expand from 40 example rows to full coverage (target: every AICM objective relevant to a web-research agent and to T2–T4 client agentic use cases) | Yes, before G1 |
