// PLUMB executive deck renderer.
// Input: resolved.json from resolve_storyline.py (every face sentence already checked
// against released evidence). Output: a 16:9 PowerPoint in the PLUMB executive style.
// Nothing internal (claim ids, tiers, gap ids, interlock reasons) is rendered here.
//
// Usage: node render_exec.js resolved.json out.pptx
"use strict";
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const SKILL = process.env.PPTX_SKILL_DIR || "";
let applyTheme = null;
try { if (SKILL) applyTheme = require(path.join(SKILL, "scripts/apply_theme.js")).applyTheme; } catch (e) { applyTheme = null; }

const [, , inFile, outFile] = process.argv;
const story = JSON.parse(fs.readFileSync(inFile, "utf8"));
const STATUS = story._status || { final: false, marker: "DRAFT FOR DISCUSSION" };

// ---------------------------------------------------------------- design system
const COL = {
  ink: "13233A",       // dominant: titles, dark slides
  text: "2B3645",      // body
  muted: "667085",     // captions, sources
  hair: "D7DCE3",      // hairlines, outlines
  panel: "F3F5F8",     // quiet panels
  teal: "0B6E6E",      // brand accent / "in use"
  slate: "4B6584",     // "developed"
  amber: "A86B12",     // "testing" / target
  white: "FFFFFF",
  onDark: "C9D1DC",
};
const F = { head: "Cambria", body: "Arial" };
const THEME = {
  name: "PLUMB Executive", headFontFace: F.head, bodyFontFace: F.body,
  colors: { dk1: COL.ink, lt1: COL.white, dk2: COL.text, lt2: COL.panel,
    accent1: COL.teal, accent2: COL.slate, accent3: COL.amber, accent4: COL.muted,
    accent5: COL.hair, accent6: COL.ink, hlink: COL.teal, folHlink: COL.slate },
};
const W = 13.333, H = 7.5, MX = 0.6, CW = W - 2 * MX;
const STATUS_COL = { "In use": COL.teal, "Developed": COL.slate, "Testing": COL.amber };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "PLUMB Advisory";
pres.company = "PLUMB Advisory";
pres.title = story.slides[0].title.text;
pres.theme = { headFontFace: F.head, bodyFontFace: F.body };

const footerLeft = `PLUMB Advisory   |   ${story.client}   |   ${STATUS.marker || "Confidential"}`;

pres.defineSlideMaster({
  title: "PLUMB_CONTENT",
  background: { color: COL.white },
  objects: [
    { text: { text: footerLeft, options: { x: MX, y: 7.0, w: 8, h: 0.25, fontFace: F.body, fontSize: 9, color: COL.muted, margin: 0 } } },
  ],
  slideNumber: { x: W - MX - 0.5, y: 7.0, w: 0.5, h: 0.25, fontFace: F.body, fontSize: 9, color: COL.muted, align: "right" },
});
pres.defineSlideMaster({ title: "PLUMB_DARK", background: { color: COL.ink }, objects: [] });

// ---------------------------------------------------------------- helpers
const t = (el) => (el == null ? "" : typeof el === "string" ? el : el.text);
// "[[FOUNDER: x]]" -> visible amber "to confirm" run; a deck containing one can never be final
function fmt(text, base) {
  const out = [];
  String(text).split(/(\[\[FOUNDER: [^\]]+\]\])/).forEach((part) => {
    if (!part) return;
    const m = part.match(/^\[\[FOUNDER: ([^\]]+)\]\]$/);
    out.push(m ? { text: `‹to confirm: ${m[1]}›`, options: Object.assign({}, base, { color: COL.amber, italic: true, bold: true }) }
               : { text: part, options: Object.assign({}, base) });
  });
  return out;
}

function plumbMark(s, x, y, len, color, bob) {
  // brand motif: a plumb line and bob
  s.addShape(pres.shapes.LINE, { x, y, w: 0, h: len, line: { color, width: 1.25 } });
  const r = bob || 0.11;
  s.addShape(pres.shapes.OVAL, { x: x - r / 2, y: y + len, w: r, h: r, fill: { color }, line: { color, width: 0 } });
}

function draftMarker(s, dark) {
  return; // status is carried by the footer mark only (CXO review 2026-10-26)
  // eslint-disable-next-line no-unreachable
  s.addText(STATUS.marker, {
    x: W - MX - 2.1, y: 0.32, w: 2.1, h: 0.28, isTextBox: true,
    fontFace: F.body, fontSize: 8, bold: true, charSpacing: 1.5, align: "center", valign: "middle",
    color: dark ? COL.onDark : COL.muted,
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06, line: { color: dark ? COL.onDark : COL.hair, width: 0.75 },
  });
}

// exact wrapping against Arial-metric fonts (Liberation Sans ships the same advance widths)
const opentype = require("opentype.js");
const FONT_DIR = process.env.PLUMB_FONT_DIR || "/usr/share/fonts/truetype/liberation";
const FONTS = {};
function font(bold) {
  const k = bold ? "b" : "r";
  if (!FONTS[k]) FONTS[k] = opentype.loadSync(path.join(FONT_DIR, bold ? "LiberationSans-Bold.ttf" : "LiberationSans-Regular.ttf"));
  return FONTS[k];
}
const SERIF_FILE = process.env.PLUMB_SERIF_FILE || "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"; // metric-compatible with Cambria
function serif() { if (!FONTS.s) FONTS.s = opentype.loadSync(SERIF_FILE); return FONTS.s; }
function lines(txt, wIn, pt, bold, useSerif) {
  const f = useSerif ? serif() : font(bold), limit = wIn * 72;
  let n = 1, cur = "";
  for (const word of String(txt).split(/\s+/)) {
    const trial = cur ? cur + " " + word : word;
    if (f.getAdvanceWidth(trial, pt) <= limit || !cur) { cur = trial; } else { n += 1; cur = word; }
  }
  return n;
}
function titleLines(txt) { return lines(txt, CW - 0.4, 25, false, true) > 1 ? 2 : 1; }
function contentTop(sl) { return titleLines(t(sl.title)) === 2 ? 2.05 : 1.6; }

// text over a shape: draw the shape, then a separate zero-margin text box inside it
function onShape(s, shape, box, text, txt) {
  s.addShape(shape, { x: box.x, y: box.y, w: box.w, h: box.h, fill: { color: box.fill }, line: { color: box.line || box.fill, width: box.lineW || 0 } });
  s.addText(txt, Object.assign({ x: box.x + (box.padL || 0.2), y: box.y, w: box.w - (box.padL || 0.2) - (box.padR || 0.2), h: box.h,
    isTextBox: true, margin: 0, fontFace: F.body, valign: "middle" }, text));
}

function frame(sl, slideIdx) {
  const s = pres.addSlide({ masterName: "PLUMB_CONTENT" });
  plumbMark(s, MX + 0.04, 0.36, 0.17, COL.teal, 0.08);
  s.addText((sl.section || "").toUpperCase(), {
    x: MX + 0.22, y: 0.33, w: 7, h: 0.3, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9.5, bold: true, color: COL.teal, charSpacing: 1.5, valign: "middle",
  });
  draftMarker(s, false);
  s.addText(t(sl.title), {
    x: MX, y: 0.78, w: CW - 0.4, h: 1.05, isTextBox: true, margin: 0,
    fontFace: F.head, fontSize: 25, color: COL.ink, valign: "top", paraSpaceAfter: 0,
  });
  if (sl._source) {
    s.addText(sl._source, { x: MX, y: 6.62, w: CW, h: 0.28, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 10, color: COL.muted, valign: "bottom" });
  }
  return s;
}

// ---------------------------------------------------------------- layouts
function cover(sl) {
  const s = pres.addSlide({ masterName: "PLUMB_DARK" });
  draftMarker(s, true);
  plumbMark(s, 10.6, 0.0, 4.55, COL.teal, 0.32);
  s.addText(t(sl.eyebrow).toUpperCase(), { x: MX + 0.2, y: 1.75, w: 8.8, h: 0.35, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 12, bold: true, color: "5FB3B0", charSpacing: 2 });
  s.addText(t(sl.title), { x: MX + 0.2, y: 2.2, w: 8.9, h: 2.2, isTextBox: true, margin: 0,
    fontFace: F.head, fontSize: 40, color: COL.white, valign: "top" });
  s.addText(`${t(sl.subtitle)}  ·  ${story.date_label}`, { x: MX + 0.2, y: 4.55, w: 8.9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 15, color: COL.onDark });
  if (sl.footnote) s.addText(t(sl.footnote), { x: MX + 0.2, y: 6.45, w: 8.9, h: 0.5, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 10, color: "8C99AA", valign: "bottom" });
  s.addText("PLUMB ADVISORY", { x: W - MX - 2.6, y: 6.6, w: 2.6, h: 0.35, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 10, bold: true, color: COL.onDark, charSpacing: 3, align: "right" });
}

function execSummary(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.05, rowH = 1.18;
  sl.points.forEach((p, k) => {
    const y = top + k * rowH;
    if (k > 0) s.addShape(pres.shapes.LINE, { x: MX, y: y - 0.12, w: CW, h: 0, line: { color: COL.hair, width: 0.75 } });
    s.addText(String(k + 1), { x: MX, y, w: 0.6, h: 0.75, isTextBox: true, margin: 0,
      fontFace: F.head, fontSize: 38, color: COL.teal, valign: "top" });
    s.addText(t(p.head), { x: MX + 0.85, y, w: CW - 0.85, h: 0.36, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 16, bold: true, color: COL.ink, valign: "top" });
    s.addText(t(p.body), { x: MX + 0.85, y: y + 0.4, w: CW - 1.6, h: 0.62, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 14, color: COL.text, valign: "top" });
  });
  const cy = top + 3 * rowH + 0.05;
  onShape(s, pres.shapes.RECTANGLE, { x: MX, y: cy, w: CW, h: 0.55, fill: COL.panel, padL: 0.25 },
    { fontSize: 13 }, [{ text: "Next   ", options: { bold: true, color: COL.teal } }, { text: t(sl.callout), options: { color: COL.ink } }]);
}

function chip(s, x, y, status) {
  const c = STATUS_COL[status] || COL.muted;
  s.addText(status.toUpperCase(), { x, y, w: 1.05, h: 0.24, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 7.5, bold: true, color: COL.white, charSpacing: 1, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: c }, line: { color: c, width: 0 } });
}

function valueChain(sl, i) {
  const s = frame(sl, i);
  const n = sl.stages.length, gap = 0.12, cw = (CW - gap * (n - 1)) / n, top = contentTop(sl);
  sl.stages.forEach((st, k) => {
    const x = MX + k * (cw + gap);
    onShape(s, k === 0 ? pres.shapes.PENTAGON : pres.shapes.CHEVRON,
      { x, y: top, w: cw + (k < n - 1 ? 0.1 : 0), h: 0.5, fill: "E3E8EE", padL: k === 0 ? 0.16 : 0.4, padR: 0.3 },
      { fontSize: 12, bold: true, color: COL.ink }, st.name);
    let y = top + 0.68;
    st.items.forEach((it) => {
      const h = 0.62 + lines(it.text, cw - 0.28, 12) * 0.205 + 0.12;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h, fill: { color: COL.white }, line: { color: COL.hair, width: 0.75 } });
      chip(s, x + 0.14, y + 0.14, it.status);
      if (it.market) s.addText(it.market.toUpperCase(), { x: x + 1.27, y: y + 0.14, w: cw - 1.4, h: 0.24, isTextBox: true, margin: 0,
        fontFace: F.body, fontSize: 7.5, bold: true, color: COL.muted, charSpacing: 1, valign: "middle" });
      s.addText(it.text, { x: x + 0.14, y: y + 0.44, w: cw - 0.28, h: h - 0.52, isTextBox: true, margin: 0,
        fontFace: F.body, fontSize: 12, color: COL.text, valign: "top" });
      y += h + 0.14;
    });
  });
  // legend
  const ly = 6.08;
  let lx = MX;
  const used = new Set(sl.stages.flatMap((st) => st.items.map((it) => it.status)));
  ["In use", "Developed", "Testing"].filter((st) => used.has(st)).forEach((st) => { chip(s, lx, ly, st); lx += 1.2; });
  if (sl.legend_note) s.addText(t(sl.legend_note), { x: lx + 0.1, y: ly - 0.06, w: CW - (lx - MX) - 0.1, h: 0.38, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 10, color: COL.muted, valign: "middle" });
}

function twoStats(sl, i) {
  const s = frame(sl, i);
  const gap = 0.35, cw = (CW - gap) / 2, top = contentTop(sl), h = 3.45;
  sl.stats.forEach((st, k) => {
    const x = MX + k * (cw + gap);
    const isTarget = /TARGET/.test(st.tag);
    s.addShape(pres.shapes.RECTANGLE, { x, y: top, w: cw, h, fill: { color: COL.panel }, line: { color: COL.panel, width: 0 } });
    const c = isTarget ? COL.amber : COL.teal;
    s.addText(st.tag, { x: x + 0.4, y: top + 0.35, w: 1.6, h: 0.28, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 8.5, bold: true, color: COL.white, charSpacing: 1.5, align: "center", valign: "middle",
      shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: c }, line: { color: c, width: 0 } });
    s.addText(st.value, { x: x + 0.38, y: top + 0.75, w: cw - 0.8, h: 1.15, isTextBox: true, margin: 0,
      fontFace: F.head, fontSize: 66, color: COL.ink, valign: "middle" });
    s.addText(t(st.label), { x: x + 0.4, y: top + 1.95, w: cw - 0.8, h: 0.7, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 17, bold: true, color: COL.ink, valign: "top" });
    s.addText(t(st.detail), { x: x + 0.4, y: top + 2.7, w: cw - 0.8, h: 0.6, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 13, color: COL.text, valign: "top" });
  });
  onShape(s, pres.shapes.RECTANGLE, { x: MX, y: top + h + 0.3, w: CW, h: 0.75, fill: COL.white, line: COL.hair, lineW: 0.75, padL: 0.25, padR: 0.3 },
    { fontSize: 14 }, [{ text: "So what   ", options: { bold: true, color: COL.teal } }, { text: t(sl.so_what), options: { color: COL.ink } }]);
}

function heroStat(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl), h = 3.45, gap = 0.35, hw = 7.6, sw = CW - hw - gap;
  // hero
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: top, w: hw, h, fill: { color: COL.ink }, line: { color: COL.ink, width: 0 } });
  s.addText(sl.hero.tag, { x: MX + 0.45, y: top + 0.4, w: 1.7, h: 0.28, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9, bold: true, color: COL.white, charSpacing: 1.5, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: COL.teal }, line: { color: COL.teal, width: 0 } });
  s.addText(sl.hero.value, { x: MX + 0.42, y: top + 0.8, w: hw - 0.9, h: 1.3, isTextBox: true, margin: 0,
    fontFace: F.head, fontSize: 80, color: COL.white, valign: "middle" });
  s.addText(t(sl.hero.label), { x: MX + 0.45, y: top + 2.15, w: hw - 0.9, h: 0.45, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 20, bold: true, color: COL.white, valign: "top" });
  s.addText(t(sl.hero.detail), { x: MX + 0.45, y: top + 2.65, w: hw - 0.9, h: 0.6, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 13.5, color: COL.onDark, valign: "top" });
  // secondary
  const sx = MX + hw + gap;
  s.addShape(pres.shapes.RECTANGLE, { x: sx, y: top, w: sw, h, fill: { color: COL.panel }, line: { color: COL.panel, width: 0 } });
  s.addText(sl.secondary.tag, { x: sx + 0.35, y: top + 0.4, w: 1.2, h: 0.28, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9, bold: true, color: COL.white, charSpacing: 1.5, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: COL.amber }, line: { color: COL.amber, width: 0 } });
  s.addText(sl.secondary.value, { x: sx + 0.33, y: top + 0.85, w: sw - 0.66, h: 0.9, isTextBox: true, margin: 0,
    fontFace: F.head, fontSize: 48, color: COL.ink, valign: "middle" });
  s.addText(t(sl.secondary.label), { x: sx + 0.35, y: top + 1.85, w: sw - 0.7, h: 0.6, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 15, bold: true, color: COL.ink, valign: "top" });
  s.addText(t(sl.secondary.detail), { x: sx + 0.35, y: top + 2.5, w: sw - 0.7, h: 0.8, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 12.5, color: COL.text, valign: "top" });
  onShape(s, pres.shapes.RECTANGLE, { x: MX, y: top + h + 0.3, w: CW, h: 0.7, fill: COL.white, line: COL.hair, lineW: 0.75, padL: 0.25, padR: 0.3 },
    { fontSize: 14 }, [{ text: "So what   ", options: { bold: true, color: COL.teal } }, { text: t(sl.so_what), options: { color: COL.ink } }]);
}

function hypotheses(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.15, tx = MX + 0.6, qx = MX + 2.3, qw = 5.35, hx = qx + qw + 0.4, hw = W - MX - hx;
  s.addText(sl.col_heads[0].toUpperCase(), { x: qx, y: top, w: qw, h: 0.3, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9.5, bold: true, color: COL.muted, charSpacing: 1.5 });
  s.addText(sl.col_heads[1].toUpperCase(), { x: hx, y: top, w: hw, h: 0.3, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9.5, bold: true, color: COL.muted, charSpacing: 1.5 });
  const rowH = 1.35, r0 = top + 0.45;
  sl.rows.forEach((r, k) => {
    const y = r0 + k * rowH;
    s.addShape(pres.shapes.LINE, { x: MX, y: y - 0.12, w: CW, h: 0, line: { color: COL.hair, width: 0.75 } });
    s.addText(String(k + 1), { x: MX, y, w: 0.5, h: 0.6, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 30, color: COL.teal, valign: "top" });
    s.addText(r.topic.toUpperCase(), { x: tx, y: y + 0.12, w: 1.6, h: 0.3, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 10, bold: true, color: COL.teal, charSpacing: 1.5 });
    s.addText(r.text, { x: qx, y, w: qw, h: rowH - 0.25, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15.5, color: COL.ink, valign: "top" });
    s.addText(r.how, { x: hx, y, w: hw, h: rowH - 0.25, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 13.5, color: COL.text, valign: "top" });
  });
}

function timeline(sl, i) {
  const s = frame(sl, i);
  const bt = contentTop(sl), blockH = 3.6, off = Math.min(0.3, Math.max(0, (6.45 - bt - blockH) / 2));
  const x0 = MX, x1 = 8.55, ly = bt + off + 0.95, n = sl.events.length;
  s.addShape(pres.shapes.LINE, { x: x0 + 0.1, y: ly, w: x1 - x0 - 0.2, h: 0, line: { color: COL.hair, width: 2 } });
  const step = (x1 - x0) / n;
  sl.events.forEach((ev, k) => {
    const cx = x0 + step * k + 0.12;
    const r = ev.emphasis ? 0.3 : 0.22;
    s.addShape(pres.shapes.OVAL, { x: cx, y: ly - r / 2, w: r, h: r,
      fill: { color: ev.emphasis ? COL.teal : COL.white }, line: { color: COL.teal, width: 1.75 } });
    s.addText(ev.when, { x: cx, y: ly - 0.78, w: step - 0.15, h: 0.4, isTextBox: true, margin: 0,
      fontFace: F.head, fontSize: 18, bold: false, color: ev.emphasis ? COL.teal : COL.ink, valign: "bottom" });
    s.addText(t(ev.text), { x: cx, y: ly + 0.35, w: step - 0.2, h: 2.4, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 13, bold: !!ev.emphasis, color: COL.text, valign: "top" });
  });
  // aside
  const ax = 9.05, aw = W - MX - ax, ay = bt + off, ah = blockH;
  s.addShape(pres.shapes.RECTANGLE, { x: ax, y: ay, w: aw, h: ah, fill: { color: COL.ink }, line: { color: COL.ink, width: 0 } });
  s.addText(t(sl.aside.head).toUpperCase(), { x: ax + 0.35, y: ay + 0.35, w: aw - 0.7, h: 0.3, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 9.5, bold: true, color: "5FB3B0", charSpacing: 1.5 });
  s.addText(t(sl.aside.body), { x: ax + 0.35, y: ay + 0.8, w: aw - 0.7, h: 1.5, isTextBox: true, margin: 0,
    fontFace: F.head, fontSize: 22, italic: true, color: COL.white, valign: "top" });
  s.addText(t(sl.aside.note), { x: ax + 0.35, y: ay + ah - 1.1, w: aw - 0.7, h: 0.8, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 12.5, color: COL.onDark, valign: "bottom" });
}

function twoColumns(sl, i) {
  const s = frame(sl, i);
  const gap = 0.35, cw = (CW - gap) / 2, top = contentTop(sl) + 0.1;
  const need = (items) => 0.9 + items.reduce((a, it) => a + lines(t(it), cw - 1.1, 14) * 0.255 + 0.22, 0) + 0.1;
  const h = Math.min(6.25 - top, Math.max(3.2, need(sl.left.items), need(sl.right.items)));
  [["left", false], ["right", true]].forEach(([key, quiet], k) => {
    const col = sl[key], x = MX + k * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: top, w: cw, h,
      fill: { color: quiet ? COL.panel : COL.white }, line: { color: quiet ? COL.panel : COL.hair, width: 0.75 } });
    s.addText(col.head, { x: x + 0.35, y: top + 0.28, w: cw - 0.7, h: 0.4, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 15, bold: true, color: COL.ink });
    let y = top + 0.9;
    col.items.forEach((it, j) => {
      const nl = lines(t(it), cw - 1.1, 14), ih = nl * 0.255;
      if (quiet) {
        s.addShape(pres.shapes.OVAL, { x: x + 0.37, y: y + 0.06, w: 0.2, h: 0.2, fill: { color: COL.panel }, line: { color: COL.muted, width: 1.25 } });
      } else {
        s.addShape(pres.shapes.OVAL, { x: x + 0.37, y: y + 0.06, w: 0.2, h: 0.2, fill: { color: COL.teal }, line: { color: COL.teal, width: 0 } });
      }
      s.addText(t(it), { x: x + 0.75, y, w: cw - 1.1, h: ih + 0.05, isTextBox: true, margin: 0,
        fontFace: F.body, fontSize: 14, color: COL.text, valign: "top" });
      y += ih + 0.22;
    });
  });
  s.addText(t(sl.footnote), { x: MX, y: top + h + 0.12, w: CW, h: 0.4, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 10, italic: true, color: COL.muted, valign: "top" });
}

function questions(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.25, rowH = 0.9;
  sl.questions.forEach((q, k) => {
    const y = top + k * rowH;
    if (k > 0) s.addShape(pres.shapes.LINE, { x: MX, y: y - 0.1, w: CW, h: 0, line: { color: COL.hair, width: 0.75 } });
    s.addText(String(k + 1), { x: MX, y, w: 0.5, h: 0.6, isTextBox: true, margin: 0,
      fontFace: F.head, fontSize: 26, color: COL.teal, valign: "top" });
    s.addText(q.topic.toUpperCase(), { x: MX + 0.6, y: y + 0.1, w: 1.9, h: 0.3, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 9.5, bold: true, color: COL.teal, charSpacing: 1.5 });
    s.addText(q.text, { x: MX + 2.6, y: y + 0.02, w: CW - 2.6, h: 0.66, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 16, color: COL.ink, valign: "top" });
  });
}

function proposal(sl, i) {
  const s = frame(sl, i);
  const gap = 0.3, n = sl.columns.length, cw = (CW - gap * (n - 1)) / n, top = contentTop(sl) + 0.1, h = 1.95;
  sl.columns.forEach((c, k) => {
    const x = MX + k * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: top, w: cw, h, fill: { color: COL.panel }, line: { color: COL.panel, width: 0 } });
    s.addText(c.head, { x: x + 0.3, y: top + 0.25, w: cw - 0.6, h: 0.4, isTextBox: true, margin: 0,
      fontFace: F.head, fontSize: 19, color: COL.teal });
    s.addText(c.body, { x: x + 0.3, y: top + 0.75, w: cw - 0.6, h: 1.1, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 13.5, color: COL.text, valign: "top" });
  });
  const py = top + h + 0.4, pn = sl.phases.length, pw = CW / pn;
  sl.phases.forEach((p, k) => {
    const x = MX + k * pw;
    onShape(s, k === 0 ? pres.shapes.PENTAGON : pres.shapes.CHEVRON,
      { x, y: py, w: pw + (k < pn - 1 ? 0.12 : 0), h: 0.95, fill: k === pn - 1 ? COL.teal : COL.ink, padL: k === 0 ? 0.3 : 0.6, padR: 0.45 },
      { color: COL.white },
      [{ text: p.when, options: { bold: true, fontSize: 13, breakLine: true } }, { text: p.what, options: { fontSize: 12 } }]);
  });
  s.addText(fmt(t(sl.ask), { color: COL.ink }), { x: MX, y: py + 1.2, w: CW, h: 0.7, isTextBox: true, margin: 0,
    fontFace: F.body, fontSize: 14, valign: "top" });
}

function about(sl, i) {
  const s = frame(sl, i);
  const gap = 0.35, cw = (CW - gap) / 2, top = contentTop(sl) + 0.1, rh = 1.95;
  sl.blocks.forEach((b, k) => {
    const x = MX + (k % 2) * (cw + gap), y = top + Math.floor(k / 2) * (rh + 0.25);
    const isStatus = b.head === "Status";
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: rh,
      fill: { color: isStatus && !STATUS.final ? "FBF6EC" : COL.panel }, line: { color: COL.panel, width: 0 } });
    s.addText(b.head, { x: x + 0.3, y: y + 0.25, w: cw - 0.6, h: 0.35, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 13, bold: true, color: isStatus && !STATUS.final ? COL.amber : COL.teal });
    s.addText(fmt(b.body, { color: COL.text }), { x: x + 0.3, y: y + 0.68, w: cw - 0.6, h: rh - 0.85, isTextBox: true, margin: 0,
      fontFace: F.body, fontSize: 13.5, valign: "top" });
  });
}


// ================================================================ v3 visual layouts
const ICONS = {};
async function prerenderIcons() {
  const React = require("react"), RDS = require("react-dom/server"), sharp = require("sharp"), lu = require("react-icons/lu");
  const want = new Set(JSON.stringify(story).match(/"Lu[A-Za-z0-9]+"/g)?.map((x) => x.slice(1, -1)) || []);
  ["LuCheck", "LuTarget", "LuLandmark"].forEach((n) => want.add(n));
  for (const name of want) {
    if (!lu[name]) throw new Error(`unknown icon ${name}`);
    for (const [key, color] of [["white", "#FFFFFF"], ["teal", "#" + COL.teal], ["ink", "#" + COL.ink], ["muted", "#" + COL.muted]]) {
      const svg = RDS.renderToStaticMarkup(React.createElement(lu[name], { size: 256, color, strokeWidth: 1.75 }));
      const buf = await sharp(Buffer.from(svg)).png().toBuffer();
      ICONS[`${name}:${key}`] = "image/png;base64," + buf.toString("base64");
    }
  }
}
function icon(s, name, x, y, size, color) {
  s.addImage({ data: ICONS[`${name}:${color || "white"}`], x, y, w: size, h: size, altText: name.replace(/^Lu/, "") });
}
function iconDisc(s, name, cx, cy, d, fill, iconColor) {
  s.addShape(pres.shapes.OVAL, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
  const isz = d * 0.5; icon(s, name, cx - isz / 2, cy - isz / 2, isz, iconColor || "white");
}
function strap(s, sl, y, iconName) {
  if (!sl.strap) return;
  const h = 0.62;
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y, w: CW, h, fill: { color: COL.panel }, line: { color: COL.panel, width: 0 } });
  let tx = MX + 0.3;
  if (iconName) { icon(s, iconName, MX + 0.28, y + (h - 0.3) / 2, 0.3, "teal"); tx = MX + 0.75; }
  s.addText(t(sl.strap), { x: tx, y, w: CW - (tx - MX) - 0.3, h, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, color: COL.ink, valign: "middle" });
}
function pendingStamp(s, x, y) {
  s.addText("AWAITING SOURCE DOCUMENTS", { x, y, w: 3.0, h: 0.34, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 9, bold: true,
    color: COL.amber, charSpacing: 1.5, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06, fill: { color: "FBF6EC" }, line: { color: COL.amber, width: 1 } });
}

function tiles(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.1, n = sl.tiles.length, gap = 0.3, tw = (CW - gap * (n - 1)) / n, th = 3.15;
  sl.tiles.forEach((tl, k) => {
    const x = MX + k * (tw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: top, w: tw, h: th, fill: { color: k === n - 1 ? COL.ink : COL.panel }, line: { color: k === n - 1 ? COL.ink : COL.panel, width: 0 } });
    const dark = k === n - 1;
    iconDisc(s, tl.icon, x + 0.75, top + 0.75, 0.82, dark ? COL.teal : COL.teal, "white");
    s.addText(tl.big, { x: x + 0.4, y: top + 1.3, w: tw - 0.8, h: 1.0, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 52, color: dark ? COL.white : COL.ink, valign: "bottom" });
    s.addText(t(tl.line), { x: x + 0.42, y: top + 2.35, w: tw - 0.84, h: 0.65, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, color: dark ? COL.onDark : COL.text, valign: "top" });
  });
  strap(s, sl, top + th + 0.3, "LuLandmark");
}

function lifecycle(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.15, n = sl.stages.length, cw = CW / n, d = 0.95, cy = top + d / 2;
  s.addShape(pres.shapes.LINE, { x: MX + cw / 2, y: cy, w: CW - cw, h: 0, line: { color: COL.hair, width: 2 } });
  sl.stages.forEach((st, k) => {
    const cx = MX + cw * k + cw / 2;
    iconDisc(s, st.icon, cx, cy, d, COL.teal, "white");
    s.addText(st.name, { x: cx - cw / 2, y: top + d + 0.15, w: cw, h: 0.35, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, bold: true, color: COL.ink, align: "center" });
    st.items.forEach((it, j) => {
      const py = top + d + 0.7 + j * 0.62, pw = cw - 0.16, px = cx - pw / 2;
      const c = STATUS_COL[it.status] || COL.muted;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: px, y: py, w: pw, h: 0.48, rectRadius: 0.24, fill: { color: COL.white }, line: { color: c, width: 1.25 } });
      s.addShape(pres.shapes.OVAL, { x: px + 0.17, y: py + 0.17, w: 0.14, h: 0.14, fill: { color: c }, line: { color: c, width: 0 } });
      s.addText(it.text, { x: px + 0.4, y: py, w: pw - (it.market ? 0.78 : 0.5), h: 0.48, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.ink, valign: "middle" });
      if (it.market) s.addText(it.market, { x: px + pw - 0.42, y: py, w: 0.3, h: 0.48, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 9, bold: true, color: COL.muted, align: "right", valign: "middle" });
    });
  });
  const ly = 6.08; let lx = MX;
  [["In use", COL.teal], ["Testing", COL.amber]].forEach(([lab, c]) => {
    s.addShape(pres.shapes.OVAL, { x: lx, y: ly + 0.07, w: 0.16, h: 0.16, fill: { color: c }, line: { color: c, width: 0 } });
    s.addText(lab, { x: lx + 0.25, y: ly, w: 1.1, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.text, valign: "middle" });
    lx += 1.35;
  });
  s.addText("MY = Malaysia operations", { x: lx, y: ly, w: 3, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.muted, valign: "middle" });
}

function donut(s, cx, cy, d, pct, color, track) {
  s.addChart(pres.charts.DOUGHNUT, [{ name: "share", labels: ["value", "rest"], values: [pct, 100 - pct] }], {
    x: cx - d / 2, y: cy - d / 2, w: d, h: d, holeSize: 72, chartColors: [color, track], showLegend: false, showValue: false,
    showLabel: false, showPercent: false, showTitle: false, dataBorder: { pt: 0, color: "FFFFFF" }, firstSliceAng: 0 });
}
function donuts(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.05;
  // primary (result)
  const d1 = 3.0, c1x = MX + 2.0, c1y = top + 1.75;
  donut(s, c1x, c1y, d1, sl.primary.pct, COL.teal, "E3E8EE");
  s.addText(`${sl.primary.pct}%`, { x: c1x - 1.2, y: c1y - 0.45, w: 2.4, h: 0.9, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 44, color: COL.ink, align: "center", valign: "middle" });
  s.addText(sl.primary.tag.toUpperCase(), { x: MX + 4.0, y: top + 0.9, w: 1.3, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 9, bold: true, color: COL.white, charSpacing: 1.5, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: COL.teal }, line: { color: COL.teal, width: 0 } });
  s.addText(t(sl.primary.label), { x: MX + 4.0, y: top + 1.35, w: 2.6, h: 1.2, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 18, bold: true, color: COL.ink, valign: "top" });
  // secondary (target)
  const d2 = 2.1, c2x = MX + 8.25, c2y = top + 1.75;
  donut(s, c2x, c2y, d2, sl.secondary.pct, "D9B98A", "F1F3F6");
  s.addText(`${sl.secondary.approx ? "~" : ""}${sl.secondary.pct}%`, { x: c2x - 0.9, y: c2y - 0.35, w: 1.8, h: 0.7, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 30, color: COL.ink, align: "center", valign: "middle" });
  s.addText(sl.secondary.tag.toUpperCase(), { x: MX + 9.55, y: top + 1.05, w: 1.1, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 9, bold: true, color: COL.white, charSpacing: 1.5, align: "center", valign: "middle",
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.05, fill: { color: COL.amber }, line: { color: COL.amber, width: 0 } });
  s.addText(t(sl.secondary.label), { x: MX + 9.55, y: top + 1.5, w: 2.55, h: 1.0, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, color: COL.text, valign: "top" });
  strap(s, sl, top + 3.75, "LuTarget");
}

function valueBars(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.35, maxV = Math.max(...sl.figures.map((f) => f._num)), lw = 3.1, bx = MX + lw, bwMax = 4.5, bh = 0.62, gap = 0.42;
  sl.figures.forEach((f, k) => {
    const y = top + k * (bh + gap), w = bwMax * f._num / maxV, lead = k === 0;
    s.addText(f.label, { x: MX, y, w: lw - 0.2, h: bh, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, bold: lead, color: COL.ink, valign: "middle" });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y, w, h: bh, fill: { color: lead ? COL.teal : "C9D3DE" }, line: { color: lead ? COL.teal : "C9D3DE", width: 0 } });
    s.addText(`S$${f.value}m`, { x: bx + w + 0.15, y, w: 1.6, h: bh, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, bold: lead, color: COL.ink, valign: "middle" });
  });
  s.addText(sl.unit, { x: bx, y: top + 3 * (bh + gap) - 0.25, w: 4, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.muted });
  // callout
  const cx = MX + 9.3, cy = top - 0.05, cw2 = W - MX - cx;
  s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: cw2, h: 2.75, fill: { color: COL.ink }, line: { color: COL.ink, width: 0 } });
  s.addText("Every 1%", { x: cx + 0.3, y: cy + 0.3, w: cw2 - 0.6, h: 0.4, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 14, color: COL.onDark });
  s.addText(sl.title.derived.display.replace("S$", "S$"), { x: cx + 0.28, y: cy + 0.7, w: cw2 - 0.5, h: 1.0, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 40, color: COL.white, valign: "middle" });
  s.addText("a year on claims and benefits", { x: cx + 0.3, y: cy + 1.75, w: cw2 - 0.6, h: 0.75, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 14, color: COL.onDark, valign: "top" });
  if (sl.strap) s.addText(t(sl.strap), { x: MX, y: 5.95, w: CW, h: 0.4, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, italic: true, color: COL.muted });
}

function pendingBars(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.35, lw = 2.4, bx = MX + lw, bh = 0.6, gap = 0.35, widths = [5.6, 4.0, 3.2, 0];
  sl.bars.forEach((b, k) => {
    const y = top + k * (bh + gap), isClient = k === sl.bars.length - 1;
    s.addText(b, { x: MX, y, w: lw - 0.2, h: bh, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, bold: isClient, color: COL.ink, valign: "middle" });
    if (isClient) s.addText("Not reported in dollars", { x: bx, y, w: 4, h: bh, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 14, italic: true, color: COL.amber, valign: "middle" });
    else s.addShape(pres.shapes.RECTANGLE, { x: bx, y, w: widths[k], h: bh, fill: { color: "E6EAEF" }, line: { color: "C9D3DE", width: 0.75, dashType: "dash" } });
  });
  s.addText(sl.axis, { x: bx, y: top + sl.bars.length * (bh + gap) - 0.2, w: 5, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.muted });
  pendingStamp(s, W - MX - 3.0, top);
  s.addText(t(sl.note), { x: W - MX - 3.0, y: top + 0.5, w: 3.0, h: 0.8, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.muted, align: "center" });
}

function pendingTimeline(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.6, n = sl.milestones.length, x0 = MX + 1.5, x1 = W - MX - 1.5, ly = top + 1.2, step = (x1 - x0) / (n - 1);
  s.addShape(pres.shapes.LINE, { x: x0, y: ly, w: x1 - x0, h: 0, line: { color: COL.hair, width: 3 } });
  sl.milestones.forEach((m, k) => {
    const cx = x0 + step * k;
    s.addShape(pres.shapes.OVAL, { x: cx - 0.2, y: ly - 0.2, w: 0.4, h: 0.4, fill: { color: k === 0 ? COL.ink : COL.white }, line: { color: COL.ink, width: 2 } });
    s.addText(m.when, { x: cx - 1.4, y: ly - 1.05, w: 2.8, h: 0.6, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 28, color: COL.ink, align: "center", valign: "bottom" });
    s.addText(m.what, { x: cx - 1.5, y: ly + 0.4, w: 3.0, h: 0.8, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 15, color: COL.text, align: "center", valign: "top" });
  });
  pendingStamp(s, (W - 3.0) / 2, top + 2.75);
  s.addText(t(sl.note), { x: MX, y: top + 3.2, w: CW, h: 0.4, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.muted, align: "center" });
}

function disclosureMatrix(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.05, lx = MX, lw = 6.2, colX = MX + 7.0, colW = 3.0, rh = 0.66;
  sl.columns.forEach((c, k) => s.addText(c, { x: colX + k * colW, y: top, w: colW, h: 0.4, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 12, bold: true, color: COL.muted, align: "center", valign: "bottom" }));
  sl.rows.forEach((r, j) => {
    const y = top + 0.55 + j * rh;
    s.addShape(pres.shapes.LINE, { x: MX, y: y + rh, w: CW - 1.4, h: 0, line: { color: COL.hair, width: 0.75 } });
    icon(s, r.icon, lx, y + (rh - 0.34) / 2, 0.34, "ink");
    s.addText(r.label, { x: lx + 0.6, y, w: lw, h: rh, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 16, color: COL.ink, valign: "middle" });
    r.cells.forEach((c, k) => {
      const cx = colX + k * colW + colW / 2, cy = y + rh / 2, d = 0.42;
      if (c.state === "yes") {
        s.addShape(pres.shapes.OVAL, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: COL.teal }, line: { color: COL.teal, width: 0 } });
        icon(s, "LuCheck", cx - 0.13, cy - 0.13, 0.26, "white");
      } else {
        s.addShape(pres.shapes.OVAL, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: COL.white }, line: { color: COL.muted, width: 1.5 } });
      }
    });
  });
  const ky = top + 0.55 + sl.rows.length * rh + 0.2;
  s.addShape(pres.shapes.OVAL, { x: colX + 0.2, y: ky + 0.06, w: 0.2, h: 0.2, fill: { color: COL.teal }, line: { color: COL.teal, width: 0 } });
  s.addText("Disclosed", { x: colX + 0.5, y: ky, w: 1.1, h: 0.32, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.text, valign: "middle" });
  s.addShape(pres.shapes.OVAL, { x: colX + 1.55, y: ky + 0.06, w: 0.2, h: 0.2, fill: { color: COL.white }, line: { color: COL.muted, width: 1.25 } });
  s.addText("Not described", { x: colX + 1.85, y: ky, w: 1.4, h: 0.32, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, color: COL.text, valign: "middle" });
  if (sl.strap) s.addText(t(sl.strap), { x: MX, y: 6.0, w: CW, h: 0.35, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 11, italic: true, color: COL.muted });
}

function iconCards(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.2, n = sl.cards.length, gap = 0.35, w = (CW - gap * (n - 1)) / n, h = 3.6;
  sl.cards.forEach((c, k) => {
    const x = MX + k * (w + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: top, w, h, fill: { color: COL.panel }, line: { color: COL.panel, width: 0 } });
    iconDisc(s, c.icon, x + 0.8, top + 0.85, 0.9, COL.teal, "white");
    s.addText(c.head, { x: x + 0.4, y: top + 1.55, w: w - 0.8, h: 0.5, isTextBox: true, margin: 0, fontFace: F.head, fontSize: 24, color: COL.teal });
    s.addText(c.text, { x: x + 0.4, y: top + 2.15, w: w - 0.8, h: 1.2, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 17, color: COL.ink, valign: "top" });
  });
}

function plan(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.1, lw = 3.2, gx = MX + lw, gw = 6.0, days = 12, dw = gw / days, rh = 0.5;
  for (let d = 1; d <= days; d++) {
    s.addText(String(d), { x: gx + (d - 1) * dw, y: top, w: dw, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 10, color: COL.muted, align: "center" });
    if (d > 1) s.addShape(pres.shapes.LINE, { x: gx + (d - 1) * dw, y: top + 0.35, w: 0, h: sl.lanes.length * rh + 0.05, line: { color: "EDF0F4", width: 0.75 } });
  }
  s.addText("Working day", { x: MX, y: top, w: lw - 0.2, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 10, color: COL.muted });
  sl.lanes.forEach((ln, k) => {
    const y = top + 0.42 + k * rh, last = k === sl.lanes.length - 1;
    s.addText(ln.name, { x: MX, y, w: lw - 0.2, h: rh - 0.08, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 13, color: COL.ink, valign: "middle" });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: gx + (ln.from - 1) * dw + 0.03, y: y + 0.07, w: (ln.to - ln.from + 1) * dw - 0.06, h: rh - 0.22, rectRadius: 0.08,
      fill: { color: last ? COL.teal : COL.ink }, line: { color: last ? COL.teal : COL.ink, width: 0 } });
  });
  // outputs
  const ox = gx + gw + 0.45, ow = W - MX - ox;
  s.addText("YOU RECEIVE", { x: ox, y: top, w: ow, h: 0.3, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 10, bold: true, color: COL.muted, charSpacing: 1.5 });
  sl.outputs.forEach((o, k) => {
    const y = top + 0.45 + k * 0.62;
    iconDisc(s, o.icon, ox + 0.22, y + 0.22, 0.44, COL.teal, "white");
    s.addText(o.text, { x: ox + 0.6, y, w: ow - 0.6, h: 0.46, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 13, color: COL.ink, valign: "middle" });
  });
  // ask
  const ay = top + 0.42 + sl.lanes.length * rh + 0.55;
  s.addShape(pres.shapes.RECTANGLE, { x: MX, y: ay, w: CW, h: 0.75, fill: { color: COL.ink }, line: { color: COL.ink, width: 0 } });
  s.addText("THE ASK", { x: MX + 0.3, y: ay, w: 1.3, h: 0.75, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 10, bold: true, color: "5FB3B0", charSpacing: 1.5, valign: "middle" });
  s.addText(fmt(t(sl.ask), { color: COL.white }), { x: MX + 1.6, y: ay, w: CW - 1.9, h: 0.75, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 14, valign: "middle" });
}

function aboutMin(sl, i) {
  const s = frame(sl, i);
  const top = contentTop(sl) + 0.25;
  sl.lines.forEach((ln, k) => {
    const y = top + k * 0.95;
    iconDisc(s, ln.icon, MX + 0.35, y + 0.35, 0.7, COL.teal, "white");
    s.addText(fmt(ln.text, { color: COL.ink }), { x: MX + 1.0, y, w: CW - 1.2, h: 0.7, isTextBox: true, margin: 0, fontFace: F.body, fontSize: 17, valign: "middle" });
  });
}

const LAYOUTS = { cover, exec_summary: execSummary, value_chain: valueChain, two_stats: twoStats, hero_stat: heroStat, hypotheses,
  timeline, two_columns: twoColumns, questions, proposal, about,
  tiles, lifecycle, donuts, value_bars: valueBars, pending_bars: pendingBars, pending_timeline: pendingTimeline,
  disclosure_matrix: disclosureMatrix, icon_cards: iconCards, plan, about_min: aboutMin };

(async () => {
  await prerenderIcons();
  story.slides.forEach((sl, i) => {
    const fn = LAYOUTS[sl.layout];
    if (!fn) throw new Error(`unknown layout ${sl.layout}`);
    fn(sl, i);
  });
  await pres.writeFile({ fileName: outFile });
  if (applyTheme) await applyTheme(outFile, THEME);
  console.log(`wrote ${outFile} (${story.slides.length} slides, ${STATUS.final ? "FINAL" : STATUS.marker})`);
})();
