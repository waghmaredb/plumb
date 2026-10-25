# Great Eastern — run 2, FY2025 annual report attached (2026-10-25)

Input: `great-eastern-holdings-limited-ar-2025.pdf` (244 pp, SHA-256 `ae320cb3…6488`), supplied by the founder, ingested via the attached-document path under the publisher URL; reconciliation **pending** (no egress). All annual-report claims carry the label `attached; publisher hash unreconciled`.

## Scored signals (outside-in; corroborative only, never lift an item above L3 per instrument §5.4)

| Signal | Value | Verified against raw text? |
|---|---|---|
| Annual-report AI rubric | **L4** — production language, ≥2 specific use cases, quantified outcomes | Yes. Use cases named: AI advisory platform (~75% advisor prep-time reduction), proprietary AI medical-claims automation (75% same-day turnaround, MOH indicator), OCR for medical-bill wastage/abuse (Malaysia, award), AI misconduct-detection model, analytics lead prioritisation; AI underwriting for complex cases "in testing" |
| AI mentions density | 0.23 per 1,000 words (24 / 104,761) | Yes |
| Governance component | **0** | Yes — no "AI governance", "responsible AI", "model risk", "FEAT", "Veritas", "GenAI" anywhere in the report. Material finding for a MAS-regulated insurer 12 months before AIRM applies |
| Ownership component | 1 | Yes — "In 2025, we restructured our Data & AI operating model" |
| AI / data leadership titles | reported **0** — **DEFECT** | Raw text has **Zhao Jingyuan, Managing Director, Group Data and AI** (with GE since 2022; 20+ yrs data/analytics/AI) in the management-team pages. Extractor's title lexicon lacks "Managing Director, Group Data and AI" |
| Named competitors | 1 | Report does not name competitors; peer seed must come from the funnel's other steps (as designed) |
| Peer sizes | 4 claims **BLOCKED** | Sources (Prudential factsheet, Income AR, Singlife newsroom, AIA AR) unreachable from sandbox → DEAD → not citable. Correct behaviour |
| Postings, patents, financials, calls | not-available | Data pack not yet fetched |

Build: FAIL (4 blocked peer-size claims). Citation resolution 0.2 (1 of 5 sources resolvable, the attachment). Quotation pass rate 1.0.

## Defects logged
1. `plumbresearch.modules.annual_report` leadership extractor: add patterns "Managing Director, Group Data and AI", "Group Data and AI", "Head/Director of Data & AI", "Chief Digital Officer"; treat any C-suite/MD title containing "Data" and/or "AI" as D1.2 evidence.
2. Two-column PDF layout: pypdf extraction interleaves columns, so rubric evidence strings mix adjacent text (e.g. the underwriting sentence runs into the bonus-issue paragraph). Rubric scoring was unaffected here but quotation claims from multi-column pages will fail C5. Fix: use `pdftotext -layout` or pdfplumber column detection in `plumbverify.extract` for PDFs.
3. Competitor extractor returned 1 "name" from a false-positive context; tighten to require an organisation NER hit.

## Next
- Fetch the data pack on a laptop (`data-packs/great-eastern/fetch-datapack.sh`), re-run online: reconciles the attachment, unblocks peer sizes, fills postings/patents/financials.
- Fix defects 1–3, re-run offline on the same attachment and diff `report.json`.
