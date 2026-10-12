---
name: project_wsc_odoo_opening_balances
description: "★ W&SC (co1) Odoo migration used FULL TRANSACTION IMPORT, not a 1/1/2025 opening-balance entry (checked 2026-10-12). Bank/AR balances derive OK; credit-card balances, real loan payoff, and fixed assets are MISSING/wrong. Doesn't affect cash-basis taxes; balance-sheet completeness only."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T18:24:52.219Z
---

**Checked 2026-10-12 (Accounting, DJ asked whether the migration set opening balances as of 1/1/2025).** Queried account.move.line company_id=1, date<=2024-12-31, posted. FINDING: the W&SC→Odoo migration imported **full transaction history** (e.g. Chase 4,048 pre-2025 lines, AR 3,620, Product Sales 2,512) — NOT a single opening-balance JE. So 2025 opening balances are DERIVED from cumulative pre-2025 lines, not stated. (This is also why the QB-import duplicates exist — see [[project_2025_schedule_c_categorized]].)

**DERIVED balances present as of 12/31/2024 (company 1):**
- 101401 Chase Checking (9008): $30,560.13 (verify vs Dec-2024 stmt)
- 101405 Venmo: $12,679.05 (⚠ all debits/no credits — looks off, verify)
- 101402 Bank Suspense: $1,849.86 (should clear ~0) · 101403 Outstanding Receipts: $395.00
- 121000 Accounts Receivable: $475.00 · 251000 Tax Received: -$7.29
- 291200 Toyota Loan: $712.16 (⚠ only 2 lines dr900/cr187.84 — NOT the real truck payoff, wrong)
- 312000 Owner's Pay & Personal Expenses (equity/draws): $51,166.82

**MISSING opening balances (all $0 in Odoo, need real 12/31/2024 figures):**
- CREDIT CARDS: 201230 Thank You Card (Citi), 201220 Shop Your Way Mastercard, 201200/201210 Discover ×2, 201100 Credit Card — charges imported as expenses but card LIABILITY balance never set.
- LOANS: real Tacoma payoff (the $712 is wrong), 291100 Ford Transit 250 Loan, 291300 Van Shelving Loan, 291400 Notes Payable-Saunders — missing/zero.
- FIXED ASSETS: 155500 Vehicles, Technology, Furniture, 151000 Accum Deprec — none (may be INTENTIONAL: W&SC uses standard mileage, truck not capitalized).
- 211000 Accounts Payable: $0 (confirm no unpaid vendor bills at 12/31/2024).
- Equity: 309000 Opening Balance Equity / 311000 Owner's Investment / Capital = unused.

**IMPACT: none on 2025 cash-basis taxes** (Schedule C = income/expense, not balance sheet). This is balance-sheet completeness only. NOTE chart has duplicate template accounts (unnumbered "Bank"/"Credit Card" placeholders vs numbered real ones).

**NEXT (pending DJ):** pull credit-card + loan 12/31/2024 balances via computer-use (same method as the Amex/Chase pull), then Operator posts a clean opening-balance JE (offset to 309000 Opening Balance Equity). Reversible/additive — fits DJ's no-irreversible-delete rule. See [[project_saunders_qb2010_export_findings]], [[feedback_assistant_use_app_workflow_not_raw_api]].
