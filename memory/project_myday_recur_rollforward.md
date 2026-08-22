---
name: project_myday_recur_rollforward
description: "Recurring My Day habits only advance on mark-done; skipping days froze them on a stale past date. Added auto-roll-forward in api_myday so overdue habits bump to today."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Model:** a recurring My Day to-do (`project.task`, `x_myday_recur` in {daily, weekdays, weekly, biweekly, monthly, 6months}) tracks **ONE current occurrence**. `_complete_task_with_spawn` (myday.py) advances it ONLY when you mark it **done** — it spawns the next-dated task + closes the current. There is NO cron. So if DJ stops checking a habit off, the occurrence just sits frozen on its old date (overdue forever) instead of rolling to today. Extra copies (e.g. 3 "💪 Workout" at 984/985/986/987) can also accumulate if new ones get created without the old being marked done — there should be exactly ONE live occurrence per habit.

**2026-07-12 fix:** DJ's habits (🧘 Meditate / 💪 Workout / 🐕 Walk the Dogs / 🎮 Watch TV) were stuck on Jun 17–22. Manually: canceled the 2 duplicate Workouts (state=1_canceled), re-dated the 4 survivors to today 09:00 PT. Then added durable **auto-roll-forward**: new `_rollforward_recurring(tasks, today)` helper (after `_advance_recur`) called in `api_myday` right after the task fetch — for any overdue recurring task it steps `_advance_recur` (bounded 400) until the occurrence is today-or-later, WRITEs the new date_deadline (no new task spawned), and mutates the in-memory task so the same load shows it on today. Runs once/day per stale habit. Commit 7b69e08 (myday.py 1366→1401 lines). See [[project_planner_myday_sync.md]], [[project_myday_task_lifecycle.md]].
