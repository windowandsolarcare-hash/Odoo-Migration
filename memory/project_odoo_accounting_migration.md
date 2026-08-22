---
name: Odoo Accounting Migration Plan
description: Complete plan to migrate DJ's financials from QuickBooks into Odoo accounting — revenue from Odoo/Workiz, expenses from QB CSV, opening balances from real accounts
type: project
originSessionId: d77fc6bd-119f-4192-b2c8-a8592257d2b6
---
# Odoo Accounting Migration — Full Detail

**Created:** 2026-04-15
**Last Verified:** 2026-05-09

## CURRENT STATUS (verified 2026-05-08)

### ✅ DONE
- Chart of Accounts: all QB expense categories + balance sheet accounts created (143 expense accounts, all credit card accounts, Opening Balance Equity, Owner's Pay, etc.)
- Payment Journals: Chase Checking (j6, live sync), Check Payments (j17), Credit Card Payments (j20), Zelle (j19), Cash (j18)
- Chase bank feed connected to Odoo (Plaid, linked today under W&SC)
- Chase CSV imported: 1,504 transactions, Nov 25 2024 – May 8 2026 (journal 6)
- AWP vendor bill recorded: BILL/2026/05/0001, $148.77, linked to P00101, paid by CC

### ✅ DONE (updated 2026-05-08 evening)
- Bulk invoice+payment script: `2_Testing_Tools/bulk_invoice_payment.py` — WORKING
  - Tested on SO 000009 (single payment $100 Check) and SO 000029 (2 payments totaling $170) — both produce `payment_state=paid, amount_residual=0.0`
  - 2,232 Done SOs awaiting invoice, 2,390 jobs in payment CSVs
  - Script ready to run full overnight: `python bulk_invoice_payment.py --full`

### ✅ DONE (updated 2026-05-09)
- QB historical expenses: 3,324 JEs created via `import_qb_expenses.py`, 0 failed. Journal 3, credit Chase account 100. Covers 2019–2025.
- 2025 P&L confirmed: Revenue $79,062 | Expenses $46,502 | Net $32,560
- 2026 YTD: $28,979 (Jan–May partial)
- Workiz vs Odoo 2025 cross-reference: 7 jobs missing invoices (total $2,090) — all have SOs, 4 in draft, 3 confirmed. Not yet invoiced.

### ❌ NOT YET DONE
- Invoice the 7 missing 2025 jobs (fix SO amounts on 3462 Claudia Duran $110 short, 3647 Rik Ports $40 short first)
- Opening Balance Journal Entries (need real account balances from DJ on cutover date)
- Fixed Assets (20 Odoo default templates exist, all $0 — no actual vehicles/equipment entered yet)
- Loan accounts in CoA (Ford Transit 250, Toyota, Van Shelving, Notes Payable-Saunders Printing)
- QB Fixed Asset List export — not yet collected
- QB expense re-export after 2026 categorization — open question whether fully categorized
- Cutover date — not decided
- Historical expense import from QB CSV (Phase 6) — not done
- Pre-Nov 2024 bank transactions (2019–Nov 2024 from QB CSV) — not imported

### DATA SOURCES STATUS
- Chase CSV (raw bank): Nov 25, 2024 – May 8, 2026 → imported to Odoo ✅
- Chase Plaid live sync: active, auto-syncs going forward ✅
- QB Transaction Detail CSV: Jan 2019–Apr 2026, 3,006 categorized expenses + 3,312 set aside → NOT yet imported
- QB SetAside file: C:\Users\dj\Downloads\QB_SetAside_3312.csv (CC bill payments, draws, loan payments)

---

## BACKGROUND & CONTEXT

DJ runs Window & Solar Care as a solo/contractor service business. He is migrating away from QuickBooks Online and Workiz, moving everything into Odoo. The accounting migration is a separate phase from the operational migration (Workiz→Odoo sync) which is already running.

### How the current system works (important for context)
- All jobs are managed in Workiz
- When DJ marks a job Done and invoices the customer in Workiz, Workiz auto-syncs the invoice AND payment to QuickBooks via a built-in integration
- In QB: invoice hits Sales + Accounts Receivable; payment hits AR + Undeposited Funds
- When Chase bank transactions come in (linked to QB), DJ matches the deposit → zeroes Undeposited Funds → credits Checking
- Expenses also come in from Chase bank feed and DJ categorizes them in QB

### Problems with current system
- Workiz→QB sync has duplicate/orphaned payment issues — sometimes creates extra invoices or payments in QB that have no matching bank transaction, leaving them permanently open
- DJ has not categorized all 2025 and 2026 expenses yet
- DJ has not fully reconciled QB and does not want to — it's too tedious
- Workiz is being phased out — the Workiz→Odoo phases (3,4,5,6) are already handling new jobs

### Why the migration approach works without reconciling QB
Because we are using **real account balances** (logged into actual Chase/credit card/loan accounts on cutover day) as opening entries in Odoo. This makes QB's internal reconciliation state irrelevant. Whatever QB says is offset by the truth from the actual bank.

---

## THE THREE DATA SOURCES

### 1. Odoo SOs (Sales Orders)
- Every job ever synced from Workiz exists as an SO in Odoo
- SO name format: Workiz Job ID zero-padded to 6 digits. Example: Workiz job 4265 = Odoo SO name `004265`
- Each SO has: customer, service date (date_order), line items, amounts, Workiz UUID, payment method info
- SOs with Workiz status "Done" are completed paid jobs — these need invoices created

### 2. Workiz Payment CSVs (6 files, one per year)
- Downloaded from Workiz Reports → Payment Report
- Workiz only allows one year at a time — DJ downloads 6 separate files
- File naming convention: `Workiz_Payments_YYYY.csv`
- Stored in: `C:\Users\dj\Downloads\`
- Sample file already reviewed: `Payment report - 04-15-2026.csv`
- Columns confirmed: Job ID, Document, Payment type, Status, Amount, Service Fee, Net, Tips, Technician, Client name, Transaction method, Card, Payment date, Payment time, Collected by, Description, Job type, Job status, Confirmation code
- **Join key:** Workiz Job ID (e.g. 4265) → Odoo SO name (e.g. 004265) by zero-padding to 6 digits
- Payment types seen: Check, Credit charge — need to map to Odoo payment journals
- Contains exact payment date, amount, and method per job — this is authoritative

### 3. QuickBooks Transaction Detail CSV
- Already downloaded: `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail by Account.csv`
- Date range: January 1, 2019 – April 15, 2026
- Size: 17,335 rows, 16,777 actual transactions
- **Transaction type breakdown:**
  - Expense: 6,318 rows ← THIS is what we need from QB
  - Invoice: 4,131 rows ← SKIP — Odoo SOs are better source
  - Payment: 3,222 rows ← SKIP — Workiz CSVs are better source
  - Deposit: 2,575 rows ← handled by bank feed matching in Odoo
  - Journal Entry: 266 rows ← review individually, some may be needed
  - Credit Card Payment: 164 rows ← may need for balance sheet
  - Transfer: 60 rows ← between accounts, handle with opening balances
  - Check: 4 rows
- **Account sections in the file (balance sheet accounts seen):**
  - TOTAL BUS CHK (9008) — Chase checking account
  - Undeposited Funds
  - Discover (credit card)
  - Discover II
  - Shop Your Way - Mastercard
  - Thank You Card
  - CRV Loan (deleted)
  - Ford Transit 250 2019 Loan
  - Notes Payable - Saunders Printing
  - Toyota Loan
  - Van Shelving Loan
  - Opening Balance Equity
  - Owner's Investment
  - Owner's Pay & Personal Expenses
  - Discounts given
  - Services (revenue)
- **Expense categories confirmed in QB:**
  - Advertising & Marketing (EDDM Post Cards, Herald Mag, Lead Generation)
  - Bank Charges & Fees (Credit Processing Fees)
  - Car & Truck (Auto Insurance, Fuel, Vehicle Maintenance and Repair)
  - Contractors
  - Dues & Subscriptions
  - Employee Benefits
  - Equipment Purchase
  - Equipment Rental
  - Insurance
  - Interest Paid
  - Job Supplies
  - Meals & Entertainment
  - Office Supplies & Software (Scheduling Software, Software - Other)
  - Other Business Expenses
  - Rent & Lease
  - Repairs & Maintenance
  - Supplies & Materials - Not Job Specific (Screens)
  - Taxes & Licenses
  - Travel
  - Uncategorized Expense
  - Utilities
- **This file must be re-exported AFTER DJ categorizes 2025/2026 expenses** so the newly categorized items are included

### 4. QuickBooks Fixed Asset List (not yet exported)
- QB tracks vehicles and equipment separately with depreciation schedules
- Must be exported from QB: Reports → Fixed Asset List
- Contains: asset name, purchase date, purchase price, current book value (after depreciation)
- Needed for the balance sheet — vehicles/equipment show up as assets in Odoo

---

## DECISIONS ALREADY MADE (do not re-litigate these)

1. **No QB reconciliation** — DJ is not reconciling QB before migration. Opening balances from real accounts make it unnecessary.

2. **No QB customer balance / open invoices report** — Not needed. All customers pay at the door. There is no AR. Odoo already knows who paid from the Workiz payment CSVs.

3. **No QB deposit matching** — Not needed. Matching deposits to QB invoices produces data we're throwing away. Skip it entirely.

4. **Revenue source = Odoo + Workiz, NOT QuickBooks** — Odoo SOs have more detail (service type, line items, job date, customer) than QB invoices ever had. QB invoice rows are ignored during import.

5. **Expense source = QB Transaction Detail CSV** — QB is the only place expenses ever lived. This is the one thing QB has that Odoo doesn't.

6. **Opening balances from real accounts** — On cutover day, DJ logs into Chase, each credit card, and each loan account and reads the actual balance. These become opening journal entries in Odoo. Claude handles all double-entry.

7. **Workiz→QB sync problems are irrelevant** — The duplicate/orphaned payment issues in QB don't matter. Our new system bypasses Workiz→QB entirely and drives invoicing from Workiz payment CSVs directly.

8. **DJ does not want to do anything manually in Odoo accounting setup** — Claude handles all journal entries, chart of accounts, opening balances, scripts. DJ supplies numbers and files.

---

## PHASE-BY-PHASE PLAN

### PHASE 1 — QuickBooks Cleanup (DJ does this, no Claude involvement)
**Purpose:** Get expense history accurate before final export

Steps:
1. Open QuickBooks Online
2. Go to Banking → Review (or Transactions → Banking)
3. For every uncategorized expense in 2025 and 2026: assign the correct expense category
4. Do NOT match deposits to invoices — waste of time
5. Do NOT reconcile — not needed
6. When done: re-export Transaction Detail by Account CSV (same report, full date range 2019–today)
7. Save new file as: `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail FINAL.csv`

**Why this matters:** The 6,318 expense rows in the CSV will have "Uncategorized Expense" for anything not categorized. If we import those into Odoo they're useless. Do the categorization once in QB, then export and never go back.

---

### PHASE 2 — Gather All Source Files (DJ does this)
**Purpose:** Collect everything Claude needs before touching Odoo

Files to collect:
1. **QB Transaction Detail CSV** — re-export after Phase 1 (replaces current file)
2. **QB Fixed Asset List** — QB → Reports → Fixed Asset List → export CSV
3. **6x Workiz Payment CSVs** — Workiz → Reports → Payment Report, one per year:
   - `Workiz_Payments_2021.csv` (or earliest year available)
   - `Workiz_Payments_2022.csv`
   - `Workiz_Payments_2023.csv`
   - `Workiz_Payments_2024.csv`
   - `Workiz_Payments_2025.csv`
   - `Workiz_Payments_2026.csv`
   - Drop all in `C:\Users\dj\Downloads\`

When all files are in Downloads, tell Claude and provide the exact filenames.

---

### PHASE 3 — Choose Cutover Date & Gather Real Account Balances (DJ does this)
**Purpose:** Establish the opening state of every balance sheet account

DJ picks a cutover date (recommendation: first of a month, e.g. June 1, 2026).

On that date, DJ logs into each account and records the actual balance:

| Account | Institution | Balance Needed |
|---|---|---|
| Chase Checking (9008) | chase.com | Ending balance on cutover date |
| Discover Card | discover.com | Statement balance |
| Discover II | discover.com | Statement balance |
| Shop Your Way Mastercard | | Statement balance |
| Thank You Card | | Statement balance |
| Ford Transit 250 2019 Loan | Lender | Remaining payoff balance |
| Toyota Loan | Lender | Remaining payoff balance |
| Van Shelving Loan | Lender | Remaining payoff balance |
| Notes Payable — Saunders Printing | Own records | Amount still owed |
| Owner's Equity | Calculated | Assets minus Liabilities (Claude calculates) |

DJ gives these numbers to Claude. Claude enters them as opening journal entries. All entries offset to "Opening Balance Equity" account (standard accounting practice). Claude then zeros Opening Balance Equity into Retained Earnings.

---

### PHASE 4 — Odoo Accounting Setup (Claude does this via API)
**Purpose:** Configure Odoo's accounting module to receive data

Steps Claude handles:
1. **Chart of Accounts** — create/map all QB expense categories to Odoo accounts
   - Use QB category names exactly so historical imports match
   - Key accounts: all expense categories listed above + AR, AP, Checking, Undeposited Funds, each credit card, each loan, Owner's Equity
2. **Payment Journals** — create journals for:
   - Check
   - Cash
   - Credit Card (generic)
   - Zelle (used for some payments)
   - Bank (Chase) — connected to bank feed
3. **Opening Balance Journal Entries** — one entry per account using Phase 3 numbers
4. **Fixed Assets** — enter each vehicle/equipment from QB Fixed Asset List
   - Asset name, purchase date, original cost, accumulated depreciation, current book value
5. **Bank Feed Connection** — DJ connects Chase to Odoo (requires DJ's Chase login, cannot be done by Claude)
   - In Odoo: Accounting → Configuration → Add Bank Account → connect Chase
   - After connected, transactions flow in automatically — same as QB

---

### PHASE 5 — Bulk Invoice Creation + Payment Application (Claude builds and runs script)
**Purpose:** Create invoices for all 6 years of completed jobs and apply payments

**Script logic:**
1. Query Odoo for all SOs where:
   - Workiz status (x_studio_workiz_status or equivalent field) = "Done"
   - No invoice yet exists (invoice_ids is empty)
2. For each SO:
   - Call `action_confirm()` if SO is still in draft (write date_order back after — Odoo resets it)
   - Create invoice: `sale.order` → `_create_invoices()` method
   - Post (confirm) the invoice: `action_post()`
3. Load all 6 Workiz payment CSV files, combine into one lookup table keyed by Job ID
4. For each invoice:
   - Zero-pad the SO name to get Job ID (e.g. `004265` → `4265`)
   - Look up matching payment row in Workiz CSV
   - If found: create payment in Odoo with correct amount, date, method
   - Apply payment to invoice (reconcile)
   - If not found: leave invoice open (these become flagged for review)
5. Report: how many invoices created, how many paid, how many left open

**Payment method mapping (Workiz → Odoo journal):**
- "Check" → Check journal
- "Credit charge" → Credit Card journal
- "Cash" → Cash journal
- "Zelle" → Zelle journal
- anything else → flag for review

**Important technical notes:**
- SO name join: Workiz Job ID is integer in CSV (e.g. 4265.0) → strip .0 → zero-pad to 6 digits → match SO name
- date_order on SO must be preserved — always write back after action_confirm()
- Invoice date = payment date from Workiz CSV (not today's date)
- Do NOT use `response` or `result` as variable names in any Odoo server action (reserved)
- Run in batches to avoid timeouts — 50 SOs at a time with error handling

---

### PHASE 6 — Import Historical Expenses from QB (Claude builds and runs script)
**Purpose:** Get 6 years of expense history into Odoo so P&L is complete

**Script logic:**
1. Read the final QB Transaction Detail CSV
2. For each row where Transaction type = "Expense":
   - Parse: date, vendor name (Name column), category (Split column), amount (negative = expense)
   - Create vendor bill in Odoo (`account.move` with move_type = `in_invoice`)
   - Set: partner (vendor name), invoice_date, account (mapped from QB category), amount
   - Post the bill
3. For Journal Entry rows: review list first, Claude presents them to DJ for decision on which to import
4. Skip: Invoice, Payment, Deposit, Transfer rows — handled by other phases or bank feed

**QB category → Odoo account mapping (to build during Phase 4):**
- Advertising & Marketing → Marketing/Advertising expense account
- Car & Truck → Vehicle expense account
- Bank Charges & Fees → Bank fees account
- etc. (full mapping built when chart of accounts is created in Phase 4)

**Volume:** ~6,318 expense rows. Will run in batches.

---

### PHASE 7 — Go Live (DJ switches from QB to Odoo for daily work)
**Purpose:** Stop using QB, start using Odoo for everything

Steps:
1. Chase bank feed now connected to Odoo (from Phase 4)
2. Transactions come in daily — DJ matches them in Odoo instead of QB
   - Deposits → match to invoices/payments sitting in Undeposited Funds (same as QB)
   - Expenses → categorize vendor/category (same as QB, Odoo learns over time)
3. New invoices → created automatically by Zapier Phase 6 (already running)
4. Stop logging into QuickBooks

---

### PHASE 8 — Validate (Claude checks, DJ confirms)
**Purpose:** Sanity check that the numbers make sense

1. Claude pulls P&L from Odoo for 2024 → compares income/expense totals to QB P&L for same period
2. Claude checks balance sheet → verifies cash, credit card, loan balances match real accounts
3. Any discrepancy → Claude creates an adjusting journal entry to correct it
4. DJ confirms the numbers look right

---

## WHAT DJ DOES vs. WHAT CLAUDE DOES

| Task | Who |
|---|---|
| Categorize 2025/2026 expenses in QB | DJ |
| Re-export QB Transaction Detail CSV (after categorizing) | DJ |
| Export QB Fixed Asset List | DJ |
| Download 6 Workiz payment CSVs (one per year) | DJ |
| Pick cutover date | DJ |
| Look up real account balances on cutover date | DJ |
| Connect Chase bank feed to Odoo | DJ (requires Chase login) |
| Daily: match deposits & categorize expenses in Odoo | DJ |
| Chart of accounts setup in Odoo | Claude |
| Payment journal setup in Odoo | Claude |
| Opening balance journal entries | Claude |
| Fixed asset entries | Claude |
| Bulk invoice creation script | Claude |
| Payment application from Workiz CSVs | Claude |
| Expense import script from QB CSV | Claude |
| All double-entry accounting | Claude |
| Validation and adjusting entries | Claude |

---

## POST-MIGRATION AUTOMATIONS TO BUILD (after books are live)

All of these were agreed upon on 2026-04-15. Build after accounting migration is complete.

1. **Nightly bank reconciliation script** — pulls new Chase transactions, matches deposits to invoices one-to-one (DJ deposits checks one at a time via phone — always 1:1), categorizes expenses by vendor name rules, flags unknowns for DJ review
2. **Monthly P&L email** — runs last day of every month via scheduled trigger:
   - Pulls P&L from Odoo API
   - Formats clean summary (revenue, expenses, net income, vs. prior month %)
   - Claude adds written commentary flagging anything unusual (expense spikes, revenue drops)
   - Includes one-click deep link to Odoo P&L with dates pre-filled: `https://window-solar-care.odoo.com/odoo/accounting/reports/profit-and-loss?date_from=YYYY-MM-01&date_to=YYYY-MM-DD`
   - Attaches PDF for records
   - Sends to windowandsolarcare@gmail.com via Gmail MCP
   - Creates activity in Odoo: "Monthly P&L ready — [link]"
3. **Weekly cash summary** — every Monday morning: checking balance, what came in, what went out that week
4. **Vendor categorization rules** — built once, run forever. New unknown vendors flagged to DJ, DJ confirms category once, never asked again.

---

## THINGS STILL TO DECIDE

- [ ] **Cutover date** — what date to go live on Odoo accounting?
- [ ] **How far back to import expenses** — all the way to 2019, or just 2024 forward?
- [ ] **Fixed assets** — full depreciation schedules or just current book value as a lump?
- [ ] **Journal entries from QB** — which of the 266 journal entry rows are needed vs. skip?

---

## QUICKBOOKS FINANCIAL SUMMARY (for reference)
Pulled via QuickBooks MCP on 2026-04-15, period 2020–2026:
- Total Income: $390,935
- Total Expenses: $214,159
- Net Operating Income: $176,759
- Revenue breakdown: Services $341,992 | Sales $40,118 | Unapplied Cash $8,433 | Tips $588
- Top expense categories: Car & Truck $47,493 | Supplies & Materials $39,885 | Office/Software $36,883 | Meals $11,462 | Utilities $11,489 | Advertising $19,855 | Interest $9,556 | Rent $15,843

---

## FILE LOCATIONS

| File | Location |
|---|---|
| This migration plan (detailed) | `C:\Users\dj\.claude\projects\...\memory\project_odoo_accounting_migration.md` |
| Migration checklist (for DJ) | `C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\Odoo_Accounting_Migration_Plan.md` |
| QB Transaction Detail CSV (current) | `C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail by Account.csv` |
| Workiz Payment sample (2026) | `C:\Users\dj\Downloads\Payment report - 04-15-2026.csv` |
| Workiz 6-year master job data | `C:\Users\dj\Downloads\Workiz_6Year_Absolute_Master_FINAL.csv` |

---

## HOW TO RESUME THIS IN A NEW SESSION

Just tell Claude "I want to work on the accounting migration" — Claude will find this memory file automatically and have full context. No special phrase needed.

## DJ'S CHECKLIST DOCUMENT — WHERE TO FIND IT

DJ has a human-readable checklist version of this plan saved here:

**`C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\Odoo_Accounting_Migration_Plan.md`**

If DJ asks "where is the accounting migration document?" or "where did we save that plan?" — point him to that path. It can be opened in any text editor, Notepad, VS Code, etc. Claude can also open and read it directly.
