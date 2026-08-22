---
name: project_myday_task_done_is_state_not_stage
description: "My Day / Odoo To-do project.task records track open/done/cancelled via the `state` field, NOT stage_id (which is False). Filtering by stage gives wrong counts."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce472468-5c4c-4b62-be96-a95fc1c75f1b
---

**My Day / Activities tasks are Odoo To-do `project.task` records with `project_id = False` AND `stage_id = False`.** Open vs done/cancelled is tracked entirely in the **`state`** field (Odoo 19 To-do app):
- `01_in_progress` = OPEN / active
- `1_done` = completed (set by myday.py L250 / reactivation.py followup markdone L921)
- `1_canceled` = cancelled/removed (this is how you "delete" one reversibly — keeps active=True, just closed)

**GOTCHA that burned me 2026-06-25:** filtering these tasks by `stage_id`/folded-stage is meaningless (stage is always False) — it treats cancelled+done as "open" and massively over-counts. Earlier wrong query said "38 dup customers / 85 open re-engagement tasks"; the CORRECT `state`-based query said 151 in_progress / 46 canceled / 6 done → **0 open duplicates**. ALWAYS filter `['state','not in',['1_done','1_canceled']]` for "open My Day tasks" (this is exactly what myday.py L266/319/948 and activities.py L103 do). Cancelled tasks still have active=True, so `active` filtering won't hide them either — only `state` does. Both My Day and Activities views correctly hide done+cancelled via the state filter.

**Re-engagement duplicate cleanup STATUS (2026-06-25): already done.** A prior chat cancelled 46 duplicate "Re-engagement:" tasks (state→1_canceled), kept 1 open per customer, and correctly marked sent-then-done ones (e.g. Barbara Rago pid 23220: Jun-17-texted task #347→1_done, new cycle #1088 kept open). 0 open duplicates remain. The planned `/owner/dedup-reengagement` page was NOT built — there was nothing left to dedup. See [[project_reengagement_vs_reactivation]], [[project_reengagement_sms_template_detector]].

**To reverse a cancel:** write `state='01_in_progress'` (myday.py "uncomplete" L662 does this). **How to apply:** any time you count, list, or dedup My Day/To-do tasks, key off `state`, never stage_id/active alone.
