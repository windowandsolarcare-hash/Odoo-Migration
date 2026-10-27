---
name: project_chase_holding_account_parked
description: "PARKED (DJ 2026-10-27) — app payments mis-route clearing leg to Chase GL not Outstanding Receipts; Chase overstated $46,320 / 236 danglers. DJ will fix LATER, WITH Accounting. Re-surface on his say-so."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-27T21:56:49.827Z
---

**STATUS: PARKED by DJ 2026-10-27.** DJ was shown this and chose to deal with it LATER, WITH Accounting —
he did NOT approve the fix now. When he says he's ready, bring this straight back up with the full picture
below. The payment matcher build (Specialists) stays PAUSED pending this fix.

**The bug (verified live, read-only, company 1):** the app's `_execute_payment` (dashboard.py:5116) records
payments via payment.method.line **6/7/8** (Cash/Credit/Check) whose `payment_account_id = 100`
"Chase Checking (9008)" (code 101401, asset_cash, **reconcile=FALSE**) instead of **103** "Outstanding
Receipts" (code 101403, asset_current, **reconcile=TRUE**). The native j6 methods pml 41/42/51
(Manual/Batch/Stripe) correctly use 103. So every app cash/credit/check/Zelle payment books its clearing
leg into the bank GL → double-debits Chase vs the bank feed and can never bank-reconcile.

**Mechanism (Sue Garcia, the trigger case):** payment PBNK1/2026/00347 → AML 25633 = acct 100 DR 515;
bank line BNK1/2026/00786 → AML 25612 = acct 100 DR 515. Both debits on the same non-reconcilable account
→ can never match. That's the orphan "Zelle payment from FLE, LLC" $515 on 2026-10-23.

**Book impact — balance-sheet reclass only, NO P&L / AR / revenue hit:**
- Chase Checking GL (acct 100) **OVERSTATED by $46,320.00**.
- Outstanding Receipts (acct 103) understated by the same $46,320.
- AR/revenue UNAFFECTED — payments correctly credited AR; invoices show paid. Pure misclassification between
  two asset accounts.
- Sanity anchor: acct 100 posted net balance = **$62,290.22**; back out the $46,320 → implied true Chase
  ≈ **$15,970** (approx; plus unreconciled bank-feed noise). DJ can cross-check vs his real Chase balance.

**Blast radius:** **236** app-recorded payments dangling on acct 100, total **$46,320.00**, every one
unreconciled (full_reconcile_id=False), all inbound debits. Full population (only pml 6/7/8 post to 100).

**Proposed 2-part fix (HELD — needs DJ go-ahead, then Operator-executed, never raw; CPA glance on method):**
1. **Fix-forward config:** set pml 6/7/8 `payment_account_id` → 103. Stops new danglers. (Odoo config change
   on payment.method.line, not an app money-write.)
2. **Repair the 236 existing danglers:** reverse-and-repost each payment with the corrected method (clean;
   lets each reconcile against the bank feed). A grouped reclass JE (DR 103 / CR 100) is lighter but leaves
   the bank side to reconcile, so reverse+repost is cleaner end-to-end. **TEST on Sue (payment 519) FIRST** —
   verify the invoice stays paid + acct 100 drops $515 + the bank line reconciles — THEN batch the rest.

**Related instances (same cleanup theme — capture as DJ takes it up):**
- **2026-10-27 Barbara Scott door-charge** — $180 Visa on INV/2026/02598 (account.payment id 522, Stripe
  `pi_3UVI6MImQWeVzsL90BH9u6F2`) posted to the **Chase Checking JOURNAL (j6)** instead of the **Credit Card
  journal (j20)**. ⚠ This is a DISTINCT sub-issue from the clearing-account bug above: this payment
  RECONCILED fine ($0 residual), so it's not a dangler — the problem is **method-bucketing** (a card payment
  sitting in the bank journal → card revenue won't report under Credit Card). So the cleanup has TWO axes:
  (a) clearing ACCOUNT — pml 6/7/8 → 103 (the main bug); (b) JOURNAL/method selection — card payments should
  land in j20, not j6. No action now (DJ deferred); listed so both get addressed when he takes it up.

**Durable record also in AGENT_MAIL** (saunders-render-app `3_Documentation/AGENT_MAIL.md`, entry
"ROOT CAUSE VERIFIED + QUANTIFIED — app payment mis-routing", marked PARKED). Lead carried the plain-English
surface to DJ via Dispatcher. Ties to [[project_paid_without_payment_record]] and the Sue Zelle gap.
