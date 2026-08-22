---
name: project_sched_page_window_and_fit
description: "Customer confirm/reschedule page (_SCHED_HTML) — \"select my own day\" uses a Morning/Afternoon/No-preference WINDOW (never an exact clock time; DJ sets time by route); the day list shows 📍\"in your area\"/available via _open_dates_for_city fit. Requested-day HUD approve books it + marks confirmed."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T20:39:30.212Z
---

Three DJ-approved fixes to the branded confirm/reschedule page (`_SCHED_HTML` in booking.py), 2026-08-07 (Ed Dismukes SO 17555 hit them live):

1. **No exact-time picker.** `showPick()` ("I'll select my own") replaced the `<input type=time>` with **Morning / Afternoon / No preference** buttons (`.win`, default No preference; `pickWin()` toggles). Copy: "Dan sets the exact time by his route that day and confirms with you." `submitPick`→`/book/api/sched/request` sends **`window`** (am|pm|none), NOT a clock time. `sched_request` stores `requested_window` + a window label ("Tuesday, August 12 (morning)"); the stored `requested_time` is a window default (am→09:00 / pm→13:00 / none→09:00) for the mover. DJ never wants customers choosing exact times.

2. **Requested-day HUD card → opens DJ's day-planner (NOT a silent auto-book).** DJ 2026-08-07 refinement: "even if they pick morning I still need to tell them a time; the approve should go to my booking screen where I set the exact time by what's around them, then confirm." So `sched_req:<so_id>` is now a **kind='attention'** card whose action **📅 Set the time** → `/static/owner/v2_field.html?open_so=<so>&rs_date=<date>&rs_win=<win>`. v2_field boot reads `rs_date`/`rs_win` → `openJobRsModal(soid,name,preDate,preTime)` (new `_jobRsPre` overrides the SO's current date in `jobRsLoadSuggest`) → opens the reschedule day-planner (WSCDayPlan: jobs around them + route map + open slots) ON the requested day, time pre-set to the window default. DJ picks the exact time → `submitJobRs` → `/api/schedule/reschedule` books it + auto-opens the date-smart **confirm** send box → DJ texts the customer the EXACT time to confirm (closes DJ's "we said we'd confirm" loop). The reschedule also **clears the sched_req card** (scheduler.py `delete_item`). (The old one-tap `/api/sched/approve_request` still exists + auto-confirms, but the card no longer calls it.)

3. **Day list (option 2) shows the pin + available, matching the /book page.** `/book/api/sched/days` now uses **`_open_dates_for_city(city, lat, lon)`** (property's city/partner_latitude/longitude) — SAME route-tight sort + **`fit`** flag as the main booking page (was `open_days_for_partner`, which looked randomly ordered to customers). `showDays()` tags the route-tight day **📍 "I'll already be in your area"** and others **"available"**. Book time per day = am→09:00 / pm→13:00. "Same data, should look the same" (shared-screen consistency). See [[project_sched_lifecycle_one_page]].
