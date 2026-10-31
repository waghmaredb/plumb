# Quality bar — executive deliverables

The Great Eastern pre-read (deck v4 + deep-dive report v1, 2026-10-26) is the benchmark. Every
client deliverable must clear the same bar. Most of it is enforced by the build; the rest is a
cold review that runs the same way every time.

## One command

```
cd pipeline/plumbdeck/exec
PPTX_SKILL_DIR=<pptx skill dir> python build_deck.py storylines/<client>.json \
  --run <run dir> --out <out dir> --pdf <attached source PDF> --name <file name> --previews
```

Gates, in order; any failure stops the build:

| Gate | What it refuses |
|---|---|
| resolve | Face text resting on a withheld or missing claim; a table figure not found on its row of the hashed source PDF; arithmetic that does not equal its figures at the precision shown; slides over the word budget |
| rubric (`deck_rubric.py`) | A finding with no page footnote; a value calculation without a "not a forecast" qualifier, or on a base AI cannot move (e.g. contractual policyholder benefits); a fee in the ask; credentials after slide 3; placeholder bars that pre-rank peers; fear or hype words |
| lint (`face_lint.py`) | Internal vocabulary on the face (claim ids, "withheld", tiers, gap ids, tool names) |
| render (layout audit) | Text that overflows its box, runs off the slide, collides with other text, wraps where it must stay on one line, or leaves one or two words alone on a title's last line |
| validate | A malformed .pptx package |

Soft rubric rules (reported, scored): varied headline syntax, no number repeated on more than
two slides, value anchored on the client's own reported figures, hypotheses phrased as
falsifiable statements, icons used with restraint, 8–12 slides.

A deck is final only when, in addition: every reviewer row in the QA sheet is ticked by an
independent reviewer, all source documents are attached and reconciled, there are no
`[[FOUNDER: …]]` inputs and no pending slides.

## Regression

`pipeline/plumbdeck/exec/tests/test_golden.py` freezes the benchmark: titles, sources, figures,
tiles, status; full rubric pass; clean layout audit. `plumbreport` tests check that every number
on the deck face appears in the report. To change the benchmark on purpose, re-run with
`PLUMB_UPDATE_GOLDEN=1` and review the diff of `tests/golden/geh-preread-v4.json`.

## Cold review (every new client deck, before it leaves)

Give an independent reviewer (agent or person) only the slide images and this brief — not the
storyline, not our reasoning:

> You are a sceptical Group CEO/COO of the client, who has seen hundreds of top-tier consulting
> decks. A small advisory firm sent this pre-read before a first meeting. Amber "to confirm"
> fields and "awaiting source documents" stamps will be filled before sending. Report: (1) would
> you take the meeting, in two sentences; (2) per slide keep / fix / cut with the single most
> important fix; (3) anything amateur, generic or machine-written; (4) anything factually risky
> or over-claimed about the client; (5) top five changes by impact.

Fix what it finds. When a finding is a pattern rather than a one-off, add it to `deck_rubric.py`
so the next deck cannot repeat it.

## Lessons already encoded

| Review finding (2026-10-26) | Now enforced by |
|---|---|
| "Every 1% of claims and benefits ≈ S$40m" priced contractual benefits as a cost | rubric H7 (addressable basis) |
| Credentials on the last slide | rubric H4 |
| Fee in the ask | rubric H3 |
| Placeholder bars ranked peers before data existed | rubric H5 |
| Same "X; Y" headline pattern on most slides | rubric S1 |
| Questions instead of hypotheses | rubric S4 |
| Orphaned title words, wrapped pills, colliding legend | layout audit |
| Page numbers from the PDF, not the printed folio | resolver (printed-page mapping) |
