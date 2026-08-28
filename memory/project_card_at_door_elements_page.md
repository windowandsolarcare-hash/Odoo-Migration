---
name: project_card_at_door_elements_page
description: "Card-at-the-Door = OUR OWN Stripe Elements page, routers/owner/carddoor.py (NEW file, 2026-08-28), routes /owner/api/carddoor/{page,intent,record,receipt}. Replaces hosted Checkout on the DOOR path only (send-link keeps Checkout + wallets). No Link/no wallets is STRUCTURAL: bare Card Element + payment_method_types=['card']. Records via canonical _stripe_record_and_close, idempotent on payment_intent. INERT until STRIPE_PUBLISHABLE_KEY is set in Render."
metadata:
  node_type: memory
  type: project
  modified: 2026-08-28T19:23:00.000Z
---

**Built 2026-08-28 (Specialists, cloud) — CARD_AT_DOOR_SPEC.md P1, Lead-directed after DJ hit the
wrong-card bug a second time in the field.** Full build report: `saunders-render-app`
→ `3_Documentation/CARD_AT_DOOR_P1_STATUS.md`.

**Why it exists.** The door charge opened Stripe's **hosted Checkout on DJ's own phone**. Hosted
Checkout treats the phone's owner as the customer, so it offered **Stripe Link** and Google/Samsung
Pay — and Link surfaced **a previous customer's saved card (Vincent Russo) and charged him $200 for Bob
Lis's job** (2026-08-26). The interim `payment_method_types=['card']` fix kills Link but **does NOT hide
Apple/Google/Samsung Pay** — those are card wallets *under* the `card` method, and hosted Checkout has
**no per-session flag** to suppress them. That is why a hosted page could never be made safe here.

**★ The guarantee is structural, not a setting** — it holds even with account-level Link ON:
1. The page renders the **bare Card Element** (`stripe.elements().create('card')`) — a raw card field.
   Wallet buttons come only from a `paymentRequestButton`/`expressCheckout` Element; Link UI only from a
   `linkAuthentication`/`payment` Element. **The page creates none of them** — there is no code path
   that can paint one. (Verified by grepping the live served HTML: 0 hits outside one comment line.)
2. The PaymentIntent is created with explicit **`payment_method_types[0]=card`**, NOT
   `automatic_payment_methods` — Link is not an eligible method on the intent either.
**If anyone ever "modernizes" this to the Payment Element, the guarantee is GONE** unless they also pass
`wallets:{applePay:'never',googlePay:'never'}` and keep Link off. Don't swap the element casually.

**Routes** (all namespaced `/api/carddoor/*` so nothing can shadow them — the route-shadowing rule):
- `GET /api/carddoor/page?so_id=&amount=[&invoice_id=&so_name=&access_code=]` — the page. With no
  `invoice_id` it mints/reuses the draft invoice itself by calling the CANONICAL
  `dashboard._create_stripe_tip_link(..., door=1)` (lazy import — invoice-creation logic stays in one
  place). **So the page is usable by direct link with just so_id + amount.**
- `POST /api/carddoor/intent` — creates the card-only PaymentIntent. Sends
  `Idempotency-Key: carddoor-<invoice_id>-<cents>`, so a double-tap or a retry after a lost response
  returns the SAME intent, never a second one. An already-`succeeded` intent returns `already_paid` and
  the client skips confirm.
- `POST /api/carddoor/record` — **re-reads the intent from Stripe** (never trusts the browser that it
  succeeded), uses Stripe's **`amount_received`** as the money-truth, prefers the ids in the intent's
  own metadata over the client's, then calls **`payments._stripe_record_and_close`** — the ONE canonical
  close-out (journal 6 → post → finalize cascade: Done, gate/pricing snapshot roll, next maintenance SO,
  funds text), **idempotent on `payment_intent`**, the same key the webhook uses. This is what removes
  the browser-bounce dependency that stranded Vince, Renee and Bart.
- `POST /api/carddoor/receipt` — sets `receipt_email` (PI + charge) and saves the address back to the
  PERSON record **only if they had none**. **Asked, never automatic** (spec decision #3).

**Prefill resolves the PERSON, not the property** — SO `partner_id` is the property child; the person is
its `parent_id` ([[project_so_partner_id_is_property]]). Skipping that is how the pay-link email greeted
"Hi 73200 El Paseo."

**Phone-edge-case handling** (all per the CLAUDE.md phone rules): `_charging` double-tap flag + button
disable; `AbortController` timeouts on every money call (20–30 s); the intent id goes to **localStorage
BEFORE** confirming, so a dropped signal / killed webview finishes the booking on the next page open;
when recording fails the page says in plain words that the card WAS charged and **not** to re-charge.

**★ INERT until `STRIPE_PUBLISHABLE_KEY` is set in Render env** (POST/merge, NEVER PUT —
[[feedback_render_put_env_vars]]). Live page currently reports `data-nokey="1"`; it hides the form and
tells DJ to use Send Stripe Link instead. A publishable `pk_live_…` is public by design (it ships in
client JS) — it is not the secret key.

**Still open:** (1) the `v2_field.html doChargeAtDoor` re-point — written + `node --check` clean but a
cloud session cannot push a 264 KB file ([[feedback_cloud_push_size_limit]]); exact patch is in
CARD_AT_DOOR_P1_STATUS.md §4. (2) P2 save-card/charge-on-file — suggest keeping the Stripe customer +
payment-method ids in `ir.config_parameter wsc.stripe.customer.<partner_id>` rather than new Odoo fields.
(3) `payment_intent.succeeded` is not yet handled by `/api/stripe/webhook` (it only handles
`checkout.session.*`), so the door path's belt-and-suspenders webhook needs that ~15-line branch in
payments.py — also blocked on the file-size limit.
