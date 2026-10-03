---
name: project_stripe_checkout_server_amount_and_pay_link
description: "MONEY/SECURITY (shipped 2026-10-03): Stripe create_checkout charged `base_amount` straight from the request body with no invoice check → a customer editing the tip_page ?amount= (or POSTing create_checkout) could underpay. Fixed: amount DERIVED SERVER-SIDE from the invoice (amount_residual; invoice∈SO.invoice_ids binding; cancelled/paid refused; tip bounded). Plus a short opaque wscare.pro/pay/<token> link (HMAC, kind c=card/z=zelle, ids only, no amount in URL) replacing the long tip_page/zelle URLs; old long links still work."
metadata:
  node_type: memory
  type: project
  originSessionId: 8a97aa73-5f27-4f02-a0f6-64f2dd10d242
  modified: 2026-10-03T02:23:26.347Z
---

**Underpayment hole (proven, code-only):** LIVE `api_stripe_create_checkout` = **dashboard.py:6217** (main.py includes `owner_dashboard` BEFORE `owner_payments`, both `/owner` → dashboard WINS; payments.py:442 twin is DEAD). It took `base_amount = float(body.get('base_amount',0))`, charged `base_amount+tip_amount` as the Stripe `unit_amount`, and read the invoice ONLY for `state` (to post-if-draft) — no amount check. The tip_page embedded `const BASE={amount}` from the URL `?amount=` (dashboard.py ~6179), so editing the link, or POSTing create_checkout directly (it's public — customer-reachable), let a customer pay $5 on an $85 job. Reconcile (`api_stripe_success`) was faithful (records Stripe's actual `amount_total`), so it recorded the underpayment accurately — the hole was the charge, not the record.

**Fix (shipped, Lead-QC'd hard — 3 rounds):**
1. **Server-derived amount:** post the invoice if draft, then charge `amount_residual` (open balance, respects partial payments). Draft→`amount_total`; no invoice→SO `amount_total`.
2. **invoice↔SO binding BEFORE any read/write:** reject unless `invoice_id ∈ sale.order(so_id).invoice_ids` — else a customer could pair an expensive SO with a cheap invoice id, or trigger `action_post` on a stranger's draft. (Lead caught this in QC round 1.)
3. **Refuse** `state not in ('draft','posted')` (cancelled) and a **paid invoice** (`amount_residual ≤ 0` → "already paid in full" — no re-charge).
4. **Both `so_id` + `invoice_id` required** (the tip-link builder always makes/binds an invoice, so legit flow always has both). Client `base_amount` never charged; a >$0.01 mismatch → **server log** (`logging` 'wsc.security'), not SO chatter (customer can't spam).
5. **Verified** `amount_residual` exists on account.move (fields_get) and that ALL current open invoices (0 of them) link outside `SO.invoice_ids` — so no already-sent long link breaks.

**Short /pay link (same deploy):**
- `booking.make_pay_token(so_id, invoice_id=0, kind='c')` / `parse_pay_token` → `(kind, so_id, invoice_id)`. HMAC over `pay:<k>:<so>:<inv>` on `BOOKING_TOKEN_SECRET`, format `<k>-<so>-<inv>-<sig>`. `k='c'` card (tip page, needs invoice_id), `k='z'` Zelle (invoice_id 0, amount from SO). IDs ONLY — no amount/name in the URL.
- Top-level `GET /pay/{token}` (main.py, mirrors `/c/{token}`): bad/tampered token → 404 (never 500); `k='z'` → `owner_payments.api_zelle_pay(so_id)` (SO-derived total); `k='c'` → `dashboard._pay_token_tip_page(so_id, invoice_id)` (same binding + server-derived amount + "already paid" page if residual 0). authz: `/pay/` added to PUBLIC_PREFIXES + PUBLIC_ROOT_PREFIXES.
- `dashboard._create_stripe_tip_link` returns `wscare.pro/pay/c-...` for customer links (door=0); owner Charge-at-Door (door=1) keeps the LONG tip_page link (preserves card-only wallet suppression). `specialist_billing._zelle_pay_url` returns `wscare.pro/pay/z-...`. Both fall back to the long URL if the token helper fails. The long `/owner/api/stripe/tip_page` + `/owner/api/zelle/pay` routes are UNCHANGED → **every already-sent long link keeps working.**

**How to apply / lessons:**
- **Never trust a client-supplied amount on a payment path** — derive it server-side from the invoice, every time. A faithful reconcile does NOT save you if the charge itself was attacker-controlled.
- **Bind the ids before acting** — `invoice_id` + `so_id` both from the body means the PAIR must be verified (invoice∈SO.invoice_ids) before any read-for-amount or write, or an attacker mixes a cheap invoice with an expensive job.
- Short links reuse the existing HMAC token scheme (`booking.make_token` style); a **kind marker** lets ONE `/pay` route serve multiple surfaces. Keep the old routes alive so sent links don't break.
- Two units touching the same file (dashboard.py here) MUST ship as ONE merged file (stale-base rule). Related: [[feedback_regression_guard_pushes]], [[feedback_reuse_function_follow_full_logic]], [[project_stripe_payments_not_reconciled_to_odoo]].
