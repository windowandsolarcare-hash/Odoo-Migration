---
name: Odoo todo models — mail.activity vs project.task — when each is used
description: 2026-04-30 — DJ has TWO different models that act like to-dos. mail.activity is reminders attached to records (chatter). project.task with project_id=False is Odoo's "To-do" app records. Render's /api/todos must query BOTH. Bug found 2026-04-30 when Mark Sarah Fredricksen follow-ups (project.task) didn't show in Render Activities tab.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when editing /api/todos, /api/followup/*, /api/todos/snooze, the create_todo tool, or any code that queries DJ's to-dos.**

## The two models

DJ's Odoo has two distinct "to-do-like" models, each used for different purposes:

### `mail.activity`
- "Next step on this record" — a reminder anchored to a specific business object via `res_model` + `res_id`
- Lives in the **chatter** of the parent record + appears in Odoo's global "Activities" filter
- Has `summary`, `note`, `date_deadline` (date), `activity_type_id`, `user_id`
- No stages, no tags, no time tracking
- Used in W&SC for: **reactivation follow-ups, follow-up SMS reminders, future-self reminders DJ creates ad-hoc**

### `project.task`
- A unit of work with stages, assignees, deadlines, tags, time tracking
- Two flavors:
  - **`project_id != False`** — task in a real project. Used by Field Service jobs (Phase 4 syncs Workiz jobs to project.tasks in `Field Service` project, id 2)
  - **`project_id = False`** — Odoo's "To-do" app records. Personal to-dos. Lives at `/odoo/to-do`.
- Has `name` (not summary), `description` (HTML), `date_deadline` (datetime), `state` (Kanban: '01_in_progress', '1_done', etc.)
- Used in W&SC for: **Field Service tasks (the schedule), personal To-dos created from Render via `create_todo` tool**

## Why Render's `create_todo` tool uses `project.task`

When Render Claude (or DJ via voice) says "create a follow-up to-do for X," the `create_todo` tool in `Saunders Render App/routers/owner/dashboard.py` writes to **`project.task`** with `project_id = False`. This is intentional — it's how Odoo's "To-do" app stores its records, so DJ sees them at `/odoo/to-do`. Using `mail.activity` instead would bury the reminder in the customer's chatter, which DJ doesn't check daily.

## The bug we hit on 2026-04-30

Render's `/api/todos` was originally built reading only `mail.activity`. When `create_todo` was later wired to use `project.task` (so to-dos appear in Odoo's To-do app), nobody updated `/api/todos` to ALSO read `project.task`. Result: the 3 Mark Sarah Fredricksen follow-ups DJ created via Render lived in `project.task`, showed up in Odoo's To-do menu, but **never appeared in Render's Activities tab**.

**Fix (commit 668d619f, 2026-04-30):** `/api/todos` now queries BOTH models, returns a merged list with a `source` field (`'activity'` or `'task'`) on each item. The `markdone` and `snooze` endpoints accept `source` to know which model to write to. Frontend passes `source` through.

## Rules going forward

When working on /api/todos or any to-do query/write code:

1. **Read both `mail.activity` AND `project.task`** in the same response. Filter project.task to:
   - `project_id = False` (Odoo To-do app records — NOT Field Service tasks)
   - `user_ids in [ODOO_USER_ID]` (DJ assigned)
   - `state not in ['1_done', '1_canceled']`
2. Each todo gets a **`source`** field: `'activity'` or `'task'`. Keep this on every record.
3. **Frontend must pass `source`** when calling write endpoints (markdone, snooze, etc.) so backend writes to the right model.
4. **Markdone semantics differ:**
   - `mail.activity`: `action_done` (or `unlink` as fallback)
   - `project.task`: `write({state: '1_done'})` (or `write({active: False})` as fallback)
5. **Snooze semantics differ:**
   - `mail.activity.date_deadline` is a **date** ('2026-04-30')
   - `project.task.date_deadline` is a **datetime** ('2026-04-30 12:00:00') — append ` 12:00:00` to avoid TZ rollover
6. **Followup-SMS modal only applies to mail.activity** — `isFollowupTodo()` predicate returns false for source='task' to suppress the "Open Follow-Up Editor" button. Task-source records get only Mark Done + Snooze.
7. **Done-list query needs both models too** (added 2026-04-30 night). `/api/todos/done` reads:
   - `mail.activity`: `active=False AND date_done >= cutoff` (with `active_test: False` context)
   - `project.task`: `project_id=False AND user_ids in [DJ] AND state='1_done' AND write_date >= cutoff`
   `write_date` is the proxy for "when completed" on tasks (most recent write is usually the state flip). Both share a `source` field.
8. **Reactivate semantics** (commit 19854da0, `/api/todos/reactivate`):
   - `mail.activity`: `write({active: True})` to un-archive (record stays present after action_done; only the `unlink` fallback would lose it permanently)
   - `project.task`: `write({state: '01_in_progress', active: True})` — `01_in_progress` is the default open state for Odoo 19 To-do app records

## Files involved

- `Saunders Render App/routers/owner/dashboard.py`:
  - `create_todo` tool — writes to project.task
  - `/api/todos` — reads both
  - `/api/todos/snooze` — handles both
  - `/api/followup/markdone` — handles both
- `Saunders Render App/static/owner/activities.html`:
  - `loadOpen` / `renderOpen` — caches `source` per todo
  - `detailMarkDone`, `detailSnooze` — pass `source` to backend
  - `isFollowupTodo` — returns false for source='task'

## Don't confuse these with project.task records that ARE Field Service jobs

`project.task` with `project_id = 2` (Field Service) is a SCHEDULED JOB on DJ's calendar, NOT a To-do. Different concept entirely:
- Field Service tasks come from Phase 4 (Workiz job → Odoo SO → action_confirm → task creation)
- They have product line items, planned start/end times, tech assignees, etc.
- DJ uses these for actual work scheduling, not reminders
- They're shown in the Render Field Assistant schedule tab, not the Activities tab

The To-do app filter (`project_id = False`) cleanly separates them.
