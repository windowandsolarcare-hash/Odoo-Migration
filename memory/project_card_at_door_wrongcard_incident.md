---
name: project_card_at_door_wrongcard_incident
description: "2026-08-26 INCIDENT: 'Charge Card at Door' still opens Stripe HOSTED Checkout on DJ's phone → Stripe Link auto-used a PREVIOUS customer's (Vincent Russo) saved card and charged $200 for Bob Lis's job (SO 264956). Refunded same-day. Root cause: CARD_AT_DOOR_SPEC (custom Elements page suppressing Link/wallets) is designed but UNBUILT. Build it = P0."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-26T21:50:07.288Z
---

**INCIDENT 2026-08-26 (real money, resolved):** DJ, at "Bob's" door and near heat-stroke, tapped **💳 Charge Card at Door** for Bob Lis's job (**SO 264956**, $200 solar). The button (`doChargeAtDoor()` in `static/owner/v2_field.html`) calls `/owner/api/stripe/payment_link` and opens **Stripe's HOSTED Checkout page** in a new tab **on DJ's own phone**. Because it's DJ's phone, **Stripe Link auto-filled a PREVIOUS customer's saved card — Vincent Russo** — and the "pay" tap **charged Vincent $200 for Bob's job.** Succeeded 10:52 AM. **DJ refunded it same-day from the Stripe charge page (↩ Refund → full).** Vincent made whole.

**Two failures confirmed:**
1. **Wrong-card / wallet exposure — the exact thing `CARD_AT_DOOR_SPEC.md` was written (2026-08-18) to fix, but that spec is a DRAFT and was NEVER BUILT.** Current flow = hosted Checkout on DJ's phone = pops his Samsung/Google Pay + Stripe Link's remembered cards (incl. old customers'). The fix: our own **Stripe-Elements page** — card data only in the secure Element (browsers/Link can't autofill it), **wallets/Link SUPPRESSED on the door-charge path**, prefill customer from Odoo, camera-scan the CUSTOMER's card, save-on-file/charge-on-file, server-side instant record + webhook. **Building this is now P0.**
2. **Recording gap:** the $200 charge succeeded on Stripe but **nothing recorded in Odoo** (zero account.payment that day) — because door-charge records back only via a browser bounce/poll and **STRIPE_WEBHOOK_SECRET is not set** (the standing "waiting on DJ" money item). So Stripe is the ONLY source of truth for these — always check Stripe directly, not Odoo, for door charges.

**How to diagnose a "did it charge / whose card" question:** Odoo is NOT authoritative here (recording gap). Check **Stripe** — dashboard Payments/Transactions, or the Stripe restricted key (DJ keeps it in a Google Drive doc named "stripe" in **Saunders Vault**, per [[feedback_api_keys_via_file]]; NOT in Render-readable-by-Lead form). The charge page shows the card owner ("Charged to <name>") + line item (SO#) → mismatch of payer-name vs job-SO = wrong card → refund from that page.

Spec: `saunders-render-app/3_Documentation/CARD_AT_DOOR_SPEC.md`. Owner: Specialists (payments). Related: [[project_phase4a_sync]], [[feedback_assistant_use_app_workflow_not_raw_api]].
