---
name: GPS Shift Review — Phase 2 shipped 2026-05-07. Cluster/match/$/hr/range view all live.
description: GPS stop clustering, customer matching, $/hr analysis, date range view. Phase 1 collects pings. Phase 2 (this) clusters into stops, matches to Property partners, shows $/hr per stop and shift, drive time analysis, Day/Range toggle. Endpoints all in dashboard.py under /owner prefix.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when extending the GPS logger, building the cluster/match algorithm, or wiring auto-fill (Phase 3).**

## Phase 2 shipped 2026-05-07 — Shift Review UI + Analysis

## Why this exists

DJ + Danny don't want to start/stop a timer per task — they just want to clock in once at start of day and have per-task hours filled in automatically based on where the phone was. Bonus: when DJ misses a timer toggle, the GPS data corrects the timesheet retroactively.

## Phase 1 (this build) — Data collection

Storage model: **x_gps_ping** (Odoo Studio, model_id=1024)

| Field | Type | Notes |
|---|---|---|
| `x_employee_id` | m2o → hr.employee | Required. ondelete=cascade. |
| `x_timestamp_utc` | Datetime | Required. UTC. |
| `x_lat` | Float | Required. |
| `x_lng` | Float | Required. |
| `x_accuracy_m` | Float | Optional — meters. From browser's GeolocationPositionError.accuracy. |
| `x_shift_id` | Char | Synthesized "{emp_id}:{check_in_utc_iso}" — same format as `_shift_id()` in dashboard.py for the Manage Shifts UI. Empty string if employee not currently clocked in. |
| `x_active_so_id` | m2o → sale.order | Optional — what the employee thinks they're working on, if any. |
| `x_active_task_id` | m2o → project.task | Optional — same. |

ACL: Administrator group has full read/write/create/unlink. Internal User group has read+create. Render's API user (UID=2) writes via JSON-RPC.

## Endpoint

`POST /owner/api/payroll/gps_ping`
- Body: `{employee_id, lat, lng, accuracy?, active_so_id?, active_task_id?}`
- Server tags the ping with the current shift_id by reading `payroll.clockin.{emp_id}` from ir.config_parameter
- Returns `{ok: true, ping_id, shift_id}`

## Frontend behavior (timeclock.html)

- `startGpsTracking()` is called from `updateClockUI()` whenever `clockedIn=true`. `stopGpsTracking()` is called when `clockedIn=false`.
- Uses `navigator.geolocation.watchPosition({enableHighAccuracy: false, maximumAge: 30000, timeout: 60000})`.
- Throttle: a position is converted into a ping only if **both** of these are true:
  - 5 minutes have passed since last ping, OR
  - the phone has moved more than 100m since last ping
  
  (Implemented as: skip if elapsed<5min AND moved<100m. So either condition can fire a ping.)
- Status indicator (`#gps-status`) below the CLOCK OUT button shows last ping time + accuracy. Hidden when not tracking.
- On geolocation error → red status with the error message. No retry — just informative.

## Two-person scenario (DJ + Danny on one truck)

Each phone runs its own GPS watcher with its own employee_id. Pings are stored per-employee. Phase 3 auto-fill will create separate timesheet entries per employee on the same matched task → correct for payroll (Danny gets paid hourly, both per-person hours visible) and project costing (2 person-hours visible on a 1-hour job).

## Limitations to remember (and address in Phase 4)

1. **Foreground only.** Web `watchPosition` only fires when the page is visible/focused. If Danny closes the tab or his phone screen sleeps, no pings during that gap. Phase 4 may add a TWA/Bubblewrap wrapper or PWA Wake Lock to mitigate.
2. **No backfill if forgot to clock in.** GPS only logs while the JS knows employee is clocked in. If DJ forgets to clock in, no pings → no auto-fill that day.
3. **Indoor accuracy** drifts to ±30m. Cluster algorithm in Phase 2 will tolerate this.
4. **Quarter-hour rounding** applied at Phase 3 (matches existing payroll FLSA rule).

## Phase roadmap

- **Phase 1** ✅ shipped 2026-04-30: x_gps_ping model + /api/payroll/gps_ping + watchPosition in timeclock.html
- **Phase 2** ✅ shipped 2026-05-07: shift_review.html — cluster/match/$/hr/drive time/range view (see below)
- **Phase 3** (task #40): auto-write account.analytic.line per stop, manual review UI, drive-time allocation
- **Phase 4** (task #41): mileage logs, native Android wrapper for background GPS

## Phase 2 Detail — Shift Review (2026-05-07)

### Clustering algorithm (in /api/payroll/stops)
- RADIUS_M=80, MIN_STOP_MIN=8, MERGE_GAP_MIN=30, MATCH_RADIUS_M=150
- Consecutive pings within 80m = same cluster. Cluster >= 8min dwell = stop.
- Merge consecutive stops at same partner if gap <= 30min.

### Partner matching
- Query ONLY res.partner where x_studio_x_studio_record_category = Property AND partner_latitude != 0
- Fetch parent_id field; display name = parent_id[1] (customer name, NOT property street name)
- Auto-match if nearest property within 150m. Ambiguous if second within 30m of best.
- Manual match saved to ir.config_parameter key: gps.match.{emp_id}.{date}.{stop_num}

### $/hr analysis
- Per-stop: SO amount_total / (duration_min/60). SO lookup by partner_shipping_id + date.
- Shift $/hr: total revenue / (total_shift_min/60) — denominator includes drive time.
- Drive stats: total_drive_min, drive_pct, avg per leg, total shift time.

### Date range view (/api/payroll/shift_range)
- Max 31 days. Returns per-day rows + totals.
- Per day: stop_count, matched, ping_count, on_site_min, drive_min, shift_min, drive_pct, revenue, dollar_per_hr

### Geocoder (/api/payroll/geocode_properties + /api/payroll/geocode_status)
- Nominatim batch geocoder for un-geocoded Property records. 1.1s throttle.
- _GEOCODE_IN_PROGRESS global flag. Result in ir.config_parameter key gps.geocode.last_result
- Ran 2026-05-07: 166 properties geocoded. Some addresses unknown to Nominatim (e.g. East Sonora Rd PS).
- Fix for bad geocodes: write actual GPS coords from a confirmed stop directly to res.partner.

### Known coordinate fix: Moody Nashawaty
- 221 East Sonora Road, Palm Springs: Nominatim returns wrong coords
- Correct: lat=33.8047028, lng=-116.5445317 (written 2026-05-07 to IDs 26940 + 26941)

### Employee IDs
- DJ (Dan Saunders): hr.employee ID=1
- Danny Saunders: hr.employee ID=2

## Files involved

- `static/owner/gps_tracker.js` — **shared module** (added 2026-04-30 commit 3e46318b). Exposes `window.WSC_GPS.start(employeeId)`, `.stop()`, `.isActive()`. Throttle constants + haversine + watchPosition all in here. Both timeclock.html and field.html load it via `<script src="/static/owner/gps_tracker.js">`.
- `routers/owner/dashboard.py`:
  - `/api/payroll/gps_ping` endpoint (POST) — stores ping in x_gps_ping
  - `/api/whoami` (GET) — resolves access_code → {type, name, employeeId} for field.html
- `static/owner/timeclock.html` — calls `WSC_GPS.start()` from `updateClockUI()` when clockedIn=true; `WSC_GPS.stop()` when false. Status indicator div: `#gps-status` near the CLOCK OUT button.
- `static/owner/field.html` — `initGpsWatcherFromAccessCode()` runs from `boot()`. Resolves employee_id via `/api/whoami`, then polls `/api/payroll/status` every 60s + on `visibilitychange` to start/stop the watcher based on the same source-of-truth clock state. Status indicator is a fixed top-right badge so it doesn't conflict with the page layout.
- Odoo Studio model: `x_gps_ping` (id 1024), 8 fields all stored

## Multiple-tab behavior

If both timeclock.html and field.html are open in different tabs while clocked in, BOTH will fire pings. The Phase 2 cluster algorithm absorbs duplicates within tolerance, so this is harmless (just extra DB rows). No coordination is implemented because the cost is low.

## Validation / smoke test (already done)

Created + deleted a test ping via the Studio model creation script. Endpoint not yet hit from a real browser — that happens when DJ or Danny next clocks in.

## Browser permission flow

First clock-in after deploy will prompt: "wsc-field-assistant.onrender.com wants to use your location." DJ/Danny tap Allow. Permission persists across sessions until manually revoked or browser data wiped.
