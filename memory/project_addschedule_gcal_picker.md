---
name: project_addschedule_gcal_picker
description: "Field app \"Add to schedule\" modal now has a \"Pick from Google Calendar\" picker that prefills the block from a chosen GCal event"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**★ TWO separate "Add to schedule" sheets exist — both now have the picker:**
1. `field.html` job-detail modal — `block-modal` / `openBlockModal` / `submitBlock` (button `#gcal-pick-btn`, `toggleGcalPicker`). Commit 8d0da91.
2. `schedule_hub.html` (the newer Command Center schedule — this is the one DJ usually taps from the schedule view) — `ab-modal` / `openAddBlock` / `submitAddBlock` (button `#ab-gcal-btn`, `abToggleGcal`). Commit f9301c8. Its time dropdown is 6 AM–6 PM (`_abFillTimes` 360–1080) vs field's 6 AM–8 PM; clamp accordingly. schedule_hub has NO `esc()` helper — added local `_abEsc`.

Both got a **"📇 Pick from Google Calendar"** button (add mode only). Built 2026-07-10, frontend-only. ★ When DJ says he can't see an "Add to schedule" change, check BOTH sheets — they're independent copies.

Flow: `toggleGcalPicker()` → `loadGcalPicker()` GETs `/owner/api/gcal_events?start=<block-date>&end=+30d`, flattens all calendars into a date-sorted tappable list; `pickGcal(i)` prefills What=summary, Day=event date, Notes=location, and snaps the event time to the nearest 15-min slot clamped to the 6:00 AM–8:00 PM `_fillBlockTimes` dropdown. DJ then reviews + taps "Add to schedule" (existing `/api/schedule/add_block`).

**Why:** DJ wanted to select an existing Google Calendar item instead of retyping it when blocking time on his work schedule. The Schedule Calendar page (`calendar.html`) already did this per-event (`gcalToSchedule` on each gcal chip); this brings the same to the field app's add-block modal.

**How to apply:**
- Google Calendar is **read-only** in the app via iCal feeds (`GCAL_1_URL` etc. on Render, up to 3). The app can LIST events, not WRITE them. Pushing app jobs OUT to Google Calendar would need Google Calendar API + OAuth write scope (a `GOOGLE_OAUTH_REFRESH_TOKEN` exists on Render for Drive — see [[project_drive_upload_no_local_auth]] — could be extended, not done).
- Endpoint `GET /owner/api/gcal_events?start=&end=` (shift_review.py) returns `{ok, calendars:[{name,color,events:{"YYYY-MM-DD":[{summary,time,all_day,location,link}]}}]}`. `time` is like "1:30 PM" or "" for all-day. Handles RRULE recurrence expansion server-side.
- Picker box uses `var(--bg-card)` (OPAQUE) not `--card-bg` (translucent) — see [[reference_field_css_bg_vars]]. field.html escape helper is `esc()` (defined near end, hoisted).
