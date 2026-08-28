---
name: project_stripe_success_dead_twin
description: "★ CORRECTION to project_stripe_webhook: the idempotent _stripe_record_and_close refactor of /api/stripe/success landed in payments.py — the SHADOWED DEAD TWIN. dashboard.py is included first in main.py so IT serves /api/stripe/success, and that live copy books to journal_id 7, has NO idempotency key, and never calls finalize_payment. The helper + the webhook (unique to payments.py) are live and fine."
metadata:
  node_type: memory
  type: project
  modified: 2026-08-28T19:24:00.000Z
---

**Found 2026-08-28 (Specialists) while building the Card-at-Door page. Not yet fixed — flagged to Lead;
it is existing working money code, so it needs DJ's call before anyone touches it.**

**The shadowing.** `main.py` includes `dashboard.py` under `/owner` at line 242 and `payments.py` at
line 250. Both define `/api/stripe/success`, `/api/stripe/payment_link`, `/api/stripe/tip_page`,
`/api/stripe/create_checkout`, `/api/stripe/logo`, `/api/stripe/check_payment`, `/api/stripe/cancel`.
**First include wins → dashboard.py serves all of them; payments.py's copies never run.** Already known
for payment_link/tip_page/create_checkout ([[project_stripe_routes_live_in_dashboard]]) — this memory
adds that **`/api/stripe/success` is in the same set**, which had not been noticed.

**Why it matters.** `project_stripe_webhook` records that `/success` "was refactored to route through
`_stripe_record_and_close` — that IS the dedup." **That refactor is in payments.py, i.e. in the dead
twin.** So the LIVE redirect path (dashboard.py ~line 5896) today:
- books with **`journal_id: 7`** — while `_execute_payment`, `_stripe_record_and_close` and every other
  payment path use **journal 6** with `payment_method_line_id` carrying the method (credit = 7). It looks
  like a payment-method-line value was written into the journal field.
- has **no idempotency key** — so once `STRIPE_WEBHOOK_SECRET` lands, a redirect **and** a webhook for the
  same Checkout Session can **double-book** (the webhook's own `_stripe_record_and_close` guard only
  protects writers that go through the helper; the live `/success` does not).
- never calls **`finalize_payment`** — so a hosted-Checkout card payment does **not** mark the job Done,
  roll the gate/pricing snapshot, or spawn the next maintenance SO. It only posts + registers, then calls
  `specialist_billing.settle`.

**Still true and unaffected:** `_stripe_record_and_close` itself and `POST /api/stripe/webhook` live in
payments.py and are **NOT shadowed** (no dashboard twin defines them), so both are live. The new
Card-at-Door path calls the helper directly and is therefore correct and idempotent.

**How to apply.** Before editing ANY `/api/stripe/*` endpoint, confirm which file SERVES it — grep the
path across `routers/` and check `main.py` include order. Assume dashboard.py wins for anything it also
defines. When the fix is approved, the shape is: point dashboard.py's `/success` at
`_stripe_record_and_close` (keeping its nice card brand/last4 chatter), which fixes the journal, the
idempotency and the missing finalize cascade in one move — but that is a money-path change to working
code and needs DJ's yes first. See [[feedback_never_remove_working_code]].
