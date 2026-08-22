---
name: project_stripe_webhook
description: "Stripe server-to-server webhook POST /owner/api/stripe/webhook (payments.py) — the robust card close-out that doesn't depend on the browser redirect (the gap that left Bart paid-at-Stripe but unpaid in Odoo). Fail-closed HMAC sig verify; idempotent shared _stripe_record_and_close keyed on payment_intent. INERT until STRIPE_WEBHOOK_SECRET is set in Render + endpoint registered in Stripe dashboard."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-21T22:21:49.976Z
---

**Built 2026-08-21 (Specialists, Lead-approved with 5 conditions).** Card payments used to close out ONLY via `/owner/api/stripe/success` — a browser REDIRECT. If the customer's tab closed before returning (Bart Ogburn), the money hit Stripe but the Odoo invoice stayed unpaid + SO stayed Scheduled. Fix = a server-to-server webhook that closes out independent of the browser.

**The endpoint:** `POST /owner/api/stripe/webhook` in `routers/owner/payments.py` (commit 80eb44c). Handles `checkout.session.completed` (+ `checkout.session.async_payment_succeeded`). Checkout Sessions carry our `metadata[so_id]`/`metadata[invoice_id]` (set at session creation in `api_stripe_create_checkout`), so the webhook resolves the invoice/SO with NO browser involvement; the Stripe `payment_intent` is the idempotency key.

**5 safety properties (all Lead conditions):**
1. **Idempotent** — ONE shared helper `_stripe_record_and_close(invoice_id, so_id, amount, intent_key, source)` is now used by BOTH `/success` (backgrounded) AND the webhook. Dedup key = `ir.config_parameter` `wsc.stripe.processed.<payment_intent>` set BEFORE finalize; PLUS a 2nd guard that skips if the invoice is already `paid`/`in_payment`/`reversed`. Books EXACTLY once in any order. `/success` was refactored to route through this (was inline post+register+finalize) — that IS the dedup.
2. **Signature FAIL-CLOSED** — `_verify_stripe_sig(raw_body, sig_header, secret, tolerance=300)` does MANUAL HMAC-SHA256 (no `stripe` lib; app uses raw httpx). Parses `Stripe-Signature` `t=`/`v1=` (multiple v1 supported), `signed = "<t>.<raw_body>"`, `hmac.compare_digest`, ±300s replay window. No secret / bad sig / stale ts / bad json → **HTTP 400, books nothing**. (`import hmac, hashlib` added to payments.py line 3.)
3. **Namespaced** route (`/api/stripe/webhook`) — grep-confirmed unique across payments/dashboard/main (route-shadow rule).
4. **Secret via Render env** — reads `os.environ['STRIPE_WEBHOOK_SECRET']`. ★ NOT SET as of build → endpoint is **INERT/fail-closed** (returns 400 to everything) until it lands. Set it via Render env **POST/merge, NEVER PUT** ([[feedback_render_put_env_vars]]). Needs Stripe ACCOUNT access (register the endpoint URL in the Stripe dashboard for those events → it generates the signing secret). Lead/DJ own the Stripe-account side; Specialists does the Render env POST once the secret exists.
5. **End-to-end content test** (run AFTER secret lands): a test-mode checkout completed with the browser TAB CLOSED must yield invoice paid + SO Done, no redirect. Verify by CONTENT, not a 200.

**Verified by content at build time:** deployed on Render, unsigned POST to `/owner/api/stripe/webhook` → HTTP 400 (route live + fail-closed). Full money-moving path can't be verified until the secret is configured.

**Same commit-cluster:** the `/api/payment` route collision was de-duped (commit c36aadf) — payments.py's copy was a dead byte-identical shadow (dashboard.py's wins, registered first + has `_sched_cache_bust()`); removed it, canonical stays in dashboard.py. See [[project_so_partner_id_is_property]] and the Bart close-out (canonical `_execute_payment`/`finalize_payment`).
