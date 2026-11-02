# PLUMB Advisory — India client document set

**Status:** v0.1 draft, 2026-11-03. Not for issue until every `[VERIFY: …]` and `[[FOUNDER: …]]` marker is cleared.
**Built from:** red-team review 2026-11-03 §B; existing Singapore drafts in `../` (engagement letter clauses, DPA outline, conflict-check procedure); UFlex strategy §§10–12.
**Nature:** plain-English model wording for review by Indian counsel and a chartered accountant. Not legal or tax advice.

## Marker key

| Marker | Meaning | Who clears it |
|---|---|---|
| `[VERIFY: counsel]` | Legal point to be confirmed by Indian counsel (and Singapore counsel where noted) | Counsel |
| `[VERIFY: CA]` | Tax, GST or remittance point to be confirmed by a chartered accountant | CA |
| `[[FOUNDER: …]]` | Fact only PLUMB can supply (entity details, names, prices, insurance, confirmations). Never fill with an estimate | Founder |

## How this set relates to the Singapore drafts

| Singapore draft | For Indian clients |
|---|---|
| `engagement-letter-clauses.md` | Replaced by `sprint-sow-india.md` (Indian law, India seat, 30/70 payment, assignment of deliverables, benchmark and reference **off** by default). The AI-use and human-responsibility wording (clauses 2.1–2.4) is carried over |
| `data-processing-addendum-outline.md` (PDPA) | Replaced by `india-data-protection-rider.md` (DPDP and CERT-In). The sub-processor register format is carried over |
| `conflict-check-procedure.md` | Stays internal; the client sees only `vendor-independence-declaration.md` |
| `pricing-ladder.md` | India prices are stated in ₹ in the SOW and pilot fee schedule |

Statutory references to the Income-tax Act 1961 (s.195, s.206AA, Form 15CA/15CB) are kept because procurement teams still use them; the Income-tax Act 2025 applies from 1 April 2026 with renumbered provisions **[VERIFY: CA — map every section reference to the 2025 Act]**.

## The documents and when they are used

| # | File | What it is for | Stage in the customer journey | Review |
|---|---|---|---|---|
| 1 | `README.md` | This index | — | — |
| 2 | `mutual-nda-india.md` | Mutual NDA with UPSI and Structured Digital Database clauses; fallback if the client does not use its own paper | **Before first data** (signed before any non-public information is exchanged) | Counsel |
| 3 | `insider-trading-pack.md` | PLUMB code of conduct as a fiduciary, per-person undertaking and holdings declaration, SDD identifier form | **Before first data** (in force before UPSI is received) | Counsel |
| 4 | `india-data-protection-rider.md` | DPDP processor terms, CERT-In flow-down, cross-border basis, sub-processor and AI-tool register, LLM-off option | **Before first data**; attached to the SOW | Counsel |
| 5 | `security-response-pack.md` | Pre-filled answers to a CISO's vendor questionnaire | **Before outreach** (prepared); sent **to close the sprint** | Founder; counsel for the insurance lines |
| 6 | `ot-rules-of-engagement.md` | One-page plant rules, signed by the plant head | **In the sprint** (signed before the first site visit) | Client EHS and OT security; counsel light-touch |
| 7 | `data-request-schedule.md` | Item-by-item data request with channel, storage, UPSI, LLM route, retention | **Before first data** (agreed at kickoff); maintained **in the sprint** | Founder; client CS and CISO |
| 8 | `sprint-sow-india.md` | Statement of work for the two-week readiness sprint | **To close the sprint** | Counsel and CA |
| 9 | `pilot-fee-schedule.md` | Pilot advisory fee, holdback, metric, baseline, attribution, dispute route | Proposed at sprint readout; signed with the pilot; **applied at Gate 2** | Counsel and CA; client group finance |
| 10 | `vendor-registration-tax-pack.md` | Checklist of documents Indian procurement asks a Singapore vendor for, plus the client tax note | **Before outreach** (start collecting; longest lead times); submitted **to close the sprint** | CA |
| 11 | `vendor-independence-declaration.md` | Conflict-of-interest declaration: vendor independence and personal holdings | **Before outreach** (signed and ready); sent **to close the sprint** | Counsel light-touch |
| 12 | `redline-playbook.md` | PLUMB's fallback positions on the client's MSA. **Internal only** | **To close the sprint** and again before the pilot | Counsel |
| 13 | `interviewee-privacy-notice.md` | Notice and consent for interviews, including AI transcription option | **In the sprint** (sent with each interview invitation) | Counsel |
| 14 | `single-source-justification.md` | One-page note the client's sponsor can file with procurement | **To close the sprint** | None (factual) |
| 15 | `cover-email-uflex.md` | First outreach email and follow-up | **Before outreach** (send after UFlex's Q2 FY27 results, ~13–14 Nov 2026, with refreshed numbers) | Founder |

## Order of work

1. **Before outreach:** entity, bank account, PLUMB-domain email and website live; PI (and ideally cyber) insurance bound; film-process specialist agreed in writing; sub-processor register confirmations filled in; conflict check run on UFlex and recorded; documents 5, 10 and 11 ready; send document 15.
2. **Before first data:** documents 2, 3, 4 and 7 signed or agreed; identifiers given to the client's company secretary.
3. **To close the sprint:** documents 8, 14 (and 5, 10, 11 on request); use 12 against the client's paper.
4. **In the sprint:** documents 6, 7 and 13 operate.
5. **At Gate 2:** document 9 governs measurement, holdback release and disputes.

## Internal only — never send

`redline-playbook.md`; the internal conflict-check record; discussion guides; red-team files and lessons; model JSON, build scripts and research folders; superseded workbook versions. Strip author and company metadata from every exported file (PDF, DOCX, XLSX) before sending.
