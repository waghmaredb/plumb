"""UFlex AI strategy v2 — rewritten after the CEO/technical and CFO red-team reviews."""
import html, json
from openpyxl import load_workbook

RUN = "/home/claude/plumb/runs/uflex/2026-11-03"
SCR = "/tmp/claude-0/-home-claude/598a1fc4-71d0-5dc6-b611-3434cc77d612/scratchpad"
OUT = f"{RUN}/uflex-ai-strategy.html"
E = html.escape

def read(path):
    wb = load_workbook(path, data_only=True)
    u, v = wb["Use cases"], wb["Five years"]
    yr = lambda r: [v[f"{c}{r}"].value for c in "CDEFG"]
    return {
        "uc1s": u["B5"].value, "uc1e": u["B6"].value, "uc2": u["B7"].value, "uc3": u["B8"].value, "uc6": u["B9"].value,
        "uc4": u["B10"].value, "wc": u["B11"].value, "wc_int": u["B12"].value, "full": u["B14"].value,
        "rec": yr(9), "ramp": yr(10), "cost": yr(11), "net": yr(12), "cum": yr(13), "wcy": yr(15),
        "npv": v["B19"].value, "npv_wc": v["B20"].value, "y5ben": v["B21"].value, "y5run": v["B22"].value, "y5net": v["B23"].value,
        "roc": v["B25"].value, "payback": v["B26"].value, "be": v["B27"].value, "be_scrap": v["B28"].value, "be_energy": v["B29"].value,
        "cost_tot": sum(yr(11)), "rec_tot": sum(yr(9)),
    }

LOW, BASE, HIGH = (read(f"{SCR}/v2s{i}.xlsx") for i in (1, 2, 3))
json.dump({"low": LOW, "base": BASE, "high": HIGH}, open(f"{RUN}/model-results-v2.json", "w"), indent=1, default=str)
b, lo, hi = BASE, LOW, HIGH
cr = lambda x, d=0: (f"−₹{-x:,.{d}f} cr" if x < 0 else f"₹{x:,.{d}f} cr")

# reuse the v1 page CSS and table helper
_h = open(f"{SCR}/helpers.py").read()
_start = _h.index('CSS = """'); _end = _h.index('def T(')
exec(_h[_start:_end])
def T(headers, rows, num=()):
    h = "".join(f'<th class="{"num" if i in num else ""}">{x}</th>' for i, x in enumerate(headers))
    body = "".join("<tr>" + "".join(f'<td class="{"num" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

# ------------------------------------------------------------------ charts
def value_chart():
    names = ["UC1 Film-line stability and yield", "UC3 Recycling quality and evidence", "UC6 Gravure make-ready and colour", "UC2 Slitting, deckle and scheduling"]
    key = lambda d: [d["uc1s"] + d["uc1e"], d["uc3"], d["uc6"], d["uc2"]]
    L_, B_, H_ = key(lo), key(b), key(hi)
    W, H, L, R, T0, rowh = 760, 290, 280, 70, 24, 56
    xmax = 35.0
    sx = lambda v: L + (W - L - R) * v / xmax
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Recurring EBITDA at full scale by use case, low, base and high, ₹ crore a year">']
    for t in range(0, 36, 5):
        x = sx(t); o.append(f'<line x1="{x:.1f}" y1="{T0-6}" x2="{x:.1f}" y2="{T0+rowh*4}" class="grid"/><text x="{x:.1f}" y="{T0+rowh*4+18}" class="tick" text-anchor="middle">{t}</text>')
    for i, n in enumerate(names):
        y = T0 + i * rowh + rowh / 2
        o.append(f'<text x="{L-12}" y="{y+4:.1f}" class="lab" text-anchor="end">{E(n)}</text>')
        o.append(f'<rect x="{sx(0):.1f}" y="{y-11:.1f}" width="{sx(B_[i])-sx(0):.1f}" height="22" class="bar"/>')
        o.append(f'<line x1="{sx(L_[i]):.1f}" y1="{y:.1f}" x2="{sx(H_[i]):.1f}" y2="{y:.1f}" class="range"/><line x1="{sx(L_[i]):.1f}" y1="{y-7:.1f}" x2="{sx(L_[i]):.1f}" y2="{y+7:.1f}" class="range"/><line x1="{sx(H_[i]):.1f}" y1="{y-7:.1f}" x2="{sx(H_[i]):.1f}" y2="{y+7:.1f}" class="range"/>')
        o.append(f'<text x="{sx(H_[i])+8:.1f}" y="{y+4:.1f}" class="val">{B_[i]:.1f}</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-4}" class="tick" text-anchor="middle">₹ crore a year at full scale · bar = base, whiskers = low to high</text></svg>')
    return "".join(o)

def five_year_chart():
    W, H, L, R, T0, B0 = 780, 320, 60, 20, 20, 54
    ymin, ymax = -60, 50
    sy = lambda v: T0 + (H - T0 - B0) * (ymax - v) / (ymax - ymin)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Base case five years: EBITDA benefits against programme cost, ₹ crore">']
    for t in range(-60, 51, 20):
        y = sy(t); o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/><text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    gw = (W - L - R) / 5
    pts = []
    for i in range(5):
        cx = L + gw * i + gw / 2; bw = 34
        rec, ramp, cost, net = b["rec"][i], b["ramp"][i], b["cost"][i], b["net"][i]
        x1 = cx - bw - 4
        o.append(f'<rect x="{x1:.1f}" y="{sy(rec):.1f}" width="{bw}" height="{sy(0)-sy(rec):.1f}" class="bar"/>')
        if ramp > 0:
            o.append(f'<rect x="{x1:.1f}" y="{sy(rec+ramp):.1f}" width="{bw}" height="{sy(rec)-sy(rec+ramp):.1f}" class="bar2"/>')
        o.append(f'<text x="{x1+bw/2:.1f}" y="{sy(rec+ramp)-6:.1f}" class="val" text-anchor="middle">{rec+ramp:.0f}</text>')
        x2 = cx + 4
        o.append(f'<rect x="{x2:.1f}" y="{sy(0):.1f}" width="{bw}" height="{sy(-cost)-sy(0):.1f}" class="cost"/>')
        o.append(f'<text x="{x2+bw/2:.1f}" y="{sy(-cost)+14:.1f}" class="val" text-anchor="middle">−{cost:.0f}</text>')
        o.append(f'<text x="{cx:.1f}" y="{H-30}" class="lab" text-anchor="middle">Year {i+1}</text><text x="{cx:.1f}" y="{H-14}" class="tick" text-anchor="middle">net {("−" if net < 0 else "+")}{abs(net):.0f}</text>')
    o.append("</svg>")
    return "".join(o)

def matrix_chart():
    pts = [("UC1", "Film-line stability", 3.8, b["uc1s"] + b["uc1e"]), ("UC3", "Recycling quality", 3.9, b["uc3"]),
           ("UC6", "Gravure make-ready", 3.4, b["uc6"]), ("UC2", "Slitting and scheduling", 3.6, b["uc2"])]
    later = [("Metalliser and coating", "W2"), ("Chip-plant control", "W2"), ("Aseptic quality and filling uptime", "W2"), ("AI in UFlex machines", "W2"), ("Plant copilot", "W2")]
    W, H, L, R, T0, B0 = 760, 360, 60, 30, 20, 50
    ymax = 20
    sx = lambda f: L + (W - L - R) * (f - 1.5) / 3.5
    sy = lambda v: T0 + (H - T0 - B0) * (ymax - v) / ymax
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Use-case prioritisation: base value at full scale against feasibility">']
    o.append(f'<rect x="{sx(3.25):.1f}" y="{sy(ymax):.1f}" width="{sx(5)-sx(3.25):.1f}" height="{sy(0)-sy(ymax):.1f}" class="zone"/><text x="{sx(4.98):.1f}" y="{sy(ymax)+16:.1f}" class="tick" text-anchor="end">Wave 1 zone</text>')
    for t in range(0, 21, 5):
        y = sy(t); o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/><text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    o.append(f'<text x="{sx(2):.1f}" y="{H-30}" class="tick" text-anchor="middle">harder</text><text x="{sx(5):.1f}" y="{H-30}" class="tick" text-anchor="middle">easier</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-10}" class="tick" text-anchor="middle">Feasibility (data likely available, integration effort, time to first value) — re-scored in the sprint</text>')
    o.append(f'<text x="14" y="{(T0+H-B0)/2:.1f}" class="tick" text-anchor="middle" transform="rotate(-90 14 {(T0+H-B0)/2:.1f})">Base value at full scale, ₹ cr a year</text>')
    for uc, lab, f, v in pts:
        x, y = sx(f), sy(v); anchor, dx = ("end", -12) if f > 4.1 else ("start", 12)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" class="pt"/><text x="{x+dx:.1f}" y="{y+4:.1f}" class="lab" text-anchor="{anchor}">{uc} {E(lab)}</text>')
    o.append("</svg>")
    return "".join(o)

def ref_arch():
    W, H = 900, 580
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Reference architecture from plant and enterprise sources through plant edge, data fabric and AI services to applications">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    def box(x, y, w, h, title, items):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="lay"/><text x="{x+12}" y="{y+20}" class="bt">{E(title)}</text>')
        for i, it in enumerate(items):
            o.append(f'<text x="{x+12}" y="{y+40+i*16}" class="bi">{E(it)}</text>')
    box(60, 456, 380, 110, "Plant sources", ["Film lines: extrusion, MDO/TDO, winders (OEM controls)", "Metallisers, coaters, slitters; chip plant DCS", "Inspection systems, gauges, energy meters", "Recycling lines; gravure presses, ink kitchen"])
    box(460, 456, 380, 110, "Enterprise sources", ["ERP (to confirm in the sprint)", "Quality and lab records, maintenance (CMMS)", "Planning, procurement, orders; EPR records", "Specifications, recipes, SOPs, artwork"])
    box(60, 354, 780, 78, "Plant edge (each site, on UFlex infrastructure)", ["Historian and time-series buffer · edge compute for vision and second-by-second models · keeps working when the WAN drops",
        "Reuses OEM and inspection-vendor data feeds already paid for; advisory mode first"])
    box(60, 252, 780, 78, "Governed data fabric (group)", ["One data model: site → line → grade → order → roll, with genealogy from resin to finished pack · data owners and quality rules",
        "Cross-border transfers reviewed per country; Russia excluded pending sanctions review · lineage for model datasets"])
    box(60, 150, 780, 78, "AI services", ["Break and defect cause models · scheduling and trim optimisation · recycling quality · demand and inventory models",
        "Language models with retrieval over SOPs (later) · MLOps: registry, monitoring, drift, retraining"])
    box(60, 48, 780, 78, "Applications and decisions", ["Shift-lead advisories inside existing line screens · scheduling and slitting plans · recycled-content evidence for customers",
        "S&OP and buyer workbench · make-ready settings · value ledger tracking every use case against its baseline"])
    o.append('<rect x="856" y="48" width="34" height="518" rx="4" class="cross"/><text x="878" y="307" class="bt" text-anchor="middle" transform="rotate(-90 878 307)">Security (IEC 62443) · AI governance · CERT-In, DPDP</text>')
    for y in (434, 332, 230, 128):
        o.append(f'<line x1="450" y1="{y+18}" x2="450" y2="{y-2}" class="flow" marker-end="url(#ah)"/>')
    o.append('<text x="20" y="306" class="tick" text-anchor="middle" transform="rotate(-90 20 306)">Data flows up; decisions flow back to the line</text></svg>')
    return "".join(o)

def flow(steps, label):
    W, n = 900, len(steps); bw = (W - 20 * (n - 1)) / n; mid = f"a{abs(hash(label)) % 99999}"
    o = [f'<svg viewBox="0 0 {W} 112" role="img" aria-label="{E(label)}"><defs><marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    for i, (t, sub) in enumerate(steps):
        x = i * (bw + 20)
        o.append(f'<rect x="{x:.1f}" y="6" width="{bw:.1f}" height="100" rx="4" class="{"lay2" if i in (0, n-1) else "lay"}"/><text x="{x+10:.1f}" y="28" class="bt">{E(t)}</text>')
        line, ly, maxc = "", 48, int(bw / 7.0)
        for w in sub.split():
            if len(line) + len(w) + 1 > maxc:
                o.append(f'<text x="{x+10:.1f}" y="{ly}" class="bi">{E(line)}</text>'); ly += 15; line = w
            else:
                line = (line + " " + w).strip()
        o.append(f'<text x="{x+10:.1f}" y="{ly}" class="bi">{E(line)}</text>')
        if i < n - 1:
            o.append(f'<line x1="{x+bw+2:.1f}" y1="56" x2="{x+bw+18:.1f}" y2="56" class="flow" marker-end="url(#{mid})"/>')
    o.append("</svg>")
    return "".join(o)

def gantt():
    rows = [("Readiness sprint, incl. inventory of AI already in use", 0, 0.5, "s"), ("Gate 1: choose the line and problem; data access agreed", 0.5, 0, "g"),
            ("Pilot on one UFlex-chosen line (6 months, control line)", 0.6, 7, "p"), ("UC5 planning and inventory (enterprise)", 0.6, 5.5, "p"),
            ("UC3 recycling quality and evidence (Noida)", 0.6, 6, "p"), ("UC4 ramp-up instrumentation (Dharwad BOPP, Egypt aseptic)", 1.5, 9, "p"),
            ("Gate 2: pilot measured against break-even", 7, 0, "g"), ("Scale UC1 to India film sites; UC2 slitting and scheduling", 7.2, 15, "c"),
            ("UC6 gravure make-ready (Noida, Jammu)", 9, 15, "c"), ("Gate 3: year-1 value review; overseas plan", 15, 0, "g"), ("Overseas film sites (excl. Russia pending review)", 15.2, 30, "c")]
    W, L, T0, rh = 900, 420, 34, 30; H = T0 + len(rows) * rh + 12; months = 30
    sx = lambda m: L + (W - L - 10) * m / months
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Roadmap over 30 months with decision gates">']
    for m in range(0, 31, 6):
        x = sx(m); o.append(f'<line x1="{x:.1f}" y1="{T0-8}" x2="{x:.1f}" y2="{T0+len(rows)*rh}" class="grid"/><text x="{x:.1f}" y="{T0-12}" class="tick" text-anchor="middle">M{m}</text>')
    for i, (lab, a, z, k) in enumerate(rows):
        y = T0 + i * rh
        o.append(f'<text x="{L-10}" y="{y+rh/2+4:.1f}" class="lab" text-anchor="end">{E(lab)}</text>')
        if k == "g":
            cx, cy = sx(a), y + rh / 2; o.append(f'<path d="M{cx:.1f},{cy-9:.1f} L{cx+9:.1f},{cy:.1f} L{cx:.1f},{cy+9:.1f} L{cx-9:.1f},{cy:.1f} z" class="gate"/>')
        else:
            o.append(f'<rect x="{sx(a):.1f}" y="{y+7:.1f}" width="{max(sx(z)-sx(a), 4):.1f}" height="{rh-14}" rx="2" class="{ {"s": "bar2", "p": "bar", "c": "bar3"}[k] }"/>')
    o.append("</svg>")
    return "".join(o)

def uc_card(tag, title, owner, problem, does, data, kpi, value, cost, evidence, risk, flowsvg):
    return f"""<article class="uc"><div class="tag">{tag}</div><h3>{title}</h3>
<dl class="facts">
 <div><dt>The problem</dt><dd>{problem}</dd></div><div><dt>What AI adds</dt><dd>{does}</dd></div><div><dt>Data needed</dt><dd>{data}</dd></div>
 <div><dt>KPIs and baseline</dt><dd>{kpi}</dd></div><div><dt>Value logic (base)</dt><dd>{value}</dd></div><div><dt>Indicative cost</dt><dd>{cost}</dd></div>
 <div><dt>Evidence it works</dt><dd>{evidence}</dd></div><div><dt>Main risks</dt><dd>{risk}</dd></div><div><dt>Natural owner (to be agreed)</dt><dd>{owner}</dd></div>
</dl><figure><div class="scroll">{flowsvg}</div><figcaption>How it works: data in, model, decision, action, measurement.</figcaption></figure></article>"""

# ------------------------------------------------------------------ page
S = []
S.append(f"""<title>UFlex AI Strategy</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="cover">
 <div class="eyebrow">UFlex Limited · AI strategy · outside-in · version 2</div>
 <h1>Faster ramp-ups, cheaper kilograms and recycled-content claims that can be proved</h1>
 <p class="lede">An AI strategy for UFlex's growth phase, built from public disclosures to 3 November 2026: where AI pays across new capacity, film lines and recycling, what to build first, how it fits together, and the measured result that should decide whether it scales.</p>
 <div class="meta"><span><b>Prepared by</b> PLUMB Advisory</span><span><b>Date</b> November 2026</span><span><b>Basis</b> UFlex annual reports FY25–FY26, results and investor presentations to Q1 FY27, public industry sources</span><span class="status">For discussion · not validated with UFlex data</span></div>
 <nav class="toc" aria-label="Contents">
  <a href="#summary">1 · Summary</a><a href="#uflex">2 · UFlex today</a><a href="#industry">3 · The industry</a><a href="#ai-today">4 · AI at UFlex today</a>
  <a href="#strategy">5 · The strategy</a><a href="#usecases">6 · Use cases</a><a href="#architecture">7 · Architecture</a><a href="#roi">8 · Value and ROI</a>
  <a href="#roadmap">9 · Roadmap and gates</a><a href="#operating">10 · Operating model and governance</a><a href="#risks">11 · Risks</a><a href="#next">12 · Next step</a>
 </nav>
</header>""")

S.append(f"""<section><h2 id="summary"><span class="n">1</span>Summary</h2>
<div class="col">
<p>UFlex is in a growth phase. It is commissioning Egypt aseptic and building a 54,000-tonne BOPP line at Dharwad; Mexico WPP and the Noida recycling plant came on stream in 2026; and its stated focus is <span class="q">"Focused investments in aseptic, WPP and recycling to accelerate growth"</span>. Film lines ran at 85.4% utilisation in Q1 FY27, with an EBITDA margin of 17.0%, though management expects some normalisation as prices settle.</p>
<p>AI can help in three ways in this phase: bring new capacity to target output faster and right first time; take scrap, breaks and energy out of every kilogram on existing lines; and turn UFlex's unusual control of the chain, from PET chips to film to converting to recycling, into recycled-content evidence that brand owners and regulators can check.</p>
<p>We recommend six use cases, proved on one line that UFlex chooses before anything scales, and one data foundation built once. The case is deliberately conservative, and on those conservative rates a nine-country programme does not yet pay for itself. That is the point of the pilot: it measures UFlex's real rates against a clear break-even line before the larger spend is committed.</p>
</div>
<div class="kpis">
 <div class="kpi"><div class="v">{cr(b['full'])}</div><div class="l">recurring EBITDA a year at full scale, base case</div><div class="r">range {cr(lo['full'])} to {cr(hi['full'])}</div></div>
 <div class="kpi"><div class="v">{cr(b['uc4'])} + {cr(b['wc'])}</div><div class="l">one-off: faster ramp-up of new capacity, and the AI share of an inventory release</div><div class="r">kept separate from recurring value</div></div>
 <div class="kpi"><div class="v">{b['be_scrap']*100:.2f}%</div><div class="l">of film production removed as scrap: the measured result at which the full programme breaks even</div><div class="r">with {b['be_energy']*100:.1f}% energy saved per good kg</div></div>
</div>
<div class="col">
<h3>What we recommend</h3>
<ol class="recs">
 <li><b>Start by listing what UFlex already runs.</b> Line suppliers' digital services, installed inspection systems, Ceruflex remote monitoring and the AI segregation in recycling, so nothing is paid for twice.</li>
 <li><b>Prove value on one line and one problem that UFlex chooses.</b> For example, film breaks on a BOPP line or restart scrap on a BOPET line, measured for six months against a control line.</li>
 <li><b>Run three enterprise-level use cases in parallel.</b> These are recycling quality and recycled-content evidence at Noida, instrumentation of the Dharwad and Egypt ramp-ups, and planning and inventory. None depends on the line pilot.</li>
 <li><b>Scale only on evidence.</b> Scale the film-line work to other sites only if the pilot clears the break-even line. Overseas sites follow India, and Russia waits for a sanctions and data-transfer review.</li>
 <li><b>Build the data foundation once, with genealogy from resin to finished pack.</b> It serves every use case and the recycled-content claims customers will ask for.</li>
</ol></div></section>""")

S.append(f"""<section><h2 id="uflex"><span class="n">2</span>UFlex today</h2>
<div class="col"><p>UFlex describes itself as <span class="q">"India's largest flexible packaging materials and Solutions Company"</span>. In FY26 it reported total income of ₹15,513 crore, EBITDA of ₹1,983.6 crore (12.8%) and profit after tax of ₹317.1 crore. In Q1 FY27 revenue from operations rose 37.6% to ₹5,366 crore and EBITDA margin reached 17.0%. Films are 58.6% of FY26 revenue, from 636,160 tonnes a year of capacity in nine countries.</p></div>
{T(["Business", "FY26 share of revenue", "Scale (UFlex disclosures)"], [
 ["Packaging films and PET chips", "58.6%", "BOPET 401,800, BOPP 150,200, CPP 84,160 MTPA; metallised 238,600; AlOx 14,200; UHB 13,200. 492,779 t produced in FY26; 85.4% utilisation in Q1 FY27. Chip plants at Panipat and in Egypt."],
 ["Packaging: flexible, aseptic liquid, holography", "32.7%", "Flexible packaging about 100,000 MTPA (Noida, Jammu); aseptic 12 bn packs a year at Sanand, Egypt plant in trials, target 24 bn by FY2027; holography 20,600 MTPA"],
 ["Engineering: packaging machines, printing cylinders", "2.9%", "500 machines and 108,000 cylinders a year; Ceruflex 500 gravure press with remote monitoring"],
 ["Others: inks, adhesives, coatings", "5.1%", "69,730 MTPA"],
 ["Recycling (within the businesses above)", "—", "rPET chips 79,020 MTPA and rMLP granules 34,897 MTPA; management cites ₹850 crore-plus revenue potential"],
])}
<h3>The cost lines AI can move (FY26, consolidated)</h3>
{T(["Line", "₹ crore", "AI levers"], [
 ["Cost of materials consumed", "8,877.0", "Scrap, breaks, restart and changeover loss, trim, converting waste (UC1, UC2, UC6)"],
 ["Power and fuel", "739.3", "Energy per good kilogram on film lines (UC1); chip-plant and utilities control (wave 2)"],
 ["Other expenses", "2,171.4", "Maintenance and spares (wave 2, once repair and maintenance spend is known)"],
 ["Inventories, 31 March 2026", "2,408.3", "About 100 days of cost of goods sold; planning and inventory (UC5)"],
], num=(1,))}
<h3>What makes UFlex distinctive</h3>
<div class="col"><ol>
 <li><b>It controls the chain from resin to pack.</b> PET chips, film, metallising and coating, inks and adhesives, cylinders, converting and recycling sit under one roof. So the evidence for a recycled-content or recyclability claim can be assembled inside one company, which few competitors can offer Nestlé, PepsiCo or Mondelez.</li>
 <li><b>It is adding capacity now.</b> New lines are the cheapest place to build in data and AI, because instrumentation goes in during commissioning, not as a retrofit.</li>
 <li><b>A film playbook can be repeated across nine countries.</b> A result proven on one line can be replicated, which is where AI economics improve.</li>
 <li><b>It builds machines.</b> Plant learning can become product features, and machine sales into the EU will need to meet the Machinery Regulation from January 2027.</li>
 <li><b>Its recycling capacity is built and running.</b> Noida was commissioned in 2026, alongside sites in Mexico, Egypt, Poland, Jammu and Malanpur.</li>
</ol></div></section>""")

S.append(f"""<section><h2 id="industry"><span class="n">3</span>The industry</h2>
<div class="col">
<p><b>Film prices follow capacity.</b> Peers describe raw materials as largely passed through, with prices set by supply and demand, and expect volatile BOPET and BOPP margins as new lines arrive in India and China. The 2026 spike in film prices followed the West Asia conflict; UFlex itself expects some normalisation. Cost per kilogram and first-time-right production are what a producer controls through the cycle.</p>
<p><b>Feedstock is more volatile.</b> Indian PTA rose about 31% within days in March 2026 and polypropylene list prices rose by a cumulative ₹23 a kilogram, so planning and buying decisions carry more value than before.</p>
<p><b>Recycled content is becoming a legal and commercial requirement.</b> Under India's Plastic Waste Management (Amendment) Rules 2026, flexible packaging must reach 10% recycled content, rising to 20% by 2027-28, and multilayer packaging 5%, rising to 10%. QR or barcode labelling has applied since July 2025, and shortfalls attract ₹5,000 a tonne in environmental compensation. The EU Packaging and Packaging Waste Regulation has applied since 12 August 2026, with recyclability grades and recycled-content targets binding from 2030, averaged per plant per year. Both require evidence by plant and format.</p>
</div>
<h3>What peers show</h3>
{T(["Company", "AI evidence", "Result", "Evidence type"], [
 ["Kunlene Film Industries, Suzhou (BOPP films)", "WEF Lighthouse, Jan 2026", "Defects −31%, R&amp;D lead time −45%, minimum order size −83%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["ACG Packaging Materials, Shirwal (India)", "WEF Lighthouse, Jan 2026: machine learning, generative AI, IIoT, digital twins", "Lead time −40%, defects −71%, energy −31%, on-time-in-full +34%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["Mondi, Hilm (Austria)", "Predictive quality 24 hours ahead, with operator recommendations", "Rework and waste −50% versus 2018", '<span class="lbl">Company-reported</span>'],
 ["Amcor", "Vision for seal defects, predictive maintenance, changeover root-cause analysis", "No figures disclosed", '<span class="lbl">Company, qualitative</span>'],
 ["Indian film peers (Polyplex, Cosmo First, others)", "Describe digitalisation", "No quantified AI outcomes disclosed", '<span class="lbl">Annual reports</span>'],
])}
<div class="col"><p>No Indian film producer we reviewed discloses a measured AI programme, so a measured one would stand out with customers and investors. We treat the Lighthouse results as upper bounds: they are whole-site programmes run over several years.</p></div></section>""")

S.append(f"""<section><h2 id="ai-today"><span class="n">4</span>AI at UFlex today</h2>
<div class="col"><p>UFlex's own reports already describe AI across several businesses. We list what is public. We do not score maturity from the outside: a fair assessment needs UFlex's people, systems and data, and it is part of the sprint.</p></div>
{T(["Where", "What UFlex has reported", "Source"], [
 ["Engineering", 'Machines that <span class="q">"feature embedded AI for predictive maintenance and realtime monitoring"</span>; strategy to <span class="q">"Intensify deployment of AI, predictive analytics, and real-time diagnostics to enhance uptime"</span>', "Annual Report FY25, pp. 44, 46"],
 ["Holography", '<span class="q">"embedding AI-based quality control"</span> and <span class="q">"AI-driven track-and-trace systems"</span>', "Annual Report FY25, p. 38"],
 ["Packaging films", '<span class="q">"AI-led product development for greater efficiency and precision"</span>', "Annual Report FY25, p. 22"],
 ["Recycling", '<span class="q">"adding advanced recycling technologies, AI-enabled segregation systems, and traceability solutions"</span>', "Annual Report FY26, p. 10"],
 ["People", 'Leadership programme <span class="q">"AIM-AIA (AI in Manufacturing)"</span>', "Annual Report FY26, p. 35"],
 ["Gravure presses", 'Ceruflex 500 with <span class="q">"remote monitoring via mobile and tablet connectivity"</span>', "Annual Report FY26, pp. 28–29"],
])}
<h3>What we would assess together in the sprint</h3>
{T(["Area", "Questions"], [
 ["Strategy and value", "Which AI initiatives are live, who owns them, and are their benefits tracked against a baseline?"],
 ["Data and platforms", "Which plants have historians; what line, quality and energy data exists and at what resolution; what the ERP and OEM systems hold"],
 ["Existing tools", "Which line-supplier digital services and inspection systems are installed and paid for, and what they already do"],
 ["People and delivery", "In-house data and automation skills, partners, and how pilots reach production today"],
 ["Governance and security", "AI and OT security policies, remote-access control, and data-transfer rules across the nine countries"],
])}</section>""")

S.append("""<section><h2 id="strategy"><span class="n">5</span>The strategy</h2>
<div class="col"><p><b>Ambition.</b> Use AI to bring UFlex's new capacity to target output faster and right first time, to lower the cost of every kilogram on existing lines, and to make every recycled-content and recyclability claim provable, proving each step in rupees before it scales.</p>
<h3>Four strategic choices</h3></div>""" + T(["Choice", "What it means", "Why, for UFlex"], [
 ["Build AI into new capacity", "Instrument Dharwad BOPP and Egypt aseptic from commissioning; first-time-right grades and faster ramp-up.", "Management guides about ₹500 crore of EBITDA from four projects at decent utilisation; each month earlier matters."],
 ["Make compliance evidence a commercial asset", "Genealogy from resin to pack and recycling quality data, offered to brand owners.", "PWM 2026, QR labelling and EU PPWR require it, and UFlex controls more of the chain than its peers."],
 ["Take loss out of every kilogram", "Breaks, gels, restart and changeover scrap, trim and energy per good kilogram.", "Film prices follow capacity; cost per kilogram is what UFlex controls through the cycle."],
 ["Prove once, then replicate", "One line, one problem, six months, a control line; then a packaged playbook for other sites.", "Replication across nine countries is where the economics improve, if the first result is real."],
]) + """<div class="col"><h3>Guiding principles</h3><ul>
 <li><b>Start from what is installed.</b> Use OEM and inspection-vendor data feeds already paid for; add only what is missing.</li>
 <li><b>Start with the data model.</b> One model of site, line, grade, order and roll serves every use case and every compliance claim.</li>
 <li><b>Advise first, automate later.</b> Thickness control and defect classification are already automated on modern lines; AI adds cause-finding and advice before it earns any closed-loop role.</li>
 <li><b>Data stays on UFlex-controlled infrastructure.</b> Cross-border transfers are reviewed country by country; the Russia site is excluded until a sanctions and data-transfer review clears it.</li>
 <li><b>Measure everything.</b> Each use case has a baseline, a control where possible, a finance-signed attribution rule and a stop condition.</li>
</ul></div></section>""")

S.append(f"""<section><h2 id="usecases"><span class="n">6</span>Use cases</h2>
<div class="col"><p>Six use cases form the programme. Four produce recurring EBITDA and carry the business case; two produce one-off value that we report separately. Five more are wave 2, sized in the sprint once UFlex's data is available.</p></div>
<figure><div class="scroll">{matrix_chart()}</div><figcaption>Base value at full scale for the four recurring use cases. UC4 (ramp-up) and UC5 (inventory) are one-off and shown in section 8. Wave 2 use cases are listed after the use-case cards. Feasibility is our outside-in judgement, re-scored in the sprint.</figcaption></figure>""")

S.append(uc_card("UC1 · Recurring · Pilot", "Film-line stability and yield",
 "Head of technical and film operations, with the pilot plant's head",
 "On modern film lines, thickness control and defect classification are already automated. The loss sits elsewhere: film breaks at the MDO and TDO, gels and black specks from filtration and melt-pump pressure, restart scrap after breaks, changeover scrap, and winding defects such as gauge bands, wrinkles and telescoping.",
 "Links each break or defect to its upstream cause across time lags and roll positions; warns shift leads before a break; recommends changeover sequences and settings that cut restart and transition scrap; tracks energy per good kilogram.",
 "Line control tags at 1-second resolution, scanner defect events, break logs, filtration and melt-pump data, roll and grade records, energy meters. Most of this already exists in OEM and inspection systems.",
 "Breaks per 1,000 running hours; scrap and off-spec kg per tonne; restart and changeover loss; kWh per good kg. Baseline and control line agreed with finance before go-live.",
 f"Film production 492,779 t × 0.6% avoidable scrap removed × ₹110/kg × 30% value lost after reclaim or sale as seconds, plus 2% energy per good kg on the film-line share of power and fuel = <b>{cr(b['uc1s']+b['uc1e'],1)} a year</b> at full scale (range {cr(lo['uc1s']+lo['uc1e'],1)} to {cr(hi['uc1s']+hi['uc1e'],1)}).",
 "₹3.5 crore at the pilot site; about ₹1.5 crore a further site, varying by OEM and line vintage.",
 "Kunlene (BOPP) defects −31% and ACG defects −71% (WEF Lighthouses); Mondi Hilm rework and waste −50%.",
 "Data locked in OEM systems; operator trust; lines from different OEMs and vintages need separate integration.",
 flow([("Sense", "Line tags, break logs, scanner events, roll IDs"), ("Cause model", "Links breaks and defects to upstream conditions"), ("Advise", "Early warning and settings for shift leads"), ("Act", "Shift lead accepts or rejects; reason logged"), ("Measure", "Breaks, scrap kg/t, kWh per good kg vs control")], "UC1 data flow")))
S.append(uc_card("UC2 · Recurring · After the pilot", "Slitting, deckle and line scheduling",
 "Heads of planning and slitting at the film sites",
 "Turning master rolls into slit rolls, planning trim across orders, and sequencing grades and thicknesses on each line decide much of the yield outside the line itself.",
 "Optimises deckle and slitting plans across open orders, and campaigns grades and thicknesses to cut changeover scrap and time, with machine learning to predict run rates and changeover losses.",
 "Order book, slitter configurations, roll inventory, changeover history, line run rates.",
 "Trim loss %; changeover scrap and time; on-time-in-full.",
 f"Film production × 0.2% trim and changeover scrap removed × ₹110/kg × 30% value lost = <b>{cr(b['uc2'],1)} a year</b> at full scale (range {cr(lo['uc2'],1)} to {cr(hi['uc2'],1)}). On-time delivery gains are not counted.",
 "₹5 crore over three years.", "Klöckner Pentaplast reports −3% waste from trim optimisation (vendor case study).",
 "Planner adoption; order-book data quality.",
 flow([("Data", "Orders, slitter set-ups, roll stock, run rates"), ("Optimise", "Deckle, slitting and grade sequence"), ("Plan", "Proposed plan for the planner"), ("Act", "Planner adjusts and releases"), ("Measure", "Trim %, changeover loss, OTIF")], "UC2 data flow")))
S.append(uc_card("UC3 · Recurring · Wave 1", "Recycling quality and recycled-content evidence",
 "Head of sustainability, with the recycling plant heads",
 "Recycled-content targets now bind under PWM 2026 and, for EU customers, PPWR from 2030. Brand owners need evidence by plant and format. Recycling lines depend on feedstock quality: contamination, colour and IV in rPET; mixed layers in rMLP.",
 "AI sorting and quality prediction on recycling lines (IV, colour, contamination). Mass-balance and genealogy records from bale to resin to film to pack, packaged as customer-ready evidence of recycled content and recyclability.",
 "Bale and feedstock records, line sensors and lab tests on recycling lines, production genealogy across chip, film and converting, EPR filings.",
 "Yield and grade mix on rPET and rMLP; contamination rejects; share of output with complete evidence; customer evidence requests met.",
 f"Management's recycling revenue potential of ₹850 crore × 1.5% yield and grade gain = <b>{cr(b['uc3'],1)} a year</b> at the realised share of potential. The commercial value of evidence for customers is not counted.",
 "₹5 crore over three years.", "UFlex already reports AI-enabled segregation systems; HUL's Tinsukia Lighthouse cut sustainable-packaging trial time by 84%.",
 "Evidence standards still settling (PPWR methodology act expected end-2026); food-contact rules.",
 flow([("Sense", "Bale data, line sensors, lab tests"), ("Model", "Quality prediction and sorting"), ("Record", "Mass balance and genealogy, resin to pack"), ("Evidence", "Customer and EPR-ready claims"), ("Measure", "Yield, grade mix, evidence coverage")], "UC3 data flow")))
S.append(uc_card("UC4 · One-off · Wave 1", "New-capacity ramp-up and first-time-right",
 "Project heads for Dharwad BOPP and Egypt aseptic",
 "Egypt aseptic is in commercial trials with first-year utilisation expected around 30%; Dharwad BOPP is due in FY27–28. Every month to target output carries EBITDA.",
 "Instruments the new lines from commissioning, so start-up, grade qualification and first-time-right data are captured from day one; applies UC1 cause models to ramp-up losses.",
 "Commissioning and line data, qualification trials, quality records.",
 "Months to target utilisation; first-pass yield on new grades; qualification trials per grade.",
 f"Guided EBITDA of about ₹500 crore a year from four projects ÷ 12 × 1 month earlier × 50% attributed to AI = <b>{cr(b['uc4'],1)}</b> one-off (range {cr(lo['uc4'],1)} to {cr(hi['uc4'],1)}).",
 "₹3 crore.", "New lines are the cheapest place to build in instrumentation; no published ramp-up benchmark was found.",
 "Commissioning teams' priorities; OEM data access during warranty.",
 flow([("Instrument", "Data capture from commissioning"), ("Learn", "Start-up and grade qualification models"), ("Advise", "Settings for first-time-right"), ("Act", "Commissioning team applies"), ("Measure", "Months to target; first-pass yield")], "UC4 data flow")))
S.append(uc_card("UC5 · One-off cash · Wave 1", "Planning, procurement and inventory",
 "Group finance with the head of supply chain",
 "Inventories were ₹2,408 crore at 31 March 2026, about 100 days of cost of goods sold across nine countries, while PTA, MEG and polypropylene swing sharply. Lamination cure time also holds stock.",
 "Forecasts demand by grade, market and customer; sets inventory norms by item and plant; gives buyers price-risk signals; flags slow-moving stock and cure-time bottlenecks.",
 "ERP sales, stock, purchases and order book; production plans; supplier lead times; public polymer price series.",
 "Inventory days by category and plant; forecast accuracy; on-time-in-full.",
 f"5 days of inventory released × 50% attributed to AI = <b>{cr(b['wc'])}</b> one-off cash (range {cr(lo['wc'])} to {cr(hi['wc'])}). Interest saved is not counted as benefit. In a supply disruption UFlex may choose to hold more stock; this lever is a choice, not a forecast.",
 "₹5 crore build plus ₹2 crore a year planning-engine licence.", "Multi-Color (labels) reports forecast accuracy up 50% (vendor case study); no credible public figure for packaging working capital.",
 "ERP data quality across countries; parallel spreadsheets.",
 flow([("Data", "ERP sales, stock, purchases, order book"), ("Model", "Demand, inventory norms, price risk"), ("Plan", "S&OP and buyer workbench"), ("Act", "Planners and buyers decide"), ("Measure", "Inventory days, OTIF, cash")], "UC5 data flow")))
S.append(uc_card("UC6 · Recurring · Wave 2", "Gravure make-ready and colour",
 "Head of flexible packaging operations (Noida, Jammu)",
 "Make-ready and colour-matching waste on gravure presses, ink viscosity drift and solvent use in the Noida and Jammu converting plants. Artwork checking is a software purchase, not part of this strategy.",
 "Recommends press and ink settings from job history, cylinder engraving data and colour measurement; predicts viscosity drift; supports colour formulation in UFlex's own ink kitchen.",
 "Press data, cylinder engraving records, colour measurements, ink formulation and viscosity data, job tickets.",
 "Make-ready waste metres per job; colour approval at first pull; solvent use per job.",
 f"Packaging volume 151,755 t × 0.4% waste removed × ₹170/kg × 80% value lost = <b>{cr(b['uc6'],1)} a year</b> at full scale (range {cr(lo['uc6'],1)} to {cr(hi['uc6'],1)}).",
 "₹3 crore.", "Published converter waste: printing 3–5%, lamination 1–2%. Gravure 100% inspection at PPL cut print complaints 50% (vendor case study).",
 "Short runs and many job types.",
 flow([("Sense", "Press, colour, viscosity, cylinder data"), ("Model", "Make-ready and colour settings"), ("Advise", "Settings per job"), ("Act", "Press crew and ink kitchen apply"), ("Measure", "Waste metres, first-pull approvals")], "UC6 data flow")))
S.append("<h3>Wave 2: sized in the sprint</h3>" + T(["Use case", "What it would do", "Why it waits"], [
 ["Metalliser and coating quality", "Optical density and barrier (OTR, WVTR) consistency, pinholes, aluminium wire use and vacuum cycle time; AlOx and UHB coating quality", "High value on premium grades; needs metalliser and coater data to size"],
 ["Chip-plant process control", "Continuous-polymerisation control of IV, DEG and carboxyl end groups; heat-transfer energy", "A mature application of advanced process control; size from Panipat and Egypt data"],
 ["Aseptic quality and filling uptime", "Carton print and crease quality; filling-machine uptime at customer sites as a service", "UFlex's main growth engine; needs customer-site data agreements"],
 ["AI in UFlex machines", "Use UFlex's own Ceruflex presses as the test bed for predictive maintenance as a product feature; EU Machinery Regulation readiness", "Product and regulatory decisions first"],
 ["Plant copilot", "Answers from SOPs, specifications and past incidents, in local languages", "An enabler once the data foundation exists"],
 ["Price and quote intelligence", "Customer- and grade-level margin and quote analytics", "Parked: film prices follow supply and demand"],
]) + "</section>")

S.append(f"""<section><h2 id="architecture"><span class="n">7</span>Architecture</h2>
<div class="col"><p>One reference architecture serves every use case. Plant and enterprise sources feed an edge layer at each site and a governed group data fabric. AI services run on top, and decisions flow back to shift leads, planners and customers. Security and governance cut across every layer.</p></div>
<figure><div class="scroll">{ref_arch()}</div><figcaption>Reference architecture. The current ERP, historians and OEM data feeds are confirmed in the sprint.</figcaption></figure>
{T(["Layer", "Design decisions", "Build or buy"], [
 ["Plant edge", "A historian and edge compute at each site, reusing OEM and inspection-vendor feeds. Models that act within seconds run on site so the line never depends on the WAN.", "Buy and configure"],
 ["Data fabric", "One data model (site, line, grade, order, roll) with genealogy from resin to pack. Named data owners and quality rules. Cross-border transfers reviewed per country; Russia excluded pending review.", "Buy the platform; the data model is UFlex's own"],
 ["AI services", "Cause and early-warning models, optimisation, recycling quality, demand and inventory models; one registry; MLOps with monitoring and retraining.", "Build with a partner; buy planning engines"],
 ["Applications", "Advisories inside existing line screens; planning and slitting plans; customer evidence packs; a value ledger tracking every use case against its baseline.", "Mix"],
 ["Security and governance", "OT segmentation and vendor remote-access control (IEC 62443); CERT-In 6-hour incident reporting and 180-day log retention in India; an AI inventory with risk tier and human-oversight rule for each system.", "Policy built; tools bought"],
])}</section>""")

sc = lambda k, f="{:.1f}": [f.format(lo[k]), f.format(b[k]), f.format(hi[k])]
S.append(f"""<section><h2 id="roi"><span class="n">8</span>Value and ROI</h2>
<div class="col"><p><b>Method.</b> Three kinds of value are kept apart. Recurring EBITDA from the plant and recycling use cases, net of the programme's own running cost, is the headline. The one-off EBITDA from a faster ramp-up is reported separately. So is the working-capital release, of which we attribute half to AI; interest on it is never counted as benefit. Plant value is built on tonnes, not revenue shares. Costs include 25% contingency, internal plant time, licences, sensors, travel and FX, and they vary by scenario (the low case assumes a 25% overrun). The accompanying workbook holds every assumption in its own cell.</p></div>
<figure><div class="scroll">{value_chart()}</div><figcaption>Recurring EBITDA at full scale. Base total {cr(b['full'],1)} a year; low {cr(lo['full'],1)}; high {cr(hi['full'],1)}.</figcaption></figure>
<h3>Five years, base case (₹ crore)</h3>
{T(["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Total"], [
 ["Recurring EBITDA benefit"] + [f"{x:,.1f}" for x in b["rec"]] + [f"{sum(b['rec']):,.1f}"],
 ["Ramp-up pull-forward (one-off)"] + [f"{x:,.1f}" for x in b["ramp"]] + [f"{sum(b['ramp']):,.1f}"],
 ["Programme cost"] + [f"({x:,.1f})" for x in b["cost"]] + [f"({sum(b['cost']):,.1f})"],
 ["<b>Net EBITDA effect</b>"] + [f"<b>{x:,.1f}</b>" for x in b["net"]] + [f"<b>{sum(b['net']):,.1f}</b>"],
 ["Working-capital release, AI share (cash)"] + [f"{x:,.1f}" for x in b["wcy"]] + [f"{sum(b['wcy']):,.1f}"],
], num=(1, 2, 3, 4, 5, 6))}
<figure><div class="scroll">{five_year_chart()}</div><figcaption>Base case. Dark bars: recurring EBITDA benefit; light: ramp-up pull-forward; red: programme cost.</figcaption></figure>
<h3>Scenarios</h3>
{T(["Measure", "Low", "Base", "High"], [
 ["Recurring EBITDA at full scale (₹ cr a year)"] + sc("full"),
 ["Year-5 net recurring EBITDA after programme run cost (₹ cr)"] + sc("y5net"),
 ["5-year programme cost (₹ cr)"] + sc("cost_tot", "{:.0f}"),
 ["5-year NPV of net EBITDA effect (₹ cr)"] + sc("npv", "{:.0f}"),
 ["5-year NPV including the AI share of working capital (₹ cr)"] + sc("npv_wc", "{:.0f}"),
 ["Payback on EBITDA"] + [lo["payback"], b["payback"], hi["payback"]],
], num=(1, 2, 3))}
<div class="callout"><b>The decision rule.</b> On our conservative base rates, the full nine-country programme does not pay for itself within five years (NPV {cr(b['npv'])} on EBITDA; about {cr(b['npv_wc'])} once the inventory release is included). It breaks even if UFlex's measured rates are about {b['be']:.1f} times our base assumptions, which means removing about {b['be_scrap']*100:.2f}% of film production as scrap and saving about {b['be_energy']*100:.1f}% of energy per good kilogram. Those rates are well below what the Kunlene and ACG Lighthouses report, but they are not proven at UFlex. The pilot exists to measure them. Below the line, UFlex keeps the enterprise use cases and the data foundation, and does not scale the film-line work.</div>
<div class="col"><h3>Assumptions to replace with UFlex data first</h3><ol>
 <li>Avoidable scrap, breaks and restart loss by line and grade, and the value recovered through reclaim and seconds.</li>
 <li>Energy per kilogram by line and grade, and the film-line share of power and fuel.</li>
 <li>Recycling line yields and grade mix; evidence requests from customers.</li>
 <li>Inventory by category, plant and age; current forecast accuracy.</li>
 <li>Vendor, OEM and partner quotes for the build, by line type and vintage.</li>
</ol></div></section>""")

S.append(f"""<section><h2 id="roadmap"><span class="n">9</span>Roadmap and gates</h2>
<figure><div class="scroll">{gantt()}</div><figcaption>Bars show workstreams; diamonds are decision gates. Months from the start of the sprint.</figcaption></figure>
{T(["Gate", "When", "Go if", "Stop or rethink if"], [
 ["1 · After the sprint", "Week 2", "UFlex has chosen the line and problem; data access and the OT security protocol are agreed; the existing-tools inventory shows what can be reused", "No line has the data needed; fix the data foundation first"],
 ["2 · After six months of pilot measurement", "Month 7", f"Measured gains at or above the break-even line (about {b['be_scrap']*100:.2f}% scrap removed, {b['be_energy']*100:.1f}% energy per good kg), against the control line, signed off by finance", "Below the line after one retraining cycle: keep UC3, UC4, UC5 and the data foundation; do not scale the film-line work"],
 ["3 · Year-1 value review", "Month 15", "The value ledger shows India sites tracking the measured rates", "Not tracking: re-plan before committing overseas spend"],
])}
<div class="col"><h3>The readiness sprint (two weeks)</h3>
<p>Days 1–3 <b>Immerse</b>: a walk-through of the line UFlex nominates, interviews, and an inventory of the AI, automation and line-supplier digital services already installed. Days 4–7 <b>Audit</b>: data availability and quality for the chosen problem; the IT and OT landscape; the security protocol. Days 8–11 <b>Prioritise</b>: rebuild the model on UFlex numbers and set the break-even line with finance. Days 12–14 <b>Decide</b>: a working session on the pilot scope, the control line and the measurement plan.</p></div></section>""")

S.append(f"""<section><h2 id="operating"><span class="n">10</span>Operating model and governance</h2>
<div class="col"><p>A small central team owns the data model, the platform and the playbook. Plants own adoption and results, and partners supply the historian, vision and planning engines. Roles below are the natural owners; names are agreed with UFlex, not assumed.</p></div>
{T(["Role", "Natural owner", "Responsibility"], [
 ["Executive sponsor", "A member of the executive leadership team", "Owns the ambition and chairs the gates"],
 ["Value owner", "Group finance", "Signs off baselines, the attribution rule and the value ledger"],
 ["Use-case owners", "Film technical and operations; recycling and sustainability; flexible packaging operations; supply chain; new-project heads", "Own outcomes at line and plant level"],
 ["Central AI and data team (6–10 people)", "UFlex IT leadership", "Data model, platform, MLOps, models with partners, the replication playbook"],
 ["Plant champions", "A process engineer at each scaled site", "Adoption, operator feedback, local baselines"],
])}
<div class="col"><h3>Governance</h3><ul>
 <li><b>AI policy and inventory</b>, aligned with ISO/IEC 42001 and the NIST AI Risk Management Framework, recording each system's purpose, data, owner, risk tier and human-oversight rule.</li>
 <li><b>Human oversight</b>: advisory by default; closed-loop control only after a documented performance record, with operator override.</li>
 <li><b>OT security</b> (IEC 62443) and vendor remote-access control before any model connects to a line.</li>
 <li><b>Sanctions and data transfer</b>: a country-by-country review of data flows and of vendor-licensing constraints, with the Russia site excluded until cleared.</li>
</ul></div>
<h3>Regulation that applies</h3>
{T(["Instrument", "Status and dates", "What it means here"], [
 ["India DPDP Act 2023 and Rules 2025", "Rules notified 13 Nov 2025; core duties from 13 May 2027", "Low for plant AI; applies to HR, customer-contact and CRM data"],
 ["CERT-In Directions (2022)", "In force", "6-hour incident reporting; 180-day log retention in India; covers connected IIoT and AI platforms"],
 ["MeitY India AI Governance Guidelines", "Released 5 Nov 2025; voluntary", "A basis for UFlex's AI policy"],
 ["EU Machinery Regulation (EU) 2023/1230", "Applies from 20 Jan 2027", "Machines with machine-learning safety functions need a Notified Body"],
 ["EU AI Act, as amended by the Digital Omnibus", "High-risk duties from 2 Dec 2027; AI in regulated products from 2 Aug 2028", "In-plant process, quality and maintenance AI is generally not high-risk"],
 ["EU Cyber Resilience Act", "Reporting from 11 Sep 2026; most duties from 11 Dec 2027", "Check applicability for connected machines sold into the EU"],
 ["India PWM (Amendment) Rules 2026; EU PPWR", "In force 31 Mar 2026; PPWR applies from 12 Aug 2026, targets from 2030", "Drives the evidence in UC3"],
])}</section>""")

S.append("""<section><h2 id="risks"><span class="n">11</span>Risks</h2>""" + T(["Risk", "Likelihood", "Mitigation"], [
 ["Line data is locked in OEM systems or under warranty terms", "High", "Inventory of installed tools in the sprint; choose the pilot line for data access; negotiate OEM data feeds"],
 ["Gains confounded by price, mix and grade changes", "High", "Per-kg, per-grade measurement; control line; finance-signed attribution rule; six-month measurement"],
 ["Measured rates fall below break-even", "Medium", "Gate 2 stops film-line scale-up; enterprise use cases and the data foundation continue"],
 ["Integration cost higher across OEMs and line vintages", "Medium", "Cost by line type in the sprint; 25% contingency; replicate only on lines with similar control systems first"],
 ["Sanctions and vendor-licensing constraints at overseas sites", "Medium", "Country-by-country review; Russia excluded until cleared; vendor stack chosen with export controls in mind"],
 ["Operators do not trust advisories", "Medium", "Advisory mode with reasons shown; feedback logged; plant champions"],
 ["OT cyber exposure from connecting lines", "Medium", "IEC 62443 segmentation and remote-access control before integration"],
]) + "</section>")

S.append("""<section><h2 id="next"><span class="n">12</span>Next step</h2>
<div class="col"><p>We propose a two-week readiness sprint on one line and one problem that UFlex nominates, preceded by a 45-minute working session with film technical leadership and group finance to choose them.</p>
<h3>Commercial terms we would propose</h3><ul>
 <li>Sprint: a fixed fee in the range of ₹15–25 lakh. UFlex keeps every deliverable, with no exclusivity and no obligation to continue.</li>
 <li>Pilot: advisory fees capped, with 30–50% at risk against the finance-signed baseline on the control line.</li>
 <li>Team: a lead advisor and a film-process specialist with BOPET and BOPP line experience, named with references in the proposal.</li>
 <li>Independence: no fees from historian, vision or planning vendors; a written conflict-of-interest declaration; NDA and data-security terms covering CERT-In and DPDP.</li>
</ul>
<h3>What we would need from UFlex</h3><ul>
 <li>Access to the chosen line, its engineers, and its control, inspection and energy data</li>
 <li>The list of installed line-supplier digital services and inspection systems</li>
 <li>ERP extracts for inventory, sales and purchases (24 months)</li>
 <li>Recycling line data and customer evidence requests</li>
 <li>Interviews with 6–8 leaders across films, recycling, packaging, finance, supply chain and IT</li>
</ul></div></section>""")

S.append("""<section><h2 id="sources"><span class="n">A</span>Sources and notes</h2>
<div class="col"><p>All UFlex figures are from UFlex's own results, presentations and annual reports. ₹ crore figures are converted from published ₹ lakh or ₹ million values without other adjustment. Peer results carry their evidence type. Open items to confirm with UFlex: the commissioning date of the Noida recycling plant (30 April or 1 May 2026), India film capacity history (155,000 or 164,160 MTPA), FY25 restated EBITDA, IT leadership and the ERP in use.</p></div>
<ul class="src">
 <li>UFlex, Q4 FY26 investor presentation: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q4FY26_Presentation.pdf</li>
 <li>UFlex, consolidated results FY26: https://www.uflexltd.com/pdf/financials/Consolidated/UFLEX_NSEBSE_CONS_RESULTS_31MAR2026.pdf</li>
 <li>UFlex, consolidated results Q1 FY27: https://www.uflexltd.com/pdf/financials/Consolidated/UFLEX_NSEBSE_CONS_RESULTS_30JUN2026.pdf</li>
 <li>UFlex, Q1 FY27 presentation: https://www.uflexltd.com/pdf/QER/2026-27/UFlex_Q1FY27_Presentation.pdf</li>
 <li>UFlex, investor presentation 10 Sep 2026: https://www.uflexltd.com/pdf/IR/Investor_Presentation_10Sep_2026.pdf</li>
 <li>UFlex, Annual Report FY2025-26: https://www.uflexltd.com/pdf/financials/annual-reports/UFLEX-AR-2025-26.pdf</li>
 <li>UFlex, Annual Report FY2024-25: https://www.uflexltd.com/pdf/financials/annual-reports/UFLEX-AR-2024-25.pdf</li>
 <li>UFlex, Q2 FY26 call transcript: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q2FY26_Transcript.pdf</li>
 <li>UFlex, BRSR FY2025-26: https://nsearchives.nseindia.com/corporate/DineshSharma_04072026193230_SIGNEDUFLEXNSEBSEREG36BRSR20252026.pdf</li>
 <li>Polyplex, Q4 FY26 investor presentation: https://nsearchives.nseindia.com/corporate/POLYPLEX_27052026174118_PCL_Investor_Presentation_Q4_2025-26_signed.pdf</li>
 <li>Cosmo First, Q4 FY26 call transcript: https://nsearchives.nseindia.com/corporate/COSMOFILMS_28052026143240_Intimation_Transcript.pdf</li>
 <li>World Economic Forum, Global Lighthouse Network, 15 Jan 2026: https://www.weforum.org/press/2026/01/global-lighthouse-network-recognizes-23-new-sites-launches-ai-platform-for-industrial-transformation/</li>
 <li>ACG, Shirwal Lighthouse: https://www.acg-world.com/news/acg-shirwal-facility-joins-world-economic-forum-global-lighthouse-network</li>
 <li>McKinsey, The continuing evolution of the Global Lighthouse Network: https://www.mckinsey.com/capabilities/operations/our-insights/the-continuing-evolution-of-the-global-lighthouse-network</li>
 <li>EU Packaging and Packaging Waste Regulation (EU) 2025/40: https://eur-lex.europa.eu/eli/reg/2025/40/oj/eng</li>
 <li>EU Machinery Regulation overview (UL): https://www.ul.com/resources/navigating-new-eu-machinery-regulation-eu-20231230</li>
 <li>DPDP Rules 2025 (JSA summary): https://www.jsalaw.com/wp-content/uploads/2025/11/JSA-Prism-InfoTech-November-2025-DPDP-Rules.Final_.pdf</li>
 <li>MeitY AI Governance Guidelines: https://indianinfrastructure.com/2025/11/07/meity-unveils-india-ai-governance-guidelines-under-indiaai-mission/</li>
</ul>
<footer>PLUMB Advisory · Prepared from public information only; not reviewed by UFlex. Figures are illustrative until re-based on UFlex data in the readiness sprint.</footer></section></div>""")

open(OUT, "w").write("\n".join(S))
print(OUT, sum(len(x) for x in S))
