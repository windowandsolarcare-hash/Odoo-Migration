---
name: project_stripe_reconcile_intent_endpoint
description: "How to reconcile a STRANDED succeeded Stripe payment_intent into Odoo: POST /owner/api/stripe/reconcile_intent?pi=<pi> (NOTIFY_SECRET header/param, fail-closed) — Operator-fired on DJ's go. Verifies the pi succeeded at Stripe, pulls invoice/so from pi-or-session metadata, anti-double-books vs Odoo's own provider (payment.transaction.provider_reference), then books via the shared idempotent _stripe_record_and_close (journal 6, tip-aware). Shipped 2026-09-24, deploy dep-daqf65rbc2fs73focfd0."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-24T09:59:39.085Z
---

# Reconciling a stranded Stripe payment (the reconcile_intent endpoint)

**Shipped 2026-09-24 (Stripe fix "1a"), commit 07cc25b0 / deploy dep-daqf65rbc2fs73focfd0.** When a Stripe card charge SUCCEEDED but never reconciled to Odoo (the redirect-gap / unwired-webhook problem — see [[project_stripe_payments_not_reconciled_to_odoo]], [[project_stripe_abandoned_checkout_strands_invoice]]), this is the manual catch-up tool.

## The endpoint
`POST /owner/api/stripe/reconcile_intent?pi=<payment_intent_id>` (in `routers/owner/payments.py`).
- **Auth:** `NOTIFY_SECRET` — header `x-notify-secret` OR `?secret=`; **fail-closed** (401 if secret unset/missing/wrong), constant-time compare. Listed in `authz.py` PUBLIC_EXACT (cookieless so Operator's curl reaches it; the in-handler secret is the real gate).
- **What it does:** (1) verifies the pi `status == succeeded` at Stripe (Stripe is source-of-truth for status + amount, NOT the caller); (2) pulls `invoice_id`/`so_id` from the pi metadata, falling back to the checkout session that made the pi; (3) **anti-double-book** — refuses (returns `already`) if `payment.transaction.provider_reference == pi` (Odoo's OWN Stripe provider already booked it); (4) books via the shared idempotent `_stripe_record_and_close` → journal **6** (Chase Checking), **tip-aware**, full finalize cascade (service-type-aware).
- **Idempotent:** re-firing the same pi returns `{"already": true}` (config-param key `wsc.stripe.processed.<pi>` + payment_state guard). Safe to re-run.

## Who fires it + how
**Operator**, on DJ's explicit go (money-touching). Not Lead, not a raw Odoo write. Example (secret from env/Vault, never inline a live secret): `POST …/reconcile_intent?pi=pi_XXXX` with the `x-notify-secret` header.

## Tip handling (the standard CC-tip path)
If the Stripe `amount` exceeds the invoice total, the extra is a TIP: `_stripe_record_and_close` adds a **product-2 "Tip"** line (product 2 = the "Tip" service, `taxes_id: []`, income falls back to the Services category account), tax-cleared `[(6,0,[])]` so the line == the tip exactly, then re-posts (button_draft ONLY if already posted) so the invoice ends at `amount` with a real Tip line + $0 residual — never over-applies against a base-only total. Same base+tip-split path as Zelle/checks. **Verified live 2026-09-24:** Angela INV/2026/02538 = $60 Commercial Window Cleaning + $12 Tip, number PRESERVED across the re-post, residual $0.

## Still pending (1b, DJ-gated)
The DURABLE fix (un-shadow `/api/stripe/success`, wire a live `checkout.session` webhook so future charges reconcile automatically) is BLOCKED on DJ's Stripe-dashboard config (`STRIPE_WEBHOOK_SECRET`) — nightly window. Until then, reconcile_intent is the manual catch-up for any new strand. Ties to [[feedback_data_location_odoo_vs_postgres]] (journal/money = Odoo). MIRROR to Odoo-Migration/memory/.
