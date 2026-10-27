---
name: project_chase_holding_account_parked
description: "PARKED (DJ 2026-10-27) — app payments mis-route clearing leg to Chase GL not Outstanding Receipts; Chase overstated $46,320 / 236 danglers. DJ will fix LATER, WITH Accounting. Re-surface on his say-so."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-27T22:07:52.035Z
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

**★ CORRECTED 2026-10-27 — the "card should go to j20" idea was WRONG; DJ was right.** There is a SINGLE
axis to this bug: the clearing ACCOUNT (pml 6/7/8 → 103). There is NO separate "journal" axis. Verified live:
- **Journal 20 "Credit Card Payments"** (code CC, type=bank) `default_account_id` = acct **100 Chase Checking**
  (asset_cash) — the SAME account as j6. It is NOT wired to any independent card asset account, its method
  lines (pml 26–30) have NO clearing accounts, and only **1 payment in all history** ever posted to it. It is
  effectively **vestigial**.
- **No independent credit-card holding/asset account exists.** Both j6 and j20 point at Chase (acct 100).
  Incoming card money nets into Chase Checking — exactly like Zelle (mirrors the documented Zelle→j6 rule).
  Credit cards exist only on the LIABILITY side (the company's own card spending) — a separate matter.
- **Pattern:** 392 of 394 company-1 payments post to Chase j6; the 34 "Credit" (card) payments all land in
  j6. So booking card revenue to Chase j6 is CORRECT and consistent, not a mis-bucket.
- **Barbara Scott $180 Visa (payment 522, INV/2026/02598)** is actually booked CORRECTLY: it used native
  method pml 41 (Manual Payment/Chase) → clearing leg in acct **103 Outstanding Receipts**, reconciled
  ($0 residual). NOT a dangler and NOT a mis-bucket. My earlier "mis-bucketing" flag is WITHDRAWN.
- Card payments recorded via the app's "Credit" method (pml 7) DO route clearing to acct 100 → they're part
  of the SAME single dangler bug (clearing account), fixed by the same pml 6/7/8 → 103 change. No extra fix.
- **Reporting nuance (not a booking error):** a "Credit Card revenue" report bucket can't come from a
  separate account/journal (none exists) — it must be derived from the payment method / Stripe metadata.
  That's the per-method routing reporting work, separate from this clearing-account fix.

**Durable record also in AGENT_MAIL** (saunders-render-app `3_Documentation/AGENT_MAIL.md`, entry
"ROOT CAUSE VERIFIED + QUANTIFIED — app payment mis-routing", marked PARKED). Lead carried the plain-English
surface to DJ via Dispatcher. Ties to [[project_paid_without_payment_record]] and the Sue Zelle gap.
