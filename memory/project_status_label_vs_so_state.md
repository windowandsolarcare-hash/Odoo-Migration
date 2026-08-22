---
name: project_status_label_vs_so_state
description: "The schedule gates on SO `state` in ('sale','done'), NOT the x_studio_x_studio_workiz_status LABEL. Marking a job 'Submitted' in the job editor does NOT unconfirm it → it stays on the schedule. Unconfirm = action_cancel then action_draft."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T14:34:45.931Z
---

**A job stays on the schedule even after you mark it 'Submitted' — because the two are different things.** (DJ hit this 2026-08-04 with Rod & Becky Hahn, SO 004870/id 17462.)

- **The schedule** (Command Center `/api/scheduled_sos` + `/api/calendar_jobs`, field.html) gates on the SO **`state` in ('sale','done')** + `date_order` = that day. It does NOT look at `x_studio_x_studio_workiz_status`.
- `x_studio_x_studio_workiz_status` (Submitted/Scheduled/Done/Canceled/...) is just a **LABEL**. Writing it 'Submitted' does NOT change `state`. So a confirmed job (state='sale') marked 'Submitted' is inconsistent and **stays on the schedule**.
- **To take a confirmed SO OFF the schedule (make it a draft/Submitted job):** `action_cancel` then `action_draft` → state='draft'. Verified 2026-08-04: 'sale'→(action_cancel)→'cancel'→(action_draft)→'draft'; name + date_order preserved. `action_draft` ALONE from 'sale' is a no-op (must cancel first). Direct `write({'state':'draft'})` also works as a last resort (no invoices/deliveries on a simple service SO). Guard: skip if `invoice_ids` present.
- Re-scheduling later: `schedule_odoo_so(so_id, dt_pt, set_status=True)` confirms draft→sale + writes date_order → back on the schedule.

## ★ DECISION (DJ 2026-08-04): KEEP the confirmed gate. Do NOT switch to status-based, do NOT auto-change confirm/draft in code (yet).
DJ chose to STAY with the existing rule — **on the schedule = SO `state` in ('sale','done')**. He is NOT building status-based gating (that's "old-school Workiz" + unknown ripples). Instead, keep the DATA consistent: a job that should not be scheduled = **un-confirm it** (action_cancel→action_draft). **Schedule verified CLEAN 2026-08-04:** of 87 confirmed future jobs, 0 were Submitted (Rod & Becky was the only stray, hand-fixed); the only blank-status ones are a Personal Time block + the "ZZ PDF Test" junk. So no mass cleanup was needed. The auto-unconfirm-on-status-edit CODE change stays **deferred/unbuilt** (specialist stood down). Open later task (DJ): "gather up the nonconfirmed" (draft/Submitted jobs) into a pile to deal with = the Submitted Jobs pipeline. Below kept for reference on the mechanism.

## (reference) earlier framing — study-repercussions before switching gate (superseded by the decision above)
DJ pumped the brakes: don't touch the confirmed/draft mechanism now (unknown ripple effects). His analysis (correct):
- **The INTENDED schedule gate was always the STATUS**, not state — a job is meant to be on the schedule ONLY when `x_studio_x_studio_workiz_status` is one of the ~4 on-schedule values: **Scheduled / Send Confirmation - Text / Next Appointment - Text / Next Appointment 2 - Text** (CLAUDE.md KEY VOCABULARY). **Submitted was NEVER meant to be on the schedule.**
- Command Center gates on `state in (sale,done)` because the MIGRATION made state an accidental PROXY: Phase 3/4 created Submitted jobs as **draft** and only CONFIRMED (→sale) when they reached one of those scheduled statuses. So state tracked status — until you edit status manually post-Workiz (proxy breaks).
- **Near-future (before any code): full repercussions review** — enumerate everything reading `state` in ('sale','done') vs the status — then deliberately either (A) gate the schedule on STATUS, or (B) make status changes drive state. Lead drives the analysis with DJ first. Specialist told to STAND DOWN (AGENT_MAIL 2026-08-04). Rod & Becky (17462) hand-fix stays. See [[project_appt_confirmation_odoo]], [[feedback_done_jobs_definition]].
