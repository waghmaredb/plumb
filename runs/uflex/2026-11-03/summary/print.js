const { chromium } = require('playwright');
(async () => {
  const [,, inp, out, png] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(inp)); await p.waitForTimeout(300);
  await p.pdf({ path: out, format: 'A4', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
