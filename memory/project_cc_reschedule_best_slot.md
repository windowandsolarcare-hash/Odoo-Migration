---
name: project_cc_reschedule_best_slot
description: "CC reschedule sheet suggests the route-tightest best day/slot + draws the day route, REUSING the shared scheduler engine (not a rebuild). Built 2026-06-29."
metadata: 
  node_type: memory
  type: project
  originSessionId: b8f82f75-713b-49ec-b4d3-aeb0cffeef8f
---

The Command Center **Reschedule** sheet (schedule_hub.html `openReschedule`) now SUGGESTS the soonest route-tightest day+time and draws that day's route/slots — DJ can override. Built 2026-06-29 by REUSING the proven shared scheduler, NOT rebuilding (DJ: "we've done this successfully and unsuccessfully — know which is which").

## ★ Right vs wrong (the distinction DJ wanted nailed down)
- **RIGHT (reused):** `scheduler.rank_days` + the **7-mile early-accept rule** (`NEAR_ENOUGH_MI=7.0`) for the best DAY; `build_day_plan` for the day's slots/route; and the shared **`route_map.js`** components (`WSCDayPlan` + `WSCRouteMap` + `WSCTime`). Reference integrations = the duplicate-job sheet + reactivation Book Job sheet. See [[project_shared_scheduler]].
- **WRONG (do NOT reintroduce):** the old `cost = geo + 0.08*days_off` distance-minimizer (over-optimized miles — jumped 17 days to save 3mi; replaced by the 7-mile rule). And native `<input type=time>` (Android clips the "Set" button — use `WSCTime`/15-min `<select>`).

## How it's wired
- **Backend (NEW):** `GET /owner/api/scheduler/so-suggest?so_id=&window=` in `scheduler.py` → reads SO `partner_shipping_id` = the property → `prop_geo(prop_id)` coords + `rank_days(prop_id, target=today_pt(), window=21, top_n=3)`. Returns `{ok, prop_id, lat, lon, city, best, options:[{date,time,minute,near_mi,job_count}]}`. Anchored on TODAY so it offers the next good openings (rank_days clamps to tomorrow-forward). Reschedule sheet is the only caller.
- **Frontend (schedule_hub.html):** added Leaflet CDN + `/static/owner/route_map.js` + `.hide{display:none}` + var aliases `:root{--text-dim:var(--dim);--border-input:var(--line);--bg-page:var(--card2)}` (route_map.js was authored for field.html's tokens). rs-modal got best-day chips `#rs-bestdays` + WSCDayPlan containers (`rs-schedHdr/sched/slotsHdr/slots/mapHdr/mapWrap/map/mapMeta`) + made scrollable (max-height:92dvh). Flow: `openReschedule`→`rsLoadSuggest(soId)`→renders best-day chips + `rsPick(best)`→`rsRenderDay()` = `WSCDayPlan.render({date,lat,lon,name,timeInputId:'rs-time',ids})`. Date `onchange`→rsRenderDay; chip click→rsPick; slot tap (handled inside WSCDayPlan)→sets rs-time + redraws map. `closeReschedule`→`WSCDayPlan.clear()`.
- **GRACEFUL:** if so-suggest fails/no options, chips clear and the manual day/time picker + the (Workiz-correct) reschedule POST still work — non-regressive. The reschedule POST itself is unchanged ([[project_cc_reschedule_via_workiz]]).

## Both reschedule entry points are smart (2026-06-29)
DJ caught that the smart suggest+map was ONLY on the CC card 🔁 (`schedule_hub.openReschedule`), NOT on the **Field Assistant 3-dot menu Reschedule** (the job panel, `field.html rescheduleJobFromMenu`→`openJobRsModal`) which was the older plain date/time modal. Fixed: `openJobRsModal` now calls the SAME `/api/scheduler/so-suggest` + renders best-day chips + `WSCDayPlan` (field.html already loads route_map.js/Leaflet/.hide + the dup sheet uses WSCDayPlan, so no setup). New fns: `jobRsLoadSuggest`/`jobRsPick`/`jobRsRenderDay` (job-rs-* container ids). So now BOTH the CC card 🔁 AND the Field 3-dot Reschedule suggest the route-tight day. The ONLY other "reschedule" = Personal Time block "📅 Move / Reschedule" (`moveBlockFromMenu`→`openBlockModal`, Odoo date_order only) — intentionally NOT route-aware (it's a personal block, no Workiz/property). RULE: any future reschedule entry point for a real job should call `/api/scheduler/so-suggest` + WSCDayPlan, not a bare date/time picker.

## Test / watch
- The "rescheduled but stayed in the same spot" DJ saw = the bare modal defaulted to TOMORROW (≈ the job's current day) so it looked unchanged; also the list reflects the new date only after Phase 4 sync (~5 min, Workiz→Odoo). The smart picker suggesting a far-future day fixes the first; the ~5min lag is inherent (reschedule writes Workiz, not date_order). If DJ wants instant, add an optimistic date_order write or a one-job sync after the Workiz update.
- Leaflet in a bottom-sheet that was display:none can need invalidateSize — WSCRouteMap handles it in the dup/reactivation sheets, but verify the map actually draws here on DJ's phone.
- Slot minutes are 90-min boundaries (8:00/9:30/11:00…) = multiples of 15, so they select cleanly in the `_abFillTimes` 15-min `<select>`.
