# Founder checklist — things only Deepak can do

Change log: 2026-10-25 — F4 moved to the top and marked BLOCKER; F25 (D7 clearance basis) and F26 (GE re-run with egress + reconcile) added (red-team review 2026-10-25, Blocker §1(c), §1(d), §2.8, rank 1, 2, 10).

Status: living document. Everything product-side (methodology, pipeline, catalogue, compliance library) is Claude's; this file is the list of actions that need the founder's identity, signature, money, network or judgement. Tick items here; the GA plan references this file.

## BLOCKER — before any charter, proposal or client-facing material

| # | Action | Why now | Where | Cost / time |
|---|---|---|---|---|
| F4 | **BLOCKER.** Name the **G1 independent reviewer** (D3): a real person, CV on file, per-deck fee agreed | Every trust claim depends on it; no charter can be signed truthfully until it closes (review §1(c), §2.8, rank 1); must be someone who did not run the agents | Record in `docs/decisions.md` D3 and the charter §0 | S$2–4K/deck if paid |

## This week (by Fri 31 Oct 2026)

| # | Action | Why now | Where | Cost / time |
|---|---|---|---|---|
| F1 | Backorder **plumb.ai** with a drop-catch service | Domain expires 31 Oct 2026 | Registrar backorder (DropCatch / SnapNames / NameJet) | ~US$60–100 |
| F2 | Decide on **plumbadvisory.com** (parked on Afternic, buyable) and register **plumb.sg / plumbadvisory.sg** | Brand lock before incorporation | Afternic; SGNIC-accredited registrar | [VERIFY] prices |
| F3 | **BizFile+ "Plumb" name search**, then file the name application for *PLUMB ADVISORY PTE. LTD.* | Catches reserved names the mirrors don't show; 120-day reservation | bizfile.gov.sg (Singpass) | S$15, 10 min |
| F5 | **Conflict declaration** for Maybank, Great Eastern and OCBC (GEH parent) under C6 of the conflict-check procedure | Alpha subjects cannot be scored until declared clear | `commercial/conflict-check-procedure.md` → engagement file | 15 min |
| F6 | Download **Maybank FY2025** and **Great Eastern FY2025** annual reports and attach them | SGX/Maybank links return 403 from the sandbox; needed for the AI rubric and peer seed | maybank.com IR; greateasternlife.com IR | 10 min |
| F25 | Record the **D7 clearance basis** in `docs/decisions.md`: written employer clearance, or the documented reason none is needed; file it with the GE/OCBC conflict declaration (F5) | "Already cleared" with no paper is a self-attestation by the person with the conflict; procurement will ask (review §1(d), rank 10) | `docs/decisions.md` D7; engagement file | 30 min + employer response |
| F26 | **Re-run Great Eastern from a machine with egress** (`data-packs/great-eastern/fetch-datapack.sh`, then `plumbresearch run` with the default client profile) **and run `plumbverify reconcile`** on the evidence store | Turns the one real output from a liability into the first sales asset: reconciles the attachment, unblocks peer sizes, removes the sandbox artefacts (review §2.6, §5.3, rank 2) | Laptop with egress | ~1 hour |

## Before incorporation (next 2–3 weeks)

| # | Action | Notes |
|---|---|---|
| F7 | Incorporate **PLUMB Advisory Pte. Ltd.** | S$300; ≥1 resident director; model constitution; SSIC 70201 primary, 62021 secondary (see `docs/incorporation-checklist.md`) |
| F8 | Decide **Startup SG Founder** eligibility and timing | Requires company <6 months old at application and first-time founder — a month-1 decision |
| F9 | Appoint company secretary (within 6 months) and registered address | Corporate-secretary provider or self |
| F10 | Open business bank account | Expect 1–3 weeks; have constitution, UEN, director IDs ready |
| F11 | Register a **Data Protection Officer** with PDPC | Mandatory; can be yourself |
| F12 | File **IPOS trademark** — "PLUMB" word mark + stylised acronym, Classes 35 and 42 | S$560 for two classes via picklist; 9–14 months |
| F13 | Get **professional indemnity + cyber insurance** quotes | PI ~S$500–3,500/yr, cyber ~S$1,000/yr for S$250K cover [VERIFY] |
| F14 | Engage counsel to review `commercial/engagement-letter-clauses.md` and `data-processing-addendum-outline.md` | Model wording only until a lawyer signs off |

## Credentials and accounts you must hold personally

| # | Action | Unblocks |
|---|---|---|
| F15 | Create a **CSA (Cloud Security Alliance) account** and download the AICM v1.1 spreadsheet; attach the xlsx | Resolves the 12 `TBD [candidate]` control IDs in `compliance/control-library.csv` |
| F16 | **LLM vendor accounts** in the company's name: OpenAI (Singapore data residency project), Anthropic (apply for zero-data-retention), Google Cloud (pin Vertex to asia-southeast1); confirm ZDR/retention **in writing** and attach | Vendor rules V1–V8 in the pipeline spec; DPA sub-processor table |
| F17 | Choose and sign up for a **compliance-automation platform** (Vanta / Drata / Secureframe) with the ISO 42001 module | Starts SOC 2 + ISO 27001 readiness clock (wave 1) |
| F18 | Pick an **ISO 27001/42001 certification body** for a scoping call (TÜV SÜD PSB under SAC is the Singapore-accredited option) | Wave 2–3 timeline |
| F19 | Confirm **SS 680 / EDGE** position with Enterprise Singapore: does strategy-only AI work need an SS 680-certified lead? Decide: get SCMC/PMC certified yourself, or partner with a certified consultant | Whether SME clients can co-fund 50% of a PLUMB assessment |
| F20 | **AI Verify Foundation** membership application; read the AI TAP criteria and decide whether to build the testing capability (benchmarking method) for a wave-2 application | Assurance-market positioning |

## Network and commercial (your relationships, not mine)

| # | Action | Target |
|---|---|---|
| F21 | Shortlist **3–5 design-partner candidates** in Singapore FIs or their suppliers who would accept a 40–50% discounted assessment for data access, a reference and a measured follow-up | Names + warm intro path; G2 needs three signed |
| F22 | Identify **2–3 potential second reviewers / associates** (ex-Big-4/MBB, or senior FI risk people) for paid QA gate 3 work | Repeatability test at G3 |
| F23 | Line up a **fractional compliance lead** (SOC 2/ISO experience) and a **contract engineer** for the pipeline | Budget D4 assumed both |
| F24 | Decide the **public posture**: when and where PLUMB is announced (LinkedIn, vexpose, your site), and what is said about AI use and the method | Trust data says sell verification, never "AI-generated" |

## Standing items (recurring)

| Cadence | Action |
|---|---|
| Weekly until G1 | Review the alpha outputs as the "partner who signs"; log acceptance in the engagement file |
| Per engagement | Sign QA gate 3; approve the AI-use disclosure wording on the deck |
| Monthly | Approve the regulatory-status-map changes (MAS, Malaysia/Thailand bills, Australian standards) before they alter tier rules |
| Quarterly | Benchmark refresh sign-off; control-library resync review |

## Decisions still open

- D3 reviewer name (F4) — BLOCKER
- D7 clearance basis (F25)
- SS 680 route (F19)
- Startup SG Founder (F8)
- Public announcement timing (F24)
