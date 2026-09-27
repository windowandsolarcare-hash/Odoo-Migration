---
name: project_payment_paths_thread_capture
description: "The 3 payment code paths + which one threads a \"💵 Payment received\" timeline event into the customer's inbox"
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-27T05:56:10.585Z
---

**Payment recording has THREE code paths — know which is which before touching payment or timeline-capture code:**
1. **Job-detail Pay flow** → `dashboard.py` `_execute_payment` (~:4900). This is the LIVE owner-app payment path (live `/api/payment` = dashboard:6214). It threads the timeline event `💵 Payment received $X by <method>` via `append_inbox_event(..., source='system', label=None, index=False, direction='out')` at ~dashboard.py:4965, guarded by the already-paid early-return so a re-tap never double-threads.
2. **Stripe customer self-pay** (branded pay link → `/api/stripe/success` redirect + `/api/stripe/webhook`) → both funnel through `payments.py` `_stripe_record_and_close` (:695) → `finalize_payment` (payment_finalize.py). This path does NOT go through dashboard `_execute_payment`, so it was the one live payment path NOT threaded until the Stripe-funnel follow-up (2026-09-26, commit 7fd0eaaa): added the SAME `💵 Payment received $X by Card` append inside its `if so_id:` block after finalize_payment. **Idempotent for free** — `_stripe_record_and_close` books EXACTLY ONCE per `payment_intent` (the `wsc.stripe.processed.<intent>` key guards at :702/:713/:751 return early on any redirect+webhook re-fire), so it threads once.
3. **`field.py` `_execute_payment` (~:3373) is a DEAD shadowed twin** — the `/ask` voice router's copy that main.py's include-order makes dead (dashboard registers first). Do NOT edit it expecting effect (route-shadow trap, same class as `/owner/ask` + `/api/hemet/*`).

**Why:** a "payment isn't showing in the thread" or "add X to the payment flow" task must target the RIGHT path — dashboard for job-detail, payments.py for Stripe self-pay — and never the field.py dead twin. **How to apply:** timeline/thread captures use `index=False` (record-only, no needs-action escalation) + best-effort try/except so a thread-write can never touch the money path. Related: [[project_confirm_arm_on_inbox_send]], [[feedback_reuse_function_follow_full_logic]]. Manual method recorders (Zelle/cash/check/credit/venmo) live in payments.py too (`_stale_so_payment` + `api_record_*`).
