# India data-protection rider

**Status:** v0.1 draft for Indian counsel, 2026-11-03. Model wording, not legal advice. Replaces the Singapore PDPA DPA (`../data-processing-addendum-outline.md`) for Indian clients.
**Attaches to:** the sprint SOW and any pilot SOW between UFlex Limited ("**Client**") and PLUMB Advisory Pte. Ltd. ("**PLUMB**"). Prevails over the SOW on personal data and security incidents.
**Law:** Digital Personal Data Protection Act 2023 ("**DPDP Act**") and Digital Personal Data Protection Rules 2025 ("**Rules**") — core obligations from 13 May 2027 **[VERIFY: counsel — commencement]**; CERT-In Directions under s.70B(6) of the IT Act 2000, 28 April 2022 ("**CERT-In Directions**"). PLUMB applies these terms from signature, ahead of commencement.

## 1. Roles

| Data | Client role | PLUMB role |
|---|---|---|
| Personal data the Client supplies or makes available (interviewee details, org charts, operator IDs in line or ERP extracts) | Data Fiduciary | **Data Processor** under a valid contract (DPDP Act s.8(2)) |
| Interview notes and recordings made by PLUMB for the Client's engagement | Data Fiduciary | Data Processor **[VERIFY: counsel — whether PLUMB is a fiduciary for its own interview records; see `interviewee-privacy-notice.md`]** |
| PLUMB's own business contacts | — | Data Fiduciary (outside this rider) |

Most sprint data (line, lab, energy, inventory) is non-personal. This rider still applies its security, incident and deletion terms to **all** Client data, personal or not.

## 2. Processor obligations

PLUMB will:
1. **Purpose limitation** — process Client personal data only on the Client's documented instructions (the SOW and the data request schedule) and only for the engagement; never for its own purposes, benchmarking, marketing or model training.
2. **Minimisation** — ask for roles rather than names, and pseudonymous IDs rather than operator names, wherever the analysis allows.
3. **Security safeguards** — maintain reasonable security safeguards to prevent personal data breach (DPDP Act s.8(5); Rules on security safeguards), including at least: encryption in transit and at rest; access limited to named personnel with MFA; logging of access; back-ups; and the controls in `security-response-pack.md` **[VERIFY: counsel — Rule numbering and minimum measures, incl. log retention of one year]**.
4. **Personnel** — ensure everyone with access is bound by confidentiality and has signed PLUMB's insider-trading undertaking.
5. **Assistance** — help the Client respond to Data Principal requests (access, correction, erasure, grievance) within [5] working days; not respond directly to Data Principals except to redirect them to the Client.
6. **Erasure** — delete Client personal data and Client data when the purpose is served or on instruction (s.8(7)), within the period in the data request schedule and in any case within [30] days of the final deliverable; return on request before deletion; issue a **deletion certificate** listing items, systems (including sub-processors), method and date.
7. **Records and audit** — keep a record of processing for the engagement and give the Client, on request, the sub-processor register, access logs for Client data and evidence of deletion; allow one audit per year (or after an incident) on [15] working days' notice, under confidentiality.

## 3. Personal data breach and cyber incident notice

| Event | PLUMB action | Clock |
|---|---|---|
| Any personal data breach, or any cyber security incident of a type listed in the CERT-In Directions affecting Client data or a PLUMB system that connects to the Client | Notify the Client's named security contact by phone **and** email | **Within [2] hours** of PLUMB becoming aware, so the Client can meet its **6-hour** CERT-In reporting obligation **[VERIFY: counsel — whether the Client's CERT-In obligation is triggered by a vendor-side incident]** |
| Same | Written update: what happened, data and systems affected, Data Principals affected (number, categories), containment, likely consequences | Within **[24] hours**, then daily until closed |
| Same | Full report to support the Client's detailed intimation to the Data Protection Board | Within **[48] hours**, so the Client can file within **72 hours** **[VERIFY: counsel — Rules timeline]** |
| Same | No notice to the Board, CERT-In, Data Principals or the media by PLUMB unless the Client agrees or the law requires PLUMB to | — |
| Close | Root cause, corrective actions, evidence of deletion of any exposed copies | Within [10] working days |

**Named 24/7 security contacts**

| Party | Name | Phone (24/7) | Email |
|---|---|---|---|
| PLUMB | [[FOUNDER: primary]] / [[FOUNDER: deputy]] | [[FOUNDER]] | [[FOUNDER: security@ PLUMB domain]] |
| Client | [ ] (CISO or SOC) | [ ] | [ ] |

## 4. CERT-In flow-down

1. **Incident notice** as in section 3.
2. **Logs** — PLUMB keeps logs of access to Client data and of its own systems used for the engagement (identity provider sign-ins, file access, admin actions) for at least **180 days**, time-synchronised to a reliable NTP source, and gives them to the Client on request. The CERT-In Directions require these logs to be kept within Indian jurisdiction where they apply; PLUMB's tenant is in [[FOUNDER: region]] **[VERIFY: counsel — whether the Directions apply to PLUMB as a non-resident vendor; if so, an India-region log store is needed]**.
3. **Point of contact** — PLUMB's named security contact above, reachable 24/7 during the engagement.
4. **No PLUMB system connects to Client OT or IT networks** (see `ot-rules-of-engagement.md`); this keeps PLUMB outside the Client's connected-system perimeter.

## 5. Cross-border transfer

1. PLUMB processes Client data in [[FOUNDER: Singapore / India region]] and through the sub-processors in section 7, each with its region stated.
2. Basis: the DPDP Act permits transfer outside India except to countries the Central Government restricts by notification (s.16). PLUMB will not transfer Client personal data to a restricted country, and will stop and notify the Client within [2] working days if a route becomes restricted **[VERIFY: counsel — current notifications and any sector rule that applies to the Client]**.
3. The Client may require, per data item, that data stays in a Client-hosted workspace (section 6 option A). Non-personal confidential data follows the same routes.

## 6. AI tools and the "LLM-off" option

| Option | What it means | When to use |
|---|---|---|
| **A. Client-hosted, LLM-off** | Raw data stays in a workspace the Client provisions and controls; PLUMB analyses it there with non-AI tools (spreadsheets, Python/SQL) and no data is sent to any model API | Default for raw line, lab, energy and ERP extracts, and for any UPSI |
| **B. PLUMB tenant, LLM-off** | Data copied to PLUMB's tenant; no model API calls on it | When the Client cannot host a workspace |
| **C. PLUMB tenant, LLM route approved** | Named items may be sent to the model APIs in section 7 (zero data retention or stated retention, no training) | Only for items marked "LLM route: Y" in the data request schedule, approved by the Client in writing |

The **LLM route (Y/N)** column of `data-request-schedule.md` is the per-item instruction. Anything not marked Y is N. UPSI is N unless the Client's company secretary approves otherwise in writing. PLUMB remains fully responsible for every deliverable whether or not AI tools were used; all AI-assisted content is reviewed by a named PLUMB professional before issue.

## 7. Sub-processor and AI-tool register

Only providers listed here may process Client data. **No row may be used for Client data until its "written confirmation" cell is filled.** PLUMB gives [10] working days' notice before adding or replacing a provider; the Client may object on reasonable data-protection grounds and, if unresolved, terminate the affected work without penalty.

| # | Provider | Purpose | Processing region | Retention / zero-data-retention status | Used for model training? | Written confirmation (date / reference) |
|---|---|---|---|---|---|---|
| 1 | [[FOUNDER: productivity tenant — email, documents, storage]] | Engagement workspace, email | [[FOUNDER]] | Per PLUMB retention schedule; deleted at engagement end | No | [[FOUNDER: …]] |
| 2 | [[FOUNDER: model API provider 1]] | Drafting and analysis of items approved for the LLM route | [[FOUNDER: pinned region]] | [[FOUNDER: ZDR approved / N days]] | No | [[FOUNDER: …]] |
| 3 | [[FOUNDER: model API provider 2, if any]] | As above | [[FOUNDER]] | [[FOUNDER]] | No | [[FOUNDER: …]] |
| 4 | [[FOUNDER: transcription service]] | Interview transcription (only with interviewee consent to AI transcription) | [[FOUNDER]] | [[FOUNDER]] | No | [[FOUNDER: …]] |
| 5 | [[FOUNDER: secure file exchange, if not Client-hosted]] | Receipt of data exports | [[FOUNDER]] | Deleted on transfer to workspace | No | [[FOUNDER: …]] |
| 6 | [[FOUNDER: endpoint management / EDR]] | Device security telemetry (no Client content) | [[FOUNDER]] | [[FOUNDER]] | No | [[FOUNDER: …]] |
| 7 | [[FOUNDER: film-process specialist's firm, if contracted separately]] | Specialist analysis | [[FOUNDER]] | Per this rider | No | [[FOUNDER: signed flow-down, date]] |

PLUMB flows down obligations no less protective than this rider to each sub-processor and remains responsible for them.

## 8. Client responsibilities

The Client confirms it has a lawful basis (consent or a legitimate use under s.7) to share any personal data it supplies, and that it will not supply sensitive or special categories (health, biometric, financial account, children's data) unless agreed in writing.

## 9. Liability and term

Breach of this rider is subject to the super-cap in the SOW (insurance limit). This rider lasts as long as PLUMB holds any Client data; deletion, confidentiality and incident obligations survive.

| For UFlex Limited | For PLUMB Advisory Pte. Ltd. |
|---|---|
| Signature / name / title / date | Signature / name / title / date |
