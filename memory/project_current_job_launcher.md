# "📍 The job I'm on" — launcher item
**Type:** project
**Created:** 2026-09-02 (Lead, cloud) — DJ asked for one launcher tap that opens the job he's at.

## Where it lives
- `routers/owner/current_job.py` (app repo) — `GET /owner/api/current_job` (JSON) and
  `GET /owner/current-job` (the launcher target page). READ-ONLY: never starts/stops/writes a timer.
- One registry line in `static/owner/v2_apps.js`: `{ico:'📍', t:"The job I'm on", h:'/owner/current-job', fav:true}`.
  It is a **plain href**, so the launcher needed no special-casing at all — favorites, search and
  badges all key off `h` already. Default-favorite, so it auto-stars on DJ's phone once.

## The decision order (DJ picked timer-first, clock-as-backup)
1. **Running timer = the job, full stop.** Checked twice:
   - `localStorage.wsc_timer` on the phone — set by `field.html` `doStartTimer()`, shape
     `{so_id, start_ms, employee_id}` (+ `stop_ms/stop_iso/duration_min` once stopped, then removed
     on a successful `/api/timer/log`). **Running = present && !stop_ms.** Checked CLIENT-side, so
     the common case costs zero network.
   - Server: `ir.config_parameter` **`timer.debug.log`** — a rolling last-100 list of start/stop
     events written by `/owner/api/timer/event` + `_append_timer_debug`. Replay it; a `start` with
     no matching `stop` is an open timer. Covers a timer started on another device.
   - Both ignore anything older than **14h** (`TIMER_STALE_H`) so a forgotten timer can't hijack today.
2. **`x_studio_x_studio_workiz_status == 'In Progress'`** beats the clock — a person said so.
   (Nothing writes this automatically; it's selectable and free to honour.)
3. **The clock.** Today's jobs (company 1, state sale/done, not Canceled), soonest first, Done ones
   dropped: take the LAST whose start has passed with a **45-min grace** (so tapping it on the drive
   over still lands right), else the first one still ahead. Completing a job flips it to Done, so
   this walks itself forward through the day with no extra state.

**Personal Time is skipped** — it is a block on the calendar, not a job you can stand at.

## When nothing resolves
It does NOT guess. The page prints which signal came up empty (`"every job today is done"`,
`"nothing on the schedule today"`) and lists today's jobs to tap. Every successful answer carries a
`why` (`"timer still running"` / `"scheduled for 8:30 AM"` / `"up next at 9:30 AM"`) so DJ can always
see which signal spoke — and can tell when it guessed from the clock rather than knew from a timer.

## Reusable facts
- Canonical "open this job" URL is **`/static/owner/v2_field.html?open_so=<so_id>`** (v2_field reads
  `open_so`, plus optional `date_raw`, `rs_date`, `rs_win`). `WSCThread.goJob()` uses the same.
- The job timer has **no server-side "is it running" record** other than `timer.debug.log` — the
  live state is on the device. Don't look for a `sale.order` field; there isn't one.
- Owner page-serving routes should return through `shared.html_nostore(...)`, not a bare HTMLResponse.
