---
name: project_calendly_retired
description: Calendly retired 2026-07-19 — ALL outreach booking links now wscare.pro (tokenized /c/<token> or /book fallback). Never re-add calendly.com links.
metadata: 
  node_type: memory
  type: project
  originSessionId: 17f1db69-cc3e-47ab-9387-b6a4dee9ca9a
---

DJ retired Calendly 100% on 2026-07-19. No customer-facing text may contain a calendly.com link.

**Where booking links come from now:**
- Personalized: `https://wscare.pro/c/<token>` — token = `make_token(partner_id)` in `routers/booking.py` (HMAC, Python-only). Preloads name/address/history on the booking page.
- Generic fallback (no contact_id): `https://wscare.pro/book` (public booking page, /book router).

**What was patched (all live 2026-07-19):**
- Odoo SA 562 (Preview, 2 sites) + SA 563 (LAUNCH, 1 site): `cal_url` now `https://wscare.pro/book` — Odoo can't compute HMAC, so Render upgrades it (see next). SA 564 backup + SA 1340 (inbound Calendly capture webhook) left untouched.
- `routers/owner/reactivation.py`: link-swap regex now replaces BOTH `calendly.com/...` AND plain `wscare.pro/book` with the tokenized link; no-contact fallback → wscare.pro/book.
- `routers/owner/hemet.py` AND `routers/owner/dashboard.py` (~line 8628): Hemet `_hemet_build_sms` → tokenized link. ★ dashboard.py SHADOWS hemet.py for /api/hemet/* (dashboard registers first) — patching hemet.py alone did nothing; the live behavior came from dashboard.py's copy. Any future /api/hemet change must hit dashboard.py.
- Odoo-Migration repo mirrors updated: 1_Active_Odoo_Scripts/{odoo_reactivation_launch,odoo_reactivation_preview,ODOO_REACTIVATION_COMPLETE_NO_IMPORTS}.py + 1_Production_Code/{ODOO_REACTIVATION_COMPLETE_NO_IMPORTS,ODOO_REACTIVATION_PREVIEW}.py.
- v2_home.html: Calendly tile → "Booking page" tile (wscare.pro/book).

**Left in place (passive, drains naturally):** booking_requests calendly inbox (`booking.calendly.incoming` ir.config_parameter fed by Zapier), SA 1340 capture, display code on booking_requests pages, live index.html shortcut tiles.

**Why:** DJ: "calendly.com is out 100%" (2026-07-19).
**How to apply:** never emit calendly.com in any SMS/flow; use `_booking_link(partner_id)` (reactivation.py) or `make_token` directly. The CLAUDE.md "PAIRED CHANGES" Calendly-slug rule is obsolete. Verified end-to-end: SA562→preview swap→`wscare.pro/c/26474-...`→/book/api/me ok. See [[project_render_app_redesign]].
