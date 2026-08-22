---
name: project_calendar_day_ondemand_load
description: "v2_calendar day-sheet: calData holds ONLY the currently-viewed month, so roaming the week strip/arrows to a day in another month showed 'No jobs scheduled' while Capacity (per-day server fetch) showed the real jobs. Fix: openDay loads that day's jobs+gcal on demand."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T18:30:07.756Z
---

**2026-07-25 (DJ: "when I change the days or the weeks... the schedule and jobs aren't updating correctly").** On the calendar day pop-up, the Capacity block showed e.g. "Jobs 3.5h" for Tue Jul 28 but the jobs list below said "No jobs scheduled" — a visible contradiction that appeared after roaming via the week strip / header arrows.

**Root cause.** `load()` fetches `/owner/api/calendar_jobs?year=&month=` and does `calData = d.days || {}` — it REPLACES calData with only the currently-viewed month's days (keys exist only for days that HAVE jobs). The day sheet's job list reads client-side `calData[dk]`. The Capacity block (`renderDayCapacity` → `/owner/api/goals/day_capacity?date_str=dk`) fetches per-day SERVER-side, so it's always correct. When the strip/arrows roam to a day in a DIFFERENT month than `curMonth`, `calData[dk]` is absent → "No jobs scheduled", while Capacity still shows the real hours → the mismatch. (Verified: session loaded on August had calData spanning only 08-04..08-26; `/calendar_jobs?start=2026-07-28&end=2026-07-28` returned Jul 28's 3 jobs — Diane 8:30 / Caroline 9:30 / Trish 11:00 = 3.5h — matching capacity.)

**Fix (commit bdc80cf).** The `calendar_jobs` endpoint also supports a range form `?start=DK&end=DK` (already used by `loadUpcoming`). Added:
- `_extraLoaded={}` state; reset to `{}` inside `load()` right after `calData=d.days||{}` (a month reload replaces calData, so forget prior on-demand loads).
- `_dayLoaded(dk)` = `dk` is in `curYear-curMonth` OR already in `_extraLoaded`.
- `async ensureDayLoaded(dk)`: if not loaded, `Promise.all` fetch `calendar_jobs?start=dk&end=dk` (merge `d.days` into `calData`) + `gcal_events?start=dk&end=dk` (merge `c.events` into `gcalData[c.name]`), then `_extraLoaded[dk]=true` (mark even if empty → no refetch).
- `openDay` is now `async`: after setting title, if `!_dayLoaded(dk)` it renders the week-strip shell + "Loading…" and opens the sheet immediately (strip stays tappable), `await ensureDayLoaded(dk)`, then a STALE GUARD `if(currentSheetDay!==dk) return` (rapid strip/arrow taps can't render the wrong day) before building the real body.

Same-month days hit `_dayLoaded` true → no network, renders instantly (no regression). **Verified live:** loaded August, called `openDay('2026-07-28')` → calData Jul 28 went absent → 3 jobs, sheet rendered 3 job rows (Diane/Caroline/Trish), no "No jobs scheduled". Minor cosmetic: week-strip dots for OTHER unloaded days in a roamed week may not show until tapped (each day loads on open) — acceptable. See [[project_capacity_overview_screen]], [[project_task_date_offby1_calendar_vs_myday]].
