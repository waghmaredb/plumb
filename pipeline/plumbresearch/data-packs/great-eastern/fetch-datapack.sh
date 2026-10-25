#!/usr/bin/env bash
# PLUMB alpha — Great Eastern data pack fetcher.
# Run on a laptop with normal egress (the research sandbox cannot reach greateasternlife.com, mas.gov.sg, ocbc.com).
#
#   bash fetch-datapack.sh                 # downloads into ../../data/great-eastern
#   DATA_DIR=/path/to/data/great-eastern bash fetch-datapack.sh
#   SKIP_MCF=1 bash fetch-datapack.sh      # skip the MyCareersFuture API snapshot
#
# What it does
#   1. curl every item in MANIFEST.yaml (table below mirrors it) with -L, retries and a browser UA
#   2. probes alternate MAS URL patterns for the returns whose index page could not be read
#   3. writes CHECKSUMS.txt (sha256) + FETCH-LOG.txt (url, http code, content-type, bytes)
#   4. snapshots the MyCareersFuture search API (JSON pages) for later conversion to postings.csv
#   5. writes financials.csv (skeleton with the peer rows pre-filled from the scout) — never overwrites an existing one
#   6. writes transcripts/index.yaml for the OCBC proxy-by-parent material — never overwrites
#   7. prints what still needs a human (LinkedIn count, IPOS screenshot, MAS XLSX total-assets read-off, PDF page checks)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${DATA_DIR:-$HERE/../../data/great-eastern}"
mkdir -p "$DATA_DIR/transcripts" "$DATA_DIR/postings" "$DATA_DIR/patents"
DATA_DIR="$(cd "$DATA_DIR" && pwd)"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 PLUMB-datapack/0.1 (+research; contact engagement lead)"
LOG="$DATA_DIR/FETCH-LOG.txt"
SUMS="$DATA_DIR/CHECKSUMS.txt"
: > "$LOG"
echo "# PLUMB great-eastern data pack — fetched $(date -u +%Y-%m-%dT%H:%M:%SZ) by $(whoami)@$(hostname)" > "$SUMS"
FAILED=()
MANUAL=()

sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

# fetch URL DEST EXPECTED_TYPE  -> 0 on success
fetch() {
  local url="$1" dest="$2" want="$3" tmp code ctype size
  tmp="$(mktemp)"
  code="$(curl -sSL --retry 4 --retry-delay 3 --retry-all-errors --connect-timeout 20 --max-time 600 \
          -A "$UA" -H 'Accept: */*' -o "$tmp" -w '%{http_code} %{content_type}' "$url" 2>>"$LOG" || true)"
  ctype="${code#* }"; code="${code%% *}"
  size="$(wc -c < "$tmp" | tr -d ' ')"
  printf '%s\t%s\t%s\t%s\t%s\n' "$code" "${ctype:-?}" "$size" "$dest" "$url" >> "$LOG"
  if [[ "$code" != "200" || "$size" -lt 1024 ]]; then rm -f "$tmp"; return 1; fi
  # sanity on type: PDFs start with %PDF, XLSX are zip (PK)
  local magic; magic="$(head -c 4 "$tmp" | tr -d '\0')"
  case "$want" in
    pdf)  [[ "$magic" == "%PDF" ]] || { echo "   ! $dest: expected PDF, got '$ctype' (magic '$magic') — kept, check manually" ; MANUAL+=("$dest: not a PDF by magic bytes ($ctype)"); } ;;
    xlsx) [[ "${magic:0:2}" == "PK" ]] || { rm -f "$tmp"; return 1; } ;;
  esac
  mkdir -p "$(dirname "$DATA_DIR/$dest")"
  mv "$tmp" "$DATA_DIR/$dest"
  printf '%s  %s\n' "$(sha256 "$DATA_DIR/$dest")" "$dest" >> "$SUMS"
  echo "   ok  $dest  ($size bytes, $ctype)"
  return 0
}

# ------------------------------------------------------------------ 1. primary documents (local_file|type|url)
ITEMS=(
  "geh-annual-report-fy2025.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-website/annual-report/great-eastern-holdings-limited-ar-2025.pdf"
  "geh-annual-report-fy2024.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-website/annual-report/Great%20Eastern%20Holdings%20Limited%20AR%202024.pdf"
  "geh-fy2025-results-sgx-announcement.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/2025-fy25-sgx-announcement%20(SGX).pdf"
  "geh-fy2025-media-release.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/2025-fy25_media-release%20(SGX).pdf"
  "geh-fy2025-financial-summary.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/2025-fy25-financial-summary%20(SGX).pdf"
  "geh-20250819-form3-ocbc.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/20250819-form-3.pdf"
  "geh-20250819-completion-of-bonus-issue.pdf|pdf|https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/20250819-completion-of-bonus-issue-announcement.pdf"
  "ocbc-20250606-backs-geh-delisting-proposal.html|html|https://www.ocbc.com/group/media/release/2025/ocbc-backs-great-eastern-delisting-proposal"
  # peer corroboration
  "income-insurance-annual-report-2025.pdf|pdf|https://www.income.com.sg/getContentAsset/f39850fb-3691-42e4-b8b9-bfb476d651f8/05c6012c-3879-4f1c-b994-00e61e65c363/Income-Insurance-%E2%80%93-Annual-Report-2025.pdf?language=en"
  "singapore-life-holdings-financial-statements-fy2025.pdf|pdf|https://singlife.com/content/dam/public/sg/documents/merger/singapore-life-holdings-financial-statements-fy2025.pdf"
  "singapore-life-ltd-public-disclosure-fy2025.pdf|pdf|https://singlife.com/content/dam/public/sg/documents/merger/fy25-public-disclosure.pdf"
  "singlife-20260608-credit-ratings.html|html|https://singlife.com/en/about-us/newsroom/2026/singlifes-credit-ratings-maintained-with-stable-outlook"
  "prudential-singapore-factsheet-2025.pdf|pdf|https://www.prudential.com.sg/content/dam/prudential-aem-lbu/pacs/en/project/prudential/pdf/annual-reports/factsheet-2025.pdf"
  "prudential-singapore-annual-report-2024.pdf|pdf|https://www.prudential.com.sg/content/dam/prudential-aem-lbu/pacs/en/project/prudential/pdf/annual-reports/annual-report-2024.pdf"
  "aia-group-annual-report-2025.pdf|pdf|https://www.aia.com/content/dam/group-wise/en/docs/investor-relations/2025/AIA%202025%20annual%20report_EN.pdf"
  "aia-delivers-record-results-in-2025.html|html|https://www.aia.com.sg/en/about-aia/media-centre/press-releases/2026/aia-delivers-record-results-in-2025"
  "allianz-20260724-acquire-hsbc-life-singapore.html|html|https://www.allianz.com/en/mediacenter/news/media-releases/financials/260724-allianz-to-acquire-hsbc-life-singapore-and-enter-a-new-long-term-distribution-partnership-with-hsbc-singapore.html"
  "etiqa-singapore-supplementary-info-dec-2025.pdf|pdf|https://www.etiqa.com.sg/wp-content/uploads/2026/05/Etiqa-Insurance-Pte-Ltd-Dec-2025-Supplementary-Info.pdf"
  "china-taiping-singapore-public-disclosure-ye2025.pdf|pdf|https://www.sg.cntaiping.com/wp-content/uploads/2026/06/Public-Disclosure_YE-2025_clean_03.06.2026.pdf"
  "manulife-singapore-company-factsheet.pdf|pdf|https://www.manulife.com.sg/content/dam/insurance/sg/about-us/our-story/manulife_sg_company_brochure_en.pdf"
  "lia-4q2025-results-media-release.pdf|pdf|https://www.lia.org.sg/media/4789/20260211_lia-4q2025-results_media-release.pdf"
  # OCBC proxy-by-parent (transcripts/ so the earnings-calls module can index them with a label)
  "transcripts/ocbc-fy2025-results-presentation.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2025/ocbc%20fy25%20results%20presentation.pdf"
  "transcripts/ocbc-fy2025-ceo-presentation.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2025/OCBC%20FY25%20CEO%20Presentation.pdf"
  "transcripts/ocbc-fy2025-media-release.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2025/ocbc%20fy25%20media%20release%20financial%20highlights.pdf"
  "transcripts/ocbc-1h2026-results-presentation.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2026/ocbc%201h26%20results%20presentation.pdf"
  "transcripts/ocbc-1h2026-ceo-presentation.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2026/OCBC%201H26%20CEO%20Presentation.pdf"
  "transcripts/ocbc-1h2026-media-release.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2026/ocbc%201h26%20media%20release%20financial%20highlights.pdf"
  "ocbc-annual-report-2025.pdf|pdf|https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/annual-reports/2025/2025-annual-report-en.pdf"
  "ocbc-ar2025-group-ceo-perspectives.html|html|https://www.ocbc.com/group/investors/annual-reports/2025-annual-report/group-ceos-perspectives.page"
)

echo "== 1. primary documents → $DATA_DIR"
for row in "${ITEMS[@]}"; do
  IFS='|' read -r dest type url <<< "$row"
  if [[ -s "$DATA_DIR/$dest" ]]; then echo "   skip $dest (exists)"; printf '%s  %s\n' "$(sha256 "$DATA_DIR/$dest")" "$dest" >> "$SUMS"; continue; fi
  fetch "$url" "$dest" "$type" || { echo "   FAIL $dest"; FAILED+=("$dest <- $url"); }
done

# ------------------------------------------------------------------ 2. MAS insurance company returns (XLSX, 2025 and 2024)
# code|entity-slug|preferred pattern (A composite / B life / C general); the loop probes the others on failure
MAS=(
  "i516l|great-eastern-life|B"
  "i703c|great-eastern-general|C"
  "i566c|aia-singapore|A"
  "i527l|prudential-singapore|B"
  "i585c|income-insurance|A"
  "i518c|singapore-life|A"
  "i522l|manulife-singapore|B"
  "i544c|hsbc-life-singapore|B"
  "i517l|tokio-marine-life-singapore|B"
  "i570c|etiqa-singapore|A"
  "i579c|china-taiping-singapore|A"
)
mas_url() { # pattern code year
  case "$1" in
    A) echo "https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/$2/$3/$3.xlsx" ;;
    B) echo "https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/$2/$3/$3.xlsx" ;;
    C) echo "https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_g/$2/$3/$3.xlsx" ;;
  esac
}
echo "== 2. MAS insurance company returns (XLSX)"
for row in "${MAS[@]}"; do
  IFS='|' read -r code slug pref <<< "$row"
  for year in 2025 2024; do
    dest="mas-return-$code-$slug-$year.xlsx"
    if [[ -s "$DATA_DIR/$dest" ]]; then echo "   skip $dest"; printf '%s  %s\n' "$(sha256 "$DATA_DIR/$dest")" "$dest" >> "$SUMS"; continue; fi
    got=0
    for pat in "$pref" A B C; do
      url="$(mas_url "$pat" "$code" "$year")"
      if fetch "$url" "$dest" xlsx; then got=1; echo "      via pattern $pat: $url"; echo "$dest	$url" >> "$DATA_DIR/MAS-RESOLVED-URLS.txt"; break; fi
      sleep 2   # MAS rate-limits bursts
    done
    [[ $got == 1 ]] || { echo "   FAIL $dest — open https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/$code and copy the $year link"; FAILED+=("$dest (all MAS patterns failed; index page: .../insurance-company-returns/$code)"); }
  done
done

# ------------------------------------------------------------------ 3. MyCareersFuture API snapshot (current postings only)
if [[ -z "${SKIP_MCF:-}" ]]; then
  echo "== 3. MyCareersFuture API snapshot → postings/"
  snap="$(date -u +%Y%m%d)"
  for term in "great eastern" "great eastern life" "great eastern general insurance"; do
    tslug="$(echo "$term" | tr ' ' '-')"
    for page in 0 1 2 3 4; do
      out="$DATA_DIR/postings/mcf-$tslug-$snap-p$page.json"
      code="$(curl -sS --retry 3 --retry-delay 2 -A "$UA" -H 'Content-Type: application/json' -H 'Accept: application/json' \
              -X POST "https://api.mycareersfuture.gov.sg/v2/search?limit=50&page=$page" \
              --data "{\"search\":\"$term\",\"sessionId\":\"\"}" -o "$out" -w '%{http_code}' || true)"
      n="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d.get("results",[])), d.get("total"))' "$out" 2>/dev/null || echo "? ?")"
      echo "   [$code] $term p$page → $n (results total)"
      printf '%s\tapplication/json\t%s\tpostings/%s\t%s\n' "$code" "$(wc -c < "$out" | tr -d ' ')" "$(basename "$out")" "POST api.mycareersfuture.gov.sg/v2/search?limit=50&page=$page {\"search\":\"$term\"}" >> "$LOG"
      [[ "$code" == "200" ]] || { rm -f "$out"; break; }
      [[ "${n%% *}" == "50" ]] || break
    done
  done
  MANUAL+=("postings: convert postings/mcf-*.json → postings.csv (id, company, title, description, posted_at, url, location, source='mycareersfuture api snapshot $snap'); filter postedCompany.name to the GE entities; this is a point-in-time snapshot, not the 24-month series")
fi

# ------------------------------------------------------------------ 4. Google Patents JSON (expect zero)
echo "== 4. Google Patents XHR (expect 0 results)"
for a in "Great Eastern Life" "Great Eastern Holdings" "Great Eastern General Insurance"; do
  enc="$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$a")"
  out="$DATA_DIR/patents/google-patents-$(echo "$a" | tr 'A-Z ' 'a-z-').json"
  url="https://patents.google.com/xhr/query?url=assignee%3D%22$enc%22%26oq%3Dassignee%3A%22$enc%22&exp="
  code="$(curl -sS --retry 2 -A "$UA" -H 'Accept: application/json' -H 'Referer: https://patents.google.com/' -o "$out" -w '%{http_code}' "$url" || true)"
  tot="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["results"]["total_num_results"])' "$out" 2>/dev/null || echo "?")"
  echo "   [$code] assignee \"$a\" → total_num_results=$tot  ($url)"
  printf '%s\tapplication/json\t%s\tpatents/%s\t%s\n' "$code" "$(wc -c < "$out" 2>/dev/null | tr -d ' ')" "$(basename "$out")" "$url" >> "$LOG"
  [[ "$code" == "200" ]] || { rm -f "$out"; MANUAL+=("patents: Google Patents XHR blocked ($code) for \"$a\" — open https://patents.google.com/?assignee=%22$enc%22 in a browser and save the page"); }
done
MANUAL+=("patents: IPOS Digital Hub applicant search 'Great Eastern' (https://digitalhub.ipos.gov.sg) — screenshot the result page with date; write patents.csv with a header row only if zero")

# ------------------------------------------------------------------ 5. financials.csv skeleton
FIN="$DATA_DIR/financials.csv"
if [[ -s "$FIN" ]]; then
  echo "== 5. financials.csv exists — not overwritten"
else
  echo "== 5. writing financials.csv skeleton (money in S$ millions; peer total_assets blank until read from the MAS XLSX)"
  cat > "$FIN" <<'CSV'
entity,role,fy,currency,revenue,npat,total_assets,equity,cost_income,roe,source_urls,note,total_assets_as_reported,npat_as_reported,revenue_as_reported,equity_as_reported
Great Eastern Holdings Limited,subject,2025,SGD,7032.6,1207.1,122639.1,9710.1,,,https://www.greateasternlife.com/content/dam/corp-site/great-eastern/sg/gels-au-group-mgmt/investor-relations/2025-fy25-sgx-announcement%20(SGX).pdf;https://www.greateasternlife.com/content/dam/corp-site/group/gels-au-corpcomms/english-website/annual-report/great-eastern-holdings-limited-ar-2025.pdf,"[VERIFY] figures read from WebFetch summaries of the FY25 SGX announcement and AR2025; revenue = insurance revenue; equity = Group shareholders' equity. Re-read from the hashed PDFs before release.",S$122639.1 million,S$1207.1 million,S$7032.6 million (insurance revenue),S$9710.1 million
The Great Eastern Life Assurance Company Limited (I516L),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/i516l/2025/2025.xlsx,"regulated entity; fill total_assets from MAS return Form 1 (all funds); URL pattern inferred — see MAS-RESOLVED-URLS.txt",,,,
Great Eastern General Insurance Limited (I703C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i703c,"general arm; code I703C confirmed from MAS index; fill from MAS return",,,,
AIA Singapore Private Limited (I566C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i566c/2025/2025.xlsx;https://www.aia.com/content/dam/group-wise/en/docs/investor-relations/2025/AIA%202025%20annual%20report_EN.pdf,"fill total_assets from MAS return; AIA Group AR2025 segment note may give Singapore assets (group total US$345,423m)",,,,
Prudential Assurance Company Singapore (Pte) Limited (I527L),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/i527l/2025/2025.xlsx;https://www.prudential.com.sg/content/dam/prudential-aem-lbu/pacs/en/project/prudential/pdf/annual-reports/factsheet-2025.pdf,"fill total_assets from MAS return; factsheet gives AUM 'S$66.3 billion under management as at 31 December 2025' (AUM, not total assets)",,,,
Income Insurance Limited (I585C),core,2025,SGD,,118.9,44700,,,,https://www.income.com.sg/getContentAsset/f39850fb-3691-42e4-b8b9-bfb476d651f8/05c6012c-3879-4f1c-b994-00e61e65c363/Income-Insurance-%E2%80%93-Annual-Report-2025.pdf?language=en;https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i585c/2025/2025.xlsx,"[VERIFY] AR2025 'Total Assets' S$44.7 billion (PY24 S$43.4 billion), 'Profit After Tax' S$118.9 million (PY24 S$44.8m) per WebFetch summary; cross-check MAS return",S$44.7 billion,S$118.9 million,,
Singapore Life Ltd (I518C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i518c/2025/2025.xlsx;https://singlife.com/content/dam/public/sg/documents/merger/singapore-life-holdings-financial-statements-fy2025.pdf;https://singlife.com/en/about-us/newsroom/2026/singlifes-credit-ratings-maintained-with-stable-outlook,"fill total_assets from MAS return; newsroom (8 Jun 2026) says 'over S$16 billion' total assets (undated, not a balance-sheet figure); public disclosure FY25 net income $45,663k per MAS returns",over S$16 billion (newsroom; not entered as a value),,,
Manulife (Singapore) Pte. Ltd. (I522L),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/i522l/2025/2025.xlsx,"fill total_assets from MAS return; company factsheet gives no Singapore figures (Tier 1 insurer ⇒ ≥S$5bn total assets)",,,,
HSBC Life (Singapore) Pte. Ltd. (I544C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i544c;https://www.allianz.com/en/mediacenter/news/media-releases/financials/260724-allianz-to-acquire-hsbc-life-singapore-and-enter-a-new-long-term-distribution-partnership-with-hsbc-singapore.html,"fill total_assets from MAS return (URL pattern inferred); Allianz release: operating profit €80m (2025), comprehensive equity €1.2bn, price S$2.7bn",,,,
Tokio Marine Life Insurance Singapore Pte. Ltd. (I517L),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas-media-library/statistics/insurance-statistics/insurance-company-returns/annual_l/i517l/2025/2025.xlsx,"fill total_assets from MAS return",,,,
Etiqa Insurance Pte. Ltd. (I570C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/-/media/mas/statistics/insurance-returns/life-and-general-business/i570c/2025/2025.xlsx;https://www.etiqa.com.sg/wp-content/uploads/2026/05/Etiqa-Insurance-Pte-Ltd-Dec-2025-Supplementary-Info.pdf,"fill total_assets from MAS return; Notice 124 supplementary info has no total-assets line",,,,
China Taiping Insurance (Singapore) Pte. Ltd. (I579C),core,2025,SGD,,,,,,,https://www.mas.gov.sg/statistics/insurance-statistics/insurance-company-returns/i579c;https://www.sg.cntaiping.com/wp-content/uploads/2026/06/Public-Disclosure_YE-2025_clean_03.06.2026.pdf,"fill total_assets from MAS return (URL pattern inferred); public disclosure: capital available S$480m at 31 Dec 2025",,,,
CSV
  MANUAL+=("financials.csv: open each mas-return-*-2025.xlsx, read Form 1 total assets (sum over SIF par/non-par/ILP + OIF + shareholders' fund, as the sheet prints it), enter in S\$ millions with total_assets_as_reported; then set verify flags in the subject YAML")
fi

# ------------------------------------------------------------------ 6. transcripts/index.yaml (proxy-by-parent)
IDX="$DATA_DIR/transcripts/index.yaml"
if [[ -s "$IDX" ]]; then
  echo "== 6. transcripts/index.yaml exists — not overwritten"
else
  echo "== 6. writing transcripts/index.yaml (OCBC proxy-by-parent; text files need extraction, see README)"
  cat > "$IDX" <<'YAML'
# Great Eastern holds no results briefings or calls (financial calendar lists announcements, AGM/EGM, dividends only).
# Every row here is OCBC parent material and MUST carry the proxy label into every claim and exhibit.
# `file` must point at an extracted text file (pdftotext -layout <pdf> <txt>); the PDFs are alongside.
- url: https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2025/ocbc%20fy25%20results%20presentation.pdf
  date: 2026-02-25
  quarter: FY2025
  file: ocbc-fy2025-results-presentation.txt
  label: "proxy-by-parent: OCBC"
- url: https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2025/OCBC%20FY25%20CEO%20Presentation.pdf
  date: 2026-02-25
  quarter: FY2025
  file: ocbc-fy2025-ceo-presentation.txt
  label: "proxy-by-parent: OCBC"
- url: https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2026/ocbc%201h26%20results%20presentation.pdf
  date: 2026-08-07
  quarter: 1H2026
  file: ocbc-1h2026-results-presentation.txt
  label: "proxy-by-parent: OCBC"
- url: https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/pdf/investors/quarterly-results/2026/OCBC%201H26%20CEO%20Presentation.pdf
  date: 2026-08-07
  quarter: 1H2026
  file: ocbc-1h2026-ceo-presentation.txt
  label: "proxy-by-parent: OCBC"
# Briefing recordings (Q&A, where GE is usually discussed) — not downloaded, no official transcript exists:
#   FY2025: https://www.youtube.com/watch?v=ZGEw4bU-xgo     1H2026: https://www.youtube.com/watch?v=6rN0Tp2JxyU
YAML
  if command -v pdftotext >/dev/null; then
    for p in "$DATA_DIR"/transcripts/*.pdf; do [[ -s "$p" ]] && pdftotext -layout "$p" "${p%.pdf}.txt" && echo "   text  $(basename "${p%.pdf}.txt")"; done
  else
    MANUAL+=("transcripts: pdftotext not installed — run 'pdftotext -layout' on transcripts/*.pdf so index.yaml's file: entries exist")
  fi
fi

# ------------------------------------------------------------------ 7. report
echo
echo "== CHECKSUMS: $SUMS"
echo "== LOG:       $LOG"
if ((${#FAILED[@]})); then echo; echo "== FAILED downloads (${#FAILED[@]}):"; printf '   - %s\n' "${FAILED[@]}"; fi
echo
echo "== STILL MANUAL:"
printf '   - %s\n' "${MANUAL[@]}"
cat <<'TXT'
   - LinkedIn: open https://www.linkedin.com/company/great-eastern-group/jobs logged in; note the open-jobs count, the numeric company id (f_C=…) and the date
   - GEH careers: https://www.greateasternlife.com/sg/en/careers/employee.html — check for an embedded job board (Workday/SuccessFactors) with a JSON feed
   - Form 3 (geh-20250819-form3-ocbc.pdf): confirm the file is the Form 3 itself and read OCBC's %-after figure (expected 88.19% of 503,030,110 ordinary shares)
   - AR FY2025: confirm page count (~232) and extract the AI paragraph count locally (pdftotext | grep -ci 'artificial intelligence\|\bAI\b')
   - OCBC briefing Q&A: only if the engagement lead approves transcription of the YouTube recordings; label proxy-by-parent
   - Then: plumbresearch run plumbresearch/subjects/great-eastern.yaml --out out --data-dir data
TXT
