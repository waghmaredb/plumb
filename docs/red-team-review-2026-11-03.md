# Red-team review — UFlex strategy v2 and the customer document set (2026-11-03)

Two independent reviews: (1) UFlex v2 strategy and workbook, read as CEO + head of film technology + CFO, with every document number recomputed from the workbook; (2) the planned customer document set, read as the CEO's office, procurement, CIO/CISO, company secretary/legal, and CFO. Legal and tax points are for counsel and a chartered accountant to confirm.

## A. UFlex strategy v2

**Verdict:** would take the 45-minute session; would not sign the sprint as written. All document numbers match the workbook.

### Must fix (errors)
1. **Gate 2 test is mis-scoped.** The 1.6× break-even assumes every use case outperforms; the pilot only measures UC1. UC1 alone needs ~2.6× (≈1.5% scrap, 5.1% energy) under the current cost allocation; on its own incremental cost UC1 is roughly break-even. Gate 2 must test incremental UC1 economics, with a measurement design (historian pre-period, difference-in-differences, power calculation).
2. **The money contradicts the pitch.** "Prove on one line before the larger spend", but year 1 spends ₹41.6 cr (data foundation, UC2–UC5, team, contingency). Re-tranche: an explicit pre-Gate-2 commitment (~₹10–12 cr), the rest after evidence.
3. **UC6 base is wrong.** "Packaging volume 151,755 t" includes aseptic and holography; flexible packaging is ~80,000 t a year → UC6 ≈ ₹4.3 cr, not ₹8.3 cr.
4. **UC4 mis-scoped.** Two of the four guided projects are already running (Noida recycling, Mexico WPP); Egypt is in trials. Only Dharwad can be instrumented from commissioning; ramps are demand-constrained.
5. **UC3 is a revenue-share proxy** (₹850 cr potential × 1.5%), breaking our own tonnage rule; rebuild on bale-to-flake yield, IV, grade, actual throughput. Recycling is "commissioned and ramping", not "built and running" (~15 kt PET + 10 kt MLP processed vs ~114 kt capacity).
6. **Headline labelling.** ₹42 cr is gross and never reached (model caps at 85%/80% → ₹36 cr); net year-5 is ₹11 cr. "Realised share" wording wrong for UC3. Russia is 7.5% of capacity, not the 15% implied by the 85% cap. Wave count wrong (six, not five). UC2 costed in year 1 though "after the pilot". Year-2 coverage (30%) exceeds India capacity (26%) while overseas starts after Gate 3. Team cost implies ~12 FTE, not 6–10.
7. **Lighthouse comparison mixes units** (absolute 0.95% vs relative −31%/−71%); ACG makes pharma barrier films, not BOPET/BOPP. Several peer claims lack sources in Appendix A (HUL is a Jan 2025 Lighthouse). Converter-waste benchmark is from Ethiopian plants — don't present it as UFlex's benchmark.
8. **Accounting labels.** "Net EBITDA effect" charges capitalisable hardware to EBITDA (Ind AS 16/38); NPV "including working capital" mixes pre-tax EBITDA with cash. No terminal value. Show reported 17.0% beside normalised 15.5% Q1 FY27 margin.

### Should improve (depth and fit)
- Film science in UC1: chip IV/moisture, drying and crystallisation; reclaim and rPET blend ratio (direct link to PWM recycled-content push); pinning and casting; filter-change cycles; TDO clip/chain wear; BOPP master-roll ageing. Black specks come from degraded polymer, not "melt-pump pressure". "Already automated" is true for modern lines only; name the OEM and inspection stack to inventory.
- Metallising (238,600 MTPA) needs named loss mechanisms and sizing; chip plant SSP/acetaldehyde control; recycling: bale grading, SSP decontamination, food-contact approvals, chain-of-custody models (ISO 22095); gravure: spectral ΔE, returned inks, solvent recovery, coat weight and cure.
- Align with stated strategy: aseptic laminate integrity in wave 1; WPP absent; AI-led product development; recycling utilisation.
- Missing strategy layer: enterprise GenAI and treasury cash/FX forecasting across nine currencies, predictive maintenance (show break-downtime throughput as a scenario at 85% utilisation), energy-to-carbon 2035, talent/CoE building on AIM-AIA, partner strategy, capex/opex funding model, 90-day quick wins, sensitivity (tornado) chart, top-down value-at-stake check.

### Tone and leak risk
- "Russia"/"sanctions" appear ~6 times → use "one CIS site, subject to a vendor export-licensing review".
- Remove AI/draft fingerprints: the `claude:` meta tag, "version 2", workbook "revised after executive red-team review", the Ethiopian benchmark cell.
- Lead with the staged decision, not "does not yet pay".
- Timing: Q2 FY27 results due ~13–14 Nov; send after, with refreshed numbers.
- Plan the route to decision through the CMD and promoter family.

## B. Customer document set

**Verdict:** a good sales sequence, not yet a set a listed Indian company can approve. Most likely deal-killer: the founder's current employment.

### Missing documents
1. Vendor-registration and tax pack: ACRA profile, constitution, directors and beneficial owners, bank letter, IRAS tax residency certificate, Form 10F, no-PE and beneficial-ownership declarations, PAN (consider), tax note (payments to a non-resident fall under s.195 and DTAA Art. 12, not s.194J; IGST under reverse charge by the client), anti-bribery and sanctions declarations, insurance certificates.
2. Mutual NDA (expect the client's paper) with UPSI / Structured Digital Database clauses, signed before any non-public data.
3. SEBI insider-trading pack: PLUMB's code of conduct as a fiduciary (PIT Regulations Schedule C), restricted list, per-person undertakings and holdings declarations, identifiers for the client's SDD.
4. Founder employment clearance (written employer consent) and a standing outside-interests declaration.
5. India data-protection rider: DPDP processor terms, CERT-In flow-down (incident notice within hours, logs, 24/7 contact), sub-processor register with written confirmations filled in. Replaces the Singapore PDPA-only DPA for Indian clients.
6. Security response pack: pre-filled questionnaire answers, device/tenant controls (PLUMB-owned devices and tenant; never employer devices), incident SLA.
7. OT rules of engagement (one page, signed by the plant head): no remote OT access, read-only exports via client IT, no photography, EHS induction.
8. Pilot fee schedule and measurement design: holdback (not refund), metric, baseline, attribution, dispute route.
9. Interviewee privacy notice and consent text.
10. Single-source justification note for procurement.
11. Redline playbook for the client's MSA (fallbacks on IP, liability, law and forum, benchmark and reference).

### Improvements to planned documents
- Cover email: plain text, sent from a PLUMB domain, link to a 2-page summary rather than attachments, one small ask to one person, independence line.
- Pre-read deck: second touch, not first. The long strategy is sent only on request.
- Credentials: honest; never cite employer customer work; if no engagements yet, say so and lean on risk-reversal terms.
- Proposal/SOW: one price (not a range), currency and FX, taxes clause, milestones tied to acceptance, PO reference, named personnel and days, India sites only, IP assignment of deliverables (perpetual, worldwide; PLUMB keeps its methodology with a licence), "not legal or sanctions advice", benchmark and reference clauses off.
- Contract defaults for Indian clients: Indian law with arbitration seated in India (or concede the seat), 30/70 payment rather than 50% advance, assignment rather than licence, liability super-cap at insurance limits.
- Conflict declaration covers all technology vendors, including compute, storage, edge and cloud.
- Value ledger owned by client finance, not PLUMB.
- Pare the 48-item maturity instrument to the sprint's problem.
- Remove "sanctions review" as a PLUMB task; it is client counsel's.

### Gate 0 — before any outreach (founder)
Incorporated entity, bank account, domain email and website; written employer clearance; PI (and ideally cyber) insurance; a named film-process specialist who has agreed in writing; AI-vendor register confirmations filled in; check whether the client is a customer or prospect of the founder's employer (if so, decline or recuse).

### Never leak
Discussion guide; red-team files and lessons; model JSON, build scripts and research folders; superseded workbook versions; internal conflict-check records. Strip author and company metadata from exported files.
