# Great Eastern — run 5: outside-in pre-read draft for independent review (P5, 2026-10-25)

This folder holds the artefact the independent reviewer audits: the **outside-in pre-read** for a first management meeting (11 slide IDs), the full-assessment draft built from the same run, and the run outputs behind both. Nothing was committed.

**Status: internal draft, not for client or board use.** Every slide carries the banner `DRAFT — not for board use (internal profile; 1 attachment unreconciled; resolution 0.1429; no QA gate 3 sign-off)`. The interlock has no override. The deck cannot become final until three things happen: the annual-report attachment is reconciled MATCH on a machine with egress, the run is repeated under the `client` profile, and a named independent reviewer signs QA gate 3.

## How it was produced

Input: `great-eastern-holdings-limited-ar-2025.pdf` (244 pp, SHA-256 `ae320cb3…6488`), supplied by Deepak Waghmare. It was re-ingested into a fresh output folder under the publisher URL.

```
cd pipeline/plumbresearch
rm -rf out/geh5
plumbresearch ingest plumbresearch/subjects/great-eastern.yaml --file ".../19c5f9bb-great-eastern-holdings-limited-ar-2025.pdf" \
    --doc annual_report-2025 --out out/geh5 --supplied-by "Deepak Waghmare"
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh5 --data-dir data --offline --profile internal
cd ../plumbdeck
plumbdeck build --spec specs/plumb-prospect-preread-v0.1.yaml --run <this folder> --out <this folder>/deck/preread
plumbdeck build --spec specs/plumb-assessment-v0.1.yaml       --run <this folder> --out <this folder>/deck/assessment
soffice --headless --convert-to pdf deck-DRAFT.pptx; pdftoppm -r 80 -png deck-DRAFT.pdf preview/slide
```

- Run ID: `research-00b2c3ba8084`.
- Text extraction engine: `pdftotext-layout`.
- Log chain: ok.
- Lint: **0 errors** on both decks. Each deck has one warning, the placeholder count, which is allowed on a draft:
  - pre-read: S07, withheld;
  - full assessment: 36 engagement-data placeholders.

## Files

| Path | What it is |
|---|---|
| `claims.json`, `report.json`, `signals.md`, `gap-register.md`, `peer-set.md`, `inference.jsonl` | Run outputs. `report.json` has a new `findings` block holding the observations and the questions. `gap-register.md` §6 lists the observation, its full search record and its limitations, and which questions are shown or withheld. |
| `deck/preread/deck-DRAFT.{md,pptx,pdf}`, `titles.md`, `lint.json`, `build.json` | The pre-read. |
| `deck/preread/preview/slide-NN.png` | LibreOffice render, 14 pages. A1 continues across pages 11–14. |
| `deck/assessment/deck-DRAFT.{md,pptx}`, `titles.md`, `lint.json`, `build.json` | The full assessment, built from the same run. |

## Released vs withheld

**Released: 29 claims. Withheld: 7 claims (listed).**

All 29 released claims are exact quotations from the attached FY2025 annual report. Under the internal profile they carry the label `attached; publisher hash unreconciled`. A client build would withhold all of them until reconciliation returns MATCH (C2a).

| Module | Claims | Released | Withheld |
|---|---|---|---|
| annual-report (rubric, leadership; unchanged) | 11 | 11 | 0 |
| findings (new) | 21 | 18 | 3 |
| peer-set | 4 | 0 | 4 |

The 18 released findings claims, by category:

- Named AI applications: 7, plus 2 follow-on sentences.
  - Advisory platform, aiming at about 75% less preparation time (p. 14; the p. 40 wording is shown once).
  - Medical-claims platform rollout (p. 14).
  - Underwriting AI, **in testing** (p. 14).
  - Same-day turnaround for 75% of medical claims (p. 40).
  - Customer segmentation for Great CareShield (p. 40).
  - OCR to detect wastage and abuse (p. 43). Two follow-on quotes go with it: "strengthened our claims oversight", and the Best Claims Initiative award **in Malaysia**.
  - Misconduct-detection model (p. 43).
- Data & AI operating model:
  - the 2025 restructure (p. 41);
  - the new Integrated Propositions and Platforms division, which absorbed Group Customer and Digital (p. 67).
- Leadership:
  - the MD Group Data and AI is expected to join OCBC as Head of the Group Data Office in March 2026 (p. 67);
  - "The successors … will be named in due course" (p. 67);
  - the departure of the MD Group Customer and Digital in 2025 (p. 67).
- Governance-adjacent sentences, quoted beside the observation:
  - "with discipline and robust governance" (p. 14);
  - "risk management AI solutions strengthen governance" (p. 40);
  - artificial intelligence named among the Board's competencies (p. 73);
  - directors' fees for "data and artificial intelligence initiatives" (p. 80).

| Gap | Withheld claim | Reason | What would resolve it |
|---|---|---|---|
| G-1 to G-4 | Peer sizes: Prudential SG, Income, Singlife, AIA Group | Source unreachable offline | Re-run with egress |
| G-5 to G-7 | Regulatory clock, MAS AIRM: issued 7 Oct 2026; takes effect 7 Oct 2027; life-cycle controls by 7 Oct 2028 | The MAS primary URLs (PDF and landing page) cannot be fetched from the sandbox | Re-run with egress. This is **correct behaviour**: S07 renders as "Withheld — see gap register G-5, G-6, G-7", and no MAS date appears anywhere in the deck. |

The full search record and its limitations are in `gap-register.md` §6.

## Pre-read titles (horizontal flow)

| ID | Title |
|---|---|
| S01 | Great Eastern Holdings Limited: what public evidence says about AI, 2026-10-25 (cover) |
| S02 | DRAFT — not for board use: 29 claims released, 7 withheld and listed |
| S03 | Great Eastern's FY2025 report shows AI in use and its AI leadership seat in transition |
| S04 | Great Eastern's FY2025 report names AI in six use cases, one still in testing |
| S05 | Great Eastern's Group Data and AI seat is in transition, successor to be named |
| S06 | Great Eastern's FY2025 annual report reaches level 4 of 5 on the AI-disclosure rubric |
| S07 | [H] The MAS AI risk clock is withheld until its primary source is fetched (withheld placeholder) |
| S08 | Six questions for management that the public record raises but cannot answer |
| S09 | A Phase A assessment would test these questions against evidence in 12 working days (offer, labelled) |
| S10 | 29 claims were released and 7 withheld; every withheld claim is listed |
| A1 | Every released claim traces to a stored source passage, page and hash |

## Questions for management (S08)

1. **(Observation, not a finding.)** Where is the framework behind Great Eastern's AI governance statements documented, and who owns it?
   - Basis: the search below found 0 hits for 17 AI-specific governance terms.
   - The report does use the word: "governance" appears 106 times, twice in a sentence with an AI term (pp. 14, 40).
   - The Board is linked to AI on pp. 73 and 80.
2. Which AI risk policies does Great Eastern set itself, and which does it adopt from the OCBC group? (p. 67)
3. Has a successor for the Group Data and AI seat been named since the report, with the same scope? (p. 67)
4. What evidence would move the underwriting AI from testing to production, and who approves it? (p. 14)
5. How are the reported 75% figures measured (baseline, period and population), and which are outcomes and which are aims? (pp. 14, 40)
6. What changed in the 2025 Data & AI operating-model restructure, and where does AI risk ownership sit? (p. 41)
7. *Withheld — see gap register G-5, G-6*: the MAS inventory-readiness question. Its basis is the MAS clock, which is withheld offline.

### The governance observation: exact search and limitations

- **Document:** the attached FY2025 annual report, SHA-256 `ae320cb3…`, PDF pages 1–244. Pages are numbered by PDF page index, as in every citation; for example, PDF p. 14 is printed page 12.
- **Engine:** `pdftotext-layout`, whitespace-normalised.
- **Rule:** case-insensitive regular expressions; FEAT, Veritas, AIRM and GenAI are matched case-sensitively.
- **AI-specific terms, 0 hits each:**
  - responsible AI, AI governance, AI risk, artificial intelligence risk;
  - model risk, model validation;
  - AI policy / principles / framework, AI ethics;
  - FEAT, Veritas;
  - fairness, explainability, human oversight / human-in-the-loop, algorithm;
  - ISO/IEC 42001, NIST AI RMF, MAS AIRM.
- **Broader terms:**

  | Term | Hits | Hits in a sentence with an AI term |
  |---|---|---|
  | governance | 106 | 2 (pp. 14, 40) |
  | ethic* | 7 | 0 |
  | technology risk | 3 | 0 |
  | oversight | 19 | 0 |

- **Limitations:**
  1. Only one document was searched.
  2. The lexicon matches exact terms only. The same approach missed a leadership title in run 2.
  3. Frameworks at OCBC group level were not read.
  4. Nobody has checked by eye whether PDF extraction split terms across columns.
  5. No independent human has read the document, and the two-upstream rule is not met. **It is therefore a question, never a finding.**

Run 4's "governance is still 0" is superseded: the report does say AI was expanded "with discipline and robust governance" (p. 14). What it does not do is name an AI-specific framework.

## Reviewer instruction block (QA gate 3)

You must not have run the agents, authored the modules or be the engagement lead (ghost deck §3, pipeline §6.2 P1). Work from `deck/preread/deck-DRAFT.pdf`, `claims.json`, `report.json` and the attached PDF. Do not use this README's prose as evidence.

1. **30-claim sample.** Follow pipeline spec §6.2 P3 and the ghost deck §3.1 check 7:
   - (a) every quotation on S03;
   - (b) at least 2 claims per module (annual-report, findings);
   - (c) at least 5 qualitative claims;
   - (d) fill to 30 at random from A1.

   For each claim, open the PDF at the cited PDF page, confirm the exact string, and confirm the hash prefix `ae320cb3`. Record full / partial / none / broken. Pass condition: 0 quotation failures and 0 fabricated sources.

   Note: all 29 released claims rest on one unreconciled attachment. Record that the P4 publisher-hash check **cannot be completed** until `plumbverify reconcile` runs with egress. The sign-off decision must therefore be "returned", or approved for internal use only.
2. **Governance observation (S08 Q1, S06 governance row).**
   - Re-run at least 5 of the zero-hit terms yourself on the PDF.
   - Read pp. 14, 40, 64–84 (governance and risk sections) and p. 216 (technology risk) by eye. Then sign the human-read line, or log a counter-example.
   - Confirm the deck never states a governance conclusion. It may only ask the question, with the five limitations shown.
3. **Leadership transition quote (S05, S03).**
   - Verify the p. 67 sentence word for word: "Ms Zhao Jingyuan (Managing Director, Group Data and Artificial Intelligence) is expected to join Oversea-Chinese Banking Corporation Limited (“OCBC”) as the Head of the Group Data Office in March 2026."
   - Verify the successor sentence: "The successors to Ms Zhao Jingyuan and Mr Jimmy Tong will be named in due course."
   - Note the as-of date. The report predates today (2026-10-25), so a successor may since have been named. S08 Q3 asks this, and no slide may assert the seat is vacant today.
4. **Stage labels (S04).**
   - Check that each stage label follows from the verb in its quote.
   - Check that "six use cases" counts distinct use-case labels, not rows: the medical-claims platform and the same-day claims figure share one label.
   - Check that "one still in testing" refers to the underwriting quote.
5. **Withheld rendering.**
   - S07 and S08 Q7 must show only gap ids.
   - No MAS date may appear anywhere in the pre-read: `lint.json` runs a leak check, and you should search the PDF yourself.
6. **Offer separation.** S09, and S03's Answer box, are labelled "Offer — not a finding". Check that no figure on them is presented as a fact about Great Eastern.
7. **Horizontal flow (check 2).** Write the three-sentence story from `deck/preread/titles.md` alone.

## Known issues (for the next run)

- S07 stays a placeholder until the run has egress; it is withheld by design.
- Resolution is 0.1429: 1 of 7 sources is citable. The six that are not are the 4 peer sources and the 2 MAS URLs.
- PPTX row heights are estimated. LibreOffice renders all 14 pages without overlap, but S08 is dense (10 pt table, 10 pt notes). Check the render in PowerPoint before use.
- Two plumbresearch orchestrator fixture tests fail. The cause is outside this boundary: `plumbverify/semantic.py` is being changed concurrently, and its C4 `production_vs_pilot` rule now blocks two fixture postings claims ("LLMOps Engineer"). The failure reproduces with `--modules postings` alone, without the findings module.

## Corrections made in review (2026-10-25, before commit)

1. **S04 stage column overclaimed.** Row 7 ("We have also developed an AI-driven model … significantly reducing …") was labelled "in use"; the extractor had promoted "developed + outcome" to "in use". The column promises the company's own verb, so it now reads "developed; outcome stated". `findings.classify_stage` no longer infers stage beyond the verb.
2. **C4 rule misfire.** The offline matcher's production-vs-pilot rule fired on bare job-title claims ("LLMOps Engineer") whose posting mentions evaluation; the rule now requires the claim to assert an action or a number. Calibration on the 175 GEH pairs is unchanged (false-SUPPORT 2.6%).
3. **Governance was not "0" in run 4.** The report states AI was expanded "with discipline and robust governance" (p. 14) and records fees for "data and artificial intelligence initiatives" (p. 80). What is absent is any of 17 AI-specific governance terms. Run 4's "governance is still 0" is superseded by the S08 Q1 observation.

Outputs above were regenerated after these corrections.
