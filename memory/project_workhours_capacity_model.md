---
name: project_workhours_capacity_model
description: "Work-hours capacity model: per-day available hours (weekly default Mon-Fri 6h/wknd 0 + date overrides) replaces the flat 8h/40h across ALL goal/capacity math. Standalone v2_workhours.html page + config-param storage. No custom model."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T06:27:08.225Z
---

**2026-07-24 — DJ: capacity assumed 40h weeks; he doesn't work 40, takes days off, goes on vacation.** Built a work-hours model so every capacity number measures against his REAL availability. He chose default **Mon–Fri 6h, weekends 0** (30h/wk) and location = standalone page + reachable from Goals.

**Storage (ir.config_parameter, no new model):**
- `wsc.capacity.weekly` = JSON 7-array **[Mon,Tue,Wed,Thu,Fri,Sat,Sun]** hours. Index = Python `date.weekday()` (Mon=0).
- `wsc.capacity.overrides` = JSON `{'YYYY-MM-DD': hours}` for days off / vacations / half days.
- Both unset by default → code falls back to `_CAP_DEFAULT_WEEKLY = [6,6,6,6,6,0,0]`, so the system works day-one with no setup.

**goals.py helpers (replace the old `WEEK_CAP_HRS=40`/`DAY_CAP_HRS=8` constants, now legacy-fallback only):**
- `_cap_weekly()`, `_cap_overrides()` — read the config params.
- `_day_cap(d, weekly=None, overrides=None)` — hours for ONE date: exact-date override wins, else weekday default. **In loops, load `_wk,_ov=_cap_weekly(),_cap_overrides()` ONCE and pass in** (avoids N config reads).
- `_week_cap(week_start, wk, ov)` — sum of `_day_cap` over 7 days.
- Wired into: `day_capacity` (cap per day), `next_slots` (free = day_cap − load), `overloaded_days` (threshold = day_cap; each returned day carries its own `cap`), `capacity` (free_hrs = week_cap − booked; returns `week_cap`; free_days = weekdays with >0h not fully booked), and the goal `forecast` (weekly free = week_cap − booked − myday).
- Endpoints: `GET /api/goals/capacity_settings` → {weekly, overrides, default}; `POST` accepts `weekly` (7-array) and/or `overrides` (date→hours), clamped 0–24.

**Frontend:**
- NEW `static/owner/v2_workhours.html` — "⏱ Work Hours" page: 7 day rows (hours input + Day-off toggle) with live week total, auto-saves on change (400ms debounce); "Time off & exceptions" list with an Add sheet (single date OR start/end range → hours, default 0). Added to launcher (v2_apps.js).
- `v2_goals.html` capacity cards now say "free of your Xh week" and link "⏱ Set your work hours ›".
- `v2_myday.html` overloaded-day warning uses each day's `day.cap` (per-day, not a flat 8).

**Note:** "reachable from Goals" = a link to the standalone page (NOT a duplicated inline editor — one source of truth, per Rule #9). See [[project_goal_target_date_phaseA]], [[project_goal_layer3_bump]], [[project_personal_time_capacity]].
