# Red-team review — GEH pre-read v4 + deep-dive report (customer executive view)

Date: 2026-11-02. Material reviewed: deck v4 (10 slides) and the strict report (15 pp), exactly as the client would receive them, plus GEH's Annual Report 2025 for fact-checking. Four independent reviewers, each briefed only with the materials and a role: Group CEO, Group CRO, MD Group Data & AI, Group CFO. None saw our storyline, QA sheet or reasoning. Every claim below marked ✓ was re-checked against the AR by the lead.

## Verdict

Unanimous: **not in this form.** All four found the transcription exact — every figure and quotation matches the AR, and aims are never presented as results ("above Big-4 average" — CEO). The failure is interpretation, framing and depth. Best case today: delegated to the MD Group Operations or Data & AI lead for 30 minutes; the CEO would not take the meeting.

## Findings, ranked by impact

### 1. The S$131m headline misuses an actuarial sensitivity (4 of 4) ✓
Note 30 scenario 4 measures the remeasurement of insurance contract liabilities when the A&H claims *assumption* changes, one at a time. Under SFRS(I) 17 most of a favourable change on profitable groups goes to the CSM and releases over years; what reaches P&L is mainly loss-component reversal on onerous groups. So it is a one-off revaluation of a stock, not "a year's profit".
- Proof in the same table: Malaysia scenario 4 was S$5.9m in 2024 and S$99.3m in 2025 with "methodology… not changed" ✓; life loss component rose S$727.1m → S$873.9m ✓.
- "Group" is wrong: it is SG + MY life only (omits Other Asia and non-life PA&H, Table 30(C)).
- 10% is 2–5× our own hypothesis; S$131m ≈ 10.7% of Group PAT (S$1,227.4m ✓) — no CFO accepts that for a claims tool.
- Fair-dealing optics: "10% better claims" + "medical cost management" next to a profit number reads as "pay out less", worst in Malaysia under BNM scrutiny.
- **The insight we missed (CFO):** the swing shows Malaysia medical has turned onerous. AI that bends the medical cost trend there protects P&L directly because the CSM buffer is gone. That is truer and sharper.
- Sounder sizing (CFO, on stated assumptions): recurring run-rate on claims, roughly S$19–70m a year after tax at full run-rate, S$10–40m after par-fund, repricing and already-captured haircuts — to be vetted by an actuary; A&H claims by segment are not disclosed in the AR.

### 2. Wording drifted from the source (3 of 4) ✓
| We wrote | AR says |
|---|---|
| "75% of medical claims settled same day" (presented as group-wide) | "same-day turnarounds for 75% of medical claims" — Singapore segment review, p. 38 |
| "Bill-fraud checks" | "potential wastage and abuse within medical claims", p. 41 — fraud is legally loaded, especially in Malaysia |
| CareShield under "Onboarding" | AI segmentation enabling instant approvals — an automated underwriting decision, p. 38 |
| Directors paid "for their data and AI work" | "information technology infrastructure, data and artificial intelligence initiatives", p. 78 |
| Data & AI leadership ✓ "Described" | MD Group Data & AI leaving for OCBC, successor "to be named", p. 65 |

### 3. The inventory and context are incomplete (3 of 4) ✓
Missed in the AR: Malaysia lead prioritisation "contributing to improved conversion rates" (p. 41); in-house AI "reducing reliance on external vendors" (p. 39); "modernising our core systems, data platforms" (p. 39); "persistent medical claims inflation" handled by "structural measures" in product strategy (p. 12); the Risk Management Committee's technology-risk mandate (p. 66), technology KRIs to the Board (p. 214), Internal Audit technology coverage (p. 82); Dr Chong Yoke Sin's AI background (p. 15).
Not addressed at all: GenAI / LLMs, data foundations, the OCBC group angle (Group Data Office, Veritas), vendor-embedded AI, MLOps, talent, cost of AI, GE General / Takaful / Indonesia.

### 4. Governance framing reads as a gap finding (3 of 4)
Three empty circles beside the client's name read as "no AI framework"; the caveat does not survive forwarding. An annual report is not where AI policy or inventories are disclosed, and MAS's guidelines say FIs need not create a dedicated AI committee. Board "oversight" was evidenced by fee footnotes while the real route (RMC, KRIs, Internal Audit) went uncited. Retitle as "not disclosed publicly; to be reviewed against GEH/OCBC internal frameworks".

### 5. It does not know the organisation (2 of 4) ✓
There is no Group COO; Patrick Kok, MD Group Operations, leads customer service, underwriting and claims (p. 29). The natural buyer for a dollar case, the CFO, is not addressed; the Data & AI seat is asked for while possibly vacant. Asking four C-suite diaries in a first cold contact reads as naive.

### 6. Unfinished and unverified material in a cold approach (4 of 4)
Placeholder credentials on slide 2; a peer slide whose title asserts a claim over an empty table; a MAS slide stamped "awaiting source"; "Discussion draft" on every page; report pages admitting the independent review is not done. Each one alone fails first-pass vendor due diligence (CRO).

### 7. Tone grades the client (3 of 4)
"Great Eastern's AI is working" (an unknown firm giving a pass mark) and the dark "0 of 8" box (no insurer reports per-use AI dollars in an annual report) land as a gotcha — politically worst for the Data & AI head, who becomes the opponent instead of the champion.

### 8. The offer is the wrong shape (3 of 4)
A six-week interviews-and-synthesis diagnostic is what Big-4 sells at S$250–500k+; nobody buys it from an unknown firm. "AI inventory and risk tiers" in six weeks is not credible (embedded vendor AI, shadow GenAI, 2nd-line validation). Procurement, NDA, TRM/outsourcing and PDPA take 4–8 weeks before work starts. What they would buy: a 2-week value-sizing gate (~S$25–40k) or a 3–4-week paid pilot (~S$60–120k, part at risk) on a claims sample, producing a CFO-signable savings range with a measurement design (baseline, control, attribution net of repricing).

### 9. Regulatory depth is not visible (CRO)
Expected without prompting: the exact MAS AI Risk Management Guidelines (issued 7 Oct 2026, effective 7 Oct 2027; sections 3–4 by 2027, 5–6 by 2028; proportionality; third-party accountability; agentic-AI consultation planned 2027), FEAT/Veritas, MAS's 2024 AI model risk paper, TRM, outsourcing, fair dealing, individual accountability, PDPA/PDPC AI guidance; for Malaysia BNM RMiT, fair treatment, customer information, outsourcing, BNM's AI discussion paper, Shariah governance for Takaful.

### 10. Conflicts and identity (CRO)
Before any interview: entity, directors, PI insurance; disclosure of principals' employers and side roles; whether the lead's employer sells to GEH or OCBC and has approved the outside work; any products the firm sells (an AI-governance product would be the classic assessment-to-implementation conflict); a commitment on implementation work; an AI-use statement (tools, no client data into third-party models, no training/retention); human sign-off.

## Where reviewers disagreed
- Method and evidence appendices: CEO says cut them from anything a client sees ("about their process, not my business"); Data & AI says the evidence discipline is a genuine asset to lead with. Lead's view: keep method out of the pre-read; offer the evidence pack on request and say so in one line.

## What this says about the product (not just this deck)
- **Our quality bar measured form, the reviewers measured substance.** v4 passed every rubric rule; the rubric's "addressable basis" check accepted a declaration without testing the economics. Rules to add: valuation sensitivities and balance-sheet stocks cannot be used as annual value pools; every value figure must state flow vs stock, period, scope (segment vs group) and gross/net; loaded terms (fraud, settled, Group, policy, framework) must appear in the cited source.
- **Paraphrase drift slipped past verification.** Face text was "supported" by the right passage but changed its meaning. The offline matcher is too weak for this; the loaded-term guard above is the cheap fix, independent review the real one.
- **Extraction misses whole-document context.** Findings came from keyword passages; the reviewers read the AR end to end. Add a coverage checklist per industry (operations and data platforms, vendor strategy, risk committee mandate, board skills, leadership changes, cost pressures named by the CEO).
- **Value sizing needs a finance-literate module:** flow bases (claims incurred, expense lines), IFRS 17 recognition path, haircuts, attribution design, actuary review flag.
- **Addressees come from the client's own directory**, not a generic C-suite list.
- **The offer should be a priced pilot with a value gate**, not a diagnostic.
- **Regulation is reachable:** the CRO reviewer reached the MAS 7 Oct 2026 release and two law-firm notes via the web fetch tool, which the shell cannot. MAS facts can be checked this way (as secondary capture) instead of waiting for attachments.
