---
name: project_pinned_tasks_carry_today
description: "A DATED-overdue pinned My Day to-do rolls to TODAY on both My Day AND Capacity load (myday.py _rollforward_pinned + goals.py _roll_pinned_today). UNDATED pinned = deliberate keep-track, left alone. Future-dated + goal tasks also left alone."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T17:17:13.005Z
---

**2026-07-26 (DJ):** a task pinned to the top of My Day = "do it today," so it should ALWAYS carry today's date, not a stale one. A pinned task sitting at the top with last week's date makes no sense and throws off the capacity math (it lands on an old day instead of today). DJ's call: don't set-the-date-once-on-pin (falls behind) — keep rolling it to today.

**Impl (myday.py `_rollforward_pinned(tasks, today)`, called in `api_myday` right after `_rollforward_recurring`, commit 3da9a22):** for each task that is `x_myday_pinned` AND `project_id=False` (a plain My Day to-do, NOT a goal task) AND not recurring: if its stored date part is overdue (< today), write `date_deadline = today + ' 12:00:00'` (noon → raw `[:10]` reads as today, matching the plain-date read convention [[project_task_date_offby1_calendar_vs_myday]]). **Left alone:** future-dated (today or later) pinned, goal tasks (keep their goal/milestone date), recurring habits (own rollforward), and — corrected 2026-07-25 — **UNDATED pinned to-dos**. Mutates in place + persists, so all downstream (My Day list, goals capacity, calendar) see it on today.

**2026-07-25 (DJ) — two corrections:**
1. **UNDATED pinned tasks are left alone.** DJ: "some tasks I'm gonna lay out there with no date that I just want to keep track of and it's not urgent… those should be left alone." An earlier version rolled *undated* pinned to-dos onto today too; that was wrong. Fix: `if not cur: continue` before the overdue check, plus `if cur >= tdy: continue`. Only DATED-overdue pinned to-dos roll. A pinned no-date item is a deliberate keep-track marker, not a "do it today."
2. **Capacity is ALSO a trigger.** DJ is considering making Capacity his go-to screen instead of My Day, so the roll must fire there too, not only on My Day load. Added self-contained `_roll_pinned_today()` in **goals.py** (queries `project.task` project_id=False + x_myday_pinned + open state + `date_deadline < today`, skips recurring, writes `today + ' 12:00:00'`), called at the top of `goals_capacity`. Now whichever screen DJ opens first on a new day, the roll happens.

Runs on every My Day load AND every Capacity load. Verified live 2026-07-25: hitting `/api/goals/capacity` rolled all 13 overdue pinned (Jul 13–24) to today (on-today 1→14); 3 future (7/27–7/28) kept; undated left alone. See [[project_capacity_overview_screen]], [[project_myday_recur_rollforward]].
