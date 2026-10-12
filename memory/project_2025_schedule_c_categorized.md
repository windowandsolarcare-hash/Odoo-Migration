---
name: project_2025_schedule_c_categorized
description: "★ W&SC 2025 Schedule C, CATEGORIZED from Odoo (built 2026-10-11). Corrects the double-count in the emailed ~$9-13K worksheet: Citi + Amazon card purchases are ALREADY in Odoo, NOT new. Corrected DRAFT net = ~$23,583."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T05:46:02.109Z
---

**Built 2026-10-11 (Accounting) from live Odoo XML-RPC, company_id=1, posted, 2025.** Supersedes the "add the card totals on top of Odoo" approach that produced the emailed ~$9–13K net.

**★ CORRECTION to [[project_2025_qb_vs_odoo_reconciliation]]:** that memory said the Citi ThankYou card ($8,726) was "ALL NEW 2025 deductions, no duplicate risk" and Amazon Prime (~$3K) likewise. **FALSE — verified in Odoo:** the Citi vendors (Workiz, Angi, Thumbtack, Active Window, WindowCleaner, WPForms, Simpole, Orbit, HP Instant Ink) and $1,122 of Amazon are **already booked as 2025 expenses in Odoo** (mostly journal j3 QB-CSV import, full year — not just Jan–Apr). Adding the $8,726 Citi + ~$3K Amazon totals ON TOP of Odoo DOUBLE-COUNTS and understated the net by ~$11–12K. **Build the P&L FROM Odoo** (it already contains the card purchases) and add only what's genuinely missing. (The j6 "CITI THANKYOU / SHOP YOUR WAY MC" lines in the Chase feed are card PAYMENTS = debt paydown, correctly not expenses.)

**AUTHORITATIVE Odoo 2025 P&L (internal_group income/expense, co1, posted):** Income $79,877.00 · Expenses **$49,054.82** · Net **$30,822.18**. NOTE the common "$47,074 / net $32,803" figure OMITS acct 704000 Loan Interest Expense $1,981.22 (Toyota reclass, posted, 1 line) — include it; true net is $30,822.

**Odoo 2025 expense accounts:** 601000 Raw Materials 8,690.27 · 601100 Job Supplies 191.88 · 623000 General Subcontracting 1,000.00 (=the Danny IT already booked) · 625000 Dues & Subscriptions 4,042.93 · 631000 Office Rent 2,647.28 · 642000 Utilities 2,780.14 · 650000 Bank Fees 15.00 · 651200 Repairs & Maint 1,288.18 · 651500 Office Supplies 7,775.17 · 654000 Software 508.03 · 655300 Professional Insurance 222.98 · 656000 Licenses & Permits 104.00 · 665500 Vehicle Repairs 1,655.41 · 667000 Fuel 3,732.38 · 668000 Auto Insurance 3,493.02 · 671000 Meals & Ent 5,674.40 · 673000 Advertising 2,818.52 · 690000 Misc 434.01 · 704000 Loan Interest (Toyota) 1,981.22.

**CATEGORIZED SCHEDULE C (DRAFT net ≈ $23,583):**
- L8 Advertising 2,818.52 · L9 Car&truck 10,266 (14,665 mi × $0.70 std mileage — REMOVES Odoo Fuel+AutoIns+VehRepairs $8,880.81) · L11 Contract labor 4,425 (Odoo $1,000 + $3,425 remaining Danny Zelle IT) · L15 Insurance non-health 222.98 · L16b Interest 3,786.22 (Toyota loan 1,981.22 + Citi card interest 1,805 NOT yet in Odoo) · L18 Office 12,326.13 (OfficeSupplies+Dues+Software) · L20b Rent 2,647.28 · L21 Repairs 1,288.18 · L22 Supplies 8,882.15 (RawMat+JobSupplies) · L23 Taxes&licenses 745 (Permits 104 + employer payroll tax 641) · L24b Meals 2,837.20 (50% of 5,674.40) · L26 Wages 4,950 (Danny W-2 2,250 + owner 2,700) · L27a Other 449.01 (BankFees+Misc).
- L28 Total expenses 55,643.67 · L29 24,233.33 · L30 Home office 650 (simplified 130 sq ft) · **L31 NET PROFIT ≈ 23,583**.
- **Owner $2,700 W-2 WASHES** (deducted L26, added back 1040 line 1a).

**Genuinely NOT in Odoo (so added here):** remaining Danny Zelle IT $3,425 (Odoo had only $1,000); Gusto wages $4,950 + employer payroll tax $641 (payroll accts 611000/616000 don't exist, $0); Citi card interest $1,805 (Odoo has only Toyota loan interest); home office $650.

**STILL OPEN:** (a) Amazon Prime card business remainder — needs DJ biz/personal split; $1,122 already booked in Odoo Raw Materials, don't re-add. (b) SEP/Solo-401k (none funded — biggest ↓ lever). (c) SE health insurance (DJ said none). (d) Meals 751 txns / $5,674 — verify all business. (e) Possible Workiz spread across Dues ($3,792) + Office Supplies ($3,712) — likely real (card renewal + Chase ACH both), but glance. (f) This is W&SC ONLY — Saunders Printing co3 is a separate Schedule C still to build.

**DRAFT analysis for DJ / his CPA — DJ self-files. Any money write → Operator via app, never raw RPC** ([[feedback_assistant_use_app_workflow_not_raw_api]]). See [[project_dj_tax_filing_2025]], [[project_dj_2024_return_schedule_c]], [[project_accounting_migration_unfinished]].
