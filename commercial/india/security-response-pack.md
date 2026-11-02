# Security response pack — standard answers for client security reviews

**Status:** v0.1, 2026-11-03. Every answer must be true on the day it is sent: confirm each `[[FOUNDER: …]]` against the live configuration first.
**Use:** paste into the client's vendor security questionnaire, or send as-is with `india-data-protection-rider.md`.

## Summary for the CISO

PLUMB Advisory is a small advisory firm. It does **not yet hold ISO/IEC 27001 or a SOC 2 report**; it plans both, targeted for [[FOUNDER: month/year]]. Until then it relies on a small attack surface and compensating controls:

- **No connection to your networks.** PLUMB never connects to client OT or IT networks and needs no remote access. Data arrives as read-only exports pulled by your IT.
- **Your data can stay with you.** Raw data can be analysed in a workspace you host and control, with no AI model calls ("LLM-off").
- **Few people, named.** Only the named engagement personnel have access, on PLUMB-managed devices with phishing-resistant MFA.
- **Fast incident notice.** Within [2] hours to your named contact, so you can meet the 6-hour CERT-In clock.
- **Deletion with a certificate** at the end of the engagement.

## Standard answers

| # | Area | Question a CISO asks | PLUMB answer |
|---|---|---|---|
| 1 | Certifications | ISO 27001, SOC 2, other? | None yet. Planned: SOC 2 Type II and ISO 27001, target [[FOUNDER: date]]. Interim: [[FOUNDER: CSA Cyber Essentials mark (Singapore) — obtained / applied / not planned]]. Compensating controls below; audit right in the data-protection rider |
| 2 | Devices | Which devices touch our data? | Only PLUMB-owned laptops issued to named personnel. No personal, shared or third-party devices. [[FOUNDER: device count and OS]] |
| 3 | Device management | MDM / EDR? | All devices enrolled in [[FOUNDER: MDM product]]; [[FOUNDER: EDR product]] active; OS and browser auto-update enforced; firewall on; screen lock ≤ [5] minutes; remote wipe enabled |
| 4 | Encryption | At rest and in transit? | Full-disk encryption on every device ([[FOUNDER: FileVault / BitLocker]]); tenant storage encrypted at rest by the provider; TLS 1.2+ in transit; files exchanged only over encrypted channels |
| 5 | Tenant | Where is our data held? | A PLUMB-owned [[FOUNDER: Microsoft 365 / Google Workspace]] tenant in [[FOUNDER: region]], separate from any other organisation's tenant; or, by preference, in a workspace you host (option A in the rider) |
| 6 | Identity and MFA | How is access authenticated? | Single identity provider; MFA enforced for every account, [[FOUNDER: FIDO2 security keys / passkeys]] for admins; no shared accounts; conditional access limited to managed devices |
| 7 | Access control | Who can see our data? | Named engagement personnel only (listed in the SOW), least privilege, per-engagement workspace; access removed within 1 working day of leaving the engagement; quarterly access review |
| 8 | Logging | What is logged, how long? | Sign-ins, file access and admin actions in the tenant audit log; retained [[FOUNDER: ≥ 180 days]]; available to you on request. Region of log store: [[FOUNDER]] |
| 9 | Incident response | Do you have a plan? Notice time? | Written incident-response procedure, tested [[FOUNDER: last tabletop date]]. Notice to your named contact within [2] hours of awareness; written update within [24] hours; full report within [48] hours. 24/7 contact: [[FOUNDER]] |
| 10 | Backup | How is data backed up and restored? | Provider-native versioning and retention on the tenant; no client raw data on removable media; restore tested [[FOUNDER: date]]. Back-ups are covered by the deletion commitment (expire within [[FOUNDER: N]] days) |
| 11 | Personnel | Confidentiality, screening, training? | Every person signs a confidentiality agreement and PLUMB's insider-trading undertaking before access; [[FOUNDER: background-check practice]]; annual security and data-protection training |
| 12 | Subcontractors | Who else processes our data? | Only providers listed in the sub-processor register in the rider, each with written confirmation of region, retention and no training; obligations flowed down; [10] working days' notice of changes with your right to object |
| 13 | Data residency | Where is data processed? | As stated per provider in the register; India-hosted (your workspace) on request. No transfer to any country restricted under the DPDP Act |
| 14 | Deletion | How and when is data deleted? | Per item in the data request schedule; at the latest [30] days after final deliverable; deletion certificate listing items, systems (including sub-processors), method and date |
| 15 | AI tool use | Do you use AI on our data? | Only items you mark "LLM route: Y", only through listed model APIs with [[FOUNDER: zero data retention / stated retention]] and no training on your data. Raw data and any UPSI default to LLM-off. Every AI-assisted output is reviewed and owned by a named PLUMB professional |
| 16 | OT | Will you connect to plant systems? | No. No network connection, no remote access, no USB into OT. See `ot-rules-of-engagement.md` |
| 17 | Vulnerability management | Patching, testing? | Managed devices patched automatically within [14] days (critical within [3]); SaaS-only estate, no PLUMB-hosted servers. No penetration test yet: [[FOUNDER: planned date / not applicable]] |
| 18 | Email security | Phishing, spoofing? | SPF, DKIM and DMARC ([[FOUNDER: policy]]) on the PLUMB domain; provider-native phishing and malware filtering |
| 19 | Insurance | PI and cyber cover? | Professional indemnity [[FOUNDER: insurer, limit, expiry]]; cyber [[FOUNDER: insurer, limit, expiry / not held]]. Certificates on request |
| 20 | Business continuity | What if a key person is unavailable? | Named deputy for each engagement role [[FOUNDER]]; all work in the tenant, none on local disks only |
| 21 | Policies | Can we see your policies? | Information security, acceptable use, incident response, data retention and AI-use policies available under NDA [[FOUNDER: confirm each exists and is dated]] |

## Open items before first use

| Item | Owner |
|---|---|
| Fill every `[[FOUNDER]]` from live configuration; screenshot evidence kept in the internal file | Founder |
| Decide on CSA Cyber Essentials as an interim mark | Founder |
| Confirm insurance lines with the broker before quoting them | Founder; counsel |
