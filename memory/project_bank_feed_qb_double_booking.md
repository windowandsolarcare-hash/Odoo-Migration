---
name: project_bank_feed_qb_double_booking
description: "Chase Checking GL (101401) is double-booked — QB import AND bank feed both hit it. Do NOT categorize the 1,491 suspense lines as new expenses; they must be reconciled/matched."
metadata: 
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

**Chase Checking GL account `101401` (code, "Chase Checking (9008)") is hit by TWO independent sources for 2025+2026 (company_id=1):**

1. **Bank feed** — journal "Chase Checking" (BNK1, journal id 6). 2,122 lines, +109,142.21. Each imported statement line posts: debit/credit `101401` (real bank) and parks the counterpart in `101402` Bank Suspense Account. **1,491 of these suspense counterparts are still UNRECONCILED** (`account.bank.statement.line.is_reconciled = False`).
2. **QB historical import** — journal "Miscellaneous Operations". 847 expense JEs, −54,818.81. `ref` = `QB Import | <vendor>`. Each already categorized the expense (e.g. Dr 667000 Fuel) and credited `101401` Chase Checking as the other side.

**Why this matters:** Both sources move the bank account, so `101401` is distorted (net 54,323.40, but that mixes two overlapping truths) AND every expense QB booked is also sitting—uncategorized—as a bank-feed suspense line. Only 201 of 1,491 suspense lines exact-match (same date + abs amount) an existing QB expense JE; the rest differ mostly by date offset.

**THE TRAP:** Do NOT "categorize" the 1,491 suspense lines by booking them to expense accounts. QB already booked those expenses. Doing so DOUBLE-COUNTS every expense.

**Correct resolution (standard Odoo bank rec):** Reconcile/match each bank statement line against its existing QB JE. Lines with no matching QB JE are the ones that genuinely need a category (QB missed them). QB JEs with no bank line = booked against a non-Chase account (cash/CC) or an error.

**DECISIONS LOCKED (DJ, 2026-06-07):**
- **Cutover = 2024-11-25** (the date the Chase feed starts). Feed canonical from there forward.
- **Feed WINS in the overlap.** For the ~725 feed↔QB matched lines: categorize the FEED line using the matched QB entry's category, then retire (reverse) the duplicate QB JE. Same P&L, single record sourced from the bank.
- **The ~122 "QB-no-bank" entries = DJ's credit-card-paid expenses. KEEP untouched.** No Chase line because paid by CC, not checking. NOT duplicates.
- **Before 2024-11-25:** QB untouched history.
- **Treat all feed items as business for now** (personal sort-out deferred).
- **Credit cards PUNTED.** DJ has 2 CCs not yet connected. Later he connects them → their feeds will duplicate the 122 (and pre-2024 CC entries) → dedupe CC feed vs QB at that point. ROUND TWO, future task.
- **Sales confirmed NOT in QB** (0 income lines in QB import). All revenue = 633 invoices. Income-side feed deposits (454, ~$85K) must RECONCILE to existing invoices/payments, never re-booked as new income.
- QB import date range 2019-10-31 → 2026-04-12 (6,658 lines). Chase feed 2024-11-25 → 2026-06-05 (1,607 lines, 1,491 unreconciled).

Reconciliation report buckets (CSVs in 5_Accounting/): MATCHED 725 (~$38K), FEED ORPHANS 766 (454 income $85K + ~300 real expense), QB-NO-BANK 122 (~$16K = credit cards).

**PROGRESS (2026-06-07 session):**
- ✅ 105 orphan expenses auto-categorized (software/meals/supplies/fuel/insurance/utilities/licenses). audit_log_categorize.csv
- ✅ 795 matched duplicates RETIRED: feed line categorized to QB's category + QB move reversed (feed wins). Verified per-year P&L correct (2025 $47,074 / 2026 $11,760, NOT doubled). audit_log_retire_matched.csv. Engine: retire_matched.py. (Date-bug found+fixed mid-run — see [[project_categorize_bank_line_mechanic]].)
- ✅ 18 NFCU lines → 291200 Toyota Loan paydown (−$16,200).
- Suspense 101402: 1,491 → ~688 lines remaining.

- ✅ **INCOME matched dups (144, $28,295) — DONE via proper fix.** Re-pointed payment bank line 101401→101403 Outstanding Receipts + categorized matching feed deposit→101403; Odoo auto-reconciled the pair. OR nets to $0 (0 unreconciled lines), all 627 invoices still 'paid'. Chase journal method lines 41,42 set to payment_account_id=101403 so FUTURE manual/batch payments use Outstanding Receipts automatically. Mechanic: re-pointing a payment's bank line does NOT draft the move and does NOT break AR↔invoice reconciliation (verified). Engine: income_reconcile.py, audit_log_income.csv.
- PAYMENT_ONLY (99, $18,944): payments with no feed deposit — left as-is, already correct (counted once).

**INCOME SETTLEMENT MECHANISM (discovered 2026-06-08):** DJ's history — migrated SOs, then had Odoo invoice each Done SO (same date as SO, Dr AR/Cr Sales, CORRECT), then ran a **Workiz payment CSV**. That CSV created **2,135 SYNTHETIC settlement entries** in the Chase journal (id 6), `ref` = `"<Method> | SO <num>"`, `statement_line_id=False`, posting **Dr Chase 101401 / Cr AR** — which marked invoices paid but (a) SKIPPED Outstanding Receipts and (b) dumped EVERY method into Chase. Method counts: Check 1192, Cash 407, Zelle 266, Credit Card 195, Venmo 74, Cash App 1. Range 2020-02 → 2026-03. Revenue account 400000 is CLEAN (only invoices credit it — verified April: $10,860, matches AR, no double-count). The double-count is purely on the CASH/bank side, never revenue.

**Real-world method behavior (DJ, 2026-06-08):** Cash → DJ's safe, used personally (NOT bank). Venmo → standalone app, DJ sweeps to personal as draws. Credit Card → batches through Workiz into Chase **minus a processing fee**. Check/Zelle → real Chase deposits.

**BACKWARD INCOME-FIX ROUTING (decided + in progress):**
- ✅ **STAGE 1 DONE (2026-06-08):** Cash (all 407, $60,846.82) → **Owner's Draw 312000** (past = personal, DJ's call); Venmo (all 74, $14,654.05) → **Venmo 101405**. 481 synthetic Chase-debit lines re-pointed. Chase $164,911 → $89,410 (−$75,501 phantom removed). audit_log_income_stage1.csv. Created accounts: **Cash on Hand 101406** (id 335, for June-2026-FORWARD cash) + **Merchant/CC Processing Fees 650100** (id 336).
- ⬜ **STAGE 2:** Check/Zelle POST-cutoff (2024-11-25+, 237+90 entries ~$58K) → Outstanding Receipts 101403, reconcile vs real feed (Check/remote $38,054 + Zelle $24,969 available; expect timing residual). Check/Zelle PRE-cutoff (955+176, $143,560+$43,184) STAY on Chase (only record of pre-feed deposits).
- ⬜ **STAGE 3:** Credit Card (195, ~$37,540) → Outstanding Receipts gross; Workiz batch feed deposits (~50, "WORKIZ INC") net reconcile; fee plug (gross−net) → Merchant Fees 650100. Cash App (1, $150) → review.
- TODO going forward: point Cash journal (id 18, currently defaults to 101401) at Cash on Hand 101406.

**🎯 RECONCILIATION TARGET / NORTH STAR (DJ, 2026-06-08): the REAL Chase bank balance is ~$1,000.00.** Odoo currently shows Chase 101401 at **$89,410** (after Stage 1). Gap ≈ **$88,410 still to eliminate** — this is THE validation endpoint: when the cleanup is right, Odoo Chase must tie to the real bank balance. Likely composition of the gap: Stage 2 post-cutoff Check/Zelle duplicates (~$58K) + Stage 3 Credit Card (gross-on-Chase ~$37K, needs fee/batch + dedupe) + missing pre-feed OUTFLOWS (synthetic CSV recorded customer DEPOSITS into Chase but pre-feed withdrawals/expenses/draws may be incompletely captured) + **no opening balance ever set** [[project_opening_balances_needed]]. Next session: work Stages 2-3, then reconcile remaining gap to the $1,000 real balance.

**STILL TODO:**
- **DEPOSIT_ONLY (411 deposits, $79,880) — income deposits with NO account.payment record.** NOTE: now understood as the real feed twins of the synthetic Check/Zelle/CC entries — handled by Stages 2-3 above, NOT a separate mystery. Breakdown: checks/remote deposits 244 ($38,054), Zelle 102 ($24,969), Workiz card settlements 50 ($10,921), 1 transfer-in ($5,000), misc 14. These are customer money in the bank not recorded as payments. DO NOT auto-book to income (revenue already recognized on the invoices → would double-count). Must match to OPEN invoices/AR and apply as payment (Cr AR), or to income only if truly uninvoiced. Workiz settlements are batch deposits spanning multiple jobs. Needs careful matching pass + DJ input. file: income_deposit_only_review.csv.
- **REVIEW remainder (~118):** CC payoffs (~38, PARKED till DJ connects 2 cards), Gusto payroll (split wages vs taxes — needs Gusto per-run breakdown, not in bank feed), internal transfers (need destination acct), misc unclassified. review_queue.csv.
- Optional later: a few odd QB categories carried over (U-Haul→Office Rent, Sam's→Fuel, Car Wash→Vehicle Repairs) — cleanup pass if DJ wants.

**Note:** Chase 9008 is mapped to company 1 (W&SC). Feed contains likely-personal items (Starbucks Redwood City, Panera Sip Club) — W&SC is a DBA of Saunders Printing [[project_twilio_a2p_and_entity]], so expect owner personal/business commingling that needs a judgment call per line.

Recon scripts: `5_Accounting/recon_books.py`, `dig_suspense.py`, `check_double.py`, `confirm_dup.py` (all read-only).
