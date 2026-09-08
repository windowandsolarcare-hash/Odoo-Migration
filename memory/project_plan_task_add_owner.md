---
name: project_plan_task_add_owner
description: "Plan Add-task (POST /cheryl/api/task/add → goals.task_create): accepts name (req), goal_id (OPTIONAL → defaults to the 'Not sorted yet' goal, project id 25, so goal-less tasks still show on the Gantt), hours (→allocated_hours), due (→date_deadline), owner dan|cheryl. NEW custom field project.task.x_owner (Many2one→res.partner, Dan=3 / Cheryl=23243, ONE owner) — the plan reads owner off it (there's no cheryl Odoo user; only Dan Saunders id 2)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T17:15:23.860Z
---

**Built 2026-09-08 (Cheryl Add-task UI + the plan owner model).** Cheryl's plan (plan-views.html) got an Add-task form; the backend is `POST /cheryl/api/task/add` → delegates to `goals.py task_create` (the canonical task-create, shared with the owner Goals UI).

**`task_create` now accepts (all additive, owner UI unaffected — it always sends goal_id):**
- `name` (required), `goal_id` (**OPTIONAL** — if absent, defaults to the **"Not sorted yet" goal**), `hours` OR `duration` → `allocated_hours`, `due` → `date_deadline`, `milestone_id`, `pin`, and `owner` ∈ {`dan`,`cheryl`} → `x_owner`.
- **Why goal is optional + defaults:** a `project_id=False` task is a loose My-Day to-do the plan/Gantt does NOT show (the plan reads tasks whose `project_id` is a goal-tagged project.project, company 1). So a goal-less plan task lands in **"Not sorted yet"** (`project.project` id **25**, tag "Goal"=25, company 1; via `_unsorted_goal_id()`, cached/auto-created) to stay visible. Frontend rule (Cheryl): context-first (inherit the goal she's inside), fall back to "Not sorted yet" only when no context, never preselect, surface its count.
- **Why hours+due matter:** without them the task has no capacity/date so it's invisible on the Gantt/day-total (the Launch-Runway "no dates/hours = invisible" blocker).

**★ NEW custom field `project.task.x_owner`** = Many2one → res.partner, store=True (created 2026-09-08, field id 21398). **There is NO cheryl Odoo user — only Dan Saunders (res.users id 2, partner id 3).** So plan "owner" (dan vs cheryl) is stored on `x_owner` as ONE res.partner (**Dan=partner 3, Cheryl=partner 23243**), NOT on `user_ids`. `_build_view_plan` reads `owner` off `x_owner` (`t['x_owner'][1]`), not user_ids. This is also the Launch-Runway ingest's owner field. See [[project_cheryl_ideas_delegation]] (the cheryl-role QC discipline — Lead verifies the Add as cheryl) and [[project_writeback_not_proof_computed_field]] (x_manual_progress, the other custom project.task field).
