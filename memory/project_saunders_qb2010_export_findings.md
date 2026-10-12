---
name: project_saunders_qb2010_export_findings
description: "★ Saunders Printing QB Pro 2010 export analyzed 2026-10-12. QB has CLEAN revenue (accrual invoices) but EMPTY expenses (1 entry). Rebuild = QB revenue + Amex/Chase expenses mapped through the QB chart of accounts. Revenue: 2024≈$22,141, 2025≈$39,725, 2026=none."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T17:32:00.827Z
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

**★ BASIS = CASH, CONFIRMED (2026-10-12).** DJ's 2024 filed return (both Schedule Cs) = cash method ([[project_dj_2024_return_schedule_c]]). STAY CASH for consistency (DJ initially guessed accrual — wrong; the return settles it). Proof: 2024 Saunders return gross = $19,755 (cash collected) vs QB 2024 invoiced = ~$22,141 (accrual) — the gap is cash-vs-accrual timing. IMPLICATION: rebuild ANY year PURELY from Chase+Amex (revenue=deposits collected, expenses=card/bank spend); QB journal entries NOT needed for taxes. DJ's long-time method (total the Amex for what applied to Saunders = his "cost of goods") was valid cash-basis accounting. COGS vs Supplies line is just presentation — the printer payments are the cost of goods either way; same dollars, same deduction.

**★ SCOPE DECISION (DJ wrestling 2026-10-12; my rec): split two goals.** (1) TAXES = only need 2024/2025/2026 → Chase+Amex cash-basis rebuild. (2) PRESERVE QB DATA before abandoning QB = do NOT re-key 5yrs of JEs; instead run QB **Transaction Detail, date range = All → one CSV export** (+ P&L by year) — captures every year QB has incl. the accurate Cheryl-era years (pre-~2022, when JEs were done) — archive to Drive, I read it forever. (3) SKIP re-entering never-recorded dead years into Odoo (filed/closed, no tax benefit). WHY recent years are revenue-only in QB: only invoices were entered, never the expense JEs (DJ: "too lazy"); older Cheryl-era years have BOTH sides.

**OPEN:** Costco/Citi used in 24–26? (COA lists them with stale balances; DJ says Chase+Amex only now — confirm before declaring expenses complete).

**★★ 2025 SAUNDERS SCHEDULE C FINALIZED (cash, both sides pulled 2026-10-12 via computer-use).** Chase 8356 CSV (back to 10/15/2024) + Amex 11003 CSV. Revenue (deposits collected) = **$39,724.68** — TIES EXACTLY to QB 2025 invoiced. DJ answers 2026-10-12: freight is folded INTO the Zoo invoice/COGS (no separate line); Desert Aire (~$2,239, Cheryl's name) = PERSONAL exclude; phone+internet ALL business; check #2375 $159 → Other/misc. DRAFT:
- Gross receipts 39,725 · COGS (Zoo print+4over, freight incl) 8,536 · Gross profit 31,189
- Expenses: Rent/storage 2,452 · Utilities (AT&T+Frontier+Spectrum) 1,344 · Office (software/web) 622 · Interest (Amex finance chg) 680 · Other (bank fees+$159 chk) 223 = Total 5,321
- **NET ≈ $25,870** (vs 2024 filed net $5,642 — 2025 is a ~2x revenue year → more Saunders tax). No vehicle/home-office/wages (matches 2024 return).
- OPEN: confirm no Zoo charges on Amex 11003 are actually W&SC EDDM postcards (W&SC uses Citi/Amazon cards → likely clean). Source files: C:\Users\dj\Downloads\Chase8356_Activity_20261012.csv + activity.csv (Amex 11003 2025). Scratchpad: saunders_chase_8356_raw.md + saunders_amex_11003_raw.md.

**★ 2024 AMEX vs RETURN comparison (2026-10-12, DJ-requested; "settled for now").** Amex online caps at 24 months + only a 2025 Year-End Summary exists, so pulled all 12 **2024 monthly statement PDFs** (Downloads/2024-MM-DD.pdf; readable via pypdf; extract script scratchpad/extract_amex2024.py). NOTE Amex dialog: statements >2yr = PDF-only (Download btn y527); <2yr (Oct–Dec 2024) = also Excel/CSV/QB/Quicken (btn y635).
- **2024 Amex total New Charges = $10,000.27** (+ Interest $570.56). Monthly: Jan 440.75/Feb 1310.64/Mar 381.80/Apr 674.87/May 759.64/Jun 1700.51/Jul 1004.77/Aug 1053.10/Sep 443.33/Oct 1622.63/Nov 283.75/Dec 324.48. ~$1,200 personal (Oct US-Treas tax $869 + TurboTax $193 + Audible $149.50) → business Amex ≈ $8,800.
- **2024 filed return (Saunders) claimed $14,113 total expenses** (Adv 345, Office 695, Rent 4,863, Repairs 551, Supplies 5,125, Utilities 1,595, Interest 466, Other 473) on gross $19,755 → net $5,642.
- **CONCLUSION: 2024 did NOT under-capture costs** — return ($14,113) > Amex ($10,000) + Chase biz (~$1,800). So the 2024→2025 timing mismatch (costs paid 2024, NBHOF invoiced/collected 2025 due to late invoicing; fixed going forward by invoice-on-ship) is NOT double taxation — costs already deducted in 2024, 2025 income correctly stands alone on cash basis. 2024 SETTLED (DJ 2026-10-12). Minor open: return Rent $4,863 >> storage ~$2,400 (what else in Rent?) — deferred, doesn't change conclusion.

**Files:** Detail_TX.CSV + QB_DJ.IIF in uploads/d70db154-.../. See [[project_accounting_next_priorities]] (#1 Saunders setup), [[project_saunders_printing_migration_plan]], [[project_2025_schedule_c_categorized]] (W&SC, separate). Amex is mostly Saunders co3 — watch attribution vs W&SC. Reconstruction = QB revenue + Amex/Chase expenses → QB COA → Schedule C. Money writes via Operator/app, never raw RPC.
