---
name: project_branded_receipt_page
description: "Payment receipts must be W&SC-BRANDED (our hosted page, texted to the customer), NOT Stripe's pay.stripe.com receipt. Governing design: Stripe touches ONLY the card-processing moment; everything before + after is ours + our-branded."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-08T19:07:16.791Z
---

**DJ reaffirmed the payment-flow design, 2026-09-08 (correcting current carddoor behavior).**

**Governing principle:** Stripe is a **last-mile processor ONLY** — it should appear to the customer at the actual card-entry/charge moment and nowhere else. Everything before (quote, ack, confirmation) and after (receipt) is done by us and carries **Window & Solar Care branding**, so it looks like it's from us, not Stripe.

**What was already right:** the card-at-door page (`carddoor.py`) is already OUR page (our logo, layout, "Window & Solar Care"); Stripe only renders the bare card field. Good — matches the principle.

**What was WRONG (the gap DJ caught):** the receipt. `/api/carddoor/receipt` just set Stripe `receipt_email`, so Stripe mailed its own `pay.stripe.com`-branded receipt. That's the opposite of the intent.

**The fix (DJ chose: branded PAGE + TEXT the link) — routed to Specialists 2026-09-08:**
1. NEW public magic-link receipt PAGE `/receipt/{token}` — reuse the calfeed.py `appt_link` token pattern. Brand: W&SC logo, dark-blue **#1e5aa8** accents ([[feedback_brand_dark_blue_accents]]), light-gray hairline under each line item ([[feedback_report_gray_lines]]), mobile + print friendly. Shows amount, date, service, job #, **card brand + last4**, "Paid in full", business contact.
2. Capture card brand+last4 at record time (PaymentIntent `latest_charge.payment_method_details.card`) — money/record path (`_stripe_record_and_close`) otherwise UNTOUCHED.
3. Deliver by **Twilio `messaging.send`** (the ported number) — DJ **taps to send** (keep the standing "always ask, never auto-send" receipt rule); email-the-same-link fallback for a customer with no cell.
4. **SUPPRESS Stripe's own receipt** — stop setting `receipt_email`. (A card-at-door PaymentIntent with no receipt_email + no Customer won't auto-email, but confirm the Stripe dashboard customer-email setting is off for zero Stripe-branded mail.)

**How to apply:** any customer-facing artifact in the pay flow (receipt, confirmation, ack) must be W&SC-branded and delivered by us — NEVER lean on a Stripe/third-party hosted page for the customer touch. Lead owns the brand look + QCs the rendered page before it reaches DJ. See [[feedback_ported_means_twilio]], [[feedback_wsc_email_from_domain]].
