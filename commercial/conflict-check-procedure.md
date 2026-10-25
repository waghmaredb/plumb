# Conflict-Check Procedure (one page)

**Status: v0.1 draft**
**Owner:** Signing partner (procedure); engagement lead (execution)
**Purpose:** The acceptance control in the ISQM-style engagement file. No charter is issued, no peer set is run and no client data is received until the check is recorded as clear or clear-with-conditions. Drafted for counsel review alongside the engagement letter; the founder's employment-clearance position is **[VERIFY]** against the founder's employment terms.
**Related:** `engagement-charter-template.md` §0 and §3; `engagement-letter-clauses.md` §9 and Schedule 4.

## Change log

| Version | Date | Author | Change |
|---|---|---|---|
| v0.1 | 2026-10-25 | Signing partner | Initial procedure from Phase 0 acceptance step and GA-gate requirement |

---

## 1. When the check runs

| Trigger | Scope of check | Deadline | Who |
|---|---|---|---|
| T1 First contact with a prospect that could become an engagement | Prospect entity and group | Before any proposal or pricing is sent | Engagement lead |
| T2 Charter drafting (Phase 0, day 1) | Full check: client, group, named competitors, draft peer set, interviewee employers, founder's other roles | Before charter issue (day 2) | Engagement lead; signing partner approves |
| T3 Peer set finalised (end of Phase 1, day 8) | Any peer added after T2 | Before the peer's data enters any benchmark exhibit | Engagement lead |
| T4 Scope change, new segment, add-on contracted | Delta only | Before the change order is signed | Engagement lead |
| T5 New engagement anywhere in the firm while this one is open | Cross-check new prospect against all open engagements' clients and peer sets | Before proposal | Engagement lead of the new matter |
| T6 Change in founder's employment, directorships or investments | All open engagements | Within 5 working days of the change | Founder |
| T7 Annual | All retainers (Tier 3) | Retainer anniversary | Signing partner |

---

## 2. What is checked

| # | Subject | Checked against | Method | Source of names |
|---|---|---|---|---|
| C1 | Client entity, parent, subsidiaries, major shareholders (≥ 20%) | Open and closed engagements (last 24 months); design-partner list; retainer list | Entity register search; firm's engagement register | Registry extract; charter §1 |
| C2 | Peer set (core and secondary) and competitors named by the client | Open engagements and retainers; prospects in active proposal | Engagement register | Charter §3 |
| C3 | Competitors named in the peer set that are current or recent (24 months) PLUMB clients | Whether PLUMB holds their confidential information that could colour the benchmark | Engagement register; information-barrier log | Charter §3 |
| C4 | External interviewees' employers (won / lost / churned customers, channel partners) | Open engagements | Engagement register | Charter §5.3 |
| C5 | Technology vendors likely to be named in use cases | Any PLUMB commercial relationship (referral, reseller, equity, advisory) | Vendor-relationship register (must be empty or disclosed) | Catalogue; charter §2 |
| C6 | Founder's current employer, its group, its named competitors, its customers and suppliers where the founder has had material involvement | Client, client's group, peer set | Founder's declaration; employer's conflict and outside-activity policy **[VERIFY]** | Founder |
| C7 | Founder's other engagements, advisory roles, directorships, investments | Client, peer set, vendors in C5 | Founder's standing declaration (updated at T6) | Founder |
| C8 | Independent reviewer and signing partner | Personal relationships, prior employment, shareholdings in client or peers | Individual declaration per engagement | Charter §8 |
| C9 | Sanctions, adverse media, regulatory action against the client or its principals | Public sources | Screening search; recorded in file | Registry; press |

---

## 3. Decision rules

| Finding | Decision | Conditions / action |
|---|---|---|
| No matches on C1–C9 | **Clear** | Record and proceed |
| Peer-set company is a closed PLUMB client (> 12 months) and no confidential information is relevant to the benchmark | Clear with conditions | Use only public-source data for that peer; note in decision log; disclose in Schedule 4 |
| Peer-set company is a current PLUMB client or retainer | Clear with conditions **or** exclude peer | Information barrier (separate engagement lead and reviewer; no shared drive access); both clients informed that PLUMB serves companies in the sector (engagement letter 9.2); if either objects, exclude the peer from the core set and record. Never exclude silently: the benchmark disclosure must state the exclusion |
| Client is a direct competitor of a current client in the same segment and both engagements would run concurrently with the same engagement lead | **Decline or defer** | Defer until the first engagement closes, or staff with a different lead and reviewer and obtain both clients' written consent |
| Founder's employer (C6) is the client, a group company, or a named competitor of the client in the segment in scope | **Decline** | No conditions cure this |
| Founder's employer is a supplier to or customer of the client, or appears in the peer set as a secondary peer | Clear with conditions | Founder's employer-side clearance obtained in writing **[VERIFY policy]**; founder does not hold the engagement-lead role on modules touching that relationship; disclosed in Schedule 4; employer's data never used |
| Founder holds an advisory role, investment or directorship in a company in the peer set or in a vendor likely to be recommended (C5, C7) | Clear with conditions **or** decline | Disclose in Schedule 4; vendor excluded from recommendation or presented with the disclosure on the slide; if the interest is material (≥ 5% equity or board seat) in a core peer, decline |
| Any PLUMB commercial relationship with a vendor named in use cases (C5) | Clear with conditions | Disclose on the slide and in Schedule 4; engagement letter 9.3 applies; if a referral fee exists it is waived for this client |
| Sanctions hit or unresolved regulatory action against client principals (C9) | **Decline** pending counsel review | |
| Independent reviewer or signing partner has a personal or financial link (C8) | Replace the individual | Cannot proceed with the same QA gate owners |
| Client objects to a peer with a written reason | Engagement lead decides; signing partner approves | Objection and decision recorded; peer-set disclosure on the exhibit notes "one peer excluded at client request" without naming |

Escalation: any "clear with conditions" is approved by the signing partner; any "decline" is recorded with reason and communicated to the prospect by the signing partner.

---

## 4. Record kept in the engagement file

| Field | Entry |
|---|---|
| Conflict-check ID | [CC-YYYY-NNN] |
| Engagement ID | [PLUMB-YYYY-NNN] |
| Trigger (T1–T7) and date run | |
| Names checked (C1–C9), with source of each list | Attached list; version of peer set checked |
| Searches performed and systems used | Engagement register version; founder declaration date; screening tool and date |
| Matches found | None / list with subject and type |
| Decision | Clear / clear with conditions / declined / deferred |
| Conditions imposed | Information barrier, exclusions, disclosures, staffing changes |
| Disclosures to client (Schedule 4 text) | |
| Founder declaration reference | [date, version] |
| Reviewer and partner independence declarations | [signed, dates] |
| Approved by | Signing partner [signature, date] |
| Re-check due | Next trigger (T3 day 8; T4 on scope change; T7 anniversary) |
| Retention | With the engagement file for the full engagement-file retention period |

---

## 5. Open items for v0.2

| Item | Action | Owner |
|---|---|---|
| Founder employment-clearance policy and process | Obtain the employer's outside-activity rules in writing; decide whether a standing clearance or per-engagement clearance is required **[VERIFY]** | Founder + counsel |
| Engagement register tooling | Choose where the register lives so T5 cross-checks are one query | Founder |
| Screening tool for C9 | Select a sanctions / adverse-media source within the data-stack budget | Compliance lead |
| Threshold for "material" interest (5% / board seat working value) | Counsel view | Counsel |
