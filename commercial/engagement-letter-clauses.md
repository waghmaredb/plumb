# Engagement Letter — Drafting Notes and Model Clauses

**Status: v0.1 draft**
**Owner:** Founder + counsel (Entity & legal workstream)
**Nature of this document:** **Model wording, for counsel review, not legal advice.** Nothing here has been reviewed by a Singapore-qualified lawyer. Every clause is a starting position to be redrafted by counsel against the entity's PI/cyber insurance terms and the client's own paper. Items marked **[VERIFY]** rest on secondary sources.
**Related:** `engagement-charter-template.md` (Schedule 1 of the letter), `data-processing-addendum-outline.md` (Schedule 2), `conflict-check-procedure.md`, `compliance/evidence-pack-templates.md` §12 (disclosure wording incorporated by reference).

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Founder | Initial drafting notes and model clauses from engagement-framework and compliance-layer reports |
| v0.1.1 | 2026-10-25 | Product | Clause 3.6 "refund on fabrication" added (model wording, counsel review) per red-team review 2026-10-25, Major / §3.5; clause 1.3 dependencies split by Phase A / Phase B (Blocker 4); counsel item 8 added |

---

## 0. Why these clauses exist (drivers)

| Driver | What it requires or shows | Clauses affected | Source |
|---|---|---|---|
| Australian APS AI Plan | Suppliers on management-advisory panels must disclose planned AI use in RFQ responses; consultants remain fully responsible for output regardless of gen-AI use | 2, 3 | [Canberra Times](https://www.canberratimes.com.au/story/9110516/new-ai-plan-for-the-aps-sets-out-expectations-for-contractors/) |
| Canada PSPC | Advance AI-use disclosure now required | 2 | [BNN Bloomberg](https://www.bnnbloomberg.ca/business/company-news/2025/12/18/feds-defend-11-million-deloitte-contract-for-ai-advice-after-firm-admitted-mistakes/) |
| California GenAI procurement | Generative-AI disclosure language required in contracts | 2 | [GenAI.ca.gov](https://www.genai.ca.gov/choose-your-journey/procure-tool/follow-procurement-process/disclosure-contract-language/) |
| EU AI Act Art 50 | Exemption for AI-generated text depends on human editorial responsibility; live since 2 Aug 2026 | 2 | [Cookiebot](https://www.cookiebot.com/en/eu-ai-act-article-50-transparency-compliance/) |
| Deloitte Australia DEWR report | A$440K report with fabricated references and an invented court quote; toolchain disclosed only in the corrected version; partial refund | 2, 3, 4 | [Fortune](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund); [Accounting Times](https://www.accountingtimes.com.au/technology/deloitte-to-refund-government-after-using-ai-in-440k-report) |
| Deloitte Canada NL health plan | C$1.6M report with at least four citations to non-existent papers | 3, 4 | [HR Reporter](https://www.hrreporter.com/focus-areas/automation-ai/ai-errors-province-grapples-with-deloitte-report-marred-by-false-citations/393782) |
| Citation failure rates in deep-research agents | 3–13% of cited URLs hallucinated; only 24–77% of citations support the attributed fact | 3, 4 | [arXiv 2604.03173](https://arxiv.org/html/2604.03173v1); [arXiv 2605.06635](https://arxiv.org/html/2605.06635v1) |
| PDPA s.26 and LLM vendor retention terms | Transfer basis for any non-Singapore route; ZDR must be approved in writing and verified | 6 | [DeepInspect](https://www.deepinspect.ai/blog/singapore-pdpa-ai-controls-mapping); [The Register](https://www.theregister.com/ai-and-ml/2026/09/02/anthropic-promises-zero-data-retention-but-customers-must-check-it-worked/5293789) |
| TQA 9561 | LLM vendors are subservice organisations in the firm's SOC 2 system description | 6 | [Arthur AI](https://www.arthur.ai/column/soc-2-ai-agents-aicpa-tqa-9561) |
| Market shift to outcome pricing | McKinsey ~a third of revenue underwriting outcomes; BCG ~75% of largest AI cases on variable fees | 11 | [HBR IdeaCast](https://hbr.org/podcast/2026/01/where-mckinsey-and-consulting-go-from-here); [WebProNews](https://www.webpronews.com/consultants-put-skin-in-the-ai-game-as-clients-demand-proof-of-results/) |
| ICAEW commercial due diligence guideline | Gaps are disclosed, not silently estimated | 4 | [ICAEW CDD Guideline](https://assets.kpmg.com/content/dam/kpmgsites/ie/pdf/services/deal-advisory/ie-commercial-due-diligence-guideline.pdf.coredownload.inline.pdf) |

---

## 1. Scope and deliverables

| Drafting note | Position |
|---|---|
| Scope lives in the charter | The letter incorporates the engagement charter as Schedule 1; the charter's sections 1–2 define scope and outputs; the charter's decision log governs changes |
| Fixed fee tied to client dependencies | Phase A: timeline, not fee, moves when the client misses day 10 (interviews); there is no data dependency. Phase B: the day-5 data cut-off counts from onboarding clearance. Change order after 10 working days |
| Deliverables list | Must match the standard list in the framework report so that the client cannot later argue an output was implied |

> **1.1 Services.** PLUMB Advisory Pte. Ltd. **[VERIFY entity name on incorporation]** ("PLUMB") will perform the Verified Enterprise AI Journey Assessment described in the Engagement Charter at Schedule 1 (the "Services") and deliver the outputs listed in Schedule 1 section 2 (the "Deliverables").
>
> **1.2 Exclusions.** The Services do not include implementation of any use case, vendor selection, systems design, legal or regulatory advice, tax advice, audit or assurance opinions, or any work after the date of the final Deliverable, unless separately agreed in writing.
>
> **1.3 Client dependencies.** The Client will make the persons listed in Schedule 1 section 5 available and, for Phase B only, provide the data items listed in Schedule 1 section 4.2 by the dates stated, counted from the date the Client confirms its third-party onboarding of PLUMB has cleared. Phase A requires no confidential data from the Client. Where the Client does not meet a dependency, the affected phase's timeline extends day-for-day up to ten working days without change to the fee; thereafter PLUMB may issue a change order.
>
> **1.4 Changes.** Changes to scope are recorded in the Charter decision log and, where they affect fee or timeline, confirmed by written change order signed by both parties.

---

## 2. AI-assisted work and human accountability

| Drafting note | Position |
|---|---|
| Disclosure is affirmative and specific | Names the models, platforms, regions and retention settings; mirrors APS "fully responsible regardless of GenAI use" and preserves EU Art 50 editorial-responsibility exemption |
| No AI output without human review | Written as an obligation, not a description; this is the control whose absence produced the Deloitte refund |
| Agent action classes | Research agent operates under the same reversibility rules the firm recommends to clients: read autonomous, draft notify, write/send approve |
| Client consent to AI use | Some clients' procurement terms require buyer approval of AI use; the clause records the Client's consent and references any Client clause |

> **2.1 Use of AI tools.** PLUMB uses artificial-intelligence tools in delivering the Services, including for research and source retrieval, first-draft text, data analysis and summarisation. The models, tools, platforms, processing regions and data-retention settings in use for this engagement are listed in Schedule 1 section 9 and Schedule 2, and PLUMB will notify the Client in writing before adding or changing any of them.
>
> **2.2 Human responsibility.** All Deliverables are reviewed, edited and approved by named PLUMB professionals before issue. PLUMB takes full editorial and professional responsibility for the content of the Deliverables regardless of whether or to what extent artificial-intelligence tools were used in their preparation. No content generated by an AI tool is included in a Deliverable without human review.
>
> **2.3 Named accountability.** Each Deliverable identifies the engagement lead who prepared it, the independent reviewer who performed the quality-gate review, and the partner who approved it, and carries the AI-use and verification statement in the form at Schedule 3.
>
> **2.4 Limits on AI actions.** PLUMB's AI tools do not execute actions in Client systems. Any communication sent, document published or data written on behalf of the Client is approved by a named PLUMB professional before it occurs.
>
> **2.5 Client AI-use terms.** The Client confirms that the use of AI tools described in this clause is approved for the purposes of [Client's procurement policy / clause reference] **[VERIFY]**, and will notify PLUMB of any further AI-use approval, disclosure or restriction requirement that applies to the Client.

---

## 3. Source verification standard and its limits

| Drafting note | Position |
|---|---|
| State the standard precisely | It is the product; it is also what the firm is liable for. The standard is written as testable criteria that match the Processing Integrity control in `pipeline/verification-pipeline-spec.md` |
| State what it does not cover | Verification confirms that a source exists, says what is attributed to it and has a second independent upstream; it does not warrant that a public source is itself accurate |
| Confidence labels | Every metric carries filed / vendor-estimate / model-inferred / interview-anecdote and correlational / causal; the client is told how to read them |
| [VERIFY] convention | Unconfirmed items are stated as unconfirmed; the client agrees not to rely on them |

> **3.1 Verification standard.** PLUMB will apply the following standard to each Deliverable: (a) every citation resolves to a source that PLUMB fetched and stored with a content hash during the engagement; (b) every direct quotation is string-matched against the stored source; (c) every number on which a finding or recommendation depends (a "load-bearing number") is supported by at least two independent upstream sources, or is expressly labelled single-sourced; (d) claims that cannot be verified to this standard are removed from the Deliverable rather than flagged; (e) aggregator and secondary sources are traced to the original where available; (f) web pages identified as AI-generated are not used as sources; (g) an independent reviewer who did not operate the research tools samples at least thirty claims per Deliverable before issue.
>
> **3.2 Data-confidence labels.** Each metric in a Deliverable carries a label indicating its evidentiary basis (filed; vendor estimate; model-inferred; interview anecdote) and, where a relationship is asserted, whether it is correlational or causal. Figures from vendor case studies are directional only. The Client agrees to read Deliverables with these labels.
>
> **3.3 Unconfirmed items.** Items marked "[VERIFY]" in a Deliverable are stated as unconfirmed. The Client agrees not to rely on such items without further confirmation and acknowledges that PLUMB discloses gaps rather than estimating them.
>
> **3.4 Limits.** The verification standard confirms the existence, content and independence of sources. It does not warrant the accuracy of information published by third parties, including regulators, exchanges, companies, data vendors and the press, nor the accuracy of information supplied by the Client or by interviewees. Benchmark percentiles depend on the composition and size of the peer set, which is disclosed on each exhibit. Regulatory positions change frequently; information is current as at the date stated on each Deliverable.
>
> **3.5 Correction.** If, within twelve months of issue, the Client identifies a citation in a Deliverable that does not resolve, a quotation that does not match its source, or a load-bearing number that does not meet clause 3.1(c), PLUMB will investigate, correct the Deliverable at no charge, record the matter in the engagement file and, where the error affects a finding, re-issue the affected finding.
>
> **3.6 Refund on fabrication.** *(Model wording for counsel review; the per-instance amount, the aggregate ceiling and the interaction with clause 4 and PI cover are to be set with counsel and the insurer **[VERIFY]**.)* If any citation in a delivered Deliverable does not resolve to the source PLUMB stored for it (matched by the content hash recorded in the evidence appendix), or any quotation in a delivered Deliverable does not match the stored source after whitespace normalisation, then for each such instance (a) PLUMB will refund [S$[ ] / [ ]% of the fee] to the Client, up to an aggregate of [100]% of the fee paid under this letter, and (b) PLUMB will re-issue the Deliverable with the instance corrected or removed, within [10] working days, at no charge. An instance is established by PLUMB's own re-check or by the Client's written notice identifying the citation or quotation, and is confirmed by the independent reviewer named in Schedule 1. The refund is payable within [30] days of confirmation and is in addition to the correction remedy in clause 3.5. This clause does not apply to a source that resolved and matched at delivery and was later altered or withdrawn by its publisher, provided the stored copy and hash still match the evidence appendix.

---

## 4. Limitation of liability and cap

| Drafting note | Position |
|---|---|
| Cap | Market practice for advisory is a multiple of fees; **[VERIFY]** against PI insurer's required wording and cap. Working position: 1× fees for ordinary claims; higher cap or carve-out for breach of confidentiality / data protection to be decided with insurer |
| Carve-outs that cannot be capped | Fraud, wilful misconduct; anything Singapore law does not permit to be excluded |
| Consequential loss | Excluded |
| Decisions remain the client's | Deliverables inform a decision; they are not the decision |
| Interaction with clauses 3.5 and 3.6 | Correction at no charge plus the stated per-instance refund on fabrication are the primary remedies for verification failures; damages beyond that are subject to the cap. Counsel to decide whether 3.6 refunds count toward the cap |

> **4.1 Nature of the Deliverables.** The Deliverables are advisory. Decisions on whether and how to act on them, including any investment, deployment, hiring, procurement or regulatory decision, are made by the Client alone.
>
> **4.2 Cap.** PLUMB's total aggregate liability to the Client arising out of or in connection with this engagement, whether in contract, tort (including negligence), breach of statutory duty or otherwise, is limited to [one times / [x] times] the fees paid under this letter **[VERIFY with insurer]**.
>
> **4.3 Excluded losses.** PLUMB is not liable for loss of profit, revenue, business, goodwill or anticipated savings, or for indirect or consequential loss, however arising.
>
> **4.4 Exceptions.** Nothing in this letter limits liability for fraud, fraudulent misrepresentation, wilful misconduct, or any liability that cannot lawfully be limited.
>
> **4.5 Time bar.** Claims must be notified in writing within [twelve] months of the date of the final Deliverable and brought within [two] years **[VERIFY]**.

---

## 5. No reliance by third parties

| Drafting note | Position |
|---|---|
| Board decks travel | Deliverables will be shown to boards, lenders, investors and regulators; the letter must say who may rely |
| Regulator submissions | Where the Client uses an evidence-pack artefact in a regulatory submission (MAS inventory, DTA register), the Client submits it in its own name |

> **5.1** The Deliverables are prepared solely for the Client for the purposes stated in the Charter. No other person may rely on them. The Client may share Deliverables with its directors, officers, employees and professional advisers on a need-to-know basis, and with regulators where required by law, in each case on the basis that PLUMB accepts no duty of care or liability to the recipient. Any other disclosure requires PLUMB's prior written consent, which may be conditioned on a reliance letter at a separate fee.
>
> **5.2** Where the Client submits any Deliverable or part of it to a regulator, certification body or counterparty, the Client does so in its own name and on its own responsibility.

---

## 6. Confidentiality and client data handling

| Drafting note | Position |
|---|---|
| Residency | Processing in Singapore-region endpoints; any non-Singapore route needs a PDPA s.26 basis documented before use |
| Subservice providers | LLM and data vendors listed by name in Schedule 2 with region, retention and ZDR status; change requires notice |
| Retention | Engagement file retained for the longer of the firm's quality-system period and the regulatory minimum; client raw data deleted on a shorter clock; hashes of fetched public sources retained as verification evidence |
| Personal data | Handled under the DPA (Schedule 2) |
| Public-source corpus | Public-source material is not client confidential information; the client's identity and the fact of the engagement are |

> **6.1 Confidential information.** Each party will keep the other's confidential information confidential and use it only for the engagement. The Client's identity and the existence of the engagement are PLUMB confidential obligations unless the Client agrees to act as a reference under clause 8.
>
> **6.2 Processing location.** PLUMB processes Client data, including through AI tools, using Singapore-region endpoints. PLUMB will not route Client data through an endpoint outside Singapore unless a transfer basis under section 26 of the Personal Data Protection Act 2012 (or the equivalent for non-personal confidential data) is documented and the Client is notified in advance.
>
> **6.3 Subservice providers.** The LLM and data providers PLUMB uses for this engagement, with their processing region, data-retention setting and zero-data-retention status, are listed in Schedule 2. PLUMB obtains written confirmation of each provider's retention terms before Client data is processed and will give the Client [ten] working days' notice before adding or replacing a provider.
>
> **6.4 No training.** PLUMB will not permit any provider to use Client data to train or improve models, and selects only providers whose terms exclude such use.
>
> **6.5 Retention and deletion.** Client-supplied raw data is deleted or returned within [90] days of the final Deliverable unless the Client instructs otherwise or law requires retention. PLUMB retains the engagement file (Deliverables, decision log, verification logs, hashes of fetched public sources, quality-gate records) for [10] years for professional-quality and attestation purposes **[VERIFY period with counsel and insurer]**, in a form that does not include Client raw data beyond what the Deliverables themselves contain.
>
> **6.6 Personal data.** Where Client data includes personal data, the Data Processing Addendum at Schedule 2 applies and prevails over this clause to the extent of any conflict.
>
> **6.7 Security.** PLUMB maintains the security measures described in Schedule 2 section 6 and will notify the Client of any security incident affecting Client data within the period stated there.

---

## 7. Intellectual property

| Drafting note | Position |
|---|---|
| Methodology stays with PLUMB | Instrument, scoring, tiers, control library, catalogue, pipeline, templates, benchmark DB |
| Deliverables licensed | Client gets a perpetual licence to use Deliverables internally; may not resell or publish the methodology |
| Client data stays with client | |
| Benchmark DB | Anonymised scores are PLUMB's (clause 8) |

> **7.1 PLUMB materials.** The PLUMB methodology, including the maturity instrument, scoring and banding rules, right-to-win test, value and use-case kits, risk tiers and gates, control library, use-case catalogue, verification pipeline, templates, benchmark database and all improvements to them, is and remains PLUMB's property, whether or not developed or refined during the engagement.
>
> **7.2 Deliverables.** On payment in full, PLUMB grants the Client a perpetual, non-exclusive, non-transferable licence to use, copy and adapt the Deliverables for its internal business purposes. The Client may not publish, sell or license the Deliverables or the PLUMB materials embedded in them to third parties, other than as permitted by clause 5.
>
> **7.3 Client materials.** Client data and Client confidential information remain the Client's property. PLUMB may use them only to perform the Services and as permitted by clause 8.

---

## 8. Benchmark-data anonymised reuse consent

| Drafting note | Position |
|---|---|
| What is reused | Scores, bands, peer percentiles, size band, sector, sub-region; never the client's name, raw data, quotes or interview content |
| Why | GA criterion n ≥ 30; the benchmark is the moat; disclosure of n and self-scored share on each scorecard |
| Reversibility | Client may withdraw future use; entries already aggregated into published percentiles are not unwound |

> **8.1** The Client consents to PLUMB including the Client's maturity, value-axis and compliance scores, risk-tier distribution and related non-identifying attributes (sector, sub-region, size band, listed status) in PLUMB's anonymised benchmark database and in aggregated benchmark outputs provided to other clients and the public, provided that no output identifies the Client or allows the Client to be identified, and no Client raw data, interview content or quotation is included.
>
> **8.2** The Client may withdraw this consent for future use by written notice; withdrawal does not require PLUMB to remove the Client's entry from aggregates already published.
>
> **8.3 Reference.** [Optional] The Client agrees to act as a reference for PLUMB [by name / by anonymised description] and to approve a short case description, subject to the Client's prior review of the wording. [Design-partner engagements: this clause is mandatory per `pricing-ladder.md` §7.]

---

## 9. Conflict and independence

| Drafting note | Position |
|---|---|
| Peer set | Research on named competitors is inherent to the Services; the client is told so and the conflict procedure governs |
| Founder's other roles | Disclosed where relevant; see `conflict-check-procedure.md` |
| Vendor independence | PLUMB takes no fees from AI vendors recommended in use cases |

> **9.1** PLUMB has completed its conflict-check procedure and confirms that, as at the date of this letter, it is not aware of any conflict of interest that would prevent it from performing the Services, other than as disclosed in Schedule 4.
>
> **9.2** The Services include research on, and benchmarking against, companies in the Client's peer set using publicly available information. PLUMB may perform services for companies in the Client's sector, including companies in the peer set, provided it does not use the Client's confidential information for them and maintains information barriers where it does so concurrently.
>
> **9.3** PLUMB does not receive referral fees, commissions or other consideration from technology vendors in connection with any recommendation in the Deliverables, and will disclose any commercial relationship with a vendor named in a Deliverable.
>
> **9.4** PLUMB will notify the Client promptly if a conflict arises during the engagement and the parties will agree in good faith how to proceed; if they cannot, either party may terminate under clause 12.

---

## 10. Fees, payment and fee credit

> **10.1** The fee for the Services is S$[ ] (plus GST where applicable), payable 50% on signature of the Charter and 50% on delivery of the final Deliverable, each within [14] days of invoice.
>
> **10.2** One hundred per cent of the fee paid under this letter will be credited against the fees of any implementation or retainer engagement contracted between the parties within ninety days of the date of the final Deliverable.
>
> **10.3** [Design partner] The fee reflects a design-partner discount of [40/50]% in consideration of the Client's undertakings in Schedule 5 (data access, participation, reference, measured follow-up). If the Client does not perform those undertakings, PLUMB may invoice the difference to the list fee.

---

## 11. Outcome-fee measurement and dispute mechanism (Tier 2 only)

| Drafting note | Position |
|---|---|
| Preconditions | The eight preconditions in `pricing-ladder.md` §4.2 are conditions precedent; without them the engagement defaults to fixed fee |
| Measurement is by the client's system records | Not by estimate; PLUMB has contractual read access |
| Three-step dispute ladder | Joint review → independent measurer → expert determination (not arbitration) for speed |
| Caps | Performance component capped (§4.3) |

> **11.1 Measurement design.** The parties will agree, before any performance-linked work starts, a written Measurement Design specifying: the metric(s); the baseline period and value from Client system records; the counterfactual method (holdout, adjusted pre/post or synthetic control); the measurement window; the Client metric owner; the data extracts, format and cadence; the realisation-adjusted target; stop and re-baseline triggers; and the calculation of the performance fee or savings share. The Measurement Design is a condition precedent to clauses 11.2–11.5.
>
> **11.2 Measurement.** The Client will provide the agreed extracts on the agreed cadence. PLUMB will calculate the metric and the resulting fee and deliver a measurement statement within [15] working days after each measurement period.
>
> **11.3 Joint review.** Either party may dispute a measurement statement within [15] working days by written notice stating the grounds. The parties' metric owners will meet within [10] working days to resolve it.
>
> **11.4 Independent measurer.** If unresolved after [20] working days, the dispute is referred to an independent measurer agreed by the parties (or, failing agreement, nominated by [the Singapore Institute of Arbitrators / the Singapore Mediation Centre] **[VERIFY nominating body]**), who determines the metric value on the agreed Measurement Design. Costs are shared equally unless the measurer determines otherwise.
>
> **11.5 Expert determination.** The independent measurer acts as an expert and not as an arbitrator; the determination is final and binding on the metric value, save for manifest error. Disputes about the Measurement Design itself, rather than the measured value, are resolved under clause 13.
>
> **11.6 Re-baseline and stop.** On a stop or re-baseline trigger, measurement is suspended and the parties agree a revised baseline within [20] working days; failing agreement, the performance component for the affected period is calculated on the last agreed baseline pro rata.

---

## 12. Termination

> **12.1** Either party may terminate on [10] working days' written notice. The Client will pay fees for Services performed and Deliverables issued to the date of termination, and PLUMB's reasonable committed third-party costs.
>
> **12.2** Either party may terminate immediately for the other's material breach not remedied within [10] working days of notice, or for insolvency.
>
> **12.3 Design partner.** If PLUMB misses the Phase A day-12 delivery by more than ten working days for reasons within its control, the Client may terminate and pay only for Phase 1 and Phase 2 outputs delivered.
>
> **12.4 Survival.** Clauses 3.5, 3.6, 4, 5, 6, 7, 8, 13 and the DPA survive termination.

---

## 13. Governing law and disputes

> **13.1** This letter is governed by the laws of Singapore.
>
> **13.2** The parties will attempt to resolve any dispute by negotiation between senior representatives within [20] working days, failing which by mediation at the Singapore Mediation Centre, and failing settlement within [30] days of commencement of mediation, by arbitration administered by the Singapore International Arbitration Centre under its rules, seat Singapore, one arbitrator, language English **[VERIFY: counsel to confirm SMC/SIAC model clause wording and whether court jurisdiction is preferable at this fee level]**.

---

## 14. Schedules

| Schedule | Content | Source file |
|---|---|---|
| 1 | Engagement Charter | `engagement-charter-template.md` |
| 2 | Data Processing Addendum, including subservice-provider table | `data-processing-addendum-outline.md` |
| 3 | AI-use disclosure and verification statement (full and short forms) | `compliance/evidence-pack-templates.md` §12.1–12.2 |
| 4 | Conflict disclosures | `conflict-check-procedure.md` record |
| 5 | Design-partner undertakings (where applicable) | `pricing-ladder.md` §7 |
| 6 | Measurement Design (Tier 2 only) | Phase 4 output |

---

## 15. Open items for counsel

| # | Item | Why |
|---|---|---|
| 1 | Entity name, UEN, GST status | Letter cannot issue without them |
| 2 | Liability cap level and carve-outs | Must align with PI/cyber policy wording |
| 3 | Engagement-file retention period (10 years working value) | Balance quality-system evidence against PDPA retention-limitation obligation |
| 4 | Client procurement AI-use clause text (APS / DTA ClauseBank / California special provisions) | **[VERIFY]**; notes found RFQ-stage disclosure but no clause requiring deliverable-level disclosure beyond it |
| 5 | Dispute clause: expert determination for Tier 2 measurement; SMC/SIAC model wording | Speed vs enforceability |
| 6 | Whether clause 3.5 correction remedy should be expressed as the sole remedy for verification failures | Insurer position |
| 7 | Reference and benchmark-consent interaction with client confidentiality for listed clients | Disclosure rules |
| 8 | Clause 3.6 refund on fabrication: per-instance amount, aggregate ceiling, whether it sits inside or outside the clause 4.2 cap, insurer consent | Must be louder than the Deloitte precedent and still insurable (red-team review §3.5) |
