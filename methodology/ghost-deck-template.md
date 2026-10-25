# Storyline and Ghost-Deck Template

**Status: v0.1 draft**

| Field | Value |
|---|---|
| Methodology step | Phase 0 output (ghost deck of action titles, signed before analysis) and Phase 4 deliverable (board-ready storyline deck) |
| Owner | Methodology lead; engagement lead fills it per client; independent reviewer signs QA gate 3 against it |
| Upstream | `../docs/AI first consulting engagement framework.md` (methodology and deliverable list); research note `ai_native_consulting_landscape.md` KQ3 ("Big 4 quality operationalised"); `maturity-instrument.md`; `right-to-win-kit.md`; `value-and-use-case-kit.md`; `../compliance/risk-tiers-and-gates.md`; `../compliance/evidence-pack-templates.md` §12; `../pipeline/verification-pipeline-spec.md` §6.2 |
| How it is used | Phase 0: every title is a hypothesis, prefixed `[H]`. Phase 3: each `[H]` is replaced by a verified claim or the slide is deleted. A slide whose title still reads `[H]` cannot pass deck-export lint. |
| Evidence caveat | The craft rules in §1 come from ex-consultant training material, not from any firm's published QA manual (research note KQ3, Gaps). They are adopted as house rules, not cited as industry standards. |

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Methodology lead | Initial draft: storyline rules, 34-slide ghost deck plus appendix, QA gate 3 reviewer checklist, titles-only worked example |
| v0.1.1 | 2026-10-25 | Product | Red-team review 2026-10-25 applied: R8/R9 "DRAFT — not for board use" banner unless resolution = 1.0 and every attachment reconciled; S02 populated from the build report (Blocker 2 / §3.1); S09 replaced by a ranked list of named peers where core peer n < 15, percentile only where the evidenced peer population has n ≥ 15 (Blocker 3 / §2.3); S08 shows self-view and evidenced view side by side (Major / §2.2); §2.4 run-presentation format "Released: N claims. Withheld: M claims (listed)", never "Build: FAIL" (Blocker 6 / §5.4) |

---

## 1. Storyline rules (one page)

| # | Rule | Specification | Test applied at QA gate 3 |
|---|---|---|---|
| R1 | SCQA executive summary | Slide S03 opens with Situation, Complication, Question, Answer in that order, four short paragraphs or four labelled boxes. The Answer is the recommendation. No new fact appears in the exec summary that is not on a later slide. | Reviewer labels the four elements; any missing element fails. |
| R2 | Pyramid | Recommendation first, then the 3–4 supporting lines (where you are, why you exist, where to improve, which use cases), then evidence slides, then appendix. Think bottom-up, present top-down. Each section divider restates the section's one claim. | Each section's slides must all support the divider claim; a slide that supports no claim is deleted. |
| R3 | Action titles | Every title is a full-sentence claim, ≤15 words, ≤2 lines at 18–20 pt, active voice, quantified where the slide carries a number, states a conclusion not a process ("Meridian scores 47 of 100", never "Maturity assessment results"). | Word count checked mechanically; any title describing the exhibit rather than the finding fails. |
| R4 | Horizontal-flow test | Reading the titles alone, in order, cover to roadmap, tells the complete argument with no gap and no repetition. | Reviewer reads titles only (no body) and writes the story in three sentences; if they cannot, the gate fails. |
| R5 | One message per slide | One claim, one exhibit. A title that joins two claims with "and" or "but" is split into two slides (a list inside one claim is allowed). A slide that repeats a point already made is deleted. | Reviewer flags any slide with two conclusions or any duplicate. |
| R6 | Source line | Every slide carrying a number, quotation or ranking shows, bottom-left, 9–10 pt: `Source: <T-tier> <document>, <date>; confidence: <label>`. Tier T1–T5 per pipeline C8. Label per pipeline C9: `filed` / `vendor-estimate` / `model-inferred` / `interview-anecdote`, plus `correlational` / `causal` where a relationship is asserted. Multiple sources are semicolon-separated. T5 never appears as a source of record. | Lint checks presence; reviewer checks the tier and label are correct for the sample. |
| R7 | So-what | Every evidence slide ends with one line, boxed, beginning "So what:" that states the implication for the recommendation. If the so-what cannot be written, the slide is appendix material. | Reviewer reads each so-what and confirms it follows from the exhibit and feeds a later slide. |
| R8 | No unverified number leaves the deck | Every number traces to a claim in state RELEASED in the claim store (pipeline C3–C11). Load-bearing numbers (anything in S03–S04, scorecards, value-pool sizing, business cases) have two independent upstreams or are labelled "directional, single-upstream" with recorded rationale. Blocked claims are removed, never footnoted "unverified". Claims withheld under pipeline C2a (attached document, publisher hash unreconciled) are listed in A6 as "awaiting publisher reconciliation" and never appear on a slide with the attached label. **DRAFT banner:** unless the build report shows citation resolution = 1.0, every attached document reconciled MATCH and build profile = client, every slide carries the header banner "DRAFT — not for board use" and the deck cannot be exported as a deliverable. | Build asserts zero BLOCKED in the released set; lint reads the build report and applies the banner; reviewer re-verifies every exec-summary number and the 30-claim sample. |
| R9 | AI-use disclosure slide | S02 carries the full-form statement from `evidence-pack-templates.md` §12.1 and names the human approver. Its verification fields are populated from the build report, never typed. The verification statement renders only when R8's banner conditions are met; otherwise S02 shows the "DRAFT — not for board use" banner in its place, with the released/withheld counts and resolution rate. Every subsequent slide footer carries the short form (§12.2) under the same rule. The deck cannot be exported without S02. | Lint (pipeline S8) checks presence, that the approver field is filled, and that the statement's figures equal the build report (truth, not presence). |
| R10 | Charts | Action title, labelled axes with units, legend, source line, callouts; 3–5 series maximum; ≤2 font families; 3–4 colours; fonts never shrunk to fit. | Reviewer spot-checks every chart in S08–S23. |
| R11 | Leave-behind standard | The deck must stand without a presenter. Anything that only makes sense when spoken is rewritten or moved to speaker notes. | Reviewer has not attended any working session and reads cold. |
| R12 | Human view before AI synthesis | The engagement lead writes the `[H]` ghost titles before the Phase 1 agents run. Phase 3 titles that differ from the `[H]` hypothesis are marked in the engagement file with the evidence that changed them. | Engagement file shows a dated ghost deck signed at Phase 0. |

---

## 2. The ghost deck

### 2.1 Conventions

| Element | Convention |
|---|---|
| Slide ID | `S01`–`S34` main body; `A1`–`A7` appendix. IDs are stable; a deleted slide leaves a gap rather than renumbering. |
| Title template | `[brackets]` mark the client-specific claim to be filled. `{n}` marks a verified number. Templates are written as the strongest expected form; weaken to what the evidence supports, never the reverse. |
| Exhibit | Type, then the methodology artefact it is produced from. Exhibits are rendered from the structured output of that artefact, not redrawn by hand. |
| Data inputs | What must be in the claim store or evidence register before the slide can be built. |
| QA gate | The gate(s) that must have passed for the slide's content. QA1 = automated pipeline (`verification-pipeline-spec.md` S1–S6). QA2 = client-input and primary-research checks (perception variance computed; every quote matched to transcript; anecdotes separated from patterns). QA3 = independent reviewer (§3 of this file). Lint = deck-export lint (pipeline S8). Partner = lead partner signs the finding. |
| Variable-count sections | "Why you exist" carries 3–5 reason slides (S14–S18); "Which use cases" carries one slide per selected domain, 2–5 (S24–S28). Unused IDs are deleted, not left blank. Target length: 30–35 slides plus appendix. |

### 2.2 Slide placeholders

| ID | Section | Draft action-title template | Exhibit (type; source artefact) | Data inputs required | QA gate passed |
|---|---|---|---|---|---|
| S01 | Cover | `[Client]`: Verified Enterprise AI Journey Assessment — board read-out, `[date]` (cover; title rule R3 does not apply) | Cover block: client, date, deliverable ID and version, PLUMB mark, "AI-assisted, human-accountable" strap | Deliverable ID from engagement file | Lint |
| S02 | AI-use disclosure and verification statement | This deck is AI-assisted, human-accountable, and every citation was verified before release *(title renders only when R8 banner conditions are met; otherwise: "DRAFT — not for board use: `{n}` claims released, `{m}` withheld and listed")* | Full-form statement (`evidence-pack-templates.md` §12.1): tools, models, regions, retention; scope of AI assistance; verification steps (fields from the build report); limitations; approver; corrections contact | Build report (resolution rate, attachment reconciliation, released/withheld counts, build profile); model/vendor register with ZDR confirmation dates; QA3 worksheet summary (resolution rate, support rate, fabricated count); approver name | QA3, Lint (truth of S02), Partner |
| S03 | Executive summary (SCQA) | `[Client]`'s `[named strength]` is `[hollowing / eroding / strengthening]`; `[n]` AI domains `[recover / extend]` `[the margin / the position]` | SCQA four-box: Situation (position vs peers), Complication (what the scorecard and hollowing check show), Question, Answer (the 3–5 pools and the headline use cases) | Every number and quotation here is load-bearing by default (pipeline C3); all must be RELEASED with two upstreams | QA1, QA2, QA3 (100% line-by-line), Partner |
| S04 | Executive summary (answer detail) | `{n}` gated use cases, led by `[use case]`, pay back within `{n}` months on conservative cases | Three-column answer: reasons you exist (3–5) · value pools (3–5, Band 2 range) · use cases (9–15, score, tier, GO status); plus the decision asked of the board | Right-to-win exhibit; value-pool table; use-case portfolio; business-case conservative scenarios | QA1, QA3 (100% line-by-line), Partner |
| S05 | Context and peer set | `[Segment A]` and `[segment B]` carry most of `[Client]`'s profit, so they anchor this assessment | Segment profit bridge and scope statement: lines of business, geographies, the three value lenses in scope, data the client supplied | Engagement charter scope; client P&L by segment (QA2) or filed segment note (T1/T2) | QA1, QA2 |
| S06 | Context and peer set | `{n}` core peers were selected by a documented funnel, including `{n}` exited `[insurers / firms]` | Peer-set protocol exhibit: funnel (seed codes + named competitors → TNIC-style text similarity → 0.3x–3x size filter → same regulatory regime → 5–12 core + labelled secondary tier, exited peers included), with named peers and exclusion reasons (framework doc, Phase 1) | Peer-set register with scores per funnel stage; data-availability gaps per peer (ACRA / exchange / DART / EDINET / none) | QA1 |
| S07 | Context and peer set | `[Client]` ranks `{k}` of `{n}` on economic profit `[and has slipped / gained {n} places since FY{yyyy}]` | Competitive ranking exhibit: economic-profit bar by peer, KPI percentile strip (gross margin, capex/sales, growth), move-threshold scorecard (framework doc, "competitor benchmarking") | NOPLAT, invested capital, WACC per peer from filings; derivation computed in code (pipeline architecture note); confidence label per peer | QA1 |
| S08 | Where you are | `[Client]` scores `{C}` of 100, `[band]`, with `[value-axis headline, e.g. value attribution still unmeasured]` | Two-axis maturity scorecard: capability bar 0–100 with four bands and the 50-line production boundary, shown as **self-view (uncapped) and evidenced view (cap rule applied) side by side**, with the per-item gap rendered as the client's artefact to-do list; value-axis four-cell profile (V1–V4) beside it; evidence coverage %; "self-report-dominant" flag if coverage <60% (`maturity-instrument.md` §1, §4, §5.1–5.4) | 48 item scores after cap rule; V1–V4 with evidence; evidence register coverage; assessor adjustments with reasons | QA1, QA2, Partner |
| S09 | Where you are | **Core peer n < 15 (the default for Singapore FI engagements):** `[Client]` ranks `{k}` of `{n+1}` among `{n}` named peers on `[signal]`, and last on `[weakest signal]`. **Only where the evidenced peer population has n ≥ 15:** `[Client]` sits at the `{p}`th peer percentile overall but `{p}`th on `[weakest dimension]` | **Ranked-list exhibit (n < 15):** one row per named core peer plus the client, ordered, each peer's value shown, on the outside-in signals that *were* computed (and the capability score only where peers have evidenced scores); n disclosed; the "peer n insufficient" line from the instrument (§5.5) printed under the table; no percentile and no global-percentile substitute. **Percentile exhibit (n ≥ 15):** eight dimension scores vs peer median, n disclosed, population stated. The Tier-0 self-scored pool and evidence-gated engagement scores are never pooled (`instrument/README.md`) | Peer-set register (named peers, funnel stage); per-peer signal values in RELEASED state; benchmark extract with `population` for the percentile case; peer-set definition date | QA1 |
| S10 | Where you are | `[ExCo / operating managers]` rate `[dimension]` a full level `[above / below]` `[the other group]` | Leadership-perception variance exhibit: per-dimension ExCo-vs-operating gap with sign, items flagged σ>1.0 with roles at each extreme, dimensions marked "leadership not aligned" (`maturity-instrument.md` §5.3) | Raw self-report levels from 10–30 respondents (≥5 for σ), respondent roles; computed before cap rule | QA2 |
| S11 | Where you are | `[Compliance sub-dimension]` reaches level `{n}`; `[named controls]` do not yet exist | Compliance sub-dimension exhibit: eight sub-dimensions scored 0–4 on the OWASP governance ladder with evidence class per cell; D6 items from `maturity-instrument.md` §3 D6 and `../docs/AI framework compliance standards layer.md` sub-dimension table | D6.1–D6.6 scores with artefact IDs; inventory record presence; kill-switch test record (O class); vendor-evidence review | QA1, QA2 |
| S12 | Where you are | `[Instrument]` binds `[Client]` from `[date]`; `{n}` proposed domains fall under `[its high-materiality / Annex III / override]` track | Regulatory-exposure matrix: jurisdictions the client operates or sells into × proposed use-case domains; cells carry instrument, binding date, penalty ceiling, control forced; three status colours (binding / dated / voluntary-draft) (`../compliance/regulatory-status-map.md`; compliance doc §"exposure map") | Jurisdiction list from charter; domain list from S21; status map rows with [VERIFY] flags carried visibly | QA1 |
| S13 | Why you exist | `{n}` capabilities pass all six right-to-win criteria; `[a further {n} are temporary edges / the list raised the incoherence flag]` | Six-criterion scorecard, one row per candidate: C1–C6 score/class, total /12, verdict R1–R3, AI-era tag column; incoherence-flag statement above the table if raised (`right-to-win-kit.md` §1.5, §6) | Long list of 8–15 candidates with provisional evidence packs; scores and evidence classes per cell; κ result for LLM-coded cells | QA1, QA2, Partner |
| S14 | Why you exist — reason 1 | `[Capability statement ≤20 words naming customer benefit and comparator]` is a `[strengthening / hollowing / eroding]` advantage | Reason block: statement; evidence pack (3–5 cited facts with class F/V/M/I, ≥1 F or V); C1–C6 scores; verdict; AI-era tag with H1–H5 results; implication for domain screen; open items (`right-to-win-kit.md` §6.1) | Evidence pack facts in RELEASED state; interview quotes passed string match (§5.4); hollowing-check metrics vs peer set | QA1, QA2, Partner |
| S15 | Why you exist — reason 2 | as S14 | as S14 | as S14 | as S14 |
| S16 | Why you exist — reason 3 | as S14 | as S14 | as S14 | as S14 |
| S17 | Why you exist — reason 4 (optional) | as S14 | as S14 | as S14 | as S14 |
| S18 | Why you exist — reason 5 or temporary edge (optional) | `[Candidate]` is a benefit without a barrier, not a reason to exist | Same block; verdict "temporary edge" per R2; shown so the client sees why it is not headlined | as S14 | as S14 |
| S19 | Why you exist — coherence and hollowing summary | `{n}` of `{n}` strengths are hollowing or eroding, which makes them `[Client]`'s largest value pools | Hollowing summary: H1–H5 grid per passing strength; tag per strength; hand-off arrow to domain type (invest / defend / reshape) with the metric that defines each candidate pool (`right-to-win-kit.md` §2.2–2.3, R5) | H1–H5 results; margin and pricing-power series vs peer median, 3-year; attacker map | QA1, Partner |
| S20 | Where to improve | `[Leaf KPI 1]`, `[leaf KPI 2]` and `[leaf KPI 3]` move most of `[Client]`'s economic profit | Driver tree: economic profit → revenue / cost / capital / risk branches → operational leaves, pruned to leaves with an owner; sensitivity bar per leaf; source convention per leaf (AR / EC / JP / APP / REG / IND) (`value-and-use-case-kit.md` §1) | KPI extract from client (QA2) or outside-in proxies; peer medians per leaf; sensitivity computed in code | QA1, QA2 |
| S21 | Where to improve | Of `{n}` domains screened, `[domain A]`, `[domain B]` and `[domain C]` clear the value-feasibility bar | Domain screen 2×2: 10–15 candidate domains plotted on value (4 criteria) × feasibility (4 criteria), 2–5 selected, two-core-plus-one-support default marked, fast/slow pairing shown (`value-and-use-case-kit.md` §2.1–2.3) | Scores per criterion with rationale; sponsor named per selected domain; AI-era tag hand-offs from S19 | QA1, Partner |
| S22 | Where to improve | The `{n}` pools are worth `[S$X–Y]` realised-to-date against a `[S$Z+]` technical ceiling | Value-pool table with two-band sizing per pool: Band 1 technical potential (MGI ceiling × function cost) and Band 2 realised-to-date (survey-reported range, RCT where available); planning base stated; T-tier and correlational/causal label per number; oversizing note (`value-and-use-case-kit.md` §2.4) | Function cost base per domain (client extract or filed); ceiling and realised references with upstream pairs; ladder position chosen per pool | QA1, QA3 (all sizing numbers), Partner |
| S23 | Which use cases — portfolio | `{n}` use cases pass all five hard gates; `{n}` are Likely wins, `{n}` Calculated risks | Portfolio view: 9–15 use cases by domain; matrix score /100 with bucket; tier T1–T4 with override IDs; gate status G1–G5; GO / CONDITIONAL / ESCALATE / NO-GO; ladder rung L1–L3; deferred candidates listed with the gate they failed (`value-and-use-case-kit.md` §3.1–3.2; `risk-tiers-and-gates.md` §2, §5) | Scored matrix per use case with evidence for any 5; intake scores C1–C5 and overrides; signed gate checklists | QA1, Partner |
| S24 | Which use cases — domain 1 | `[Use case A]`, `[use case B]` and `[use case C]` lead the portfolio at tier `[Tn–Tn]` | Domain card: 3–5 use cases with value / feasibility / time / reuse / fit scores, penalties, total; tier and override; gate G1–G5 ticks; technique and agent archetype; ladder rung; named owner; link to business case (`value-and-use-case-kit.md` §3.1–3.4) | Per-use-case matrix rows; owner name and KPI; baseline extract reference; tier worksheet | QA1, QA2 |
| S25 | Which use cases — domain 2 | as S24 (title states the domain's distinctive finding, e.g. a tier floor or a payback claim) | as S24 | as S24 | as S24 |
| S26 | Which use cases — domain 3 | as S24 | as S24 | as S24 | as S24 |
| S27 | Which use cases — domain 4 (optional) | as S24 | as S24 | as S24 | as S24 |
| S28 | Which use cases — domain 5 (optional) | as S24 | as S24 | as S24 | as S24 |
| S29 | Business cases summary | Conservative cases clear payback norms for `{n}` of `{n}`; `{n}` drop a ladder rung | Business-case summary table: per use case, conservative / base / optimistic annual benefit by lens, 3-year TCO incl. run and token cost, payback months, NPV; payback norm for type; rung after conservative-case rule; do-nothing trajectory (`value-and-use-case-kit.md` §4) | Seven-section business case per use case; system-measured baselines (G3); inference-price sensitivity | QA1, QA3 (all business-case numbers), Partner |
| S30 | Responsible-AI and agent gate summary | `{n}` use cases are GO, `{n}` CONDITIONAL on `[named conditions]` | Gate summary: per use case, final tier, overrides fired, agent-gate status (identity, action classes, tool classes, lethal-trifecta check, kill switch tested Y/N), decision with conditions, owners and dates; control checklist cost line per tier (`risk-tiers-and-gates.md` §4–§7; `evidence-pack-templates.md` artefacts 1–9) | Signed gate checklists; kill-switch test records; vendor-assessment artefact 7 per model route; ISO 42001 / NIST AI RMF mapping per control | QA1, Partner |
| S31 | Roadmap 30/60/90 | The first 90 days build `[the inventory, baselines and the first control group]` | 30/60/90 swim-lane: governance (inventory, policy, committee), data and baselines (G3 extracts), first use case to control-group design (G4), people and change (70% of effort), decision points | Owner per lane; dependencies from CONDITIONAL items in S30 | Partner |
| S32 | Roadmap 6/12 months | By month 12, `[use cases]` are in production with finance-reconciled value | 6/12-month roadmap: per domain, use cases by rung with production dates, value-tracking milestones (V3 level targets), re-tier triggers, regulatory dates from S12 overlaid | Business-case timelines; regulatory binding dates; capacity constraints stated by client | Partner |
| S33 | Measurement design | Every use case gets a system baseline, holdout group and stop condition before build | Measurement design table: per use case, baseline source system and period, control design (A/B / holdout / matched), cadence, statistical owner, finance reconciliation rule, pause and stop triggers; becomes the basis of outcome-priced follow-on (`value-and-use-case-kit.md` §3.2 G3–G4, §4 row 6) | Baseline extracts; named statistical owner; finance attribution rule (D8.4) | QA2, Partner |
| S34 | Risks and open items | `{n}` open items, led by `[item]`, must close before `[the board decision / build]` | Risk and open-item register: implementation, benefit-shortfall, data, adoption, vendor, regulatory risks with likelihood × impact; [VERIFY] items carried from the status map; single-upstream numbers re-labelled directional; evidence gaps disclosed rather than estimated | Gap register from pipeline C11; [VERIFY] register; risk register entries (artefact 3) | QA1, Partner |
| A1 | Appendix — evidence log | Every claim in this deck resolves to a fetched, hashed source | Evidence log: claim ID, slide, claim text, source(s), tier, confidence label, upstream pair, fetch date, hash prefix, state (pipeline C1–C9) | Claim store export filtered to RELEASED | QA1, Lint |
| A2 | Appendix — source tiers | Sources are tiered T1–T5 and T5 is never a source of record | Source-tier table with counts per tier used in the deck and the tier rule table (pipeline C8) | Source store export | QA1 |
| A3 | Appendix — confidence labels | Every metric carries one of four confidence labels and a causal label where a relationship is claimed | Label definitions (filed / vendor-estimate / model-inferred / interview-anecdote; correlational / causal) with counts per label in the deck (pipeline C9) | Claim store export | QA1 |
| A4 | Appendix — methodology notes | Scores follow published anchors, weights and gates that the client can re-run | Method summary: maturity instrument structure, weights and cap rule; six-criterion test and tag rules; domain screen criteria; matrix weights and gates; tier intake and overrides; realisation discounts marked "working value"; known gaps from each kit's gap table | Kit version numbers; working-value register | Partner |
| A5 | Appendix — benchmark n and composition | The peer benchmark holds n=`{n}` evidenced entries, defined on `[date]`; self-scored entries are reported separately | Benchmark composition: n by industry × sub-region × size band; evidence-gated vs self-scored share; global n; date of definition; κ test-subset result (`maturity-instrument.md` §5.5, §7) | Benchmark database extract | QA1 |
| A6 | Appendix — gap and [VERIFY] register | `{n}` claims were removed rather than flagged; `{n}` items remain unconfirmed | "Removed, not footnoted" table per §2.4 (claim · source attempted · reason · what would resolve it · who holds it), including C2a "awaiting publisher reconciliation" rows, and the [VERIFY] register carried from the regulatory-status map | Pipeline gap register; status-map [VERIFY] rows relevant to S12 | QA1, Lint |
| A7 | Appendix — reviewer worksheet summary | The independent reviewer sampled `{n}` claims and found `{n}` fabricated or non-resolving sources | QA3 worksheet summary: reviewer identity and eligibility, sample composition, counts per label, rates against thresholds, C7 agreement, sign-off date (pipeline §6.2 P6–P8) | Signed worksheet | QA3 |

### 2.3 Section dividers

| Divider before | Divider claim template (restates the section's one message) |
|---|---|
| S05 | `[Client]` competes in `[segments]` against `{n}` documented peers |
| S08 | `[Client]` is `[band]` on capability and `[value-axis headline]` on value |
| S13 | `[Client]` exists for `{n}` reasons, `{n}` of which AI is `[hollowing / eroding]` |
| S20 | `{n}` domains hold `[S$X–Y]` of realised value |
| S23 | `{n}` gated use cases, `{n}` of them GO, deliver it |
| S31 | The first 12 months build the controls, baselines and first production value |


### 2.4 Presenting a run result (one page; red-team review §5.4)

Any pipeline run shown outside the firm (a prospect letter, a Phase A read-out, a sales conversation) uses exactly this format. Sandbox runs without egress or with unreconciled attachments are internal artefacts and are never shown externally.

| # | Block | Content |
|---|---|---|
| 1 | What was verified | Five to eight lines, each with source, hash prefix and page: e.g. "FY2025 AR, p.N: AI advisory platform, ~75% adviser prep-time reduction (quote string-matched)". The reader checks one and trusts the rest |
| 2 | Scored signals | Each with its instrument item and the standing caveat in the same font size: "corroborates D1.1; cannot lift above L3 without evidence" |
| 3 | What we could not verify, and why | Table titled **"Removed, not footnoted"**: claim · source attempted · reason (unreachable / mismatch / single upstream / awaiting publisher reconciliation) · what would resolve it · who holds it (often the client) |
| 4 | What this run cannot tell you | Peer percentile (state n), governance maturity (document-level signal only), anything requiring interviews; each with the Tier-1 step that fills it |
| 5 | Footer | Run ID, resolution rate, quotation pass rate, reviewer name and date of human read |

**Outcome sentence.** Never "Build: FAIL" or "Build: PASS". Always: **"Released: N claims. Withheld: M claims (listed)."** Same facts, different sentence. `plumbverify` and `plumbresearch` render this sentence in their CLI output, `report.md` and `signals.md`; the PASS/FAIL gate state stays in `report.json` for the operator.

Single-document findings (e.g. a keyword absence in one annual report) are presented as **a question to put to management**, never as a conclusion: state the document, the lexicon's known limits, what was not examined (group-level documents), and that the two-upstream rule for load-bearing claims is not met.

---

## 3. Independent-reviewer checklist for QA gate 3

Eligibility (pipeline §6.2 P1): the reviewer did not run the agents, did not author module drafts and is not the engagement lead. The reviewer works from the candidate deck, the claim store and the source store, and has not attended client working sessions.

### 3.1 Checklist

| # | Check | Method | Pass condition | Result | Note |
|---|---|---|---|---|---|
| 1 | Ghost deck on file | Open engagement file; confirm a dated `[H]` ghost deck signed at Phase 0 exists and that title changes are logged with evidence | Present and signed | ☐ | |
| 2 | Horizontal-flow test | Read titles only, S01–S34, no body text. Write the argument in three sentences. Mark any gap (a title that does not follow from the previous) and any repetition | Story reconstructable; zero gaps; zero repeats | ☐ | |
| 3 | Action-title form | Count words in every title; check full-sentence claim, active voice, ≤2 lines, no exhibit descriptions, no `[H]` or `[bracket]` residue | 100% ≤15 words; zero residue | ☐ | |
| 4 | One message per slide | For each slide, state its single claim; flag any slide with two conclusions joined by "and"/"but", or any slide repeating an earlier one | Zero flags, or flags resolved by split/delete | ☐ | |
| 5 | So-what test | Read each so-what line on S05–S30; confirm it follows from the exhibit and is used by a later slide (name the slide) | 100% follow and are used | ☐ | |
| 6 | Exec summary, line by line | For every number and quotation on S03–S04: re-fetch cited URL live; open hashed copy and confirm hash; locate passage; label full / partial / none / broken; quotations visually exact-matched; load-bearing numbers traced to two distinct upstream termini | 100% full support; 0 quotation failures; 100% two-upstream (or labelled directional with rationale) | ☐ | |
| 7 | 30-claim sample | Build the sample per pipeline §6.2 P3: (a) all exec-summary numbers and quotations; (b) ≥2 load-bearing claims per research module; (c) ≥5 qualitative claims; (d) fill to 30 at random. Apply P4 to each | Resolution 100%; load-bearing full support ≥95%; fabricated or non-resolving 0; quotation failures 0; no AI-generated or farm page cited | ☐ | |
| 8 | Source-line format | On every slide with data, check `Source: <T-tier> <doc>, <date>; confidence: <label>` is present and that tier and label match the claim store for sampled claims | 100% present; tier/label errors 0 in sample | ☐ | |
| 9 | C7 agreement | Inspect 10 pages the pipeline rejected and 10 it accepted; record agreement | Recorded; disagreements logged | ☐ | |
| 10 | Scorecard integrity | Recompute C from the 48 item scores and weights (`maturity-instrument.md` §5.1); confirm band assigned on unrounded value; confirm cap rule applied where no artefact logged and self-view shown beside evidenced view; confirm n≥15 in one population for any percentile, otherwise S09 is the ranked list of named peers with n disclosed | Recomputation matches; cap rule evidence present; no pooled or sub-15 percentile | ☐ | |
| 11 | Right-to-win integrity | Confirm every headline reason scores 2 on C1–C6; temporary edges not headlined; incoherence flag stated if >6 passed; every hollowing tag has H1 pass + (H2 or H3 fail) on file | All rules R1–R5 satisfied | ☐ | |
| 12 | Sizing integrity | Every value pool shows both bands; planning base = Band 2 or Band 1 × discount cross-checked; any number above survey top-end carries a stated top-decile reason | 100% two-band | ☐ | |
| 13 | Gate integrity | Every use case on S23 has a signed gate checklist; tier matches intake score plus overrides; no NO-GO or ESCALATE item presented as a recommendation; CONDITIONAL items carry owner and date; no agentic use case with an irreversible tool in the Autonomous class above T1 | 100% | ☐ | |
| 14 | Disclosure slide | S02 carries §12.1 full form with approver named and figures equal to the build report; footers carry §12.2 short form; A7 figures match the reviewer's own worksheet; if resolution < 1.0 or any attachment unreconciled, the DRAFT banner is present and the statement absent | Present, consistent and true | ☐ | |
| 15 | Blocked-claim overrides | Count C11 dual-sign-off overrides in the engagement file; confirm each has engagement-lead and quality-lead signatures and rationale | Count reported; signatures complete | ☐ | |
| 16 | Chart standard | Every chart: action title, axis labels with units, legend, source line, ≤5 series | 100% | ☐ | |

Any single failure on checks 2, 6, 7, 13 or 14 returns the deck to the pipeline. After remediation the reviewer re-samples the failed claims plus 10 fresh random claims (pipeline P7).

### 3.2 Sign-off block

```
QA GATE 3 — INDEPENDENT REVIEW                       Status: v0.1 draft
Client: ______________________  Deliverable ID / version: ______________
Reviewer (name, role): ______________________
Eligibility confirmed (did not run agents / did not author / not engagement lead): [ ] yes

Horizontal-flow story in three sentences:
1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

Sample: total claims ____  exec-summary (a) ____  module fill (b) ____  qualitative (c) ____
Citation resolution ____%   Load-bearing full support ____%   Quotation failures ____
Fabricated / non-resolving sources ____   Two-upstream pass ____%   Tier/label errors ____
C7 agreement: rejected ___/10  accepted ___/10      C11 overrides in file ____

Decision:  [ ] SIGNED — release    [ ] RETURNED — checks failed: ____________________
Reviewer signature: ____________________  Date: __________  Time logged (h): ______
Lead partner acknowledgement: ____________________  Date: __________
Filed in engagement file; summarised in EP-10 and A7.
```

---

## 4. Titles-only worked example

**ILLUSTRATIVE ONLY.** The client, "Meridian Straits General Insurance" (MSGI), is invented: a fictional Singapore mid-market general insurer writing motor, home, SME commercial and travel lines. Every number, peer, date and finding below is made up to demonstrate the horizontal flow. None is a fact, none is sourced, and in a real deck each would carry a source line and a RELEASED claim ID or be removed. Regulatory dates referenced (e.g. MAS AIRM binding dates) carry [VERIFY] flags in `../compliance/regulatory-status-map.md` and are used here only as placeholders.

| ID | Section | Action title (words) | What it must hand to the next title |
|---|---|---|---|
| S01 | Cover | Meridian Straits General Insurance: Verified Enterprise AI Journey Assessment — board read-out (cover) | — |
| S02 | Disclosure | This deck is AI-assisted, human-accountable, and every citation was verified before release (12) | Licence to trust what follows |
| S03 | Exec summary | Meridian's claims-speed edge is hollowing; three AI domains can recover the margin (12) | The whole argument in one line |
| S04 | Exec summary | Twelve gated use cases, led by claims triage, pay back within 24 months (13) | The decision asked of the board |
| S05 | Context | Motor and SME commercial carry most of Meridian's profit, so they anchor this assessment (14) | Where to look |
| S06 | Context | Nine core peers were selected by a documented funnel, including two exited insurers (13) | Against whom |
| S07 | Context | Meridian ranks third of ten on economic profit but has slipped two places since FY2023 (15) | The complication, outside-in |
| S08 | Where you are | Meridian scores 47 of 100, top of Emerging, with value attribution still unmeasured (13) | Capability below the production boundary |
| S09 | Where you are | Meridian ranks fourth of ten named insurers on AI disclosure, and last on governance language (15) | The weakest dimension (ranked list; n = 9 peers is below the percentile minimum) |
| S10 | Where you are | ExCo rates data foundations a full level above the managers who run them (13) | Why the board may be surprised |
| S11 | Where you are | Governance reaches level 2; the inventory, testing and kill-switch controls do not yet exist (14) | What the gates will demand |
| S12 | Where you are | MAS AIRM binds Meridian from October 2027; two proposed domains fall under its high-materiality track (15) | The regulatory clock |
| S13 | Why you exist | Four capabilities pass all six right-to-win criteria; a fifth is a temporary edge (13) | The list to be examined |
| S14 | Reason 1 | Same-day motor claims settlement, where peers take five days, is a strengthening advantage (13) | Invest domain: claims |
| S15 | Reason 2 | The 1,400-agent tied distribution network still wins SME accounts but its margin is hollowing (14) | Reshape domain: agent servicing |
| S16 | Reason 3 | Proprietary flood and telematics data gives motor pricing a barrier rivals cannot buy (13) | Asset beneath the model layer |
| S17 | Reason 4 | Underwriter expertise in SME commercial is a right to win that AI is eroding (14) | Defend domain: SME underwriting |
| S18 | Temporary edge | Early chatbot adoption is a benefit without a barrier, not a reason to exist (14) | Why it is not headlined |
| S19 | Coherence | Two of four strengths are hollowing or eroding, which makes them Meridian's largest value pools (15) | Hand-off to the driver tree |
| S20 | Where to improve | Claims leakage, agent commission and SME loss ratio move most of Meridian's economic profit (14) | The leaves that matter |
| S21 | Where to improve | Of twelve domains screened, claims, SME underwriting and agent servicing clear the value-feasibility bar (14) | The 2–5 domains |
| S22 | Where to improve | The three pools are worth S$18–26M realised-to-date against a S$60M+ technical ceiling (12) | Two-band sizing; planning base |
| S23 | Portfolio | Twelve use cases pass all five hard gates; seven are Likely wins, five Calculated risks (15) | The gated list |
| S24 | Domain 1 | Claims triage, document extraction and fraud flagging lead the portfolio at tier T2–T3 (13) | Headline use cases |
| S25 | Domain 2 | SME underwriting copilots score well but carry a T4 floor under OV-02 (12) | The compliance cost |
| S26 | Domain 3 | Agent-servicing automation offers the fastest payback, with one L3 redesign candidate (11) | The quick win and the bold move |
| S27 | Domain 4 | — not used; three domains selected | — |
| S28 | Domain 5 | — not used | — |
| S29 | Business cases | Conservative cases clear payback norms for ten of twelve; two drop a ladder rung (14) | CFO-grade numbers |
| S30 | RAI / agent gate | Nine use cases are GO, three CONDITIONAL on tested kill switches and signed risk acceptance (15) | What must be true before build |
| S31 | Roadmap 30/60/90 | The first 90 days build the inventory, baselines and claims-triage control group (12) | Immediate actions |
| S32 | Roadmap 6/12 | By month 12, claims triage and agent servicing are in production with finance-reconciled value (14) | The year-one promise |
| S33 | Measurement | Every use case gets a system baseline, holdout group and stop condition before build (14) | Basis for outcome pricing |
| S34 | Risks | Three open items, led by the MAS AIRM text, must close before the board decision (15) | Honest close |

Flow test on the example (what a reviewer should be able to write from titles alone): *Meridian is a mid-table, Emerging-maturity insurer whose headline strength, fast claims, is still real but whose distribution and underwriting advantages are losing margin to AI-enabled rivals. Three domains, claims, SME underwriting and agent servicing, hold S$18–26M of realisable value, and twelve gated use cases, nine already GO, recover it within 24 months if the first 90 days build the inventory, baselines and control groups the gates require. Three open items, led by the MAS text, must close first.*

---

## 5. Open items for v0.2

| Item | Why it matters | Owner |
|---|---|---|
| Decide whether S03 and S04 collapse into one slide for sub-S$50K engagements | Fixed-fee tier may not justify a two-slide exec summary | Engagement lead |
| Add a deck-export lint rule for the ≤15-word title count and `[H]` / `[bracket]` residue | Removes a manual step from QA3 check 3 | Pipeline lead |
| Test the horizontal-flow test with a reader who has never seen PLUMB material | Rule R4 is currently untested on outsiders | Quality lead |
| Agree the typography and colour tokens with the brand work | R10 currently states the craft-canon numbers only | Methodology lead |
| Confirm whether the engagement letter requires the client to receive A1 (evidence log) in machine-readable form | Procurement clauses (APS, PSPC) may require it | Compliance lead |
