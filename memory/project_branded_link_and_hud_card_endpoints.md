---
name: project_branded_link_and_hud_card_endpoints
description: "Operator mechanics for the branded customer pages (invoice / quote / paid-receipt) and for pushing a custom review-first card onto the HUD feed: which endpoints MINT a link vs. SEND it, and how to stage a HUD card via /owner/api/feed/submit."
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-10-27T15:13:41.210Z
---

**Context (2026-10-27, Kathy Sell — DJ wanted ONE text combining a paid-solar RECEIPT link + a $215 QUOTE link, staged in his HUD, review-first + the quote amount adjustable at send.):** Mapping which app endpoints give a branded link without sending, which only send, and how Operator stages a HUD card.

**Three branded customer pages (all token/HMAC-signed, PUBLIC, read-only):**
- **Invoice doc** — `GET /owner/api/job/quote_view` is the QUOTE page; the INVOICE page link is minted by `invoice_view_url(so_id)` (dashboard.py). Branded itemized invoice.
- **Quote (estimate)** — `GET /owner/api/job/quote_view?so_id=&sig=` (dashboard.py:6652). Shows ONLY service + the SO's `amount_total` live (no pane counts/breakdown). Link minter = `quote_view_url(so_id)` (dashboard.py:5653).
- **Paid RECEIPT** — `GET /receipt/{token}` (receipt.py:61), token = `make_so_token(so_id)` (calfeed HMAC). Reads a payment snapshot `ir.config_parameter wsc.receipt.<so_id>` (amount/paid_at/brand/last4, written by carddoor at record time); falls back to `amount_total` if no snapshot. Link minter = `receipt_link(so_id)` (receipt.py).

**MINT-without-send vs SEND-only (the key distinction):**
- **Quote link WITHOUT sending:** `POST /owner/api/job/send_quote {so_id, method:'text', send:false}` → PREVIEW returns `{url, sms_body, amount, email, phone, customer, so_name, can_override}`. `send:false` sends NOTHING. The `amount_override` (DJ's rounded/audible price) is applied ONLY on `send:true` (via `_apply_quote_override` — rewrites just the windows line price_unit, keeps the [Render Quote Tool] breakdown note, refuses if a POSTED invoice exists). There is NO standalone "set quote price without sending" HTTP route — the adjustable amount is entered in the Send Quote preview UI (v2_job), which IS the review-first adjustable step.
- **Invoice link WITHOUT sending:** `POST /owner/api/job/send_invoice {so_id, plain:true, send:false}` → returns `invoice_view_url` (the plain itemized invoice doc; `plain` avoids creating a Stripe pay-link/draft).
- **RECEIPT link canNOT be obtained without sending:** the only receipt endpoint is `POST /owner/api/carddoor/receipt {so_id, channel:'text'|'email', email?}` which SENDS the branded receipt immediately (spec: "ONLY when DJ taps, always ask, never auto"). No preview/link-return. So you cannot drop a receipt link into a composed text from Operator endpoints — minting it requires the send.

**Pushing a CUSTOM review-first card onto the HUD:** `POST /owner/api/feed/submit` with `{item:{id, kind:'attention', source:'operator', title, why_now, urgency, action:{label, href}, created}}` → calls `feed.submit_item`. Remove with `POST /owner/api/feed/delete {id}`. HUD reads `GET /owner/api/feed/list`. This is how Operator can stage an arbitrary review-first card (e.g. a deep-link `href` to `/static/owner/v2_inbox.html?open=<partner>&draft=<urlenc text>` or `/static/owner/v2_job.html?open_so=<id>`). `/owner/api/confirm_card {so_id}` is the FIXED-copy confirmation variant (canonical confirm message + sched token, auto-clears on proven send) — use feed/submit for anything with custom text/links.

**Consequence for a "combined receipt + adjustable-quote in ONE text" card:** NOT wireable from existing endpoints — no endpoint bundles a receipt link + an adjustable quote into a single send, and the receipt link can't be minted without sending. That's a small Lead/Specialists build; do NOT hardcode a fixed quote link when DJ wants the amount adjustable at send ([[feedback_no_ai_offered_dates_use_link]] cousin: honor the review-first adjustable path). Interim: two review-first taps — Send Quote (adjustable) on the quote SO + Send Receipt on the paid SO. See [[project_record_payment_when_draft_invoice_exists]].
