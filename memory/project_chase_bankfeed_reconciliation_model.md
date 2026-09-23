---
name: project_chase_bankfeed_reconciliation_model
description: "How Chase (journal 6) deposits + app-recorded payments + invoices relate in Odoo — the reconciliation model for the Stale-SOs retool. TWO worlds: app account.payment (all reconciled to invoices) vs the raw Chase bank.statement.line FEED (all is_reconciled=False, unmatched). Deterministic per-SO branch key = the SO's invoice payment_state. + the double-record risk + the recon gap."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T01:12:57.207Z
---

**Chase (journal 6) bank-feed ↔ payment ↔ invoice ↔ SO reconciliation model** (read-only recon 2026-09-23, for the Stale-SOs retool). Verify against live before acting; all figures = a 90-day co1 sample.

## Two worlds (they do NOT currently reconcile to each other)
- **APP-recorded payments** — `account.payment` on **journal_id=6** (Chase; Zelle+Venmo... note Venmo=j29 per [[project_payment_journal_routing]]). When the app records a payment (`_execute_payment`/paywatch/manual owner-Pay) it creates the invoice + payment + reconciles them: ALL 93 j6 payments (90d) had `reconciled_invoice_ids` populated, `is_reconciled=True`, `is_matched=True`. So an app-recorded deposit → SO is invoiced + paid (NOT stale).
- **RAW Chase bank FEED** — `account.bank.statement.line` (journal_id=6): imports EVERY deposit (201 lines/90d, 32 Zelle), each **`is_reconciled=False`**, own bank `move_id` (BNK1/…), `partner_id` EMPTY, payer in **`payment_ref`** ("Zelle payment from <NAME> <txn>"), + `amount`, `date`. UNMATCHED to any invoice/payment.

## ★ Deterministic per-SO branch key = the SO's invoice payment_state
Relations: `sale.order.invoice_ids` → `account.move` (move_type='out_invoice', state='posted'); reverse `account.move.invoice_origin` = SO name. Paid-ness = `account.move.payment_state` ∈ {not_paid, in_payment, paid, partial, reversed} + `amount_residual` (0 = fully paid). Invoice↔payment = `account.move.matched_payment_ids` ↔ `account.payment.reconciled_invoice_ids`.
- **(a) already-paid** → SO has a posted invoice with `payment_state` ∈ ('paid','in_payment') → payment already recorded+reconciled → **CLOSE-OUT ONLY, never re-record**.
- **(b) needs-recording** → SO has NO posted invoice (invoice_status='to invoice' ⇒ `invoice_ids=[]`, confirmed on the stale list) OR `payment_state='not_paid'` → no payment recorded → if it matches an unreconciled j6 bank line (name/amount/date) → **RECORD then close; never close without recording**.
`payment_state` is the SINGLE source of truth for "is the money already recorded" → makes (a)/(b) deterministic + prevents double-recording. (A stale to-invoice SO by definition has no invoice yet → inherently branch-b; branch-a = an invoice that's paid but the SO/job wasn't closed, i.e. workiz_status != 'Done'.)

## ★ Money-critical subtlety (branch-b recording) + the recon gap
`_execute_payment` creates an account.payment that posts ITS OWN bank move — it does NOT reconcile the existing unreconciled FEED line. So recording via the app leaves BOTH the new payment's bank move AND the original feed line = the same deposit TWICE in the Chase ledger. The clean fix = reconcile the new payment/invoice AGAINST the `account.bank.statement.line` so its `is_reconciled` flips True (one deposit, one entry) — deeper than _execute_payment does today = a money-careful DJ decision (record-and-reconcile vs record-only-and-leave-the-gap).
- **RECON GAP:** the Chase feed imports lines but NOTHING reconciles them → 201 unreconciled j6 lines (incl. 32 Zelle), even for deposits already app-recorded as payments. Broader accounting hygiene; surface to DJ.

## Stale-SOs retool inputs
- Matcher input = live `account.bank.statement.line` (journal_id=6, `payment_ref` ilike 'zelle', recent) → parse payer/amount/date from the line → the existing fuzzy-matcher. REPLACES the manual `ir.config_parameter['zelle_payments_csv']` upload.
- Endpoints (dashboard.py): /api/stale_sos, /stale_sos page (static/owner/stale_sos.html), /api/stale_sos_with_payment_matches (the matcher = retool target), _stale_so_payment. STRIP the Workiz fields (x_studio_x_studio_workiz_uuid/_link/_status) + rename. See [[project_workiz_retirement]], [[feedback_data_location_odoo_vs_postgres]].
