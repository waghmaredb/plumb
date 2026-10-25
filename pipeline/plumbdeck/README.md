# plumbdeck 0.1.0

Deck exporter for PLUMB (product item P4). Renders the ghost-deck storyline
(`../../methodology/ghost-deck-template.md` v0.1.1) from a `plumbresearch` run
folder (`report.json`, `claims.json`) and an optional `plumbscore` scorecard,
to Markdown and 16:9 PPTX, and enforces the **S02 interlock** (ghost deck
R8/R9, `../../compliance/evidence-pack-templates.md` §12.1, pipeline spec step S8).

```
pip install -e .            # python-pptx, pyyaml; pytest for the tests
plumbdeck build --spec specs/plumb-assessment-v0.1.yaml --run <run_dir> \
                [--scorecard <scorecard.json>] [--signoff <qa3-signoff.yaml>] --out <dir>
plumbdeck lint <out_dir>
pytest                      # 42 tests, offline
```

`build` writes `deck.md` + `deck.pptx` when the interlock passes, otherwise
`deck-DRAFT.md` + `deck-DRAFT.pptx` (a stale final-named deck in the same folder is
deleted), plus `titles.md` (horizontal-flow export, titles only), `build.json`
(manifest) and `lint.json`. It prints the run outcome in the house format,
"Released: N claims. Withheld: M claims (listed).", never "Build: PASS/FAIL".
Exit code: 0 lint ok, 1 lint errors, 2 bad input. `--run` accepts the folder that
holds `report.json` or a parent holding exactly one such folder.

## The interlock

S02's verification statement and the §12.2 short-form footer render **only if all**
of these hold; otherwise every slide (Markdown and PPTX) carries the top banner
`DRAFT — not for board use (<reasons>)`, S02 shows the draft disclosure (counts,
resolution, attachment status, reasons) and the files get `-DRAFT`.

| # | Condition | Read from | Reason text when it fails |
|---|---|---|---|
| a | citation resolution == 1.0 | `verification.metrics.citation_resolution_rate` | `resolution 0.2` / `resolution not recorded` |
| b | every ATTACHED source reconciled MATCH | `verification.sources[].reconciliation`, `attached_documents[]`, metrics `attached_unreconciled` / `attached_mismatch` (the larger count wins) | `1 attachment unreconciled` / `1 attachment mismatched` |
| c | build profile == `client` | `build_profile` | `internal profile` / `build profile not recorded` |
| d | QA gate 3 sign-off present and valid | `--signoff` YAML | `no QA gate 3 sign-off`; `QA gate 3 sign-off missing …`; `QA gate 3 sign-off file not found (…)` |
| d1 | decision == `approved` | sign-off `decision` | `QA gate 3 decision: returned` |
| d2 | independence attested | sign-off `independence_attestation: true` | `QA gate 3 reviewer independence not attested` |
| d3 | sign-off names this run | sign-off `run_id` | `QA gate 3 sign-off is for run X, not Y` |
| d4 | reviewer is not the run operator | operators = report `operator` / `run_operator` (if present) + every attachment's `supplied_by`; case- and space-insensitive | `QA gate 3 reviewer is the run operator (name)`; if no operator is recorded: `run operator not recorded; QA gate 3 reviewer independence cannot be checked` |

Truth table (tests/test_interlock.py): each failing condition alone gives DRAFT
with exactly its reason; all satisfied gives the final deck; several failures are
listed in the order a, b, c, d. There is **no override**: the CLI has no
`--force` (argparse rejects it and abbreviations), no environment variable is
read, and the spec schema is closed (an unknown key such as `force:` is an error).
`plumbdeck lint` recomputes the interlock from the build report rather than trusting
the manifest, so a deck whose report changed after the build fails with
`interlock_drift`.

Sign-off file (QA gate 3, ghost deck §3.2):

```yaml
qa_gate: 3
run_id: research-870b6a68ce63
reviewer: {name: "…", role: "Independent reviewer"}
independence_attestation: true      # did not run agents / did not author / not engagement lead
date: 2026-10-26
sample: {total: 30, exec_summary: 6, module_fill: 10, qualitative: 5, fabricated: 0, quotation_failures: 0}
decision: approved                  # approved | returned
approver: {name: "…", role: "Lead partner"}   # optional; S02 "Reviewed and approved by"
```

## Withheld claims

A claim not in `released_claim_ids` (BLOCKED, or withheld under C2a) never renders its
text or figures. Withheld claims are numbered `G-1…G-n` in the order of the run's gap
register; a bound cell or line reads `Withheld — see gap register G-n`. A title token
bound to withheld data switches the slide to its `title_withheld`. A slide whose bound
data is entirely withheld becomes a placeholder automatically. A6 lists withheld claims
by a descriptor (e.g. "Peer size: AIA Group (whole)"), never by their text.

## Lint (`plumbdeck lint`)

Errors: action title > 15 words (cover exempt); data slide without a source line, or
one not in the form `Source: <T-tier> <doc>, <date>; confidence: <label>` (build-report
slides S02/A6 use `Source: PLUMB build report <run>, <date>`); withheld-claim leakage
in deck Markdown, PPTX text (read back with python-pptx) or titles.md (8-word text
shingles; distinctive numbers: any decimal or 3+ digit figure, years excluded; 1–2
digit figures only with currency / % / scale context); banner missing on any slide
when the interlock fails (or present when it passes); verification statement on a
draft S02 or missing on a final one; S02 figures not equal to the build report;
missing `-DRAFT` suffix; Markdown / PPTX / titles.md out of step; not 16:9;
interlock drift. Warnings on a draft, errors on a final: placeholder slides and
`[H]` / `[bracket]` residue. Warning: evidence slide S05–S30 without a so-what.

## What is data-bound vs placeholder (spec `plumb-assessment-v0.1.yaml`)

| Slide | Exhibit | Bound to | Notes |
|---|---|---|---|
| S01 | cover | subject, run date, deliverable ID | strap reads "AI-assisted draft" until final |
| S02 | disclosure | build report + sign-off + inference log models | interlock-controlled |
| S06 | peer-set protocol | `<slug>.peerset.core_n` signal + peer-size claims + subject peer register | auto-placeholder when the signal and size claims are all withheld (GEH run 3) |
| S08 | two-axis scorecard | `--scorecard` JSON: self-view (uncapped) vs evidenced view, dimension table, V1–V4 | uses plumbscore's `self_view_score` when present, else recomputes from item raw means (only if the capped recomputation reproduces the scorecard); placeholder without a scorecard |
| S09 | outside-in signals | `report.signals` | signals without a tiered source show "not evidenced"; parent-group context signals (`…-context` items, run 4) are labelled "context only — not scored"; no peer percentile below n = 15 |
| A1 | evidence log | released claims (text, page, tier, label, hash prefix, slides using it) | |
| A6 | "Removed, not footnoted" | withheld claims G-n, reason class, resolver, holder; module-gap and [VERIFY] counts | |
| S03–S05, S07, S10–S34, A2–A5, A7 | placeholder | — | `[H]` title + "requires engagement data" list from the ghost deck |

Section dividers (ghost deck §2.3) are not rendered in v0.1. The PPTX template is
neutral (Arial, charcoal and slate, no logos, no client branding); oversize tables
continue on extra slides with the same ID (`A1 (2/2)`).

## Smoke outputs

`out/geh-run3/` (required smoke, run `runs/great-eastern/2026-10-25-ar-attached-fixed/`)
and `out/geh-run4/` (run 4). Both are DRAFT: `internal profile; 1 attachment
unreconciled; resolution 0.2; no QA gate 3 sign-off`. PNG previews of S02, S09 and A6
from LibreOffice are in `out/geh-run3/preview/`.
