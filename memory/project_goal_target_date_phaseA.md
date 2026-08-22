---
name: project-goal-target-date-phasea
description: "Goals Phase A: a goal now has a 'Hit by' target date (custom field x_goal_target_date on project.project, id 21374). Milestones/tasks dated past it are flagged + warn-on-save. Phase B (hand-set milestone order + neighbor-date checks) is next."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T06:57:07.773Z
---

**2026-07-24 — DJ steering Goals toward project management.** He chose: milestones = HAND-SET order with date validation (not auto-sort by date); build order = Phase A (goal target date + guardrail) first, then Phase B.

**NEW FIELD (verified via API):** `x_goal_target_date` — ttype **date**, `store=True`, on model **project.project** (model_id 859), ir.model.fields **id 21374**. This is the goal's "hit by" finish line. Deliberately NOT reusing project.project's native `date` field (that's Odoo's "Expiration Date" and can auto-archive the project once it passes).

**Phase A shipped (goals.py commit 1f78860 + v2_goals.html b87c2e2):**
- Backend: `/create` + `/update` accept `target`; `/list` + `/get` return `target`. `/get` adds a `past_goal` boolean on each milestone (its `deadline` > target) and each task (its `due` > target).
- Frontend: "🎯 Hit by" date on the New-goal form; editable finish-line chip in the goal hero with a live countdown (`goalCountdown()` → "Nd left" / "Nd overdue"); `editTarget()` opens the styled date sheet. Milestones/tasks past the goal show a red ⚠ (`.pastgoal`). Guardrail `confirmPastGoal(dt, proceed)` intercepts milestone/task saves whose date is past the goal target → "past your goal date, pull it in or push the goal out — save anyway?" (active decision, not a hard block).

**Phase B SHIPPED 2026-07-24 (goals.py d22e9d5 + v2_goals.html bb3e7f5):** hand-set milestone order + neighbor-date awareness.
- `project.milestone` has a NATIVE `sequence` (integer) field — used it, no custom field needed. `goals_get` now orders milestones `sequence asc, id asc` (was `deadline asc`) and returns `sequence`. `ms_create` appends at end (max sequence +1). New endpoint `/api/goals/milestone/reorder {ids:[...]}` writes sequence from the id order.
- Frontend: ▲▼ up/down buttons on each milestone header (`.ms-move .mv`) → `msMove(id,dir)` swaps optimistically + posts reorder + reload (chose up/down over drag = reliable on phone). Add/Edit-milestone forms show the prev/next milestone's date IN the date-field label ("after 'X' (date) · before 'Y' (date)"). The old `confirmPastGoal` became general `confirmDate(dt, {prevDate,prevName,nextDate,nextName}, proceed)` — warns (never blocks) if a date is past the goal target OR before the prior milestone OR after the next one in the hand-set order. Tasks call `confirmDate(v.due, {}, …)` (past-goal only).
- NOTE: the forecast's cumulative-weeks now follows sequence order (the order DJ will actually do them) — correct for this model.

**Fix 2026-07-24 (DJ: moving a milestone up gave no out-of-sequence message + roadmap wrong after a move) — v2_goals.html 4049267:**
- `msMove` now runs `msOrderViolation(arr, j)` after the swap: if the moved milestone ends up before a milestone dated earlier (or after one dated later), it `openConfirm`s "Out of date order … reorder anyway?" before committing (warns, doesn't block). Previously the guardrail only fired on date EDITS, never on reorder.
- `renderRoadmap` REWRITTEN to position dots by hand-set ORDER (evenly spaced 6→94%), not by date — so the map matches the list after a move (before, dots were date-positioned + date-sorted, so a reorder never moved them). "today" marker now sits in order-space after however many milestones are past by date. TRADE-OFF: the roadmap is no longer time-scaled (uniform gaps regardless of real date spacing) — it's a "steps in order" view. Acceptable for the ordered-milestone PM model; revisit if DJ wants true time-scaling back.

**Possible Phase C (not requested):** true drag-reorder, real task/milestone dependencies, planned_date_begin → Gantt. See [[project_goal_board]], [[project_goal_layer3_bump]].
