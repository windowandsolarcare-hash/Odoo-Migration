---
name: project_calendar_job_move_postworkiz
description: Post-Workiz plan — let DJ move/reschedule REAL jobs block-by-block on the calendar (drag or tap-to-move). Capability already proven via move_block; blocked today only by Workiz being source-of-truth.
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

DJ wants (post-Workiz): move REAL customer jobs around on the **calendar view** block-by-block (drag-and-drop or tap → "Move to…" day/time), to reshuffle a day/week visually.

**The capability already exists and is proven.** Moving any job = rewriting ONE field, `sale.order.date_order` (PT→UTC). That's exactly what the Personal-Time `POST /owner/api/schedule/move_block` does (built 2026-06-24, see [[project_schedule_add_block]]). A real job is mechanically identical to a Personal Time block.

**Why it's locked to Personal Time blocks TODAY (not a technical limit):** Workiz is the source of truth for real jobs. (1) Moving a job's date in Odoo alone wouldn't reflect in Workiz → the two disagree. (2) Phase 4 sync polls Workiz every few minutes and would **overwrite the move right back**. The `move_block` guard (`refuses any SO with workiz_uuid or job_type != 'Personal Time'`) exists precisely to prevent this desync.

**Post-Workiz build (when Odoo is the single source of truth — see [[project_system_roadmap]] migration item, [[project_north_star_comprehensive_crm]]):**
1. Drop / relax the `move_block` guard so it accepts any job (or add a sibling endpoint for real jobs).
2. Add the move UI on the **calendar** (`static/owner/calendar.html`): drag-and-drop block-by-block, or tap a job → pick new day/time (mirror the field-schedule 3-dot "📅 Move / Reschedule" item already shipped in field.html).
3. Keep CLAUDE.md rule 8/9 in mind: `date_order` = job START time, and `action_confirm` resets it — don't re-confirm on a move, just write date_order (the block move already does this correctly).

**Open product decisions for then (not blockers):** (a) should moving a job auto-TEXT the customer the new time? (b) re-run route optimization after a shuffle? ([[project_shared_scheduler]] `build_day_plan` exists for the GPS/route side).

Status 2026-06-25: parked on the post-Workiz list at DJ's request. Not started. Workiz drop/port is the prerequisite ([[project_twilio_port_from_workiz]]).
