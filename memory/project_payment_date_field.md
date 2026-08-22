---
name: project_payment_date_field
description: "Record Payment (job detail) has a Payment date field (defaults to Pacific today, editable) for late payments"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
---

**Record Payment on the job-detail screen (field.html) has a Payment DATE field (added 2026-07-01).** For all methods (check/cash/zelle/venmo/credit). Defaults to Pacific today (`#pay-date` set to `_todayPT()` when the payment section shows), so normal same-day recording needs no input; DJ changes it only when recording a payment (e.g. a Zelle) a few days after it hit the bank, so it ties to the bank on the right date. `doPayment()` sends `payment_date` in the `/owner/api/payment` body; the confirm dialog shows "dated <date>" when it's not today.

★ The BACKEND already supported this — `/owner/api/payment` (payments.py) reads `body.get('payment_date')` → `_execute_payment(...)` (dashboard.py) does `payment_date = str(args.get('payment_date') or today)` → `account.payment.register.payment_date`. Only the UI was missing it. So don't "add backend support" — it's there. `.pay-date-input` deliberately has NO `-webkit-appearance:none` (avoids the iOS date-picker bug, see [[feedback_ios_date_input_appearance]]). Included in the paid-state show/hide set (`.pay-date-row`). There is a SEPARATE payment sheet (`psDoPayment` → same endpoint) that still defaults to today server-side — not given a date field (DJ asked for the job-detail card).
