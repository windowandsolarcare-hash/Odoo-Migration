---
name: project_stripe_payment_methods
description: "Stripe Checkout methods are controlled by the Dashboard config, NOT app code. As of 2026-08-13: card/Link/Apple Pay/Cash App = ON; PayPal + Google Pay = OFF (Bart couldn't pay by PayPal via the link)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-14T07:50:22.299Z
---

**Which payment methods a customer sees on the Stripe payment link is decided by the Stripe DASHBOARD, not the app.** `routers/owner/payments.py` `api_stripe_create_checkout` (creates the Checkout Session) does NOT pass `payment_method_types` or `automatic_payment_methods` — so Stripe uses whatever is toggled on in the account's Payment Method Configuration. Flow: field "Charge at Door"/"Send Stripe Link" → `/owner/api/stripe/payment_link` → returns `wscare.pro/owner/api/stripe/tip_page` → "Proceed to Checkout" → `/api/stripe/create_checkout` → Stripe hosted checkout.

**Account state 2026-08-13** (Stripe acct `acct_1Me495ImQWeVzsL9`, default PMC `pmc_1ReU1NImQWeVzsL9CKXw9SyW`):
- ON: **card, Link, Apple Pay, Cash App Pay**
- OFF: **PayPal** (available=false, preference=off), **Google Pay** (off), Amazon Pay, Affirm, Klarna.

**Google Pay ENABLED 2026-08-13** (via API `POST /v1/payment_method_configurations/{PMC}` `google_pay[display_preference][preference]=on`; confirmed in the Stripe dashboard list = "Enabled"). Now live on the link.

**★ PayPal is NOT available on Stripe for US accounts — FULL STOP.** Confirmed 2026-08-13 two ways: (1) API — account (`country=US`) has NO `paypal_payments` capability and PMC shows `paypal available=false` even after setting preference=on; (2) visually read the Stripe Dashboard payment-methods list (all 39 methods) via the Chrome extension — **PayPal is not in the list at all** (not disabled, just absent). Stripe only offers PayPal to merchants in the EEA/UK/Switzerland; US businesses cannot accept PayPal through Stripe, period. So the app's Stripe link can NEVER offer PayPal as long as W&SC is US-based on Stripe. Don't keep trying to "enable" it. (The paypal preference=on I set via API is inert — harmless.)

**Implication / how to take a PayPal payment:** Customer must pay through DJ's OWN PayPal, OUTSIDE Stripe/the app — a PayPal.me link or a PayPal invoice DJ sends himself — then the payment is recorded in the app manually (there's a Venmo/other manual-payment path; PayPal would record as "Other"). Via the app's Stripe link a customer can pay by card / Apple Pay / Google Pay / Cash App Pay / Link — but NOT PayPal. (Came up 2026-08-13: customer "Bart" wanted PayPal.)

**Field payment method chips MERGED 2026-08-14:** the old separate **Credit** (manual card-record, journal-only, legacy Workiz-terminal era) and **Stripe** chips are now ONE chip labeled **"Credit Card"** with `data-m="stripe"` (v2_field.html method-btns). It runs the full Stripe flow (Send Stripe Link + Charge Card at Door, which only shows when this is selected). The manual `credit` chip was removed; `preselectPayMethod` maps a historical `last_payment_method='credit'` → the `stripe` chip so card-last-time jobs auto-select it. Backend `credit` path (`_execute_payment` map `{'credit':7}`, `/api/record_credit_payment`) left DORMANT (not removed). Method row is now: Check, Cash, Zelle, Venmo, Credit Card. Note: `_execute_payment` still does a Phase-4A `_sync_so_with_workiz` for ALL manual methods (legacy, shared — not touched).

**Stripe secret key** lives as Render env `STRIPE_SECRET_KEY`; also in DJ's Drive doc "00193 · Stripe API - Odoo Credit Card" / "00001 · Stripe API" (his file-based key sharing). Read-only config check: `GET https://api.stripe.com/v1/payment_method_configurations` with `Authorization: Bearer sk_live_...`.

**Charge-at-Door button:** `doChargeAtDoor()` in v2_field.html reads the amount from the **Record Payment** `#pay-amount` box (must be filled first) then opens the Stripe page. Fixed 2026-08-13: it opened the page in a NEW tab and silently failed when the mobile popup blocker killed it — now falls back to same-tab (`window.location.href`). If "nothing happens" persists, the cause is an empty amount field (shows an easy-to-miss "Enter the job amount first" status). "Charge at Door" = DJ enters the customer's card himself on his phone; "Send Stripe Link" = texts the customer the link so THEY pay (wallets show on their device).
