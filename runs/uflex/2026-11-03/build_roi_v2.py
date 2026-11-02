"""UFlex AI business case v2 — five years, three value streams kept separate, tonnage-based, costs vary by scenario.
Every result cell is an Excel formula."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = "/home/claude/plumb/runs/uflex/2026-11-03/UFlex-AI-business-case-v2.xlsx"
F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF"); BLACK = Font(name=F, size=10); BOLD = Font(name=F, size=10, bold=True)
GREEN = Font(name=F, size=10, color="008000"); H1 = Font(name=F, size=14, bold=True, color="0E1B2B"); H2 = Font(name=F, size=11, bold=True, color="0E1B2B")
HDR = Font(name=F, size=10, bold=True, color="FFFFFF"); HFILL = PatternFill("solid", fgColor="0E1B2B"); YEL = PatternFill("solid", fgColor="FFFF00")
CR = '#,##0.0;(#,##0.0);-'; PCT = '0.0%;(0.0%);-'
YC = ["C", "D", "E", "F", "G"]  # Year 1..5 columns

wb = Workbook()

def header(ws, row, labels, col=1):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=l); c.font, c.fill = HDR, HFILL
        c.alignment = Alignment(horizontal="left" if i == 0 else "center", wrap_text=True)

# ------------------------------------------------------------------ README
r = wb.active; r.title = "README"
txt = [
 ("UFlex Limited — AI business case v2 (outside-in, illustrative)", H1),
 ("PLUMB Advisory · November 2026 · ₹ crore unless stated · revised after executive red-team review", BLACK), ("", BLACK),
 ("Three value streams, kept separate", H2),
 ("1. Recurring EBITDA from plant use cases, net of the programme's own running cost. This is the headline.", BLACK),
 ("2. One-off EBITDA pull-forward from a faster ramp-up of new capacity (UFlex's own guidance: four projects, about ₹500 cr EBITDA at decent utilisation).", BLACK),
 ("3. Working-capital release from planning and inventory. Shown separately with 50% attributed to AI; the rest belongs to policy and S&OP. Interest saved is a memo line, never counted as recurring benefit.", BLACK), ("", BLACK),
 ("How to use", H2),
 ("Pick a scenario on Assumptions!C4 (1 Low, 2 Base, 3 High). Low pairs low benefits with a 25% cost overrun; High pairs high benefits with 10% lower cost.", BLACK),
 ("Blue = input. Yellow = replace with UFlex plant data in the sprint. Black = formula. Green = link to another sheet.", BLACK), ("", BLACK),
 ("Conservatism rules", H2),
 ("• Plant benefits are built on tonnes (production × avoidable scrap × value lost per kg after reclaim or sale as seconds), not on revenue shares.", BLACK),
 ("• Value bases match scope: converting uses Noida and Jammu flexible-packaging volume only; energy uses the film-line share of power and fuel only.", BLACK),
 ("• Coverage is capped at 85% of film capacity: the Russia site is excluded pending a sanctions and data-transfer review.", BLACK),
 ("• Costs include 25% contingency, internal plant time, licences, sensors, travel and FX. All build cost is charged in the year incurred.", BLACK),
 ("• Not valued: extra throughput, predictive maintenance, plant copilot, metalliser and coating quality, chip-plant control, pricing, and the commercial value of recycled-content evidence. Each is sized in the sprint.", BLACK),
]
for i, (t, f) in enumerate(txt, 1):
    c = r.cell(row=i, column=1, value=t); c.font = f; c.alignment = Alignment(wrap_text=True, vertical="top")
r.column_dimensions["A"].width = 125

# ------------------------------------------------------------------ Baseline
b = wb.create_sheet("Baseline")
b["A1"] = "Baseline — UFlex published figures (₹ crore unless stated)"; b["A1"].font = H1
header(b, 3, ["Item", "Value", "Unit", "Source"])
base = [
 ("rev", "Revenue from operations, FY26", 15400.52, "₹ cr", "Consolidated results FY26 (31 Mar 2026)"),
 ("mat", "Cost of materials consumed, FY26", 8877.00, "₹ cr", "Consolidated results FY26"),
 ("pf", "Power and fuel, FY26", 739.33, "₹ cr", "Consolidated results FY26"),
 ("ebitda", "Reported EBITDA, FY26", 1983.6, "₹ cr", "Q4 FY26 investor presentation, slide 21"),
 ("prod", "Packaging film production, FY26", 492779, "t", "Q4 FY26 investor presentation, slide 10"),
 ("vol", "Total sales volume, FY26", 649789, "t", "Q4 FY26 investor presentation, slides 6 and 23"),
 ("flex", "Packaging volume, FY26", 151755, "t", "Q4 FY26 earnings release"),
 ("inv", "Inventories, 31 Mar 2026", 2408.3, "₹ cr", "Q4 FY26 investor presentation, slide 22"),
 ("turn", "Inventory turnover (cost of goods sold ÷ average inventory), FY26", 3.67, "x", "Q4 FY26 investor presentation, slide 28"),
 ("kd", "Blended cost of debt", 0.085, "%", "Q1 FY27 earnings release"),
 ("proj", "EBITDA from four new projects at decent utilisation (management guidance)", 500.0, "₹ cr / yr", "Q2 FY26 earnings call, 14 Nov 2025: 'around Rs. 3,000 odd crores within an EBITDA of about Rs. 500 crores'"),
 ("recy", "Revenue potential of recycling capacities (management)", 850.0, "₹ cr / yr", "Investor presentation 10 Sep 2026, slide 9: 'Rs. 8.5 bn+ revenue potential'"),
 ("util", "Film capacity utilisation, Q1 FY27", 0.854, "%", "Q1 FY27 investor presentation, slide 10"),
]
B = {}
for i, (k, lab, v, u, s) in enumerate(base, 4):
    b.cell(row=i, column=1, value=lab).font = BLACK
    c = b.cell(row=i, column=2, value=v); c.font = BLUE
    c.number_format = PCT if u == "%" else ('0.00"x"' if u == "x" else ('#,##0' if u == "t" else CR))
    b.cell(row=i, column=3, value=u).font = BLACK; b.cell(row=i, column=4, value=s).font = BLACK
    B[k] = f"Baseline!$B${i}"
n = 4 + len(base) + 1
b.cell(row=n, column=1, value="Derived").font = H2
der = [("Materials per tonne sold, all products (₹/kg) — cross-check for polymer cost", f"={B['mat']}*1E7/{B['vol']}/1000", '#,##0'),
       ("Inventory per day of cost of goods sold (₹ cr)", f"={B['inv']}*{B['turn']}/365", CR),
       ("Implied days of inventory (cost of goods sold basis)", f"=365/{B['turn']}", '0')]
for j, (lab, f, fmt) in enumerate(der, n + 1):
    b.cell(row=j, column=1, value=lab).font = BLACK
    c = b.cell(row=j, column=2, value=f); c.font = BLACK; c.number_format = fmt
B["perday"] = f"Baseline!$B${n + 2}"
for k, w in {"A": 70, "B": 14, "C": 10, "D": 100}.items(): b.column_dimensions[k].width = w

# ------------------------------------------------------------------ Assumptions
a = wb.create_sheet("Assumptions")
a["A1"] = "Assumptions — blue cells are inputs; yellow = replace with UFlex data in the sprint"; a["A1"].font = H1
a["A3"] = "Scenario selector"; a["A3"].font = H2
a["A4"] = "Scenario (1 = Low, 2 = Base, 3 = High)"; a["A4"].font = BOLD
a["C4"] = 2; a["C4"].font = BLUE; a["C4"].fill = YEL
a["D4"] = '=INDEX({"Low","Base","High"},C4)'; a["D4"].font = BOLD
header(a, 6, ["Assumption", "Use case", "Low", "Base", "High", "Active", "Unit", "Basis"])
assum = [
 ("cost_mult", "Cost multiplier (applied to every cost line)", "All", 1.25, 1.00, 0.90, "x", "Low case assumes a 25% overrun; high case a 10% saving.", False),
 ("disc", "Discount rate", "All", 0.14, 0.12, 0.10, "%", "Above the 8.5% blended cost of debt to reflect equity risk.", False),
 ("resin", "Polymer value of a kilogram of film (₹/kg)", "UC1, UC2", 105, 110, 115, "₹/kg", "Cross-check: FY26 materials ÷ total tonnes sold ≈ ₹137/kg across all products (Baseline). Replace with grade-level resin cost.", True),
 ("scrap", "Avoidable scrap and off-spec removed (share of film production)", "UC1", 0.003, 0.006, 0.010, "%", "Breaks, gels and specks, restart and changeover scrap, winding defects. Kunlene (BOPP) defects −31%, ACG −71% (WEF Lighthouses) are far higher.", True),
 ("loss", "Value lost per kg of scrap after reclaim or sale as seconds", "UC1, UC2", 0.25, 0.30, 0.35, "%", "Most edge trim and reclaim returns to the process; the loss is the virgin–reclaim value gap, reprocessing cost and downgrade discount. Replace with UFlex reclaim data.", True),
 ("e_share", "Film-line share of power and fuel", "UC1", 0.55, 0.55, 0.55, "%", "Assumption: excludes chip, aseptic, converting and utilities outside film lines. Replace with plant meter data.", True),
 ("e_save", "Energy saved per good kg on film lines", "UC1", 0.01, 0.02, 0.03, "%", "Fewer breaks and restarts and steadier operation; well below ACG Shirwal −31% (site-wide).", True),
 ("trim", "Slitting trim and changeover scrap removed (share of film production)", "UC2", 0.001, 0.002, 0.004, "%", "Deckle and sequence optimisation; Klöckner Pentaplast reports −3% waste with trim optimisation (vendor case study).", True),
 ("recy_gain", "Yield and grade gain on recycling revenue", "UC3", 0.0075, 0.015, 0.025, "%", "AI sorting and quality control on rPET and rMLP lines (IV, colour, contamination).", True),
 ("conv_cost", "Material value of a kilogram of converted laminate (₹/kg)", "UC6", 170, 170, 170, "₹/kg", "Assumption: film, foil, ink and adhesive. Replace with job costing.", True),
 ("conv_gain", "Converting waste removed (share of packaging volume)", "UC6", 0.002, 0.004, 0.007, "%", "Published converter waste: printing 3–5%, lamination 1–2%, slitting under 1% (Tesfahun 2026).", True),
 ("conv_loss", "Value lost per kg of converting waste", "UC6", 0.80, 0.80, 0.80, "%", "Laminated waste has little recovery value.", False),
 ("months", "Months earlier to target utilisation on new capacity", "UC4", 0.5, 1.0, 2.0, "months", "Instrumenting Dharwad BOPP and Egypt aseptic from day one; first-time-right grades.", True),
 ("attr_ramp", "Share of the ramp-up gain attributed to AI", "UC4", 0.5, 0.5, 0.5, "%", "The rest is engineering, commissioning and commercial effort.", False),
 ("days", "Inventory days released", "UC5", 3, 5, 8, "days", "Against ~100 days of cost of goods sold. A policy and S&OP decision as much as an analytics one.", True),
 ("attr_wc", "Share of the working-capital release attributed to AI", "UC5", 0.5, 0.5, 0.5, "%", "The rest belongs to inventory policy and supplier terms.", False),
]
A = {}
for i, (k, lab, uc, lo, ba, hi, u, basis, key) in enumerate(assum, 7):
    a.cell(row=i, column=1, value=lab).font = BLACK; a.cell(row=i, column=2, value=uc).font = BLACK
    fmt = {"%": '0.0%', "x": '0.00"x"', "₹/kg": '#,##0', "months": '0.0', "days": '0'}[u]
    for j, v in enumerate((lo, ba, hi), 3):
        c = a.cell(row=i, column=j, value=v); c.font = BLUE; c.number_format = fmt
        if key: c.fill = YEL
    act = a.cell(row=i, column=6, value=f"=INDEX(C{i}:E{i},$C$4)"); act.font = BOLD; act.number_format = fmt
    a.cell(row=i, column=7, value=u).font = BLACK
    c = a.cell(row=i, column=8, value=basis); c.font = BLACK; c.alignment = Alignment(wrap_text=True, vertical="top")
    A[k] = f"Assumptions!$F${i}"

rr = 7 + len(assum) + 1
a.cell(row=rr, column=1, value="Phasing (share of full value realised, by year)").font = H2
header(a, rr + 1, ["Line", "", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Basis"])
ph = [("cov", "Film capacity covered (UC1, UC2)", [0.08, 0.30, 0.55, 0.75, 0.85], "Lighthouse line in year 1; about 3 sites a year after; capped at 85% (Russia excluded pending sanctions review)."),
      ("recy_ph", "Recycling plants at the realised share of potential (UC3)", [0.30, 0.50, 0.70, 0.80, 0.80], "Noida commissioned 2026; ramps with plant utilisation."),
      ("conv_ph", "Converting coverage (UC6, Noida and Jammu)", [0.0, 0.40, 0.90, 1.0, 1.0], "Wave 2."),
      ("ramp_ph", "Ramp-up pull-forward timing (UC4)", [0.5, 0.5, 0, 0, 0], "Dharwad BOPP (FY27–28) and Egypt aseptic (trials Sep 2026)."),
      ("wc_ph", "Working-capital release timing (UC5)", [0.5, 0.5, 0, 0, 0], "")]
P = {}
for i, (k, lab, vals, basis) in enumerate(ph, rr + 2):
    a.cell(row=i, column=1, value=lab).font = BLACK
    for j, v in enumerate(vals, 3):
        c = a.cell(row=i, column=j, value=v); c.font = BLUE; c.number_format = '0%'
    a.cell(row=i, column=8, value=basis).font = BLACK
    P[k] = i

cr = rr + 2 + len(ph) + 1
a.cell(row=cr, column=1, value="Costs before scenario multiplier (₹ crore) — pending vendor and partner quotes").font = H2
header(a, cr + 1, ["Cost line", "Type", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Basis"])
costs = [
 ("Data foundation and OT security (historian, edge, segmentation, data model)", "Build", [8.0, 7.5, 7.5, 5.0, 0], "Lighthouse ₹8 cr; about ₹2.5 cr a site thereafter."),
 ("UC1 film-line models and integration (varies by OEM and line vintage)", "Build", [3.5, 4.5, 4.5, 3.0, 0], "₹3.5 cr lighthouse; ~₹1.5 cr a site."),
 ("Sensors, sub-metering and scanner / OEM data access", "Build", [1.0, 2.0, 2.0, 1.5, 0], "Line-by-line; OEM data-access licences."),
 ("UC2 slitting, deckle and scheduling optimisation", "Build", [1.5, 2.0, 1.5, 0, 0], ""),
 ("UC3 recycling quality and recycled-content genealogy", "Build", [2.5, 1.5, 1.0, 0, 0], ""),
 ("UC4 ramp-up instrumentation (Dharwad, Egypt aseptic)", "Build", [2.0, 1.0, 0, 0, 0], ""),
 ("UC5 planning, procurement and inventory", "Build", [3.0, 2.0, 0, 0, 0], "Including ERP data clean-up across countries."),
 ("UC6 converting make-ready and colour", "Build", [0, 2.5, 0.5, 0, 0], ""),
 ("Contingency (25% of build)", "Build", ["=0.25*SUM({c}{a}:{c}{b})"] * 5, ""),
 ("Readiness sprint and pilot advisory (capped)", "Advisory", [1.5, 0, 0, 0, 0], "Sprint fixed fee plus pilot advisory capped, part at risk."),
 ("Run: platform, licences, support (15% of cumulative build)", "Run", ["=0.15*SUM($C{a}:{c}{b})"] * 5, ""),
 ("Planning engine licence", "Run", [2.0, 2.0, 2.0, 2.0, 2.0], ""),
 ("AI and data team (central)", "Run", [4.5, 5.5, 6.5, 6.5, 6.5], "~₹0.55 cr per FTE, fully loaded; grows with scale."),
 ("Plant champions and internal staff time", "Run", [0.5, 1.5, 2.5, 3.0, 3.0], "~₹0.25 cr per site a year plus process and IT/OT time."),
 ("Change management and training", "Run", [2.0, 2.0, 2.0, 2.0, 2.0], ""),
 ("Travel, FX, taxes allowance", "Run", [1.0, 1.0, 1.0, 1.0, 1.0], ""),
]
first = cr + 2
build_last = first + 7       # last plain build line (UC6)
for i, (lab, typ, vals, basis) in enumerate(costs, first):
    a.cell(row=i, column=1, value=lab).font = BLACK; a.cell(row=i, column=2, value=typ).font = BLACK
    for j, v in enumerate(vals):
        col = YC[j]
        if isinstance(v, str):
            f = v.format(c=col, a=first, b=build_last)
            c = a.cell(row=i, column=3 + j, value=f); c.font = BLACK
        else:
            c = a.cell(row=i, column=3 + j, value=v); c.font = BLUE; c.fill = YEL
        c.number_format = CR
    a.cell(row=i, column=8, value=basis).font = BLACK
last = first + len(costs) - 1
tot = last + 1
a.cell(row=tot, column=1, value="Total cost after scenario multiplier").font = BOLD
for col in YC:
    c = a[f"{col}{tot}"]; c.value = f"=SUM({col}{first}:{col}{last})*{A['cost_mult']}"; c.font = BOLD; c.number_format = CR
a.cell(row=tot + 1, column=1, value="of which run cost (recurring, after multiplier)").font = BLACK
for col in YC:
    c = a[f"{col}{tot+1}"]; c.value = f"=SUM({col}{first+10}:{col}{last})*{A['cost_mult']}"; c.font = BLACK; c.number_format = CR
for k, w in {"A": 70, "B": 10, "C": 10, "D": 10, "E": 10, "F": 10, "G": 10, "H": 90}.items(): a.column_dimensions[k].width = w
COST_TOT, RUN_TOT = tot, tot + 1

# ------------------------------------------------------------------ Use cases (full run-rate values)
u = wb.create_sheet("Use cases")
u["A1"] = "Value at full scale (₹ crore) — active scenario"; u["A1"].font = H1
u["A2"] = '="Scenario: "&Assumptions!$D$4'; u["A2"].font = BOLD
header(u, 4, ["Use case", "Value at full scale (₹ cr)", "Type", "Logic"])
ucs = [
 ("UC1 Film-line stability and yield — scrap", f"={B['prod']}*{A['scrap']}*1000*{A['resin']}*{A['loss']}/1E7", "Recurring EBITDA (a year)", "Film production (t) × avoidable scrap share × 1,000 × ₹/kg × value lost after reclaim ÷ 10⁷"),
 ("UC1 Film-line stability and yield — energy per good kg", f"={B['pf']}*{A['e_share']}*{A['e_save']}", "Recurring EBITDA (a year)", "Power and fuel × film-line share × saving"),
 ("UC2 Slitting, deckle and scheduling", f"={B['prod']}*{A['trim']}*1000*{A['resin']}*{A['loss']}/1E7", "Recurring EBITDA (a year)", "Film production × trim and changeover scrap removed × ₹/kg × value lost"),
 ("UC3 Recycling quality and recycled-content evidence", f"={B['recy']}*{A['recy_gain']}", "Recurring EBITDA (a year)", "Management's recycling revenue potential × yield and grade gain (commercial value of evidence not counted)"),
 ("UC6 Converting make-ready and colour", f"={B['flex']}*{A['conv_gain']}*1000*{A['conv_cost']}*{A['conv_loss']}/1E7", "Recurring EBITDA (a year)", "Packaging volume (t) × waste removed × ₹/kg × value lost"),
 ("UC4 New-capacity ramp-up", f"={B['proj']}/12*{A['months']}*{A['attr_ramp']}", "One-off EBITDA", "Guided EBITDA of the four projects ÷ 12 × months earlier × AI share"),
 ("UC5 Planning, procurement and inventory — cash released", f"={B['perday']}*{A['days']}*{A['attr_wc']}", "One-off cash (working capital)", "Inventory per day of cost of goods sold × days released × AI share"),
 ("UC5 memo: interest on that cash", f"=D11*{B['kd']}", "Memo only (below EBITDA)", "Not counted in any return measure"),
]
for i, (lab, f, typ, logic) in enumerate(ucs, 5):
    u.cell(row=i, column=1, value=lab).font = BLACK
    c = u.cell(row=i, column=2, value=f); c.font = BOLD; c.number_format = CR
    u.cell(row=i, column=3, value=typ).font = BLACK; u.cell(row=i, column=4, value=logic).font = BLACK
# fix memo reference to the cash row (row 11)
u["B12"] = f"=B11*{B['kd']}"
u["A14"] = "Recurring EBITDA at full scale (UC1, UC2, UC3, UC6)"; u["A14"].font = BOLD
u["B14"] = "=SUM(B5:B9)"; u["B14"].font = BOLD; u["B14"].number_format = CR
for k, w in {"A": 62, "B": 22, "C": 30, "D": 100}.items(): u.column_dimensions[k].width = w

# ------------------------------------------------------------------ Five-year view
v = wb.create_sheet("Five years")
v["A1"] = "Five-year view (₹ crore) — active scenario"; v["A1"].font = H1
v["A2"] = '="Scenario: "&Assumptions!$D$4'; v["A2"].font = BOLD
header(v, 4, ["Line", "", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Total"])
lines = [
 (5, "UC1 film-line stability and yield", lambda c: f"=('Use cases'!$B$5+'Use cases'!$B$6)*Assumptions!{c}{P['cov']}"),
 (6, "UC2 slitting, deckle and scheduling", lambda c: f"='Use cases'!$B$7*Assumptions!{c}{P['cov']}"),
 (7, "UC3 recycling quality", lambda c: f"='Use cases'!$B$8*Assumptions!{c}{P['recy_ph']}"),
 (8, "UC6 converting make-ready and colour", lambda c: f"='Use cases'!$B$9*Assumptions!{c}{P['conv_ph']}"),
 (9, "Recurring EBITDA benefit", lambda c: f"=SUM({c}5:{c}8)"),
 (10, "UC4 ramp-up pull-forward (one-off EBITDA)", lambda c: f"='Use cases'!$B$10*Assumptions!{c}{P['ramp_ph']}"),
 (11, "Programme cost (build, run, team, contingency, advisory)", lambda c: f"=Assumptions!{c}{COST_TOT}"),
 (12, "Net EBITDA effect", lambda c: f"={c}9+{c}10-{c}11"),
 (13, "Cumulative net EBITDA effect", lambda c: f"=SUM($C$12:{c}12)"),
 (15, "UC5 working-capital release, AI share (cash, not EBITDA)", lambda c: f"='Use cases'!$B$11*Assumptions!{c}{P['wc_ph']}"),
 (16, "Memo: interest on released cash (not counted)", lambda c: f"=SUM($C$15:{c}15)*Baseline!$B$13"),
]
for row, lab, fn in lines:
    v.cell(row=row, column=1, value=lab).font = BOLD if row in (9, 12) else BLACK
    for col in YC:
        c = v[f"{col}{row}"]; c.value = fn(col); c.number_format = CR
        c.font = BOLD if row in (9, 12) else (GREEN if row in (5, 6, 7, 8, 10, 11, 15) else BLACK)
    if row not in (13,):
        c = v[f"H{row}"]; c.value = f"=SUM(C{row}:G{row})"; c.number_format = CR; c.font = BOLD
v["A18"] = "Returns"; v["A18"].font = H2
ret = [
 ("5-year NPV of net EBITDA effect (excludes working capital)", f"=NPV({A['disc']},C12:G12)", CR),
 ("5-year NPV including the AI share of working-capital release", f"=NPV({A['disc']},C12:G12)+NPV({A['disc']},C15:G15)", CR),
 ("Year-5 recurring EBITDA benefit", "=G9", CR),
 ("Year-5 run cost of the programme", f"=Assumptions!G{RUN_TOT}", CR),
 ("Year-5 net recurring EBITDA (benefit − run cost)", "=G9-Assumptions!G" + str(RUN_TOT), CR),
 ("as % of FY26 reported EBITDA", f"=B23/{B['ebitda']}", PCT),
 ("5-year return on cost (EBITDA benefits ÷ programme cost)", "=IF(H11>0,(H9+H10)/H11,0)", '0.00"x"'),
 ("Payback year on EBITDA (cumulative net ≥ 0)", '=IF(C13>=0,"Year 1",IF(D13>=0,"Year 2",IF(E13>=0,"Year 3",IF(F13>=0,"Year 4",IF(G13>=0,"Year 5","After year 5")))))', "@"),
]
ret += [
 ("Break-even multiple on recurring benefit rates (NPV of net EBITDA = 0)", f"=(NPV({A['disc']},C11:G11)-NPV({A['disc']},C10:G10))/NPV({A['disc']},C9:G9)", '0.00"x"'),
 ("Scrap removed needed at break-even (share of film production)", f"=B27*{A['scrap']}", '0.00%'),
 ("Energy saving per good kg needed at break-even", f"=B27*{A['e_save']}", '0.0%'),
]
for i, (lab, f, fmt) in enumerate(ret, 19):
    v.cell(row=i, column=1, value=lab).font = BLACK
    c = v.cell(row=i, column=2, value=f); c.font = BOLD; c.number_format = fmt
for k, w in {"A": 62, "B": 14, "C": 11, "D": 11, "E": 11, "F": 11, "G": 11, "H": 11}.items(): v.column_dimensions[k].width = w

for ws in wb.worksheets:
    ws.sheet_view.showGridLines = False
wb.save(OUT); print(OUT)
