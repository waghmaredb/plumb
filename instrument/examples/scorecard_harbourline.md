# Harbourline Mutual Bank (fictional) — Enterprise AI Maturity Scorecard

Instrument v0.1 · respondents n=12 (ExCo 5, operating 7) · scores after cap rule (§5.4)

## S08 · Where you are: two-axis scorecard

**Harbourline Mutual Bank (fictional) scores 42.6 of 100, Emerging**, with value attribution still unmeasured.

```
0 █████████████████░░░┃░░░░░░░░░░░░░░░░░░░ 100   ┃ = production boundary (50)
  Stagnating ≤25 · Emerging ≤50 · Scaling ≤75 · Leading >75
```

| Capability axis | | Value axis (never merged) | |
|---|---|---|---|
| Capability score | **42.6** / 100 | Profile | **V1 A (not evidenced) · V2 12–39% · V3 3 · V4 2** |
| Band | Emerging | V1 EBIT share attributable to AI | A (reported B; recorded Band A (not evidenced: no S+D evidence)) |
| Production boundary (50) | at/below | V2 share of initiatives in production | 12–39% (reported 40–61%; self-report capped at 12–39% without S evidence) |
| Evidence coverage | 25% — **self-report-dominant** | V3 value-tracking rigour | 3 |
| Weights renormalised | no | V4 agent control maturity (OWASP GML) | 2 |

### Dimension scores

| Dim | Dimension | Weight | Items scored | Mean (1–5) | Score (0–100) | σ-flagged items | Alignment |
|---|---|---|---|---|---|---|---|
| D1 | Strategy & ambition | 10 | 6/6 | 3.01 | 50.3 | 0 | 0% flagged |
| D2 | Data foundations | 12 | 6/6 | 2.56 | 38.9 | 2 | 33% flagged |
| D3 | Technology & platform (incl. LLMOps/agent infra) | 12 | 6/6 | 2.88 | 46.9 | 0 | 0% flagged |
| D4 | Talent & skills | 10 | 6/6 | 2.43 | 35.8 | 1 | 17% flagged |
| D5 | Operating model & workflow redesign | 14 | 6/6 | 2.75 | 43.8 | 1 | 17% flagged |
| D6 | Governance, risk & compliance | 16 | 6/6 | 2.89 | 47.2 | 0 | 0% flagged |
| D7 | Culture & adoption | 10 | 6/6 | 2.94 | 48.6 | 0 | 0% flagged |
| D8 | Value management | 16 | 6/6 | 2.29 | 32.3 | 1 | 17% flagged |

## S09 · Peer percentile

**Harbourline Mutual Bank (fictional) sits at the 35th percentile overall** but 24th on Value management (D8) — peer set n=17; population: evidenced.

Peer set: sector=banking, size_band=large, region=SG · n=17 (peer; minimum n for a peer percentile is 15) · peer-set definition date: 2026-10-01 · population: evidenced · share of entries evidence-gated: 100%

| Dim | Score | Set median | Global median | Percentile |
|---|---|---|---|---|
| D1 | 50.3 | 52.5 | 46.1 | 47 |
| D2 | 38.9 | 54.3 | 49.5 | 41 |
| D3 | 46.9 | 48.1 | 46.2 | 41 |
| D4 | 35.8 | 53.1 | 49.5 | 35 |
| D5 | 43.8 | 43.6 | 43.2 | 59 |
| D6 | 47.2 | 52.9 | 49.9 | 47 |
| D7 | 48.6 | 55.1 | 50.6 | 41 |
| D8 | 32.3 | 52.6 | 52.5 | 24 |
| **Total** | **42.6** | 47.9 | 46.3 | **35** |

## S10 · Leadership-perception variance

**ExCo rate Data foundations 1.51 levels above operating managers** (ExCo-optimistic).

| Dim | ExCo mean | Operating mean | Gap (ExCo − operating) | Flag (>0.75) | Items σ>1.0 | Alignment |
|---|---|---|---|---|---|---|
| D1 | 3.60 | 3.10 | +0.50 | — | 0 | — |
| D2 | 3.80 | 2.29 | +1.51 | ExCo-optimistic | 2 | — |
| D3 | 3.03 | 3.10 | -0.06 | — | 0 | — |
| D4 | 3.10 | 2.14 | +0.96 | ExCo-optimistic | 1 | — |
| D5 | 3.70 | 2.62 | +1.08 | ExCo-optimistic | 1 | — |
| D6 | 3.13 | 3.10 | +0.04 | — | 0 | — |
| D7 | 3.30 | 3.19 | +0.11 | — | 0 | — |
| D8 | 2.33 | 2.31 | +0.02 | — | 1 | — |

Items flagged for perception divergence (σ > 1.0 on raw self-report, computed before the cap rule):

| Item | σ | Range | Roles at highest level | Roles at lowest level |
|---|---|---|---|---|
| D2.1 | 1.01 | 1–4 | CEO, CFO, CIO, CRO | Head of Operations |
| D2.3 | 1.36 | 1–5 | CEO, CFO, CIO, COO | Head of Data |
| D4.4 | 1.01 | 1–4 | CFO, CIO, COO, CRO | Head of Data |
| D5.1 | 1.04 | 1–4 | CEO, CFO, CIO, COO, CRO | Head of HR |
| D8.6 | 1.12 | 1–4 | Head of Analytics, Head of Digital Lending, Head of HR, Head of Model Risk | CEO, Head of Payments |

## S11 · Governance, risk & compliance (D6) by item

| Item | Question | Level (mean, capped) | Ev≥4 required | Evidence logged | Capped responses | OWASP GML (D6.6) |
|---|---|---|---|---|---|---|
| D6.1 | Do you run an AI management system? | 3.17 | D (policy, SoA, audit report) | D | 3/12 | — |
| D6.2 | Do you keep an AI inventory with risk tiering? | 3.08 | S (inventory extract) | S | 5/12 | — |
| D6.3 | Are impact and risk assessments performed before deployment? | 2.42 | D (assessments) | none | 1/12 | — |
| D6.4 | How are AI systems tested and validated? | 2.83 | D (test reports) + S | none | 0/12 | — |
| D6.5 | How are production AI systems monitored and incidents handled? | 2.92 | S (logs, incident register) | none | 4/12 | — |
| D6.6 | How mature is your governance of AI agents? | 2.92 | O (kill-switch test) + S | none | 3/12 | GML 1.9 |

S12 (regulatory exposure) is built from the regulatory-status map, not from instrument data.

## Appendix · Item detail (all 48 items)

| Item | n | Mean raw | Mean capped | σ raw | Capped | Evidence logged | Ev≥4 |
|---|---|---|---|---|---|---|---|
| D1.1 | 12 | 3.42 | 3.25 | 0.64 | 2 | D | D |
| D1.2 | 12 | 3.50 | 2.92 | 0.76 | 6 | — | D |
| D1.3 | 12 | 3.08 | 2.92 | 0.49 | 2 | — | D |
| D1.4 | 12 | 3.33 | 2.92 | 0.62 | 5 | D | D+S |
| D1.5 | 12 | 3.42 | 3.17 | 0.64 | 3 | D+O | O+D |
| D1.6 | 12 | 3.08 | 2.92 | 0.49 | 2 | — | D+S |
| D2.1 | 12 | 2.75 | 2.42 | 1.01 ⚑ | 4 | — | D |
| D2.2 | 12 | 2.58 | 2.42 | 0.95 | 1 | — | S |
| D2.3 | 12 | 3.25 | 2.58 | 1.36 ⚑ | 4 | — | S |
| D2.4 | 12 | 2.83 | 2.58 | 0.80 | 3 | — | S |
| D2.5 | 12 | 3.00 | 2.67 | 0.91 | 3 | — | S |
| D2.6 | 12 | 3.08 | 2.67 | 0.86 | 5 | D | D+S |
| D3.1 | 12 | 2.83 | 2.58 | 0.90 | 2 | — | O+S |
| D3.2 | 12 | 3.50 | 3.25 | 0.65 | 3 | S | S |
| D3.3 | 12 | 2.92 | 2.67 | 0.76 | 3 | — | S |
| D3.4 | 12 | 3.25 | 3.08 | 0.43 | 2 | S | S |
| D3.5 | 12 | 3.08 | 3.00 | 0.28 | 1 | — | O+S |
| D3.6 | 12 | 2.83 | 2.67 | 0.69 | 2 | — | D+S |
| D4.1 | 12 | 2.58 | 2.58 | 0.64 | 0 | — | D |
| D4.2 | 12 | 2.92 | 2.67 | 0.76 | 3 | — | S |
| D4.3 | 12 | 2.42 | 2.42 | 0.49 | 0 | — | S |
| D4.4 | 12 | 2.75 | 2.42 | 1.01 ⚑ | 4 | I | I+O |
| D4.5 | 12 | 2.25 | 2.17 | 0.92 | 1 | — | D |
| D4.6 | 12 | 2.33 | 2.33 | 0.75 | 0 | — | D |
| D5.1 | 12 | 2.92 | 2.50 | 1.04 ⚑ | 5 | — | D+O |
| D5.2 | 12 | 3.08 | 2.83 | 0.76 | 2 | — | D |
| D5.3 | 12 | 3.00 | 2.67 | 0.91 | 3 | — | S |
| D5.4 | 12 | 2.83 | 2.58 | 0.80 | 3 | — | S |
| D5.5 | 12 | 3.75 | 3.25 | 0.43 | 6 | D+S | D+S |
| D5.6 | 12 | 2.83 | 2.67 | 0.69 | 2 | — | D+S |
| D6.1 | 12 | 3.42 | 3.17 | 0.76 | 3 | D | D |
| D6.2 | 12 | 3.50 | 3.08 | 0.76 | 5 | S | S |
| D6.3 | 12 | 2.50 | 2.42 | 0.65 | 1 | — | D |
| D6.4 | 12 | 2.83 | 2.83 | 0.37 | 0 | — | D+S |
| D6.5 | 12 | 3.25 | 2.92 | 0.60 | 4 | — | S |
| D6.6 | 12 | 3.17 | 2.92 | 0.55 | 3 | — | O+S |
| D7.1 | 12 | 3.58 | 3.42 | 0.49 | 2 | S | S |
| D7.2 | 12 | 3.58 | 3.00 | 0.49 | 7 | — | I+D |
| D7.3 | 12 | 3.17 | 2.92 | 0.55 | 3 | — | D+I |
| D7.4 | 12 | 3.08 | 2.83 | 0.64 | 3 | — | S |
| D7.5 | 12 | 3.42 | 2.92 | 0.64 | 6 | — | S |
| D7.6 | 12 | 2.58 | 2.58 | 0.49 | 0 | — | S+D |
| D8.1 | 12 | 2.25 | 2.25 | 0.60 | 0 | — | S |
| D8.2 | 12 | 2.33 | 2.33 | 0.47 | 0 | — | D+S |
| D8.3 | 12 | 2.25 | 2.25 | 0.60 | 0 | — | S |
| D8.4 | 12 | 2.33 | 2.33 | 0.47 | 0 | — | D |
| D8.5 | 12 | 2.25 | 2.25 | 0.72 | 0 | — | D |
| D8.6 | 12 | 2.50 | 2.33 | 1.12 ⚑ | 2 | S | S |

## Flags

- D2 ExCo-vs-operating gap +1.51 (ExCo-optimistic) exceeds 0.75 (§5.3)
- D4 ExCo-vs-operating gap +0.96 (ExCo-optimistic) exceeds 0.75 (§5.3)
- D5 ExCo-vs-operating gap +1.08 (ExCo-optimistic) exceeds 0.75 (§5.3)
- Evidence coverage 25% < 60%: capability score is self-report-dominant (§5.4)
- Cap rule applied on 38 items (self-report >3 without required evidence class, §5.4)
