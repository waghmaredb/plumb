# Pilot fee schedule and measurement design

**Status:** v0.1 draft, 2026-11-03, for counsel, a chartered accountant and the Client's group finance. Model wording.
**Use:** proposed at the sprint readout (deliverable D4/D5); attached to the pilot SOW; applied at Gate 2. Thresholds below are the outside-in values from the UFlex strategy and are **re-set on UFlex data in the sprint**.

## 1. Fee and holdback

| Term | Position |
|---|---|
| Pilot advisory fee | Capped at **₹[[FOUNDER: cap]]** for the pilot (about [[FOUNDER: months]] months: build, tune, six-month measurement). Fixed monthly instalments; no time-and-materials overrun |
| Sprint fee credit | Sprint fee credited against the pilot fee if the pilot SOW is signed within 90 days of sprint acceptance |
| **Holdback** | **[[FOUNDER: 30–50]]%** of each instalment is **held back by the Client** (not invoiced for payment) until Gate 2. This is a holdback, not a refund: PLUMB never returns money already paid |
| Release | Held-back amount is invoiced and paid within 30 days of **Gate 2 sign-off by group finance** that the pilot line met the test in §2 |
| If Gate 2 is not met | [[FOUNDER: choose — (a) holdback is not payable; or (b) holdback paid pro rata to the share of the break-even value achieved, zero below [50]%]] |
| If measurement cannot be completed for Client reasons | (data feed withdrawn, control line changed without agreement, Client stops for convenience) — holdback becomes payable in full within 30 days |
| Taxes | As in the sprint SOW (s.195 / DTAA, IGST reverse charge) **[VERIFY: CA]** |

## 2. The Gate 2 test

| Element | Definition |
|---|---|
| **Metric** | (1) **Scrap %**: film scrapped (breaks, start-up, changeover, edge trim beyond design, off-grade) as a share of film produced on the pilot line; (2) **kWh per good kg**: line and allocated utilities energy per kg of saleable film |
| Comparison | Pilot line versus a **control line** of similar type, vintage and grade family nominated by the Client; difference-in-differences against the pre-period |
| Normalisation | Both metrics computed **per grade** and re-weighted to a fixed baseline grade mix, so changes in mix, thickness and order length do not count as results |
| **Baseline period and source** | [[FOUNDER/Client: 6–12]] months before the pilot start, from [historian / MES / ERP — named source system and tags], frozen and signed by group finance before the pilot starts |
| **Measurement window** | **Six months** after models go live in advisory mode, after an agreed run-in of [4] weeks |
| Pass level | The measured scrap and energy effects, valued at the agreed ₹/kg and ₹/kWh, at least cover the pilot use case's own incremental annual cost (break-even). Indicative outside-in pair: **about 1.02 percentage points of scrap removed with 3.4% less energy per good kg**; re-computed on Client data in the sprint and fixed in the pilot SOW |
| Power | Sprint estimates the minimum detectable effect from pre-period variance; if six months cannot detect the pass level, the window or line choice is changed before the pilot is signed |

## 3. Attribution rule

Signed by **Client group finance** before the pilot starts, stating: the formula (difference-in-differences, grade-normalised); the ₹ values per kg of scrap avoided and per kWh; which concurrent initiatives are excluded or netted off (e.g. new OEM upgrades, raw-material changes); and that the result counts only advisories that operators acted on or that were active in the period. Group finance owns the calculation; PLUMB can inspect inputs.

## 4. Value ledger

The value ledger is **owned and maintained by Client group finance**, monthly, from Client system records. PLUMB has read access and may comment; it does not keep the official numbers.

## 5. Re-baseline and stop triggers

| Trigger | Effect |
|---|---|
| Line rebuild, major OEM upgrade, die or winder replacement on pilot or control line | Measurement paused; baseline re-set within 20 working days by agreement |
| Grade mix outside the baseline range by more than [[FOUNDER/Client: X]]% for a month | That month excluded or re-weighted per the attribution rule |
| Unplanned outage > [10] days on either line | Window extended day-for-day |
| Pilot changes applied to the control line | Control line replaced or window restarted by agreement |
| Data feed lost > [10] working days | Window extended; if > [30] days for Client reasons, holdback payable (§1) |
| Safety or quality incident linked to an advisory | Advisory switched off at once; joint review; Client may stop the pilot |
| Below the pass level after one retraining cycle | Stop: Gate 2 not met; enterprise use cases and data foundation may continue |

## 6. Disputes on the measured result

1. **Joint review** by the Client's metric owner and PLUMB within 10 working days of the Gate 2 statement.
2. **Independent measurer** if unresolved after 20 working days: an independent chartered accountant or engineering assessor agreed by the parties (failing agreement, nominated by [ ] **[VERIFY: counsel — nominating body]**), who determines the metric value on the signed measurement design, acting as expert not arbitrator; decision final on the value, save manifest error; costs shared equally unless the measurer decides otherwise.
3. Disputes about the design itself (not the value) go to arbitration under the pilot SOW.

| Group finance, UFlex Limited (attribution rule and baseline) | Executive sponsor, UFlex Limited | PLUMB Advisory Pte. Ltd. |
|---|---|---|
| | | [[FOUNDER]] |
