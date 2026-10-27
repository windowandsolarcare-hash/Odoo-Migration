---
name: project_app_payments_outstanding_acct100_unreconcilable
description: App-recorded payments book the outstanding leg to acct 100 (reconcile=FALSE) not 103 — double-debits Chase + can never bank-reconcile
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T16:37:13.777Z
---

Discovered 2026-10-27 (read-only Odoo spike) while scoping the payment-reconciliation matcher. A **systemic accounting-correctness bug**, independent of the matcher:

**`_execute_payment` (routers/owner/dashboard.py:5116) records payments via global `payment_method_line_id` 6/7/8** ('Cash'/'Credit'/'Check'; map `{'check':8,'cash':6,'zelle':6,'venmo':6,'credit':7}`) **whose `payment_account_id = 100 "Chase Checking" (reconcile=FALSE)`** — NOT the correct `103 "Outstanding Receipts" (reconcile=TRUE)`. So every app-recorded cash/check/credit/zelle payment books its OUTSTANDING/clearing leg straight into the bank GL account. Effect: (a) **double-debits Chase** against the live bank feed, (b) the payment's clearing line **can never be bank-reconciled** (Odoo reconcile only works on reconcile=TRUE accounts). Journal 6's PROPER payment-method lines (41 Manual / 42 Batch Deposit / 51 Stripe) correctly use 103; the app's 6/7/8 do not.

**Account map (company 1):** 100 code 101401 "Chase Checking" asset_cash reconcile=FALSE (j6 default/liquidity); 101 code 101402 "Bank Suspense" reconcile=FALSE (j6 suspense); **103 code 101403 "Outstanding Receipts" reconcile=TRUE** (where payments SHOULD clear); 6 code 121000 "Accounts Receivable" reconcile=TRUE. Journal 6 = Chase BNK1 (default_account_id=100, suspense_account_id=101).

**Why it blocks bank reconciliation / the matcher's MODE A:** the dangling bank-feed line (`account.bank.statement.line`, is_reconciled=FALSE) and the payment's outstanding leg are BOTH same-side (debit) in acct 100 → no nettable pair, and acct 100 refuses reconciliation ("Account 101401 does not allow reconciliation"). Example: Sue Garcia payment 519 outstanding AML 25633 (acct 100 DR 515) vs bank line 2602 liquidity AML 25612 (acct 100 DR 515).

**Reconcile mechanism (for when the config is fixed) — confirmed JSON-RPC-doable, no widget:** reconcile at the MOVE-LINE level (`account.bank.statement.line` auto-creates its `move_id`). Canonical: `rpc('account.bank.statement.line','reconcile',[[st_line_id],[{'id': <payment_outstanding_aml_in_acct_103>}]])`. ★ The OWL `bank.rec.widget` and `account.reconciliation.widget` models are NOT registered in this instance — do NOT target them. Verify by re-reading `is_reconciled` + the AML `full_reconcile_id` (HTTP 200 ≠ success here).

**Fix paths (Accounting + DJ call — money/record-of-truth, NOT a builder decision):** (1) fix-forward: record app payments through a method line whose `payment_account_id=103` (fix the pml config or `_execute_payment` routing) → then bank↔payment reconcile is a one-call RPC; (2) repair existing danglers: re-point/repost each existing payment's outstanding leg into a reconcilable account (a write/repost). Surfaced to Lead (cc Accounting) 2026-10-27; matcher build HELD pending their reshape ruling (v1 may be detect-and-surface only). See [[feedback_data_location_odoo_vs_postgres]], [[feedback_root_cause_not_just_instance]].
