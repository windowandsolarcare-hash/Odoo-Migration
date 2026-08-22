---
name: project_wsc_llc_formation
description: "Window & Solar Care is now a CA LLC (entity B20260293155, filed 6/23/2026) — supersedes the old sole-prop structure; Statement of Information due ~9/21/2026"
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

**Window & Solar Care, LLC** was formed with the California Secretary of State (bizfile Online). Approval email from no_reply@sos.ca.gov landed in windowandsolarcare@gmail.com 2026-06-25.
- Entity / Document No.: **B20260293155** (Articles of Organization – CA LLC)
- File Date: **06/23/2026**, approved 06/25/2026
- Lookup / free filed-doc copies: bizfileOnline.sos.ca.gov (search entity name or number). SOS: (916) 657-5448.

**LLC's own federal EIN obtained 2026-06-27 (resolves the earlier "does the LLC have its own EIN?" unknown):**
- **EIN = 42-3461012** (IRS CP575A issued 06/27/2026). IRS name control **WIND**.
- IRS-registered legal name: **WINDOW & SOLAR CARE LLC** (NO comma — IRS legal-name field rejects commas; `&` is allowed). Member: Daniel Joseph Saunders III, Sole Mbr. Address 32569 San Miguelito Drive, Thousand Palms CA 92276.
- This is SEPARATE from the old Saunders Printing sole-prop EIN 87-3872426 — use 42-3461012 for the LLC going forward (Twilio Trust Hub, Gusto/payroll, bank, W-9s, invoices).
- IRS-stated filing obligations on the CP575: **Form 941 (quarterly payroll) due 10/31/2026**, **Form 940 (FUTA) due 01/31/2027** — Gusto handles these once payroll runs under this EIN.
- **The two EIN PDFs (IRS CP575 letter + online confirmation) are FILED IN THE APP** → Reference (/owner/reference) → card "Window & Solar Care, LLC - CA SOS Filing" (card id 1782408185597) → Documents section (ir.attachment 2211 = CP575 letter, 2212 = online confirmation; served via /owner/api/attachment_image?att_id=). EIN also added to that card's body text. This also added a NEW capability: Reference cards now support **file attachments** (reference.py `/api/reference/attach` + `/file-delete`; reference.html Documents section per card, 📎 badge in list). See [[project_reference_quickref]]. GOTCHA: `ir.attachment.create([{...}])` returns the id as a 1-element LIST; flatten before storing. Don't put the card's JS-timestamp id as `res_id` over XML-RPC (exceeds XML-RPC int limit; app's odoo_rpc is JSON-RPC so it's fine there).
- EIN application answers used (for reference): reason "Started a new business"; LLC start date June 2026; highest employees next 12mo = 2 (David + son), agricultural 0; employment-tax-liability ≤$1,000? **No** (→ quarterly 941, matches Gusto); not S-corp at EIN stage (separate 2553 election TBD with CPA).

**This SUPERSEDES the old structure** noted in [[project_workers_comp_shopping]] ("sole prop Saunders Printing dba W&SC, FEIN 87-3872426"). Downstream items that may need to reflect the LLC now: workers-comp policy named insured, Gusto/payroll employer entity, bank account, insurance, invoices/quotes. NOT yet reconciled — flag when any of those come up.

**Hard deadline:** Statement of Information (SOI) due **within 90 days** of filing → ~**09/21/2026**, then every 2 years.
- Filed in DJ's Reference notes (/owner/reference, ir.config_parameter `owner.reference.cards`, card "Window & Solar Care, LLC - CA SOS Filing"). See [[project_reference_quickref]].
- My Day reminder = project.task **id 1154** "📋 File CA Statement of Information — DUE Sept 21 (W&SC LLC)", dated 2026-09-05, x_myday_recur='daily', x_myday_priority=3, user 2. See [[project_myday_reminders]].

Reusable how-to (verified 2026-06-25): create a My Day to-do via direct Odoo `project.task` create — fields `x_myday_type='task'` (or 'habit'), `x_myday_recur` in daily/weekdays/weekly/biweekly/monthly/6months (char), `x_myday_priority` int (3=High), `date_deadline` 'YYYY-MM-DD HH:MM:SS' UTC (use ~15:00 UTC = 8am PDT for a date-only feel), `user_ids=[(6,0,[2])]`, no project/stage needed. Mirror task 1009. NOTE: `x_myday_tags` is NOT a field on project.task (read errors).
