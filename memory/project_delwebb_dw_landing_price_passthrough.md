---
name: project_delwebb_dw_landing_price_passthrough
description: "How the Del Webb / Rancho Mirage EDDM landing page (wscare.pro/dw) passes the customer's quoted dollar amount into Odoo — as a shown-estimate chatter note + review-queue; AS OF 2026-10-28 (LIVE) it ALSO lands as a real verify-flagged SO line (carrier product 120) and the off-host silent-fail is rescued via POST /book/api/demo-alert. Plus the LIVE-hostname gotcha."
metadata:
  node_type: memory
  type: project
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-28T20:40:39.983Z
---

**★ UPDATE 2026-10-28 (LIVE, main aaad5476) — the design CHANGE flagged at the bottom of this note SHIPPED** (Specialists + Frontdoor, dual-GREEN Lead+Audit). Two things below are now SUPERSEDED: (1) the /dw online estimate NOW lands as a REAL `sale.order.line` — carrier product **120** (Single Story Window Panes), qty 1, `price_unit` = client `est_price` (new JSON field), name "(online estimate — verify)", guarded against double-pricing (skips if any window-service line exists → a known-customer SEED's real prices win). The 🧮 chatter note is KEPT alongside it. Still a verify-flagged STARTING point; request lands Submitted, DJ re-prices (NOT an auto-charge). (2) the off-host silent-fail is FIXED: a real customer on a non-LIVE host no longer fake-succeeds — the page beacons `POST /book/api/demo-alert` (rescue ping: no SO, rate-limited 12/hr, pushes DJ to call them back) + shows a call/text fallback; intentional previews (file://localhost or `?demo=1`, client KNOWN_PREVIEW) stay silent. Product IDs + full detail → [[project_window_cleaning_service_products_and_dw_estimate_line]]. The chain below is the PRIOR (pre-2026-10-28) behavior, kept for history.

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

So "passing the dollar amount" originally = the shown-estimate note + queue only. **That design CHANGE
(quoted base price as a real SO line) SHIPPED 2026-10-28 (LIVE, main aaad5476, §16-closed)** — see the
UPDATE block at top + [[project_window_cleaning_service_products_and_dw_estimate_line]].
Ownership: landing HTML = Frontdoor (public surface); booking.py = Specialists.
