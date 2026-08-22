---
name: project_zelle_customer_ux
description: "Making Zelle EASY for W&SC customers (older, error-prone typing DJ's long email). Verified facts 2026-08-05: Zelle blocks Twilio/VoIP numbers (email-only token), Chase has a personal QR code, standalone Zelle app died Apr 2025. Build: itemized Text Zelle request → branded pay page (QR + tap-to-copy email + total) → auto-arm paywatch."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T02:04:41.933Z
---

**Goal:** stop customers hand-typing `windowandsolarcare@gmail.com` (long → typos, esp. older customers). Part of the Zelle collection loop: Text Zelle request → customer pays → Gmail watcher (specialist_paywatch.py) pops "record + mark Done?" card.

**Verified 2026-08-05 (web research):**
- **Zelle needs a real MOBILE number** (SMS-verifies the recipient) and **BLOCKS VoIP** → DJ's Twilio numbers can NEVER enroll in Zelle. **Email is his only Zelle token.** Don't try to give customers a phone number for Zelle.
- **Zelle QR code is real + the unlock.** Zelle's standalone app shut down **Apr 1, 2025** — it's now bank-app-only. DJ's Zelle lives at **Chase** (paywatch reads Chase Zelle alerts). Get his personal QR: Chase app → **Zelle → Receive → "Show My Code"** (or Zelle settings → Zelle QR code → My Code). Scanning it auto-fills DJ as recipient — customer types nothing. He screenshots it once; we host it. Caveat: QR only helps customers who scan from inside their bank's Zelle screen — not universal, so ALSO give tap-to-copy + the link.
- **Long email doesn't need changing** if the UX hides it (QR + one-tap-copy button + a wscare.pro link the customer taps instead of typing). Re-enrolling Zelle to a shorter email/alias = bank-side risk, skip unless DJ insists.

**★ QR is DOOR-ONLY (DJ 2026-08-05, correct):** a QR texted to the customer's phone is USELESS — one phone can't scan its own screen, and their bank app can't read a QR on that same device. QR needs TWO devices → in-person only. Also verified: **Zelle has NO shareable pay-link** (unlike Venmo/PayPal). Remote single-device options = (a) tap-to-copy email+amount on a page, (b) DJ sends a Zelle "Request" from Chase (customer just approves — cleanest but manual, no API), (c) Stripe card link (true one-tap, ~3% fee). So the TEXTED page uses tap-to-copy (NOT QR); QR lives on DJ's phone for the door.

**DONE 2026-08-05 (lead): door screen** `static/owner/v2_zelle_qr.html` (launcher tile 💸 "Zelle QR (show at door)") — shows DJ's cropped Chase Zelle QR big (`static/owner/zelle_qr.png`, WASC ...9008) + amount helper + tap-to-copy email fallback + steps. Verified live. Image is under /static (public) — it's a receive-only code meant to be shown to payers, low risk.

**DONE 2026-08-05 (lead): texted PAY PAGE** — `GET /owner/api/zelle/pay?so_id=<id>` in `routers/owner/payments.py` (`api_zelle_pay`), mirrors the Stripe tip_page. Public (whitelisted `/owner/api/zelle/pay` in authz). Reads amount_total + order_line from Odoo by so_id (just pass so_id; optional amount/so_name overrides). Shows itemized services + Total + **tap-to-copy email** + **tap-to-copy amount** + steps + **"pay by card" fallback** (POST /owner/api/stripe/payment_link → redirect). NO QR (tap-to-copy, per the door-only rule). Verified live SO 17389: $185+$145=$330. Customer link = `https://wscare.pro/owner/api/zelle/pay?so_id=<SO_ID>`.

**★ LOOP COMPLETE 2026-08-05.** Field button **"💸 Text Zelle request"** in v2_field Process Payment (`zelleRequest()`, next to Charge Card at Door) → POST `/owner/api/job/zelle_request {so_id, send:false}` preview → shared `_openSendBox` (editable, approve-first) → send:true (edited_body) → messaging.send + auto-arm via specialist_billing `_mark_asked(...,'zelle')` (idem `zelle:<so_id>`, quiet/STOP/DNC enforced). Specialist owns the endpoint (`routers/owner/*` billing); lead owns the button + pay page + door QR. Verified end-to-end: preview for 17389 = itemized ($330) + Zelle handle + `wscare.pro/owner/api/zelle/pay?so_id=17389` + signature. Full loop: tap → itemized text w/ link → customer pays (copy email/amount or card) → Gmail watcher pops "record + mark Done?" card.

**ENGAGEMENT TRACKING DONE 2026-08-05 (lead):** pay page beacons (`track()` → `POST /owner/api/zelle/track {so_id,event}`, whitelisted public) fire on **open**, **copy_email/copy_amount**, **card**. Endpoint stores `wsc.zelle.track.<so_id>` {open_at/n, copy_at/n, card_at} + SO chatter on first open/copy. **OPEN = soft** (texted links auto-preview/prefetch → could be a bot, never HUD). **COPY tap = strong** (a preview bot never taps) → **HUD glance card** `zelle_engaged:<so_id>` "💸 {cust} is paying — tapped Copy (${amt})", action → `/static/owner/v2_field.html?open_so=<id>`. Deduped (first-open/first-copy only). Verified end-to-end on throwaway SO. The DEFINITIVE signal remains the actual payment (specialist_paywatch Gmail watcher). In-app job deep link = `v2_field.html?open_so=<id>` (NOT the Odoo sales link, per [[feedback_never_send_dj_to_odoo]]).

**Build (approved — ALL DONE 2026-08-05):**
- Field **"Text Zelle request"** button in v2_field Process Payment (lead) → itemized text (greeting + services from SO lines + total + Zelle handle + wscare.pro link).
- Branded **Zelle pay page** (lead): big total, itemized, **one-tap COPY email** + **copy amount**, DJ's **Chase Zelle QR** (PENDING his screenshot).
- Backend send + **AUTO-ARM** `wsc.billing.awaiting.<so_id>` on send (specialist lane, mailed 2026-08-05) — reuse specialist_billing Zelle template, add itemization + link.
- **BLOCKER on DJ:** send the Chase Zelle "Show My Code" screenshot for the QR.

See [[project_click_to_call]] (dialer), specialist_paywatch (Gmail watch = approve-first, armed-by-work, not silent-auto yet), specialist_billing (canonical Zelle text).
