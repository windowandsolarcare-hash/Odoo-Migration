---
name: project_duplicate_job_button
description: Duplicate button on the field history modal — clone a job into a new Workiz job with suggested date picker
metadata: 
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Shipped 2026-06-09.** On the **history modal** (field.html `openHistModal` — opens when you tap a PAST job in a customer's job list, Customers tab), the **📋 Job History** button was replaced with **📄 Duplicate**.

## Flow
Tap Duplicate → bottom sheet with: **suggested slots** + **job-type picker** (defaulted to the source job's type) + **date/time pickers**. Confirm → creates a NEW Workiz job copying all fields from the source, with the new date. **No SubStatus** — DJ adds line items + sets Scheduled in Workiz himself (Workiz job link opens automatically).

## Reuse — overlaps with reactivation Sent/Book
- Suggested slots call **the same** `/owner/api/reactivation/suggest?partner_id=` endpoint. **As of 2026-06-17 that endpoint uses the new `scheduler.rank_days` engine** (route-aware, 7-mile rule, frequency-anchored, returns `prop_lat`/`prop_lon`) — so the dup date suggestions are already the precise logic, NOT the old find_next_opening.
- Same date-picker / slot-chip UX pattern.

## ROUTE MAP added to the dup sheet (2026-06-18, commit b7ed2b54)
DJ: dup dates were fine but wanted the **map** (precise route view) like New Job step 3 / reactivation Book. Added to the dup sheet in field.html: Leaflet CSS+JS + `route_map.js` now loaded in field.html (weren't before; also added a `.hide{display:none!important}` rule since `WSCRouteMap` toggles `.hide`). New `#dup-map`/`#dup-map-wrap`/`#dup-map-hdr` + `dupRedrawMap()` → fetches `/api/scheduler/day-plan?date=&lat=&lon=` (coords captured from `/suggest`'s `prop_lat/prop_lon` in `dupLoadSlots`) → `WSCRouteMap.render(...)`. Redraws on slot pick + date/time onchange. **Both duplicate entry points (history-modal `histDuplicate` AND Customers-tab `dupCustJob`) share this one dup sheet, so this covered "change it everywhere."** New Order "Use This" already had the map (New Job step 3). field.py voice `duplicate_workiz_job` = no UI.
- **2026-06-18 (commit ee7bf6a) — day schedule list + open slots:** changing the date now also shows **that day's schedule** (`dup-day-sched`, who's booked) + **open 1.5h slots** (`dup-day-slots`, tap to set time → `dupPickDaySlot`) above the map, so DJ can place the time around existing jobs. All from the same day-plan fetch (`dupRedrawMap` renders sched+slots+map; `dupRenderDaySched`/`dupRenderDaySlots`/`dupMarkSlot`). Schedule list shows even if no map coords. Full parity with Book/New-Job day view.
- **2026-06-18 (route_map.js 92b95d57 + field.html cca14b2f) — EXTRACTED day-view into shared `WSCDayPlan` component:** the dup-sheet day-view (schedule list + open 1.5h slots + route map, synced to a time input) is now a reusable IIFE in **`static/owner/route_map.js`**: `WSCDayPlan.render({date,lat,lon,name,timeInputId,ids:{schedHdr,sched,slotsHdr,slots,mapHdr,mapWrap,map,mapMeta}})` fetches `/api/scheduler/day-plan`, renders schedule + `.wdp-tslot` open-slot buttons (click sets the time input + redraws map) + `WSCRouteMap`; `WSCDayPlan.clear()` resets its CFG/DAY/DATE cache + hides. field.html now calls it via thin wrappers `dupCfg()` (builds the ids/coords config) + `dupRedrawMap()` (`if(window.WSCDayPlan)WSCDayPlan.render(dupCfg())`); the old dup-specific render fns (dupRenderDaySched/dupRenderDaySlots/dupPickDaySlot/dupMarkSlot/_dupM2hm24) were REMOVED. `dupLoadSlots` reset calls `WSCDayPlan.clear()`. Coords held in `_dupPropLat/_dupPropLon/_dupPropName`. route_map.js guards with `if(window.WSCDayPlan)` so screens load it safely. **DEFERRED (DJ said "later"): migrate reactivation Book sheet + New Job step 3 to WSCDayPlan — they still use their own day-view code for now.**
- **2026-06-18 — clipboard split (field.html cca14b2f, first shipped 5e3112b0):** after Duplicate, line items are copied to the clipboard as TWO sequential clips PER item — **price first, then name/description** — so DJ's paste#1 = description and paste#2 = price (matches the reactivation/Phase5 hand-off). `dupCopyItems(itemsText)` parses each `Name [x2] - $Price` line, strips the `x{qty}`, writes price then name with ~80ms gaps. Replaced the single `navigator.clipboard.writeText` in `doDuplicate`. Toast reports item count.

## Duplicate from a My Day task → auto-closes the task (2026-06-18)
DJ's flow: a My Day task ("give customer next date in Oct") → tap **🧑 Open customer card →** in the task editor → 📄 Duplicate → go to Workiz to text the customer. The task used to stay open. Now it auto-closes on a successful duplicate.
- **myday.html `tkOpenCustomer()`** appends `&myday_id=<task id>&myday_source=<source>` to the `/owner/field?tab=customers&cust_q=&cust_pid=` deep-link.
- **field.html boot** (next to the `block_name` handler) stashes `{id, source, pid:<cust_pid>, ts:Date.now()}` to **localStorage `wsc_dup_myday`** (rule 12 — survives the field-page refresh + the Workiz tab switch). Only when `myday_id` present AND no `block_name`.
- **field.html `_closeDupMyday()`** (called in `doDuplicate` success, after `dupCopyItems`): POSTs `/owner/api/myday/done` `{id, source}` — SAME endpoint as the "Add to schedule" flow, so a **recurring** task spawns its next occurrence. Then removes the flag. Toast appends ` · My Day task done`.
- **Two guards against closing the WRONG task:** (1) **2h staleness** — ignore+clear a hand-off older than 2h. (2) **customer-match** — `if (p.pid && parseInt(p.pid)!==parseInt(_dupPartnerId)) return false` WITHOUT clearing, so a stale flag from customer A won't close task #1 when you duplicate customer B reached some other way; the correct duplicate still closes it. This works because `preloadCustomer(name,cust_pid)` sets `_custAutoOpenPid=cust_pid` and `dupCustJob`/history-dup set `_dupPartnerId` to that same card pid. (3) network fail on the done call → keep flag, retry on next duplicate. Opening a NEW customer card from another My Day task overwrites the flag (most-recent wins).
- Only auto-closes when reached via that task's **Open customer card** button — intentional, so it never closes a task you didn't navigate from.

## Backend — `/api/duplicate_job` (POST) in dashboard.py
Body `{so_id, job_type, date, time}`. Reads the SO's `x_studio_x_studio_workiz_uuid`, fetches the source Workiz job, copies ALL fields (ClientId, name, phone, address, gate_code, pricing, JobNotes, type_of_service_2, frequency, etc.), overrides JobType with the picked value, sets JobDateTime = Pacific `'YYYY-MM-DD HH:MM:SS'`, NO SubStatus. Mirrors field.py's `duplicate_workiz_job` Claude tool logic (self-contained copy, did NOT modify the tool).

## Fields copied to the new Workiz job (verified field names)
ClientId, FirstName, LastName, Phone, Country, JobType (override), type_of_service_2, frequency, confirmation_method, ok_to_text, JobSource, JobDateTime, State, Address, City, PostalCode, **Unit**, **ServiceArea** ("Desert"/"Hemet"), **gate_code**, pricing, JobNotes.
- **2026-06-10 fix:** ServiceArea + Unit were originally omitted; added. Workiz GET returns `ServiceArea` (capitalized) and `gate_code` (lowercase). gate_code now falls back: `gate_code` → `GateCode` → SO `x_studio_x_gate_snapshot` (older jobs have blank Workiz gate_code but a populated Odoo snapshot).

## ALSO on the Customers-tab job rows (added 2026-06-18, commit 6d9144f4)
Every job row in the Customers-tab list (`toggleCustJobs` render, the `.cust-job-pills` line) now has a **📄 Duplicate** pill → **`dupCustJob(pid, idx)`** which reads `_custJobsCache[pid][idx]`, sets `_dupSoId`/`_dupPartnerId`, and opens the **SAME dup sheet** (`dup-modal` + `dupLoadSlots` + `doDuplicate` → `/api/duplicate_job`). So duplicate is reachable directly from a customer's job history without opening the per-job history modal. DJ chose this over linking out to New Order ("Use This →") — fewer taps, faithful clone, consistent with the existing Duplicate. Decision 2026-06-18.

## Limitations (told to DJ)
- **Workiz create API can't set structured line items** — pricing/notes TEXT copies, but service line items do NOT. DJ adds line items in Workiz after (same hand-off as reactivation Book).
- History modal + Customers-tab rows. Live job panel keeps its own Job History button. `histJobHistory()` function left intact (dead code, not deleted).

## Frontend specifics (field.html)
- `_histJobType` captured in `openHistModal` from `d.so.job_type` (defaults the picker).
- `histDuplicate()` snapshots `_dupSoId`/`_dupPartnerId` BEFORE `closeHistModal()` (close resets _hist* state).
- `showToast(type, msg)` signature here (type = 'ok'/'err'), NOT the reactivation.html `showToast(msg)`.
- Not smoke-tested (mutating) — DJ runs first real one. See [[feedback_no_mutating_smoketest_payroll]].
