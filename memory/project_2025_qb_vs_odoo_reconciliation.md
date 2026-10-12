---
name: project_2025_qb_vs_odoo_reconciliation
description: "2025 reconciliation QuickBooks (W&SC company, cash basis) vs Odoo (company 1). QB Net $43,241 vs Odoo Net $32,803 vs return-style ~$15K. Feed-driven categories match to the dollar (trustworthy); the biggest Schedule C deduction gap is the vehicle (standard mileage vs the actual costs booked). Pulled live 2026-10-11."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-11T22:11:55.417Z
  originSessionId: c55fb80c-b5c7-4e62-a78d-f46e55b25f48
---

**2025 P&L reconciliation, pulled live 2026-10-11.** QuickBooks via computer use (QBO "Window & Solar Care" company, **Cash basis**, Jan–Dec 2025); Odoo via XML-RPC (company_id=1, posted, 2025). DJ's rule: QB dollar AMOUNTS are reliable (bank feeds) but CATEGORIZATION is suspect; 2026 QB is NOT accurate (ignore). Focus = 2025 (tax year). This QB company = W&SC only (Saunders Printing is a separate Schedule C, likely separate/manual books).

## Top line
| | QuickBooks 2025 | Odoo 2025 |
|---|---|---|
| Total income | **$85,849.01** | **$79,877** |
| Total expenses | **$42,607.82** | **$47,074** |
| **Net income** | **$43,241.19** | **$32,803** |

## QB 2025 income detail
Sales: Gutter 1,440 · Misc 1,363 · Pressure Washing 580 · Screen Repair 440 · Window Cleaning 42.50 = Total Sales $3,865.50 · **Services 63,868.51** · **Unapplied Cash Payment Income 17,765.00** (QB mess — payments not matched to invoices; DJ's categorization concern) · Workiz tips 350 → **Total $85,849.01**. Odoo income = one account "Product Sales $79,877" (invoice-based). Different bases; QB's $17,765 unapplied cash is the main reconciling/uncertainty item — drill if needed.

## QB 2025 expense detail (cash)
Advertising/Lead Gen 1,409.26 · Bank Charges 15.00 · **Car & Truck $8,816.94** (direct 1,560.62 + Auto Ins 3,493.02 + Fuel 3,668.51 + Veh Maint 94.79) · **Contractors 2,000.00** · Dues 250.93 · Insurance 222.98 · Interest Paid 3,046.25 · Job Supplies 191.88 · Meals & Ent 5,543.80 · Office Supplies & Software 7,635.34 (direct 7,351.93 + Scheduling 80 + Software-Other 203.41) · Other Business 77.42 · Rent & Lease 2,647.28 · Repairs & Maint 1,288.18 · Supplies & Materials-Not Job Specific 6,566.20 · Taxes & Licenses 99.00 · Uncategorized 17.22 · Utilities 2,780.14 → **Total $42,607.82**.

## Who's right (the findings)
- **MATCH TO THE DOLLAR (both pull the same feed → trust these):** Rent **$2,647** · Utilities **$2,780** · Auto Insurance **$3,493** · Bank Fees **$15**. Close: Meals (QB 5,544 / Odoo 5,674), Fuel (QB 3,669 / Odoo 3,732), Office+Software (QB 7,635 / Odoo ~8,283).
- **DIVERGE (categorization):** Advertising (QB 1,409 / Odoo 2,819) · Supplies (QB 6,566 / Odoo 8,690 "Raw Materials") · Contractors (QB 2,000 / Odoo 1,000) · Interest Paid (QB 3,046 / Odoo ~0 — Odoo missing loan interest). These are classification differences, not amount errors.
- **★ BOTH MISS A BIG SCHEDULE-C DEDUCTION** (why both nets are above the ~$15-20K a properly-built Schedule C would show):
  1. **VEHICLE** — QB books ACTUAL ($8,817); the 2024 return used **standard mileage ($17,582)**. 2025 mileage (if ~similar miles ≈ 26k × ~$0.70) ≈ **~$18K** → roughly **$9K more deduction** than QB's actual. Standard mileage wins; need 2025 miles.

## Bottom line for the return
Neither QB ($43,241) nor Odoo ($32,803) is tax-correct yet — both overstate net because they lack full vehicle mileage (+ home office $650). Rebuild 2025 Schedule C on the **2024 filed-return method** ([[project_dj_2024_return_schedule_c]]) → real net likely back near **~$15-20K**, dropping the TurboTax **$14,649** owed substantially. Arbiter = the filed-return methodology, not QB or Odoo raw. See [[project_dj_tax_filing_2025]], [[project_accounting_migration_unfinished]]. QB MCP connector (re-auth via /mcp) gives cheap structured P&L/Balance-Sheet pulls; computer use for transaction-level categorization detail the MCP can't export.

**★ 2025 UNRECONCILED CHASE FEED = the P&L gap (scoped live 2026-10-11).** Chase journal 6, 2025: 902 reconciled / **124 UNRECONCILED** lines parked in Bank Suspense (101402, 2025 bal $13,579), NOT allocated to any account → NOT on the P&L. Split: **60 expense OUTFLOWS = $31,554** (money out of Chase never categorized to an expense account → MISSING from the P&L → Odoo 2025 net OVERSTATED by the business portion) + **64 deposit INFLOWS = $17,975** (customer payments → MATCH to existing invoices, revenue already counted — do NOT re-book as income/double-count). Gusto payroll is inside the 60 (payroll accounts 611000 Salaries&Wages / 616000 Payroll Tax all $0 for 2025; ~$5,856 Gusto debits unreconciled). ★ FINISH-THE-2025-BOOKS STEP: allocate the 60 expense lines one-by-one — each is either a business expense (→ deductible, onto P&L) OR an owner draw/transfer (→ not an expense; commingling expected). THEN the P&L is accurate for the return. Allocation = money-touching book change → via app/Operator or a DJ-approved cleanup pass, NOT raw RPC by Accounting (read/analyze only). See [[feedback_assistant_use_app_workflow_not_raw_api]], [[project_accounting_migration_unfinished]].

**★ CREDIT-CARD FEEDS + MIGRATION VERIFIED (computer-use QB + Odoo RPC, 2026-10-11).** QB 'Bank transactions' flags **'Unable to get transactions for 2 accounts' (Error 377):** **Shop Your Way Mastercard** (last pulled **2025-04-04**) + **Thank You Card** (Citi). Chase checking (9008) still live (10/8/2026). Discover + Chase credit card (ending 7690) appear NOT connected to QB at all (seen only as Chase-feed payees). MIGRATION CHECK (Odoo co1 2025 expenses by journal): **Chase Checking j6 $31,833 (595 ln) + Miscellaneous Operations j3 (QB CSV import) $15,240 (1,244 exp ln, import covers →2026-05-31) = $47,074 total** (matches P&L). So QB-held card expenses DID migrate to Odoo via the j3 import. **GAP: card expenses AFTER the feeds died (~Apr 2025 Shop Your Way; Thank You; + the never-connected Discover/Chase-7690 cards) were never in QB → never in the CSV → NOT in Odoo = genuinely MISSING 2025 business deductions.** FIX: pull the actual 2025 year-end statements for Shop Your Way / Thank You / Discover / Chase-7690, extract business purchases, add them. This is a bigger hidden-deduction source than the unreconciled Chase feed (which is mostly card PAYMENTS, not expenses). Credit-card *payments* out of Chase are NOT deductible (debt paydown); the card PURCHASES are the deduction, and they live on the statements.