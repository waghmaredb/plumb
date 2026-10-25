# Founder checklist — things only Deepak can do

**Status: PARKED 2026-10-25.** Product work continues without these; items marked ⛔ block a gate and are listed with the gate they block. Tick a box when done and tell Claude — it picks up whatever the item unblocks.

Change log: 2026-10-25 — converted to checkboxes and parked; F6 split (GE done, Maybank open); gate dependencies added. Earlier: F4 marked BLOCKER, F25/F26 added (red-team review 2026-10-25).

## ⛔ Blockers

- [ ] **F4 — Name the independent reviewer** (D3). Real person, CV on file, per-deck fee agreed (S$2–4K/deck if paid); must not have run the agents. *Blocks: G1 close, any charter or proposal.* Record in `docs/decisions.md` D3.
- [ ] **F26 — Re-run Great Eastern from a laptop with internet.** `bash pipeline/plumbresearch/data-packs/great-eastern/fetch-datapack.sh` → `plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out --data-dir data` → `plumbverify reconcile --store out/great-eastern/evidence`. ~1 hour. *Blocks: first client-grade output (G1).*
- [ ] **F27 — Pull the verification models** on the same laptop as F26: `plumbverify models pull`, then `plumbverify calibrate calibration/geh_c4_v1.jsonl --split all`. ~20 min. *Blocks: written-claim checking meeting its 2% target (G1).*
- [ ] **F5 — Conflict declaration** for Maybank, Great Eastern and OCBC (GEH parent) under C6 of `commercial/conflict-check-procedure.md`. 15 min. *Blocks: showing any alpha output externally.*
- [ ] **F25 — Record the D7 clearance basis** in `docs/decisions.md`: written employer clearance, or the documented reason none is needed. *Blocks: design-partner contracts (G2).*

## This week (by Fri 31 Oct 2026)

- [ ] **F1 — Backorder plumb.ai** (expires 31 Oct 2026). DropCatch / SnapNames / NameJet, ~US$60–100.
- [ ] **F2 — Domains:** decide on plumbadvisory.com (Afternic, buyable); register plumb.sg / plumbadvisory.sg.
- [ ] **F3 — BizFile+ "Plumb" name search**, then name application for *PLUMB ADVISORY PTE. LTD.* (S$15, 120-day reservation).
- [x] **F6a — Great Eastern FY2025 annual report** attached (2026-10-25; ingested, SHA-256 `ae320cb3…6488`).
- [ ] **F6b — Maybank FY2025 integrated annual report** — download and attach. *Unblocks the second alpha subject.*

## Before incorporation (next 2–3 weeks)

- [ ] **F7 — Incorporate PLUMB Advisory Pte. Ltd.** S$300; ≥1 resident director; model constitution; SSIC 70201 + 62021 (`docs/incorporation-checklist.md`).
- [ ] **F8 — Startup SG Founder:** decide eligibility and timing (company <6 months old at application; first-time founder).
- [ ] **F9 — Company secretary** (within 6 months) and registered address.
- [ ] **F10 — Business bank account** (1–3 weeks; constitution, UEN, director IDs).
- [ ] **F11 — Register a Data Protection Officer** with PDPC (can be yourself).
- [ ] **F12 — IPOS trademark:** "PLUMB" word mark + stylised acronym, Classes 35 and 42 (S$560; 9–14 months).
- [ ] **F13 — PI + cyber insurance quotes** (PI ~S$500–3,500/yr; cyber ~S$1,000/yr for S$250K [VERIFY]).
- [ ] **F14 — Counsel review** of `commercial/engagement-letter-clauses.md` (incl. clause 3.6 refund-on-fabrication) and `data-processing-addendum-outline.md`.

## Accounts and credentials you must hold

- [ ] **F15 — CSA account;** download the AICM v1.1 spreadsheet and attach it. *Resolves 12 candidate control IDs.*
- [ ] **F16 — LLM vendor accounts in the company's name:** OpenAI (Singapore residency project), Anthropic (apply for zero-data-retention), Google Cloud (Vertex pinned to asia-southeast1). Get ZDR/retention **in writing** and attach. *Blocks: Phase B (confidential client data).*
- [ ] **F17 — Compliance-automation platform** (Vanta / Drata / Secureframe, with ISO 42001 module). *Starts the SOC 2 + ISO 27001 clock.*
- [ ] **F18 — Certification-body scoping call** (TÜV SÜD PSB under SAC).
- [ ] **F19 — SS 680 / EDGE:** confirm with Enterprise Singapore whether strategy-only AI work needs an SS 680-certified lead; decide certify-yourself vs partner.
- [ ] **F20 — AI Verify Foundation** membership; read AI TAP criteria; decide on a wave-2 testing application.

## Network and commercial

- [ ] **F21 — Shortlist 3–5 design partners** (Singapore FIs or suppliers) with warm-intro paths. *G2 needs three signed.*
- [ ] **F22 — 2–3 second reviewers / associates** (ex-Big-4/MBB or senior FI risk) for paid QA gate 3 work. *G3 repeatability test.*
- [ ] **F23 — Fractional compliance lead + contract engineer.**
- [ ] **F24 — Public posture:** when/where PLUMB is announced and what is said about AI use. Sell verification, never "AI-generated".

## Standing items

| Cadence | Action |
|---|---|
| Weekly until G1 | Review alpha outputs as the signing partner; log acceptance in the engagement file |
| Per engagement | Sign QA gate 3; approve the AI-use disclosure wording |
| Monthly | Approve regulatory-status-map changes before they alter tier rules |
| Quarterly | Benchmark refresh sign-off; control-library resync review |

## Open decisions

- [ ] D3 reviewer name (F4) — ⛔
- [ ] D7 clearance basis (F25)
- [ ] SS 680 route (F19)
- [ ] Startup SG Founder (F8)
- [ ] Public announcement timing (F24)
