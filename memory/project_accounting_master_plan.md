---
name: project_accounting_master_plan
description: "MASTER PLAN for the Odoo accounting migration/cleanup. Read FIRST for any accounting/bookkeeping work. Strategy, current state, roadmap, validation target."
metadata: 
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Accounting Migration — Master Plan (as of 2026-06-08)

**Role:** Claude is DJ's bookkeeper + accountant, working directly in Odoo (company_id=1, Window & Solar Care) via XML-RPC. Scripts live in `5_Accounting/`. Every batch writes an audit-log CSV and is reversible.

## THE STRATEGY (DJ, 2026-06-08) — this is the key framing
- **QuickBooks was accurate through end of 2024.** QB is the trusted historical book through 2024-12-31.
- **Decision: do the accounting in ODOO going forward, not QB.** Stop categorizing/reconciling in QB; Odoo is the system of record from the cutover forward.
- **Cutover date: Jan 1, 2025** (QB accurate through 2024; 2025 revenue fully imported to Odoo).
- **Use an OPENING BALANCE at the cutover to make Odoo accounts reflect reality** — we do NOT need to reconcile every pre-2025 transaction by hand. Set opening balances from QB/reality at 2025-01-01, then keep Odoo accurate with real transaction detail going forward. [[project_opening_balances_needed]]
- **🎯 Validation target: the REAL Chase balance is ~$1,000.** When the cleanup + opening balance are right, Odoo Chase (101401) must tie to the real bank balance. **After Stage 2 (2026-06-24) Odoo Chase = $36,081 → gap ~$35,081 remaining** (was $94,513 pre-Stage-2). Remaining gap composition: Stage 3 Credit Card (~$37K gross still on Chase, nets down w/ fee+batch) + missing pre-feed outflows + no opening balance yet. The gap is NOT a transaction mystery — it's resolved by Stages 2-3 (remove income duplicates) + the opening-balance/cutover (the pre-feed synthetic CSV recorded customer DEPOSITS into Chase but pre-feed outflows are incompletely captured; opening balance fixes this).

## WHAT'S DONE (2026-06-07/08) — detail in [[project_bank_feed_qb_double_booking]]
- Expense side: 105 orphan expenses categorized; **795 QB↔feed duplicate expenses retired** (feed wins, reversed QB); 18 NFCU→Toyota loan. Per-year expense P&L verified correct.
- Income side: discovered invoices were settled by **2,135 synthetic "Method | SO" entries** (Workiz CSV) that skipped Outstanding Receipts and dumped every method into Chase. Revenue account 400000 is CLEAN (no double-count — the dup is only on the cash/bank side).
  - 144 account.payment duplicates fixed via Outstanding Receipts.
  - **STAGE 1 done:** Cash (407, $60,847)→Owner's Draw 312000; Venmo (74, $14,654)→Venmo 101405. Chase $164,911→$89,410.
- Mechanics proven: categorize bank line = re-point its suspense line; retire dup = reverse with ORIGINAL date; re-point payment bank line doesn't break invoice. See [[project_categorize_bank_line_mechanic]].

## ⭐ SESSION 2026-06-24 — STAGE 2 DONE, NEXT = OPENING BALANCES (not Stage 3)
- **Stage 2 applied** (see roadmap item 1 below): Chase $94,513 → **$36,081**.
- **Stage 3 recalibrated DOWN:** post-cutoff `Credit Card | SO` synthetics are only **22 = $3,635** (pre-cutoff 173 = $33,905 stays on Chase, trued by opening balance). 50 `WORKIZ INC` net batch deposits ($10,921) + 29 real "Credit" account.payments ($5,077) make Stage 3 a fiddly batch+fee reconciliation with LOW Chase impact. So Stage 3 is cleanliness, NOT the lever to $1,000.
- **THE LEVER TO $1,000 IS OPENING BALANCES** (~$35K remaining gap = pre-cutover synthetic inflows still on Chase by design [Check $143,560 + Zelle $43,184 + CC $33,905], netted vs expenses, trued at cutover). [[project_opening_balances_needed]]
- **Credit-card finding:** DJ's own cards never linked; all 5 card liability accts $0; QB credited Chase for $260,838 (ALL methods collapsed into Chase, card expenses included). DECISION: opening balances FIRST, link card feeds (if ever) AFTER with start past QB import. Shopping list handed to DJ (awaiting his card/loan balances at year-end 2024).
- **NEXT SESSION:** when DJ returns balances → build opening-balance JEs (per-account adjust to real balance vs Opening Balance Equity 309000), resolve the feed-overlap cutover date (feed starts 2024-11-25 vs Jan-1 anchor), then reconcile Chase to real ~$1,000. Stage 3 + the 30 Stage-2 residuals = later cleanup.

## ROADMAP (next sessions)
1. ~~**Stage 2**~~ ✅ **DONE 2026-06-24.** Post-cutoff Check/Zelle synthetics → OR + reconciled vs feed. **Chase $94,513 → $36,081** (−$58,432). 327 synthetic Chase debits re-pointed to OR 101403; 297 ($53,602) auto-reconciled 1:1 against real feed deposits (window ±7d, exact amt, class-preferred); 30 residuals ($4,830) parked in OR unreconciled for manual cleanup. Invoices stay `paid`, revenue/AR untouched. Engine: `5_Accounting/stage2_check_zelle.py`, audit `audit_log_stage2.csv`, worklist `stage2_residual.csv`. **MECHANIC NOTE:** re-pointing BOTH the synthetic debit AND the matched feed-deposit suspense line to OR (101403, reconcile=True) makes Odoo **auto-reconcile** the equal/opposite pair — an explicit `account.move.line.reconcile()` afterward then Faults "already reconciled" (benign). Verify via OR reconciled-line count, not the reconcile return. **30 RESIDUALS to resolve:** Bucket A = lump payments arriving as one deposit (Brenda Williams 2×$150=$300 Zelle; Hennessy Group commercial; batched checks deposited days late) → match by batch later; Bucket B = NO bank trace (likely cash-at-door mislabeled or never deposited: SO 003362 $450, 003476 $85, 003489 $100, 003578 $65, 003740 $250, 003659 $110, 003732 $250) → candidate route to Owner's Draw like Stage 1 cash, confirm w/ DJ; Bucket C = Patti Martel two $140 Zelles but only one $140 deposit (possible internal dup).
2. **Stage 3** — Credit Card: synthetic gross → Outstanding Receipts; Workiz batch feed deposits (net) reconcile; fee plug → Merchant/CC Processing Fees 650100. (Feed pool still has 50 "workiz" deposits ~$10,921 for this.)
3. **Opening balances** — set 2025-01-01 balances from QB for Chase, the credit cards, loans, Notes Payable, fixed assets. Reconcile Odoo Chase to the ~$1,000 real balance. [[project_opening_balances_needed]]
4. **DJ's 2 credit cards** — STILL TO HANDLE. Not yet connected to Odoo feeds. When connected: their feeds will duplicate the QB CC entries + the synthetic "Credit Card | SO" settlements → dedupe round. The CC payoff feed lines are already parked in review (review_queue.csv).
5. Going forward: point Cash journal (id 18) at Cash on Hand 101406; new cash (June 2026+) = Cash on Hand (not draw).

## LOAN INTEREST — split principal vs interest (don't book 100% to loan)
Loan payments = principal (balance sheet, the loan liability) + interest (P&L, 704000 Loan Interest Expense). A loan payment does NOT hit the P&L except for its interest portion. Truck depreciation also hits P&L (needs Fixed Asset setup).
- **Toyota Loan (NFCU, 291200):** 5.99%, reg pmt $861.18, DJ pays $900. Remaining $24,252.45 (2026-05-20). Interest reclass JEs booked 2026-06-08 (moves 11466/11467/11468): Dr 704000 / Cr 291200 — 2024 $187.84, 2025 $1,981.22, 2026-YTD $657.42 (statement figures; backward-amortization validated within ~$10). The 18 NFCU feed payments were first booked 100% to 291200; these JEs move the interest portion to the P&L.
- Need same treatment for other loans (Ford 291100, Van Shelving 291300, Notes Payable 291400) when their statements arrive.
- P&L emailer: `5_Accounting/pl_2024_2025.py` (gray separator line under every line item per DJ's phone-readability request; sends via Odoo mail.mail to windowandsolarcare@gmail.com; mail.send() returns None → wrap in try/except Fault).

## KEY ACCOUNTS
101401 Chase · 101402 Bank Suspense · 101403 Outstanding Receipts · 101405 Venmo · 101406 Cash on Hand (new) · 121000 AR · 400000 Product Sales · 312000 Owner's Pay & Personal (draw) · 650100 Merchant/CC Processing Fees (new) · 309000 Opening Balance Equity. Chase journal id 6, Misc Operations journal = QB import.
