---
name: project_myday_task_creators
description: "Two My Day task creators — /api/myday/add (canonical, rich) and /api/todos/create (note-capture that promotes to My Day when dated). They now share myday.myday_deadline_utc for PT→UTC dates. A My Day task needs user_ids=[DJ] AND (project_id=False OR x_myday_pinned OR dated-goal-task)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T07:43:55.178Z
---

**Clarified 2026-09-12** fixing the Operator-reported todos/create bug.

## The two creators (both make a project.task; keep them consistent, don't re-diverge)
- **`POST /owner/api/myday/add`** (myday.py) = the **canonical, rich** My Day creator. Fields: `title`, `date`+`time` (PT→UTC), `note`, `duration`, `priority`, `recur`, `kind`, `pinned`, `status`, `checklist`, `action`, `tag_ids`. ALWAYS a My Day task (assigns DJ; blank date → today). This is what the My Day UI uses.
- **`POST /owner/api/todos/create`** (activities.py) = the **note-capture** entry (Notes card / job notes). `note` → task name (first line) + description, `partner_id`, and a date (`date` OR `due_date`, + optional `time`). **Undated = job-only note** (`user_ids=[]`, off My Day — its unique capability). **Dated = promotes to a My Day task** (assigns DJ, sets `x_myday_type='task'`/`x_myday_status='todo'`).
- Shared date logic: **`myday.myday_deadline_utc(date, time='09:00')`** — the ONE PT→UTC converter, used by BOTH (no divergent date handling).

## What the My Day list actually requires (api_myday task domain, myday.py)
A project.task shows on My Day when:
`( project_id==False  OR  x_myday_pinned==True  OR  (project_id in goal_ids AND date_deadline!=False) )  AND  user_ids in [DJ]  AND  state not in (1_done,1_canceled)`.
⇒ the silent-failure trap: a task with **`user_ids=[]` never surfaces**, no matter its date.

## The bug that was fixed (root cause)
todos/create read only `due_date`; a caller (and myday/add) use `date`. A dated note sent as `date` → `due_date` was None → fell to the undated branch → `user_ids=[]` → **never appeared in My Day** (looked like "dropped the date + owner"). Fix: accept `date|due_date`, use `myday_deadline_utc`, set the `x_myday_*` metadata. Verified: dated via `date` now assigns DJ + lands on My Day; undated stays job-only.

Related: [[feedback_reuse_canonical_endpoint]].
