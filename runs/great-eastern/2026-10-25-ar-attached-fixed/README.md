# Great Eastern — run 3, FY2025 annual report attached, defects 1–3 fixed (2026-10-25)

Same input as run 2 (`../2026-10-25-ar-attached/`): `great-eastern-holdings-limited-ar-2025.pdf`, 244 pp, SHA-256 `ae320cb3…6488`, supplied by Deepak Waghmare, ingested under the publisher URL. Reconciliation is still **pending** (no egress), so every annual-report claim carries the label `attached; publisher hash unreconciled`.

Commands (from `pipeline/plumbresearch`):

```
rm -rf out/geh3
plumbresearch ingest plumbresearch/subjects/great-eastern.yaml --file ".../19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf" --doc annual_report-2025 --out out/geh3 --supplied-by "Deepak Waghmare"
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh3 --data-dir data --offline                      # client build (new default)
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh3 --data-dir data --offline --profile internal   # files in this folder
```

**Build profile note.** Between run 2 and run 3, plumbverify gained a `build_profile` (spec C2a, client | internal; another agent made this change in `policy.py` / `pipeline.py` / `cli.py`). The new default, `client`, withholds every claim whose only support is an unreconciled attachment. Under `client`, all 14 claims are BLOCKED (10 withheld until reconciliation, 4 peer sizes) and the quotation pass rate shows 0.0, because nothing is released. Run 2 behaved like today's `internal` profile, so the files here come from the **`--profile internal`** run, which keeps the before/after comparison like for like. The client-build output is kept at `pipeline/plumbresearch/out/geh3-client/`.

Code: plumbverify **0.3.1** (layout-aware PDF extraction) and the plumbresearch annual-report module (leadership and competitor extractors). Nothing was committed.

## Before / after

| Measure | Run 2 (before) | Run 3 (after, internal profile) |
|---|---|---|
| PDF extraction engine | pypdf (columns interleaved) | **pdftotext-layout** + column split (`Extraction.engine`) |
| Rubric level | L4 | **L4** (unchanged) |
| Components: specificity / production / pilot-only / quantified / governance / ownership / investment | 10 / 4 / 0 / 4 / 0 / 1 / no | 10 / 6 / 0 / 3 / 0 / 3 / no |
| AI mentions, words, density | 24 / 104,761 / 0.23 per 1,000 | 25 / 104,844 / 0.24 per 1,000 |
| D1.2 leadership proxy titles | **0** | **5** (1 CAIO-equivalent, 1 CDO-equivalent, 3 CDigO), plus 1 "other" not counted |
| — Managing Director, Group Data and AI | missed | **Zhao Jingyuan**, CAIO-equivalent, p. 31 (bio, name above title), p. 229 (listing, name before title), p. 67 ("Group Data and Artificial Intelligence" spelling, merged) |
| — Managing Director, Group Customer and Digital | missed | Ryan Cheong, CDigO, p. 67 (**left the Group in 2025**) |
| — Division Head, Group & Digital Affinity | missed | Wynn Chew Ai Ling, CDigO, p. 229 |
| — Division Head, Marketing and Digital Transformation | missed | Lucy Loo Liuxi, CDigO, p. 229 |
| — Head of the Group Data Office | missed | no name, CDO-equivalent, p. 67: **this is an OCBC role** (see issue 2) |
| — Group Chief Information Security Officer | missed | "other", not counted; OCBC history in a director bio, p. 18 |
| Named competitors | 1 (`NEA`: a false positive from a "compared with" context) | **0**. The report names no competitors; "compared with FY2025"-style and bare acronyms no longer match |
| Claims total / released / blocked | 9 / 5 / 4 | 14 / 10 / 4 |
| Blocked claims | 4 peer sizes (Prudential, Income, Singlife, AIA: sources DEAD offline) | the same 4, for the same reason |
| Quotation pass rate | 1.0 (5/5) | **1.0 (10/10)**. Every quote exact-matched, with page numbers p. 8, 14, 18, 31, 40, 67, 229 |
| Citation resolution | 0.2 | 0.2 (only the attachment resolves offline) |
| Build | FAIL (4 blocked) | FAIL (4 blocked); client profile: FAIL (14 blocked) |
| Log chain | ok | ok (`plumbverify verify-log`: 94 records) |

Why the components moved:
- **Quantified dropped from 4 to 3.** Before, the underwriting sentence was merged with the bonus-issue column ("$1.10 per share … 22%"), so it counted as quantified. That was defect 2. The underwriting sentence now stands alone and correctly counts only as specificity (it describes testing, with no outcome figure).
- **Ownership rose from 1 to 3.** The old single hit was a column-merged "Management Team … Great Eastern Life Assurance Company Limited …" fragment. The three new hits are the sentences carrying the Zhao Jingyuan title, because the rubric now counts a D1.2 proxy title as ownership evidence. L5 still fails on governance = 0.
- **Production rose from 4 to 6.** One of the new hits is spurious (issue 1). The level does not change.

## Material findings (for the scorecard)

- **D1.2.** A dedicated AI/data executive exists: Zhao Jingyuan, Managing Director, Group Data and AI, with GE since 2022. She sits at MD level, not C-suite, and the report does not say who she reports to. The report also says she **is expected to join OCBC as Head of the Group Data Office in March 2026, successor "to be named in due course"** (p. 67). On the as-of date, the CAIO-equivalent seat is therefore vacant or pending, and the role is moving to the parent. The digital MD (Ryan Cheong) also left in 2025.
- Governance is still 0. That finding from run 2 stands.

## New issues observed

1. **Pull-quote fragment counted as production evidence.** The layout dump splits a pull quote at "AI-" across a blank line, so `“We rolled out a proprietary AI-` became its own sentence (p. 14). It does not change the level, but it inflates production by 1. Fix: de-hyphenate across blank lines when the next block starts in lower case, or drop sentences under 40 characters from the rubric evidence (the claim builder already skips them).
2. **Wrong-entity title.** "Head of the Group Data Office" is OCBC's role, which Zhao Jingyuan is moving into. It is counted as a GEH CDO-equivalent. The leadership extractor needs an employer check: drop a title in the same clause as "join <Org>" or "of <Org>" when the Org is not the subject. With that fix, the GEH proxy count would be 4. "Group Chief Information Security Officer of OCBC" shows the same pattern but is already excluded as "other".
3. **Departed and leaving executives still count.** Titles in "left the Group" or "is expected to join … / will be leaving" sentences should carry a `status: departed | leaving` flag and not count as current D1.2 presence. Ryan Cheong and Zhao Jingyuan are both affected.
4. **The bio sentence "Responsible for … through Data, Analytics & AI" counts as production** because of the `operational` pattern. This was present in run 2 too. Consider removing `\boperational\b` from PRODUCTION, or requiring an AI-system subject.
5. **Column splitting is heuristic.** On this report, 15 of 15 reference sentences come out contiguous (pypdf: 14/15, missing the name-above-title bio). The share of sentences unique to one engine fell from 5.8% (pypdf) to 4.4%. The remaining disagreements are mostly tables, director-bio sidebars and proxy-form pages, where neither engine is clean. Quotations from table pages should still be treated with care.
6. **Client profile.** No annual-report signal can be *released* in a client build until `plumbverify reconcile` returns MATCH on a machine with egress. That is by design (C2a), but it means the leadership and rubric findings above are internal-draft only.

## Next

- Reconcile the attachment on a laptop (`data-packs/great-eastern/fetch-datapack.sh`, then `plumbverify reconcile --store out/geh3/great-eastern/evidence`). Then re-run under the default client profile.
- Fix issues 1–3 (small; the extractor already returns `context` and `page` for the employer and status checks).
