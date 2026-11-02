"""UFlex AI business case — formula-driven workbook (every result is an Excel formula)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

OUT = "/home/claude/plumb/runs/uflex/2026-11-03/UFlex-AI-business-case.xlsx"
F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF")
BLACK = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
GREEN = Font(name=F, size=10, color="008000")
H1 = Font(name=F, size=14, bold=True, color="051C2C")
H2 = Font(name=F, size=11, bold=True, color="051C2C")
HDR = Font(name=F, size=10, bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="051C2C")
YEL = PatternFill("solid", fgColor="FFFF00")
PANEL = PatternFill("solid", fgColor="F3F5F8")
thin = Side(style="thin", color="D7DCE3")
CR = '#,##0.0;(#,##0.0);-'
PCT = '0.0%;(0.0%);-'
X = '0.00"x"'

wb = Workbook()

def header(ws, row, labels, col=1):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=l)
        c.font, c.fill = HDR, HFILL
        c.alignment = Alignment(horizontal="center" if i else "left", vertical="center", wrap_text=True)

def widths(ws, ws_w):
    for k, v in ws_w.items():
        ws.column_dimensions[k].width = v

# ------------------------------------------------------------------ README
r = wb.active
r.title = "README"
rows = [
    ("UFlex Limited — AI business case (outside-in, illustrative)", H1),
    ("PLUMB Advisory · prepared 3 Nov 2026 · all amounts ₹ crore unless stated", BLACK),
    ("", BLACK),
    ("What this is", H2),
    ("A conservative, assumption-transparent model of the AI use cases in the strategy document. It is built only on UFlex's published FY26 figures plus stated assumptions; it is not a forecast and has not been validated with UFlex data.", BLACK),
    ("", BLACK),
    ("How to use it", H2),
    ("1. Pick a scenario on the Assumptions sheet (cell C4: 1 = Low, 2 = Base, 3 = High). Every result updates.", BLACK),
    ("2. Blue text = an input you can change. Yellow fill = a key assumption to replace with UFlex plant data in the readiness sprint. Black = formula. Green = link to another sheet.", BLACK),
    ("3. Baseline holds the FY26 actuals with their sources. Do not overwrite them unless restating.", BLACK),
    ("", BLACK),
    ("Conservatism rules (Cloudster ROI method)", H2),
    ("• Benefit rates sit at the low end of published ranges; the best published results (WEF Lighthouses) are shown only for context.", BLACK),
    ("• All one-off build and integration cost is charged in the year incurred; run cost and the AI team are charged every year.", BLACK),
    ("• Benefits that are hard to attribute are excluded from the case: predictive maintenance (downtime avoided), plant copilot, recycling feedstock quality, EPR penalty avoidance, pricing and mix. They are listed as upside.", BLACK),
    ("• Value is measured on recurring cost lines (flows), never on balance-sheet or valuation figures. The one exception, inventory, is a one-off cash release plus its annual carrying cost — shown separately.", BLACK),
    ("• Throughput gains are not valued: film utilisation was 77.5% in FY26 in an oversupplied market, so extra output is not extra profit.", BLACK),
    ("", BLACK),
    ("What must be replaced with UFlex data before any decision", H2),
    ("Scrap/off-spec rate and regrind recovery by line; kWh/kg by line and grade; energy split by plant; converting waste by process; inventory by category and plant; real cost quotes from vendors and partners.", BLACK),
]
for i, (t, f) in enumerate(rows, 1):
    c = r.cell(row=i, column=1, value=t); c.font = f
    c.alignment = Alignment(wrap_text=True, vertical="top")
r.column_dimensions["A"].width = 120

# ------------------------------------------------------------------ Baseline (FY26 actuals)
b = wb.create_sheet("Baseline")
b["A1"] = "FY26 baseline — UFlex consolidated (₹ crore unless stated)"; b["A1"].font = H1
header(b, 3, ["Item", "Value", "Unit", "Source"])
base = [
    ("rev", "Revenue from operations", 15400.52, "₹ cr", "Consolidated results FY26 (31 Mar 2026), statutory; ₹ lakh ÷ 100"),
    ("mat", "Cost of materials consumed", 8877.00, "₹ cr", "Consolidated results FY26, statutory"),
    ("pf", "Power & fuel", 739.33, "₹ cr", "Consolidated results FY26 / Q4FY26 earnings release"),
    ("emp", "Employee benefit expense", 1556.90, "₹ cr", "Consolidated results FY26, statutory"),
    ("oox", "Other operating expenses (management definition)", 2171.4, "₹ cr", "Q4FY26 earnings release (statutory 'other expenses' FY26 not legible in the filed scan; management figure used)"),
    ("ebitda", "Reported EBITDA", 1983.6, "₹ cr", "Q4FY26 investor presentation, slide 21 (Rs 19,836 mn)"),
    ("inv", "Inventories, 31 Mar 2026", 2408.3, "₹ cr", "Q4FY26 investor presentation, slide 22 (Rs 24,083 mn)"),
    ("turn", "Inventory turnover", 3.67, "x", "Q4FY26 investor presentation, slide 28"),
    ("nd", "Net debt, 31 Mar 2026", 8621.8, "₹ cr", "Q4FY26 investor presentation, slide 26 (Rs 86,218 mn)"),
    ("kd", "Blended cost of debt", 0.085, "%", "Q1FY27 earnings release: 'Blended cost of debt: 8.5%'"),
    ("films", "Packaging films share of revenue", 0.586, "%", "Q4FY26 investor presentation, slides 24–25"),
    ("pack", "Packaging (flexible, aseptic, holography) share of revenue", 0.327, "%", "Q4FY26 investor presentation, slides 24–25"),
    ("prod", "Packaging film production", 492779, "MT", "Q4FY26 investor presentation, slide 10"),
    ("util", "Packaging film capacity utilisation", 0.775, "%", "Q4FY26 investor presentation, slide 10"),
    ("trig", "CRISIL downgrade trigger, net debt / EBITDA", 3.25, "x", "CRISIL rating rationale, 6 Aug 2026 ('above 3.25 times on a sustained basis')"),
]
B = {}
for i, (k, lab, v, u, s) in enumerate(base, 4):
    b.cell(row=i, column=1, value=lab).font = BLACK
    c = b.cell(row=i, column=2, value=v); c.font = BLUE
    c.number_format = PCT if u == "%" else (X if u == "x" else ('#,##0' if u == "MT" else CR))
    b.cell(row=i, column=3, value=u).font = BLACK
    b.cell(row=i, column=4, value=s).font = BLACK
    B[k] = f"Baseline!$B${i}"
n = 4 + len(base)
b.cell(row=n + 1, column=1, value="Derived").font = H2
der = [
    ("Materials as % of revenue", f"={B['mat']}/{B['rev']}", PCT),
    ("Net debt / reported EBITDA", f"={B['nd']}/{B['ebitda']}", X),
    ("Inventory held per day of turnover (₹ cr)", f"={B['inv']}*{B['turn']}/365", CR),
    ("Implied days of inventory", f"=365/{B['turn']}", '0'),
]
for j, (lab, f, fmt) in enumerate(der, n + 2):
    b.cell(row=j, column=1, value=lab).font = BLACK
    c = b.cell(row=j, column=2, value=f); c.font = BLACK; c.number_format = fmt
B["perday"] = f"Baseline!$B${n + 4}"
B["lev"] = f"Baseline!$B${n + 3}"
widths(b, {"A": 52, "B": 14, "C": 8, "D": 95})

# ------------------------------------------------------------------ Assumptions
a = wb.create_sheet("Assumptions")
a["A1"] = "Assumptions — change the blue cells; yellow = replace with UFlex data in the sprint"; a["A1"].font = H1
a["A3"] = "Scenario selector"; a["A3"].font = H2
a["A4"] = "Scenario (1 = Low, 2 = Base, 3 = High)"; a["A4"].font = BOLD
a["C4"] = 2; a["C4"].font = BLUE; a["C4"].fill = YEL
a["D4"] = '=INDEX({"Low","Base","High"},C4)'; a["D4"].font = BOLD
header(a, 6, ["Assumption", "Use case", "Low", "Base", "High", "Active", "Unit", "Basis"])
assum = [
    # key, label, uc, low, base, high, unit, basis, key_assumption
    ("y_gain", "Net good-output gain on film lines (scrap + off-spec avoided)", "UC1", 0.003, 0.006, 0.010, "% of film materials",
     "Low end vs published results: ACG Shirwal defects −71%, Kunlene defects −31% (WEF Lighthouse, Jan 2026, site-wide programmes); Mondi Hilm rework & waste −50% vs 2018. UFlex scrap baseline unknown.", True),
    ("regrind", "Value recovered from scrap via regrind / resale", "UC1", 0.50, 0.40, 0.30, "% of material value",
     "Assumption: part of film scrap is reprocessed (UFlex runs PET resin and recycling plants), so only the unrecovered share is saved.", True),
    ("e_save", "Energy saving on addressable load", "UC2", 0.02, 0.03, 0.05, "%",
     "Low end vs ACG Shirwal energy −31% (WEF) and McKinsey Lighthouse average energy/water −25%. No public kWh/kg benchmark for film lines.", True),
    ("e_share", "Share of power & fuel in film, resin and aseptic lines (addressable)", "UC2", 0.70, 0.75, 0.80, "%",
     "Assumption: film extrusion/stretching, chip plants and aseptic lines dominate the energy bill. Replace with plant meter data.", True),
    ("inv_days", "Inventory days released (planning + procurement intelligence)", "UC3", 4, 7, 10, "days",
     "Assumption against ~100 days implied by 3.67x turnover (FY26). Multi-Color (labels) reports forecast accuracy +50% (vendor case study) — not used directly.", True),
    ("conv_gain", "Converting waste reduction (make-ready, colour, artwork errors)", "UC4", 0.002, 0.004, 0.007, "% of packaging materials",
     "Published converter waste benchmarks: printing 3–5%, lamination 1–2%, slitting <1% (Tesfahun 2026). Gravure 100% inspection: complaints −50% (AVT/PPL, vendor case study).", True),
    ("conv_rec", "Value recovered from converting waste", "UC4", 0.30, 0.20, 0.10, "% of material value", "Assumption: laminated waste has low recovery value.", False),
    ("disc", "Discount rate", "All", 0.14, 0.12, 0.10, "%", "Assumption: above the 8.5% blended cost of debt to reflect equity risk.", False),
]
A = {}
for i, (k, lab, uc, lo, ba, hi, u, basis, key) in enumerate(assum, 7):
    a.cell(row=i, column=1, value=lab).font = BLACK
    a.cell(row=i, column=2, value=uc).font = BLACK
    for j, v in enumerate((lo, ba, hi), 3):
        c = a.cell(row=i, column=j, value=v); c.font = BLUE
        c.number_format = '0' if u == "days" else '0.0%'
        if key: c.fill = YEL
    act = a.cell(row=i, column=6, value=f"=INDEX(C{i}:E{i},$C$4)"); act.font = BOLD
    act.number_format = '0' if u == "days" else '0.0%'
    a.cell(row=i, column=7, value=u).font = BLACK
    a.cell(row=i, column=8, value=basis).font = BLACK
    a.cell(row=i, column=8).alignment = Alignment(wrap_text=True, vertical="top")
    A[k] = f"Assumptions!$F${i}"

# ramp + costs
rr = 7 + len(assum) + 2
a.cell(row=rr, column=1, value="Benefit realised (share of full run-rate), by year").font = H2
header(a, rr + 1, ["Use case", "", "Year 1", "Year 2", "Year 3", "", "", "Basis"])
ramps = [("UC1", "Film-line yield and quality intelligence", 0.10, 0.45, 0.85, "Lighthouse site in year 1 (India BOPET/BOPP), 3 more film sites in year 2, remaining sites in year 3."),
         ("UC2", "Energy optimisation", 0.10, 0.45, 0.85, "Follows the same site sequence as UC1 (shared data foundation)."),
         ("UC3", "Planning, procurement and inventory intelligence", 0.50, 1.00, 1.00, "Enterprise-level (ERP and planning data); no plant sensors needed."),
         ("UC4", "Converting make-ready and artwork assurance", 0.40, 1.00, 1.00, "India flexible packaging plants (Noida, Jammu).")]
R = {}
for i, (uc, lab, y1, y2, y3, basis) in enumerate(ramps, rr + 2):
    a.cell(row=i, column=1, value=f"{uc} — {lab}").font = BLACK
    for j, v in enumerate((y1, y2, y3), 3):
        c = a.cell(row=i, column=j, value=v); c.font = BLUE; c.number_format = '0%'
    a.cell(row=i, column=8, value=basis).font = BLACK
    R[uc] = i

cr = rr + 2 + len(ramps) + 1
a.cell(row=cr, column=1, value="Costs (₹ crore) — assumptions pending vendor quotes").font = H2
header(a, cr + 1, ["Cost item", "Type", "Year 1", "Year 2", "Year 3", "", "", "Basis"])
costs = [
    ("Data foundation: plant historian/edge, governed data fabric, OT/IT security", "One-off", 6.0, 4.5, 4.5, "Lighthouse ₹6 cr; ~₹1.5 cr per additional site, 3 sites a year in years 2–3 (assumption)."),
    ("UC1 build: vision data integration, defect/root-cause models", "One-off", 3.0, 3.6, 3.6, "Lighthouse ₹3 cr; ₹1.2 cr per additional site (assumption)."),
    ("UC2 build: energy models and advisory loop", "One-off", 1.5, 1.8, 1.8, "Lighthouse ₹1.5 cr; ₹0.6 cr per additional site (assumption)."),
    ("UC3 build: demand sensing, inventory optimisation, procurement analytics", "One-off", 4.0, 1.0, 0.0, "Enterprise build on ERP data (assumption)."),
    ("UC4 build: print inspection analytics, artwork/label assurance", "One-off", 2.5, 0.5, 0.0, "Two converting plants (assumption)."),
    ("Readiness sprint and pilot advisory", "One-off", 2.0, 0.0, 0.0, "Sprint fee credited against the pilot (Cloudster offer); assumption."),
    ("Run: platform, licences, cloud/edge support", "Recurring", "=0.2*SUM(C{a}:C{b})", "=0.2*SUM(C{a}:D{b})", "=0.2*SUM(C{a}:E{b})", "20% a year of cumulative build (assumption)."),
    ("AI and data team (8–12 FTE, fully loaded)", "Recurring", 4.5, 5.0, 5.5, "~₹0.45 cr per FTE a year, fully loaded (assumption)."),
    ("Change management and training", "Recurring", 1.0, 1.0, 1.0, "Assumption."),
]
first = cr + 2
C = {}
for i, (lab, typ, y1, y2, y3, basis) in enumerate(costs, first):
    a.cell(row=i, column=1, value=lab).font = BLACK
    a.cell(row=i, column=2, value=typ).font = BLACK
    for j, v in enumerate((y1, y2, y3), 3):
        if isinstance(v, str):
            v = v.format(a=first, b=first + 5)
            c = a.cell(row=i, column=j, value=v); c.font = BLACK
        else:
            c = a.cell(row=i, column=j, value=v); c.font = BLUE; c.fill = YEL
        c.number_format = CR
    a.cell(row=i, column=8, value=basis).font = BLACK
last = first + len(costs) - 1
tot = last + 1
a.cell(row=tot, column=1, value="Total cost").font = BOLD
for j in (3, 4, 5):
    col = get_column_letter(j)
    c = a.cell(row=tot, column=j, value=f"=SUM({col}{first}:{col}{last})"); c.font = BOLD; c.number_format = CR
C["total"] = tot
widths(a, {"A": 62, "B": 10, "C": 10, "D": 10, "E": 10, "F": 10, "G": 18, "H": 110})

# ------------------------------------------------------------------ Use cases (run-rate)
u = wb.create_sheet("Use cases")
u["A1"] = "Annual benefit at full run-rate (₹ crore) — active scenario"; u["A1"].font = H1
u["A2"] = "=\"Scenario: \"&Assumptions!$D$4"; u["A2"].font = BOLD
header(u, 4, ["Use case", "Value base (₹ cr)", "Lever", "Annual benefit (₹ cr)", "P&L line", "Formula logic"])
ucs = [
    ("UC1 Film-line yield and quality intelligence", f"={B['mat']}*{B['films']}", f"={A['y_gain']}", f"=B5*C5*(1-{A['regrind']})", "Cost of materials (EBITDA)",
     "Film materials (materials × films revenue share) × net good-output gain × (1 − regrind recovery)"),
    ("UC2 Energy optimisation", f"={B['pf']}*{A['e_share']}", f"={A['e_save']}", "=B6*C6", "Power & fuel (EBITDA)",
     "Power & fuel × addressable share × saving"),
    ("UC3 Planning, procurement and inventory — carrying cost", f"={B['perday']}*{A['inv_days']}", f"={B['kd']}", "=B7*C7", "Finance cost (below EBITDA)",
     "Inventory per day of turnover × days released × blended cost of debt. The cash release itself is one-off (row 10)."),
    ("UC4 Converting make-ready and artwork assurance", f"={B['mat']}*{B['pack']}", f"={A['conv_gain']}", f"=B8*C8*(1-{A['conv_rec']})", "Cost of materials (EBITDA)",
     "Packaging materials (materials × packaging revenue share) × waste reduction × (1 − recovery)"),
]
for i, (lab, vb, lev, ben, line, logic) in enumerate(ucs, 5):
    u.cell(row=i, column=1, value=lab).font = BLACK
    c = u.cell(row=i, column=2, value=vb); c.font = GREEN; c.number_format = CR
    c = u.cell(row=i, column=3, value=lev); c.font = GREEN; c.number_format = '0.0%'
    c = u.cell(row=i, column=4, value=ben); c.font = BOLD; c.number_format = CR
    u.cell(row=i, column=5, value=line).font = BLACK
    u.cell(row=i, column=6, value=logic).font = BLACK
u["A9"] = "Total recurring benefit at run-rate"; u["A9"].font = BOLD
u["D9"] = "=SUM(D5:D8)"; u["D9"].font = BOLD; u["D9"].number_format = CR
u["A10"] = "UC3 one-off cash release from inventory (not P&L)"; u["A10"].font = BOLD
u["D10"] = "=B7"; u["D10"].font = BOLD; u["D10"].number_format = CR
u["A12"] = "What it means for the CFO"; u["A12"].font = H2
lines = [
    ("EBITDA uplift at run-rate (UC1 + UC2 + UC4)", "=D5+D6+D8", CR),
    ("as % of FY26 reported EBITDA", f"=D13/{B['ebitda']}", PCT),
    ("FY26 net debt / EBITDA", f"={B['lev']}", X),
    ("Pro forma net debt / EBITDA with run-rate EBITDA uplift and inventory cash release", f"=({B['nd']}-D10)/({B['ebitda']}+D13)", X),
    ("Improvement in leverage (turns)", "=D15-D16", X),
    ("Gap from FY26 leverage to CRISIL trigger (turns)", f"=D15-{B['trig']}", X),
    ("Share of that gap closed by the AI programme", "=IF(D18>0,D17/D18,0)", PCT),
]
for i, (lab, f, fmt) in enumerate(lines, 13):
    u.cell(row=i, column=1, value=lab).font = BLACK
    c = u.cell(row=i, column=4, value=f); c.font = BOLD; c.number_format = fmt
u["A21"] = "Upside not counted in the case (needs UFlex data to size)"; u["A21"].font = H2
ups = ["UC5 Predictive maintenance and changeover optimisation on film lines — downtime avoided; R&M spend not disclosed",
       "UC6 Sovereign plant copilot (multilingual SOPs, troubleshooting across 9 countries) — productivity, onboarding",
       "UC7 Recycling feedstock sorting and recycled-content traceability — rPET/rMLP yield, PWM 2026 and EU PPWR compliance, ₹5,000/t EPR compensation avoided",
       "UC8 Commercial: price/mix and quote intelligence — film pricing is set by supply and demand, so excluded",
       "UC9 Engineering: AI-enabled machines (predictive maintenance as a product) and EU Machinery Regulation readiness"]
for i, t in enumerate(ups, 22):
    u.cell(row=i, column=1, value="• " + t).font = BLACK
widths(u, {"A": 78, "B": 18, "C": 10, "D": 20, "E": 26, "F": 95})

# ------------------------------------------------------------------ Cash flow
cf = wb.create_sheet("Cash flow")
cf["A1"] = "Three-year cash flow (₹ crore) — active scenario"; cf["A1"].font = H1
cf["A2"] = "=\"Scenario: \"&Assumptions!$D$4"; cf["A2"].font = BOLD
header(cf, 4, ["Line", "Year 1", "Year 2", "Year 3", "Total"])
rows = []
ucrow = {"UC1": 5, "UC2": 6, "UC3": 7, "UC4": 8}
r0 = 5
for k, (uc, lab) in enumerate([("UC1", "UC1 benefit"), ("UC2", "UC2 benefit"), ("UC3", "UC3 carrying-cost benefit"), ("UC4", "UC4 benefit")]):
    i = r0 + k
    cf.cell(row=i, column=1, value=lab).font = BLACK
    for j, col in enumerate(("C", "D", "E"), 2):
        c = cf.cell(row=i, column=j, value=f"='Use cases'!$D${ucrow[uc]}*Assumptions!{col}{R[uc]}")
        c.font = GREEN; c.number_format = CR
i = r0 + 4
cf.cell(row=i, column=1, value="Inventory cash release (one-off, follows UC3 ramp)").font = BLACK
cf.cell(row=i, column=2, value=f"='Use cases'!$D$10*Assumptions!C{R['UC3']}").font = GREEN
cf.cell(row=i, column=3, value=f"='Use cases'!$D$10*(Assumptions!D{R['UC3']}-Assumptions!C{R['UC3']})").font = GREEN
cf.cell(row=i, column=4, value=f"='Use cases'!$D$10*(Assumptions!E{R['UC3']}-Assumptions!D{R['UC3']})").font = GREEN
for j in (2, 3, 4): cf.cell(row=i, column=j).number_format = CR
cf.cell(row=10, column=1, value="Total benefit and cash release").font = BOLD
cf.cell(row=11, column=1, value="Total cost").font = BLACK
cf.cell(row=12, column=1, value="Net cash flow").font = BOLD
cf.cell(row=13, column=1, value="Cumulative net cash flow").font = BLACK
cf.cell(row=14, column=1, value="Recurring benefit only (excl. inventory cash)").font = BLACK
cf.cell(row=15, column=1, value="Net recurring (excl. inventory cash)").font = BLACK
for j, col in enumerate(("B", "C", "D"), 2):
    acol = ("C", "D", "E")[j - 2]
    cf[f"{col}10"] = f"=SUM({col}5:{col}9)"
    cf[f"{col}11"] = f"=Assumptions!{acol}{C['total']}"
    cf[f"{col}12"] = f"={col}10-{col}11"
    cf[f"{col}13"] = f"=SUM($B$12:{col}12)"
    cf[f"{col}14"] = f"=SUM({col}5:{col}8)"
    cf[f"{col}15"] = f"={col}14-{col}11"
    for rr_ in range(10, 16):
        cf[f"{col}{rr_}"].number_format = CR
        cf[f"{col}{rr_}"].font = BOLD if rr_ in (10, 12) else BLACK
    cf[f"{col}11"].font = GREEN
for rr_ in list(range(5, 13)) + [14, 15]:
    if rr_ == 13: continue
    cf[f"E{rr_}"] = f"=SUM(B{rr_}:D{rr_})"; cf[f"E{rr_}"].number_format = CR; cf[f"E{rr_}"].font = BOLD
cf["A17"] = "Returns"; cf["A17"].font = H2
ret = [
    ("NPV of net cash flow, 3 years", f"=NPV({A['disc']},B12:D12)", CR),
    ("3-year return on cost (total benefit ÷ total cost)", "=IF(E11>0,E10/E11,0)", X),
    ("3-year return on cost, recurring benefit only", "=IF(E11>0,E14/E11,0)", X),
    ("Payback year (first year cumulative net cash ≥ 0)", '=IF(B13>=0,"Year 1",IF(C13>=0,"Year 2",IF(D13>=0,"Year 3","After year 3")))', "@"),
    ("Year-3 run-rate recurring benefit vs year-3 cost", "=IF(D11>0,D14/D11,0)", X),
]
for i, (lab, f, fmt) in enumerate(ret, 18):
    cf.cell(row=i, column=1, value=lab).font = BLACK
    c = cf.cell(row=i, column=2, value=f); c.font = BOLD; c.number_format = fmt
widths(cf, {"A": 58, "B": 14, "C": 14, "D": 14, "E": 14})

for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
    for row in ws.iter_rows():
        for c in row:
            if c.font and c.font.name != F:
                c.font = Font(name=F, size=c.font.size or 10, bold=c.font.bold, color=c.font.color)
wb.save(OUT)
print(OUT)
