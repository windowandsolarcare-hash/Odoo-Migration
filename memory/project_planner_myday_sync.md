---
name: project_planner_myday_sync
description: "Daily Planner habits ↔ My Day recurring to-dos are kept in two-way sync (check off in either place, reflects in the other for TODAY). Built 2026-06-17. Hook lives in dashboard.py (planner routes are shadowed)."
metadata:
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ wanted FULL sync between his Daily Planner habits and their My Day to-do mirrors** (he kept both per [[project_myday_reminders]]). Done 2026-06-17, both directions verified live.

## The model
- DJ's 6 planner habits (`personal.planner.8487.template`, access code **8487**) are ALSO 8 recurring My Day `project.task`s (ids 984-991; Workout is M/W/F → 3 weekly tasks). Match key = **My Day task name == planner `emoji + ' ' + name`** (e.g. `🧘 Meditate`) — stable across the spawn-on-done id change, so no stored task-id map needed. Verified all 8 match incl. the ZWJ emoji (`👨‍👩‍👧 Visit Mom & Dad`).
- Planner tracks per-DATE history (`personal.planner.8487.history` = `{date:{habit_id:'done'}}`). My Day recurring task = one open occurrence that spawns the next on done. Sync only touches **TODAY** (the live occurrence); past/future planner edits don't move My Day.

## Where the code lives (myday.py)
Helpers in `routers/owner/myday.py`: `_planner_habit_map()` ({taskname→habit_id} from template), `_planner_write_history()`, `_sync_myday_to_planner(name, done)`, `_complete_task_with_spawn(rid)` (the done+spawn logic, extracted so both the /done endpoint AND planner-sync share it), and the exported **`planner_checkin_to_myday(habit_id, date_iso, status)`**.
- **My Day → Planner:** `/api/myday/done` (task branch) calls `_complete_task_with_spawn` then `_sync_myday_to_planner(name, done=True)`. `/api/myday/reopen` calls `_sync_myday_to_planner(name, done=False)` (writes 'undo').
- **Planner → My Day:** `planner_checkin_to_myday`: status 'done' → find the open task by name, `_complete_task_with_spawn` it (spawns next). status 'undo' → reopen the most-recent done task + delete the future spawn (`x_myday_recur` set, deadline > today).
- **No loops:** each direction writes the OTHER via low-level param/task ops, never via the other's endpoint.

## ⚠ THE GOTCHA THAT COST AN HOUR — planner routes are SHADOWED in dashboard.py
ALL `/api/planner/*` routes (template, template/save, history, **checkin**, stats) AND `/planner` are defined in BOTH `dashboard.py` (~line 12153+, registered first → WINS) AND `planner.py` (dead). I added the sync hook to **planner.py first → ZERO effect** (no `[PLANNER-SYNC]` logs at all — the tell). The LIVE checkin is **dashboard.py `api_planner_checkin` (~line 12198)** — the hook HAD to go there. planner.py keeps a copy of the hook (harmless, dead) in case the shadow is ever resolved. Same disease as calendar_jobs / reactivation — see [[project_reactivation_route_shadowed_in_dashboard]]. **RULE: before adding behavior to ANY `/api/*` route in a router registered after dashboard, grep dashboard.py for the path first.**

## Verified (isolated, self-cleaning)
Tested with a THROWAWAY habit (`habit-synctest-zzz` / `🧪 __SyncTest__`) added to the template + a matching daily task, never touching DJ's real habits: planner done→My Day completes+spawns; planner undo→reopen+despawn; My Day done→planner history 'done'+spawn; My Day reopen→planner history cleared. All passed, then habit+tasks+history fully removed.

## Gotcha: local `calendar.py` shadows stdlib
Running a test script from a dir containing a local `calendar.py` copy breaks `import calendar` (and `requests`, which imports it). Run from a clean dir.
