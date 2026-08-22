---
name: Phase 4 / sync_action_955 task re-entry bug
description: When Workiz substatus cycles Scheduled → "Next Appointment X - Text" → back to Scheduled, the Planned project.task gets deleted on the outbound trip but isn't recreated on return — Field Assistant shows no timer
type: project
originSessionId: 545d601c-e5c6-46c0-aca1-5a8081a73ec9
---
**Root cause:** Phase 4 and/or sync_action_955 delete Planned project.tasks when a Workiz job transitions out of Scheduled (into "Next Appointment - Text", "Next Appointment 2 - Text", etc.). When the job cycles back to Scheduled, the task is never recreated. The SO's cached `tasks_count` stays at 1, which fools any "has task?" check that uses the cached field instead of actually querying project.task.

**Symptom:** DJ opens a job in Field Service Assistant, sees no task, can't start the timer. SO looks fine on paper — tasks_count shows 1 — but project.task for that sale_order_id is empty.

**Case confirmed 2026-04-20:** SO 15916 (Barbra Balser, Apr 20 3:30 PM job). Chatter showed substatus went Scheduled → "Next Appointment - Text" → "Next Appointment 2 - Text" → back to Scheduled on Apr 17. Task was deleted, never recreated. Fix today: manually recreated as task 297, linked to order line 17478. Modeled on Ruby Weaver's task (same service type, same tech, stage 17 Planned).

**Sweep 2026-04-20:** 4 active-future SOs have `tasks_count > 0` but zero actual tasks:
- SO 17116, 17117 (Naresh Bellara test jobs, May 5) — skip, no tech assigned
- SO 15857 (Lanny & Sue Lund, May 12) — expected, Phase 4 deletes tasks on Submitted before confirmation
- **SO 17066 (Wayne Geringer, Aug 20 2026)** — same bug as Balser, reactivation orphan, needs task recreated before that date

**Why it matters:** Timer won't start without a task. Every reactivation-cycled job is a potential silent orphan.

**How to apply:** 
- When DJ reports "no task" on a recently-reactivated SO, first check: `env['project.task'].search([('sale_order_id', '=', SO_ID)])`. If empty but `tasks_count > 0`, this bug.
- Short-term fix: recreate the task modeled on a peer job (same tech, same service, stage 17 Planned), link to the correct order line via `x_sale_order_line_id`.
- Long-term fix (NOT BUILT): in whatever server action / Zapier step handles "Scheduled" status entry, add logic: if SO has no project.task for its sale_order_id, call the task creation routine (same one used at initial Schedule). Candidates: sync_action_955, Phase 4's status-change branch. Needs a read of those files to locate the exact insertion point.

Related memory: `project_task_deletion_stage_filter.md` — the outbound deletion side is already stage-gated (only New/Planned, not In Progress/Done). The gap is purely on the return trip.
