---
name: project_2025_qb_vs_odoo_reconciliation
description: "2025 reconciliation QuickBooks (W&SC company, cash basis) vs Odoo (company 1). QB Net $43,241 vs Odoo Net $32,803 vs return-style ~$15K. Feed-driven categories match to the dollar (trustworthy); both MISS the two biggest Schedule C deductions — full vehicle (mileage) + contract labor. Pulled live 2026-10-11."
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
- **★ BOTH MISS THE TWO BIGGEST SCHEDULE-C DEDUCTIONS** (why both nets are far above the ~$15K the filed return would show):
  1. **VEHICLE** — QB books ACTUAL ($8,817); the 2024 return used **standard mileage ($17,582)**. 2025 mileage (if ~similar miles ≈ 26k × ~$0.70) ≈ **~$18K** → roughly **$9K more deduction** than QB's actual. Standard mileage wins; need 2025 miles.
  2. **CONTRACT LABOR** — 2024 return had **$15,750**; 2025 shows only **$2,000 (QB) / $1,000 (Odoo)**. If DJ used helpers in 2025, **~$13K+ is missing** — likely paid by Zelle/Venmo/cash and landing as "uncategorized/transfer," not "Contractors." **THE single biggest open question.**

## Bottom line for the return
Neither QB ($43,241) nor Odoo ($32,803) is tax-correct yet — both overstate net because they lack mileage + contract labor (+ home office $650). Rebuild 2025 Schedule C on the **2024 filed-return method** ([[project_dj_2024_return_schedule_c]]) → real net likely back near **~$15-20K**, dropping the TurboTax **$14,649** owed substantially. Arbiter = the filed-return methodology, not QB or Odoo raw. See [[project_dj_tax_filing_2025]], [[project_accounting_migration_unfinished]]. QB MCP connector (re-auth via /mcp) gives cheap structured P&L/Balance-Sheet pulls; computer use for transaction-level categorization detail the MCP can't export.
