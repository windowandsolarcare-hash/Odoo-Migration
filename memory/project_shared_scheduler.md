---
name: project_shared_scheduler
description: "Shared scheduling brain — scheduler.py (day-plan: slots + route-tightest GPS) + route_map.js (Leaflet/OSRM). Used by booking_requests, reactivation Book sheet, New Job. Read before touching any booking/scheduling slot or route-map code."
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

**Shipped 2026-06-15.** Unified the scheduling logic across all 3 booking funnels (online `/book` review, reactivation Book Job, New Job intake) so they share ONE slot+route engine and ONE map. saunders-render-app.

## BACKEND BRAIN = `routers/owner/scheduler.py` (prefix /owner)
- `build_day_plan(new_lat, new_lon, date_str)` → `{schedule:[{minute,time,so_name,customer,address,job_type,lat,lon}], slots:[{minute,label,half,suggested}], suggested_minute}`. **Route-tightest** = the free 1.5h slot whose closest-in-time existing job is geographically nearest the new stop (haversine).
- Endpoint `GET /owner/api/scheduler/day-plan?date=YYYY-MM-DD&lat=&lon=` (or `&prop_id=` to resolve coords from a property). Returns `{ok, schedule, slots, suggested_minute}`.
- Slot grid itself still lives in `routers/booking.py` (`_free_slots`/`_slot_label`/`AM_CUTOFF_MIN`, 8–17h, 90-min slots); scheduler imports it. `_haversine` + `prop_geo` live in scheduler.py.
- Imports `from .shared import *` (routers/owner/shared.py → odoo_rpc + `_PT` zoneinfo) — consistent with new_job.py. (booking_requests.py uses different imports: `from shared.odoo import odoo_rpc` + pytz — both fine.)
- **scheduler.py is imported at boot in main.py → a bad import takes the WHOLE app down. py_compile + verify app health after any change.**

## FRONTEND MAP = `static/owner/route_map.js`  →  `window.WSCRouteMap.render({...})`
Reusable Leaflet + OSRM (`router.project-osrm.org`, public, no key) route map. Faithful generalization of the original booking_requests map. Call:
```
WSCRouteMap.render({ mapId, wrapId, hdrId, metaId,
  newStop:{lat,lon,name}, schedule:[...day-plan schedule...], selMinute:<int|null> })
```
New stop = plum ★, existing jobs = green A,B,C in time order, driving route + mi/min via OSRM. Keyed per `mapId` so multiple maps coexist. **Requires Leaflet `<link>`+`<script>` on the page AND a `.hide{display:none}` CSS rule** (WSCRouteMap toggles `.hide` on wrap/hdr). Redraw on date/time change; it returns early (hides) when newStop has no coords.

## THE 3 CONSUMERS
- **booking_requests** (online): detail endpoint now DELEGATES to `build_day_plan` (one backend brain). Its HTML still has its own inline map copy (works; not yet migrated to route_map.js — minor dup, low priority).
- **reactivation Book Job sheet** (reactivation.py/html): `/api/reactivation/suggest` now also returns `prop_id/prop_lat/prop_lon`. Full PHASE-2 PARITY (2026-06-16): best-DAY chips stay on top (the day picker); picking a day (chip or date field) → `loadDay()` calls day-plan and renders **that day's schedule** (time·customer·address, `bk-day-sched`) + **free 1.5h slot chips** (`bk-day-slots`, green=route-tightest, tap→`pickTimeSlot`→fills time+redraws map) + the route map (`bk-map`). `bk-time` oninput → `redrawMapTime()` only (doesn't reload day). Commit still = in-place graveyard update + CRM→Won.
- **New Job step 3** (new_job.py/html): `/api/intake/properties` + `/recent-jobs` now return `partner_latitude/partner_longitude`. Step 3 shows a route map (`nj-map`) that redraws on date/start-time change with the selected property as the new stop.

## TIME FIELDS = 15-MIN DROPDOWNS, NOT native `type="time"` (2026-06-16)
Android's native `<input type=time>` clock dialog clips its "Set" button off-screen on DJ's phone (worse under accessibility Magnification) — and it's an OS dialog we can't restyle. So ALL booking time fields are `<select>` populated by **`WSCTime.fill(selectEl, fromMin=360, toMin=1140, step=15)`** in route_map.js (6:00 AM–7:00 PM, option value=`HH:MM` 24h so downstream reads/writes are unchanged). Applied to new_job (job-start/job-end, filled in loadStep3), reactivation (bk-time, filled in showBookSheet), booking_requests (startT/endT, filled in init — also had to add `route_map.js` to that page for WSCTime). **Don't reintroduce `type="time"` here.** Fill happens where route_map.js is guaranteed loaded (user-triggered handlers / loadStep3), not page-load init for new_job (route_map.js loads after the inline script there).

## UNIFIED DAY-PICKER LAYER = `scheduler.rank_days` (2026-06-17)
The DAY-suggestion layer (not just the per-day plan) is now shared too. `scheduler.py`:
- **`rank_days(prop_id, target_str, window_days=21, top_n=1)`** → ranks the property city's open service-weekday options around a target date by route tightness + availability. Returns `{ok, city, best:{date,time,minute,near_mi,job_count}, options:[...top_n...], considered:[...]}`. Past/lapsed target auto-clamps to today-forward; full days dropped.
- **THE 7-MILE RULE (DJ 2026-06-17):** walk candidates from the target date OUTWARD; the FIRST day whose nearest existing job is ≤ **`NEAR_ENOUGH_MI=7.0`** wins — do NOT push further out just to shave miles. Only days over 7 mi keep looking deeper. Empty days (no nearby job = special trip) get sentinel 9999, never early-accept, only win as last resort. This replaced an earlier `cost = geo + 0.08*days_off` minimizer that over-optimized miles (it'd jump 17 days to save ~3 mi). Verified: Palm Springs prop 24097 target Sep-15 → picks Sep-11 (5.4mi, 4d off) NOT Oct-2 (2.6mi, 17d off).
- **`window_for_freq(freq)`** = `min(42, max(21, months*4+9))` → 3mo:21, 6mo:33, 9mo:42, 12mo:42. Longer cycle = exact date matters less = look wider.
- **`CITY_WEEKDAYS`** (Mon=0) is now the SINGLE source of truth for city→service-weekday. `best_fit_plan` (Phase 5) is a thin wrapper on `rank_days(top_n=1)`.

**Online booking `/book` now offers ROUTE-AWARE dates too (2026-06-17, DJ: "offer dates that are best for OUR schedule").** Was the last geography-blind funnel — `_open_dates_for_city` just returned the next 4 open city-weekdays chronologically (and had a 3rd copy of the city map). Now: `/book/api/availability?city=&lat=&lon=` ranks open days **"soonest that's good for us"** — among the soonest open days, route-tight ones (≤`NEAR_ENOUGH_MI`) first; only reaches past the soonest 4 if NONE are nearby. Sources `CITY_WEEKDAYS`/`NEAR_ENOUGH_MI`/`_haversine` from scheduler via **lazy import inside the function** (scheduler imports booking.py at boot → a top-level import would be circular; local `CITY_SCHEDULE` kept as fallback). New `booking._jobs_by_day_geo` = one range query + batched coords (NOT build_day_plan-per-day — too many round-trips for a customer page; booking keeps its own day+AM/PM model, not the single-slot model). Frontend passes coords from the address autocomplete pick (re-calls loadDates to refine) + known-customer `/api/me` property coords; days flagged `fit` show a "📍 We're in your area" badge. Verified live: Hemet + coords → all Tuesdays fit, near 0.1–0.4mi; no coords → graceful city-level fallback.

**Three consumers now share this engine:**
- **Phase 5** (zapier, Odoo-Migration): `get_best_fit(prop_id, target, window)` → `GET /api/scheduler/best-fit` → `best_fit_plan`. Target = last Done job + frequency·30d; window = freq-scaled. Auto-picks the single best day+slot.
- **Reactivation `/api/reactivation/suggest`** (reactivation.py): imports `rank_days, window_for_freq, freq_months` DIRECTLY (same app, no HTTP). Target = last Done job + frequency (clamped to today-forward since lapsed), `top_n=3`. Returns `options:[{date,date_label,time(12h),job_count,min_dist}]` + `prop_lat/lon` + `last_job_type` + `note` — the shape the Book sheet expects. (Dropped old `day_labels`/`partner_name` keys — html only used `d.note`/options, confirmed safe.) Was previously `field._find_scheduling_openings`.

**STILL NOT route-aware / forked (2 left):** (1) `field.py _find_scheduling_openings` = Render Claude's phone `find_next_opening` tool — different "fit them in soon" use, today+14d gap-finder, own duplicate city map; left alone to avoid changing the live phone assistant. (2) **New Job's date chips** use `/api/intake/suggest-dates` (dashboard.py, its OWN CITY_SCHEDULE map) — soonest city-weekdays, NOT proximity-ranked. New Job's step-3 MAP is route-aware (build_day_plan) but the date CHIPS aren't. These are the last two non-route-aware date pickers. Future: point both at `rank_days`/the shared geo ordering.

## NOTE
booking_requests's single-DAY model vs reactivation's multi-DAY suggestion model are different shapes — the shared brain is the per-DAY `build_day_plan`; reactivation layers it under its own multi-day chips (now fed by `rank_days`). New Job uses its own older `/api/intake/suggest-dates` for the date chips + day-plan for the map. See [[project_new_job_intake]], [[project_customer_portal_booking]], [[project_reactivation_sent_book]], [[project_maintenance_to_schedule]].
