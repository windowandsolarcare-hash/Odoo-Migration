---
name: project_accounting_migration_unfinished
description: "★ RESUME POINT: the QuickBooks→Odoo accounting migration is NOT finished (DJ confirmed 2026-10-11) — it HALTED after Stage 2 on 2026-06-24 waiting on DJ's year-end-2024 balances. project_quickbooks_retired's 'effectively done' = operational only (stop routing to QB), NOT structural. The finish checklist + live state."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-11T19:59:00.237Z
  originSessionId: c55fb80c-b5c7-4e62-a78d-f46e55b25f48
---

**DJ 2026-10-11:** "our accounting went from quickbooks to now Odoo, we did a migration but we didn't finish it. Finish the Odoo accounting, get it up to date, then do taxes — taxes are due this week." Chose the **tax-first fast path** (get a clean 2025 P&L to the CPA for the ~Oct-15 return; balance-sheet tie-out comes right after, not blocking the filing).

**★ CONFLICT RESOLVED:** [[project_quickbooks_retired]] (2026-09-09) says the migration is "effectively done / Odoo authoritative." That is TRUE operationally (stop routing financial questions to QuickBooks; Odoo is the source going forward) but FALSE structurally — the balance-sheet/opening-balance finish was never done. Trust DJ's live word: NOT finished. Read [[project_accounting_master_plan]] + [[project_opening_balances_needed]] + [[project_bank_feed_qb_double_booking]] for the full strategy.

**Where it stalled:** the `5_Accounting/` scripts + audit logs STOP at **2026-06-24 (Stage 2)**. Nothing accounting-structural has run since. Work was blocked awaiting the "shopping list" DJ never returned: year-end-2024 balances for the 4 credit cards, Ford Transit loan, Van Shelving loan, Notes Payable–Saunders, Chase, + a QB **Fixed Asset List** export.

**Strategy (locked, don't re-litigate):** QB accurate through 2024-12-31; Odoo owns Jan 1 2025 forward (bank-feed overlap cutover 2024-11-25). DON'T hand-reconcile old QB — set **opening balances** at cutover from real statements. Revenue = Odoo/Workiz (done). Expenses = QB CSV import (done, ran 2019→~2026-05-31). 🎯 Proof-of-correct = Odoo Chase ties to the REAL Chase balance (~$1,000).

**LIVE STATE (verified via XML-RPC 2026-10-11, company_id=1, posted):**
- P&L: **2024** Rev $91,721 / Exp $50,925 / Net $40,796 · **2025** Rev $79,877 / Exp $47,074 / Net $32,803 · **2026-YTD** Rev $59,371 / Exp $11,760 / Net $47,611 (2026 expenses are SPARSE — QB import stopped ~2026-05-31; 2026 net is inflated, NOT real).
- 2025 income = one account (400000 Product Sales $79,877). 2025 expenses categorized across ~18 accounts (top: Raw Materials $8,690, Office Supplies $7,775, Meals $5,674, Dues $4,043, Fuel $3,732, Auto Ins $3,493, Advertising $2,819, Utilities $2,780, Office Rent $2,647...).
- **Chase 101401 = $59,143** (was $36,081 after Stage 2; target ~$1,000 → gap GREW to ~$58K as 4 months posted with no tie-out). Outstanding Receipts 101403 = $5,723 (should net ~$0). Venmo 101405 = $14,654.
- **Opening Balance Equity 309000 = $0 → opening balances were NEVER set** (the core unfinished item).
- Credit cards (Discover/Discover II/Shop Your Way/Thank You) ALL $0 — card debt absent from the balance sheet.
- Loans: only **Toyota 291200 = $13,374** on the books; **Ford 291100 / Van Shelving 291300 / Notes Payable 291400 all $0**.
- **Fixed assets: 30 accounts, ALL $0** → no vehicles/equipment, NO depreciation flowing to the P&L.

**THE FINISH CHECKLIST (what remains):**
1. DJ's year-end-2024 balances (the shopping list) — the actual blocker.
2. Opening-balance JEs at cutover → ties Chase to the real balance (lever to ~$1,000).
3. Stage 3 — credit-card income-settlement cleanup (batch + processing fees).
4. 30 Stage-2 residuals (parked in Outstanding Receipts).
5. 2 personal credit cards → liabilities on the balance sheet (via opening balance; link feeds later, start past the QB import).
6. Loans Ford / Van Shelving / Notes Payable — principal-vs-interest setup (Toyota done).
7. Fixed assets + depreciation (all $0 now) — **this one moves the taxable number**.
8. Confirm expense completeness (2026 expenses incomplete; 2025 appears complete).
9. Validate P&L vs QB for 2024 + balance sheet vs real accounts.

**TAX-RELEVANT (for the 2025 return):** the P&L net is the core number and 2025 is fully imported ($32,803 net). The P&L-affecting gaps are (a) **missing depreciation** (needs the Fixed Asset List) and (b) **loan interest** — 704000 Loan Interest Expense did NOT appear in the 2025 breakdown though memory says a Toyota 2025 interest reclass ($1,981) was booked; verify it posted. Meals $5,674 are 50%-deductible (CPA adjusts). ENTITY TYPE is an open DJ-only question (W&SC is noted as a DBA of Saunders Printing — affects WHICH return/form). Accounting prepares DRAFT analysis; DJ's CPA signs/files. See [[feedback_assistant_use_app_workflow_not_raw_api]] (any money write → Operator, never raw RPC), [[user_accounting_knowledge]].

**CASH-AT-DOOR / SAFE = the Chase tie-out gap (DJ clarified 2026-10-11).** DJ keeps cash taken at the door in a HOME SAFE and does NOT deposit it to Chase. So: REVENUE is still correct/complete (recognized at INVOICE time in Odoo, regardless of deposit -> the $79,877 includes cash jobs; NOT under-reported). The HOLE is purely balance-sheet/cash: the migration recorded cash payments as if they hit Chase (Dr Chase/Cr AR), but the money is in the safe -> Odoo Chase balance is OVERSTATED (shows ~$59K vs real ~$1K) and there's no 'Cash on Hand' asset for the safe money. FIX (balance-sheet work, not tax): move the never-deposited cash off Chase to **Cash on Hand 101406** (if still in safe) or **Owner's Draw 312000** (if spent personally) -- consistent with the Stage-1 routing (cash->Owner's Draw) in [[project_bank_feed_qb_double_booking]]. DOES NOT affect the Schedule C net / tax number (revenue already captured via invoices). Pure cash-tracking cleanup for when the balance sheet is built.