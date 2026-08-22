---
name: project_cc_reschedule_via_workiz
description: "Command Center reschedule must update WORKIZ (source of truth), not Odoo date_order — fixed 2026-06-28"
metadata: 
  node_type: memory
  type: project
  originSessionId: b8f82f75-713b-49ec-b4d3-aeb0cffeef8f
---

Command Center "Needs scheduling" Reschedule was WRONG: `/api/schedule/reschedule` (scheduler.py) only wrote Odoo `date_order` + confirmed the SO, never touching Workiz. Since Workiz is source of truth and Phase 4 polls every 5 min, the Workiz job kept its old date and Phase 4 overwrote Odoo right back → desync. DJ caught it 2026-06-28 ("that's not how we reschedule, we have to update from Workiz side").

**FIX (live):** `api_schedule_reschedule` branches on the SO's Workiz UUID:
- Has UUID → reschedule is **DAY/TIME ONLY**: `workiz_post('job/update/{uuid}/', {'JobDateTime': <Pacific-local>})` and LEAVE the Workiz status alone (so a job already at 'Send Confirmation - Text'/'Scheduled' isn't knocked backward). Phase 4 syncs date to Odoo. Does NOT write date_order (Phase 4 owns it). **EXCEPTION:** if current status is '' or 'Submitted' (a placeholder not yet on the schedule), ALSO send `SubStatus:'Scheduled'` to promote it + create a `[Render] Review before sending` project.task. DJ pushback 2026-06-28: don't force Scheduled on an already-scheduled job — reschedule is just day/time. ('Scheduled' belongs to the initial-scheduling tool field.py `schedule_job`, not to reschedule.)
- No UUID (Personal Time block) → old Odoo `date_order` write (Pacific→UTC) fallback, unchanged.

**workiz_post status quirk (shared.py L130):** it injects `Status='Pending'` ONLY when the payload contains a `SubStatus` (and no Status). So a JobDateTime-only update preserves the existing status — that's what makes day/time-only reschedule safe. `inject_status=False` skips it (Submitted top-level jobs reject Status).

**Direction note (DJ insight):** normal flow is Workiz-first → Phase 4 → Odoo. This reschedule is the FIRST app→Workiz write — possible only because the job already exists (has a UUID) so we can hit Workiz's update API. Workiz stays source of truth; the app is just a remote control writing INTO Workiz, then Phase 4 carries it to Odoo as usual.

**Why it works:** the Needs rows already carry `uuid` (from `/api/scheduled_sos`, dashboard.py ~L7757); reschedule modal posts `so_id` → endpoint looks up UUID.

**Non-obvious facts confirmed:**
- **Workiz `JobDateTime` = Pacific-LOCAL `'YYYY-MM-DD HH:MM:SS'`, NOT UTC** (verified in dashboard.py `duplicate_job` L6694 + field.py `schedule_job`). Odoo `date_order` is UTC; don't confuse the two.
- `scheduler.py` already has `workiz_post`/`workiz_get`/`odoo_rpc`/`_PT` via `from .shared import *` (defined in routers/owner/shared.py, exported in `__all__`).
- The canonical "schedule/move an existing job" primitive = update existing Workiz job's JobDateTime + SubStatus='Scheduled' (puts it on the schedule; does NOT text the customer — only 'Send Confirmation - Text' texts). Lives in field.py `schedule_job._update_uuid` (AI tool); now also as the reschedule HTTP endpoint.
- UI lag: rescheduled row stays in Needs until Phase 4 sync (~5 min) flips it; success toast tells DJ this. Confirmed via [[project_calendar_job_move_postworkiz]] (writing Odoo date_order alone gets overwritten by Phase 4).

Part of making Command Center (schedule_hub.html @ /owner/command-center) replace Field Assistant — see [[project_command_center]]. Phase 1 (2026-06-28) made CC the hub primary card + seamless tap-to-Field-panel handoff (back btn reads "‹ Schedule", from=cc).
