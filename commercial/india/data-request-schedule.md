# Data request schedule

**Engagement:** UFlex Limited — readiness sprint **Version:** [ ] **Agreed on:** [ ]
**Status:** template v0.1, 2026-11-03. Agreed at kickoff, maintained during the sprint, closed with deletion certificates.
**Governed by:** the NDA, `india-data-protection-rider.md` and `ot-rules-of-engagement.md`. **Scope: India sites only.** No data from overseas sites is requested in the sprint.

## How to read the columns

| Column | Meaning |
|---|---|
| Owner | UFlex person who supplies and approves the item |
| Transfer channel | How the item moves. Default: read-only export placed by UFlex IT in the agreed exchange area; never USB, never personal email |
| Storage location | **A** = UFlex-hosted workspace; **B** = PLUMB tenant ([[FOUNDER: region]]) |
| Personal data | Y if any natural person can be identified (operator IDs, names, emails) |
| UPSI | Y if UFlex's company secretary classifies the item as unpublished price sensitive information. **CS to confirm each row** |
| LLM route | Y only if UFlex approves sending this item to a listed model API; otherwise N (LLM-off). UPSI is always N unless the CS approves in writing |
| Retention | When PLUMB deletes it |
| Deletion certificate | Reference and date of the certificate issued for the item |

## Schedule

| # | Item | Site | Owner | Format | Transfer channel | Storage | Personal data | UPSI | LLM route | Retention | Deletion certificate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | List of installed line-supplier digital services, inspection systems, remote monitoring and AI tools on the pilot line | [pilot site] | Film technical head | XLSX / short list | Exchange area | A | N | N | N | Sprint end + 30 days | [ ] |
| 2 | Line control / historian tags for the pilot line and the control line: speeds, temperatures, extruder and die, casting and pinning, MDO/TDO, winder; breaks and restarts log — 12 months pre-period | [pilot site; India film site nominated by UFlex] | Line OT engineer | CSV / Parquet export, tag dictionary | Exchange area (pulled by UFlex OT) | A | N (Y if operator IDs included — pseudonymise) | [CS] | N | Sprint end + 30 days, or carried to pilot under new schedule | [ ] |
| 3 | Lab and QC results: thickness profile, haze, COF, tensile, defects; chip IV and moisture; reclaim / rPET blend ratio — same period | [pilot site] | QC head | CSV / XLSX | Exchange area | A | N | [CS] | N | As row 2 | [ ] |
| 4 | Energy meters: kWh by line section and utilities allocation, with good-kg output by grade | [pilot site] | Energy / utilities manager | CSV | Exchange area | A | N | [CS] | N | As row 2 | [ ] |
| 5 | Inspection-system defect events (type, position, time, roll ID); images only if needed and approved | [pilot site] | Quality systems owner | CSV; images as approved | Exchange area | A | N | N | N | As row 2 | [ ] |
| 6 | Scrap and reclaim records by grade, roll and shift | [pilot site] | Production planning | CSV / XLSX | Exchange area | A | N (pseudonymise shift leads) | [CS] | N | As row 2 | [ ] |
| 7 | ERP extracts — inventory (raw material, WIP, FG by SKU and site), sales and purchases, 24 months, **India entities only** | India sites | Supply-chain / ERP owner | CSV export | Exchange area | A | N (remove customer contact names) | **Likely Y** [CS] | N | Sprint end + 30 days | [ ] |
| 8 | Recycling line data: bale intake and grading, wash line, extrusion, SSP, lab tests (IV, colour, acetaldehyde), output by grade | Noida recycling | Recycling plant head | CSV / XLSX | Exchange area | A | N | [CS] | N | As row 2 | [ ] |
| 9 | Customer requests for recycled-content records (anonymised examples) | Noida / India sales | Sustainability lead | PDF / XLSX, customer names redacted | Exchange area | A | N | N | [UFlex to decide] | Sprint end + 30 days | [ ] |
| 10 | Dharwad BOPP commissioning plan and instrumentation specification (if in scope) | Dharwad project | New-projects lead | PDF | Exchange area | A | N | [CS] | N | Sprint end + 30 days | [ ] |
| 11 | Interviewee list: role, function, site, email (6–8 leaders) | — | Executive sponsor's office | Email list | PLUMB-domain email | B | **Y** | N | N | Sprint end + 30 days | [ ] |
| 12 | Interview notes / recordings / transcripts | — | PLUMB (per interviewee consent) | DOCX; audio only with consent | — | B | **Y** | [CS — may contain UPSI] | Y only for AI transcription where the interviewee consented and UFlex approved; else N | Recordings: deleted once notes verified, ≤ [14] days; notes: sprint end + 30 days | [ ] |
| 13 | Aggregated cost and margin data for the business case (plant or product level) | India | Group finance | XLSX | Exchange area | A | N | **Likely Y** [CS] | N | Sprint end + 30 days | [ ] |

## Sign-off

| UFlex — executive sponsor | UFlex — company secretary (UPSI column) | UFlex — CISO (channels, storage, LLM route) | PLUMB — engagement lead |
|---|---|---|---|
| | | | [[FOUNDER]] |
