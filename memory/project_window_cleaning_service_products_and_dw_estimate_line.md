---
name: project_window_cleaning_service_products_and_dw_estimate_line
description: W&SC window-cleaning SERVICE product.product IDs (verified via Odoo 2026-10-28) — there is NO single "whole-home window clean" product; real jobs are built from per-pane/per-service lines. How booking.py carries a flat online estimate (Del Webb /dw) as a priced SO line + the demo-alert off-host rescue pattern
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-28T20:26:47.838Z
---

**Verified via Odoo `product.product` search 2026-10-28 (Specialists).** W&SC has NO single "Window Cleaning — whole home" product. A real window job is assembled from multiple per-pane / per-service lines. The window-SERVICE product IDs (all `type=service`, sale_ok, active):

- 82 Commercial Window Cleaning ($50) · 86 First Story Window Panes - Inside & Outside ($5) · 87 French Door or Window ($1.75) · 89 Garage Door Windows Cleaned - Cut Outs ($20) · 90 Garage Door Windows Cleaned - No Cut Outs ($10) · 103 Outside Windows And Screens ($65) · 105 Outside Windows Only ($100) · 116 Second Story Window Panes - Inside & Outside ($6) · 120 Single Story Window Panes - Inside & Outside ($5) · 153 French Door or Window (dup of 87, $1.75).
- Add-on products (separate, already mapped in `routers/booking.py` `_ADDON_PRODUCTS`): 99 Mirrors, 76 Ceiling Fans, 119 Shower Glass, 122 Skylights, 94 Hard-Water, 90 Garage Door Windows, 81 Cobweb, 125 Solar ($5/panel, $100 min — `SOLAR_PRODUCT_ID`), 108 Pressure Wash (`PRESSURE_WASH_PRODUCT_ID`, $0 price-TBD quote-only).
- The `{82,86,87,89,90,103,105,116,120,153}` set = "is this SO already window-priced?" dedup check.

**Del Webb /dw estimator (`static/dw/index.html`)** shows a FLAT lump sum by floor-plan group × level (Essential/Premium/Signature; $175–$415), JOB_TYPE always "Windows Inside & Outside Plus Screens". Since there's no whole-home product, booking.py's `/api/request` carries that lump as ONE SO line on **carrier product 120** (Single Story — Del Webb homes are single-story), qty 1, `price_unit` set EXPLICITLY to the client's `est_price` (so the product's $5 list_price is irrelevant), name flagged "(online estimate — verify)". This EXACTLY mirrors the existing solar-sizing block in the same handler (product 125, explicit price_unit). Guard: skip if any window-service line already exists → a known-customer SEED (job_seed.py, their real prior prices) wins over an online estimate. The line is a verify-flagged STARTING POINT; the request lands Submitted and DJ re-prices on the booking-review page (NOT an auto-charge).

**Off-host silent-fail rescue (`POST /book/api/demo-alert`, added 2026-10-28):** the /dw page host-gates its live API (`LIVE = /wscare\.pro|onrender\.com/`). If ever served off another host (e.g. windowandsolarcare.com, which 404s /book/*), a real customer's submit would fake-succeed and lose the lead. Fix = the page `navigator.sendBeacon`s an ABSOLUTE `https://wscare.pro/book/api/demo-alert` with the lead's info (string body → text/plain = a CORS-simple request, no preflight) and shows a call/text fallback. The endpoint parses `await request.body()` (NOT `.json()` — content-type is text/plain), creates NO SO, rate-limits (12 pushes/hr) + keeps a 50-row `ir.config_parameter` audit (`booking.demo_alerts`), and pushes DJ via `myday._broadcast`. Intentional previews (file://localhost/?demo=1) stay silent (client KNOWN_PREVIEW flag) — no beacon. **Why NOT CORS on `/api/request`:** that endpoint CREATES SOs+contacts; opening it cross-origin = a junk-record/spam vector. A rescue-ping endpoint that creates nothing is the lower-risk architecture for "nothing should silently fail."

`routers/booking.router` is mounted `prefix="/book"` (main.py:1076) — handlers are defined `/api/...`, served `/book/api/...`. See [[project_new_job_via_app_endpoints]], [[feedback_odoo_verify_content_not_status]].
