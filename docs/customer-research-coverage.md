# Customer research — deeper and broader (v0.1)

**Date:** 2026-11-06. **Status:** design + first implementation (`pipeline/plumbinventory`, `catalogue/coverage/insurer.yaml`), worked on Great Eastern (`runs/great-eastern/2026-11-06-inventory/`).
**Why:** the 2026-11-02 red team found the transcription exact and the reading shallow: findings came from keyword passages while the reviewers read the annual report end to end (§3), the organisation was not known (§5), and AI outside the report was not addressed at all (§3). Customer research has to go **deeper** into the client's own documents and **broader** across sources, without loosening the evidence rules.

## 1. Deeper: read the client's own documents the way the client's executives do

| Layer | What we read | What it gives the deliverable | Rule |
|---|---|---|---|
| Strategy pages | Letter to shareholders, CEO review, segment reviews | Every AI use, by segment and market; the cost pressures the CEO names | Attribute to the segment the page belongs to, never "Group" by default |
| People pages | Management team, board profiles, nominating-committee changes | Named owners (e.g. MD Group Operations owns claims and underwriting); leadership changes in the year | Addressees come from the client's own directory, not a generic C-suite list |
| Governance report | Committee mandates, KRIs, internal audit scope, director fees | Where AI oversight actually sits (risk committee, technology KRIs, audit) | "Not disclosed publicly" is never "absent" |
| Notes to the accounts | Claims incurred, expenses, sensitivities, loss component and CSM | Flow bases for value sizing; where improvement reaches P&L fastest | Sensitivities and balances are stocks; never an annual value pool |
| Prior year | Same pages, FY-1 | What moved (e.g. Malaysia A&H sensitivity S$5.9m → S$99.3m) | Same methodology check before comparing |

Enforced by the **coverage step** (`python -m plumbinventory.coverage`): every checklist item is reported with the pages where it occurs, or "not found in this document". A reviewer sees in one table what we read and what we did not. GEH result: `runs/great-eastern/2026-11-06-inventory/coverage.md` — 18 document items, 16 found, 2 not found (GenAI/LLM language; model-risk/AI-governance language).

## 2. Broader: six source classes beyond the annual report

| Class | Typical sources | GEH yield (2026-11-06) | Tier |
|---|---|---|---|
| Job postings | Careers pages, aggregators | ML pipelines, Data & AI Ops, TensorFlow/PyTorch, AWS/GCP/Azure → in-house ML platform (inv-14) | T4 |
| Vendor case studies, conference decks | Vendor customer stories, event decks | Pega agent app on private cloud with a GenAI assistant planned (inv-10); vendor-run cloud database (inv-13) | T3–T4 |
| Customer and agent apps | App-store listings, release notes, trade press | App recommendation feature (inv-12); agent chatbot on a third-party engine (inv-11) | T4 |
| Results and media after the AR | Quarterly releases, interviews | 1H-26 release names no AI and no Data & AI successor | T2 |
| Group / parent | Parent's annual report, group press | Parent's in-house GenAI tools and agentic KYC; whether the subsidiary uses them is a question (inv-15) | T2, labelled proxy-by-parent |
| Regulator and industry | MAS guidelines and registers, enforcement, industry initiatives | Inventory scope includes AI inside SaaS not sold as AI (MAS §4.2, fn. 21) | T1 |

Rules for every broader source:
- **Secondary is labelled on every surface** ("Other public source · not hashed") and never upgraded to a disclosed fact. A secondary entry says what to confirm, not what is true.
- **Absence is a question.** Classes with no evidence go in "Worth asking about", never in findings.
- **Group material is a proxy**, labelled as the parent's, and never attributed to the subsidiary.
- **Entities are enumerated.** Every subsidiary and market (GEH: General Insurance, Takaful, Indonesia) is listed even when nothing is found, so a miss is visible.
- **Fetch path:** the shell cannot reach publisher sites from the cloud sandbox; web pages are read with the fetch tool as secondary capture. Hashing a primary document still needs a machine with egress (F26).

## 3. What the client sees: the outside-in inventory starter

`pipeline/plumbinventory` turns the research into a page a CRO can audit in 30 seconds:

1. `candidates.yaml` — one row per candidate AI system: stage, market, basis (disclosed / secondary / group), build, status, why it may matter, what to confirm, and evidence.
2. `build.py` — string-matches every quotation against the stated PDF page of the hashed source and every figure as a whole token on its page. **Any miss fails the build.** Tests cover paraphrase drift, wrong page and fragment matches.
3. `page.py` — renders a single page where every row and figure opens the exact passage (highlighted), the printed page, a link to that page of the publisher's PDF, and the hash. It refuses to render an inventory with a failed check.

GEH: 15 candidates (9 disclosed, 5 secondary, 1 group), 22/22 checks passed, published as a private artifact for internal review.

Framing rules carried over from the red teams: no grades, no gap language, materiality left to the client's control function, aims never presented as results, loaded terms only where the source uses them (the build enforces the last one by exact match).

## 4. Next

| # | Item | Why |
|---|---|---|
| R1 | Module per external class in `plumbresearch` (postings exists; add vendor-case, app, group, regulator) writing straight into `candidates.yaml` | Today the broader sources were gathered by hand in one session |
| R2 | Coverage step as a build gate: an item marked required for the industry and not searched blocks a final build | Makes "we read the whole thing" checkable |
| R3 | Banking checklist (`catalogue/coverage/bank.yaml`) for Maybank | Second subject (N4) |
| R4 | Re-hash the AR with egress and reconcile (F26), then drop the "not yet reconciled" banner | Required before the page leaves the firm |
| R5 | Fold the inventory and the finance question into the pre-read (v5) | Replaces the misused S$131m headline (red team 2026-11-02 §1) |
