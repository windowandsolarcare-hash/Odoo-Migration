---
name: project_done_stage_state_mismatch
description: "Tasks moved to a folded \"Done\" stage but state never synced to 1_done still show as active (Customer Brain Action Items) — 248 legacy per-job tasks backfilled"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Odoo gotcha:** `project.task` has a kanban `stage_id` AND a separate `state` (01_in_progress / 1_done / 1_canceled). Moving a task to a FOLDED "Done" stage does NOT set `state='1_done'`. App queries filter on `state` (not stage), so a task in a Done stage with `state='01_in_progress'` still counts as ACTIVE and shows up. The two "Done" stages are ids **6 and 19, both `fold=True`**.

**2026-07-12:** John Ham had a lingering "task" (task 196, "John Ham - Solar Panel Cleaning", stage Done/state in_progress) that DJ saw when duplicating a job for him. It was 1 of **248** DJ-assigned tasks in a folded Done stage but state!=done — ALL legacy per-job tasks ("Customer - Service"/"- Tip"/"- Clean Gutters") from Mar–May 2026, created by the OLD Phase-5 per-job task flow (deprecated 2026-05-28). **NONE were re-engagement.** First backfilled all 248 → `state='1_done'`, then DJ refined: keep DONE only where the customer already has a FUTURE non-cancel job (date_order >= today); reactivate the rest. Result: **135 kept done** (customer booked ahead), **115 reactivated** (state='01_in_progress', 73 unique customers with an old job task but NO upcoming booking = a re-schedule worklist → scratchpad/myday_115_need_scheduling.csv). Full 248: scratchpad/myday_248_done_stage_tasks.csv. (Reactivated ones are still in the Done STAGE but state=in_progress, so they show as active in state-based queries — Customer Brain Action Items/Notes, not the My Day list which is project_id=False.)

★ **Where these showed:** NOT the My Day list — every My Day `project.task` query filters `['project_id','=',False]` (personal to-dos), and these are `project_id=2` (Field Service). They surface as **Customer Brain "Action Items"** (dashboard.py customer_jobs, per-customer dated project.tasks) and any per-partner task list. **Durable fix option (not yet done):** add `['stage_id.fold','=',False]` to the Customer-Brain task queries so a Done-stage task never shows regardless of state (the dotted `stage_id.fold` domain works). Backfill handled current data; recurrence is low since per-job task creation is deprecated.

★ **Separate open item:** re-engagement DOES still create `Re-engagement:` project.tasks (project_id=False → they DO show on My Day + drive the auto-pilot [[project_reengagement_autopilot]]). DJ wants to "get rid of My Day tasks for re-engagement" — that's a distinct design change (move re-engagement fully to the Waiting screen [[project_waiting_screen]]), NOT what John Ham's task was.
