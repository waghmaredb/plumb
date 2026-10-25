# Product next steps (Claude) — from 2026-10-25

Founder items are parked in `docs/founder-checklist.md`. This is the product queue Claude works without waiting on them, in order. Each item names what it lands before.

| # | Item | Why | Gate |
|---|---|---|---|
| P1 | **Run-3 issue fixes:** org attribution for titles (OCBC title counted as GEH), departed/leaving flag on executives, pull-quote fragment filter, bio-sentence false "production" hit | The four new extractor issues from run 3; each is a visible miss a reviewer would catch | G1 |
| P2 | **Instrument v0.2:** resolve the 12 logged ambiguities (band edges, cap scope, org-level aggregation, tie rule, V2 edges first); regenerate YAML; scorer + tests in step | Red team: "a 48-item instrument with 12 known ambiguities"; the scorer currently carries interim choices | G1 |
| P3 | **Semantic matcher (C4)** behind the existing protocol: embedding model with a calibrated threshold, plus a held-out set of supported/unsupported qualitative claims | Today only numbers and quotations are truly blocked; qualitative claims are not verified | G1 |
| P4 | **Deck exporter with the S02 interlock:** render the ghost deck from run outputs (Markdown → PPTX/PDF); refuses the verification statement unless resolution = 1.0 and attachments reconciled, otherwise stamps "DRAFT — not for board use" | The interlock is spec-only; the "one real deck" GA condition needs an exporter | G1 |
| P5 | **Great Eastern draft deck (internal profile)** from run 3: titles-only storyline, maturity pre-score, governance-as-question, leadership-seat finding, gap register — the artefact the reviewer will audit | Gives F4's reviewer something concrete; becomes client-grade after F26 | G1 |
| P6 | **Tier-0 self-scored benchmark** as a web form: cap rule on screen one, writes `population=self` rows, never pooled with evidenced scores | Lead magnet + benchmark seed; red team flagged it must not mis-promise | G2 |
| P7 | **MyCareersFuture postings collector** (snapshotting the documented API, 24-month accumulation) + IPOS/Google Patents collectors | Postings share and patents are `not-available` in every run | G1 |
| P8 | **Phase 2 kit:** instrument delivery (form + CSV), interview scheduling templates, transcript-quote verification against recordings | Phase A depends on it; red team flagged one person can't do 14–22 interviews unaided | G2 |
| P9 | **Tier 2 measurement-design-first** rewrite (no holdouts on T3+ customer-facing FI use cases) | Open item from the red team, logged in pricing-ladder §10 | G2 |
| P10 | **Maybank subject run** once F6b lands | Second alpha subject; tests the bank overlay | G1 |

Ordering logic: P1–P5 together produce the single artefact the red team said not to launch without — one real deck, reviewed by someone who did not run the pipeline. P6–P9 are the commercial machinery for G2.
