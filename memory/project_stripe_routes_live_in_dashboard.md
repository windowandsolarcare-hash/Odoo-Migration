---
name: project_stripe_routes_live_in_dashboard
description: "★ The LIVE Stripe pay routes (/api/stripe/payment_link, /tip_page, /create_checkout) are served by dashboard.py, NOT payments.py — payments.py has identical DEAD twins that are route-shadowed. Edit dashboard.py for any Stripe pay-flow change."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-26T22:12:27.692Z
---

**The Stripe customer-payment routes exist in BOTH `routers/owner/dashboard.py` AND `routers/owner/payments.py`, and dashboard.py's copies WIN** (route shadowing). Confirmed 2026-08-26.

Affected endpoints (all three defined in both files):
- `POST /api/stripe/payment_link`
- `GET  /api/stripe/tip_page`
- `POST /api/stripe/create_checkout`

**Why dashboard wins:** in `main.py`, `owner_dashboard.router` is `include_router`'d at line ~241 (FIRST under prefix `/owner`); `owner_payments.router` at line ~249 (later). FastAPI serves the first-registered match, so **payments.py's Stripe pay routes are dead twins.** (Same shadowing class as dashboard.py over hemet.py and field.py — see [[project_voice_ask_lives_in_dashboard]] and the route-shadowing rule in CLAUDE.md.)

**How to apply:**
- For ANY change to the Stripe pay flow (tip page, checkout session, payment link), **edit the copies in `dashboard.py`.** Verify by content on the LIVE endpoint after deploy — editing payments.py alone does NOTHING (burned during the 2026-08-26 door-charge Link-kill: the fix was first put in payments.py, live curl still showed the old page; re-applied to dashboard.py, then `?door=1` → `DOOR=1` confirmed live).
- dashboard.py structure differs slightly: `payment_link` delegates to a helper `_create_stripe_tip_link(so_id, amount, shorten=, door=)`; payments.py inlines it. Thread new params through the helper.
- Before editing any `/owner/api/stripe/*` route, grep BOTH files + check `main.py` include order first.

Note: other Stripe endpoints (`/api/stripe/webhook`, `_stripe_record_and_close`, `/success`) may live only in payments.py — verify per-endpoint which file actually serves it; don't assume all Stripe routes are in one place. See the incident memory [[project_card_at_door_wrongcard_incident]] and [[project_stripe_webhook]].
