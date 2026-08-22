---
name: project_paid_without_payment_record
description: Migration-era invoices are payment_state=paid with NO account.payment record (bank-entry reconciled) — any paid-detection must trust invoice payment_state, not just account.payment.
metadata:
  type: project
---

2026-07-21 (Sally Walsh SO 003826): invoice INV/2026/02307 is posted + payment_state=paid, but zero account.payment records reconcile to it — early-2026 payments were reconciled via bank entries. The Job Screen searched only account.payment -> showed Record Payment on a paid job.

**Why:** two payment eras exist in this DB: account.payment records (the app flow, memo carries method) vs bank-entry reconciliation (migration era, no payment record).
**How to apply:** any "is this job paid" logic must fall back to invoice payment_state in ('paid','in_payment') when no account.payment is found. so_history in dashboard.py does this now (synthesizes a payments entry, memo 'Invoice marked paid'). Replicate in any new payment-status feature. See [[project_payment_journals_reality]].
