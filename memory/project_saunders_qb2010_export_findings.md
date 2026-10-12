---
name: project_saunders_qb2010_export_findings
description: "★ Saunders Printing QB Pro 2010 export analyzed 2026-10-12. QB has CLEAN revenue (accrual invoices) but EMPTY expenses (1 entry). Rebuild = QB revenue + Amex/Chase expenses mapped through the QB chart of accounts. Revenue: 2024≈$22,141, 2025≈$39,725, 2026=none."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T15:59:13.071Z
---

**DJ exported from QuickBooks Pro 2010 Desktop (Saunders Printing, co3) on 2026-10-12** — two files: a Transaction Detail CSV and a full-list IIF (chart of accounts). QB can't API; export path = report→CSV (transactions) + File→Utilities→Export→Lists to IIF (lists). Accountant's Copy (.QBX/.QBA/.QBY), backup (.QBB), portable (.QBM) are all proprietary binary = NOT readable by me; only IIF (tab-delimited text) and report CSV are.

**★ KEY FINDING — QB was kept up to date on REVENUE ONLY, not expenses.** The Transaction Detail (Jan 2024–Oct 2025) contains invoices (almost all National Baseball Hall of Fame + 1 International Spy Museum), their payments, and Chase deposits — but **exactly ONE expense entry in ~2 years** ($100 AT&T phone check, 3/6/2024). So:
- **Revenue (accrual, invoiced) comes from QB and is clean.** By year: **2024 ≈ $22,141.26** (inv #200201–200214); **2025 ≈ $39,725** (inv #200216–200233 through 10/27/25 — higher than the old ~$20k/yr guess); **2026 = nothing entered**. Artifacts of the neglect: inv #200215 missing; check #70666 ($7,858.37) dated both 5/21/2024 (deposit) and 5/21/2025 (payment) — the $7,858.37 = the 4/16/25 invoice batch 200216-200222, so real pay date is 2025; month gaps (no Sept–Dec 2024, no Jan–Mar 2025 invoices). Reconcile against actual Chase deposits.
- **ALL expenses + COGS must be reconstructed from Amex + Chase** (the card-pull via computer-use). COGS = "Print Manufacturing" (payments to the actual postcard printer) — hunt the recurring print vendor in the feeds.

**★ QB CHART OF ACCOUNTS (the categorization map, from IIF) — maps ~1:1 to Schedule C.** OBAMOUNT values in the IIF are stale lifetime/opening balances, NOT single-year — ignore for tax. Accounts:
- BANK: Chase (6), BBVA Checking, Paypal, Petty Cash. CCARD: American Express (51, "AM EX Business"), CitiBank (69, "used rarely – toll roads & misc"), Costco Visa (65). AR (11000), Undeposited Funds, Inventory Asset, Loan to WASC, Sales Tax Payable.
- INCOME: Sales (47900), Sales Discounts, Shipping and Delivery Income (48900, = freight billed to customer, part of gross receipts), Credit Card Credit (rebates).
- COGS: Print Manufacturing (the big one), Freight Costs (51200), Merchant Account Fees, Commissions Paid, Cost of Goods Sold.
- EXP: Advertising & Promotion, Auto and Truck, Bank Service Charges (+PayPal fee sub), Business Licenses & Permits, Computer and Internet, Depreciation, Dues & Subscriptions, Employee Retirement Exp, Equipment Rental, Insurance (Gen Liability/Health/Life&Disab/Worker's Comp subs), Interest Expense, Marketing, Meals & Entertainment, Miscellaneous, Office Expense, Office Supplies, Postage & Delivery, Printing & Reproduction, Professional Fees, Rent Expense, Repairs & Maintenance, Sales Tax, Taxes-Property, Telephone, Travel, Utilities. Plus "Ask My Accountant" clearing acct.

**★ ACCOUNTS: DJ says Chase + Amex are the only two accounts used now** (2026-10-12), despite COA also listing Costco Visa + CitiBank with stale nonzero balances. BUILD on Chase + Amex; but CONFIRM nothing ran through Costco/Citi in tax years 2024–26 before declaring expenses complete. (old act's card-pull playbook had assumed Amex + Amazon/Prime Visa(Chase) + Costco Visa(Citi) — that list was W&SC-flavored; Saunders = Chase + Amex per DJ.)

**OPEN DECISIONS before building Saunders Schedule C:**
1. **Cash vs accrual basis** — QB was accrual; NBHOF pays months after invoice so the two bases differ across year boundaries. Match whatever prior Saunders returns used (CPA question). Build BOTH views.
2. Costco/Citi used in 24–26? (see above).

**Files:** Detail_TX.CSV + QB_DJ.IIF in uploads/d70db154-.../. See [[project_accounting_next_priorities]] (#1 Saunders setup), [[project_saunders_printing_migration_plan]], [[project_2025_schedule_c_categorized]] (W&SC, separate). Amex is mostly Saunders co3 — watch attribution vs W&SC. Reconstruction = QB revenue + Amex/Chase expenses → QB COA → Schedule C. Money writes via Operator/app, never raw RPC.
