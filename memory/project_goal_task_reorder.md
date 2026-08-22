---
name: project_goal_task_reorder
description: "Goal Board tasks are now reorderable with ▲▼ buttons like milestones (project.task native `sequence`, /api/goals/task/reorder), and changing a task's due date auto-re-sorts that milestone's tasks into date order."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T07:19:14.125Z
---

**2026-07-26 (DJ: "need to be able to move tasks like I can milestones. also when I change dates it should move the order for me").** In the Goals app, milestones already had ▲▼ up/down move (`msMove` → `/milestone/reorder`, hand-set `sequence`), but tasks were fixed in creation order (`id asc`). Added the same to tasks + date-driven re-sort.

**Backend (goals.py, commit d80ca86):**
- `goals_get` now fetches tasks `order='sequence asc, id asc'` (was `id asc`) — tasks obey the native `project.task.sequence`.
- New `POST /api/goals/task/reorder {ids:[...]}` — writes `sequence` from the given id order (mirrors `ms_reorder`).
- `task_update`: when the payload includes `'due'`, after writing the date it **re-numbers that task's milestone's tasks by date** — dated tasks sorted by `date_deadline` (earliest first), undated kept last by their prior sequence. So a date change reflows the list into date order.

**Frontend (v2_goals.html, commit 5b46401):** each task row (`taskHtml`) gets a `.t-move` ▲▼ pair (smaller clone of `.ms-move`); `tMove(id,dir)` finds the task's list (`taskLoc` — its milestone's `tasks` or the loose bucket), swaps in place, re-renders, and POSTs `/task/reorder`. Task date edits already `reload()` after save, so the backend's date re-sort shows immediately. No date-order warning on task move (unlike milestones) — tasks move freely; dates re-sort separately.

**Interaction:** manual ▲▼ order persists until any task's date changes in that milestone, at which point the whole milestone re-sorts by date (DJ's explicit want). **Verified live** on goal 9: moved a task to a later date → it dropped to the end; manual reorder held out of natural order; data restored. See [[project_goal_board]], [[project_goal_target_date_phaseA]].
