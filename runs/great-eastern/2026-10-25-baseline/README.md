# Great Eastern — G1 baseline run, 2026-10-25

Command: `plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out/geh --data-dir data --offline`
Environment: sandbox with no egress to greateasternlife.com, sgx.com, aia.com.sg; no local documents in `data/great-eastern/`.

Result: 6 modules ran, 1 claim raised, 1 BLOCKED (AIA Group total assets — source unreachable → DEAD → not citable), build FAIL as required by block-not-flag. Peer-set exhibit, 10 signals, 19 module gaps and 23 [VERIFY] items produced.

What this run proves: the verifier refuses to release an uncited number; the gap register is complete and specific; the peer funnel runs on the real subject file. What it does not prove: any maturity signal for Great Eastern — every content module reported `not-available`.

To turn this into a real G1 result, place in `pipeline/plumbresearch/data/great-eastern/`:
- `geh-annual-report-fy2025.pdf`, `geh-annual-report-fy2024.pdf`
- `postings.csv` (24-month MyCareersFuture/LinkedIn export), `patents.csv`, `financials.csv` (GEH + 9 core peers from MAS returns)
and re-run from a machine with normal egress so peer-size sources resolve.
