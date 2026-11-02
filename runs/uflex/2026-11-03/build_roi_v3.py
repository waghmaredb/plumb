"""UFlex AI business case v3: staged commitment, incremental film-line gate, tonnage bases, cash and EBITDA views.
Every result cell is an Excel formula."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = "/home/claude/plumb/runs/uflex/2026-11-03/UFlex-AI-business-case.xlsx"
F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF"); BLACK = Font(name=F, size=10); BOLD = Font(name=F, size=10, bold=True)
GREEN = Font(name=F, size=10, color="008000"); H1 = Font(name=F, size=14, bold=True, color="0E1B2B"); H2 = Font(name=F, size=11, bold=True, color="0E1B2B")
HDR = Font(name=F, size=10, bold=True, color="FFFFFF"); HFILL = PatternFill("solid", fgColor="0E1B2B"); YEL = PatternFill("solid", fgColor="FFFF00")
CR = '#,##0.0;(#,##0.0);-'; PCT = '0.0%;(0.0%);-'; XF = '0.00"x"'
YC = ["C", "D", "E", "F", "G"]

wb = Workbook()
def header(ws, row, labels):
    for i, l in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=l); c.font, c.fill = HDR, HFILL
        c.alignment = Alignment(horizontal="left" if i == 1 else "center", wrap_text=True)
def widths(ws, d):
    for k, w in d.items(): ws.column_dimensions[k].width = w

# README
r = wb.active; r.title = "README"
txt = [("UFlex Limited — AI business case (outside-in, illustrative)", H1),
 ("PLUMB Advisory · November 2026 · ₹ crore unless stated", BLACK), ("", BLACK),
 ("How the case is built", H2),
 ("• Stage 1 (year 1) is the only commitment before Gate 2: one pilot line, the enterprise inventory work, recycling quality at Noida, and Dharwad instrumentation. Years 2–5 apply only if the pilot passes Gate 2.", BLACK),
 ("• Gate 2 tests the film-line use case (UC1) on its own incremental benefits and costs, not the whole programme.", BLACK),
 ("• Value streams are kept apart: recurring benefit from plant use cases; one-off ramp-up gain; one-off working-capital release (50% attributed to AI). Interest on released cash is a memo, never a benefit.", BLACK),
 ("• Two views: pre-tax cash (all build cost charged when spent) and EBITDA (capitalisable build excluded, per Ind AS 16/38, at the share set on Assumptions).", BLACK),
 ("• Plant value is built on tonnes. Value bases match each use case's scope.", BLACK), ("", BLACK),
 ("How to use", H2),
 ("Scenario on Assumptions!C4 (1 Low, 2 Base, 3 High). Low pairs low benefits with a 25% cost overrun. Blue = input; yellow = replace with UFlex data in the sprint; black = formula; green = link to another sheet.", BLACK), ("", BLACK),
 ("Not valued in the case", H2),
 ("Throughput from fewer breaks (shown as a memo), predictive maintenance, metalliser and coating quality, chip-plant control, aseptic laminate integrity, enterprise AI (cash and FX forecasting, procurement, EPR filings), product development, and the commercial value of recycled-content evidence. Each is sized in the sprint.", BLACK)]
for i, (t, f) in enumerate(txt, 1):
    c = r.cell(row=i, column=1, value=t); c.font = f; c.alignment = Alignment(wrap_text=True, vertical="top")
widths(r, {"A": 125})

# Baseline
b = wb.create_sheet("Baseline")
b["A1"] = "Baseline — UFlex published figures"; b["A1"].font = H1
header(b, 3, ["Item", "Value", "Unit", "Source"])
base = [
 ("mat", "Cost of materials consumed, FY26", 8877.00, "₹ cr", "Consolidated results FY26"),
 ("pf", "Power and fuel, FY26", 739.33, "₹ cr", "Consolidated results FY26"),
 ("ebitda", "Reported EBITDA, FY26", 1983.6, "₹ cr", "Q4 FY26 investor presentation, slide 21"),
 ("prod", "Packaging film production, FY26", 492779, "t", "Q4 FY26 investor presentation, slide 10"),
 ("vol", "Total sales volume, FY26", 649789, "t", "Q4 FY26 investor presentation, slides 6, 23"),
 ("flexq", "Flexible packaging production, Q1 FY27", 19680, "t", "Q1 FY27 investor presentation, slide 11 (78.7% utilisation)"),
 ("rpet", "rPET chip capacity", 79020, "t", "Q1 FY27 investor presentation, slide 13"),
 ("inv", "Inventories, 31 Mar 2026", 2408.3, "₹ cr", "Q4 FY26 investor presentation, slide 22"),
 ("turn", "Inventory turnover (cost of goods sold ÷ average inventory), FY26", 3.67, "x", "Q4 FY26 investor presentation, slide 28"),
 ("kd", "Blended cost of debt", 0.085, "%", "Q1 FY27 earnings release"),
 ("proj", "EBITDA from four new projects at decent utilisation (management guidance)", 500.0, "₹ cr / yr", "Q2 FY26 earnings call: 'around Rs. 3,000 odd crores within an EBITDA of about Rs. 500 crores'"),
]
B = {}
for i, (k, lab, v, u, s) in enumerate(base, 4):
    b.cell(row=i, column=1, value=lab).font = BLACK
    c = b.cell(row=i, column=2, value=v); c.font = BLUE
    c.number_format = PCT if u == "%" else (XF if u == "x" else ('#,##0' if u == "t" else CR))
    b.cell(row=i, column=3, value=u).font = BLACK; b.cell(row=i, column=4, value=s).font = BLACK
    B[k] = f"Baseline!$B${i}"
n = 4 + len(base) + 1
b.cell(row=n, column=1, value="Derived").font = H2
der = [("flexy", "Flexible packaging, annualised from Q1 FY27 (t)", f"={B['flexq']}*4", '#,##0'),
       ("rmkg", "Materials per tonne sold, all products (₹/kg) — cross-check", f"={B['mat']}*1E7/{B['vol']}/1000", '#,##0'),
       ("perday", "Inventory per day of cost of goods sold (₹ cr)", f"={B['inv']}*{B['turn']}/365", CR)]
for j, (k, lab, f, fmt) in enumerate(der, n + 1):
    b.cell(row=j, column=1, value=lab).font = BLACK
    c = b.cell(row=j, column=2, value=f); c.font = BLACK; c.number_format = fmt
    B[k] = f"Baseline!$B${j}"
widths(b, {"A": 70, "B": 14, "C": 10, "D": 95})

# Assumptions
a = wb.create_sheet("Assumptions")
a["A1"] = "Assumptions — blue cells are inputs; yellow = replace with UFlex data in the sprint"; a["A1"].font = H1
a["A4"] = "Scenario (1 = Low, 2 = Base, 3 = High)"; a["A4"].font = BOLD
a["C4"] = 2; a["C4"].font = BLUE; a["C4"].fill = YEL
a["D4"] = '=INDEX({"Low","Base","High"},C4)'; a["D4"].font = BOLD
header(a, 6, ["Assumption", "Use case", "Low", "Base", "High", "Active", "Unit", "Basis"])
assum = [
 ("cost_mult", "Cost multiplier (every cost line)", "All", 1.25, 1.00, 0.90, "x", "Low case assumes a 25% overrun.", False),
 ("disc", "Discount rate", "All", 0.14, 0.12, 0.10, "%", "Above the 8.5% blended cost of debt.", False),
 ("capex", "Share of build cost that is capitalisable", "All", 0.5, 0.6, 0.6, "%", "Hardware, historians, sensors (Ind AS 16/38); configuration and services expensed. Confirm with UFlex finance.", True),
 ("resin", "Polymer value of a kilogram of film (₹/kg)", "UC1, UC2", 105, 110, 115, "₹/kg", "Cross-check on Baseline: materials per tonne sold across all products. Replace with grade-level cost.", True),
 ("scrap", "Avoidable scrap and off-spec removed (share of film production)", "UC1", 0.003, 0.006, 0.010, "%", "Breaks, gels and specks, restart and changeover scrap, winding defects. Needs UFlex's scrap baseline.", True),
 ("loss", "Value lost per kg of scrap after reclaim or sale as seconds", "UC1, UC2", 0.25, 0.30, 0.35, "%", "Virgin–reclaim value gap, reprocessing cost and downgrade discount.", True),
 ("e_share", "Film-line share of power and fuel", "UC1", 0.55, 0.55, 0.55, "%", "Replace with plant meter data.", True),
 ("e_save", "Energy saved per good kg on film lines", "UC1", 0.01, 0.02, 0.03, "%", "Fewer breaks and restarts; steadier operation.", True),
 ("trim", "Slitting trim and changeover scrap removed (share of film production)", "UC2", 0.001, 0.002, 0.004, "%", "Incremental to any deckle optimisation already in place; excludes changeover scrap counted in UC1.", True),
 ("rpet_util", "rPET plant utilisation by year 5", "UC3", 0.65, 0.75, 0.85, "%", "Ramps from 35% in year 1 (phasing below).", True),
 ("rpet_gain", "Yield and grade gain on rPET output", "UC3", 0.01, 0.02, 0.03, "%", "Bale grading, sorting and quality control (IV, colour, contamination); net of what existing AI segregation already delivers.", True),
 ("rpet_val", "Value of a kilogram of rPET chips (₹/kg)", "UC3", 90, 100, 110, "₹/kg", "Replace with UFlex realised prices.", True),
 ("conv_cost", "Material value of a kilogram of converted laminate (₹/kg)", "UC6", 170, 170, 170, "₹/kg", "Film, foil, ink and adhesive. Replace with job costing.", True),
 ("conv_gain", "Converting waste removed (share of flexible-packaging output)", "UC6", 0.002, 0.004, 0.007, "%", "Make-ready, colour approval, ink and solvent; register and inspection are already closed-loop.", True),
 ("conv_loss", "Value lost per kg of converting waste", "UC6", 0.80, 0.80, 0.80, "%", "Laminated waste has little recovery value.", False),
 ("ramp_share", "Share of guided project EBITDA from Dharwad BOPP and Egypt aseptic", "UC4", 0.5, 0.5, 0.5, "%", "The other two guided projects (Noida recycling, Mexico WPP) are already running.", True),
 ("months", "Months earlier to target utilisation", "UC4", 0.5, 1.0, 2.0, "months", "Dharwad instrumented from commissioning; Egypt retrofit during ramp.", True),
 ("attr_ramp", "Share of the ramp-up gain attributed to AI", "UC4", 0.3, 0.4, 0.5, "%", "Ramps are partly demand-constrained; AI does not create demand.", False),
 ("days", "Inventory days released", "UC5", 3, 5, 8, "days", "Against ~100 days of cost of goods sold; measured in days because inventory grows with revenue.", True),
 ("attr_wc", "Share of the working-capital release attributed to AI", "UC5", 0.5, 0.5, 0.5, "%", "The rest belongs to inventory policy and supplier terms.", False),
 ("uptime", "Memo: running time gained from fewer breaks", "Memo", 0.0025, 0.005, 0.01, "%", "Not counted in the case. Relevant only when lines are sold out.", False),
 ("contrib", "Memo: contribution per extra kg of film (₹/kg)", "Memo", 10, 15, 20, "₹/kg", "Not counted in the case.", False),
]
A = {}
for i, (k, lab, uc, lo, ba, hi, u, basis, key) in enumerate(assum, 7):
    a.cell(row=i, column=1, value=lab).font = BLACK; a.cell(row=i, column=2, value=uc).font = BLACK
    fmt = {"%": '0.00%', "x": XF, "₹/kg": '#,##0', "months": '0.0', "days": '0'}[u]
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
ph = [("cov1", "UC1 film capacity covered", [0.05, 0.20, 0.45, 0.70, 0.85], "Pilot line in year 1; India film sites (about 26% of capacity) in year 2; overseas after Gate 3; one CIS site (7.5%) held back pending a vendor export-licensing review."),
      ("cov2", "UC2 film capacity covered", [0.0, 0.15, 0.40, 0.65, 0.85], "Starts after the pilot."),
      ("rpet_ph", "rPET utilisation path (year 5 = assumption above)", [0.35, 0.50, 0.60, 0.70, "=Assumptions!$F$" + "{rpu}"], "Noida commissioned April 2026."),
      ("conv_ph", "UC6 converting coverage (Noida, Jammu)", [0.0, 0.40, 0.90, 1.0, 1.0], "Wave 2."),
      ("ramp_ph", "UC4 timing of the ramp-up gain", [0.2, 0.4, 0.4, 0, 0], "Dharwad due FY27–28; Egypt in trials since Sept 2026."),
      ("wc_ph", "UC5 timing of the working-capital release", [0.5, 0.5, 0, 0, 0], "")]
P = {}
rpu_row = 7 + [x[0] for x in assum].index("rpet_util")
for i, (k, lab, vals, basis) in enumerate(ph, rr + 2):
    a.cell(row=i, column=1, value=lab).font = BLACK
    for j, v in enumerate(vals, 3):
        if isinstance(v, str):
            c = a.cell(row=i, column=j, value=v.format(rpu=rpu_row)); c.font = GREEN
        else:
            c = a.cell(row=i, column=j, value=v); c.font = BLUE
        c.number_format = '0%'
    a.cell(row=i, column=8, value=basis).font = BLACK
    P[k] = i
cr = rr + 2 + len(ph) + 1
a.cell(row=cr, column=1, value="Costs before the scenario multiplier (₹ crore) — Year 1 is the Stage 1 commitment; years 2–5 only if Gate 2 passes").font = H2
header(a, cr + 1, ["Cost line", "Type", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Basis"])
costs = [
 ("df", "Data foundation and OT security (historian, edge, segmentation, data model)", "Build", [3.0, 6.0, 7.5, 5.0, 0], "Pilot site in year 1; India sites year 2; overseas after Gate 3."),
 ("uc1", "UC1 film-line models and integration", "Build", [3.0, 3.5, 4.5, 3.0, 0], "Varies by OEM and line vintage; priced by line type in the sprint."),
 ("sens", "Sensors, sub-metering and OEM / inspection data access", "Build", [0.8, 1.5, 2.0, 1.5, 0], ""),
 ("uc2", "UC2 slitting, deckle and scheduling", "Build", [0, 2.0, 1.5, 0, 0], "After the pilot."),
 ("uc3", "UC3 recycling quality and recycled-content records", "Build", [1.0, 1.5, 1.0, 0, 0], ""),
 ("uc4", "UC4 Dharwad instrumentation and Egypt ramp support", "Build", [0.5, 1.5, 0, 0, 0], ""),
 ("uc5", "UC5 planning, procurement and inventory", "Build", [1.5, 2.0, 0, 0, 0], "Including ERP data clean-up."),
 ("uc6", "UC6 gravure make-ready and colour", "Build", [0, 2.0, 0.5, 0, 0], ""),
 ("cont", "Contingency (25% of build)", "Build", "cont", ""),
 ("adv", "Readiness sprint and pilot advisory (capped)", "Advisory", [1.5, 0, 0, 0, 0], "Fixed sprint fee plus capped pilot fees, part held back against results."),
 ("run", "Run: platform, licences, support (15% of cumulative build)", "Run", "run", ""),
 ("lic", "Planning engine licence", "Run", [0, 2.0, 2.0, 2.0, 2.0], "From year 2; Stage 1 uses existing tools."),
 ("team", "Central AI and data team (FTE × ₹0.55 cr)", "Run", [1.65, 3.85, 5.5, 5.5, 5.5], "3, 7, 10, 10, 10 FTE."),
 ("champ", "Plant champions and internal staff time", "Run", [0.25, 1.0, 2.0, 2.5, 2.5], ""),
 ("chg", "Change management and training", "Run", [0.3, 1.5, 1.5, 1.0, 1.0], ""),
 ("trav", "Travel, FX, taxes allowance", "Run", [0.3, 1.0, 1.0, 1.0, 1.0], ""),
]
first = cr + 2
CROW = {}
for i, (k, lab, typ, vals, basis) in enumerate(costs, first):
    CROW[k] = i
build_rows = [first + j for j in range(8)]
for i, (k, lab, typ, vals, basis) in enumerate(costs, first):
    a.cell(row=i, column=1, value=lab).font = BLACK; a.cell(row=i, column=2, value=typ).font = BLACK
    for j, col in enumerate(YC):
        if vals == "cont":
            f = f"=0.25*SUM({col}{build_rows[0]}:{col}{build_rows[-1]})"; c = a.cell(row=i, column=3 + j, value=f); c.font = BLACK
        elif vals == "run":
            f = f"=0.15*SUM($C${build_rows[0]}:{col}{build_rows[-1]})"; c = a.cell(row=i, column=3 + j, value=f); c.font = BLACK
        else:
            c = a.cell(row=i, column=3 + j, value=vals[j]); c.font = BLUE; c.fill = YEL
        c.number_format = CR
    a.cell(row=i, column=8, value=basis).font = BLACK
last = first + len(costs) - 1
TOT, BUILD_TOT, REC_TOT = last + 1, last + 2, last + 3
labels = {TOT: "Total cost after scenario multiplier (pre-tax cash)", BUILD_TOT: "of which build incl. contingency (after multiplier)", REC_TOT: "of which recurring run cost (after multiplier)"}
for row, lab in labels.items():
    a.cell(row=row, column=1, value=lab).font = BOLD if row == TOT else BLACK
for col in YC:
    a[f"{col}{TOT}"] = f"=SUM({col}{first}:{col}{last})*{A['cost_mult']}"
    a[f"{col}{BUILD_TOT}"] = f"=SUM({col}{first}:{col}{CROW['cont']})*{A['cost_mult']}"
    a[f"{col}{REC_TOT}"] = f"=SUM({col}{CROW['run']}:{col}{last})*{A['cost_mult']}"
    for row in (TOT, BUILD_TOT, REC_TOT):
        a[f"{col}{row}"].number_format = CR; a[f"{col}{row}"].font = BOLD if row == TOT else BLACK
widths(a, {"A": 72, "B": 10, "C": 10, "D": 10, "E": 10, "F": 10, "G": 10, "H": 95})

# Use cases
u = wb.create_sheet("Use cases")
u["A1"] = "Value at full rate (₹ crore a year unless stated) — active scenario"; u["A1"].font = H1
u["A2"] = '="Scenario: "&Assumptions!$D$4'; u["A2"].font = BOLD
header(u, 4, ["Use case", "Value", "Type", "Logic"])
ucs = [
 ("UC1 film-line stability — scrap", f"={B['prod']}*{A['scrap']}*1000*{A['resin']}*{A['loss']}/1E7", "Recurring, at 100% coverage", "Film production × avoidable scrap × ₹/kg × value lost ÷ 10⁷"),
 ("UC1 film-line stability — energy per good kg", f"={B['pf']}*{A['e_share']}*{A['e_save']}", "Recurring, at 100% coverage", "Power and fuel × film-line share × saving"),
 ("UC2 slitting, deckle and scheduling", f"={B['prod']}*{A['trim']}*1000*{A['resin']}*{A['loss']}/1E7", "Recurring, at 100% coverage", "Film production × trim removed × ₹/kg × value lost"),
 ("UC3 recycling quality (at 100% rPET utilisation)", f"={B['rpet']}*{A['rpet_gain']}*1000*{A['rpet_val']}/1E7", "Recurring; scaled by utilisation path", "rPET capacity × yield and grade gain × ₹/kg"),
 ("UC6 gravure make-ready and colour", f"={B['flexy']}*{A['conv_gain']}*1000*{A['conv_cost']}*{A['conv_loss']}/1E7", "Recurring, at 100% coverage", "Flexible-packaging output × waste removed × ₹/kg × value lost"),
 ("UC4 ramp-up gain", f"={B['proj']}*{A['ramp_share']}/12*{A['months']}*{A['attr_ramp']}", "One-off EBITDA, spread over the ramp", "Guided EBITDA × Dharwad+Egypt share ÷ 12 × months earlier × AI share"),
 ("UC5 working-capital release", f"={B['perday']}*{A['days']}*{A['attr_wc']}", "One-off cash", "Inventory per day × days released × AI share"),
 ("Memo: interest on released cash (not counted)", f"=B11*{B['kd']}", "Memo", ""),
 ("Memo: throughput from fewer breaks (not counted)", f"={B['prod']}*{A['uptime']}*1000*{A['contrib']}/1E7", "Memo", "Only when lines are sold out"),
]
for i, (lab, f, typ, logic) in enumerate(ucs, 5):
    u.cell(row=i, column=1, value=lab).font = BLACK
    c = u.cell(row=i, column=2, value=f); c.font = BOLD; c.number_format = CR
    u.cell(row=i, column=3, value=typ).font = BLACK; u.cell(row=i, column=4, value=logic).font = BLACK
widths(u, {"A": 56, "B": 14, "C": 38, "D": 80})

# Five years
v = wb.create_sheet("Five years")
v["A1"] = "Five-year view (₹ crore) — active scenario"; v["A1"].font = H1
v["A2"] = '="Scenario: "&Assumptions!$D$4'; v["A2"].font = BOLD
header(v, 4, ["Line", "", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Total"])
rows = [
 (5, "UC1 film-line stability and yield", lambda c: f"=('Use cases'!$B$5+'Use cases'!$B$6)*Assumptions!{c}{P['cov1']}"),
 (6, "UC2 slitting, deckle and scheduling", lambda c: f"='Use cases'!$B$7*Assumptions!{c}{P['cov2']}"),
 (7, "UC3 recycling quality", lambda c: f"='Use cases'!$B$8*Assumptions!{c}{P['rpet_ph']}"),
 (8, "UC6 gravure make-ready", lambda c: f"='Use cases'!$B$9*Assumptions!{c}{P['conv_ph']}"),
 (9, "Recurring benefit (gross)", lambda c: f"=SUM({c}5:{c}8)"),
 (10, "UC4 ramp-up gain (one-off)", lambda c: f"='Use cases'!$B$10*Assumptions!{c}{P['ramp_ph']}"),
 (11, "Programme cost (pre-tax cash)", lambda c: f"=Assumptions!{c}{TOT}"),
 (12, "Net pre-tax cash effect (excl. working capital)", lambda c: f"={c}9+{c}10-{c}11"),
 (13, "Cumulative", lambda c: f"=SUM($C$12:{c}12)"),
 (14, "EBITDA effect (capitalisable build excluded)", lambda c: f"={c}9+{c}10-({c}11-Assumptions!{c}{BUILD_TOT}*{A['capex']})"),
 (15, "UC5 working-capital release, AI share (cash)", lambda c: f"='Use cases'!$B$11*Assumptions!{c}{P['wc_ph']}"),
 (17, "UC1 attributable cost (own build, sensors, half the data foundation, contingency, run, plant champions)", lambda c:
     f"=(((Assumptions!{c}{CROW['uc1']}+Assumptions!{c}{CROW['sens']}+0.5*Assumptions!{c}{CROW['df']})*1.25)+0.15*SUM(Assumptions!$C${CROW['uc1']}:{c}{CROW['uc1']},Assumptions!$C${CROW['sens']}:{c}{CROW['sens']})+0.075*SUM(Assumptions!$C${CROW['df']}:{c}{CROW['df']})+Assumptions!{c}{CROW['champ']})*{A['cost_mult']}"),
 (18, "UC1 net (benefit − attributable cost)", lambda c: f"={c}5-{c}17"),
]
for row, lab, fn in rows:
    v.cell(row=row, column=1, value=lab).font = BOLD if row in (9, 12, 14, 18) else BLACK
    for col in YC:
        c = v[f"{col}{row}"]; c.value = fn(col); c.number_format = CR
        c.font = BOLD if row in (9, 12, 14, 18) else (GREEN if row in (5, 6, 7, 8, 10, 11, 15) else BLACK)
    if row != 13:
        v[f"H{row}"] = f"=SUM(C{row}:G{row})"; v[f"H{row}"].number_format = CR; v[f"H{row}"].font = BOLD
v["A20"] = "Returns"; v["A20"].font = H2
D = A['disc']
ret = [
 ("Stage 1 commitment before Gate 2 (year 1 cost)", "=C11", CR),
 ("5-year NPV, pre-tax cash (excl. working capital)", f"=NPV({D},C12:G12)", CR),
 ("Year-5 recurring benefit (gross)", "=G9", CR),
 ("Year-5 recurring run cost", f"=Assumptions!G{REC_TOT}", CR),
 ("Year-5 net recurring (steady state)", "=B23-B24", CR),
 ("as % of FY26 reported EBITDA", f"=B25/{B['ebitda']}", PCT),
 ("NPV including steady state after year 5 (perpetuity, no growth)", f"=B22+B25/{D}/(1+{D})^5", CR),
 ("NPV including the AI share of working capital", f"=B27+NPV({D},C15:G15)", CR),
 ("Payback, pre-tax cash", '=IF(C13>=0,"Year 1",IF(D13>=0,"Year 2",IF(E13>=0,"Year 3",IF(F13>=0,"Year 4",IF(G13>=0,"Year 5","After year 5")))))', "@"),
 ("Gate 2 — UC1 5-year NPV on its own incremental cost", f"=NPV({D},C18:G18)", CR),
 ("Gate 2 — UC1 break-even multiple on base rates", f"=NPV({D},C17:G17)/NPV({D},C5:G5)", XF),
 ("Gate 2 — scrap removed needed (share of film production)", f"=B31*{A['scrap']}", '0.00%'),
 ("Gate 2 — energy saved per good kg needed", f"=B31*{A['e_save']}", '0.0%'),
 ("Programme break-even multiple on all recurring rates (5-year, cash)", f"=(NPV({D},C11:G11)-NPV({D},C10:G10))/NPV({D},C9:G9)", XF),
]
for i, (lab, f, fmt) in enumerate(ret, 21):
    v.cell(row=i, column=1, value=lab).font = BLACK
    c = v.cell(row=i, column=2, value=f); c.font = BOLD; c.number_format = fmt
widths(v, {"A": 78, "B": 14, "C": 11, "D": 11, "E": 11, "F": 11, "G": 11, "H": 11})
for ws in wb.worksheets: ws.sheet_view.showGridLines = False
wb.save(OUT); print(OUT, "rows", dict(TOT=TOT, REC=REC_TOT, rpu=rpu_row))
