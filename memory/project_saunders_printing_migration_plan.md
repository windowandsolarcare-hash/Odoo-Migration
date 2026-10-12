---
name: project_saunders_printing_migration_plan
description: "DJ's plan (2026-10-11) to bring SAUNDERS PRINTING accounting into Odoo (company 3) like W&SC was, and retire the old QuickBooks 2010 Desktop (runs in a Parallels Windows VM on DJ's old Mac). Two accounts: Amex (expenses) + Chase checking (revenue + debit card). Accrual basis. Invoices already converted into Odoo."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-11
---

**DJ's SAUNDERS PRINTING plan (stated 2026-10-11).** Saunders Printing = **Odoo company 3** (W&SC=1, Cheryl=2, Saunders=3). Goal: migrate its accounting into Odoo so it carries its OWN sales/customers/accounting, and **retire the old QuickBooks 2010 Desktop** (a pre-cloud app running in a **Parallels Windows VM on DJ's old Mac ~2012 / old macOS**; NO API/connector; raw .QBW unreadable; extraction = export reports from within QB, or computer-use on a session running on that VM — but likely NOT needed for the tax return).

**Two accounts only (tight/simple):**
- **American Express** (Business Cash Rebate, ending 11003) = MOST expenses. 2025 already pulled = **$12,290 business** (Zoo Printing COGS $8,536 + storage $2,452 + subs $622 + interest $680); see [[project_dj_tax_filing_2025]]. Domain SCENICC = scenicartprint.com.
- **Chase checking** = where REVENUE comes in; ALSO a debit card for the non-Amex expenses (debits out of Chase). (Which Chase acct = TBD; may differ from W&SC's 9008.)
- Revenue is SMALL: **~$20k/yr or less**. 2024 return Saunders Sch C = gross $19,755 / net $5,642 (template, [[project_dj_2024_return_schedule_c]]).

**★ ACCRUAL BASIS (key difference from W&SC's cash basis):** DJ invoices (often LATE in the year) and reports revenue in the YEAR INVOICED, receives payment the FOLLOWING year. So YEAR-BOUNDARY timing matters — a Dec-2024 invoice paid Jan-2025 = 2024 revenue. Watch cross-year items (invoice in 24 / paid in 25 or 26).

**Invoices ALREADY in Odoo:** DJ built a production-tracking app LAYERED on Odoo (tracks artwork upload / ship / invoice) but underneath uses Odoo correctly -> he has **already converted all Saunders invoices into Odoo company 3** ("almost certain it's right" — VERIFY). So revenue/invoices should already be in Odoo co3.

**BUILD PLAN:** do 2024 first (expenses + revenue), then 2025 + 2026 TOGETHER (small amounts), catch cross-year accrual items; wire up the 2026 bank feed. For the TAX return, build Saunders 2025 Sch C from **Amex ($12,290) + Chase deposits (revenue) + 2024 template** — probably WITHOUT QB 2010. DJ will DOWNLOAD the Amex + Chase data (he's fine doing that, like the cards). This is a NEW, distinct workstream from W&SC — a natural session breakpoint. See [[project_quickbooks_retired]], [[project_accounting_migration_unfinished]].
