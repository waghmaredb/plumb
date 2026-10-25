# Great Eastern data pack

The research sandbox cannot reach `greateasternlife.com`, `mas.gov.sg`, `ocbc.com` or `links.sgx.com`
(the proxy answers `CONNECT 403`), so the alpha run is a two-step: **fetch on a laptop, run anywhere**.

Everything in `MANIFEST.yaml` was located on 2026-10-25 with web search and probed with a page-summary
fetcher. Those summaries are scouting notes, not evidence: no file has been hashed and every figure quoted
in the manifest or pre-filled in `financials.csv` carries `[VERIFY]` until the pipeline reads it from the
downloaded file.

## Step 1 — laptop (normal egress)

```bash
cd pipeline/plumbresearch
bash data-packs/great-eastern/fetch-datapack.sh            # → data/great-eastern/
```

The script:

1. downloads every manifest item with `curl -L --retry 4` and a browser user-agent, checks PDF/XLSX magic
   bytes, and skips files that already exist;
2. fetches the 2025 and 2024 MAS insurance company returns (XLSX) for the eleven Singapore entities, probing the
   three MAS URL patterns for the four whose index page could not be read (I516L, I703C, I544C, I579C) and
   recording the pattern that worked in `MAS-RESOLVED-URLS.txt`;
3. writes `CHECKSUMS.txt` (SHA-256 per file) and `FETCH-LOG.txt` (HTTP code, content-type, bytes, URL);
4. snapshots the MyCareersFuture search API (`POST api.mycareersfuture.gov.sg/v2/search`) into
   `postings/*.json` — current postings only, dated by filename;
5. calls the Google Patents JSON endpoint for three assignee strings into `patents/*.json` (expect zero);
6. writes `financials.csv` (subject row from the FY25 SGX announcement; Income from its AR2025; all other peer
   `total_assets` blank with the MAS XLSX as `source_urls`) and `transcripts/index.yaml` (OCBC proxy-by-parent
   rows, each with `label: "proxy-by-parent: OCBC"`), neither overwritten if present;
7. prints what is still manual.

Still manual after the script: reading total assets off each MAS XLSX into `financials.csv`; the LinkedIn
open-jobs count (login wall); the IPOS Digital Hub applicant search screenshot; confirming the 19 Aug 2025
Form 3 PDF is the form itself and not the SGXNet wrapper; `pdftotext` on the OCBC decks if it is not installed.

Copy the resulting `data/great-eastern/` folder (with `CHECKSUMS.txt`) back to the run machine.

## Step 2 — run

```bash
plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out --data-dir data
plumbverify verify-log out/great-eastern/inference.jsonl
```

Local PDFs are served under the URL the subject YAML declares (`LocalDocTransport`), so the citation of record
stays the primary URL. Expect peer size claims to stay directional until each MAS figure has two upstreams.

## File map (local name → what it is)

| Local file | Source | Used by |
|---|---|---|
| `geh-annual-report-fy2025.pdf` | greateasternlife.com AR2025 (primary; replaces the SGX 403 link) | annual-report, size |
| `geh-annual-report-fy2024.pdf` | greateasternlife.com AR2024 | annual-report |
| `geh-fy2025-results-sgx-announcement.pdf` | FY25 condensed financial statements, 24 Feb 2026 | financials (subject row) |
| `geh-fy2025-media-release.pdf` | FY25 media release (AI platform claims) | annual-report / D2 |
| `geh-20250819-form3-ocbc.pdf`, `geh-20250819-completion-of-bonus-issue.pdf` | OCBC 88.19 % resolution | regulator_status, C6 |
| `mas-return-<code>-<entity>-<year>.xlsx` | MAS insurance company returns | peer-set sizes |
| `income-insurance-annual-report-2025.pdf`, `singapore-life-holdings-financial-statements-fy2025.pdf`, `prudential-singapore-*.pdf`, `aia-group-annual-report-2025.pdf`, … | second upstream per peer | peer-set |
| `transcripts/ocbc-*.pdf` + `.txt`, `transcripts/index.yaml` | OCBC results decks (proxy-by-parent) | earnings-calls |
| `postings/mcf-*.json` | MyCareersFuture API snapshot | postings (after conversion to `postings.csv`) |
| `patents/google-patents-*.json` | Google Patents JSON | patents (zero-finding evidence) |

## Resolutions recorded while scouting

- **OCBC % in GEH**: 88.44 % was the holding *before* the May 2024 voluntary offer; 93.72 % after it; the
  1-for-1 bonus issue completed 19 Aug 2025 left OCBC with 443,608,028 of 503,030,110 ordinary shares =
  **88.19 % of voting shares**, with 93.72 % economic interest kept through Class C non-voting shares.
  Public float ≈ 11.76 %; trading resumed 21 Aug 2025.
- **Great Eastern General MAS code**: I703C (from the MAS insurer list).
- **Singlife MAS code**: I518C (Singapore Life Ltd, the former Aviva Ltd licence).
- **GEH earnings calls**: none. The financial calendar lists results announcements, AGM/EGM and dividends
  only. OCBC publishes decks and a YouTube briefing recording; no transcript on ocbc.com.
- **Income total assets**: AR2025 prints S$44.7 bn (PY24 S$43.4 bn), not the S$47.2 bn carried from Wikipedia.
