---
name: project_calendar_search
description: "Schedule Calendar has a job search box (find a job by customer name, address, or SO#) → tap a result opens the job detail. Backend GET /api/calendar/search in calendar.py. Built 2026-06-17."
metadata:
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ: "need search function on schedule calendar."** Built 2026-06-17.

## What it is
A search box under the calendar header (`static/owner/calendar.html`, `#calSearch` / `.cal-sr` results). Type ≥2 chars (debounced 300ms) → matching scheduled jobs list (customer · date · time · city · SO#); tap a result → `goToField(so_id, date)` opens the existing job detail (hist) modal. Closes on outside tap / on pick. Light-theme aware.

## Backend — `GET /owner/api/calendar/search?q=` in calendar.py
A NEW UNIQUE route (NOT shadowed — dashboard.py has no copy, unlike `/api/calendar_jobs` which IS shadowed). Returns `{ok, results:[{so_id, so_name, customer, date, time, city, job_type}]}`. Domain: `state in [sale,done]`, workiz_status != Canceled, `date_order >= today-45d` (recent+future planning horizon), AND a name/SO OR-group, ordered by date_order, limit 40. Customer name derived like calendar_jobs (shipping partner's parent name).

## Also on the FIELD SCHEDULE listing (added 2026-06-18)
DJ wanted the same quick search on the main field-schedule job listing (`/owner/field`), not just the calendar. Added a search box (`#schedSearch` / `.sched-sr` results) in the STATIC markup ABOVE `#schedule-section` (so it survives the 5-min `loadField` re-render that rebuilds schedule-section's innerHTML). Reuses the SAME `GET /owner/api/calendar/search?q=` endpoint. `onSchedSearch`/`doSchedSearch`/`pickSchedSearch` in field.html (debounced 300ms, ≥2 chars, outside-tap closes). Tap a result → **`openJobById(so_id, date)`** (field.html's existing opener that handles today live-panel / future / past hist-modal by so_id). No backend change — one endpoint now serves both screens.

## ⚠ KEY GOTCHA — SOs link to the PROPERTY child, not the named customer
A first cut searched `res.partner` by name → `sale.order` where partner_id/shipping in those ids → **0 results for real customers**. Reason: an SO's `partner_id`/`partner_shipping_id` point to the **property record** whose `name` is the STREET (e.g. "43042 Balsam Ln"), and its `parent_id` is the named customer ("Lisa Scarpelli"). So a name match on the customer never matches the SO's partner. **FIX: after matching partners by name/street, also pull in their CHILDREN** (`res.partner` where `parent_id in matched`) and include those in the id set the SO search uses. See [[project_property_displayname_has_name]]. Verified: "Scarpelli" → Lisa Scarpelli 6/18 8:30am 004497; SO# "004497" also works.
