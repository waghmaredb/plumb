# Commercial

**Status: v0.1 draft** — G0 design-freeze candidate. Nothing here has been used on a real client or reviewed by counsel.

The commercial layer turns the methodology into something that can be sold, contracted and defended. Everything legal is **model wording for counsel review, not legal advice**. Every URL comes from the research reports or notes; nothing is cited from memory. Unconfirmed items are marked **[VERIFY]**.

## Files

| # | File | What it is | Used at |
|---|---|---|---|
| 1 | `pricing-ladder.md` | One-pager: Tier 0 free self-scored benchmark (cap-at-level-3 rule shown on screen one; self-scored population never pooled with engagement scores), Tier 1 fixed-fee PLUMB Assessment by size band (S$25–85K) split into Phase A (public data, instrument, interviews; 12 days; no confidential extracts) and Phase B (post-onboarding confidential data, +8 days), Tier 2 outcome pricing with measurement-design preconditions, Tier 3 Benchmark Refresh retainer (S$5–12K/month), add-ons, design-partner terms, Singapore market anchors, EDGE grant note. Change log 2026-10-25: red-team review findings applied (file header) | Proposal; public pricing page at GA |
| 2 | `engagement-charter-template.md` | Phase 0 output and Schedule 1 of the letter: client identity, segments, value lenses, peer-set protocol, data requests, interviewee list, hypothesis tree, ghost-deck reference, QA gate owners, AI-use disclosure, 20-working-day timeline, decision log | Day 1–2 of every engagement |
| 3 | `engagement-letter-clauses.md` | Drafting notes and model clauses: scope, AI-assisted work and human accountability, verification standard and its limits, liability cap, no third-party reliance, confidentiality and data handling, IP, benchmark reuse consent, conflicts, outcome-fee measurement and disputes, termination, Singapore law; drivers table with sources | Counsel drafting; every engagement |
| 4 | `data-processing-addendum-outline.md` | PDPA-aligned DPA outline (Schedule 2): roles, purposes, data categories, subservice-processor table (region / retention / ZDR / confirmation date), s.26 transfer basis, security measures mapped to SOC 2 and ISO 27001, retention, breach notification, audit rights, sub-processor change notice | Counsel drafting; any engagement with personal data |
| 5 | `conflict-check-procedure.md` | When the check runs, what is checked (client, peer set, competitors, founder's other roles and employer), decision rules, record kept | Before every charter, peer-set change and new engagement |

## How they fit together

| Document | Sits inside | References |
|---|---|---|
| Engagement letter | Signed contract | Schedule 1 charter · Schedule 2 DPA · Schedule 3 AI-use disclosure (`../compliance/evidence-pack-templates.md` §12) · Schedule 4 conflict disclosures · Schedule 5 design-partner undertakings · Schedule 6 measurement design |
| Charter | Schedule 1 | Pricing ladder (tier, size band, fee); conflict-check record ID; QA gate owners from `../pipeline/verification-pipeline-spec.md` |
| DPA | Schedule 2 | Vendor rules V1–V6 in `../pipeline/verification-pipeline-spec.md` §5; artefact 7 and 9 in `../compliance/evidence-pack-templates.md` |
| Conflict check | Engagement file, acceptance step | Charter §0, §3; letter §9 |

## GA-gate items this folder closes

From `../docs/Next steps and path to GA gate.md`: "Entity, PI/cyber insurance, engagement letter with AI-use and liability clauses, data-processing addendum, conflict-check procedure in place" and "Public pricing page (three-tier ladder plus S$5–12K/month retainer)". Entity and insurance remain open.

## [VERIFY] register for this folder

| Item | File | Needed by |
|---|---|---|
| EDGE grant eligibility for assessment work; SS 680 requirement | pricing-ladder §9 | Before any client-facing "EDGE-eligible" claim |
| Add-on prices (working values) | pricing-ladder §6 | First three quotes |
| MAS AIRM section numbering | pricing-ladder §6 | G1 |
| Entity name, liability cap, retention periods, dispute-clause body | engagement-letter-clauses §1, §4, §6, §11, §13 | Counsel, before first letter |
| Client procurement AI-use clause text (APS / DTA ClauseBank / California) | engagement-letter-clauses §2.5, §15; charter §9 | First public-sector-exposed client |
| PDPC breach-notification thresholds and clocks | data-processing-addendum §8 | G1 |
| Subservice register: Singapore routes and ZDR in writing per vendor; Bedrock and Anthropic direct-API residency | data-processing-addendum §4 | G1 (no client data before this) |
| SOC 2 TSC and ISO 27001:2022 control IDs | data-processing-addendum §6 | G2 |
| Founder employment-clearance policy | conflict-check-procedure §2, §3, §5 | Before first engagement |
