"""Builds the UFlex AI strategy page. Charts are generated from the model's numbers so they are drawn to scale."""
import html, json
from openpyxl import load_workbook

OUT = "/home/claude/plumb/runs/uflex/2026-11-03/uflex-ai-strategy.html"
SCR = "/tmp/claude-0/-home-claude/598a1fc4-71d0-5dc6-b611-3434cc77d612/scratchpad"

def read(path):
    wb = load_workbook(path, data_only=True)
    u, c = wb["Use cases"], wb["Cash flow"]
    return {
        "uc": [u[f"D{r}"].value for r in (5, 6, 7, 8)], "rec": u["D9"].value, "cash": u["D10"].value,
        "ebitda": u["D13"].value, "ebitda_pct": u["D14"].value, "lev0": u["D15"].value, "lev1": u["D16"].value,
        "dlev": u["D17"].value, "gap_share": u["D19"].value,
        "cf_ben": [c[f"{x}10"].value for x in "BCD"], "cf_cost": [c[f"{x}11"].value for x in "BCD"],
        "cf_net": [c[f"{x}12"].value for x in "BCD"], "cf_rec": [c[f"{x}14"].value for x in "BCD"],
        "cf_netrec": [c[f"{x}15"].value for x in "BCD"], "cash_rel": [c[f"{x}9"].value for x in "BCD"],
        "npv": c["B18"].value, "roc": c["B19"].value, "roc_rec": c["B20"].value, "payback": c["B21"].value,
    }

BASE = read("/home/claude/plumb/runs/uflex/2026-11-03/UFlex-AI-business-case.xlsx")
LOW = read(f"{SCR}/s1.xlsx")
HIGH = read(f"{SCR}/s3.xlsx")
json.dump({"base": BASE, "low": LOW, "high": HIGH}, open("/home/claude/plumb/runs/uflex/2026-11-03/model-results.json", "w"), indent=1, default=str)

def cr(x, d=0):
    return f"₹{x:,.{d}f} cr"

def r0(x):
    return f"{x:,.0f}"

E = html.escape

# ------------------------------------------------------------------ charts (SVG, to scale)
def value_chart():
    names = ["Film-line yield and quality", "Energy optimisation", "Inventory and procurement (carrying cost)", "Converting waste and artwork"]
    W, H, L, R, T, rowh = 760, 300, 290, 70, 30, 56
    xmax = 40.0
    sx = lambda v: L + (W - L - R) * v / xmax
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Annual benefit at run-rate by use case, low, base and high scenarios, ₹ crore">']
    for t in range(0, 41, 10):
        x = sx(t)
        out.append(f'<line x1="{x:.1f}" y1="{T-6}" x2="{x:.1f}" y2="{T+rowh*4}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{T+rowh*4+18}" class="tick" text-anchor="middle">{t}</text>')
    for i, n in enumerate(names):
        y = T + i * rowh + rowh / 2
        lo, ba, hi = LOW["uc"][i], BASE["uc"][i], HIGH["uc"][i]
        out.append(f'<text x="{L-12}" y="{y+4:.1f}" class="lab" text-anchor="end">{E(n)}</text>')
        out.append(f'<rect x="{sx(0):.1f}" y="{y-11:.1f}" width="{sx(ba)-sx(0):.1f}" height="22" class="bar"/>')
        out.append(f'<line x1="{sx(lo):.1f}" y1="{y:.1f}" x2="{sx(hi):.1f}" y2="{y:.1f}" class="range"/>')
        out.append(f'<line x1="{sx(lo):.1f}" y1="{y-7:.1f}" x2="{sx(lo):.1f}" y2="{y+7:.1f}" class="range"/>')
        out.append(f'<line x1="{sx(hi):.1f}" y1="{y-7:.1f}" x2="{sx(hi):.1f}" y2="{y+7:.1f}" class="range"/>')
        out.append(f'<text x="{sx(hi)+8:.1f}" y="{y+4:.1f}" class="val">{ba:.1f}</text>')
    out.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-4}" class="tick" text-anchor="middle">₹ crore a year at full run-rate · bar = base, whiskers = low to high</text>')
    out.append("</svg>")
    return "".join(out)

def cashflow_chart():
    W, H, L, R, T, B = 760, 300, 60, 20, 20, 50
    ymin, ymax = -40, 130
    sy = lambda v: T + (H - T - B) * (ymax - v) / (ymax - ymin)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Base case three-year cash flow: benefits, inventory cash release and costs, ₹ crore">']
    for t in range(-40, 131, 20):
        y = sy(t)
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/>')
        out.append(f'<text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    gw = (W - L - R) / 3
    for i in range(3):
        cx = L + gw * i + gw / 2
        rec, cash, cost, net = BASE["cf_rec"][i], BASE["cash_rel"][i], BASE["cf_cost"][i], BASE["cf_net"][i]
        bw = 46
        x1 = cx - bw - 6
        out.append(f'<rect x="{x1:.1f}" y="{sy(rec):.1f}" width="{bw}" height="{sy(0)-sy(rec):.1f}" class="bar"/>')
        if cash > 0:
            out.append(f'<rect x="{x1:.1f}" y="{sy(rec+cash):.1f}" width="{bw}" height="{sy(rec)-sy(rec+cash):.1f}" class="bar2"/>')
        out.append(f'<text x="{x1+bw/2:.1f}" y="{sy(rec+cash)-6:.1f}" class="val" text-anchor="middle">{rec+cash:.0f}</text>')
        x2 = cx + 6
        out.append(f'<rect x="{x2:.1f}" y="{sy(0):.1f}" width="{bw}" height="{sy(-cost)-sy(0):.1f}" class="cost"/>')
        out.append(f'<text x="{x2+bw/2:.1f}" y="{sy(-cost)+14:.1f}" class="val" text-anchor="middle">−{cost:.0f}</text>')
        out.append(f'<text x="{cx:.1f}" y="{H-26}" class="lab" text-anchor="middle">Year {i+1}</text>')
        out.append(f'<text x="{cx:.1f}" y="{H-10}" class="tick" text-anchor="middle">net {net:+.0f}</text>')
    out.append("</svg>")
    return "".join(out)

def leverage_chart():
    W, H, L, R, T = 760, 190, 300, 50, 20
    xmax = 4.6
    sx = lambda v: L + (W - L - R) * v / xmax
    rows = [("FY26 actual", BASE["lev0"], "bar"), ("With the AI programme at run-rate (base)", BASE["lev1"], "bar2"), ("CRISIL downgrade trigger", 3.25, "trig")]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Net debt to EBITDA: FY26 actual, pro forma with the AI programme, and the CRISIL trigger">']
    for t in [0, 1, 2, 3, 4]:
        x = sx(t)
        out.append(f'<line x1="{x:.1f}" y1="{T-4}" x2="{x:.1f}" y2="{T+3*44}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{T+3*44+16}" class="tick" text-anchor="middle">{t}.0x</text>')
    for i, (lab, v, cls) in enumerate(rows):
        y = T + i * 44 + 22
        out.append(f'<text x="{L-12}" y="{y+4:.1f}" class="lab" text-anchor="end">{E(lab)}</text>')
        out.append(f'<rect x="{sx(0):.1f}" y="{y-12:.1f}" width="{sx(v)-sx(0):.1f}" height="24" class="{cls}"/>')
        out.append(f'<text x="{sx(v)+8:.1f}" y="{y+4:.1f}" class="val">{v:.2f}x</text>')
    out.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-2}" class="tick" text-anchor="middle">Net debt ÷ reported EBITDA (pro forma: run-rate uplift and inventory cash)</text>')
    out.append("</svg>")
    return "".join(out)

def matrix_chart():
    # value (base, ₹ cr/yr, recurring or upside qualitative) vs feasibility (1-5, our judgement from outside)
    pts = [("UC1", "Film yield & quality", 4.0, BASE["uc"][0], "core"), ("UC2", "Energy", 3.6, BASE["uc"][1], "core"),
           ("UC3", "Inventory & procurement", 4.3, BASE["uc"][2], "core"), ("UC4", "Converting & artwork", 3.4, BASE["uc"][3], "core"),
           ("UC5", "Predictive maintenance", 3.0, None, "up"), ("UC6", "Plant copilot", 3.9, None, "up"),
           ("UC7", "Recycling & traceability", 2.4, None, "up"), ("UC8", "Price & quote", 2.2, None, "up"), ("UC9", "AI in machines sold", 2.0, None, "up")]
    W, H, L, R, T, B = 760, 360, 60, 30, 20, 50
    ymax = 25
    sx = lambda f: L + (W - L - R) * (f - 1.5) / 3.5
    sy = lambda v: T + (H - T - B) * (ymax - v) / ymax
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Use-case prioritisation: base-case value against feasibility">']
    out.append(f'<rect x="{sx(3.25):.1f}" y="{sy(ymax):.1f}" width="{sx(5)-sx(3.25):.1f}" height="{sy(0)-sy(ymax):.1f}" class="zone"/>')
    out.append(f'<text x="{sx(4.98):.1f}" y="{sy(ymax)+16:.1f}" class="tick" text-anchor="end">Wave 1 zone</text>')
    for t in range(0, 26, 5):
        y = sy(t)
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/>')
        out.append(f'<text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    for f, lab in [(2, "harder"), (3, ""), (4, ""), (5, "easier")]:
        out.append(f'<text x="{sx(f):.1f}" y="{H-30}" class="tick" text-anchor="middle">{lab}</text>')
    out.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-10}" class="tick" text-anchor="middle">Feasibility from outside-in evidence (data likely available, integration effort, time to first value)</text>')
    out.append(f'<text x="14" y="{(T+H-B)/2:.1f}" class="tick" text-anchor="middle" transform="rotate(-90 14 {(T+H-B)/2:.1f})">Base value, ₹ cr a year</text>')
    for uc, lab, f, v, kind in pts:
        x = sx(f)
        if v is None:
            continue
        else:
            y = sy(v)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" class="pt"/>')
            anchor, dx = ("end", -12) if f > 4.1 else ("start", 12)
            out.append(f'<text x="{x+dx:.1f}" y="{y+4:.1f}" class="lab" text-anchor="{anchor}">{uc} {E(lab)}</text>')
    ups = [p for p in pts if p[3] is None]
    for k, (uc, lab, f, v, kind) in enumerate(ups):
        x = L + 70 + k * ((W - L - R - 140) / (len(ups) - 1)); y = sy(3.2)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="ptup"/>')
        out.append(f'<text x="{x:.1f}" y="{y+(20 if k % 2 == 0 else -12):.1f}" class="tick" text-anchor="middle">{uc} {E(lab)}</text>')
    out.append(f'<text x="{L+8:.1f}" y="{sy(7.4):.1f}" class="tick">Upside, not sized until UFlex data is available (position not to scale):</text>')
    out.append("</svg>")
    return "".join(out)

def ref_arch():
    W, H = 900, 560
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Reference architecture: plant and enterprise sources, edge layer, governed data fabric, AI services, applications, with security and governance across all layers">']
    def box(x, y, w, h, title, items, cls="lay"):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>')
        out.append(f'<text x="{x+12}" y="{y+20}" class="bt">{E(title)}</text>')
        for i, it in enumerate(items):
            out.append(f'<text x="{x+12}" y="{y+40+i*16}" class="bi">{E(it)}</text>')
    # layers bottom to top
    box(60, 452, 380, 92, "Plant sources (each film, chip and converting site)", ["Line PLC/DCS: extrusion, stretching, winding", "Inline thickness gauges and defect scanners", "Energy meters: chillers, compressors, ovens", "Print inspection, presses, slitters"])
    box(460, 452, 380, 92, "Enterprise sources", ["ERP (Oracle EBS per a past case study; to confirm)", "Quality / lab records, maintenance (CMMS)", "Planning, procurement, sales orders, CRM", "Artwork, specifications, SOPs, recipes"])
    box(60, 350, 780, 78, "Plant edge (on site, sovereign)", ["Historian + time-series buffer · edge GPU for vision models · store-and-forward when the WAN drops", "Models that act in seconds run here: defect classification, process advisories, energy set-points (advisory first)"])
    box(60, 248, 780, 78, "Governed data fabric (group)", ["Lakehouse with one data model: site → line → grade → order → roll (genealogy) · data owners and quality rules per domain", "Governed APIs to ERP and planning · lineage for every dataset that feeds a model · India data residency by default"])
    box(60, 146, 780, 78, "AI services", ["Vision and anomaly models · process-optimisation and energy models · demand, inventory and price-risk models", "Sovereign language models with retrieval over SOPs and specs (plant copilot) · MLOps: registry, monitoring, drift, retraining"])
    box(60, 44, 780, 78, "Applications and decisions", ["Line operator and shift-lead advisories · quality release and root-cause workbench · energy cockpit", "S&OP and buyer workbench · artwork and label assurance · KPI tracking against baselines (value ledger)"])
    # cross-cutting
    out.append(f'<rect x="856" y="44" width="34" height="500" rx="4" class="cross"/>')
    out.append(f'<text x="878" y="294" class="bt" text-anchor="middle" transform="rotate(-90 878 294)">Security (IEC 62443) · AI governance · DPDP, CERT-In</text>')
    for y in (430, 328, 226, 124):
        out.append(f'<line x1="450" y1="{y+18}" x2="450" y2="{y-2}" class="flow" marker-end="url(#ah)"/>')
    out.insert(1, '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>')
    out.append(f'<text x="20" y="300" class="tick" text-anchor="middle" transform="rotate(-90 20 300)">Data flows up; decisions flow back to the line</text>')
    out.append("</svg>")
    return "".join(out)

def flow(steps, label):
    W, n = 900, len(steps)
    bw = (W - 20 * (n - 1)) / n
    out = [f'<svg viewBox="0 0 {W} 112" role="img" aria-label="{E(label)}"><defs><marker id="a{abs(hash(label))%9999}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    mid = f"a{abs(hash(label))%9999}"
    for i, (t, sub) in enumerate(steps):
        x = i * (bw + 20)
        out.append(f'<rect x="{x:.1f}" y="6" width="{bw:.1f}" height="100" rx="4" class="{"lay2" if i in (0, n-1) else "lay"}"/>')
        out.append(f'<text x="{x+10:.1f}" y="28" class="bt">{E(t)}</text>')
        words, line, ly = sub.split(), "", 48
        maxc = int(bw / 7.0)
        for w in words:
            if len(line) + len(w) + 1 > maxc:
                out.append(f'<text x="{x+10:.1f}" y="{ly}" class="bi">{E(line)}</text>'); ly += 15; line = w
            else:
                line = (line + " " + w).strip()
        out.append(f'<text x="{x+10:.1f}" y="{ly}" class="bi">{E(line)}</text>')
        if i < n - 1:
            out.append(f'<line x1="{x+bw+2:.1f}" y1="56" x2="{x+bw+18:.1f}" y2="56" class="flow" marker-end="url(#{mid})"/>')
    out.append("</svg>")
    return "".join(out)

def gantt():
    W, L, T, rh = 900, 380, 34, 30
    H = T + 10 * rh + 12
    months = 24
    sx = lambda m: L + (W - L - 10) * m / months
    rows = [
        ("Readiness sprint (2 weeks)", 0, 0.5, "s"), ("Gate 1: go / no-go on pilot", 0.5, 0.6, "g"),
        ("Lighthouse pilot: UC1 + UC2, one India film site", 0.6, 3.6, "p"), ("UC3 inventory and procurement (enterprise)", 0.6, 4.6, "p"),
        ("Gate 2: measured against baseline", 3.6, 3.75, "g"), ("UC4 converting and artwork (Noida, Jammu)", 3.75, 9, "p"),
        ("Scale UC1 + UC2 to 3 more film sites", 4, 12, "c"), ("UC5 predictive maintenance pilot; UC6 plant copilot", 6, 12, "c"),
        ("Gate 3: year-1 value review, scale plan", 12, 12.2, "g"), ("Remaining film sites; UC7 traceability", 12.2, 24, "c"),
    ]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Roadmap over 24 months with decision gates">']
    for m in range(0, 25, 3):
        x = sx(m)
        out.append(f'<line x1="{x:.1f}" y1="{T-8}" x2="{x:.1f}" y2="{T+len(rows)*rh}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{T-12}" class="tick" text-anchor="middle">M{m}</text>')
    for i, (lab, a, b, k) in enumerate(rows):
        y = T + i * rh
        out.append(f'<text x="{L-10}" y="{y+rh/2+4:.1f}" class="lab" text-anchor="end">{E(lab)}</text>')
        if k == "g":
            cx = sx(a); cy = y + rh / 2
            out.append(f'<path d="M{cx:.1f},{cy-9:.1f} L{cx+9:.1f},{cy:.1f} L{cx:.1f},{cy+9:.1f} L{cx-9:.1f},{cy:.1f} z" class="gate"/>')
        else:
            cls = {"s": "bar2", "p": "bar", "c": "bar3"}[k]
            out.append(f'<rect x="{sx(a):.1f}" y="{y+7:.1f}" width="{max(sx(b)-sx(a), 4):.1f}" height="{rh-14}" rx="2" class="{cls}"/>')
    out.append("</svg>")
    return "".join(out)

# ------------------------------------------------------------------ page
b, lo, hi = BASE, LOW, HIGH
CSS = """
:root{
 /* Layout: a report column of ~68ch with wide figures; numbered sections because the document is read in order */
 --bg:#F6F8F9; --surface:#FFFFFF; --ink:#0E1B2B; --text:#24313F; --muted:#5D6B78; --line:#D6DEE4;
 --accent:#0A7287; --accent-soft:#D9EEF2; --accent2:#7FB8C4; --cost:#B4572E; --amber:#9A6A12; --amber-soft:#F6EBD3; --zone:#EEF6F8;
 --f-display:"Source Serif 4", Georgia, "Times New Roman", serif; --f-body:"IBM Plex Sans", "Segoe UI", Arial, sans-serif; --f-mono:"IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0D151E;--surface:#121D28;--ink:#EAF1F5;--text:#C9D5DE;--muted:#8D9CA9;--line:#273645;--accent:#5CC0D3;--accent-soft:#163742;--accent2:#2E7B8A;--cost:#E08A5E;--amber:#E2B75E;--amber-soft:#3A2F17;--zone:#132a33;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0D151E;--surface:#121D28;--ink:#EAF1F5;--text:#C9D5DE;--muted:#8D9CA9;--line:#273645;--accent:#5CC0D3;--accent-soft:#163742;--accent2:#2E7B8A;--cost:#E08A5E;--amber:#E2B75E;--amber-soft:#3A2F17;--zone:#132a33;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:var(--f-body);font-size:16px;line-height:1.6;margin:0}
.wrap{max-width:1040px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:40px 80px}
.col{max-width:68ch}
header.cover{border-bottom:1px solid var(--line);padding-bottom:32px;margin-bottom:40px}
.eyebrow{font-family:var(--f-mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
h1{font-family:var(--f-display);font-weight:600;color:var(--ink);font-size:clamp(34px,5vw,52px);line-height:1.08;margin:.3em 0 .35em;text-wrap:balance}
h2{font-family:var(--f-display);font-weight:600;color:var(--ink);font-size:30px;line-height:1.2;margin:2.4em 0 .5em;text-wrap:balance;scroll-margin-top:16px}
h2 .n{font-family:var(--f-mono);font-size:14px;color:var(--accent);display:block;letter-spacing:.08em;margin-bottom:6px}
h3{font-family:var(--f-body);font-weight:600;color:var(--ink);font-size:19px;margin:1.8em 0 .4em}
h4{font-family:var(--f-mono);font-weight:500;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:1.4em 0 .4em}
p{margin:.6em 0}
.lede{font-size:19px;color:var(--text);max-width:62ch}
.meta{display:flex;flex-wrap:wrap;gap:8px 28px;font-size:13px;color:var(--muted);margin-top:20px}
.meta b{color:var(--ink);font-weight:600}
.status{display:inline-block;font-family:var(--f-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:var(--amber-soft);color:var(--amber);padding:3px 8px;border-radius:3px}
nav.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:4px 24px;margin:28px 0 0;font-size:14px}
nav.toc a{color:var(--text);text-decoration:none;border-bottom:1px solid transparent}
nav.toc a:hover,nav.toc a:focus-visible{color:var(--accent);border-bottom-color:var(--accent)}
a{color:var(--accent)} a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:24px 0}
.kpi{background:var(--surface);border:1px solid var(--line);padding:18px 20px;min-width:0}
.kpi .v{font-family:var(--f-display);font-size:38px;color:var(--ink);line-height:1.1;font-variant-numeric:tabular-nums}
.kpi .l{font-size:14px;color:var(--text);margin-top:6px}
.kpi .r{font-family:var(--f-mono);font-size:12px;color:var(--muted);margin-top:8px}
.callout{background:var(--accent-soft);border-left:3px solid var(--accent);padding:14px 18px;margin:20px 0;max-width:72ch}
.note{background:var(--amber-soft);border-left:3px solid var(--amber);padding:12px 16px;margin:16px 0;font-size:14px;max-width:72ch}
ol.recs{padding-left:1.2em} ol.recs li{margin:.5em 0}
.tbl{overflow-x:auto;margin:16px 0;border:1px solid var(--line);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:620px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--f-mono);font-weight:500;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);background:var(--bg)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr:last-child td{border-bottom:none}
figure{margin:20px 0;background:var(--surface);border:1px solid var(--line);padding:16px}
figure .scroll{overflow-x:auto}
figure svg{display:block;width:100%;min-width:640px;height:auto}
figcaption{font-size:13px;color:var(--muted);margin-top:10px}
svg text{font-family:var(--f-body)}
svg .grid{stroke:var(--line);stroke-width:1} svg .axis{stroke:var(--muted);stroke-width:1}
svg .tick{fill:var(--muted);font-size:12px} svg .lab{fill:var(--text);font-size:13px} svg .val{fill:var(--ink);font-size:13px;font-weight:600;font-family:var(--f-mono)}
svg .bar{fill:var(--accent)} svg .bar2{fill:var(--accent2)} svg .bar3{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1}
svg .cost{fill:var(--cost)} svg .trig{fill:none;stroke:var(--cost);stroke-width:2;stroke-dasharray:5 4}
svg .range{stroke:var(--ink);stroke-width:1.5} svg .zone{fill:var(--zone)}
svg .pt{fill:var(--accent)} svg .ptup{fill:var(--surface);stroke:var(--muted);stroke-width:1.5}
svg .lay{fill:var(--surface);stroke:var(--line);stroke-width:1.2} svg .lay2{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1}
svg .cross{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1}
svg .bt{fill:var(--ink);font-size:13px;font-weight:600} svg .bi{fill:var(--text);font-size:12px}
svg .flow{stroke:var(--accent);stroke-width:1.6;fill:none} svg .arrowhead{fill:var(--accent)} svg .gate{fill:var(--amber)}
.uc{background:var(--surface);border:1px solid var(--line);padding:20px 22px;margin:22px 0}
.uc h3{margin-top:0}
.uc .tag{font-family:var(--f-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:4px 28px;margin:10px 0}
.facts div{min-width:0}
.facts dt{font-family:var(--f-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:10px}
.facts dd{margin:2px 0 0}
.lbl{font-family:var(--f-mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;padding:1px 6px;border-radius:3px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.q{font-style:italic}
footer{margin-top:64px;border-top:1px solid var(--line);padding-top:16px;font-size:13px;color:var(--muted)}
ul.src{font-size:13px;padding-left:1.1em} ul.src li{margin:.25em 0;overflow-wrap:anywhere}
@media (max-width:560px){h2{font-size:25px}.kpi .v{font-size:32px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
"""

def T(headers, rows, num=()):
    h = "".join(f'<th class="{"num" if i in num else ""}">{x}</th>' for i, x in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

S = []
S.append(f"""<title>UFlex AI Strategy</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="cover">
 <div class="eyebrow">UFlex Limited · AI strategy · outside-in</div>
 <h1>Lower cost per kilogram, freed cash, and data customers will soon require</h1>
 <p class="lede">An AI strategy for UFlex, built from public disclosures to 3 November 2026: where AI pays at the bottom of the film cycle, what to build first, how it fits together, and what it is worth on UFlex's own numbers.</p>
 <div class="meta"><span><b>Prepared by</b> PLUMB Advisory</span><span><b>Date</b> November 2026</span><span><b>Basis</b> annual reports FY25–FY26, results and investor decks to Q1 FY27, public industry sources</span><span class="status">For discussion · not validated with UFlex data</span></div>
 <nav class="toc" aria-label="Contents">
  <a href="#summary">1 · Summary</a><a href="#uflex">2 · UFlex today</a><a href="#industry">3 · The industry</a><a href="#maturity">4 · AI maturity</a>
  <a href="#strategy">5 · The strategy</a><a href="#usecases">6 · Use cases</a><a href="#architecture">7 · Architecture</a><a href="#roi">8 · Value and ROI</a>
  <a href="#roadmap">9 · Roadmap and gates</a><a href="#operating">10 · Operating model and governance</a><a href="#risks">11 · Risks</a><a href="#next">12 · Next step</a>
 </nav>
</header>
""")

# 1 Summary
S.append(f"""<section><h2 id="summary"><span class="n">1</span>Summary</h2>
<div class="col">
<p>UFlex sells film into a market where, in Polyplex's words, <span class="q">"Pricing is a function of demand/supply"</span>, and Indian producers expect <span class="q">"seven to eight lines coming in India"</span> over three years. UFlex's own film lines ran at 77.5% utilisation in FY26, and net debt reached 4.35 times EBITDA, against a CRISIL downgrade trigger of 3.25 times. AI will not set the film price. It can lower the cost of every kilogram UFlex makes, release cash tied up in inventory, and produce the recycled-content and recyclability data that India's 2026 rules and the EU's packaging regulation now ask for.</p>
<p>We recommend a focused programme of four use cases, run as one playbook across UFlex's nine film-manufacturing countries, with the business case measured against plant baselines and a stop-or-scale decision at each gate.</p>
</div>
<div class="kpis">
 <div class="kpi"><div class="v">{cr(b['rec'])}</div><div class="l">recurring annual benefit at full run-rate, base case</div><div class="r">range {cr(lo['rec'])} to {cr(hi['rec'])}</div></div>
 <div class="kpi"><div class="v">{cr(b['cash'])}</div><div class="l">one-off cash released from inventory (about 7 days of ~100)</div><div class="r">range {cr(lo['cash'])} to {cr(hi['cash'])}</div></div>
 <div class="kpi"><div class="v">−{b['dlev']:.2f}x</div><div class="l">net debt to EBITDA, pro forma at run-rate</div><div class="r">about {b['gap_share']*100:.0f}% of the gap to CRISIL's 3.25x trigger</div></div>
</div>
<div class="col">
<p>The base case adds about {cr(b['ebitda'])} a year to EBITDA ({b['ebitda_pct']*100:.1f}% of FY26), saves about {cr(b['uc'][2])} a year in carrying cost, and pays back within year 1 once the inventory cash is counted (year 2 on recurring benefits alone). These figures are deliberately conservative: they use the low end of published results, charge all build cost up front, and leave out benefits that are hard to attribute.</p>
<h3>What we recommend</h3>
<ol class="recs">
 <li><b>Aim AI at cost per kilogram, not price.</b> Film-line yield and quality (UC1) and energy (UC2) on one India film site first, then the same playbook across the other film sites.</li>
 <li><b>Release cash in parallel.</b> Planning, procurement and inventory intelligence (UC3) needs only ERP and planning data, so it can start in month 1 and directly supports deleveraging.</li>
 <li><b>Protect the converting margin and the FMCG relationship.</b> Make-ready, colour and artwork assurance (UC4) in the Noida and Jammu flexible-packaging plants.</li>
 <li><b>Build the data foundation once.</b> A plant edge layer and a group data fabric with roll-level genealogy, kept on UFlex's own infrastructure. Every later use case, and the traceability that PPWR and India's EPR rules require, reuses it.</li>
 <li><b>Decide on evidence.</b> Start with a two-week readiness sprint that replaces our assumptions with UFlex plant data, then a 12-week lighthouse pilot with written stop conditions.</li>
</ol>
</div></section>""")

# 2 UFlex today
S.append(f"""<section><h2 id="uflex"><span class="n">2</span>UFlex today</h2>
<div class="col"><p>UFlex describes itself as <span class="q">"India's largest flexible packaging materials and Solutions Company"</span>. In FY26 it reported total income of ₹15,513 crore, EBITDA of ₹1,983.6 crore (12.8%) and profit after tax of ₹317.1 crore. Films are the core: 58.6% of revenue, from 636,160 tonnes a year of film capacity, of which 164,160 tonnes is in India and the rest in Egypt, Mexico, Poland, Russia, Nigeria, Hungary, Dubai and the USA. Revenue by destination was 56% international.</p></div>
{T(["Business", "FY26 share of revenue", "Scale (UFlex disclosures)"], [
 ["Packaging films (BOPET, BOPP, CPP, metallised; PET chips)", "58.6%", "636,160 MTPA film capacity; 492,779 MT produced in FY26 at 77.5% utilisation; PET chip plants at Panipat and in Egypt"],
 ["Packaging (flexible, aseptic liquid, holography)", "32.7%", "Flexible packaging ~100,000 MTPA (Noida, Jammu); aseptic cartons 12 bn packs a year at Sanand, Egypt plant in trials; holography 20,600 MTPA"],
 ["Engineering (packaging machines, printing cylinders)", "2.9%", "500 machines and 108,000 cylinders a year; machines described as featuring embedded AI for predictive maintenance (AR FY25)"],
 ["Others (inks, adhesives, coatings)", "5.1%", "69,730 MTPA chemicals capacity"],
])}
<h3>FY26 cost base: where AI can act</h3>
{T(["Line (consolidated, FY26)", "₹ crore", "% of revenue", "AI levers"], [
 ["Revenue from operations", "15,400.5", "100%", "—"],
 ["Cost of materials consumed", "8,877.0", "57.6%", "Yield, scrap, off-spec, converting waste (UC1, UC4)"],
 ["Employee benefit expense", "1,556.9", "10.1%", "Not targeted for reduction; copilot and advisories raise output per shift"],
 ["Other operating expenses (management definition)", "2,171.4", "14.1%", "Maintenance and spares (UC5, upside); sub-lines not disclosed"],
 ["Power and fuel", "739.3", "4.8%", "Energy optimisation (UC2)"],
 ["Inventories at 31 March 2026 (balance sheet)", "2,408.3", "≈100 days", "Planning, procurement, inventory (UC3)"],
 ["Net debt at 31 March 2026 (balance sheet)", "8,621.8", "4.35x EBITDA", "Cash release and EBITDA both reduce leverage"],
], num=(1, 2))}
<p class="note">Statutory "other expenses" for FY26 were not legible in the filed scan, so the management figure from the Q4 FY26 earnings release is used. Expense sub-lines (repairs, stores and spares, freight) are in the annual-report notes and should be read in the sprint.</p>
<h3>In management's own words</h3>
{T(["Theme", "What UFlex has said", "Source"], [
 ["Oversupply", '<span class="q">"We don\'t want to get into a price war matching with import."</span>', "Q2 FY26 call"],
 ["Tariff-driven glut", 'Tariff-rerouted volumes <span class="q">"led to a supply glut in the major non-US markets."</span>', "Q3 FY26 release"],
 ["Raw materials", '<span class="q">"raw material prices, both for PET chips, for BOPET as well as for homopolymer for BOPP lines, went up quite dramatically"</span>', "Q4 FY26 call"],
 ["Margin outlook", '<span class="q">"I can\'t say the same thing with equal conviction about how the packaging films margins will remain"</span>', "Q4 FY26 call"],
 ["Direction", 'The focus is <span class="q">"building higher-value, technologyled, and sustainability-driven capabilities"</span>', "AR FY26, Chairman"],
])}
<h3>What makes UFlex distinctive</h3>
<div class="col"><ol>
 <li><b>A film playbook can be replicated nine times.</b> Few Indian peers run film lines in nine countries. A use case proven on one line can be repeated on many, which is where AI economics improve.</li>
 <li><b>It controls more of the chain than its peers.</b> PET chips, film, chemicals, cylinders, machines, converting and recycling under one roof means the data to trace a defect or a recycled-content claim from resin to pouch can exist inside one company.</li>
 <li><b>It builds the machines.</b> The engineering business can turn plant learning into product features, and has to meet the EU Machinery Regulation for exports from January 2027.</li>
 <li><b>Recycling capacity is already built.</b> 79,020 MTPA of rPET chips and 34,897 MTPA of rMLP granules, with the Noida plant commissioned in 2026, give UFlex the material behind recycled-content claims its customers now need.</li>
 <li><b>Its customers are global brand owners.</b> Nestlé, PepsiCo, P&amp;G and Mondelez are among those UFlex names. Their packaging commitments and EU rules push data requirements down to suppliers.</li>
</ol></div>
</section>""")

# 3 Industry
S.append(f"""<section><h2 id="industry"><span class="n">3</span>The industry</h2>
<div class="col">
<p><b>A capacity cycle, not a cost cycle.</b> Polyplex's May 2026 investor deck says film raw materials are largely <span class="q">"pass through"</span> and that new BOPET capacity is concentrated in China (global capacity growth 7.1% a year against 4.0% outside China). Cosmo First expects BOPET and BOPP margins to stay volatile as new Indian lines arrive. UFlex's Q1 FY27 spike (EBITDA margin 17.0%, <span class="q">"highest in 21 quarters"</span>) came from a war-driven price jump, and management already expects <span class="q">"some normalization"</span>.</p>
<p><b>Feedstock got more volatile in 2026.</b> Indian PTA prices rose about 31% within days in March 2026 and polypropylene list prices rose a cumulative ₹23 per kg. UFlex's own deck says the West Asia conflict is disrupting raw-material production and transit. Planning and procurement decisions are worth more than they were.</p>
<p><b>Regulation now asks for data.</b> India's Plastic Waste Management (Amendment) Rules 2026 set recycled-content targets for flexible packaging of 10% rising to 20% by 2027-28, and 5% rising to 10% for multilayer packaging, with QR or barcode labelling in force since July 2025 and environmental compensation of ₹5,000 a tonne for shortfalls. The EU Packaging and Packaging Waste Regulation has applied since 12 August 2026, with recyclability grades and recycled-content targets binding from 2030, averaged per plant per year. Both require reliable recycled-content and recyclability data by plant and format.</p>
</div>
<h3>What peers show</h3>
{T(["Company", "AI evidence", "Result", "Evidence type"], [
 ["ACG Packaging Materials, Shirwal (India)", "WEF Lighthouse, Jan 2026: generative AI, machine learning, IIoT, digital twins", "Lead time −40%, defects −71%, energy −31%, on-time-in-full +34%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["Kunlene Film Industries, Suzhou (BOPP films)", "WEF Lighthouse, Jan 2026", "Defects −31%, R&amp;D lead time −45%, minimum order size −83%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["Mondi, Hilm (Austria)", "Predictive quality 24 hours ahead with operator recommendations", "Rework and waste −50% versus 2018", '<span class="lbl">Company-reported</span>'],
 ["Amcor", "Vision for seal defects, predictive maintenance, changeover root-cause analysis", "No figures disclosed", '<span class="lbl">Company, qualitative</span>'],
 ["Polyplex, Cosmo First, Huhtamaki India", "Describe digitalisation", "No quantified AI outcomes disclosed", '<span class="lbl">Annual reports</span>'],
])}
<div class="col"><p>Among Indian film producers, none we reviewed discloses a measured AI programme. A disciplined, measured programme would put UFlex ahead of its domestic peers, and the two Lighthouses show the ceiling. We treat them as upper bounds, not as the base case: they are whole-site transformations over several years.</p></div>
</section>""")

# 4 Maturity
mat_rows = [
 ["D1 Strategy and ambition", "AI appears in annual-report strategy text across businesses: <span class=\"q\">\"AI-powered predictive maintenance\"</span>, <span class=\"q\">\"AI-based quality control\"</span>, <span class=\"q\">\"AI-driven track-and-trace\"</span> (AR FY25); <span class=\"q\">\"AI-enabled segregation systems\"</span> (AR FY26). No AI targets, timeline or named owner disclosed; AI not discussed on FY26–FY27 earnings calls.", "2 (AI referenced in strategy without targets)", "Is there an approved AI plan, sponsor and budget?"],
 ["D2 Data foundations", "No public information on data ownership, quality, a historian or a data platform. BRSR mentions <span class=\"q\">\"digitization of processes\"</span>.", "Not observable", "Which plants have a historian; how complete are line and quality data; who owns them?"],
 ["D3 Technology and platform", "Oracle E-Business Suite and Sales Cloud named in an undated Oracle case study. No MES, IoT or AI platform disclosed.", "Not observable", "Current ERP, MES, OT network and cloud estate; where could models run?"],
 ["D4 Talent and skills", "AR FY26 lists an <span class=\"q\">\"AIM-AIA (AI in Manufacturing)\"</span> training programme; participation not disclosed. No data or AI roles found in public job postings (careers portal not indexable).", "2 (programme exists; reach unknown)", "In-house data and AI skills; vendor dependence; uptake of AIM-AIA"],
 ["D5 Operating model", "No AI function or delivery model disclosed. A Global CIO is named in a third-party 2025 profile.", "Not observable", "Who would own AI delivery, and how do pilots reach production today?"],
 ["D6 Governance, risk and compliance", "BRSR references an <span class=\"q\">\"IT, Cyber Security &amp; Privacy Policy\"</span>. No AI policy or inventory disclosed; annual reports rarely carry these.", "Not observable", "AI policy, inventory and OT security standard in use"],
 ["D7 Culture and adoption", "No public signal.", "Not observable", "Use of AI tools on the shop floor and in offices; plant appetite"],
 ["D8 Value management", "No AI outcome disclosed in any filing, deck or call.", "Not observable", "Are any AI or analytics benefits tracked against a baseline today?"],
]
S.append(f"""<section><h2 id="maturity"><span class="n">4</span>AI maturity, from the outside</h2>
<div class="col">
<p>We use PLUMB's 48-item maturity instrument, which scores eight dimensions from 1 to 5 and requires at least four scored items per dimension. Public information supports only a handful of items, so <b>no dimension can be scored from the outside</b>, and we do not publish a maturity score. What the evidence does show is consistent with the early "Discover" stage: AI is part of the stated direction, and no AI system in production with an owner and a measured outcome is visible. Annual reports rarely describe this, so the readiness sprint scores it properly with UFlex's own people.</p>
</div>
{T(["Dimension", "Public evidence", "Reading", "What the sprint must establish"], mat_rows)}
<p class="note">Outside-in signals can only pre-populate or challenge a score, never raise it above level 3. "Not observable" means there is no public evidence either way. It is not a low score.</p>
</section>""")

# 5 Strategy
S.append("""<section><h2 id="strategy"><span class="n">5</span>The strategy</h2>
<div class="col">
<p><b>Ambition.</b> Make UFlex the lowest-cost, best-evidenced film and flexible-packaging producer in its markets by using AI where it lowers cost per kilogram, frees cash and produces the compliance data customers need, and prove each step in rupees before scaling it.</p>
<h3>Four strategic choices</h3>
</div>
""" + T(["Choice", "What it means", "Why, for UFlex"], [
 ["Win the trough on cost per kilogram", "Yield, scrap, energy and changeover first. No use case whose value depends on price.", "Film prices follow supply and demand; utilisation was 77.5% in FY26. Cost per kilogram is what UFlex controls."],
 ["Turn data into cash", "Planning, procurement and inventory intelligence alongside the plant work.", "Net debt is 4.35x EBITDA with a Negative outlook; inventory is about 100 days."],
 ["Make compliance data an asset", "Roll-level genealogy from resin to finished pack, so recycled-content and recyclability claims can be evidenced.", "PWM 2026 targets, the QR labelling rule and EU PPWR all require it; global FMCG customers will ask suppliers for it."],
 ["One playbook, nine countries", "Prove on one India film site, then replicate a packaged playbook (data model, models, operating routine).", "UFlex's spread is the multiplier; each repeat costs a fraction of the first."],
]) + """
<div class="col">
<h3>Guiding principles</h3>
<ul>
 <li><b>Start with the data model, not the algorithm.</b> One governed model of site, line, grade, order and roll serves every use case.</li>
 <li><b>Sovereign by design.</b> Plant and customer data stay on UFlex infrastructure in India and at each site; external models are brought in, data is not sent out.</li>
 <li><b>Advise first, automate later.</b> Models recommend to operators until they have earned closed-loop control on a line.</li>
 <li><b>Measure everything against a baseline.</b> Every use case has a baseline captured before go-live, a named owner and a stop condition.</li>
 <li><b>Buy where the market is mature, build where UFlex is different.</b> Vision hardware, historians and planning engines are bought; the data model, process knowledge and playbook stay UFlex's own.</li>
</ul></div></section>""")

# 6 Use cases
def uc_card(tag, title, sponsor, problem, does, data, kpi, value, cost, ttv, evidence, risk, flowsvg):
    return f"""<article class="uc"><div class="tag">{tag}</div><h3>{title}</h3>
<dl class="facts">
 <div><dt>Problem in UFlex terms</dt><dd>{problem}</dd></div>
 <div><dt>What AI does</dt><dd>{does}</dd></div>
 <div><dt>Data needed</dt><dd>{data}</dd></div>
 <div><dt>KPIs and baseline</dt><dd>{kpi}</dd></div>
 <div><dt>Value logic (base)</dt><dd>{value}</dd></div>
 <div><dt>Indicative cost and time to first value</dt><dd>{cost}<br>{ttv}</dd></div>
 <div><dt>Evidence it works</dt><dd>{evidence}</dd></div>
 <div><dt>Main risks</dt><dd>{risk}</dd></div>
 <div><dt>Proposed sponsor</dt><dd>{sponsor}</dd></div>
</dl>
<figure><div class="scroll">{flowsvg}</div><figcaption>How it works: data in, model, decision, action, measurement.</figcaption></figure></article>"""

S.append(f"""<section><h2 id="usecases"><span class="n">6</span>Use cases</h2>
<div class="col"><p>We screened nine use cases against value on UFlex's cost lines and feasibility from the evidence available. Four form the core programme and carry the business case. Five are upside: real, but not sized until UFlex data is available.</p></div>
<figure><div class="scroll">{matrix_chart()}</div><figcaption>Base-case value for the four core use cases; open circles are upside cases not yet sized. Feasibility is our outside-in judgement, to be re-scored in the sprint.</figcaption></figure>
""")
S.append(uc_card("UC1 · Core · Wave 1", "Film-line yield and quality intelligence",
 "President – Technical and NPD, Packaging Films (P. L. Sirsamkar), with plant heads",
 "Scrap, off-spec rolls and edge trim on BOPET and BOPP lines are paid for in polymer, which is most of the ₹8,877 crore materials bill. Defects are found at inspection, and their cause in extrusion or stretching is found later, if at all.",
 "Classifies defects from inline scanners in real time, links each defect to the process conditions that caused it (melt temperature, draw ratios, tension, die settings), and advises operators on set-point corrections and grade changeovers before off-spec builds up.",
 "Defect-scanner images and events; line PLC/DCS tags at 1-second resolution; thickness-gauge profiles; roll and grade records; quality release data; changeover logs.",
 "Net good output (%), off-spec and scrap kg per tonne, changeover scrap and duration, customer complaints. Baseline: 3 months of line data before go-live.",
 f"Film materials (₹8,877 cr × 58.6% = ₹5,202 cr) × 0.6% net good-output gain × (1 − 40% regrind recovery) = <b>{cr(b['uc'][0],1)} a year</b> at full run-rate (range {cr(lo['uc'][0],1)} to {cr(hi['uc'][0],1)}).",
 "₹3 crore at the lighthouse site; about ₹1.2 crore for each further site (assumption).", "First advisories in 10–12 weeks on one line.",
 "Kunlene (BOPP films) defects −31% and ACG defects −71%, both WEF Lighthouses; Mondi Hilm rework and waste −50%. Our 0.6% is far below these.",
 "Scanner data access and labelling effort; operator trust; lines from different OEMs need separate integration.",
 flow([("Sense", "Defect scanner, gauges, PLC tags, roll IDs"), ("Edge model", "Defect classes and root-cause model, runs on site"), ("Advise", "Set-point and changeover advice on the operator screen"), ("Act", "Operator accepts or rejects; reason logged"), ("Measure", "Net good output and scrap kg/t against baseline")], "UC1 data flow")))
S.append(uc_card("UC2 · Core · Wave 1", "Energy optimisation",
 "Director – Global Operations (Apoorvshree Chaturvedi), with plant engineering",
 "Power and fuel cost ₹739 crore in FY26. UFlex targets carbon neutrality for Scope 1 and 2 by FY2035, and renewable electricity was 11% of India consumption.",
 "Models the energy use of extrusion, stretching ovens, chillers and compressors against grade, throughput and ambient conditions; recommends set-points and scheduling that cut kWh per kg without affecting quality.",
 "Sub-meter data by line and utility; line tags; grade schedule; ambient conditions; tariff structure.",
 "kWh per kg by line and grade; specific fuel use; tCO2e. Baseline: 3 months of metered data (no public kWh/kg benchmark exists for film lines).",
 f"Power and fuel × 75% addressable share × 3% saving = <b>{cr(b['uc'][1],1)} a year</b> at run-rate (range {cr(lo['uc'][1],1)} to {cr(hi['uc'][1],1)}).",
 "₹1.5 crore at the lighthouse site; about ₹0.6 crore per further site (assumption).", "First savings in 8–12 weeks where sub-metering exists.",
 "ACG Shirwal energy −31% (site-wide, WEF); McKinsey Lighthouse average energy and water −25%. Our 3% is the low end.",
 "Sub-metering gaps; savings that compete with throughput or quality targets.",
 flow([("Sense", "Sub-meters, utilities, line tags, weather"), ("Model", "Energy per kg by grade and condition"), ("Advise", "Set-points and load scheduling"), ("Act", "Engineer approves; later closed loop on utilities"), ("Measure", "kWh/kg and ₹ against baseline")], "UC2 data flow")))
S.append(uc_card("UC3 · Core · Wave 1", "Planning, procurement and inventory intelligence",
 "Group CFO (Arun Kumar Sharma), with the head of supply chain",
 "Inventories were ₹2,408 crore at 31 March 2026, about 100 days at a turnover of 3.67 times, in nine countries, while PTA, MEG and polypropylene prices swing sharply and net debt carries an 8.5% blended cost.",
 "Forecasts demand by grade, market and customer; sets inventory targets by item and plant; gives buyers price-risk signals for PTA, MEG, PET chips and polypropylene; flags slow-moving stock.",
 "ERP sales, inventory and purchase history; order book; production plans; supplier lead times; public polymer price series.",
 "Inventory days by category and plant; forecast accuracy; service level (on-time-in-full); purchase price against index. Baseline: last 24 months from ERP.",
 f"About 7 days of inventory released = <b>{cr(b['cash'])}</b> one-off cash; carrying cost at 8.5% = <b>{cr(b['uc'][2],1)} a year</b>. Buying-timing gains are not counted.",
 "₹4 crore enterprise build in year 1, ₹1 crore in year 2 (assumption).", "First inventory targets in 8 weeks; needs no plant sensors.",
 "Multi-Color (labels) reports forecast accuracy up 50% (vendor case study). We found no credible public figure for working-capital effects in packaging, so the 7-day release is an assumption to test in the sprint.",
 "Data quality in ERP across countries; planners keeping parallel spreadsheets; service-level trade-offs.",
 flow([("Data", "ERP sales, stock, purchases; order book"), ("Model", "Demand forecast, inventory targets, price-risk signals"), ("Plan", "S&OP and buyer workbench"), ("Act", "Planner sets targets; buyer times purchases"), ("Measure", "Inventory days, OTIF, cash released")], "UC3 data flow")))
S.append(uc_card("UC4 · Core · Wave 2", "Converting make-ready and artwork assurance",
 "Whole-Time Director and President – Flexible Packaging and NPD (Jeevaraj Gopal Pillai)",
 "Printing, lamination and slitting waste in the Noida and Jammu converting plants, plus artwork and label errors that reach FMCG customers. India's QR/barcode labelling rule raises the cost of a label error.",
 "Analyses press and inspection data to cut make-ready and colour-matching time; checks artwork and label content (text, barcodes, QR codes, regulatory marks) against the approved specification before plates or cylinders are made.",
 "Press and print-inspection data; colour measurements; job tickets; approved artwork, specifications and label rules.",
 "Make-ready waste metres per job; colour approvals at first pull; artwork errors caught before cylinder; customer complaints. Baseline: job history.",
 f"Packaging materials (₹8,877 cr × 32.7%) × 0.4% waste reduction × (1 − 20% recovery) = <b>{cr(b['uc'][3],1)} a year</b> (range {cr(lo['uc'][3],1)} to {cr(hi['uc'][3],1)}).",
 "₹2.5 crore in year 1, ₹0.5 crore in year 2 (assumption).", "Artwork checks in 6–8 weeks; print analytics in 12–16 weeks.",
 "Published converter waste: printing 3–5%, lamination 1–2%, slitting under 1%. Gravure 100% inspection at PPL cut print-quality complaints by 50% (vendor case study).",
 "Many job types and short runs; integration with prepress and cylinder workflow.",
 flow([("Sense", "Press data, inspection, colour readings, artwork files"), ("Model", "Make-ready advisor; artwork and label checker"), ("Advise", "Settings for the job; issues before cylinder"), ("Act", "Prepress fixes; press crew applies settings"), ("Measure", "Waste metres per job; errors caught")], "UC4 data flow")))
S.append("<h3>Upside use cases (not in the business case)</h3>" + T(["Use case", "What it would do", "Why not sized yet"], [
 ["UC5 Predictive maintenance and changeover optimisation", "Predict failures on extruders, stretching frames, chillers and compressors; shorten grade changes", "Repair and maintenance spend is not disclosed, and downtime is worth little while lines run at 77.5% utilisation. Deloitte's conservative range (maintenance cost −5–10%) applies once the baseline is known."],
 ["UC6 Sovereign plant copilot", "Answers operators' questions from SOPs, specs and past incidents, in local languages across nine countries", "Productivity and onboarding gains are hard to attribute; an enabler for UC1 and UC5."],
 ["UC7 Recycling feedstock sorting and recycled-content traceability", "AI sorting in rPET and rMLP plants; mass-balance and recycled-content evidence by plant and format", "Needs UFlex's EPR position and recycling-line data; strong compliance value under PWM 2026 and PPWR."],
 ["UC8 Price, mix and quote intelligence", "Customer- and grade-level margin analytics; faster, consistent quotes for 5,000+ customers", "Film prices follow supply and demand; value is uncertain until cost-to-serve data is available."],
 ["UC9 AI in machines UFlex sells", "Predictive maintenance and remote monitoring as a product feature of UFlex machines", "Product and EU Machinery Regulation questions first; a revenue opportunity, not a cost saving."],
]) + "</section>")

# 7 Architecture
S.append(f"""<section><h2 id="architecture"><span class="n">7</span>Architecture</h2>
<div class="col"><p>One reference architecture serves all nine use cases. It follows the pattern we use in process manufacturing: plant and enterprise sources feed a plant edge layer and a governed group data fabric; AI services run on top; decisions flow back to the line and to planners. Security and governance cut across every layer.</p></div>
<figure><div class="scroll">{ref_arch()}</div><figcaption>Reference architecture. The ERP detail comes from an undated Oracle case study and must be confirmed in the sprint.</figcaption></figure>
{T(["Layer", "Design decisions", "Build or buy"], [
 ["Plant edge", "A historian and edge compute at each film site. Vision and second-by-second models run on site so the line never depends on the WAN. Advisory mode first.", "Buy (historian, edge hardware); configure"],
 ["Data fabric", "One lakehouse and one data model (site, line, grade, order, roll), with named data owners and quality rules for each domain. India residency by default; overseas sites replicate only what group models need.", "Buy the platform; build the data model (UFlex's own asset)"],
 ["AI services", "Vision, anomaly, optimisation and forecasting models in a shared registry. Sovereign language models with retrieval for the copilot. MLOps covers monitoring, drift detection and retraining.", "Build models with a partner; buy planning and vision engines where mature"],
 ["Applications", "Operator advisories inside existing line screens where possible; a quality workbench; an energy cockpit; an S&amp;OP and buyer workbench; a value ledger tracking every use case against its baseline.", "Mix"],
 ["Security and governance", "OT network segmentation (IEC 62443), remote-access control for vendors, CERT-In 6-hour incident reporting and 180-day log retention in India, and an AI inventory with a risk tier and human-oversight rule for each system.", "Policy built; tools bought"],
])}
</section>""")

# 8 ROI
cf_rows = [["Recurring benefit"] + [f"{x:,.1f}" for x in b["cf_rec"]] + [f"{sum(b['cf_rec']):,.1f}"],
           ["Inventory cash release (one-off)"] + [f"{x:,.1f}" for x in b["cash_rel"]] + [f"{sum(b['cash_rel']):,.1f}"],
           ["Cost (build, run, team, change)"] + [f"({x:,.1f})" for x in b["cf_cost"]] + [f"({sum(b['cf_cost']):,.1f})"],
           ["<b>Net cash flow</b>"] + [f"<b>{x:,.1f}</b>" for x in b["cf_net"]] + [f"<b>{sum(b['cf_net']):,.1f}</b>"],
           ["Net, recurring benefit only"] + [f"{x:,.1f}" for x in b["cf_netrec"]] + [f"{sum(b['cf_netrec']):,.1f}"]]
sc_rows = [["Recurring benefit at run-rate (₹ cr a year)", f"{lo['rec']:.1f}", f"{b['rec']:.1f}", f"{hi['rec']:.1f}"],
           ["EBITDA uplift at run-rate (₹ cr a year)", f"{lo['ebitda']:.1f}", f"{b['ebitda']:.1f}", f"{hi['ebitda']:.1f}"],
           ["Inventory cash release, one-off (₹ cr)", f"{lo['cash']:.0f}", f"{b['cash']:.0f}", f"{hi['cash']:.0f}"],
           ["3-year NPV (₹ cr)", f"{lo['npv']:.0f}", f"{b['npv']:.0f}", f"{hi['npv']:.0f}"],
           ["3-year return on cost, recurring benefit only", f"{lo['roc_rec']:.2f}x", f"{b['roc_rec']:.2f}x", f"{hi['roc_rec']:.2f}x"],
           ["Net debt to EBITDA improvement at run-rate", f"−{lo['dlev']:.2f}x", f"−{b['dlev']:.2f}x", f"−{hi['dlev']:.2f}x"]]
S.append(f"""<section><h2 id="roi"><span class="n">8</span>Value and ROI</h2>
<div class="col">
<p><b>Method.</b> Every benefit is measured on a recurring FY26 cost line, never on a balance-sheet or valuation figure. Benefit rates sit at the low end of published results. All build and integration cost is charged in the year it is incurred. Benefits that are hard to attribute (predictive maintenance, the copilot, recycling, pricing) are left out. Extra film output is not valued, because in an oversupplied market it is not extra profit. The workbook that accompanies this document holds every assumption in its own cell, with low, base and high scenarios.</p>
</div>
<figure><div class="scroll">{value_chart()}</div><figcaption>Annual benefit at full run-rate. Total base {cr(b['rec'],1)}; low {cr(lo['rec'],1)}; high {cr(hi['rec'],1)}.</figcaption></figure>
<h3>Three-year cash flow, base case (₹ crore)</h3>
{T(["", "Year 1", "Year 2", "Year 3", "Total"], cf_rows, num=(1, 2, 3, 4))}
<figure><div class="scroll">{cashflow_chart()}</div><figcaption>Base case. Dark bars: recurring benefit; light bars: one-off inventory cash; red bars: total cost. Payback: {b['payback']} including inventory cash; year 2 on recurring benefits alone.</figcaption></figure>
<h3>Scenarios</h3>
{T(["Measure", "Low", "Base", "High"], sc_rows, num=(1, 2, 3))}
<div class="callout"><b>What the low case tells us.</b> In the low case, recurring benefits only just cover their cost within three years, and the case rests on the inventory cash. That is why the roadmap has gates: if the pilot's measured gain is below the low case, the programme stops after one site and keeps the data foundation and the inventory work.</div>
<h3>What it means for leverage</h3>
<figure><div class="scroll">{leverage_chart()}</div><figcaption>Base case: about {b['gap_share']*100:.0f}% of the gap between FY26 leverage and CRISIL's trigger. AI supports deleveraging; it does not deliver it on its own.</figcaption></figure>
<div class="col"><h3>Assumptions to replace with UFlex data first</h3>
<ol><li>Scrap, off-spec and regrind recovery by line and grade (UC1).</li><li>kWh per kg by line and the energy split by plant (UC2).</li><li>Inventory by category, plant and age; forecast accuracy today (UC3).</li><li>Converting waste by process and job type (UC4).</li><li>Vendor and partner quotes for the build (all).</li></ol></div>
</section>""")

# 9 Roadmap
S.append(f"""<section><h2 id="roadmap"><span class="n">9</span>Roadmap and gates</h2>
<figure><div class="scroll">{gantt()}</div><figcaption>Bars show workstreams; diamonds are decision gates. Months from the start of the readiness sprint.</figcaption></figure>
{T(["Gate", "When", "Go if", "Stop or rethink if"], [
 ["1 · After the readiness sprint", "Week 2", "Plant data supports UC1 and UC2 on the chosen line; baselines can be captured; the business case still holds on UFlex data", "Data is not available or the re-based case falls below the low scenario; fix the data foundation first"],
 ["2 · After the lighthouse pilot", "Month 4", "Measured gain at or above the low case on net good output and kWh/kg; operators use the advisories; UC3 targets agreed by finance", "Gain below the low case after one retraining cycle; keep the data foundation and UC3, stop scaling UC1/UC2"],
 ["3 · Year-1 review", "Month 12", "Value ledger shows benefits tracking the base case at scaled sites; governance in place", "Benefits not tracking; re-plan the scale-out before committing year-2 spend"],
])}
<div class="col"><h3>The readiness sprint (two weeks)</h3>
<p>Days 1–3 <b>Immerse</b>: plant walk-through at the chosen film site, interviews, systems and data inventory. Days 4–7 <b>Audit</b>: data maturity across quality, maintenance, energy and production data; the PLUMB maturity instrument with UFlex's leaders. Days 8–11 <b>Prioritise</b>: re-score the use cases and rebuild the model on UFlex numbers. Days 12–14 <b>Decide</b>: an executive working session on the roadmap, business case and a scoped pilot. The sprint fee is credited against the pilot, and UFlex keeps every deliverable either way.</p></div>
</section>""")

# 10 Operating model and governance
S.append(f"""<section><h2 id="operating"><span class="n">10</span>Operating model and governance</h2>
{T(["Role", "Who", "Responsibility"], [
 ["Executive sponsor", "Vice Chairman and CEO (Anantshree Chaturvedi)", "Owns the ambition, chairs the gates, arbitrates between businesses"],
 ["Value owner", "Group CFO (Arun Kumar Sharma)", "Signs off baselines and the value ledger; owns UC3"],
 ["Use-case owners", "President – Technical and NPD, Packaging Films; Director – Global Operations; President – Flexible Packaging", "Own UC1/UC2 and UC4 outcomes at line and plant level"],
 ["AI and data team (8–12 people)", "Reporting to the Global CIO (to confirm the current holder)", "Data model, platform, MLOps, model development with partners, playbook packaging"],
 ["Plant champions", "One process engineer for each scaled site", "Adoption, operator feedback, local baselines"],
])}
<div class="col"><p>A small central team owns the data model, the platform and the playbook; plants own adoption and results. Partners supply vision, historian and planning engines; UFlex keeps the data model and process knowledge.</p>
<h3>Governance</h3>
<ul>
 <li><b>AI policy and inventory</b>: an approved AI policy, and an inventory of every AI system with its purpose, data, owner, risk tier and human-oversight rule, aligned with ISO/IEC 42001 and the NIST AI Risk Management Framework.</li>
 <li><b>Human oversight</b>: advisory mode by default; closed-loop control only after a documented performance record on a line, with an operator override.</li>
 <li><b>OT security</b>: network segmentation and vendor remote-access control (IEC 62443) before any model touches a line.</li>
 <li><b>Value</b>: baseline before go-live, a control line or period where possible, quarterly tracking in the value ledger, stop conditions written at approval.</li>
</ul></div>
<h3>Regulation that applies</h3>
{T(["Instrument", "Status and dates", "What it means here"], [
 ["India DPDP Act 2023 and Rules 2025", "Rules notified 13 Nov 2025; consent managers from 13 Nov 2026; core duties from 13 May 2027", "Low for plant AI; applies to HR, customer-contact and CRM data, so to any GenAI on those"],
 ["CERT-In Directions (2022)", "In force", "Report incidents within 6 hours; keep logs 180 days in India. Applies to connected IIoT and AI platforms"],
 ["MeitY India AI Governance Guidelines", "Released 5 Nov 2025; voluntary", "Use as the basis for UFlex's AI policy"],
 ["EU Machinery Regulation (EU) 2023/1230", "Applies from 20 Jan 2027", "Machines sold into the EU with machine-learning safety functions need a Notified Body; relevant to UC9"],
 ["EU AI Act, as amended by the Digital Omnibus", "High-risk obligations from 2 Dec 2027; AI in regulated products from 2 Aug 2028", "In-plant process, quality and maintenance AI is generally not high-risk"],
 ["EU Cyber Resilience Act", "Reporting from 11 Sep 2026; most duties from 11 Dec 2027", "Check applicability for connected machines sold into the EU"],
 ["India PWM (Amendment) Rules 2026; EU PPWR", "In force 31 Mar 2026; PPWR applies from 12 Aug 2026, targets from 2030", "Drives the traceability data in UC7"],
])}
</section>""")

# 11 Risks
S.append("""<section><h2 id="risks"><span class="n">11</span>Risks</h2>""" + T(["Risk", "Likelihood", "Mitigation"], [
 ["Plant data is incomplete or locked in OEM systems", "High", "Sprint audits data line by line; the pilot site is chosen for data availability; historian before models"],
 ["Benefits are confounded by price, mix and grade changes", "High", "Measure per kg and per grade against baselines; control lines or periods; CFO signs the attribution rule"],
 ["Operators do not trust advisories", "Medium", "Advisory mode, reasons shown, operator feedback logged; plant champions; recognition for adoption"],
 ["Pilot succeeds but does not scale across nine countries", "Medium", "Package the playbook (data model, models, routine) from day one; Director – Global Operations owns the scale plan"],
 ["OT cyber exposure from connecting lines", "Medium", "IEC 62443 segmentation and remote-access control before integration; CERT-In reporting ready"],
 ["Capex and cash competition with plant projects", "Medium", "Small, gated spend; UC3 cash release funds the programme; stop conditions"],
 ["Key-person risk in a lean central team", "Medium", "Partner for capacity; document the playbook; pair UFlex engineers with partners"],
]) + "</section>")

# 12 Next
S.append("""<section><h2 id="next"><span class="n">12</span>Next step</h2>
<div class="col"><p>We propose the two-week readiness sprint at one India film site, with a 45-minute working session beforehand with the CFO and the President – Technical and NPD, Packaging Films, to choose the site and confirm data access.</p>
<h3>What we would need from UFlex for the sprint</h3>
<ul><li>Access to one film site (plant walk-through, line and utilities engineers)</li><li>Line and quality data for the last 3 months; energy meter data where it exists</li><li>ERP extracts: inventory by item and plant, sales and purchase history for 24 months</li><li>The FY26 annual-report notes on other expenses, and current IT and OT architecture documents</li><li>Interviews with 8–10 leaders across films, packaging, finance, operations and IT</li></ul>
<p>The sprint ends with re-based numbers, a maturity score from UFlex's own people, and a scoped, priced pilot, or a clear recommendation not to proceed.</p></div></section>""")

# Appendix
S.append("""<section><h2 id="sources"><span class="n">A</span>Sources and notes</h2>
<div class="col"><p>All UFlex figures are from UFlex's own filings and presentations unless marked. ₹ crore figures are converted from the published ₹ lakh or ₹ million values without other adjustment. Peer results carry their evidence type. Open items: the commissioning date of the Noida recycling plant (30 April or 1 May 2026), India film capacity history (155,000 or 164,160 MTPA), FY25 restated EBITDA (₹1,818.8 or ₹1,834.3 crore), the current Global CIO, and the ERP in use.</p></div>
<ul class="src">
 <li>UFlex, Q4 FY26 investor presentation: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q4FY26_Presentation.pdf</li>
 <li>UFlex, consolidated results FY26 (31 Mar 2026): https://www.uflexltd.com/pdf/financials/Consolidated/UFLEX_NSEBSE_CONS_RESULTS_31MAR2026.pdf</li>
 <li>UFlex, consolidated results Q1 FY27 (30 Jun 2026): https://www.uflexltd.com/pdf/financials/Consolidated/UFLEX_NSEBSE_CONS_RESULTS_30JUN2026.pdf</li>
 <li>UFlex, Q1 FY27 presentation: https://www.uflexltd.com/pdf/QER/2026-27/UFlex_Q1FY27_Presentation.pdf</li>
 <li>UFlex, investor presentation 10 Sep 2026: https://www.uflexltd.com/pdf/IR/Investor_Presentation_10Sep_2026.pdf</li>
 <li>UFlex, Annual Report FY2025-26: https://www.uflexltd.com/pdf/financials/annual-reports/UFLEX-AR-2025-26.pdf</li>
 <li>UFlex, Annual Report FY2024-25: https://www.uflexltd.com/pdf/financials/annual-reports/UFLEX-AR-2024-25.pdf</li>
 <li>UFlex, BRSR FY2025-26: https://nsearchives.nseindia.com/corporate/DineshSharma_04072026193230_SIGNEDUFLEXNSEBSEREG36BRSR20252026.pdf</li>
 <li>UFlex, Q2 FY26 call transcript: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q2FY26_Transcript.pdf</li>
 <li>CRISIL rating rationale, UFlex, August 2026 (via crisil.com)</li>
 <li>Oracle case study (undated): https://www.casestudies.com/company/oracle/case-study/uflex-cuts-sales-time-by-half-and-converts-40-more-leads-with-oracle-sales-cloud</li>
 <li>Polyplex, Q4 FY26 investor presentation, 27 May 2026: https://nsearchives.nseindia.com/corporate/POLYPLEX_27052026174118_PCL_Investor_Presentation_Q4_2025-26_signed.pdf</li>
 <li>Cosmo First, Q4 FY26 call transcript, 21 May 2026: https://nsearchives.nseindia.com/corporate/COSMOFILMS_28052026143240_Intimation_Transcript.pdf</li>
 <li>World Economic Forum, Global Lighthouse Network, 15 Jan 2026: https://www.weforum.org/press/2026/01/global-lighthouse-network-recognizes-23-new-sites-launches-ai-platform-for-industrial-transformation/</li>
 <li>ACG, Shirwal Lighthouse: https://www.acg-world.com/news/acg-shirwal-facility-joins-world-economic-forum-global-lighthouse-network</li>
 <li>Mondi, "Operationalizing advanced industrial data projects" (conference deck, 2022)</li>
 <li>McKinsey, The continuing evolution of the Global Lighthouse Network: https://www.mckinsey.com/capabilities/operations/our-insights/the-continuing-evolution-of-the-global-lighthouse-network</li>
 <li>Deloitte, Predictive Maintenance position paper: https://www.deloitte.com/content/dam/assets-zone2/de/de/docs/about/2024/Deloitte_Predictive-Maintenance_PositionPaper.pdf</li>
 <li>EU Packaging and Packaging Waste Regulation (EU) 2025/40: https://eur-lex.europa.eu/eli/reg/2025/40/oj/eng</li>
 <li>EU Machinery Regulation overview (UL): https://www.ul.com/resources/navigating-new-eu-machinery-regulation-eu-20231230</li>
 <li>DPDP Rules 2025 (JSA summary): https://www.jsalaw.com/wp-content/uploads/2025/11/JSA-Prism-InfoTech-November-2025-DPDP-Rules.Final_.pdf</li>
 <li>MeitY AI Governance Guidelines: https://indianinfrastructure.com/2025/11/07/meity-unveils-india-ai-governance-guidelines-under-indiaai-mission/</li>
 <li>Esko and GlobalVision, Verify Comply launch, 18 Oct 2026: https://www.esko.com/en/company/news/esko-and-globalvision-bring-ai-powered-compliance-intelligence-to-packaging-workflows-with-verify-comply</li>
</ul>
<footer>PLUMB Advisory · Prepared from public information only; not reviewed by UFlex. Figures are illustrative until re-based on UFlex data in the readiness sprint.</footer>
</section></div>""")

open(OUT, "w").write("\n".join(S))
print(OUT, len("\n".join(S)))
