# Data Processing Addendum — Outline (PDPA-aligned)

**Status: v0.1 draft**
**Owner:** Founder + counsel (Entity & legal workstream); Compliance lead (subservice table and security measures)
**Nature of this document:** **Outline for counsel. Not a contract and not legal advice.** It lists what Schedule 2 of the engagement letter must contain, in the order counsel is likely to want it, with the operating facts PLUMB can already supply. Statutory timelines and control IDs marked **[VERIFY]** have not been checked against primary text in this repository.
**Governing statute:** Personal Data Protection Act 2012 (Singapore), including the s.26 transfer limitation; PDPC advisory guidelines on AI systems (Mar 2024; GenAI guidelines Jul 2026) as interpretive guidance (`compliance/regulatory-status-map.md` rows 24–25). Penalty cap: greater of S$1 million or 10% of local annual turnover ([CMS](https://cms.law/en/sgp/legal-updates/Organizations-face-risk-of-higher-financial-penalties-for-breaches-of-the-PDPA-from-1-October-2022)).
**Related:** `engagement-letter-clauses.md` §6; `pipeline/verification-pipeline-spec.md` §5 (vendor configuration rules V1–V6); `compliance/evidence-pack-templates.md` artefact 7 (third-party register).

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Founder | Initial outline from compliance-layer report, pipeline vendor rules and GA-gate criteria |

---

## 1. Roles

| Party | PDPA role | Why | Notes for counsel |
|---|---|---|---|
| Client | Organisation (controller-equivalent) for Client personal data supplied under the charter (D1–D12) | Determines purposes; the data is the Client's | Client warrants it has the basis to supply the data for the engagement purposes |
| PLUMB | Data intermediary for Client personal data | Processes on behalf of and for the purposes of the Client | Protection and retention-limitation obligations apply directly to intermediaries under PDPA **[VERIFY exact sections]** |
| PLUMB | Organisation in its own right for: public-source research corpus; interview recordings and transcripts it collects; respondent data from the maturity instrument; benchmark database | PLUMB determines purposes and methods for these | Needs its own consent/notification for interviewees and instrument respondents; the public-source corpus is not Client personal data but may contain personal data of named executives |
| LLM, cloud and data vendors | Sub-intermediaries (sub-processors) to PLUMB | Process on PLUMB's instructions | Each recorded as a subservice organisation (TQA 9561 — [Arthur AI](https://www.arthur.ai/column/soc-2-ai-agents-aicpa-tqa-9561)) |

---

## 2. Purposes

| Purpose | Data involved | Permitted processing | Not permitted |
|---|---|---|---|
| P1 Perform the Services per the charter | Client data D1–D12; interview data; instrument responses | Storage, analysis, AI-assisted research and drafting within the configured routes | Any use outside the engagement |
| P2 Verification evidence | Hashes and stored copies of fetched public sources; verification logs | Retention as quality-system evidence | Retention of Client raw personal data beyond section 7 |
| P3 Benchmark database | Anonymised scores and attributes only | Aggregation; percentile output | Any identifiable Client data; any raw interview or instrument free-text |
| P4 Quality and attestation | Engagement file; per-inference logs (prompt hash and redacted copy) | Internal audit; SOC 2 / ISO auditor sampling | Disclosure of Client identity to auditors without NDA |
| P5 Legal and regulatory | As required | Compliance with law, regulator requests | |

---

## 3. Categories of data and data subjects

| Category | Examples | Data subjects | Sensitivity (tier table C2) | Default AI-route permission |
|---|---|---|---|---|
| Business data (non-personal) | P&L by segment, KPI extracts, strategy documents | n/a | Confidential business data (C2 level 2) | Yes, Singapore endpoint, ZDR confirmed |
| Employee personal data | Org chart, roster, HRIS extracts (name, role, function) | Client employees | Personal data, low volume | Yes, minimised (roles not names where possible) |
| Instrument respondent data | 48-item responses, role, free text | Client leaders (10–30) | Personal data; opinions | Analysis only; free text not sent to any LLM route without redaction |
| Interview data | Recordings, transcripts, notes | Client executives (6–10); external customers (8–12) | Personal data; may include commercially sensitive statements about third parties | Transcription route must be listed in section 5; recordings never leave the Singapore store |
| Customer / counterparty data | Win/loss records, customer lists | Client's customers' contacts | Personal data; may be at scale | Contact lists used only for interview scheduling; not sent to LLM routes |
| Public-source corpus | Annual reports, filings, press, job postings, reviews | Named executives, reviewers | Publicly available; PDPA publicly-available exception **[VERIFY scope]** | Yes |
| Special-category data | Health, financial, biometric, children's | Not requested | T3 override OV-11 if present | **Not permitted**; engagement lead must refuse receipt and record in decision log |

---

## 4. Subservice processors (sub-intermediaries)

Register maintained per `pipeline/verification-pipeline-spec.md` V3 and evidence-pack artefact 7. **No row may be used for Client data until the "ZDR / retention confirmed in writing" column has a date.** Open items before G1: Bedrock Singapore availability for Claude not verified; Anthropic direct-API residency region list not retrieved.

| Vendor | Service / model | Processing region (pinned) | Retention setting | ZDR status | Confirmed in writing (date) | Retention test (date) | Certifications held | Training on customer data | PDPA s.26 basis if non-SG | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenAI | API project, [model] | Singapore (data residency available since 25 Nov 2025; in-region handling; no storage at rest for API requests) | No storage at rest for API requests (per vendor) | Equivalent per vendor statement; **[VERIFY]** in project settings | [ ] | [ ] | SOC 2 Type 2; ISO 27001/27017/27018/27701; ISO 42001 not listed | No by default | n/a if SG pinned | [OpenAI](https://openai.com/index/expanding-data-residency-access-to-business-customers-worldwide/) |
| Anthropic (direct API) | [Claude model] | **[VERIFY]** residency region list not retrieved | Default API retention 30 days | ZDR requires application and approval; customers must verify it applied | [ ] | [ ] | SOC 2 Type I and II; ISO 27001:2022; ISO/IEC 42001:2023 | No (commercial terms) | **[VERIFY]** | [Anthropic](https://support.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained); [The Register](https://www.theregister.com/ai-and-ml/2026/09/02/anthropic-promises-zero-data-retention-but-customers-must-check-it-worked/5293789) |
| Google Cloud (Vertex AI) | [Gemini model] / partner Claude models | asia-southeast1 (global endpoints carry no residency guarantee and are default unless pinned) | Interactions API stores by default unless `store=false`; abuse-monitoring logs up to 90 days on standard tier; partner Claude models retain prompts up to 30 days with sharing to Anthropic | Configurable; **[VERIFY]** per project | [ ] | [ ] | **[VERIFY]** | **[VERIFY]** | n/a if pinned | [IntuitionLabs](https://intuitionlabs.ai/insights/guides/zero-data-retention-gemini-vertex-ai-life-sciences) |
| AWS Bedrock | [Claude model] | Singapore availability **[VERIFY]** | **[VERIFY]** | **[VERIFY]** | [ ] | [ ] | **[VERIFY]** | **[VERIFY]** | **[VERIFY]** | Open item in pipeline spec |
| [Transcription provider] | Interview transcription | **[VERIFY]** | | | [ ] | [ ] | | | | |
| [Survey platform] | Instrument delivery | **[VERIFY]** | | | [ ] | [ ] | | | | |
| [Cloud storage / run store] | Engagement file, evidence store, hash-chained logs | Singapore | Per section 7 | n/a | [ ] | [ ] | | n/a | n/a | |
| [Data vendors: registries, exchange portals, Crunchbase, Statista, BuiltWith] | Public-source retrieval | Various | n/a (no Client data sent) | n/a | n/a | n/a | | n/a | n/a | No Client data flows to these |

Row rules: SOC 2 credit only where the vendor's system description scopes model lineage, inference logging, drift monitoring and AI subprocessors ([CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/)); for EU-exposed work prefer GPAI Code of Practice signatories (V6).

---

## 5. Cross-border transfer basis (PDPA s.26)

| Route | Default | If non-Singapore | Documentation | Source |
|---|---|---|---|---|
| LLM inference | Singapore-pinned endpoints; global endpoints disabled at project level; `region_asserted` logged per inference (V1) | Transfer-limitation basis under s.26 and PDP Regulations Part 3 (comparable protection: contractual clauses / binding corporate rules / certification / consent) documented and approved **before** use (V4) | Transfer-basis memo per route, held in engagement file and subservice register | [DeepInspect](https://www.deepinspect.ai/blog/singapore-pdpa-ai-controls-mapping); pipeline spec V1, V4 |
| Storage | Singapore | Not permitted for Client raw data | | |
| Transcription / survey SaaS | Singapore where available | s.26 basis memo; Client notified in advance | | |
| Client-side transfers (Client sends data from overseas affiliates) | Client's responsibility | Client warrants its own transfer basis | Warranty in DPA | |
| Reconciliation | Route inventory reconciled to endpoint configuration quarterly (T-14 blocked-call test; T-15 retention probe) | | Test records | pipeline spec §6, §7 |

---

## 6. Security measures (mapped to SOC 2 TSC and ISO/IEC 27001:2022)

Control IDs below are indicative; **[VERIFY]** exact TSC points of focus and 27001:2022 Annex A numbering against the standards when the compliance platform is configured. The firm's attestation sequencing is SOC 2 and ISO 27001 first, ISO 42001 second (compliance-layer report).

| # | Measure | Operating fact | SOC 2 TSC (indicative) | ISO 27001:2022 Annex A (indicative) | Also satisfies |
|---|---|---|---|---|---|
| S1 | Logical access: named accounts, MFA, least privilege, role separation (pipeline operator vs independent reviewer) | Reviewer cannot modify pipeline runs; write-only credentials for log store | CC6.1–CC6.3 | A.5.15–A.5.18, A.8.2–A.8.5 | ISO 42001 A.9.2 responsible use |
| S2 | Encryption in transit and at rest; Singapore-region key management | Run store encrypted; raw prompts only in encrypted run store | CC6.1, CC6.6, CC6.7 | A.8.24 | |
| S3 | Endpoint pinning and region assertion per inference | V1; blocked-call test T-14 | CC6.6, CC7.1 | A.5.23, A.8.20 | PDPA s.26 |
| S4 | Vendor retention configuration verified in writing and tested | V2; retention probe T-15 quarterly | CC9.2 (vendor management) | A.5.19–A.5.22 | TQA 9561 subservice treatment |
| S5 | Per-inference logging: model version, prompt hash, tool calls, outcome; redacted prompt copy | C12; logging failure fails the run | CC7.2, PI1.4 | A.8.15 | CSA SOC 2 AI gap note; [MLflow](https://mlflow.org/articles/soc-2-for-llm-apps/) |
| S6 | Tamper-evident, hash-chained, append-only log store; quarterly integrity verification | C13; ≥ 90 days input scores and inference logs; 6 months decision-reconstruction material | CC7.2, PI1.5 | A.8.15, A.8.17 | |
| S7 | Agent tool permissioning and reversibility classes: read autonomous, draft notify, write/send approve; connector allowlist | Agent gate applied to firm's own tool | CC6.3, CC8.1 | A.8.9, A.8.32 | OWASP LLM01; IMDA agentic framework |
| S8 | Prompt-injection controls on every input channel (retrieved chunks, tool outputs, documents, OCR) with logged per-input scores | Pipeline spec input-side controls | CC7.1, CC7.2 | A.8.8, A.8.16 | OWASP LLM01 |
| S9 | Secrets management with rotation | | CC6.1 | A.8.24, A.5.17 | |
| S10 | Change management for models and pipeline; reversible deployments; tested rollback | Model registry with immutable history | CC8.1 | A.8.32, A.8.31 | ISO 42001 A.6.2 |
| S11 | Data minimisation and redaction before any LLM route (roles not names; free text redacted) | Section 3 route permissions | CC6.5, P-series if privacy criteria in scope | A.5.34, A.8.10–A.8.12 | PDPA protection obligation |
| S12 | Secure deletion and return at end of retention | Section 7 | CC6.5 | A.8.10 | PDPA retention limitation |
| S13 | Incident response with drill records | Evidence-pack artefact 9 procedure applied to the firm | CC7.3–CC7.5 | A.5.24–A.5.28 | Section 8 below |
| S14 | Personnel confidentiality, screening and training (incl. AI-use and verification policy) | | CC1.4, CC1.5 | A.6.1–A.6.3, A.6.6 | ISO 42001 7.2–7.3 |
| S15 | Independent reviewer sampling as Processing Integrity control | PI-CV control objective; ≥ 30 claims per deliverable | PI1.1–PI1.3 | n/a | Verification pipeline spec |

---

## 7. Retention and deletion

| Data | Retention | Deletion / return | Basis |
|---|---|---|---|
| Client raw data (D1–D12) | Until final Deliverable + [90] days | Secure deletion; certificate on request; return on request before deletion | PDPA retention limitation; engagement letter 6.5 |
| Interview recordings | Until QA gate 3 sign-off + [30] days | Deleted; transcript retained per next row | Quote verification needs the recording only until gate 3 |
| Interview transcripts (verified) | Engagement-file period | Part of engagement file; personal names pseudonymised at close | Evidence for quotations in Deliverables |
| Instrument responses (individual) | Until scorecard issue + [90] days | Aggregated; individual responses deleted | Leadership-variance exhibit uses aggregates |
| Deliverables, decision log, QA records, source hashes, verification logs (engagement file) | [10] years working value **[VERIFY]** | Deleted at end of period | Quality system (ISQM-style file); attestation sampling; AI documentation retention default of 10 years in evidence-pack templates |
| Per-inference logs | ≥ 90 days input scores; 6 months decision-reconstruction material; longer where part of engagement file | Sealed segments expire by schedule | Pipeline C13 |
| Vendor-side retention | Per section 4 (ZDR or stated period) | Vendor-controlled; tested | V2 |
| Benchmark DB entries | Indefinite, anonymised | Withdrawal for future use on notice; aggregates not unwound | Engagement letter 8 |

---

## 8. Breach notification

| Step | Requirement | Owner | Clock | Status |
|---|---|---|---|---|
| Detect and contain | Any unauthorised access, loss, disclosure or integrity failure (incl. log-chain integrity failure, mis-routed inference, vendor retention deviation) | Compliance lead | Immediate | Standing (EP-9) |
| Notify Client (as data intermediary) | PLUMB notifies the Client without undue delay so the Client can assess notifiability; working value: within [24] hours of becoming aware | Engagement lead | [24 h] working value | Counsel to set |
| Client assessment | Client (as organisation) assesses whether the breach is notifiable under the PDPA mandatory breach-notification regime (significant harm or significant scale thresholds) | Client, with PLUMB's information | PDPC assessment window **[VERIFY: understood to be 30 days from awareness]** | **[VERIFY]** against PDPC guidance |
| Notify PDPC | Client notifies PDPC where notifiable | Client | **[VERIFY: understood to be 3 calendar days after determining notifiability]** | **[VERIFY]** |
| Notify affected individuals | Where the breach is likely to result in significant harm | Client | On or after PDPC notification **[VERIFY]** | **[VERIFY]** |
| PLUMB's own breaches (interview, respondent, corpus data where PLUMB is the organisation) | PLUMB assesses and notifies PDPC and individuals directly | Compliance lead | Same clocks | |
| Vendor incidents | Each subservice vendor's contractual incident-notification period recorded in the register (artefact 7, item 5) | Compliance lead | Per vendor **[VERIFY]** | |
| Record | Incident register entry; post-incident review; re-tier trigger; drill records | Compliance lead | Within [10] working days | EP-9 |

Other regimes that may apply where the Client is outside Singapore (AU OAIC notifiable data breach; India DPDP "without delay, update within 72 hours"; EU Art 73 for AI incidents) are listed in `compliance/evidence-pack-templates.md` artefact 9 and **[VERIFY per-regime clocks]** there.

---

## 9. Audit rights

| Right | Scope | Frequency | Conditions |
|---|---|---|---|
| Client information right | Subservice register extract; retention test records; region-assertion logs for the engagement; security-measures summary; SOC 2 report and ISO certificates when held | On request, once per engagement and on incident | NDA; no Client access to other clients' data |
| Client audit | On-site or remote audit of PLUMB's controls relevant to the Client's data | Once per 12 months, or after a breach | [30] days' notice; Client bears cost unless material non-compliance found; auditor bound by confidentiality |
| Reliance on third-party reports | Client accepts PLUMB's SOC 2 Type II report and ISO 27001 / 42001 certificates (when issued) in lieu of audit for the matters they cover | Annual | Report provided under NDA |
| Vendor audit | PLUMB relies on vendor SOC 2 / ISO reports and retention tests; Client has no direct audit right against vendors | | Flow-down of vendor terms limited to what vendors grant |
| Regulator access | PLUMB cooperates with PDPC and the Client's sector regulator (e.g. MAS) requests relating to the Client's data | As required | |

---

## 10. Sub-processor change notice

| Event | Notice | Client right | Record |
|---|---|---|---|
| Add or replace an LLM, transcription, survey or storage vendor | [10] working days' written notice with updated register row (region, retention, ZDR status, certifications, s.26 basis) | Object on reasonable data-protection grounds within the notice period; if unresolved, Client may terminate the affected Services without penalty for the unperformed part | Subservice register version; decision log |
| Model version change within a listed vendor | Notice in the next engagement update; retention re-tested (V2) | Information only | Register; retention test record |
| Vendor changes its retention or residency terms | Notice within [5] working days of PLUMB becoming aware; route suspended for Client data until re-approved | Object / terminate as above | Register; decision log |
| Emergency replacement (vendor outage or incident) | Notice within [2] working days after the fact; only to a vendor already on the register with confirmed ZDR and Singapore route | | Incident register |

---

## 11. Clauses counsel should also include

| Clause | Note |
|---|---|
| Client warranties | Lawful basis to supply the data; no special-category data; notification to its employees and customers where required; own s.26 basis for data sent from overseas affiliates |
| Instructions | PLUMB processes only on the Client's documented instructions (the charter); informs the Client if an instruction would breach PDPA |
| Access and correction requests | PLUMB assists the Client within [5] working days; does not respond directly to data subjects |
| Data portability | Deliverables and Client data returned in open formats |
| Liability | Cross-reference engagement letter clause 4; counsel to decide whether DPA breaches carry a separate cap |
| Order of precedence | DPA prevails over the letter for personal data |
| Term | Co-terminous with the engagement; retention and deletion obligations survive |

---

## 12. Open items for v0.2

| # | Item | Owner | Gate |
|---|---|---|---|
| 1 | PDPC breach-notification timelines and thresholds from primary PDPC guidance | Counsel | G1 |
| 2 | Complete the subservice register: Singapore routes and ZDR in writing for each vendor; Bedrock and Anthropic direct-API residency | Compliance lead | G1 (GA criterion: every vendor documented) |
| 3 | Exact SOC 2 TSC and ISO 27001:2022 Annex A control IDs from the compliance platform | Compliance lead | G2 |
| 4 | Retention periods (90-day raw-data working value; 10-year engagement file) | Counsel + insurer | G2 |
| 5 | Interviewee and respondent consent notices (PLUMB as organisation) | Counsel | G1 |
| 6 | Publicly-available-data exception scope for the research corpus | Counsel | G1 |
