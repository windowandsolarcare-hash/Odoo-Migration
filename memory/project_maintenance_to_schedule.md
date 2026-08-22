---
name: project_maintenance_to_schedule
description: "Maintenance to Schedule report (renamed from Submitted Jobs) = finds Phase-5 auto-created next-maintenance jobs sitting unfinished in Workiz; booking-style scheduler UI. Phase 5 now picks best DAY+slot around ~3mo via /api/scheduler/best-fit (availability+geo, not exact-cycle math)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**Renamed "Submitted Jobs" → "Maintenance to Schedule" (DJ 2026-06-16)** and gave it the booking-style scheduling UX.

## What the report locates (unchanged backend scan)
The **Phase 5A auto-created next-maintenance jobs sitting unfinished in Workiz**. `_submitted_jobs_refresh_worker` (dashboard.py): finds invoices with a `x_studio_workiz_job_link` (Phase 5 writes it), extracts the Workiz UUID, drops any already in Odoo, keeps only Status=Submitted + future, caches (param `submitted_jobs_cache`). Workiz API-created jobs don't fire the new-job webhook → Phase 3 never syncs them → this report is how you find them.

## What you CAN'T vs CAN automate (confirmed)
- **Line items: can't** via Workiz API — `job/create` doesn't accept them (that's why Phase 5 dumps them into a text reference field). Manual in Workiz.
- **Tech: technically possible** (`/job/assign/`, Phase 5 has `assign_job_team` but doesn't call it) — left manual.
- **Day + time: CAN** via Workiz API (`job/update` JobDateTime/JobEndDateTime). This is the part we automated.

## Phase 5's day/time logic = NOT smart
`calculate_next_service_date`: completed-job date + frequency, snapped to the customer's **city service weekday** (Palm Springs=Fri, Palm Desert=Thu, Hemet=Tue…), time **hardcoded 10:00 AM**, no slot/route awareness. It does NOT use the route-tightest engine.

## SHIPPED 2026-06-16 — booking-style scheduler in the report
New `static/owner/maintenance.html` + endpoints in `submitted_jobs.py`. Route `/owner/maintenance` (+ `/owner/submitted_jobs` back-compat alias). Tile renamed in index.html → "🔧 Maintenance to Schedule".
- List = cached jobs (Refresh re-scans). Tap → detail.
- `GET /api/maintenance/detail?uuid=&date=`: reuses **`scheduler.build_day_plan(lat,lon,date)`** (same engine as Booking Requests / New Job) → that day's schedule + free 1.5h slots + route-tightest suggestion. Coords: **prefer the customer's stored Odoo property coords** (`_prop_coords_by_addr`, match by street) — exact + reliable; **Photon geocode fallback** (server→Photon was flaky). Returns booking-shape `{request:{customer,address,lat,lon,job_type,date,current,line_items,items_link}, schedule, slots, suggested_minute}`.
- Detail UI (mirrors booking_requests.html): editable **date**, that day's schedule (lettered), **Leaflet route map** (new stop plum, OSRM driving route, redraws on slot/time change), **slot buttons** (green=SUGGESTED), editable **start/end** (15-min selects), + the **line-items reference** and a **"Open in Workiz"** items link (finish items/tech/confirmation there).
- `POST /api/maintenance/set_slot {uuid,date,start,end}`: Workiz `job/update` sets JobDateTime + JobEndDateTime (httpx, async). Verified read-side end-to-end (Sally Walsh 5XMTMY: coords resolved, 4 jobs that day, 3 slots, suggested 12:30). Did NOT trigger a live Workiz write.

## PHASE 5 NOW PICKS THE SMART SLOT TOO (2026-06-16)
`zapier_phase5_FLATTENED_FINAL.py` (GitHub Odoo-Migration; Zapier fetches on next run) upgraded: `schedule_next_maintenance_job` still computes the DAY (city-weekday + frequency), then calls **`get_best_slot_time(date, property_id)`** → HTTP GET `https://wsc-field-assistant.onrender.com/owner/api/scheduler/day-plan?date=&prop_id=` → uses `suggested_minute` (route-tightest free slot) as the TIME instead of the old hardcoded 10:00. Graceful fallback to the original time if the app is unreachable / no open slot. **Phase 5 reuses the Render scheduler over HTTP** (no logic duplication — a Zapier script CAN call the public Render endpoint). Verified the endpoint returns suggested_minute for a real property. So auto-created maintenance jobs now land in the smart slot at creation; the Maintenance-to-Schedule screen is for review/adjust. (Still: line items + tech + send-confirmation are manual in Workiz.)

## PHASE 5 NOW PICKS THE BEST DAY TOO — not just the slot (2026-06-17)
DJ: "the fact that its exactly 3 months is not as important as finding the correct day and time SOMETIME AROUND 3 months." Replaced the slot-only `get_best_slot_time` with **`get_best_fit(property_id, target_date)`** → HTTP GET `/owner/api/scheduler/best-fit?prop_id=&target=&window=21` → returns **both `date` and `time`**. `schedule_next_maintenance_job` now treats `calculate_next_service_date` output as just the **center of the search window** (not the final answer) and sets BOTH day+slot from the result. Graceful fallback to the city-weekday default if unreachable/no open day.
- **`scheduler.py best_fit_plan` → now a thin wrapper on the shared `rank_days` engine** (see [[project_shared_scheduler]] for the full engine). UPDATED 2026-06-17 to the **7-MILE RULE** (replaced the earlier `cost=geo+0.08*days` minimizer): walk candidate service-weekdays from the target OUTWARD; the FIRST day with nearest existing job ≤ 7 mi wins — do NOT push further to shave miles. Empty days (9999) never early-accept. Window scales with frequency (`window_for_freq`: 3mo→21d … 12mo→42d). Phase 5 passes the freq-scaled window.
- Endpoint `@router.get('/api/scheduler/best-fit')`. VERIFIED live 2026-06-17: Palm Springs prop 24097, target 2026-09-15 → picks **Sep-11 (5.4mi, 4d off target)** NOT Oct-2 (2.6mi, 17d off) — the 7-mile early-accept stops the over-optimization. Read-only, no Workiz write.
- Net effect: the cycle math (frequency·30d) only seeds the window center; the route+availability engine chooses the actual day, taking the first "good enough" (≤7mi) day near the cycle. The exact-cycle snap is gone as a hard constraint. SAME engine now powers reactivation's Book sheet suggestions.
