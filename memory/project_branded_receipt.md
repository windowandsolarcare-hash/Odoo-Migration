---
name: project_branded_receipt
description: "W&SC-branded receipt REPLACES Stripe's pay.stripe.com receipt. NEW public page /receipt/{token} (routers/owner/receipt.py, reuses calfeed so-token, registered NO-prefix in main.py). carddoor /api/carddoor/record stores a wsc.receipt.<so_id> snapshot (amount/paid_at/brand/last4); /api/carddoor/receipt now TEXTS (or emails) that branded link instead of setting Stripe receipt_email. Paid-view affordance = 'Text the receipt' (DJ taps — always-ask)."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T19:54:32.403Z
---

**Built 2026-09-08 (Lead spec). Governing principle DJ reaffirmed: Stripe touches ONLY the card-processing moment; everything before/after is OURS and OUR-branded.** So Stripe's own pay.stripe.com receipt is suppressed and replaced with our page.

**The page — `routers/owner/receipt.py` (NEW, PUBLIC, no prefix).** `GET /receipt/{token}` where token = **`calfeed.make_so_token(so_id)`** (HMAC over `'so:<id>'`, unguessable; reused, not reinvented). Registered in `main.py` right after calfeed: `app.include_router(owner_receipt.router)` — public because it isn't under `/owner|/tech|/cheryl` (PROTECTED_PREFIXES). Renders W&SC brand: logo `/owner/api/stripe/logo` (already PUBLIC in authz), dark-blue **#1e5aa8** header/accents, light-gray hairline (`#e6ebf1`) under each line item, mobile-first + `@media print`. Content: "✓ Payment received / Paid in full", amount, "Paid on <date>", SO service lines (or SO name fallback), Job # (SO name), "Visa ••1234" card line, business contact **760-334-5355 / windowandsolarcare@gmail.com / wscare.pro**, warm "Thank you, <first>!". Helper `receipt_link(so_id)` → `{PUBLIC_BASE}/receipt/{token}`.

**Data snapshot — `wsc.receipt.<so_id>`** (ir.config_parameter, JSON `{amount, paid_at, brand, last4}`). Written in `carddoor.py /api/carddoor/record` right after `_stripe_record_and_close`, on every verified-succeeded run (idempotent set_param, so a re-text still works when the WEBHOOK booked the payment first). brand/last4/created come from the expanded `latest_charge.payment_method_details.card`. The page reads this snapshot; falls back to SO `amount_total` if absent.

**Delivery = TEXT (email fallback) — `/api/carddoor/receipt` reworked.** STOPPED setting Stripe `receipt_email` on the intent+charge (that was Stripe's branded receipt — gone). Now takes `channel` (`text`|`email`):
- **text** → looks up the customer cell via `_carddoor_person` (extended to return `phone` from person `mobile`/`phone`, else property) and `messaging.send(cell, body, partner_id, so_id, kind='receipt')` (the canonical Twilio send). No cell on file → returns `{need_email:True}` so the UI nudges to email.
- **email** → sends the SAME branded link via Odoo `mail.mail` (email_from=**windowandsolarcare@gmail.com** per [[feedback_wsc_email_from_domain]]); saves the address back only when the person has none.
- Chatter logs "🧾 Branded receipt texted/emailed to …".

**Frontend (carddoor paid-view).** Receipt card is now Text-first: green **"📱 Text the receipt"** (primary) + "Or email it" input with **"📧 Email the receipt"** + "No receipt". `textReceipt()`/`emailReceipt()` share the `_receipting` guard. **Always-ASK is honored** — nothing auto-sends; DJ taps the button, which IS the approval.

**★ Polish 2026-09-08 (Web QC):** added a fine-print legal line **"Window & Solar Care, LLC"** (WITH the comma, per CA SOS) as a `.legal` line in the receipt FOOTER/biz block — a receipt is a money document the customer keeps, so it carries the legal entity name; the header/trade name stays "Window & Solar Care" (no LLC). **Biz-facts drift note:** BIZ_PHONE/BIZ_EMAIL/BIZ_WEB + trade name are hardcoded constants in receipt.py — there is NO shared business-facts module in the app (the phone is ALSO hardcoded in `voice.py:644`). Values are correct now; centralizing = a new config module + touching multiple files, so it was NOT forked unprompted — logged for a later dedicated centralization pass. (Lead endorsed not forking now.)

**Verify:** all 3 files py_compile; carddoor inline JS node --check clean; deploy watched to LIVE = the `owner_receipt` import + route registration resolved at boot. **Open follow-ups:** (1) Lead QCs the rendered brand look against #1e5aa8/logo. (2) DJ/Operator must confirm the **Stripe Dashboard → customer emails / successful-payment receipt toggle is OFF** so Stripe doesn't ALSO email its own receipt (the code no longer sets receipt_email, but a dashboard-level auto-receipt is a separate setting). See [[project_stripe_payments_not_reconciled_to_odoo]] neighbor + [[project_calfeed_token]] token pattern.
