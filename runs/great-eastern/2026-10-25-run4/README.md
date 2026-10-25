# Great Eastern — run 4: run-3 issues 1–4 fixed (2026-10-25)

Same input as runs 2 and 3: `great-eastern-holdings-limited-ar-2025.pdf` (244 pp, SHA-256 `ae320cb3…6488`), supplied by Deepak Waghmare and ingested under the publisher URL. Reconciliation is still **pending** because the sandbox has no egress, so every annual-report claim carries the label `attached; publisher hash unreconciled`.

Commands (run from `pipeline/plumbresearch`):

```
rm -rf out/geh4
plumbresearch ingest plumbresearch/subjects/great-eastern.yaml --file ".../19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf" --doc annual_report-2025 --out out/geh4 --supplied-by "Deepak Waghmare"
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh4 --data-dir data --offline                      # client build -> copied to out/geh4-client
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh4 --data-dir data --offline --profile internal   # files in this folder
```

The files in this folder come from the **internal** profile, so the comparison with run 3 is like for like. The client-profile output is at `pipeline/plumbresearch/out/geh4-client/`. As expected, all 15 claims are blocked there: 11 are waiting for reconciliation and 4 are peer sizes. Nothing was committed.

What changed in the code:
- `plumbresearch/modules/annual_report.py`: org attribution, transition status, the separate parent-context signal, and biography-sentence handling.
- `plumbresearch/textutil.py`: fragment and duplicate filter (`rubric_sentences`, `drop_fragments`, `is_fragment`) and `is_bio_sentence`.
- `subjects/great-eastern.yaml`: new `org_aliases` block.
- Tests: `tests/test_ar_run3_issues.py` (19 tests built from the GEH text on p. 14, 18, 31, 67 and 229).

## Before / after

| Measure | Run 3 (before) | Run 4 (after, internal profile) |
|---|---|---|
| Rubric level | L4 | **L4** (unchanged) |
| Components: specificity / production / pilot-only / quantified / governance / ownership / investment | 10 / 6 / 0 / 3 / 0 / 3 / no | 10 / **3** / 0 / 3 / 0 / **2** / no |
| AI sentence candidates dropped as fragments or duplicates | n/a | 4: `“We rolled out a proprietary AI-` (p. 14), `testing an AI solution for` (p. 14), the heading `Leveraging Emerging Technologies and AI`, and the p. 229 listing line `Zhao Jingyuan Managing Director, Group Data and AI` (repeats the p. 31 line) |
| Biography sentences (ownership only) | counted as production | 2 (p. 31: "Over 20 years of experience in Data, Analytics & AI …", "Responsible for … through Data, Analytics & AI") |
| AI mentions, words, density | 25 / 104,844 / 0.24 | 25 / 104,844 / 0.24 |
| **D1.2 signal value** | **5** (every proxy title, any org, any status) | **3** subject seats: 2 present, 1 in transition |
| Departed / former (not counted) | counted | 1 (Ryan Cheong) |
| Parent-group context (separate signal `leadership_parent`, not counted) | counted as a GEH CDO-equivalent | 1 (Head of the Group Data Office, OCBC) |
| Claims: total / released / blocked | 14 / 10 / 4 | 15 / 11 / 4 |
| Blocked claims | 4 peer sizes (sources DEAD offline) | the same 4 |
| Quotation pass rate | 1.0 (10/10) | 1.0 (11/11) |
| Citation resolution | 0.2 | 0.2 |
| Build | FAIL (4 blocked); client FAIL (14 blocked) | FAIL (4 blocked); client FAIL (15 blocked) |
| Log chain | ok (94 records) | ok (`plumbverify verify-log`: 95 records) |

### Leadership titles

| Title | Holder | Class | Org (role, basis) | Status | Counts for D1.2 | Run 3 |
|---|---|---|---|---|---|---|
| Managing Director, Group Data and AI (p. 31, 67, 229) | Zhao Jingyuan | CAIO-equivalent | Great Eastern Holdings Limited (subject; section "GROUP AND SINGAPORE", p. 229) | **leaving, seat in transition**: expected to join Oversea-Chinese Banking Corporation Limited ("OCBC"); successor to be named in due course; March 2026 | yes, as in transition | counted, as present |
| Division Head, Group & Digital Affinity (p. 229) | Wynn Chew Ai Ling | CDigO | Great Eastern Life Assurance (Malaysia) Berhad (subject-subsidiary; section "MALAYSIA" plus entity header) | present | yes | counted |
| Division Head, Marketing and Digital Transformation (p. 229) | Lucy Loo Liuxi | CDigO | Great Eastern General Insurance (Malaysia) Berhad (subject-subsidiary; entity named earlier in the same listing line) | present | yes | counted (with no claim; the passage was over 600 characters) |
| Managing Director, Group Customer and Digital (p. 67) | Ryan Cheong | CDigO | Great Eastern Holdings Limited (subject; the sentence says "the Group") | **departed**: left the Group, 2025 | no | counted |
| Head of the Group Data Office (p. 67) | (Zhao Jingyuan, incoming) | CDO-equivalent | Oversea-Chinese Banking Corporation Limited (**parent**; clause "join … as the") | incoming, March 2026 | no: parent-group context | counted as a GEH CDO-equivalent |
| Group Chief Information Security Officer (p. 18) | (director biography, Mr Choo) | other | OCBC (parent; clause "of OCBC") | former (2021–2022) | no | "other", not counted |

Seat-level reading for D1.2: GEH has one CAIO-equivalent seat, and it is in transition (the holder is moving to the parent, with no successor named as of 1 March 2026). It also has two CDigO-class seats at Malaysian subsidiaries. The group-level digital MD seat was vacated in 2025.

### Why the components moved
- **Production 6 → 3.**
  - Issue 1: the pull-quote fragment `“We rolled out a proprietary AI-` is dropped.
  - Issue 4: the p. 31 bio sentence "Responsible for improving customer experience, operational efficiency …" now counts toward ownership only.
  - Also, `\boperational\b` no longer matches "operational efficiency / risk / resilience …" (issue 4 in the run-3 README). That removes "Elevating Advisory and Service Excellence Our in-house AI capabilities … drive operational efficiency …".
  - The three sentences left are real deployment statements: the advisory platform (two wordings, p. 14 and the business review) and the medical-claims platform rollout. L4 still holds: production ≥ 1, specificity ≥ 2, quantified ≥ 1.
- **Ownership 3 → 2.** The p. 229 listing line duplicates the p. 31 name-and-title line once case and quotes are normalised, so it now counts once. The two left are the p. 31 line and the p. 67 transition sentence. Ownership counts distinct statements, not pages.
- **Claims 14 → 15.** Lucy Loo Liuxi now has a leadership claim, because an overlong listing line is cut to its exact "<name> <title>" span. The p. 67 Zhao sentence is one claim that carries both titles (her MD seat and the OCBC role) instead of two.

## Material findings (for the scorecard)

- **D1.2.** A dedicated AI/data executive exists, but the seat is in transition. Zhao Jingyuan, MD Group Data and AI, is moving to OCBC (Head of the Group Data Office, March 2026), and her successor is "to be named in due course". On the report's as-of date (1 March 2026) the CAIO-equivalent seat exists, but its continuity is not established. The D1.2 signal now says so explicitly and no longer counts the OCBC role.
- **Governance is still 0.** The finding from runs 2 and 3 stands.

## New issues observed

1. **The digital remit moved under a title with no digital keyword.** On p. 67, "Group Customer and Digital" (Ryan Cheong, departed) was folded into the new "Group Integrated Propositions and Platforms Division" under Kwek-Perroy Li Choo (MD, appointed September 2025). The keyword lexicon cannot see that this seat carries the digital remit, so D1.2 under-reports it. Fix: scope inheritance from "unified the … Digital … functions under …" sentences, or a reviewer note.
2. **`Subject` drops `org_aliases`.** `plumbresearch/subject.py` (outside this boundary) has no `org_aliases` field, and pydantic ignores unknown keys. The module falls back to re-reading the built-in YAML for the slug (`builtin_subject_path`), so a subject YAML outside `plumbresearch/subjects/` gets only the default aliases (its name patterns become `subject` aliases, with no parent). Fix: add `org_aliases: dict[str, list[str]]` to `Subject`.
3. **New signal id.** `great-eastern.ar.annual_report.2025.leadership_parent` (instrument item `D1.2-context`) is emitted only when the report names parent-group titles. Downstream consumers, including the plumbdeck work, should treat it as context and not as D1.2 evidence.
4. **A run-in heading is still glued to a sentence.** "Elevating Advisory and Service Excellence Our in-house AI capabilities …" still counts toward specificity. This is cosmetic, because specificity stays at 10 either way.
5. **Departure status uses the whole sentence.** A sentence such as "X retired from DBS and is now our Head of Data" would mark the title departed. The common cases are handled: "appointed as <title>" means present, a title after "join <org> as" means incoming, and a former role in a dated biography ("from 2014 to 2022") means former. No such sentence occurs in GEH FY2025.
6. **Client profile (unchanged by design, C2a).** No annual-report signal is released until `plumbverify reconcile` returns MATCH on a machine with egress.
