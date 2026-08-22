---
name: project_goal_forecast_daywalk
description: "Goal milestone forecast ('On track/Behind · finish ~date') now walks the real work-hours calendar day-by-day instead of rounding each milestone to a whole week. 0.5h finishes the next free day, not weeks out."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T07:37:14.045Z
---

**2026-07-25 (DJ asked what the red 'Behind · finish ~Aug 15' line meant — it was misleading).**

**The forecast line** under each milestone (`fcLine` in v2_goals.html) shows: `<work_left>h of work left · On track|Behind · finish ~<proj>`. `work_left` = sum of that milestone's UNFINISHED task durations. `Behind` = projected finish is after the milestone's deadline.

**OLD (coarse, misleading):** `cum_weeks += ceil(work / wk_free)` then `proj = today + cum_weeks*7 days`. Every milestone with any work consumed **≥1 whole week** regardless of size, so 0.5h tasks projected finishes weeks out and tipped milestones into false 'Behind'.

**NEW (goals.py `goals_get`, commit 33cc5c6):** a **day-by-day walk** over the real work-hours calendar. Pre-buckets jobs + My Day to-dos per day over a 365-day horizon (2 queries). `_free_on(d) = max(0, _day_cap(d) − jobs(d) − todos(d))` — the day's goal-work capacity (goal tasks are NOT subtracted; they're the work being placed, so no double-count). A cumulative forward pointer `_pd=[day, remaining]` and `_consume(hours)` walk forward consuming each working day's free hours; a milestone's `proj` = the day its last hour lands. Milestones consume IN ORDER (cumulative). 0-capacity days (weekends/vacations via the work-hours model) contribute 0 and are skipped. `status='behind'` only when the walked finish truly lands past the deadline.

Verified on "Hire a Lead Technician": 3×0.5h milestones (deadlines Aug 5/10/14) now finish Jul 27–28 → all On track (was Review Applications = red Behind). `wk_free` (the hero's "~Xh free/week") is unchanged — still the 6-week average. See [[project_workhours_capacity_model]], [[project_goal_target_date_phaseA]].
