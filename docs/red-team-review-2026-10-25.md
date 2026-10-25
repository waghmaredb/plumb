# Red-team review — PLUMB customer journey and expectations

**Date:** 2026-10-25
**Reviewer stance:** independent; did not build any of this. Read as a buyer, a Big-4 partner and a MAS supervisor would.
**Scope read:** README; `commercial/pricing-ladder.md`; `commercial/engagement-charter-template.md`; `methodology/ghost-deck-template.md`; `methodology/maturity-instrument.md` §1, §5, appendix; `methodology/right-to-win-kit.md` §1–2, §6; `methodology/value-and-use-case-kit.md` §2–4; `compliance/risk-tiers-and-gates.md`; `compliance/evidence-pack-templates.md`; `runs/great-eastern/2026-10-25-ar-attached/` and `-baseline/`; `docs/Next steps and path to GA gate.md`; `docs/founder-checklist.md`; `docs/decisions.md`; `docs/alpha-targets.md` (GE section); trust and Deloitte passages of the two research reports; `commercial/engagement-letter-clauses.md` §4–5 and `pipeline/verification-pipeline-spec.md` C4/C11 for cross-checks.
**Severity key:** Blocker = would stop a sale or a signature, or makes a stated claim false today. Major = a buyer or reviewer would raise it and the current materials have no answer. Minor = friction.

**Headline.** The methodology is more complete than most boutiques ever write down, and that is precisely the problem: the materials describe a firm that does not yet exist. The product is called *Verified*; the first real run resolved 1 of 5 sources (0.2), released its only source under the label "publisher hash unreconciled", missed the client's Managing Director of Data & AI, and reported governance as zero from a keyword lexicon. Every role that makes the quality claim credible (independent reviewer, signing partner, quality lead, verification control owner) is the same person, and that person has not yet been named for G1 (`docs/decisions.md` D3: "Unassigned"). The entity is not incorporated, insurance is at "get quotes", counsel has not reviewed the engagement letter, and no LLM vendor has confirmed zero-data-retention in writing. None of that is fatal at G0. All of it is fatal if any client-facing material goes out before it is fixed, because the brand promise is verification and the first thing a sceptic will verify is PLUMB.

---

## 1. The journey, five personas, eight steps

Score: 1 = walks away, 3 = proceeds with conditions, 5 = proceeds without hesitation. Scores are for the materials *as they stand today*, not as the GA plan intends them.

| Step | (a) CDO/COO, mid-size SG insurer | (b) CFO | (c) Head of Model Risk / CRO | (d) Procurement / vendor risk | (e) Big-4 partner (what they say to the client) |
|---|---|---|---|---|---|
| 1 Awareness (cold) | 2 | 2 | 2 | n/a | "Never heard of them. One person." |
| 2 Free Tier-0 benchmark | 2 | 3 | 1 | 1 | "You typed your control maturity into a stranger's web form?" |
| 3 Proposal | 3 | 3 | 2 | 1 | "Ask who signs. Ask who reviews. Same name." |
| 4 Charter / data request | 2 | 3 | 1 | 1 | "Day-5 data cut-off for an FI? They have never onboarded with a bank." |
| 5 20-day engagement | 3 | 3 | 2 | 2 | "Twenty interviews and nine research modules in six working days, by one person." |
| 6 Board deck | 3 | 3 | 2 | 3 | "Read the footnotes. 'Publisher hash unreconciled.' 'Global, peer n insufficient.'" |
| 7 Outcome-priced follow-on | 2 | 3 | 1 | 2 | "A holdout group on claims turnaround is a conduct issue, not a measurement design." |
| 8 Retainer | 3 | 2 | 3 | 3 | "Called 'Moving Goalpost'. Think about that name." |

### (a) CDO/COO of the Great Eastern archetype

**Step 1 — awareness.** The README leads with an acronym expansion ("Peer-ranked · Load-bearing · Upstream-verified · Maturity · Benchmark") and the sentence "A plumb line is how you check that something is actually true." A CDO does not buy a plumb line; she buys a defensible answer to her board before MAS's 7 Oct 2027 inventory milestone. The materials know this (GA plan §3.1: "Singapore FIs and their suppliers facing the MAS AIRM clock") but no reviewed asset says it in the first sentence. **[Major — fix: one-page outside-in letter that opens with the client's own AR rubric level, the MAS date, and one gap. See §5 for how to present the GE run.]**

**Step 2 — Tier-0.** `pricing-ladder.md` §2: "every Tier 0 entry displays ≤ 3 per item and cannot land above the Emerging band (C ≤ 50). This is stated on the output page." The CDO of an insurer whose own annual report scored L4 on PLUMB's rubric ("production language, ≥2 specific use cases, quantified outcomes") will be told by a free form that she is at best "Emerging". That is not a conversion hook; it is a reason to close the tab. The hook text ("shows which items would move with evidence") does not change the headline band she screenshots. **[Major — fix: Tier-0 output leads with "uncapped self-view" and "evidence-capped view" side by side; the capped band is the second number, with the rule explained in one line.]**

**Step 4 — charter.** `engagement-charter-template.md` §4 asks for P&L by segment, KPI extracts, win/loss records, a customer contact list with consent status, org chart, AI inventory, governance papers, vendor contracts and the AI incident log, "all items received by day 5". For a MAS-regulated insurer, D3/D4/D11 cannot leave the building until the vendor has cleared third-party onboarding (information-security questionnaire, PDPA, outsourcing/TRM review). That is weeks to months, not days. The fixed-fee condition in `pricing-ladder.md` §3.4 ("slippage past those dates extends the timeline, not the fee, up to 10 working days, after which a change order applies") then penalises the client for PLUMB's own onboarding immaturity. **[Blocker — fix: split Tier 1 into Phase A (public data + executive interviews + instrument, no confidential extracts) and Phase B (confidential data) that starts only after onboarding; price and timeline Phase A alone for design partners.]**

**Step 6 — board deck.** The ghost-deck example (`ghost-deck-template.md` §4) is strong and the horizontal-flow test is the best single quality device in the repo. But S09 ("sits at the 58th peer percentile") cannot be built for any Singapore insurer: the GE peer funnel yields n = 9 core (`signals.md` row "Core peer count after funnel ... below the instrument §5.5 minimum of 15"). The slide will read "global, peer n insufficient" against a global benchmark that today has n = 0. **[Blocker — see §2.3.]**

### (b) CFO

The CFO's question is S$65–85K vs. S$400K vs. the internal team. `pricing-ladder.md` §8 anchors the Big-4 at "~£250K–350K, i.e. S$400K+" using UK G-Cloud day rates. The same file's Singapore evidence (Pertama) puts the >1,000-staff band at S$90–200K. A Singapore CFO will have seen Big-4 AI readiness proposals in the S$150–250K range, not S$400K; the "5–15× lower" claim reads as inflated the moment she checks it, and she will. Against the internal team: the instrument is "shareable with clients under engagement terms" (`maturity-instrument.md` header) and the kits cite McKinsey, BCG, PwC and MGI on almost every row, so the CFO's analyst can rebuild 70% of the scoring in a week. What the internal team cannot do is the peer evidence log and the independent sign-off. Those are the two things the first run did not deliver. **[Major — fix: re-anchor against Singapore Big-4 figures (obtain two real quotes via F21 contacts) and against "internal team: 6 weeks of a 3-person data office at loaded cost" — that is the real alternative.]**

Payment terms: 50% on day 2 (`pricing-ladder.md` §3.4) to an entity that is not yet incorporated, from a CFO who has no reference. **[Major — fix for design partners: 30/40/30 with the middle tranche at QA gate 2 read-out.]**

### (c) Head of Model Risk / CRO

This is the persona the wedge depends on and the one the materials serve least well.

- **Who tiers?** `risk-tiers-and-gates.md` §1: "Scored at intake by the engagement lead with the client use-case owner." The CRO will say the control function tiers, not the vendor and the business owner together (MAS 4.13, which the file itself cites in artefact 2). The file's own GO rule requires a "control checklist ... costed into the business case" before GO; the CRO will ask who validated the checklist. **[Major — fix: intake score is a *proposal*; the gate checklist's "Risk / governance sign-off (T2+)" line is moved to the top and made a precondition for the use case appearing on S23 at all.]**
- **Who reviews?** `engagement-charter-template.md` §0 requires "PLUMB independent reviewer — must not run the research agents on this engagement" and a separate "PLUMB signing partner". Today those are the same person as the engagement lead, and D3 is "Unassigned". The CRO will not accept a QA gate 3 signed by the operator. **[Blocker — F4 must close before any charter is issued, not before G1 review.]**
- **Client data in LLM routes.** Charter §4: "no client data enters any LLM route until the vendor's ZDR/retention terms are confirmed in writing". F16 is open. The disclosure template (`evidence-pack-templates.md` §12.1) has "[zero-data-retention / 30-day retention / other] confirmed in writing on [date]" as a blank. The CRO will treat a blank as "no". **[Blocker — F16 before any proposal to an FI.]**
- **The firm as third party.** MAS 5.11(a) (quoted in artefact 7): "independent certifications or external assessments over self-attestations". PLUMB today is 100% self-attestation. The GA plan accepts SOC 2 "observation window open" as sufficient for GA; a CRO at an FI will accept it for a *public-data* engagement and not for one that ingests the incident log and customer lists. **[Major — same fix as (a) step 4: Phase A/Phase B split.]**
- **Outcome tier.** `pricing-ladder.md` §4.2 precondition 3: "Control group or counterfactual method agreed in writing (holdout ...)". For the GE-type use cases (claims automation, underwriting support) a holdout means some policyholders get the slower or less accurate process. That is a fairness and conduct question under MAS 5.7–5.8, not a statistics question. The CRO will veto holdouts on customer-facing T3/T4 use cases, which are exactly the ones with value. **[Major — fix: offer pre/post with seasonality adjustment or synthetic control as the default for T3+, and state in the kit that holdouts are for internal-productivity use cases only.]**

### (d) Procurement / vendor-risk officer

Checklist as they would run it against `docs/founder-checklist.md` and `docs/decisions.md`:

| Item they ask for | State today | Source |
|---|---|---|
| Legal entity, UEN | Not incorporated (F7) | founder-checklist |
| PI and cyber insurance certificate | Quotes not yet obtained (F13) | founder-checklist |
| Engagement letter reviewed by counsel | "Nothing here has been reviewed by a Singapore-qualified lawyer" | engagement-letter-clauses.md header |
| DPA | "outline" | commercial/ |
| DPO registered | Open (F11) | founder-checklist |
| SOC 2 / ISO 27001 | Not started (F17) | founder-checklist |
| Sub-processor list with retention terms | Not confirmed (F16) | founder-checklist |
| Headcount | 1 | throughout |
| Prior clients / references | 0 | README "Nothing here has been run on a real client" |
| Conflict of interest | Founder is a Dell APJC CTO; D7 says "Already cleared / not required" with no record; conflict declaration F5 for GE/OCBC still open | decisions.md; alpha-targets §1 item 3 |

Score 1 at steps 2–4 is not harsh; it is the vendor-risk officer's job. The one thing in the repo that would move them is `conflict-check-procedure.md` and the decision log, because they show the firm thinks like a regulated supplier. **[Blocker — the first FI engagement must be structured so that procurement can approve it as a "public-information advisory engagement, no confidential data, no system access", which is a lighter onboarding tier at most FIs.]**

The D7 entry deserves its own line: "Already cleared / not required" is a self-attestation by the person with the conflict, and GE's parent (OCBC, ~88%) is the kind of enterprise-infrastructure account where the founder's employer plausibly has a relationship. `alpha-targets.md` itself says "[VERIFY by founder declaration, logged on the CC form]". **[Major — fix: written clearance from the employer or a documented reason why none is needed, filed in the engagement file before the GE run is shown to anyone at GE.]**

### (e) The Big-4 partner competing for the work

What they will say, and whether the materials have an answer:

| Attack | Materials' answer today | Adequate? |
|---|---|---|
| "One person. Who covers if he is ill in week 3?" | None. GA plan has "second reviewer, part-time until G3" | No |
| "Their first run missed your MD of Data & AI and reported your governance as zero." | README logs the defect honestly | Only if PLUMB discloses it first (see §5) |
| "Their peer percentile is against a benchmark of nobody." | §5.5 fallback label | No, the label admits it |
| "The instrument has 12 known ambiguities and has never been tested for inter-rater reliability." | Appendix lists them; κ test is a v0.2 item | No |
| "The method is our own publications rearranged." | Kits cite BCG/McKinsey/PwC/MGI throughout | Partly: the verification layer and gap register are genuinely not Big-4 practice |
| "They will process your data through a US model vendor." | Charter §4 handling rule, unconfirmed | No until F16 |
| "AI wrote it." | Disclosure wording; "sell verification never AI-generated" rule | Yes, if the resolution rate is 100% rather than 0.2 |
| "Who is liable? Cap at 1× fees of S$40K on a deck that moves S$20M of spend." | engagement-letter §4.2 working position | Standard, but the Big-4's cap is on a bigger number |

The partner's strongest line is not any of these. It is: *"They have written a better QA manual than we have. Ask them to show you one deck that passed it."* Today there is none.

---

## 2. Expectation gaps: where the materials promise more than the pipeline delivers

| # | Promise (file, text) | What exists today | Severity | Fix |
|---|---|---|---|---|
| 2.1 | README: "produces three outputs at Big-4 quality with every citation verified" | GE run: one rubric level, one density figure, one governance keyword count, one ownership flag; 4 of 5 peer-size claims BLOCKED; citation resolution 0.2; leadership extractor DEFECT | Blocker | Remove "Big-4 quality" from every file until a reviewed deck exists. Replace with the measurable claim: "every number in the deck traces to a fetched, hashed source, or it is not in the deck." |
| 2.2 | `maturity-instrument.md` §5.4: "Any item where the organisation's consensus self-report is 4 or 5 is recorded at 3 until an artefact ... is logged" | Correct in principle; no client has yet been told their 5s are 3s. The charter gives respondents no warning. 10–30 leaders spend 30–45 min, then see their answers overwritten | Major | Put the cap rule in the instrument's opening screen and in the charter §5.1 respondent brief: "Levels 4–5 are evidence levels. Choose them, then attach or name the artefact." Turn the cap into a to-do list the client owns, not a verdict PLUMB imposes. Report "self-view vs evidenced view" as the S08 exhibit. |
| 2.3 | `maturity-instrument.md` §5.5 and `pricing-ladder.md` §2: peer percentile where n ≥ 15, otherwise "global benchmark, labelled" | GE peer set n = 9 core; `alpha-targets.md` §3.2 lists 9 Singapore insurers; no realistic SG insurer or mid-cap bank set reaches 15. Global benchmark n = 0 today; GA target n ≥ 30 *including* free self-scores, which are capped ≤ 3 and therefore a different population from evidence-gated entries | Blocker | Drop "percentile" from the Tier-1 promise for the first six engagements. Replace with the honest and more useful exhibit: rank within the named 9 peers on the outside-in signals that *were* computed, with each peer's value shown. Keep percentile for the free tier only, and never mix capped and evidence-gated entries in one percentile. |
| 2.4 | `right-to-win-kit.md` §1.2 C6: "Named unprompted ... by ≥ 30% of win/switch interviewees"; §3.2 corpus: earnings calls for company + 5–12 peers, ≥ 200 reviews, all win/loss records | Tier 0 includes none of it; Tier 1 allows 8–12 external interviews in days 5–12; GE has no earnings calls (`alpha-targets.md` row "No earnings calls found"); a life insurer's "customers" for win/loss are agents and policyholders, whose contact details are D3/D4 confidential data gated by onboarding | Major | State in the pricing ladder that the right-to-win exhibit at Tier 1 is "executive-stated, corpus-corroborated" (C1–C5) and that C6 is scored from public reviews and agent-channel sources unless external interviews are contracted. Price external interviews as the add-on they are. |
| 2.5 | `pricing-ladder.md` §4.2: eight preconditions for outcome pricing, including ≥ 3 months system-measured baseline and a control group | No client in the wedge runs control groups today (the instrument's own D8.2 L3 is "control group ... for ≥ 1 material use case", i.e. above the production boundary); holdouts on customer-facing FI use cases raise conduct issues | Major | Reposition Tier 2 as the *measurement-design* engagement first (build the baseline and the counterfactual in months 1–3 at base fee), with the savings share switching on only after the baseline exists. That is sellable; "we'll share savings once you have a control group" is not. |
| 2.6 | `ghost-deck-template.md` R8: "No unverified number leaves the deck ... Blocked claims are removed, never footnoted 'unverified'"; `verification-pipeline-spec.md` C11: "No 'unverified' footnotes or warning icons in client-facing material" | `signals.md`: every annual-report claim released with the label "attached; publisher hash unreconciled". That is a footnote saying "unverified". The attached-document path contradicts block-not-flag | Blocker | Either (a) reconcile before any claim is released (run `plumbverify reconcile` on a machine with egress; this is a 10-minute founder task), or (b) treat unreconciled attachments as BLOCKED for client-facing material and released only in internal runs. A board will not accept "publisher hash unreconciled" on a slide, and the Big-4 partner will read it aloud. |
| 2.7 | `pricing-ladder.md` §3.2: Phase 1 days 2–8, nine modules; Phase 2 days 5–12, 6–10 exec + 8–12 external interviews; instrument closes day 9 | One person. 14–22 interviews in six working days alongside pipeline operation and QA gate 1 at day 8 | Major | Either add a second interviewer (contract, S$-budgeted) or extend Phase 2 to days 5–14 and move QA gate 2 to day 14. Do not promise 20 days until one engagement has hit it. |
| 2.8 | `engagement-charter-template.md` §8: four distinct roles (engagement lead, independent reviewer, signing partner; plus "quality lead" in C11 overrides) | One person; D3 unassigned | Blocker | Name the reviewer (F4) and record the fee. Until then the charter cannot be signed truthfully. |
| 2.9 | `pricing-ladder.md` §1 Tier 0: "builds benchmark DB"; GA plan: "Benchmark database n ≥ 30 (free self-score + engagements)" | An FI employee cannot enter 48 control-maturity self-scores plus 8 compliance sub-dimension answers into an external web form without an InfoSec exception. The free tier will be filled by SMEs, suppliers and consultants, not by the wedge | Major | Accept this and label the free benchmark "suppliers and mid-market"; for FIs, run the instrument inside the engagement only. Do not let a supplier-heavy benchmark be presented as an FI peer set. |
| 2.10 | `maturity-instrument.md` §1: "Outside-in proxies 2–4 per item" | ~30 of 48 proxy rows say "No published validation"; appendix item 4 admits several items have one proxy | Minor | Fine as long as the deck's A4 says so; today the strap "Upstream-verified" implies more. |

---

## 3. Trust and liability

**3.1 The disclosure wording.** `evidence-pack-templates.md` §12.1 is good drafting and better than the Deloitte Australia corrected report, which named its toolchain only after the fact. Two problems. First, "Every citation in this deliverable resolves to a source that was fetched and stored with a content hash" is a factual statement that the GE run would make false (resolution 0.2, one attachment unreconciled). The template needs a hard interlock: the statement cannot be rendered unless the build's resolution rate is 1.0 and the reconciliation table shows MATCH for every attached document. The ghost deck says lint checks presence of S02; it should check truth of S02. **[Blocker — fix: S02 fields populated from the build report, not typed.]** Second, "reviewed, edited and approved by named members of [Firm], who take full editorial and professional responsibility" is plural. Today it is one member. A CRO reading "named members" and seeing one name will note the gap. **[Minor — write it in the singular until it is true in the plural.]**

**3.2 "Block not flag".** The claim is the firm's best differentiator and the code apparently does it (README: "block-not-flag ... hash-chained log" in the "what works" column). But the semantic matcher (C4) is "fixture-only / stubbed", so today only exact-string and number matching blocks. Qualitative claims pass through C4 on a stub. A Big-4 reviewer reading the pipeline spec will find C4's "SUPPORTED at or above 0.85 cosine" and ask for the calibration set; there is none (spec open item 1, G1). **[Major — fix: until C4 is calibrated, the deck may contain only number and quotation claims plus the engagement lead's own interpretive text, clearly separated; no model-generated qualitative claim is "verified".]**

**3.3 One-person firm.** Every control in the repo that depends on separation of duties (independent reviewer, signing partner, quality-lead dual sign-off on C11 overrides, verification control owner distinct from engagement lead) is currently a single human. ISQM-style language ("who accepted what", charter §11) without separation is theatre. This is the single most damaging thing a CRO can say and it is true. **[Blocker — see §7.]**

**3.4 No SOC 2 at launch.** The research report is right that SOC 2 does not test accuracy or provenance, and the firm's Processing Integrity control is the right idea. But to an FI vendor-risk officer, SOC 2 is the ticket to the conversation, not the answer. The GA plan's "observation window open" is 9 months away. Until then PLUMB must only sell engagements whose data profile does not require it. **[Major — same structural fix as §1(a) step 4.]**

**3.5 Deloitte precedent.** The materials use Deloitte DEWR well as the failure case (A$440K, fabricated references, partial refund, new APS disclosure clauses in three months). The lesson the repo has not drawn: Deloitte survived because it is Deloitte. A one-person firm with one fabricated citation in a MAS-facing deck does not get a refund negotiation; it gets a name in a supervisory letter. The quality undertaking in `pricing-ladder.md` §3.4 ("corrected at no charge and reported in the engagement file") is the right remedy and the wrong reassurance. **[Major — fix: add a stated kill rule to the undertaking: "If an independent reviewer finds a fabricated or non-resolving source in a delivered deck, PLUMB refunds the Tier-1 fee in full." That is the only undertaking that is louder than the Deloitte story.]**

**3.6 MAS's own words.** Artefact 7 quotes MAS 5.11(a): "independent certifications or external assessments over self-attestations". PLUMB applies this to the client's vendors while being, itself, a self-attesting third party to the FI. A CRO will apply 5.11 to PLUMB. What they would demand before PLUMB touches a MAS-regulated use case: (1) written ZDR and in-region processing from every model vendor; (2) a named reviewer independent of the operator, with CV; (3) PI insurance certificate; (4) incorporated entity and DPO; (5) an information-security questionnaire response; (6) agreement that no customer-level data enters the pipeline in the first engagement; (7) the right to see the gap register and the blocked-claim list, not just the deck. Items 1–6 are founder-checklist items; item 7 is already the design and should be sold as a feature.

**3.7 What a Big-4 partner says about a 48-item instrument with 12 known ambiguities.** "Ambiguity 2 — cap per response vs per consensus — changes every organisation's score. Ambiguity 3 — no rule for the org-level item score — means the headline number is an interim scorer choice. There is no κ. Their own §6 says any configuration putting >15% in Leading must be recalibrated, and they have n = 0." All true. The appendix's honesty is a strength in a methodology file and a liability in a sales conversation. **[Major — fix: resolve ambiguities 1, 2, 3, 6, 8 in v0.2 before G1 (they are decisions, not research), run the 20-item κ subset on the two alpha subjects with the named reviewer as second rater, and move the remainder to a "known limits" slide (A4) in the firm's own words rather than leaving them for the competitor to find.]**

---

## 4. Pricing and positioning stress test

**4.1 Is S$25–85K defensible for what is actually delivered in 20 days?** For the deliverable list in `pricing-ladder.md` §3.2, yes, it is cheap, and the Pertama bands support it. For what the pipeline delivers today, no: the honest Tier-1 product for engagement one is an outside-in scorecard with nine named peers, an executive-stated right-to-win exhibit, two-band value pools from public financials, a gated use-case list with tiers, and a MAS-mapped evidence-pack skeleton. That is worth S$30–45K to an FI CDO twelve months before the MAS inventory deadline, and it can be delivered without onboarding. Price *that* for design partners and stop discounting the full product that cannot yet be delivered. **[Major]**

**4.2 Is "AI-accelerated, human-accountable, source-verified" a claim or a feature?** Today it is a claim. "Human-accountable" is one human; "source-verified" is 0.2 on the only real run. It becomes a feature on the day a named independent reviewer signs a deck with resolution 1.0 and the deck ships with its gap register. Until then, use the one phrase that is already true and that no competitor says: "every claim we could not verify is listed, not hidden." **[Major]**

**4.3 Free benchmark: lead magnet or liability?** For the wedge, liability (see 2.9). A benchmark with n small, every entry capped at 3, no evidence, and respondents self-selected from whoever found the form is not a benchmark; it is a mailing list with a chart. The disclosure line ("prints n ... share self-scored only") is correct and will read as an admission. Launch it for suppliers and mid-market after G2, not before, and never cite it to an FI as a peer set. **[Major]**

**4.4 Design-partner discount: necessary or weakness?** 40–50% off is market-standard for beta and the four conditions in §7 are well chosen. The weakness is not the discount; it is that the discounted product is the full 20-day scope the firm cannot staff. A 40% discount on an undeliverable scope signals inexperience; a full-price Phase-A engagement at S$35K with a written option on Phase B at list signals confidence. **[Minor — reframe, not re-price.]**

**4.5 The retainer name.** "Moving Goalpost" means, in every boardroom in Singapore, "changing the rules after the fact". The explanation in §5 ("the benchmark, the peer set and the regulation all move") does not survive the CFO's first reaction. **[Minor — rename: "Standing Scorecard" or "MAS Clock" retainer.]**

**4.6 The sentence the CDO repeats to the CEO.** From the materials as written, she would say: *"A one-person AI consultancy that says it verifies everything."* That is not good enough; it leads with the two weaknesses. The sentence the materials should make her say: *"For S$40K and four weeks they will show us, against the nine insurers that matter and with every source we can check ourselves, which of our AI use cases will survive MAS's October 2027 inventory test and which three are worth funding."* Every clause of that sentence is deliverable from the Phase-A scope and the GE run, once the run is fixed.

---

## 5. What the Great Eastern run tells a sceptic

**5.1 Governance = 0: sellable, not yet defensible.** `README.md` (run): "no 'AI governance', 'responsible AI', 'model risk', 'FEAT', 'Veritas', 'GenAI' anywhere in the report. Material finding for a MAS-regulated insurer 12 months before AIRM applies." Four reasons a sceptic rejects this from one document:

1. The lexicon is a keyword list, and the same run proves the lexicon is incomplete (it had no pattern for "Managing Director, Group Data and AI"). A 244-page life-insurer annual report with no occurrence of "model risk" is implausible; the extraction defect 2 (two-column interleaving) is a plausible cause of multi-word phrase misses.
2. GEH is ~88% owned by OCBC. OCBC's AR2025 carries an "AI, Digital and Data" strategy (`alpha-targets.md` row I1). A subsidiary's governance may be documented at group level; the finding is "not in the GEH AR", not "does not exist".
3. The instrument itself says outside-in signals "corroborate only, never lift"; they should not headline either. A "material finding" from one T2 source with a single upstream violates the firm's own two-upstream rule for load-bearing claims (R8).
4. "Verified against raw text? Yes" was done by the operator. No independent reviewer has read the raw text.

What *is* defensible and still sellable: "GEH's FY2025 annual report describes production AI with quantified outcomes (L4 on the published rubric) but contains no AI-governance, responsible-AI or model-risk language in our lexicon; we would want to see the group-level framework before scoring D6." That sentence opens a meeting. "Governance = 0" closes one. **[Blocker as written; Major once reworded — fix: expand the lexicon (add "data governance", "ethical", "technology risk", "AI risk", "machine learning", "algorithm"), fix the two-column extraction, re-run, and have the reviewer read the governance and risk sections by eye before this claim appears anywhere.]**

**5.2 The leadership miss.** One visible miss on a 244-page document is survivable only if PLUMB found it first and says so. Here PLUMB did find it and logged it. If the GE deck ever shows "AI/data leadership titles: 0" the "Verified" brand is dead on the spot, because the client's MD of Data & AI will be in the room. The deeper lesson: every extractor is a lexicon until it is validated against human reading, which means the C7 agreement check (10 rejected / 10 accepted) must run on *extractions*, not just on page rejection. **[Major — fix: before any client sees a run, the reviewer reads the management-team pages and the governance section and signs a "human-read" line in the run README.]**

**5.3 Four of five peer sizes blocked.** Strength, and the materials are right to call it "correct behaviour". But a prospect does not see the sandbox; they see a table with four BLOCKED rows and ask why a firm that promises verified peer benchmarking could not fetch AIA's annual report. The block is discipline; the *cause* (no egress from the dev sandbox) is an operational embarrassment that must never reach a prospect. **[Major — fix: no run is shown externally until it has been executed with egress and reconciliation; the sandbox run is an internal artefact.]**

**5.4 How to present run results so blocks read as rigour.** Exactly this, on one page:

1. **Lead with what was verified**, each line with source, hash prefix and page: "FY2025 AR, p.N: AI advisory platform, ~75% adviser prep-time reduction (quote string-matched)". Five to eight such lines. The reader checks one and trusts the rest.
2. **Then the scored signals**, each with its instrument item and the standing caveat in the same font size: "corroborates D1.1; cannot lift above L3 without evidence".
3. **Then "What we could not verify, and why", as a table**: claim · source attempted · reason (unreachable / mismatch / single upstream) · what would resolve it · who holds it (often the client). Title the table "Removed, not footnoted". This is the gap register from C11, surfaced as a feature.
4. **Then "What this run cannot tell you"**: peer percentile (n = 9), governance maturity (document-level signal only), anything requiring interviews. Each with the Tier-1 step that fills it.
5. **Footer**: run ID, build status, resolution rate, quotation pass rate, reviewer name and date of human read.

Never show "Build: FAIL". Show "Released: 5 claims. Withheld: 4 claims (listed)." Same facts, different sentence.

---

## 6. Top 10 fixes, ranked by buyer impact × ease

| Rank | Fix | Owner | Gate | Why this rank |
|---|---|---|---|---|
| 1 | Name the independent reviewer (D3/F4), agree the per-deck fee, record it in the charter template as a real person | Founder | Before any charter is issued (G1) | Every trust claim depends on it; it costs a phone call |
| 2 | Re-run GE with egress, reconcile the attachment, unblock peer sizes, fix extractor defects 1–3 and widen the governance lexicon; reviewer human-reads leadership and governance pages | Founder (fetch, F6) + product | G1 | Turns the one real output from a liability into the first sales asset |
| 3 | Split Tier 1 into Phase A (public data + interviews + instrument, no confidential extracts, no onboarding) and Phase B (confidential data, post-onboarding); price and sell Phase A to design partners | Product (pricing-ladder, charter) + founder | G2 recruitment | Removes the day-5 data fantasy and the SOC 2 objection in one move |
| 4 | Interlock S02 with the build report: disclosure statement renders only when resolution = 1.0 and every attachment is MATCH; unreconciled attachments are BLOCKED for client-facing builds | Product (pipeline, lint) | G1 | Makes "block not flag" true end to end |
| 5 | Drop "percentile" from the Tier-1 promise for the first six engagements; replace S09 with rank-within-named-peers on computed signals; never mix capped and evidence-gated entries | Product (instrument §5.5, ghost deck S09, pricing-ladder) | G1 | Removes a promise that cannot be kept in the wedge |
| 6 | Confirm ZDR / in-region in writing for each LLM vendor (F16); until then, no client data of any class enters the pipeline and the proposal says so | Founder | Before first FI proposal (G2) | CRO gate; also a stated precondition in the charter already |
| 7 | Strip "Big-4 quality" from README and all client-facing text; replace with the measurable claim and the refund-on-fabrication undertaking | Product (README, pricing-ladder §3.4) + founder (insurer approval) | G1 | The phrase invites the exact comparison PLUMB cannot yet win |
| 8 | Resolve instrument ambiguities 1, 2, 3, 6, 8 by decision; put the cap rule on the instrument's first screen and in the respondent brief; report self-view and evidenced view side by side | Product (instrument v0.2, charter §5.1) | G1 | Prevents the "my 5 became a 3" revolt and removes the Big-4's easiest line |
| 9 | Reposition Tier 2 as measurement-design-first (base fee builds baseline and counterfactual; savings share switches on after) and bar holdouts on customer-facing T3+ use cases | Product (pricing-ladder §4, value kit G4) | G2 | Makes outcome pricing sellable to a CRO |
| 10 | Written employer clearance or a documented basis for "not required" (D7), plus the GE/OCBC conflict declaration (F5), filed before the GE run is shown to anyone at GE or OCBC | Founder | Before any GE contact | A vendor-risk officer will ask; "already cleared" with no paper is not an answer |

Not ranked but necessary before GA: re-anchor the Big-4 comparison on Singapore quotes; rename the retainer; add a second interviewer or extend Phase 2; calibrate C4; run the κ subset.

---

## 7. The one thing I would not launch without

**One real deck, on a real company, with resolution 1.0, every attachment reconciled, and QA gate 3 signed by a named reviewer who did not run the pipeline, shipped with its gap register.**

Not the SOC 2, not the entity, not the benchmark n. Those are hygiene and a buyer will give a start-up time on them. What a buyer will not give time on is the product's own name. PLUMB is called *Verified*. Until there exists one artefact where the verification claim has been tested by someone other than its author and found true, every page in this repository is a promise, and the Great Eastern run is evidence against it. The day that deck exists, the rest of the material, which is unusually good, starts working for the firm instead of against it.
