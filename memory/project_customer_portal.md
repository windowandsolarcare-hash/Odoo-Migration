---
name: project_customer_portal
description: "Customer portal = wscare.pro/p/<token> (magic link, no password). Files routers/owner/portal.py + static/owner/portal.html, owned by the Portal session. Reuses the booking token, sched page, approved-photo gallery, tip_page."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-18T13:31:06.837Z
---

The **customer portal** (built 2026-08-18 by the Portal session, brief =
`3_Documentation/PORTAL_BUILD_BRIEF.md` in the app repo):

- **URL:** `https://wscare.pro/p/<token>` — no password. Token = **`booking.make_token(partner_id)`**,
  the SAME token as their `/c/<token>` booking link, so a customer has ONE permanent door.
- **Files (Portal session owns these):** `routers/owner/portal.py`, `static/owner/portal.html`.
- **Registered in `main.py` with NO prefix** — `/p` and `/portal` sit outside authz's
  `PROTECTED_PREFIXES ('/owner','/tech','/cheryl')`, so the customer half is public *by construction*
  with **zero authz.py changes**. The one DJ-side route declares its full path
  `/owner/api/portal/link?partner_id=|q=` and therefore stays behind login. (Same trick `calfeed` uses.)
- **API:** `GET /portal/api/me?token=` returns the entire page in one payload.

**Reuses, never rebuilds** (per [[feedback_reuse_canonical_endpoint]]):
`booking.make_token/parse_token` (identity) · `booking.make_sched_token` → `/book/sched/<t>`
(Confirm/Reschedule) · `/c/<token>` (Book/Rebook) · `dashboard.photo_gallery_url` (photos) ·
payments `tip_page` (Pay) · `scheduler.freq_months` (due math) · `_load_brand()` (logo/colors).

**★ PHOTO APPROVAL SIGNAL:** a job's "📸 Your photos" link appears ONLY when
`ir.config_parameter` key **`wsc.job.photos_sent.<so_id>`** exists with `count > 0` — i.e. DJ actually
curated and sent that job's keepers through the existing feature. No send = no link, ever. The chosen
subset lives in `wsc.job.gallery_sel.<so_id>`; the gallery + per-photo endpoints already honor it.
Nothing is auto-selected and nothing is labeled before/after (Claude can't tell them apart — DJ tested).

**Data judgment calls made (flagged to DJ):**
- `x_studio_x_studio_last_property_visit` runs **STALE** (Bullock: field said Apr 17 while the customer
  was serviced Aug 5). The portal computes last-visit from real Done jobs instead. Never show a
  customer a stored date you can compute.
- `x_studio_x_pricing` holds DJ's **internal shorthand** ("29 x 5.00 300/185") — NOT customer-safe.
  Portal shows "Your last price" = the amount of their most recent Done job.
- A future SO in `state='draft'` / Workiz "Submitted" is **not** an appointment. It renders as
  "Pencilled in — we'll confirm the day and time", never as a promised time. Only
  `state in ('sale','done')` is shown as a confirmed visit (matches the schedule gate).
- `x_studio_x_gate_code` is free text and often prose ("The gate code is:  0702") — normalized before display.

Referral = a share link only (`/book?ref=<code>`, a SEPARATE HMAC namespace so a forwarded referral
link can never be replayed as someone's `/p/<token>`). The rewards/tracking PROGRAM is a future add-on.

Related: [[project_res_partner_no_mobile_field]], [[feedback_never_send_dj_to_odoo]]
