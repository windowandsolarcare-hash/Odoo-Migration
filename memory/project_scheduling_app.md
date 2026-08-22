---
name: Scheduling App — Design Decisions
description: Architecture and UX decisions for the Render scheduling feature (find_next_opening tool + monthly calendar)
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**Goal:** When a customer calls to schedule, DJ asks Render Claude to find the best opening. If he doesn't like the suggestion, he falls back to a visual monthly calendar.

**Flow:**
1. Primary: Render Claude `find_next_opening` tool — returns top 3 date+time suggestions with one-line reasoning ("You're already in Cathedral City that morning")
2. Fallback: Monthly calendar page on Render — color-coded by area/zone, tap day to see jobs

**Scheduling rules:**
- Lookahead window: **2 weeks** (not 4)
- Use customer's `partner_latitude`/`partner_longitude` (geocoded into Odoo) to find days with nearby existing jobs
- Proximity = jobs within X miles of the new customer's address
- Rank options by fewest driving miles added

**Data source:** `sale.order` (not tasks) — `date_order` = job start time (UTC), `x_studio_x_studio_workiz_tech` = tech, address on `partner_shipping_id`

**Geocoding:** Bulk geocode ran 2026-05-06 via Nominatim → `partner_latitude`/`partner_longitude` on `res.partner`. 827 unique addresses. New customers need geocoding added to Phase 3 flow.

**GPS Phase 2 connection:** Once GPS clustering (Phase 2) is built, proximity switches from straight-line distance to actual drive-time clusters. Current geo-proximity approach is ~80% of the value without it.

**Why:** customer calls → DJ wants instant AI recommendation, not manual calendar browsing. Calendar is the backup UI.
