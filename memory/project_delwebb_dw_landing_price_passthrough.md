---
name: project_delwebb_dw_landing_price_passthrough
description: "How the Del Webb / Rancho Mirage EDDM landing page (wscare.pro/dw) passes the customer's quoted dollar amount into Odoo — as a shown-estimate chatter note + review-queue, NOT a billable SO line. Plus the LIVE-hostname gotcha."
metadata:
  node_type: memory
  type: project
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-28T19:53:23.011Z
---

**Verified 2026-10-28 (Frontdoor), live, in answer to DJ "make sure rancho mirage landing booking
is passing the dollar amount."** It IS. Full chain:

- **Customer URL** = `wscare.pro/dw` (clean QR/EDDM URL; `main.py:1226` 307-redirects to
  `/static/dw/index.html`; route allow-listed `routers/authz.py:198`). Title "Del Webb Fall Cleaning",
  eyebrow "Del Webb at Rancho Mirage".
- **LIVE gating (`static/dw/index.html:320`):** `var LIVE = /wscare\.pro|onrender\.com/i.test(location.hostname)`
  and `var API=""` (same-origin). ⚠ GOTCHA: if this page is ever served from `windowandsolarcare.com`
  (the Odoo brand domain — which 404s `/book/*`), `LIVE`=false → the page runs in DEMO mode and
  **submits NOTHING** (line ~596 fake-succeeds). Ties to [[project_marketing_site_wscare_pro_inventory]]:
  the booking flow genuinely lives on wscare.pro; don't "rebrand" the /dw booking to the brand domain.
- **Price capture:** picking floor-plan (group) + level sets `st.price` (`:433` `st.price=g[L.priceKey]`;
  levels essential/premium/signature). Submit (`:589`) POSTs to `/book/api/request` with the $ inside
  `notes` ("Del Webb <plans> — <level> level ($<price>)…") and `quote_summary`
  ("Del Webb at Rancho Mirage — <plan> floor plan, <level> service = $<price> (fall window cleaning)"),
  `quote_src:"delwebb-eddm"`.
- **Server (`routers/booking.py` `/api/request`, :1350):** `quote_summary` is treated as UNTRUSTED —
  "what the customer was SHOWN, not a price to bill; DJ still prices" (:1368). It lands on the SO as:
  (1) the `[CUSTOMER PORTAL REQUEST] … Notes:` chatter line (:1489), (2) a dedicated chatter line
  `🧮 Online estimate the customer was shown (NOT a bill — you price the job): …` (:1528), and (3) the
  `booking.requests.pending` review queue (:1566, read by the Booking Requests page). It is **NOT** added
  as a `sale.order.line` / amount_total — so the SO total does NOT auto-equal the shown price. BY DESIGN.
- **Add-ons** are the exception: `/book/api/request/addons` (:1676) DOES create real priced SO lines
  (solar tiered via `_solar_price`, quote-only $0 price-TBD for pressure washing prod 108, catalog addons).

So "passing the dollar amount" = YES, as the shown-estimate note + queue. If DJ wants the quoted base
price as an actual SO line/total, that's a deliberate design CHANGE: client side (Frontdoor,
static/dw/index.html payload) + server line-write (Specialists, booking.py). Offered to DJ 2026-10-28.
Ownership: landing HTML = Frontdoor (public surface); booking.py = Specialists.
