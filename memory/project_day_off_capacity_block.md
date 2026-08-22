---
name: project_day_off_capacity_block
description: "Day off / vacation now blocks CUSTOMER scheduling availability, not just DJ's goal planning. Single source of truth = wsc.capacity.overrides[date]=0 (Work Hours day-off). New shared.is_day_off(date); gated into scheduler.build_day_plan + booking._open_dates_for_city. 3 duplicate availability paths still to guard."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T23:47:28.770Z
---

**Problem (DJ 2026-08-05):** a customer (William) was offered Aug 7 while DJ is in Mexico. DJ marks days off in Work Hours (`v2_workhours.html`), but that only fed his OWN goal/capacity planning — the customer-availability code never checked it. Also DJ's nuance: a day off = no JOBS, but he still wants to add his own "Add to schedule" reminders (those are personal My Day tasks, NOT capacity-gated, so unaffected — no checkbox needed).

**Design chosen (reuse, don't invent):** the EXISTING capacity override IS the single source of truth. A date set to **0** in `ir.config_parameter` **`wsc.capacity.overrides`** (JSON `{'YYYY-MM-DD': hours}`) = day off. Per-DATE only — NOT the weekly default (`wsc.capacity.weekly` [6,6,6,6,6,0,0]) — so a 0-hour weekend default doesn't blanket-block a city serviced then.

**Helper:** `shared.is_day_off(date_or_str)` (routers/owner/shared.py) — reads that param, True if the exact-date override ≤ 0. 30s in-process cache. **★ shared.py has an `__all__` — a new helper is NOT picked up by `from .shared import *` unless added to `__all__`. Forgot this → live `NameError: is_day_off is not defined` in build_day_plan on first deploy; fixed by adding it to `__all__`.**

**Availability architecture (from Explore map 2026-08-05):** TWO shared chokepoints + THREE rogue duplicates.
- **DONE (lead, verified live):** `scheduler.build_day_plan()` → on a day off returns `{slots:[], suggested_minute:None, day_off:True}` (keeps `schedule` so the day VIEW still shows any jobs); rank_days treats empty slots as "full/skip" so ALL its consumers inherit it (reactivation, calfeed, new_job.open_days_for_partner, specialist_booking, booking_requests, scheduler endpoints). AND `booking._open_dates_for_city()` (/c customer page + dialer openings) skips day-off dates (fetches overrides once, `continue`). Verified: /api/scheduler/day-plan Aug6=day_off/0 slots, Aug10=6 slots.
- **STILL TO GUARD (mailed specialist to split):** `field.py._find_scheduling_openings`, `dashboard.py._find_scheduling_openings` (both the AI find_next_opening tool, own inline CITY_SCHEDULE + gap-pack), `new_job.api_intake_suggest_dates` (own inline copy). All `import *` so is_day_off is available. Lead takes field+dashboard; specialist takes new_job (their active file). Long-term: consolidate these 3 onto scheduler.

**Immediate:** Aug 6 + 7 2026 set to 0 in overrides for DJ's trip (via ir.config_parameter set_param). Going forward DJ marks days off in **Work Hours** and they now flow to customer offers. See [[project_status_label_vs_so_state]] (schedule gate), idx_scheduling.
