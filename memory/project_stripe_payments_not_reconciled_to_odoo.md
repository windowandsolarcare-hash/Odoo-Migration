---
name: project_stripe_payments_not_reconciled_to_odoo
description: "Stripe card payments can succeed but NOT reconcile into Odoo (invoice stays not_paid, no account.payment). To find a customer's Stripe payment, search by amount+date — NOT name/email."
metadata: 
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-02T23:34:27.706Z
---

A customer can pay by **credit card via Stripe and the charge succeeds**, yet Odoo shows **no payment** — invoice `payment_state='not_paid'`, no `account.payment`, and the SO still sits at its pre-payment `workiz_status`. Stripe→Odoo reconciliation is **not automatic** (confirmed 2026-09-02 with Robert Hollenbeck: Stripe charge `ch_3U9T0rImQWeVzsL91R0rYmtV` / PaymentIntent `pi_3U9T0rImQWeVzsL9145zjhF7`, $150 Visa ****7288, succeeded 2026-08-28, but Odoo invoice INV/2026/02542 (id 11882) still not_paid, SO 264957 (id 17587) still 'Scheduled').

**★ ROOT CAUSE + LIVE FIX (2026-09-02):** Hollenbeck went through the **OLD** hosted-Checkout door flow, which recorded the Odoo payment ONLY on the `/api/stripe/success` browser redirect — his phone never completed it, so the money stranded. The live door flow is now **`routers/owner/carddoor.py`** (our own Stripe Elements page): `/api/carddoor/record` re-reads the PaymentIntent from Stripe and books via the ONE canonical idempotent close-out `payments._stripe_record_and_close` — so NEW charges can't strand this way. See [[project_stripe_abandoned_checkout_strands_invoice]].
**Booking a stranded charge the CANONICAL way (reuse, don't raw-write):** POST the succeeded PaymentIntent to **`/owner/api/carddoor/record`** with `{payment_intent, invoice_id, so_id, access_code}` — it re-verifies with Stripe and books idempotently through the same close-out (safe to retry). That's how Hollenbeck's stranded $150 should be recorded, not a raw `account.payment.register`.

**Why it's easy to miss the Stripe charge when searching:**
- The charge's **billing name is the CARDHOLDER as typed** and can be MISSPELLED ("Robert Hollen**back**" vs the Odoo "Hollen**beck**") — name search fails.
- **billing_details.email = the BUSINESS email** (`windowandsolarcare@gmail.com`), not the customer's — email search fails. `receipt_email` is often null too.
- `metadata` and `description` are usually **empty** — no SO number to join on.
- Stripe's charge Search API does NOT support `billing_details.email` as a query field (400s).

**How to actually find it:** list `GET /v1/charges?created[gte]=<epoch>&limit=100` across the date window and **eyeball by amount + date** (the charge date matches the job/invoice date). That's the reliable join.

**Stripe access:** the live Stripe secret key lives in Google Drive **Saunders Vault** → doc titled "Stripe" (live-mode key); a local session may also mirror it to a local key file. Stripe account id `acct_1Me495ImQWeVzsL9`. Odoo API key is in the standard local Odoo key file. (Never commit the actual key to the repo — GitHub secret-scanning/classifier will block it, correctly.)

**How to apply:**
- "How did X pay / did X pay by card?" → after checking Odoo, query Stripe by amount+date before concluding "unpaid."
- A succeeded Stripe charge with no Odoo payment = a **reconciliation gap** (money-touching). Surface to DJ; have **Operator** record the card payment against the invoice (journal: Credit Card, id=20). Do NOT raw-write — go through the app/Operator per [[feedback_assistant_use_app_workflow_not_raw_api]].
- Likely **systemic** — other card payments may be unrecorded. Flag to Specialists to check whether Stripe→Odoo auto-reconciliation should be built. See [[feedback_never_send_dj_to_odoo]].
