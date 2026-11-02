"""UFlex AI strategy — v3 page builder."""
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
    g = lambda r: v[f"B{r}"].value
    return {
        "uc1s": u["B5"].value, "uc1e": u["B6"].value, "uc2": u["B7"].value, "uc3": u["B8"].value, "uc6": u["B9"].value,
        "uc4": u["B10"].value, "wc": u["B11"].value, "tp": u["B13"].value,
        "rec": yr(9), "ramp": yr(10), "cost": yr(11), "net": yr(12), "ebitda": yr(14), "wcy": yr(15), "uc1c": yr(17), "uc1n": yr(18),
        "stage1": g(21), "npv": g(22), "y5gross": g(23), "y5run": g(24), "y5net": g(25), "npv_tv": g(27), "npv_wc": g(28), "payback": g(29),
        "uc1_npv": g(30), "uc1_be": g(31), "uc1_scrap": g(32), "uc1_energy": g(33), "prog_be": g(34),
        "cost_tot": sum(yr(11)),
    }

LOW, BASE, HIGH = (read(f"{SCR}/v3s{i}.xlsx") for i in (1, 2, 3))
TORN = json.load(open(f"{RUN}/tornado.json"))
json.dump({"low": LOW, "base": BASE, "high": HIGH, "tornado": TORN}, open(f"{RUN}/model-results.json", "w"), indent=1, default=str)
exec(open(f"{SCR}/v2parts.py").read())          # CSS, T(), charts, uc_card
b, lo, hi = BASE, LOW, HIGH
cr = lambda x, d=0: (f"−₹{-x:,.{d}f} cr" if x < 0 else f"₹{x:,.{d}f} cr")

def tornado_chart():
    names = {"Avoidable scrap and off-spec removed (share of film production)": "Scrap removed (UC1)",
             "Yield and grade gain on rPET output": "rPET yield and grade gain (UC3)",
             "Energy saved per good kg on film lines": "Energy per good kg (UC1)",
             "Cost multiplier (every cost line)": "Programme cost",
             "Converting waste removed (share of flexible-packaging output)": "Converting waste (UC6)",
             "Discount rate": "Discount rate",
             "Value lost per kg of scrap after reclaim or sale as seconds": "Value lost per kg of scrap",
             "Slitting trim and changeover scrap removed (share of film production)": "Trim removed (UC2)",
             "Polymer value of a kilogram of film (₹/kg)": "Polymer value per kg"}
    rows = sorted(TORN, key=lambda r: -abs(r[2] - r[1]))
    base = b["npv_tv"]
    W, L, R, T0, rh = 780, 230, 40, 26, 30
    H = T0 + rh * len(rows) + 40
    lo_v, hi_v = -40, 100
    sx = lambda x: L + (W - L - R) * (x - lo_v) / (hi_v - lo_v)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Sensitivity of NPV including steady state to each assumption, low to high">']
    for t in range(-40, 101, 20):
        x = sx(t); o.append(f'<line x1="{x:.1f}" y1="{T0-8}" x2="{x:.1f}" y2="{T0+rh*len(rows)}" class="{"axis" if t == 0 else "grid"}"/><text x="{x:.1f}" y="{T0+rh*len(rows)+16}" class="tick" text-anchor="middle">{t}</text>')
    o.append(f'<line x1="{sx(base):.1f}" y1="{T0-12}" x2="{sx(base):.1f}" y2="{T0+rh*len(rows)}" class="range"/><text x="{sx(base)+4:.1f}" y="{T0-14}" class="tick">base {base:.0f}</text>')
    for i, (k, l_, h_) in enumerate(rows):
        y = T0 + i * rh + rh / 2
        a_, z_ = min(l_, h_), max(l_, h_)
        o.append(f'<text x="{L-10}" y="{y+4:.1f}" class="lab" text-anchor="end">{E(names.get(k, k))}</text>')
        o.append(f'<rect x="{sx(a_):.1f}" y="{y-9:.1f}" width="{sx(z_)-sx(a_):.1f}" height="18" class="bar2"/>')
        o.append(f'<text x="{sx(a_)-6:.1f}" y="{y+4:.1f}" class="tick" text-anchor="end">{("−" if a_ < 0 else "")}{abs(a_):.0f}</text><text x="{sx(z_)+6:.1f}" y="{y+4:.1f}" class="tick">{z_:.0f}</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-4}" class="tick" text-anchor="middle">NPV including steady state, ₹ crore · each bar moves one assumption from low to high</text></svg>')
    return "".join(o)

def ref_arch():
    W, H = 900, 580
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Reference architecture from plant and enterprise sources through plant edge, data fabric and AI services to applications">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    def box(x, y, w, h, title, items):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="lay"/><text x="{x+12}" y="{y+20}" class="bt">{E(title)}</text>')
        for i, it in enumerate(items):
            o.append(f'<text x="{x+12}" y="{y+40+i*16}" class="bi">{E(it)}</text>')
    box(60, 456, 380, 110, "Plant sources", ["Chip plants: polymerisation, SSP, drying", "Film lines: extrusion, casting, MDO/TDO, winders", "Metallisers, coaters, slitters; inspection, gauges", "Recycling lines; gravure presses, ink kitchen"])
    box(460, 456, 380, 110, "Enterprise sources", ["ERP (confirmed in the sprint)", "Quality and lab records, maintenance", "Planning, procurement, orders; EPR records", "Specifications, recipes, SOPs"])
    box(60, 354, 780, 78, "Plant edge (each site, on UFlex infrastructure)", ["Historian and time-series buffer · edge compute for second-by-second models · keeps working when the WAN drops",
        "Reuses OEM and inspection-vendor data feeds already paid for; read-only from OT; advisory mode first"])
    box(60, 252, 780, 78, "Governed data fabric (group)", ["One data model: site → line → grade → order → roll, with records from resin to finished pack · data owners and quality rules",
        "Cross-border data flows reviewed per country · lineage for every dataset that feeds a model"])
    box(60, 150, 780, 78, "AI services", ["Break and defect cause models · scheduling and trim optimisation · recycling quality · demand, inventory, cash and FX models",
        "Language models with retrieval over SOPs and contracts (later) · MLOps: registry, monitoring, drift, retraining"])
    box(60, 48, 780, 78, "Applications and decisions", ["Shift-lead advisories inside existing line screens · scheduling and slitting plans · recycled-content records for customers",
        "S&OP and buyer workbench · make-ready settings · value ledger owned by group finance"])
    o.append('<rect x="856" y="48" width="34" height="518" rx="4" class="cross"/><text x="878" y="307" class="bt" text-anchor="middle" transform="rotate(-90 878 307)">Security (IEC 62443) · AI governance · CERT-In, DPDP</text>')
    for y in (434, 332, 230, 128):
        o.append(f'<line x1="450" y1="{y+18}" x2="450" y2="{y-2}" class="flow" marker-end="url(#ah)"/>')
    o.append('<text x="20" y="306" class="tick" text-anchor="middle" transform="rotate(-90 20 306)">Data flows up; decisions flow back to the line</text></svg>')
    return "".join(o)

def gantt():
    rows = [("Readiness sprint: line, problem, existing tools, data request", 0, 0.5, "s"), ("Gate 1: line and problem chosen; data request agreed", 0.5, 0, "g"),
            ("Data access and OT protocol; historian pre-period extracted", 0.6, 3, "p"), ("Pilot models built and tuned", 2, 4, "p"),
            ("Six-month measurement against the control line", 4, 10, "p"), ("UC5 planning and inventory (enterprise)", 0.6, 6, "p"),
            ("UC3 recycling quality and records (Noida)", 1, 8, "p"), ("UC4 Dharwad instrumentation; Egypt ramp support", 2, 12, "p"),
            ("Gate 2: UC1 measured against its own break-even", 10, 0, "g"), ("India film sites; UC2 slitting and scheduling", 10.2, 18, "c"),
            ("UC6 gravure make-ready (Noida, Jammu)", 12, 18, "c"), ("Gate 3: year-1 value review; overseas plan", 18, 0, "g"), ("Overseas film sites", 18.2, 36, "c")]
    W, L, T0, rh = 900, 420, 34, 28; H = T0 + len(rows) * rh + 12; months = 36
    sx = lambda m: L + (W - L - 12) * m / months
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Roadmap over 36 months with decision gates">']
    for m in range(0, 37, 6):
        x = sx(m); o.append(f'<line x1="{x:.1f}" y1="{T0-8}" x2="{x:.1f}" y2="{T0+len(rows)*rh}" class="grid"/><text x="{x:.1f}" y="{T0-12}" class="tick" text-anchor="middle">M{m}</text>')
    for i, (lab, a, z, k) in enumerate(rows):
        y = T0 + i * rh
        o.append(f'<text x="{L-10}" y="{y+rh/2+4:.1f}" class="lab" text-anchor="end">{E(lab)}</text>')
        if k == "g":
            cx, cy = sx(a), y + rh / 2; o.append(f'<path d="M{cx:.1f},{cy-9:.1f} L{cx+9:.1f},{cy:.1f} L{cx:.1f},{cy+9:.1f} L{cx-9:.1f},{cy:.1f} z" class="gate"/>')
        else:
            o.append(f'<rect x="{sx(a):.1f}" y="{y+6:.1f}" width="{max(sx(z)-sx(a), 4):.1f}" height="{rh-12}" rx="2" class="{ {"s": "bar2", "p": "bar", "c": "bar3"}[k] }"/>')
    o.append("</svg>")
    return "".join(o)

def matrix_chart():
    pts = [("UC1", "Film-line stability", 3.8, b["uc1s"] + b["uc1e"]), ("UC3", "Recycling quality", 3.6, b["uc3"]),
           ("UC6", "Gravure make-ready", 3.4, b["uc6"]), ("UC2", "Slitting and scheduling", 3.0, b["uc2"])]
    W, H, L, R, T0, B0 = 760, 340, 60, 30, 20, 50
    ymax = 20
    sx = lambda f: L + (W - L - R) * (f - 1.5) / 3.5
    sy = lambda v: T0 + (H - T0 - B0) * (ymax - v) / ymax
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Recurring use cases: value at full rate against feasibility">']
    o.append(f'<rect x="{sx(3.25):.1f}" y="{sy(ymax):.1f}" width="{sx(5)-sx(3.25):.1f}" height="{sy(0)-sy(ymax):.1f}" class="zone"/><text x="{sx(4.98):.1f}" y="{sy(ymax)+16:.1f}" class="tick" text-anchor="end">Stage 1 zone</text>')
    for t in range(0, 21, 5):
        y = sy(t); o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/><text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    o.append(f'<text x="{sx(2):.1f}" y="{H-30}" class="tick" text-anchor="middle">harder</text><text x="{sx(5):.1f}" y="{H-30}" class="tick" text-anchor="middle">easier</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-10}" class="tick" text-anchor="middle">Feasibility (data likely available, integration effort, time to first value) — re-scored in the sprint</text>')
    o.append(f'<text x="14" y="{(T0+H-B0)/2:.1f}" class="tick" text-anchor="middle" transform="rotate(-90 14 {(T0+H-B0)/2:.1f})">Base value at full rate, ₹ cr a year</text>')
    for uc, lab, f, v in pts:
        x, y = sx(f), sy(v); anchor, dx = ("end", -12) if f > 4.1 else ("start", 12)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" class="pt"/><text x="{x+dx:.1f}" y="{y+4:.1f}" class="lab" text-anchor="{anchor}">{uc} {E(lab)}</text>')
    o.append("</svg>")
    return "".join(o)

def value_chart():
    names = ["UC1 Film-line stability and yield", "UC3 Recycling quality", "UC6 Gravure make-ready", "UC2 Slitting and scheduling"]
    key = lambda d: [d["uc1s"] + d["uc1e"], d["uc3"], d["uc6"], d["uc2"]]
    L_, B_, H_ = key(lo), key(b), key(hi)
    W, H, L, R, T0, rowh = 760, 290, 250, 70, 24, 56
    xmax = 35.0
    sx = lambda v: L + (W - L - R) * v / xmax
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Recurring benefit at full rate by use case, low, base and high, ₹ crore a year">']
    for t in range(0, 36, 5):
        x = sx(t); o.append(f'<line x1="{x:.1f}" y1="{T0-6}" x2="{x:.1f}" y2="{T0+rowh*4}" class="grid"/><text x="{x:.1f}" y="{T0+rowh*4+18}" class="tick" text-anchor="middle">{t}</text>')
    for i, n in enumerate(names):
        y = T0 + i * rowh + rowh / 2
        o.append(f'<text x="{L-12}" y="{y+4:.1f}" class="lab" text-anchor="end">{E(n)}</text><rect x="{sx(0):.1f}" y="{y-11:.1f}" width="{sx(B_[i])-sx(0):.1f}" height="22" class="bar"/>')
        o.append(f'<line x1="{sx(L_[i]):.1f}" y1="{y:.1f}" x2="{sx(H_[i]):.1f}" y2="{y:.1f}" class="range"/><line x1="{sx(L_[i]):.1f}" y1="{y-7:.1f}" x2="{sx(L_[i]):.1f}" y2="{y+7:.1f}" class="range"/><line x1="{sx(H_[i]):.1f}" y1="{y-7:.1f}" x2="{sx(H_[i]):.1f}" y2="{y+7:.1f}" class="range"/>')
        o.append(f'<text x="{sx(H_[i])+8:.1f}" y="{y+4:.1f}" class="val">{B_[i]:.1f}</text>')
    o.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-4}" class="tick" text-anchor="middle">₹ crore a year at full rate · bar = base, whiskers = low to high</text></svg>')
    return "".join(o)

def five_year_chart():
    W, H, L, R, T0, B0 = 780, 320, 60, 20, 20, 54
    ymin, ymax = -60, 60
    sy = lambda v: T0 + (H - T0 - B0) * (ymax - v) / (ymax - ymin)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Base case five years: benefits against programme cost, ₹ crore">']
    for t in range(-60, 61, 20):
        y = sy(t); o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" class="{"axis" if t == 0 else "grid"}"/><text x="{L-8}" y="{y+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    gw = (W - L - R) / 5
    for i in range(5):
        cx = L + gw * i + gw / 2; bw = 34
        rec, ramp, cost, net = b["rec"][i], b["ramp"][i], b["cost"][i], b["net"][i]
        x1 = cx - bw - 4
        o.append(f'<rect x="{x1:.1f}" y="{sy(rec):.1f}" width="{bw}" height="{sy(0)-sy(rec):.1f}" class="bar"/>')
        if ramp > 0: o.append(f'<rect x="{x1:.1f}" y="{sy(rec+ramp):.1f}" width="{bw}" height="{sy(rec)-sy(rec+ramp):.1f}" class="bar2"/>')
        o.append(f'<text x="{x1+bw/2:.1f}" y="{sy(rec+ramp)-6:.1f}" class="val" text-anchor="middle">{rec+ramp:.0f}</text>')
        x2 = cx + 4
        o.append(f'<rect x="{x2:.1f}" y="{sy(0):.1f}" width="{bw}" height="{sy(-cost)-sy(0):.1f}" class="cost"/><text x="{x2+bw/2:.1f}" y="{sy(-cost)+14:.1f}" class="val" text-anchor="middle">−{cost:.0f}</text>')
        lab = "Stage 1" if i == 0 else f"Year {i+1}"
        o.append(f'<text x="{cx:.1f}" y="{H-30}" class="lab" text-anchor="middle">{lab}</text><text x="{cx:.1f}" y="{H-14}" class="tick" text-anchor="middle">net {("−" if net < 0 else "+")}{abs(net):.0f}</text>')
    o.append("</svg>")
    return "".join(o)

pct = lambda x, d=1: f"{x*100:.{d}f}%"
S = []
S.append(f"""<title>UFlex AI Strategy</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="cover">
 <div class="eyebrow">UFlex Limited · AI strategy · prepared from public information</div>
 <h1>Faster ramp-ups, cheaper kilograms and recycled-content records customers can rely on</h1>
 <p class="lede">An AI strategy for UFlex's growth phase: where AI can create value across new capacity, film lines, recycling and the enterprise; what to commit now and what only after measured results; how it fits together; and what it is worth on UFlex's own numbers.</p>
 <div class="meta"><span><b>Prepared by</b> PLUMB Advisory</span><span><b>Date</b> November 2026</span><span><b>Basis</b> UFlex annual reports FY25–FY26, results and investor presentations to Q1 FY27, public industry sources</span><span class="status">For discussion · not validated with UFlex data</span></div>
 <nav class="toc" aria-label="Contents">
  <a href="#summary">1 · Summary</a><a href="#uflex">2 · UFlex today</a><a href="#industry">3 · The industry</a><a href="#ai-today">4 · AI at UFlex today</a>
  <a href="#strategy">5 · The strategy</a><a href="#usecases">6 · Use cases</a><a href="#enterprise">7 · Enterprise AI</a><a href="#architecture">8 · Architecture</a>
  <a href="#roi">9 · Value and ROI</a><a href="#roadmap">10 · Roadmap and gates</a><a href="#operating">11 · Operating model and governance</a><a href="#next">12 · Risks and next step</a>
 </nav>
</header>""")

S.append(f"""<section><h2 id="summary"><span class="n">1</span>Summary</h2>
<div class="col">
<p>UFlex is in a growth phase. Egypt aseptic is in commercial trials, a 54,000-tonne BOPP line is coming at Dharwad, and Mexico WPP and the Noida recycling plant came on stream in 2026. Management's stated focus is <span class="q">"Focused investments in aseptic, WPP and recycling to accelerate growth"</span>. Film lines ran at 85.4% utilisation in Q1 FY27, with an EBITDA margin of 17.0% reported and 15.5% normalised.</p>
<p>AI can help in four places in this phase. It can bring new capacity to target output sooner, and take breaks, scrap and energy out of every kilogram on existing lines. It can lift recycling yields and produce the recycled-content records brand owners and regulators ask for. And it can give the enterprise better cash, inventory and FX forecasts across nine countries.</p>
<p>We recommend a staged programme. Stage 1 commits about {cr(b['stage1'])}: one pilot film line chosen by UFlex, inventory planning, recycling quality at Noida and Dharwad instrumentation. The larger roll-out follows only if the pilot line, measured for six months against a control line, clears its own break-even.</p>
</div>
<div class="kpis">
 <div class="kpi"><div class="v">{cr(b['stage1'])}</div><div class="l">Stage 1 commitment before any roll-out decision</div><div class="r">range {cr(hi['stage1'])} to {cr(lo['stage1'])}</div></div>
 <div class="kpi"><div class="v">{pct(b['uc1_scrap'],2)}</div><div class="l">of film production removed as scrap: the pilot result at which the film-line roll-out pays for itself</div><div class="r">with {pct(b['uc1_energy'])} energy saved per good kg</div></div>
 <div class="kpi"><div class="v">{cr(b['y5gross'])} → {cr(b['y5net'])}</div><div class="l">recurring benefit in year 5, before and after the programme's own running cost (base)</div><div class="r">plus one-off: {cr(b['wc'])} inventory cash, {cr(b['uc4'])} ramp-up</div></div>
</div>
<div class="col"><h3>What we recommend</h3>
<ol class="recs">
 <li><b>Start from what UFlex already runs.</b> List the line-supplier digital services, inspection systems, Ceruflex remote monitoring and AI segregation already in place, so nothing is bought twice.</li>
 <li><b>Prove the film-line case on one line and one problem UFlex chooses.</b> Measure for six months against a control line, using a design agreed with group finance. Roll out only if the line clears its own break-even.</li>
 <li><b>Run three enterprise-level use cases alongside.</b> These are inventory planning, recycling quality and records at Noida, and Dharwad instrumentation from commissioning. None depends on the pilot line.</li>
 <li><b>Build the data foundation once,</b> with records from resin to finished pack, because every use case and every recycled-content claim draws on it.</li>
 <li><b>Keep group finance as owner of the value ledger,</b> so results are measured by the people who report them.</li>
</ol></div></section>""")

S.append(f"""<section><h2 id="uflex"><span class="n">2</span>UFlex today</h2>
<div class="col"><p>UFlex describes itself as <span class="q">"India's largest flexible packaging materials and Solutions Company"</span>. In FY26 it reported total income of ₹15,513 crore, EBITDA of ₹1,983.6 crore (12.8%) and profit after tax of ₹317.1 crore. In Q1 FY27 revenue from operations rose 37.6% to ₹5,366 crore; management expects some normalisation as film prices settle. Films are 58.6% of FY26 revenue, from 636,160 tonnes a year of capacity in nine countries.</p></div>
{T(["Business", "FY26 share of revenue", "Scale (UFlex disclosures)"], [
 ["Packaging films and PET chips", "58.6%", "BOPET 401,800, BOPP 150,200, CPP 84,160 MTPA; metallised 238,600; AlOx 14,200; UHB 13,200. 492,779 t produced in FY26; 85.4% utilisation in Q1 FY27. Chip plants at Panipat and in Egypt."],
 ["Packaging: flexible, aseptic liquid, holography", "32.7%", "Flexible packaging 19,680 t in Q1 FY27 (78.7% utilisation); aseptic 17,983 t in Q1 FY27, Egypt plant in trials, target 24 bn packs by FY2027; holography 20,600 MTPA"],
 ["Engineering: packaging machines, printing cylinders", "2.9%", "500 machines and 108,000 cylinders a year; Ceruflex 500 gravure press with remote monitoring"],
 ["Others: inks, adhesives, coatings", "5.1%", "69,730 MTPA"],
 ["Recycling (within the businesses above)", "—", "rPET chips 79,020 MTPA and rMLP granules 34,897 MTPA; Noida commissioned April 2026 and ramping; 319 million PET bottles and 2,926 t of MLP waste recycled in Q1 FY27"],
])}
<h3>The cost lines AI can move (FY26, consolidated)</h3>
{T(["Line", "₹ crore", "AI levers"], [
 ["Cost of materials consumed", "8,877.0", "Scrap, breaks, restart and changeover loss, trim, converting waste (UC1, UC2, UC6)"],
 ["Power and fuel", "739.3", "Energy per good kilogram on film lines (UC1); chip-plant control (stage 2)"],
 ["Other operating expenses (management definition)", "2,171.4", "Maintenance and spares (stage 2, once repair and maintenance spend is known)"],
 ["Inventories, 31 March 2026", "2,408.3", "About 100 days of cost of goods sold (UC5)"],
], num=(1,))}
<h3>What makes UFlex distinctive</h3>
<div class="col"><ol>
 <li><b>It spans the chain from resin to pack.</b> PET chips, film, metallising and coating, inks and adhesives, cylinders, converting and recycling sit inside one group, so the records behind a recycled-content or recyclability claim can be assembled in one place.</li>
 <li><b>It is adding capacity now.</b> New lines are the cheapest place to build in data capture, during commissioning rather than as a retrofit.</li>
 <li><b>A film playbook can be repeated across nine countries.</b> A result proven on one line can be replicated, which is where AI economics improve.</li>
 <li><b>It builds machines.</b> Plant learning can become product features, and machines sold into the EU must meet the Machinery Regulation from January 2027.</li>
 <li><b>Its recycling capacity is commissioned and ramping,</b> at Noida, Mexico, Egypt, Poland, Jammu and Malanpur.</li>
</ol></div></section>""")

S.append(f"""<section><h2 id="industry"><span class="n">3</span>The industry</h2>
<div class="col">
<p><b>Film prices follow capacity.</b> Listed peers describe raw materials as largely passed through and expect BOPET and BOPP margins to stay volatile as new lines arrive in India and China. The 2026 rise in film prices followed the West Asia conflict, and UFlex expects some normalisation. Through the cycle, a producer controls cost per kilogram, first-time-right production and mix.</p>
<p><b>Feedstock is more volatile.</b> Indian PTA rose about 31% within days in March 2026 and polypropylene list prices rose by a cumulative ₹23 a kilogram, so planning and buying decisions carry more value than before.</p>
<p><b>Recycled content is becoming a legal and commercial requirement.</b> India's Plastic Waste Management (Amendment) Rules 2026 set recycled-content targets for producers, importers and brand owners. Flexible packaging rises from 10% to 20% by 2027-28, and multilayer from 5% to 10%. Exemptions apply where food-contact rules restrict recycled content, with a carry-forward for shortfalls. QR or barcode labelling has applied since July 2025. The EU Packaging and Packaging Waste Regulation has applied since 12 August 2026, with recyclability grades and recycled-content targets binding from 2030, averaged per plant per year. Brand owners will ask suppliers for records by plant and format.</p>
</div>
<h3>What peers show</h3>
{T(["Company", "AI evidence", "Result", "Evidence type"], [
 ["Kunlene Film Industries, Suzhou (BOPP films)", "WEF Lighthouse, January 2026", "Defects −31%, R&amp;D lead time −45%, minimum order size −83%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["ACG Packaging Materials, Shirwal (pharmaceutical films and foils)", "WEF Lighthouse, January 2026: machine learning, generative AI, IIoT, digital twins", "Lead time −40%, defects −71%, energy −31%, on-time-in-full +34%", '<span class="lbl">Company, WEF-assessed</span>'],
 ["Mondi, Hilm (Austria; product not stated)", "Predictive quality 24 hours ahead, with operator recommendations", "Rework and waste −50% versus 2018", '<span class="lbl">Company-reported</span>'],
 ["Amcor", "Vision for seal defects, predictive maintenance, changeover root-cause analysis", "No figures disclosed", '<span class="lbl">Company, qualitative</span>'],
 ["Indian film peers", "Describe digitalisation", "No quantified AI outcomes disclosed", '<span class="lbl">Annual reports</span>'],
])}
<div class="col"><p>These are relative reductions across whole sites over several years, so they cannot be compared directly with the absolute rates in our model until UFlex's own scrap and defect baselines are known. We treat them as evidence that the levers are real, not as a forecast.</p></div></section>""")

S.append(f"""<section><h2 id="ai-today"><span class="n">4</span>AI at UFlex today</h2>
<div class="col"><p>UFlex already reports AI work across several businesses, and the strategy builds on it. A fair assessment of maturity needs UFlex's people, systems and data, so it is part of the sprint rather than this document.</p></div>
{T(["Where", "What UFlex has reported", "Source"], [
 ["Engineering", "Machines with embedded AI for predictive maintenance and real-time monitoring", "Annual Report FY25"],
 ["Holography", "AI-based quality control and AI-driven track-and-trace", "Annual Report FY25"],
 ["Packaging films", "AI-led product development", "Annual Report FY25"],
 ["Recycling", "Advanced recycling technologies, AI-enabled segregation and traceability", "Annual Report FY26"],
 ["People", "AIM-AIA (AI in Manufacturing) leadership programme", "Annual Report FY26"],
 ["Gravure presses", "Ceruflex 500 with remote monitoring", "Annual Report FY26"],
])}
<h3>What we would assess together in the sprint</h3>
{T(["Area", "Questions"], [
 ["Existing tools", "Which line-supplier digital services and inspection systems are installed and paid for (for example from film-line, metalliser and inspection vendors), and what they already do"],
 ["Data", "Historian coverage and resolution by line; quality, break and energy records; what the ERP holds"],
 ["Value", "Which initiatives are live, who owns them, and whether results are tracked against a baseline"],
 ["People and delivery", "In-house data and automation skills, the AIM-AIA cohort, partners, and how pilots reach production"],
 ["Governance and security", "AI and OT security policies, vendor remote access, and cross-border data rules"],
])}</section>""")

S.append("""<section><h2 id="strategy"><span class="n">5</span>The strategy</h2>
<div class="col"><p><b>Ambition.</b> Use AI to bring new capacity to target output sooner, lower the cost of every kilogram on existing lines, make recycled-content records reliable, and improve cash and inventory decisions across nine countries, committing money in stages as results are measured.</p>
<h3>Five strategic choices</h3></div>""" + T(["Choice", "What it means", "Why, for UFlex"], [
 ["Build AI into new capacity", "Instrument Dharwad from commissioning; support the Egypt aseptic ramp-up.", "New lines are the cheapest place to capture data; each month to target output carries EBITDA."],
 ["Take loss out of every kilogram", "Breaks, gels, restart and changeover scrap, trim, energy per good kilogram.", "Cost per kilogram is what UFlex controls through the cycle."],
 ["Make recycled-content records reliable", "Recycling quality and records from bale to pack, aligned with recognised chain-of-custody models.", "PWM 2026, QR labelling and EU PPWR require it; brand owners will ask suppliers."],
 ["Improve enterprise decisions", "Inventory, procurement, cash and FX forecasting across nine currencies.", "About 100 days of inventory; FX losses in Nigeria, Egypt and Mexico drove exceptional items in FY24–FY25."],
 ["Commit in stages", "One line, six months, a control line; roll out only on measured results.", "Keeps the larger spend uncommitted until UFlex's own rates are known."],
]) + """<div class="col"><h3>Guiding principles</h3><ul>
 <li><b>Start from what is installed.</b> Use OEM and inspection-vendor data feeds already paid for; add only what is missing.</li>
 <li><b>Start with the data model.</b> One model of site, line, grade, order and roll serves every use case and every recycled-content record.</li>
 <li><b>Advise first.</b> Thickness control and defect classification are usually automated on modern lines; AI adds cause-finding and early warning, and earns any closed-loop role only after a performance record.</li>
 <li><b>Read-only from the plant floor.</b> No remote access to OT networks; data is exported by UFlex IT.</li>
 <li><b>Measure everything.</b> Each use case has a baseline, a control where possible, an attribution rule signed by group finance, and a stop condition.</li>
</ul></div></section>""")

S.append(f"""<section><h2 id="usecases"><span class="n">6</span>Use cases</h2>
<div class="col"><p>Six use cases form the programme. UC1, UC2, UC3 and UC6 produce recurring benefit; UC4 and UC5 produce one-off value that we report separately. Further use cases are sized in the sprint.</p></div>
<figure><div class="scroll">{matrix_chart()}</div><figcaption>The four recurring use cases: base value at full rate against feasibility. Feasibility is our outside-in judgement, re-scored in the sprint.</figcaption></figure>""")
S.append(uc_card("UC1 · Recurring · Stage 1 pilot", "Film-line stability and yield",
 "Film technical and operations leadership, with the pilot plant head",
 "On modern lines, thickness control and defect classification are usually automated; on older lines profile-loop tuning may still pay. The larger losses are breaks at the MDO and TDO, gels and black specks from degraded polymer (dead spots, die build-up), restart scrap after breaks, changeover scrap and winding defects. Chip moisture and IV, drying and crystallisation, and the share of reclaim and rPET in the blend all feed these, and the rising recycled-content push makes blend control matter more.",
 "Links each break or defect to its upstream cause across time lags and roll positions, from chip properties through casting and pinning, stretching and filter-change cycles to the winder; warns shift leads before a break; recommends blend, changeover and filter-change settings that cut restart and transition scrap; tracks energy per good kilogram and the carbon it represents.",
 "Chip lab data (IV, moisture), dryer and extruder tags, casting and pinning, MDO/TDO tags including clip and chain condition, break logs, scanner events, roll and grade records, energy meters. Most already exists in OEM, inspection and lab systems.",
 "Breaks per 1,000 running hours; scrap and off-spec kg per tonne; restart and changeover loss; kWh per good kg. A six-month historian pre-period and a matched control line; sample size set from historian variance in the sprint.",
 f"Film production 492,779 t × 0.6% avoidable scrap removed × ₹110/kg × 30% value lost after reclaim or sale as seconds, plus 2% energy per good kg on the film-line share of power and fuel = <b>{cr(b['uc1s']+b['uc1e'],1)} a year</b> at full coverage (range {cr(lo['uc1s']+lo['uc1e'],1)} to {cr(hi['uc1s']+hi['uc1e'],1)}). Throughput from fewer breaks is shown only as a memo ({cr(b['tp'],1)} a year when lines are sold out).",
 "₹3 crore for the pilot line; about ₹1.5 crore a further site, varying by OEM and line vintage.",
 "Kunlene (BOPP films) defects −31%; Mondi Hilm rework and waste −50% (product not stated).",
 "Data held in OEM systems; operator trust; integration effort across OEMs and vintages.",
 flow([("Sense", "Chip, extruder, stretching, break and roll data"), ("Cause model", "Links breaks and defects to upstream conditions"), ("Advise", "Early warning; blend and changeover settings"), ("Act", "Shift lead accepts or rejects; reason logged"), ("Measure", "Breaks, scrap kg/t, kWh per good kg vs control")], "UC1 data flow")))
S.append(uc_card("UC2 · Recurring · After Gate 2", "Slitting, deckle and line scheduling",
 "Planning and slitting leads at the film sites",
 "Most producers already run deckle optimisation. The remaining gains are in sequencing grades and thicknesses on each line, in master-roll ageing constraints for BOPP before slitting, and in linking slitting plans to the order book and line schedule.",
 "Extends existing trim optimisation with grade and thickness campaigning, run-rate and changeover-loss prediction, and master-roll ageing constraints.",
 "Order book, slitter set-ups, master-roll stock and age, changeover history, line run rates.",
 "Trim loss %; changeover time; on-time-in-full; finished-goods days (campaigning can raise stock, so this is tracked with UC5).",
 f"Film production × 0.2% trim removed beyond today's optimisation × ₹110/kg × 30% value lost = <b>{cr(b['uc2'],1)} a year</b> at full coverage (range {cr(lo['uc2'],1)} to {cr(hi['uc2'],1)}). Changeover scrap is counted in UC1, not here.",
 "₹3.5 crore after Gate 2.", "Klöckner Pentaplast reports −3% waste from trim optimisation (vendor case study).",
 "Gains may be small where optimisation is already in place; planner adoption.",
 flow([("Data", "Orders, slitter set-ups, roll stock and age"), ("Optimise", "Deckle, slitting and grade sequence"), ("Plan", "Proposed plan for the planner"), ("Act", "Planner adjusts and releases"), ("Measure", "Trim %, changeover time, OTIF")], "UC2 data flow")))
S.append(uc_card("UC3 · Recurring · Stage 1", "Recycling quality and recycled-content records",
 "Sustainability leadership, with the recycling plant heads",
 "Feedstock dominates rPET cost and quality. Bale quality, PVC and other contamination, colour and IV decide yield and whether output reaches food-contact grades through SSP decontamination and the relevant approvals. rMLP is lower-value. Recycled-content claims also need records that fit a recognised chain-of-custody model, such as physical segregation or mass balance (ISO 22095), and registered-recycler certificates under PWM.",
 "Grades bales at purchase from images and lab samples; predicts yield and grade from feedstock and line data; flags contamination; keeps records from bale to resin to film to pack that fit the chosen chain-of-custody model. Record-keeping is data engineering; the AI is in grading and quality prediction.",
 "Bale data and images, washing and extrusion line data, SSP and lab tests (IV, colour, acetaldehyde), production genealogy across chip, film and converting, EPR filings.",
 "rPET yield per tonne of bales; share of output reaching food-contact grade; contamination rejects; share of output with complete records.",
 f"rPET capacity 79,020 t × utilisation (35% rising to 75%) × 2% yield and grade gain × ₹100/kg = <b>{cr(b['uc3']*0.75,1)} a year</b> at 75% utilisation (range {cr(lo['uc3']*0.65,1)} to {cr(hi['uc3']*0.85,1)}), net of what existing AI segregation already delivers. The commercial value of records for customers is not counted.",
 "₹3.5 crore over three years.", "UFlex already reports AI-enabled segregation; HUL's Tinsukia Lighthouse (January 2025) cut sustainable-packaging trial time by 84%.",
 "Evidence standards still settling (EU methodology act expected end-2026); food-contact approvals; feedstock market.",
 flow([("Sense", "Bale images and samples, line and lab data"), ("Model", "Bale grading; yield and grade prediction"), ("Record", "Bale-to-pack records for the chosen chain-of-custody model"), ("Use", "Buying, process settings, customer and EPR records"), ("Measure", "Yield, food-grade share, record coverage")], "UC3 data flow")))
S.append(uc_card("UC4 · One-off · Stage 1", "New-capacity ramp-up",
 "Project leadership for Dharwad BOPP and Egypt aseptic",
 "Dharwad BOPP is due in FY27–28 and can be instrumented from commissioning. Egypt aseptic is already in commercial trials, with first-year utilisation expected around 30%, so support there is a retrofit. Ramps are also limited by demand, which AI does not change.",
 "Captures start-up, grade-qualification and first-time-right data from day one at Dharwad; applies UC1's cause models to ramp-up losses; supports laminate-quality learning in Egypt.",
 "Commissioning and line data, qualification trials, quality records.",
 "Months to target utilisation; first-pass yield on new grades; qualification trials per grade.",
 f"Half of management's guided ₹500 crore EBITDA (the Dharwad and Egypt share) ÷ 12 × 1 month earlier × 40% attributed to AI = <b>{cr(b['uc4'],1)}</b> one-off, spread over the ramp (range {cr(lo['uc4'],1)} to {cr(hi['uc4'],1)}).",
 "₹2 crore.", "New lines are the cheapest place to build in data capture; no published ramp-up benchmark was found.",
 "Commissioning priorities; OEM data access during warranty; demand.",
 flow([("Instrument", "Data capture from commissioning"), ("Learn", "Start-up and grade-qualification models"), ("Advise", "Settings for first-time-right"), ("Act", "Commissioning team applies"), ("Measure", "Months to target; first-pass yield")], "UC4 data flow")))
S.append(uc_card("UC5 · One-off cash · Stage 1", "Planning, procurement and inventory",
 "Group finance with supply-chain leadership",
 "Inventories were ₹2,408 crore at 31 March 2026, about 100 days of cost of goods sold across nine countries, while PTA, MEG and polypropylene swing sharply. Lamination cure time and grade campaigning also hold stock.",
 "Forecasts demand by grade, market and customer; sets inventory norms by item and plant; gives buyers price-risk signals; flags slow-moving stock and cure-time bottlenecks.",
 "ERP sales, stock, purchases and order book; production plans; supplier lead times; public polymer price series.",
 "Inventory days (not crore, since inventory grows with revenue); forecast accuracy; on-time-in-full.",
 f"5 days released × 50% attributed to AI = <b>{cr(b['wc'])}</b> one-off cash (range {cr(lo['wc'])} to {cr(hi['wc'])}). Interest saved is not counted as benefit. In a supply disruption UFlex may choose to hold more stock; this lever is a choice, not a forecast.",
 "₹3.5 crore build; a planning-engine licence from year 2.", "Multi-Color (labels) reports forecast accuracy up 50% (vendor case study).",
 "ERP data quality across countries; parallel spreadsheets.",
 flow([("Data", "ERP sales, stock, purchases, order book"), ("Model", "Demand, inventory norms, price risk"), ("Plan", "S&OP and buyer workbench"), ("Act", "Planners and buyers decide"), ("Measure", "Inventory days, OTIF, cash")], "UC5 data flow")))
S.append(uc_card("UC6 · Recurring · After Gate 2", "Gravure make-ready and colour",
 "Flexible packaging operations leadership (Noida, Jammu)",
 "Register control and 100% print inspection are usually closed-loop already. The remaining losses are make-ready and colour approval, ink viscosity drift, reuse of returned inks, solvent use and recovery, and adhesive coat weight and cure in lamination.",
 "Recommends press and ink settings from job history, cylinder engraving data and inline spectral colour measurement; predicts viscosity drift; supports colour formulation and returned-ink reuse in UFlex's own ink kitchen.",
 "Press data, cylinder engraving records, spectral colour data, ink formulation and viscosity, solvent and lamination data, job tickets.",
 "Make-ready waste metres per job; colour approval at first pull; solvent use per job; lamination rework.",
 f"Flexible-packaging output (about 78,700 t a year) × 0.4% waste removed × ₹170/kg × 80% value lost = <b>{cr(b['uc6'],1)} a year</b> (range {cr(lo['uc6'],1)} to {cr(hi['uc6'],1)}).",
 "₹2.5 crore after Gate 2.", "Gravure 100% inspection at PPL cut print-quality complaints 50% (vendor case study).",
 "Short runs and many job types.",
 flow([("Sense", "Press, spectral colour, viscosity, cylinder data"), ("Model", "Make-ready and colour settings"), ("Advise", "Settings per job; ink reuse"), ("Act", "Press crew and ink kitchen apply"), ("Measure", "Waste metres, first-pull approvals")], "UC6 data flow")))
S.append("<h3>Sized in the sprint</h3>" + T(["Use case", "What it would do", "Why it is not in the case yet"], [
 ["Aseptic laminate integrity", "Foil pinholes, bond strength and longitudinal strip quality; carton print and crease; later, filling-machine uptime at customer sites as a service", "Food-safety-critical and part of the main growth engine; needs Sanand and Egypt quality data. Candidate for Stage 1 if data allows."],
 ["Metalliser and coating quality", "Optical density and barrier consistency (soft sensors against lab OTR and WVTR), pinholes, metal adhesion, evaporator boat life, aluminium wire use, pump-down cycle, oxygen feed for AlOx", "Metallised capacity is 238,600 MTPA; needs metalliser and coater data to size."],
 ["Chip-plant process control", "IV, DEG and carboxyl end groups; SSP and acetaldehyde for bottle-grade chips; heat-transfer energy", "A mature application of advanced process control; size from Panipat and Egypt data."],
 ["Predictive maintenance", "TDO chains and clips, extruders, vacuum pumps, presses", "Repair and maintenance spend not disclosed; break downtime matters most when lines are sold out."],
 ["WPP bags (Mexico)", "Loom and lamination quality, print defects", "Plant commissioned July 2026; size once running data exists."],
 ["AI-led product development", "Recyclable mono-material structures, faster grade development (Kunlene cut R&D lead time 45%)", "Builds on UFlex's own reported work; size with R&D."],
 ["AI in UFlex machines", "Predictive maintenance as a product feature, tested on UFlex's own Ceruflex presses; EU Machinery Regulation readiness", "Product and regulatory decisions first."],
]) + "</section>")

S.append("""<section><h2 id="enterprise"><span class="n">7</span>Enterprise AI</h2>
<div class="col"><p>Not every gain is on the plant floor. These enterprise uses need no plant data, can start within 90 days, and are sized in the sprint.</p></div>""" + T(["Use", "What it would do", "Why it matters for UFlex"], [
 ["Cash and FX forecasting", "Rolling cash forecasts by entity; FX exposure and hedge timing across nine currencies", "FX losses in Nigeria, Egypt and Mexico drove exceptional items of ₹871 crore in FY24 and ₹178 crore in FY25"],
 ["Procurement and contracts", "Supplier and contract terms extraction; price-index clauses; spend analytics", "Polymer, chemicals and energy are the largest spend lines"],
 ["EPR and sustainability reporting", "Automate EPR filings, recycled-content records and BRSR data collection", "Rising PWM targets with ₹5,000 a tonne compensation for shortfalls"],
 ["Customer service and specifications", "Faster answers to specification, compliance and order questions for 5,000+ customers", "Speeds responses without changing commercial terms"],
 ["Workforce GenAI with guardrails", "Approved assistants for office staff; usage policy; data controls", "Builds on the AIM-AIA programme; prevents unmanaged use"],
]) + "</section>")

S.append(f"""<section><h2 id="architecture"><span class="n">8</span>Architecture</h2>
<div class="col"><p>One reference architecture serves every use case. Plant and enterprise sources feed an edge layer at each site and a governed group data fabric. AI services run on top, and decisions flow back to shift leads, planners, finance and customers. Security and governance cut across every layer.</p></div>
<figure><div class="scroll">{ref_arch()}</div><figcaption>Reference architecture. The current ERP, historians and OEM data feeds are confirmed in the sprint.</figcaption></figure>
{T(["Layer", "Design decisions", "Build or buy"], [
 ["Plant edge", "A historian and edge compute at each site, reusing OEM and inspection-vendor feeds. Read-only from OT. Models that act within seconds run on site.", "Buy and configure"],
 ["Data fabric", "One data model (site, line, grade, order, roll) with records from resin to pack. Named data owners and quality rules. Cross-border data flows reviewed per country.", "Buy the platform; the data model is UFlex's own"],
 ["AI services", "Cause and early-warning models, optimisation, recycling quality, demand, inventory, cash and FX models; one registry; MLOps with monitoring and retraining.", "Build with partners; buy planning engines"],
 ["Applications", "Advisories inside existing line screens; planning and slitting plans; recycled-content records; a value ledger owned by group finance.", "Mix"],
 ["Security and governance", "OT segmentation and vendor remote-access control (IEC 62443); CERT-In incident reporting and log retention; an AI inventory with risk tier and human-oversight rule for each system.", "Policy built; tools bought"],
])}
<div class="col"><h3>Partners and funding</h3><p>Vision, historian and planning engines come from established vendors; integration and model work from a partner selected by UFlex; the data model, process knowledge and playbook remain UFlex's. About 60% of build cost is likely to be capitalisable (hardware, historians, sensors) under Ind AS 16 and 38, with configuration and services expensed; group finance confirms the split.</p></div></section>""")

S.append(f"""<section><h2 id="roi"><span class="n">9</span>Value and ROI</h2>
<div class="col"><p><b>Method.</b> Recurring benefit from the plant and recycling use cases is kept apart from two one-off items, the ramp-up gain and the inventory release (half of which we attribute to AI). Interest on released cash is never counted. Plant value is built on tonnes, and each value base matches its use case's scope. Costs include 25% contingency, internal plant time, licences, sensors, travel and FX, and they vary by scenario: the low case assumes a 25% overrun. We show pre-tax cash, with all build cost charged when spent, and an EBITDA view that excludes capitalisable build.</p></div>
<figure><div class="scroll">{value_chart()}</div><figcaption>Recurring benefit at full rate (UC3 at 100% plant utilisation). Year 5 in the base case reaches {cr(b['y5gross'])} because coverage and recycling utilisation are still ramping.</figcaption></figure>
<h3>Five years, base case (₹ crore)</h3>
{T(["", "Stage 1", "Year 2", "Year 3", "Year 4", "Year 5", "Total"], [
 ["Recurring benefit"] + [f"{x:,.1f}" for x in b["rec"]] + [f"{sum(b['rec']):,.1f}"],
 ["Ramp-up gain (one-off)"] + [f"{x:,.1f}" for x in b["ramp"]] + [f"{sum(b['ramp']):,.1f}"],
 ["Programme cost"] + [f"({x:,.1f})" for x in b["cost"]] + [f"({sum(b['cost']):,.1f})"],
 ["<b>Net pre-tax cash</b>"] + [f"<b>{x:,.1f}</b>" for x in b["net"]] + [f"<b>{sum(b['net']):,.1f}</b>"],
 ["EBITDA effect (capitalisable build excluded)"] + [f"{x:,.1f}" for x in b["ebitda"]] + [f"{sum(b['ebitda']):,.1f}"],
 ["Inventory release, AI share (cash)"] + [f"{x:,.1f}" for x in b["wcy"]] + [f"{sum(b['wcy']):,.1f}"],
], num=(1, 2, 3, 4, 5, 6))}
<figure><div class="scroll">{five_year_chart()}</div><figcaption>Base case. Dark bars: recurring benefit; light: ramp-up gain; red: programme cost. Years 2–5 apply only if Gate 2 is passed.</figcaption></figure>
<h3>Scenarios</h3>
{T(["Measure", "Low", "Base", "High"], [
 ["Stage 1 commitment (₹ cr)", f"{lo['stage1']:.1f}", f"{b['stage1']:.1f}", f"{hi['stage1']:.1f}"],
 ["Year-5 recurring benefit, gross (₹ cr)", f"{lo['y5gross']:.1f}", f"{b['y5gross']:.1f}", f"{hi['y5gross']:.1f}"],
 ["Year-5 net of programme running cost (₹ cr)", f"{lo['y5net']:.1f}", f"{b['y5net']:.1f}", f"{hi['y5net']:.1f}"],
 ["5-year NPV, pre-tax cash (₹ cr)", f"{lo['npv']:.0f}", f"{b['npv']:.0f}", f"{hi['npv']:.0f}"],
 ["NPV including steady state after year 5 (₹ cr)", f"{lo['npv_tv']:.0f}", f"{b['npv_tv']:.0f}", f"{hi['npv_tv']:.0f}"],
 ["NPV including the inventory release (₹ cr)", f"{lo['npv_wc']:.0f}", f"{b['npv_wc']:.0f}", f"{hi['npv_wc']:.0f}"],
], num=(1, 2, 3))}
<div class="callout"><b>Gate 2: the test the pilot must pass.</b> The film-line use case is tested on its own benefits and its own costs: its build, sensors, half of the data foundation, contingency, running cost and plant time. In the base case it breaks even over five years if the pilot shows about {pct(b['uc1_scrap'],2)} of film production removed as scrap and {pct(b['uc1_energy'])} energy saved per good kilogram, which is {b['uc1_be']:.1f} times our base rates. Below that line UFlex keeps the enterprise use cases and the data foundation, and does not roll out the film-line work.</div>
<h3>What moves the answer</h3>
<figure><div class="scroll">{tornado_chart()}</div><figcaption>The rPET yield gain, programme cost, and the scrap and energy rates matter most. These are the numbers the sprint pins down first.</figcaption></figure>
<div class="col"><h3>A top-down check</h3><p>At year 5 the base case's recurring benefit equals about {b['y5gross']/9616.3*100:.2f}% of FY26 materials cost plus power and fuel ({cr(b['y5gross'])} against ₹9,616 crore). That is modest against the whole-site results reported by Lighthouse factories, which is consistent with a conservative case that leaves maintenance, metallising, chip plants, aseptic and enterprise AI unsized.</p></div></section>""")

S.append(f"""<section><h2 id="roadmap"><span class="n">10</span>Roadmap and gates</h2>
<figure><div class="scroll">{gantt()}</div><figcaption>Bars show workstreams; diamonds are decision gates. Months from the start of the sprint.</figcaption></figure>
{T(["Gate", "When", "Go if", "Stop or rethink if"], [
 ["1 · After the sprint", "Week 2", "Line and problem chosen; the data request agreed; existing tools listed", "No line has the data needed: fix the data foundation first"],
 ["2 · After six months of measurement", "About month 10", f"The pilot line, against its control and normalised for grade mix, reaches about {pct(b['uc1_scrap'],2)} scrap removed and {pct(b['uc1_energy'])} energy per good kg; group finance signs the result", "Below the line after one retraining cycle: keep UC3, UC4, UC5 and the data foundation; do not roll out UC1"],
 ["3 · Year-1 value review", "About month 18", "India sites tracking the measured rates in the value ledger", "Not tracking: re-plan before committing to overseas sites"],
])}
<div class="col"><h3>The readiness sprint (two weeks)</h3>
<p>Days 1–3 <b>Immerse</b>: a walk-through of the line UFlex nominates, interviews, and a list of the AI, automation and line-supplier digital services already installed. Days 4–7 <b>Audit</b>: data availability and quality for the chosen problem, and the IT and OT landscape. Days 8–11 <b>Prioritise</b>: rebuild the model on UFlex numbers and agree the Gate 2 test and measurement design with group finance. Days 12–14 <b>Decide</b>: a working session on the pilot scope.</p></div></section>""")

S.append(f"""<section><h2 id="operating"><span class="n">11</span>Operating model and governance</h2>
<div class="col"><p>A small central team owns the data model, the platform and the playbook. Plants own adoption and results; partners supply engines and integration capacity. The executive sponsor and use-case owners are agreed with UFlex's leadership.</p></div>
{T(["Role", "Responsibility"], [
 ["Executive sponsor", "Owns the ambition and chairs the gates"],
 ["Group finance", "Signs off baselines, the attribution rule and Gate 2; owns the value ledger"],
 ["Use-case owners (film technical and operations, sustainability and recycling, flexible packaging, supply chain, new projects)", "Own results at line and plant level"],
 ["Central AI and data team (3 FTE in Stage 1, about 10 by year 3)", "Data model, platform, MLOps, models with partners, the replication playbook; builds on the AIM-AIA cohort"],
 ["Plant champions", "A process engineer at each site in the roll-out: adoption, operator feedback, local baselines"],
])}
<div class="col"><h3>Governance</h3><ul>
 <li><b>AI policy and inventory</b>, aligned with ISO/IEC 42001 and the NIST AI Risk Management Framework, recording each system's purpose, data, owner, risk tier and human-oversight rule.</li>
 <li><b>Human oversight</b>: advisory by default; closed-loop control only after a documented performance record, with operator override.</li>
 <li><b>OT security</b> (IEC 62443): read-only exports, no remote vendor access without UFlex control, segmentation before any model connects.</li>
 <li><b>Cross-border data</b>: data flows and vendor licensing reviewed country by country with UFlex counsel.</li>
 <li><b>Change</b>: operator training and communication in local languages at each site, with plant champions.</li>
</ul></div>
<h3>Regulation that applies (summary, not legal advice)</h3>
{T(["Instrument", "Status and dates", "What it means here"], [
 ["India DPDP Act 2023 and Rules 2025", "Rules notified November 2025; core duties from 13 May 2027", "Low for plant AI; applies to HR, customer-contact and CRM data"],
 ["CERT-In Directions (2022)", "In force", "6-hour incident reporting; 180-day log retention in India; covers connected IIoT and AI platforms"],
 ["MeitY India AI Governance Guidelines", "Released November 2025; voluntary", "A basis for UFlex's AI policy"],
 ["EU Machinery Regulation (EU) 2023/1230", "Applies from 20 January 2027", "Machines with machine-learning safety functions need a Notified Body"],
 ["EU AI Act", "High-risk obligations phased from late 2027", "In-plant process, quality and maintenance AI is generally not high-risk"],
 ["India PWM (Amendment) Rules 2026; EU PPWR", "In force March 2026; PPWR applies from August 2026, targets from 2030", "Drives the records in UC3"],
])}</section>""")

S.append("""<section><h2 id="next"><span class="n">12</span>Risks and next step</h2>""" + T(["Risk", "Likelihood", "Mitigation"], [
 ["Line data held in OEM systems or under warranty terms", "High", "List installed tools in the sprint; choose the pilot line for data access; negotiate OEM data feeds"],
 ["Results confounded by price, mix and grade", "High", "Per-kg, per-grade measurement; control line; historian pre-period; finance-signed attribution"],
 ["Pilot falls below its break-even", "Medium", "Gate 2 stops the roll-out; enterprise use cases and data foundation continue"],
 ["Integration cost higher across OEMs and vintages", "Medium", "Cost by line type in the sprint; 25% contingency; replicate first on similar control systems"],
 ["Operators do not trust advisories", "Medium", "Advisory mode with reasons shown; feedback logged; plant champions"],
 ["OT cyber exposure", "Medium", "Read-only exports; IEC 62443 segmentation before integration"],
]) + """<div class="col"><h3>Next step</h3>
<p>We propose a two-week readiness sprint on one line and one problem that UFlex nominates, preceded by a short working session with film technical leadership to choose them. The sprint has a fixed fee. UFlex owns the deliverables, with no exclusivity and no obligation to continue. Pilot advisory fees are capped, with part held back by UFlex until Gate 2 results are signed off.</p>
<h3>What we would need from UFlex</h3><ul>
 <li>Access to the chosen line, its engineers, and its control, inspection, lab and energy data (read-only exports)</li>
 <li>The list of installed line-supplier digital services and inspection systems</li>
 <li>ERP extracts for inventory, sales and purchases (24 months)</li>
 <li>Recycling line data and customer requests for recycled-content records</li>
 <li>Conversations with 6–8 leaders across films, recycling, packaging, finance, supply chain and IT</li>
</ul></div></section>""")

S.append("""<section><h2 id="sources"><span class="n">A</span>Sources</h2>
<div class="col"><p>UFlex figures are from UFlex's own results, presentations and annual reports, converted from published ₹ lakh or ₹ million values without other adjustment. Peer results carry their evidence type.</p></div>
<ul class="src">
 <li>UFlex, Q4 FY26 investor presentation: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q4FY26_Presentation.pdf</li>
 <li>UFlex, consolidated results FY26: https://www.uflexltd.com/pdf/financials/Consolidated/UFLEX_NSEBSE_CONS_RESULTS_31MAR2026.pdf</li>
 <li>UFlex, Q1 FY27 investor presentation: https://www.uflexltd.com/pdf/QER/2026-27/UFlex_Q1FY27_Presentation.pdf</li>
 <li>UFlex, investor presentation 10 Sep 2026: https://www.uflexltd.com/pdf/IR/Investor_Presentation_10Sep_2026.pdf</li>
 <li>UFlex, Annual Reports FY2024-25 and FY2025-26: https://www.uflexltd.com/pdf/financials/annual-reports/UFLEX-AR-2025-26.pdf</li>
 <li>UFlex, Q2 FY26 call transcript: https://www.uflexltd.com/pdf/QER/2025-26/UFlex_Q2FY26_Transcript.pdf</li>
 <li>Polyplex, Q4 FY26 investor presentation: https://nsearchives.nseindia.com/corporate/POLYPLEX_27052026174118_PCL_Investor_Presentation_Q4_2025-26_signed.pdf</li>
 <li>Cosmo First, Q4 FY26 call transcript: https://nsearchives.nseindia.com/corporate/COSMOFILMS_28052026143240_Intimation_Transcript.pdf</li>
 <li>World Economic Forum, Global Lighthouse Network, 15 Jan 2026: https://www.weforum.org/press/2026/01/global-lighthouse-network-recognizes-23-new-sites-launches-ai-platform-for-industrial-transformation/</li>
 <li>World Economic Forum, Global Lighthouse Network, Jan 2025 (HUL Tinsukia): https://www.weforum.org/press/2025/01/global-lighthouse-network-2025-world-economic-forum-recognizes-companies-transforming-manufacturing-through-innovation/</li>
 <li>ACG, Shirwal Lighthouse: https://www.acg-world.com/news/acg-shirwal-facility-joins-world-economic-forum-global-lighthouse-network</li>
 <li>Mondi, "Operationalizing advanced industrial data projects" (conference presentation, 2022)</li>
 <li>Klöckner Pentaplast trim optimisation (Greycon case study): https://www.casestudies.com/company/greycon/case-study/klockner-pentaplast-customer-case-study</li>
 <li>Multi-Color Corporation demand planning (Blue Yonder case study): https://www.casestudies.com/company/blue-yonder-group/case-study/228c-multi-color-label-corporation-streamlines-demand-management-with-blue-yonder</li>
 <li>PPL gravure inspection (PFFC): https://www.pffc-online.com/news/545-paper-leading-converter-india</li>
 <li>EU Packaging and Packaging Waste Regulation (EU) 2025/40: https://eur-lex.europa.eu/eli/reg/2025/40/oj/eng</li>
 <li>EU Machinery Regulation overview (UL): https://www.ul.com/resources/navigating-new-eu-machinery-regulation-eu-20231230</li>
 <li>DPDP Rules 2025 (JSA summary): https://www.jsalaw.com/wp-content/uploads/2025/11/JSA-Prism-InfoTech-November-2025-DPDP-Rules.Final_.pdf</li>
 <li>MeitY AI Governance Guidelines: https://indianinfrastructure.com/2025/11/07/meity-unveils-india-ai-governance-guidelines-under-indiaai-mission/</li>
</ul>
<footer>PLUMB Advisory · Prepared from public information only; not reviewed by UFlex. Figures are illustrative until re-based on UFlex data in the readiness sprint. Not legal advice.</footer></section></div>""")

open(OUT, "w").write("\n".join(S))
print(OUT, sum(len(x) for x in S))
