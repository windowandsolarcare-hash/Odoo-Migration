---
name: project_offer_link_resolver
description: "Slot-offer customer booking-link half (Lead's build, 2026-08-17): make_token carries offer_id; /book/api/offer/{get,book,decline} in booking.py. Token secret is server-side → Reserve mints the link via booking.make_token(pid,offer_id)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-17T08:38:52.065Z
---

**The customer-facing half of the slot-offers feature (booking.py, mounted at prefix `/book`).** Built 2026-08-17 (commit f00acf6). Pairs with the specialist's `slot_offers.py` store + Reserve button + WSCDayPlan overlay.

- **Token:** `booking.make_token(partner_id, offer_id=None)` — plain link `<pid>-<sig>` OR offer link `<pid>-<offer_id>-<sig>` (offer_id = uuid4().hex[:12], no dashes → unambiguous 3-part split). `parse_token(token)` unchanged (returns int pid, back-compat for all existing callers). New `parse_offer_token(token) -> (pid, offer_id)`.
- **Endpoints (public, on the `/book` router — NOT `/owner`):**
  - `GET /book/api/offer/get?token=` → {ok,status,name,slots,so_id,expires_at}.
  - `POST /book/api/offer/book {token, slot}` → slot must ∈ offer.slots (anti-tamper) + partner must match token; reschedules `offer.so_id` to that datetime via `scheduler.schedule_odoo_so(so_id, dt_pt, set_status=True)`, OR creates+confirms a fresh SO if `so_id` is null; then `slot_offers.clear_offer(offer_id,'booked')`.
  - `POST /book/api/offer/decline {token, requested_date?}` → `clear_offer('declined')` (frees the held slots — redline 1) + posts a needs-you feed card `offer_custom:<offer_id>` (kind=attention, urgency=today, action→v2_field open_so).
- **★ Token secret is server-side (`BOOKING_TOKEN_SECRET` env, NOT the "wsc-portal-2026" default) — you CANNOT forge a token to test.** Verified the endpoints correctly REJECT forged/default-secret tokens ("invalid link"). So the happy-path E2E needs a SERVER-minted token: **the specialist's Reserve flow builds the link owner-side** — `from routers.booking import make_token`; link = `https://wscare.pro/c/` + `make_token(partner_id, offer_id)`.
- **CUSTOMER PAGE DONE 2026-08-17 (commit 52a8918):** `booking_page_token` (`/book/c/<token>`) now serves a branded server-rendered `_OFFER_HTML` page for OFFER tokens (3-part, pending offer) — brand bar, "Hi <first>!", the 1–3 offered times as tap-buttons (formatted PT), + "None of these — I'll pick another day". Tap → `/book/api/offer/book`; decline → `/book/api/offer/decline`. Double-tap guard + error states. Plain partner links still get the SPA (unchanged). Verified end-to-end on a throwaway offer (reserve→link→render→screenshot; book path earlier confirmed the SO reschedules+confirms). Signature uses 760-334-5355. **LEAD'S §4 HALF IS COMPLETE.** Remaining for the whole feature = specialist's WSCDayPlan `offer` mode (Reserve button + `offered_in_window` overlay) in route_map.js + wiring v2_field/v2_command to load wsc_offerbox.js; then joint E2E. See [[project_slot_finder_gaps]], contract `3_Documentation/SLOT_OFFERS_CONTRACT.md`.
