# Great Eastern — run 2, FY2025 annual report attached (2026-10-25)

**Internal artefact — not for client or prospect use.** Run in a sandbox without egress, before plumbverify 0.4; equivalent to an `--profile internal` build. A client-facing build of the same inputs withholds every annual-report claim under spec C2a ("awaiting publisher reconciliation") until `plumbverify reconcile` returns MATCH.

Change log: 2026-10-25 — governance finding reworded from "material finding" to a question for management; outcome line restated as released/withheld (red-team review 2026-10-25, Blocker 6 / §5.1, §5.4).

Input: `great-eastern-holdings-limited-ar-2025.pdf` (244 pp, SHA-256 `ae320cb3…6488`), supplied by the founder, ingested via the attached-document path under the publisher URL; reconciliation **pending** (no egress). All annual-report claims carry the label `attached; publisher hash unreconciled`.

## Scored signals (outside-in; corroborative only, never lift an item above L3 per instrument §5.4)

| Signal | Value | Verified against raw text? |
|---|---|---|
| Annual-report AI rubric | **L4** — production language, ≥2 specific use cases, quantified outcomes | Yes. Use cases named: AI advisory platform (~75% advisor prep-time reduction), proprietary AI medical-claims automation (75% same-day turnaround, MOH indicator), OCR for medical-bill wastage/abuse (Malaysia, award), AI misconduct-detection model, analytics lead prioritisation; AI underwriting for complex cases "in testing" |
| AI mentions density | 0.23 per 1,000 words (24 / 104,761) | Yes |
| Governance component | 0 in our lexicon (document-level signal only) | Operator-checked only; no independent reviewer has read the raw text. The lexicon ("AI governance", "responsible AI", "model risk", "FEAT", "Veritas", "GenAI") found no match in this one document. **Limits:** single document (GEH FY2025 AR); the lexicon is a keyword list and this same run shows it is incomplete (it missed the MD, Group Data and AI); two-column extraction (defect 2) can split multi-word phrases; group-level governance at OCBC (~88% parent; its AR2025 carries an "AI, Digital and Data" strategy) was not examined; the two-upstream rule for load-bearing claims is not met. **Presentation:** a question to put to management, not a conclusion — "GEH's FY2025 annual report describes production AI with quantified outcomes (L4 on the published rubric) but contains no AI-governance, responsible-AI or model-risk language in our lexicon; we would want to see the group-level framework before scoring D6." |
| Ownership component | 1 | Yes — "In 2025, we restructured our Data & AI operating model" |
| AI / data leadership titles | reported **0** — **DEFECT** | Raw text has **Zhao Jingyuan, Managing Director, Group Data and AI** (with GE since 2022; 20+ yrs data/analytics/AI) in the management-team pages. Extractor's title lexicon lacks "Managing Director, Group Data and AI" |
| Named competitors | 1 | Report does not name competitors; peer seed must come from the funnel's other steps (as designed) |
| Peer sizes | 4 claims **BLOCKED** | Sources (Prudential factsheet, Income AR, Singlife newsroom, AIA AR) unreachable from sandbox → DEAD → not citable. Correct behaviour |
| Postings, patents, financials, calls | not-available | Data pack not yet fetched |

Released: annual-report claims (internal build, labelled). Withheld: 4 claims (listed: the peer-size claims above, sources unreachable from the sandbox). Under a client build, the annual-report claims would also be withheld, awaiting publisher reconciliation. Citation resolution 0.2 (1 of 5 sources resolvable, the attachment). Quotation pass rate 1.0. Reviewer human-read: not yet recorded.

## Defects logged
1. `plumbresearch.modules.annual_report` leadership extractor: add patterns "Managing Director, Group Data and AI", "Group Data and AI", "Head/Director of Data & AI", "Chief Digital Officer"; treat any C-suite/MD title containing "Data" and/or "AI" as D1.2 evidence.
2. Two-column PDF layout: pypdf extraction interleaves columns, so rubric evidence strings mix adjacent text (e.g. the underwriting sentence runs into the bonus-issue paragraph). Rubric scoring was unaffected here but quotation claims from multi-column pages will fail C5. Fix: use `pdftotext -layout` or pdfplumber column detection in `plumbverify.extract` for PDFs.
3. Competitor extractor returned 1 "name" from a false-positive context; tighten to require an organisation NER hit.

## Next
- Fetch the data pack on a laptop (`data-packs/great-eastern/fetch-datapack.sh`), re-run online: reconciles the attachment, unblocks peer sizes, fills postings/patents/financials.
- Fix defects 1–3, re-run offline on the same attachment and diff `report.json`.
- Widen the governance lexicon ("data governance", "ethical", "technology risk", "AI risk", "machine learning", "algorithm"); independent reviewer reads the management-team and governance/risk sections by eye and signs a human-read line here before the governance signal appears anywhere external.
