# Verification Pipeline Specification (Processing Integrity control PI-CV)

**Status: v0.1 draft**
**Owner:** Pipeline lead (engineering); Quality lead (control operation and reviewer protocol); Compliance lead (vendor rules and attestation mapping)
**Applies to:** Every deliverable produced with the firm's research agent (Phase 1 outside-in sprint, Phase 3 synthesis) and the agent runtime itself. This spec is simultaneously (a) the firm's Processing Integrity control objective for SOC 2 and the AICM technical control set behind it, and (b) the engineering specification the pipeline is built and tested against.
**Control library rows:** CL-001 to CL-024 in `../compliance/control-library.csv`.
**Gate relevance:** G1 alpha exit and GA exit criteria (quality section) are defined here.

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Pipeline lead | Initial draft: control objective, components, thresholds, evidence base, vendor rules, test plan |
| | | | |

---

## 1. Control objective (SOC 2 Processing Integrity form)

**PI-CV. Citation and claim verification.** Deliverable content is complete, accurate and traceable to stored source material: every citation resolves to a fetched source held with a content hash; every quotation matches the stored source exactly; every load-bearing number has two independent upstreams traced to the original study; unverifiable claims are removed before release; AI-generated and content-farm pages are not cited; and every inference and agent action that contributed to the deliverable is logged in a tamper-evident store.

| Criterion | Testable statement | Maps to |
|---|---|---|
| PI-CV.1 Resolution | 100% of citations in a released deliverable resolve to a stored source record with hash, fetch time and final URL. | PI1.2, PI1.3; ISO A.6.2.4, A.7.5; CL-001, CL-002 |
| PI-CV.2 Support | Each claim is linked to a passage in its stored source at or above the match threshold; load-bearing claims achieve full support on reviewer sampling at or above the gate threshold. | PI1.3; ISO A.6.2.4; CL-003 |
| PI-CV.3 Quotation | 100% of quotations exact-match the stored source after whitespace normalisation. | PI1.3; CL-004 |
| PI-CV.4 Independence | 100% of load-bearing numbers have two upstreams with distinct original studies; aggregators are traced to the original. | PI1.2; ISO A.7.5; CL-005, CL-006 |
| PI-CV.5 Source quality | 0 citations in a released deliverable to pages classified AI-generated or content-farm; every source carries a tier T1–T5 and every metric a confidence label. | PI1.1, PI1.2; ISO A.7.3, A.8.2; CL-007, CL-008, CL-009 |
| PI-CV.6 Blocking | Deliverable build fails if any claim is in state BLOCKED; blocked claims appear in the gap register, never in the deck. | PI1.3, PI1.4; CL-011 |
| PI-CV.7 Traceability | Every output sentence is traceable to a retrieved chunk or tool call via per-inference logs retained tamper-evidently for at least 90 days. | PI1.4, PI1.5, CC7.2; ISO A.6.2.8; CL-012, CL-013 |
| PI-CV.8 Input integrity | Every input channel has a prompt-injection detection control with measured FP/FN; high-impact tools are unreachable from untrusted indirect input without a human gate. | CC6.6, CC7.1; OWASP LLM01; CL-014, CL-015 |
| PI-CV.9 Bounded autonomy | Agent actions are classed autonomous / notify / approve; the lethal-trifecta rule is enforced; tool-call depth is capped per module. | CC5.2, CC6.1; OWASP LLM03, ASI02; CL-010, CL-016 |
| PI-CV.10 Independent review | An independent reviewer samples at least 30 claims per deliverable and signs QA gate 3 before release. | CC4.1; ISO A.6.2.4, A.3.2; CL-022 |

Why this is written as a Processing Integrity control rather than left to SOC 2's defaults: SOC 2 does not natively test accuracy, provenance or bias, and auditors currently improvise AI evidence requests ([CSA SOC 2 AI gap note](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/)). TQA 9561 confirms agents fall inside the SOC 2 system description and LLM vendors are subservice organisations ([Arthur AI](https://www.arthur.ai/column/soc-2-ai-agents-aicpa-tqa-9561)). The firm's core risk is a fabricated citation reaching a client, which is the exact Deloitte Australia failure mode ([Fortune](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund)).

---

## 2. Evidence base: why each control exists

| Finding | Figure | Source | Control(s) it justifies |
|---|---|---|---|
| Deep-research agents hallucinate citation URLs | 3–13% of cited URLs hallucinated; 5–18% non-resolving; deep-research agents worse than plain search (10.7% vs 4.8% pooled); per system gemini-2.5-pro-deepresearch 13.3% / 18.5%, openai-deepresearch 3.5% / 10.1%, claude-3-7-sonnet-search 3.2% / 8.5% | [arXiv 2604.03173](https://arxiv.org/html/2604.03173v1) | Fetcher + hash store; URL health check (C1, C2) |
| URL-health self-correction loop works | Non-resolving rates fell below 1% in an agentic self-correction loop (GPT-5.1 16.0% to 0.6%; Gemini 2.5 Pro 6.1% to 0.1%; Claude Sonnet 4.5 4.9% to 0.8%); `urlhealth` tool classifies LIVE / DEAD / LIKELY_HALLUCINATED using HEAD/GET plus Wayback | [arXiv 2604.03173](https://arxiv.org/html/2604.03173v1) | Retry and archive policy; LIKELY_HALLUCINATED class (C2) |
| Valid links do not mean supported facts | Link validity above 94% and topical relevance above 80% for frontier models, but fact-check (source supports the attributed fact) ranges 24% to 77%; OpenAI models 39–59% fact-check accuracy; CiteAudit figures of 11–57% citation hallucination cited | [arXiv 2605.06635](https://arxiv.org/html/2605.06635v1) | Claim-to-passage match; quotation exact match; fact-support gate (C3, C4; section 4) |
| More retrieval produces less accurate citations | Fact-check accuracy fell about 42% on average from 2 to 150 tool calls (GPT-5.4 79% to 17%; Opus 4.6 80% to 58%) | [arXiv 2605.06635](https://arxiv.org/html/2605.06635v1) | Bounded tool-call depth; per-module chunking (C9) |
| Cited sources are themselves AI-generated | About 16% of sources cited by generative search engines (ChatGPT, Copilot, Gemini, Perplexity; 712 queries) were AI-generated | [infoDOCKET / AIES 2026](https://www.infodocket.com/2026/05/25/preprint-synthetic-sources-auditing-generative-search-engine-citations-for-evidence-of-ai-generated-sources/) | AI-generated / content-farm rejection (C7) |
| Unsupported claims are common in deep-research outputs | Roughly one-third of answers contain unsupported claims; citation accuracy 40–80% across systems | [arXiv 2509.04499 (DeepTRACE)](https://arxiv.org/abs/2509.04499) | Block-not-flag (C10) |
| Chatbots misattribute news sources and rarely decline | Over 60% of 1,600 news-sourcing queries answered incorrectly; over half of Gemini and Grok 3 responses cited fabricated or broken URLs; licensing deals did not guarantee accurate citations | [CJR Tow Center](https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php) | Source tiers; two-upstream rule (C5, C6, C8) |
| Agreement is not corroboration when upstreams are shared | Two series "may trace to the same study and agreement between them isn't independent corroboration" | [Koji](https://www.koji.so/blog/statista-vs-mintel-vs-euromonitor-2026); [Bell & Holmes](https://www.bellandholmes.com/blog/human-verified-primary-research-ai-control-group) | Two-independent-upstream check with aggregator tracing (C5, C6) |
| Consulting incident: Deloitte Australia | A$440,000 DEWR report (July 2025) with a dozen references to a non-existent professor's work, a wrong Robodebt citation and a fabricated judicial quote; GPT-4o on Azure OpenAI; partial refund; Finance supplier review; Senate questioning 3 Dec 2025; APS AI Plan RFQ-stage disclosure and full-responsibility clause | [Fortune](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund); [ACS](https://ia.acs.org.au/article/2025/deloitte-to-refund-government-over-ai-errors.html); [Accounting Times](https://www.accountingtimes.com.au/technology/deloitte-to-refund-government-after-using-ai-in-440k-report); [Canberra Times](https://www.canberratimes.com.au/story/9110516/new-ai-plan-for-the-aps-sets-out-expectations-for-contractors/) | Whole control; quotation exact match; AI-use disclosure (C4, C15) |
| Consulting incident: Deloitte Canada | C$1.6M Newfoundland health workforce plan with at least four citations to non-existent papers | [HR Reporter](https://www.hrreporter.com/focus-areas/automation-ai/ai-errors-province-grapples-with-deloitte-report-marred-by-false-citations/393782) | Citation resolution; independent review (C1, C16) |
| Incumbents publish input controls only | No incumbent describes a mandatory output-citation verification step; firm QC is "verify against underlying sources" | [ICAEW CDD Guideline](https://assets.kpmg.com/content/dam/kpmgsites/ie/pdf/services/deal-advisory/ie-commercial-due-diligence-guideline.pdf.coredownload.inline.pdf); [Future of Consulting](https://futureofconsulting.ai/ai-leadership/2026-consultings-ai-revolution-update/) | Positioning of PI-CV as the differentiating control |
| Prompt-injection controls need measured error rates | Threat-model every input channel with a documented detection control and measured FP/FN; high-impact tools unreachable from untrusted indirect input without a human gate; log per-input scores at least 90 days; outputs traceable to a chunk or tool call | [promptinjectionprevention.com](https://www.promptinjectionprevention.com/kb/owasp-llm-top-10-2025.php) | Input controls; 90-day logging; traceability (C12, C13, C14) |
| Auditors sample per-call logs and tamper-evident retention first | Nine artefacts: model registry, per-call logging (model version, prompt hash, tool calls, outcome), tamper-evident retention, vendor DPAs with ZDR, drift alerts, bias reports, tested rollback, secrets rotation, tool-level permissioning | [MLflow](https://mlflow.org/articles/soc-2-for-llm-apps/); [CSA PDF](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/08/CSA_research_note_soc2_ai_controls_gap_20260830-csa-styled.pdf) | Per-inference logging; retention (C12, C13) |
| Agent approval tiers and the trifecta rule | Autonomous / Notify / Approve with approval payload and fail-safe timeouts; human approval required for any session combining private data, untrusted content and external communication | [AWS Agentic Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02-bp05.html); [CSA OWASP maturity note](https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-agentic-ai-governance-maturity-v2-20/) | Action classes; lethal-trifecta rule (C14, C15) |
| Vendor-model fidelity differs | Anthropic models show highest fact-check fidelity in audits, OpenAI the most citations, Gemini the widest breadth but worst URL hygiene, Perplexity fastest but weakest support | [arXiv 2605.06635](https://arxiv.org/html/2605.06635v1); [NewsCatcher](https://www.newscatcherapi.com/blog-posts/best-deep-research-tools) | Breadth tools for discovery, verification loop for the final evidence set (section 3 architecture note) |

---

## 3. Components (engineering spec)

### 3.1 Claim and source state model

| Object | Key fields | States |
|---|---|---|
| `Source` | `source_id`, `url_requested`, `url_final`, `fetch_ts`, `http_status`, `content_sha256`, `content_type`, `text_extract`, `archive_url`, `tier` (T1–T5), `aigen_score`, `farm_score`, `health_class`, `upstream_of[]` | FETCHED, ARCHIVED, DEAD, LIKELY_HALLUCINATED, REJECTED_AIGEN, REJECTED_FARM |
| `Claim` | `claim_id`, `module`, `text`, `claim_type` (number / quotation / qualitative), `load_bearing` (bool), `confidence_label`, `causal_label`, `sources[]`, `match_scores[]`, `upstream_pairs[]` | EXTRACTED, MATCHED, SUPPORTED, PARTIAL, UNSUPPORTED, BLOCKED, RELEASED |
| `Inference` | `inference_id`, `run_id`, `model_id`, `model_version`, `ts`, `caller`, `prompt_sha256`, `tool_calls[]`, `output_ref`, `tokens_in/out`, `outcome`, `region_asserted` | logged only |
| `Action` | `action_id`, `run_id`, `tool`, `action_class` (autonomous / notify / approve), `params_ref`, `trifecta_flags`, `approver`, `approval_ts`, `rationale`, `result` | PROPOSED, EXECUTED, NOTIFIED, AWAITING_APPROVAL, APPROVED, DENIED, TIMED_OUT |

Architecture note: discovery may use breadth tools; the evidence set that reaches a deliverable is rebuilt by the verification loop below. Derived figures are computed in code, not by the model ([Marvin Labs](https://www.marvin-labs.com/blog/ai-tools-for-equity-research-complete-platform-comparison/)).

### 3.2 Component table

| # | Component | Function | Inputs | Outputs | Key parameters (v0.1 defaults) | Failure handling | Control row |
|---|---|---|---|---|---|---|---|
| C1 | Fetcher + content hash store | Fetch each candidate source once, store raw bytes and text extract, compute SHA-256, record final URL after redirects and fetch timestamp; immutable object store keyed by hash | Candidate URL from agent | `Source` record FETCHED | Timeout 20 s; max body 25 MB; user-agent declared; robots.txt honoured; per-domain rate limit | Non-2xx or timeout goes to C2; parse failure stores bytes and marks `text_extract=null` (claim cannot match, see C3) | CL-001 |
| C2 | URL health check with retry and archive policy | Classify URL health: HEAD then GET; retry 3x with exponential backoff (2 s, 8 s, 32 s) across two egress IPs; on persistent failure query Wayback for a snapshot within 24 months; classify LIVE / ARCHIVED / DEAD / LIKELY_HALLUCINATED (no DNS, no archive, pattern-plausible path) | URL, fetch result | `health_class`, `archive_url` | Re-check all LIVE URLs within 24 h of deck release; ARCHIVED citable only with archive URL and hash shown; DEAD and LIKELY_HALLUCINATED never citable | DEAD / LIKELY_HALLUCINATED sources force dependent claims to UNSUPPORTED (then C10) | CL-002 |
| C3 | Claim extraction | Split module drafts into atomic claims; tag type (number / quotation / qualitative), module, and load-bearing flag (any number or quotation in the executive summary, scorecards, value-pool sizing, or use-case business cases is load-bearing by default) | Module draft, citations | `Claim` records EXTRACTED | Load-bearing default rules are code, not model judgement; model may propose additional load-bearing flags, never remove them | Claims with no citation are UNSUPPORTED immediately | CL-003 |
| C4 | Claim-to-passage match | For each claim-source pair: exact or normalised string match on numbers and named entities, then semantic match of claim against candidate passages; record best passage and score | `Claim`, `Source.text_extract` | `match_scores[]`, state MATCHED / PARTIAL / UNSUPPORTED | Number claims: the number (with unit and period) must appear in the passage or be derivable by a logged arithmetic step; semantic threshold: SUPPORTED at or above 0.85, PARTIAL 0.70–0.85, UNSUPPORTED below 0.70 (cosine on the configured embedding model; thresholds calibrated against reviewer labels at G1 and re-tuned per release) | PARTIAL is treated as UNSUPPORTED for load-bearing claims; allowed for non-load-bearing qualitative claims only if a second source reaches SUPPORTED | CL-003 |
| C5 | Quotation exact match | Any span marked as quotation must exact-match the stored text after Unicode and whitespace normalisation; ellipses permitted only with logged omitted span | `Claim` (type quotation) | pass / fail | Zero tolerance; no fuzzy matching | Fail forces BLOCKED (not UNSUPPORTED); quotation cannot be downgraded to paraphrase automatically | CL-004 |
| C6 | Two-independent-upstream check with aggregator tracing | For every load-bearing number: build upstream graph; an upstream is the original study, filing or dataset; two sources count as independent only if their upstream terminus differs; aggregator sources (T5, and T3/T4 secondary summaries) must be traced to a terminus in T1–T3 before counting | `Claim` (load-bearing numbers), `Source.upstream_of[]` | `upstream_pairs[]`, pass / fail | Tracing depth cap 3 hops; terminus must itself be FETCHED and hashed; the terminus becomes the citation of record | Fail routes to C10; the gap register records "single-upstream" so the deck can state the number as directional only if the engagement lead re-labels it non-load-bearing with recorded rationale | CL-005, CL-006 |
| C7 | AI-generated / content-farm page rejection | Score each source on documented signals and reject above threshold | `Source` | `aigen_score`, `farm_score`, state REJECTED_* | Signals (each logged with weight): AI-text classifier score; template and boilerplate ratio; publication-velocity anomaly for the domain; absence of named author or organisation; absence of primary references; ad density and affiliate-link density; domain age under 12 months; duplicate-content ratio against already-fetched sources; self-declared AI generation; known content-farm list. Reject if combined score at or above 0.70 or any hard signal (self-declared AI generation, known-farm list) fires | Rejected pages usable for discovery only; any claim that relies solely on a rejected page becomes UNSUPPORTED | CL-007 |
| C8 | Source-tier assignment | Assign T1–T5 by rule table (domain class, document type, publisher class); display tier in evidence appendix | `Source` | `tier` | T1 regulator filings, primary documents, peer-reviewed or RCT; T2 investor materials, central-bank and official statistics; T3 named consulting-firm research, reputable trade press; T4 vendor and practitioner content (labelled); T5 aggregators and SEO content, discovery only | Unclassifiable domains default to T4 pending reviewer decision; T5 never a citation of record | CL-008 |
| C9 | Confidence labels | Attach `filed` / `vendor-estimate` / `model-inferred` / `interview-anecdote` to every metric, plus `correlational` / `causal` where a relationship is asserted; vendor case-study figures labelled directional | `Claim` (numbers), source tier, derivation log | `confidence_label`, `causal_label` | Label rules: T1/T2 primary = filed; T4 vendor = vendor-estimate; computed by pipeline from partial inputs = model-inferred; interview = interview-anecdote until repeated across 3 or more interviews | Missing label fails the deck export lint | CL-009 |
| C10 | Bounded tool-call depth and per-module chunking | Cap tool calls per module run; checkpoint module state; terminate and restart from checkpoint on cap; one module per run context | Agent run | Run logs, checkpoints | Default cap 40 tool calls per module run, 9 modules; hard ceiling 60 with recorded override; no cross-module context carry other than the structured claim store | Runs that hit the cap twice on one module are escalated to the research lead | CL-010 |
| C11 | Block-not-flag | Any claim in UNSUPPORTED or failing C5/C6 moves to BLOCKED; deck build asserts zero BLOCKED claims among released content; blocked claims and reasons are written to the gap register that ships in the evidence appendix | `Claim` states | Build pass / fail; gap register | No "unverified" footnotes or warning icons in client-facing material; gaps are disclosed as gaps | Build failure is a hard stop; override requires engagement lead and quality lead dual sign-off recorded in the engagement file and is reported at GA review | CL-011 |
| C12 | Per-inference logging | Log every model call and tool call with the `Inference` fields; link each output sentence to the inference and chunk or tool call that produced it | Runtime hooks | `Inference` records | Prompt stored as hash plus redacted copy; raw prompt retained only in the encrypted run store with the same retention | Logging failure fails the run (no silent operation) | CL-012 |
| C13 | Tamper-evident retention | Append-only, hash-chained log store; retention at least 90 days for input scores and inference logs; 6 months for decision-reconstruction material on engagements; quarterly integrity verification | `Inference`, `Action`, input-score records | Sealed segments, integrity reports | Daily segment seal with chained hash; separate write-only credentials; integrity check re-computes chain | Integrity failure is a security incident under EP-9 | CL-013 |
| C14 | Prompt-injection input controls (OWASP LLM01) | Per-channel detection: retrieved web pages, PDFs/OCR, tool outputs, interview transcripts; classifier plus rules plus LLM-judge ensemble; per-input score logged; content above threshold is quarantined and the agent is told the content is untrusted and stripped of instructions | All untrusted inputs | Per-input scores, quarantine decisions | FP and FN measured on a maintained test set (at least 500 benign and 500 injected samples, refreshed quarterly with ATLAS and OWASP updates); release threshold FN at or below 5% and FP at or below 10% at G1, FN at or below 2% and FP at or below 5% at GA | Channel without a measured control is disabled | CL-014 |
| C15 | Agent action classes and lethal-trifecta rule | Each tool registered with class: autonomous (search, fetch, read, compute), notify (write draft to engagement workspace), approve (send email, publish, write to any client system, delete, change configuration); gateway enforces class; any session with private-data access and untrusted content and an external-communication tool requires approval before the external action | Tool registry, session flags | `Action` records | Approval payload: raw action, agent reasoning, impact assessment, execution history; timeout 24 h fails safe (DENIED); approver identity, rationale and timestamp logged | A tool missing a class is unavailable; approve-class tools are never reachable from indirect input paths | CL-015, CL-016 |
| C16 | Independent reviewer protocol | Reviewer who did not run the agents samples claims per section 6, records support labels, signs QA gate 3 | Released candidate deck, claim store, source store | Signed sampling worksheet | At least 30 claims; thresholds per section 4 | Any fabricated or non-resolving source found fails the gate; deck returns to pipeline | CL-022 |

### 3.3 Processing sequence

| Step | Action | Gate |
|---|---|---|
| S1 | Agent discovery run per module (C10 bounds) with C14 screening on every ingested page | Depth cap |
| S2 | Fetch and hash every candidate source (C1); health check (C2); tier (C8); AI-gen and farm scoring (C7) | Sources in citable states only |
| S3 | Extract claims (C3); match to passages (C4); quotation check (C5) | Claim states assigned |
| S4 | Upstream graph and independence check for load-bearing numbers (C6); label confidence (C9) | Pairs recorded |
| S5 | Block (C11); write gap register | Zero BLOCKED in released set |
| S6 | 24-hour pre-release re-check of all LIVE URLs (C2) | Resolution 100% |
| S7 | Independent reviewer sampling and QA gate 3 signature (C16) | Thresholds in section 4 |
| S8 | Deck export lint: confidence labels, tier display, AI-use disclosure block (EP-10) present | Lint pass |

---

## 4. Metrics and acceptance thresholds

| Metric | Definition | G1 alpha exit | GA exit | Measured by |
|---|---|---|---|---|
| Citation resolution rate | Share of citations in released deliverable whose source is LIVE or ARCHIVED-with-hash at the 24 h pre-release re-check | 100% | 100% across the last 5 engagements | Automated (C2) plus reviewer re-fetch of sample |
| Fact-support rate (load-bearing) | Share of sampled load-bearing claims the reviewer labels full support | at or above 95% | at or above 95% | Reviewer sampling (section 6) |
| Fact-support rate (all sampled) | Share of all sampled claims labelled full or partial support, with partial allowed only for non-load-bearing qualitative claims | at or above 90% | at or above 95% | Reviewer sampling |
| Fabricated or non-resolving sources in sampling | Count found by reviewer in the 30-claim sample | 0 | 0 across the last 5 engagements | Reviewer sampling |
| Two-upstream coverage | Share of load-bearing numbers with two independent upstreams | at or above 90% (remainder re-labelled directional with rationale) | at or above 95% | Automated (C6) plus reviewer trace |
| Quotation exact-match | Share of quotations passing C5 | 100% | 100% | Automated plus 100% reviewer re-check in exec summary |
| AI-generated or farm pages cited | Count in released deliverable | 0 | 0 | Automated (C7) plus reviewer inspection of 10 accepted pages |
| Blocked-claim overrides | Number of C11 dual-sign-off overrides per deliverable | reported | 0 in the last 5 engagements | Engagement file |
| Injection control FN / FP | On maintained test set | FN at or below 5%, FP at or below 10% | FN at or below 2%, FP at or below 5% | Quarterly test run |
| Logging completeness | Share of released claims traceable to an inference and chunk or tool call | 100% | 100% | Automated reconciliation |
| Log integrity | Hash-chain verification pass | pass | pass each quarter | Integrity job |
| Tool-call depth compliance | Share of module runs within cap without override | at or above 95% | at or above 98% | Run logs |
| Action-class compliance | Approve-class actions executed without recorded approval | 0 | 0 | Action log reconciliation |
| Region assertion | Share of inferences with Singapore region asserted | 100% | 100% | Per-inference log |
| Cost and time per module | Logged per run | logged | logged, within engagement cost target | Run logs |

G1 (alpha) exit additionally requires: pipeline runs end to end on 2 public companies; zero unverified citations in both decks; defect list prioritised. GA exit additionally requires the independent reviewer signature on QA gate 3 for every delivered engagement and the subservice-organisation register complete for every vendor (see `../docs/Next steps and path to GA gate.md`).

---

## 5. LLM vendor configuration rules

| Rule | Requirement | Evidence held | Source |
|---|---|---|---|
| V1 Singapore endpoints | All production traffic pinned to Singapore-region endpoints (OpenAI Singapore API project; Claude via Google Cloud asia-southeast1 or an equivalent in-region route); global endpoints disabled at project level; `region_asserted` logged per inference | Endpoint configuration export; per-inference logs; blocked-call test record | OpenAI in-region handling since 25 Nov 2025 ([OpenAI](https://openai.com/index/expanding-data-residency-access-to-business-customers-worldwide/)); global endpoints carry no residency guarantee and are the default unless pinned ([IntuitionLabs](https://intuitionlabs.ai/insights/guides/zero-data-retention-gemini-vertex-ai-life-sciences)) |
| V2 ZDR in writing and tested | Zero-data-retention or equivalent approved in writing per vendor before production use; retention configuration recorded (Interactions API `store=false`; abuse-monitoring log tier; partner-model retention terms); retention behaviour tested at onboarding and after any vendor or model change | Approval letters; DPA clauses; retention test records | Anthropic ZDR requires application and approval, default API retention 30 days, customers must verify ZDR applied ([The Register](https://www.theregister.com/ai-and-ml/2026/09/02/anthropic-promises-zero-data-retention-but-customers-must-check-it-worked/5293789)); Google abuse-monitoring logs up to 90 days standard tier, partner Claude models retain up to 30 days ([IntuitionLabs](https://intuitionlabs.ai/insights/guides/zero-data-retention-gemini-vertex-ai-life-sciences)) |
| V3 Subservice-organisation register | Each LLM and data vendor recorded with SOC 2 / ISO status, retention configuration, region, inclusive or carve-out treatment, DPA reference, review date | Register (EP-7) | TQA 9561 treats external AI providers as subservice organisations ([Arthur AI](https://www.arthur.ai/column/soc-2-ai-agents-aicpa-tqa-9561)); CSA recommends documenting each LLM vendor's retention configuration ([CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/)) |
| V4 PDPA s.26 transfer basis | Any non-Singapore route has a documented transfer-limitation basis (comparable protection, PDP Regulations Part 3) approved before use; route inventory reconciled to endpoint configuration | Transfer-basis memo per route | [DeepInspect PDPA mapping](https://www.deepinspect.ai/blog/singapore-pdpa-ai-controls-mapping) |
| V5 Vendor certification record | Record each vendor's held certifications (e.g. Anthropic SOC 2 Type I and II, ISO 27001:2022, ISO/IEC 42001:2023; OpenAI SOC 2 Type 2, ISO 27001/27017/27018/27701, 42001 not listed) and credit SOC 2 only where the system description scopes model lineage, inference logging and AI subprocessors | Vendor trust-centre extracts in EP-7 | [Anthropic](https://support.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained); [OpenAI](https://openai.com/index/expanding-data-residency-access-to-business-customers-worldwide/); [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/) |
| V6 EU-exposed work | Prefer vendors that signed the EU GPAI Code of Practice (Meta and the Chinese labs have not); note vendor EU establishment | Vendor selection memo | [Wikipedia GPAI Code](https://en.wikipedia.org/wiki/General-Purpose_AI_Code_of_Practice); Garante annulment ([Gage Academy](https://www.gage.academy/tools/eu-ai-act-enforcement-tracker/actions/AIT-2024-0007-garante-openai-fine-annulled-court-of-rome)) |
| V7 Secrets | Provider keys in secrets manager, rotated on schedule and personnel change, never in agent configuration | Rotation log; secret-scan results | [MLflow](https://mlflow.org/articles/soc-2-for-llm-apps/) |
| V8 Model change control | Model, prompt-template and retrieval-corpus versions registered; changes deployed reversibly with regression on the verification test set before cut-over | Registry; regression records | [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-soc2-ai-controls-gap-20260830-csa-styled/) |

Open vendor items to close before G1: Bedrock Singapore availability for Claude not verified; Anthropic direct-API residency region list not retrieved (both flagged in the operationalising-compliance notes).

---

## 6. Test plan

### 6.1 Automated tests (run on every build; results stored as EP-5)

| Test ID | Component | Procedure | Pass criterion |
|---|---|---|---|
| T-01 | C1 | Fetch fixture set of 50 URLs; verify hash determinism on re-fetch of unchanged content; verify redirect final-URL capture | 50/50 hashed; redirects recorded |
| T-02 | C2 | Fixture set: 20 LIVE, 10 DEAD, 10 archived-only, 10 synthetic plausible-but-nonexistent URLs | Classification accuracy 100% on fixture; LIKELY_HALLUCINATED never citable |
| T-03 | C3/C4 | Labelled claim-passage set (at least 300 pairs with reviewer labels) | SUPPORTED/UNSUPPORTED agreement with reviewer labels at or above 90%; no load-bearing false SUPPORTED above 2% |
| T-04 | C5 | 50 quotations incl. altered single characters, moved punctuation, ellipses | Altered quotations fail 100% |
| T-05 | C6 | Fixture: 20 numbers with two independent upstreams, 20 with two aggregators of one study, 10 single-source | Shared-upstream pairs rejected 100%; independent pairs accepted 100% |
| T-06 | C7 | Labelled page set (at least 200 human-written, 200 AI-generated or farm) | Recall of AI/farm at or above 90% at G1, 95% at GA; false rejection of T1–T3 pages at or below 5% |
| T-07 | C8/C9 | 100 sources tiered by rule; 100 metrics labelled | Tier agreement with reviewer at or above 95%; 100% metrics labelled |
| T-08 | C10 | Synthetic module exceeding cap | Termination at cap; checkpoint restart; escalation on second hit |
| T-09 | C11 | Inject one BLOCKED claim into a release candidate | Build fails; gap register entry present |
| T-10 | C12 | Reconcile every sentence of a test deck to inference and chunk | 100% traceable |
| T-11 | C13 | Modify a sealed log record out of band | Integrity job detects; incident raised |
| T-12 | C14 | Run injection test set (500 benign / 500 injected across all channels) | FN and FP within gate thresholds (section 4) |
| T-13 | C15 | Attempt approve-class action from injected instruction in sandbox; attempt approve-class action with trifecta flags set | Gate fires both times; timeout yields DENIED |
| T-14 | V1 | Call global endpoint from production credentials | Blocked; alert logged |
| T-15 | V2 | Vendor retention probe per vendor (per vendor's documented verification method) | Configuration matches written approval |

### 6.2 Independent reviewer 30-claim sampling protocol (per deliverable)

| Step | Instruction |
|---|---|
| P1 | Reviewer eligibility: did not run the agents, did not author the module drafts, and is not the engagement lead. Identity recorded on the worksheet. |
| P2 | Sample frame: all claims in RELEASED state in the candidate deck and evidence appendix, drawn from the claim store, not from the slides. |
| P3 | Sample composition (minimum 30 claims): (a) every load-bearing number and every quotation in the executive summary (all of them, not sampled); (b) stratified random fill from the remaining load-bearing claims across the nine research modules so that each module with claims contributes at least 2; (c) at least 5 non-load-bearing qualitative claims chosen at random; (d) if (a)–(c) total fewer than 30, add random load-bearing claims until 30. If the deck has more than 30 qualifying claims under (a), sample all of (a) and the minimums under (b) and (c). |
| P4 | For each sampled claim, the reviewer independently: re-fetches the cited URL live (not from the store) and records resolution; opens the stored hashed copy and confirms the hash matches the store record; locates the passage and labels support as full / partial / none / broken; for quotations, performs a visual exact-match check; for load-bearing numbers, follows the upstream pair to the terminus and records whether the two termini are distinct original studies; records the source tier and confidence label as displayed and whether each is correct; inspects the page for AI-generated or content-farm indicators. |
| P5 | Additionally inspects 10 pages the pipeline rejected under C7 and 10 it accepted, and records agreement. |
| P6 | Records on the worksheet: counts per label; citation resolution rate; load-bearing full-support rate; count of fabricated or non-resolving sources; two-upstream pass rate; tier and label error counts; C7 agreement. |
| P7 | Decision: sign QA gate 3 only if resolution is 100%, load-bearing full support at or above 95%, fabricated or non-resolving count is 0, quotation failures are 0, and no AI-generated or farm page is cited. Any single failure returns the deck to the pipeline; after remediation the reviewer re-samples the failed claims plus 10 fresh random claims. |
| P8 | Worksheet, timings and signature are filed in the engagement file and summarised in EP-10 (verification statement) and the GA metric log. Reviewer time per deck is logged for the delivery-cost metric. |

### 6.3 Periodic tests

| Cadence | Test | Owner |
|---|---|---|
| Quarterly | Re-run T-12 with refreshed injection set (incorporating latest ATLAS and OWASP changes); re-run T-11 integrity check; re-tune C4 thresholds against accumulated reviewer labels | Security lead; Pipeline lead |
| Quarterly | Vendor retention probe (T-15) and subservice register review | Compliance lead |
| Per model, prompt or corpus change | Regression on T-03, T-06, T-12 before cut-over (V8) | Pipeline lead |
| Per engagement | Full automated suite plus section 6.2 protocol | Quality lead |
| Annually | Independent re-performance of the whole protocol on one delivered deck by an external reviewer (input to SOC 2 Type II and ISO 42001 A.6.2.4 evidence) | Compliance lead |

---

## 7. Open items for v0.2

| # | Item | Owner | Needed by |
|---|---|---|---|
| 1 | Calibrate C4 semantic thresholds and C7 rejection threshold against the first reviewer-labelled set | Pipeline lead | G1 |
| 2 | Decide embedding model and AI-text classifier for C4 and C7; record in model registry | Pipeline lead | G1 |
| 3 | Confirm Singapore routes for each vendor (Bedrock Singapore, Anthropic direct-API residency) and obtain ZDR approvals in writing | Compliance lead | G1 |
| 4 | Write the gap-register and verification-statement templates (EP-10 block wording per APS, California and EU Art 50 requirements) | Quality lead | G1 |
| 5 | Define the 6-month decision-reconstruction procedure that uses C12/C13 logs, for reuse in client EP-8 | Pipeline lead | G2 |
