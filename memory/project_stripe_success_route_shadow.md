---
name: project_stripe_success_route_shadow
description: "ROOT CAUSE of Stripe-paid-but-Odoo-unpaid strands — /api/stripe/success is route-shadowed (dashboard.py's bugged stub serves, payments.py's robust one is dead) + the webhook backstop is unwired"
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-24T03:01:09.104Z
---

**The Stripe reconcile gap (Bob Lis inv 11881 $200; Angela Rafferty inv 11864 $72; earlier Bart Ogburn, Robert Hollenbeck) has a two-part ROOT CAUSE** — confirmed in code 2026-09-24, reported to Lead, fix deferred to a nightly window (money is safe at Stripe; reconcile is recoverable):

1. **ROUTE-SHADOW.** `@router.get('/api/stripe/success')` is defined TWICE: `dashboard.py:6208` and `payments.py:751`. main.py includes `owner_dashboard` (L850) BEFORE `owner_payments` (L858), both under prefix `/owner` → **dashboard.py SERVES, payments.py is DEAD.** It's backwards: payments.py's (dead) is the ROBUST/INTENDED one — it reconciles through **`_stripe_record_and_close`** (the ONE idempotent path, keyed on `payment_intent`, SHARED with the webhook) and was written specifically to fix this strand ("the redirect-only gap that left Bart Ogburn paid-at-Stripe but Scheduled/unpaid"). The dashboard.py version that actually serves is the older/inferior one: inline `account.payment.register` wizard (journal_id=7), and it **early-returns the OK page with ZERO Odoo calls when `session_id` is missing/invalid** (dashboard.py:6221 `if not session_id or not invoice_id: return _ok_html`). Bob's 00:29 redirect arrived with no session_id → instant 200, redirect home, no reconcile.

2. **WEBHOOK BACKSTOP UNWIRED.** The DESIGNED robust close-out is the webhook `POST /api/stripe/webhook` (payments.py:791, NOT shadowed — POST) — server-to-server, independent of the browser redirect, idempotent via `_stripe_record_and_close`. It **fail-closes (400, books nothing) if `STRIPE_WEBHOOK_SECRET` is unset** (payments.py:798) and only fires if the Stripe dashboard is configured to POST that endpoint. Evidence it's currently NOT functioning: Bob's succeeded charge triggered NO server-side reconcile at all — if the webhook were live, it would have reconciled him regardless of the browser redirect. So EVERY redirect-gap payment strands.

**Both success_url builders** (dashboard.py:6095, payments.py:462) DO include `session_id={CHECKOUT_SESSION_ID}`, so a normal Checkout redirect carries it — why Bob's lacked it is secondary (re-visit / non-standard redirect); the architecture (shadow + unwired webhook) is the real defect.

**FIX (nightly window, DJ/rule-10-gated on the removal):** (a) un-shadow so payments.py's robust `_stripe_record_and_close`-based handler serves (retire or delegate dashboard.py's), AND (b) make the webhook LIVE — set `STRIPE_WEBHOOK_SECRET` on Render + register `https://wsc-field-assistant.onrender.com/owner/api/stripe/webhook` in the Stripe dashboard. The webhook is the durable backstop that makes reconcile NOT depend on the fragile browser redirect.

**To reconcile an already-stranded charge** (e.g. Bob pi_3UJ0Ww): the ONLY live app-native trigger to `_stripe_record_and_close` is a **Stripe webhook event RESEND** from the dashboard → POST /owner/api/stripe/webhook — which requires the webhook to be wired first. `/api/stripe/success` can't be used (payments.py's is shadowed by the bugged dashboard stub). There is NO direct HTTP endpoint to invoke `_stripe_record_and_close` for an arbitrary pi.

**Scope of the gap (150-day card-check, 2026-09-24):** small — Bob Lis $200 + Angela Rafferty $72 (verify her $72-Stripe vs $60-Odoo-residual mismatch) real; two $1/$2 May-10 rows are TEST charges (invoice not found).

Ties to [[project_stripe_payments_not_reconciled_to_odoo]], [[project_stripe_abandoned_checkout_strands_invoice]]. Instance of the route-shadow class ([[feedback_check_endpoint_map_first]] / dashboard.py shadows late-registered routers): dashboard.py:6208 wins over payments.py:751 — verify which file SERVES a route before trusting its behavior.
