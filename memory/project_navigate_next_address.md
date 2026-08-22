---
name: project_navigate_next_address
description: "Field job screen '🧭 Navigate to Next Address' button — routes to the next stop on the same day's schedule without leaving the current job. Day-aware."
metadata: 
  node_type: memory
  type: project
  originSessionId: b8f82f75-713b-49ec-b4d3-aeb0cffeef8f
---

# 🧭 Navigate to Next Address (field.html job screen, 2026-07-01)

★★ FIX 2026-07-07 (the REAL "back on the last job in my pocket" bug) — the field app auto-refreshes every 5 min (`setInterval(loadField, 5*60*1000)`), and `_applyFieldData` (~L1923) re-ran `openJobById(?open_so)` on EVERY refresh because the deep-link `open_so` param was never cleared from the URL. So after arriving via a deep link (Command Center/nudge/`?open_so=`) and stepping forward with Next Job, each 5-min refresh silently YANKED the view back to the original deep-link job (DJ found himself shooting roof photos on the wrong job). FIX: consume `?open_so` ONCE (`window._openSoDone` guard) then `history.replaceState` to strip `open_so`+`date_raw` from the URL, so refreshes leave him where he navigated. Note: the SAME-job re-open on refresh (`jobs.find(activeJob.so_id) → openJob`) is correct and kept — it's only the stale URL param that was the bug. RULE: any one-shot URL deep-link param that triggers navigation MUST be stripped after first use, or the 5-min auto-refresh replays it.

★ FIX 2026-07-07 — the separate "**Next Job ›**" button (`openNextJob`, opens the next job's DETAIL; NOT the maps 🧭 Navigate) intermittently jumped BACKWARD to an earlier/finished job. Cause: it built the combined schedule (pastDaysData + jobs + futureDays) and walked it by ARRAY INDEX, trusting source order and NOT skipping Done. A refresh re-order or an out-of-position Done job → i+1 = wrong job. FIX: sort the combined list CHRONOLOGICALLY by `date_raw`+`time_utc`, dedupe by so_id, skip Done/Personal Time → always the next real stop. Canonical job time = `date_raw` (date) + `time_utc`. ★ RULE: never trust field-app source-array order for next/prev — sort by date_raw+time_utc.


DJ's need: stay on the current job finishing notes, but fire off navigation to his NEXT stop without backing out to the schedule. Added a button in the job detail screen right after the Charge-at-Door card.

## What it does
- `openNavNext()` → `_nextJobAfter(activeJob)` → `window.open(navUrlForJob(nextJob))`.
- `_nextJobAfter(cur)` finds the next time-ordered job **on the SAME DAY as the job you're viewing** (not just today) that isn't Done / Personal Time and has an address. Uses `_dayJobsFor(cur.date_raw)`: today → `jobs[]`; a future/past day → the cached `futureDays`/`pastDaysData` bucket (each `{date, jobs}`). So opening a Friday job navigates to the next Friday stop.
- Reuses `navUrlForJob()` (which is now address-first — see [[project_navigate_gps_first]]).

## Gotchas fixed (why "it did nothing" at first)
- **so_id type mismatch:** a CC-opened job's `so_id` can be a string while `jobs[].so_id` is a number → strict `===` missed it. Fixed with `String(a)===String(b)`.
- **Toast hidden behind the cc-mode panel:** the job panel is z-index 300 in cc-mode but `#toast` was z-index 200 → the "no next job" message was invisible ("did nothing"). Bumped `#toast` to **z-index 9999**. (Any field.html toast/feedback must clear the cc panel.)
- DJ wanted the "no next job" message **INLINE below the button** (not a toast) — `#nav-next-status` div under the button shows amber "No next job on {Weekday}'s schedule after this one" (weekday computed from the viewed job's date), or red "next job has no address". Auto-hides after 7s.
- **Look:** wrapped in `<div class="ap-card ap-card--nav">` with a plain `nav-btn` to exactly match the "Navigate to Address" card (DJ: make it look the same).

## Testing note
DJ had no jobs "today," so testing on Friday's jobs correctly returned "no next job" until it was made day-aware. Now it walks whichever day you're viewing.
