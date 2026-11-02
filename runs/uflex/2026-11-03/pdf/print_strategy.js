// Print the UFlex strategy page to an A4 evidence-pack PDF (light theme, print-friendly breaks).
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [,, inp, out] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 900, height: 1200 } });
  await p.emulateMedia({ colorScheme: 'light', media: 'print' });
  await p.goto('file://' + path.resolve(inp));
  await p.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
  await p.addStyleTag({ content: `
    @page { size: A4; margin: 14mm 14mm 16mm 14mm; }
    html, body { background: #fff !important; }
    body { font-size: 13.5px; line-height: 1.5; }
    .wrap { max-width: none !important; padding: 0 !important; }
    .col { max-width: none; }
    h1 { font-size: 34px; } h2 { font-size: 24px; margin-top: 1.6em; break-after: avoid; page-break-after: avoid; }
    h3, h4 { break-after: avoid; page-break-after: avoid; }
    .uc, .kpi, .gate, figure, svg, .tbl, table, tr, .facts, .flow, .lay, .lay2, .recs, .zone { break-inside: avoid; page-break-inside: avoid; }
    section#usecases .uc { break-before: auto; }
    .scroll { overflow: visible !important; }
    nav.toc a { color: #24313F; }
    a { text-decoration: none; }
  ` });
  await p.waitForTimeout(400);
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-family:Arial;font-size:7.5px;color:#5D6B78;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>PLUMB Advisory · UFlex AI strategy · For discussion · prepared from public information</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
  await b.close();
})();
