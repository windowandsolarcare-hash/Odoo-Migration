---
name: project_voice_reschedule_tool
description: "Voice reschedule: dashboard.py reschedule_job WRITE tool (confirm-gated) moves a job by voice, Odoo-native, reusing scheduler.schedule_odoo_so. NO Workiz."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-20T02:00:52.632Z
---

**Built 2026-08-19 (DJ: "build the reschedule"), dashboard.py b7dd204.** DJ can now say *"move/reschedule Michael to Thursday at 8"* → the voice assistant finds the job itself (search_customers → get_job_details / upcoming SO), proposes a confirm — `[ODOO] Move Michael Krauss (job 17562) from Friday, Aug 21 8:30 AM to Thursday, Aug 20 8:00 AM` — and on tap-yes actually moves the appointment in Odoo. Verified live in confirm mode (proposes + gates, does NOT execute until yes).

**`reschedule_job` WRITE tool (dashboard.py — the LIVE /ask, see [[project_voice_ask_lives_in_dashboard]]):**
- In `WRITE_TOOLS` (confirm-gated: model proposes via `_describe_write`, DJ taps yes → `/execute` → `execute_write_tool`). Args: `so_id` (int, model finds it — never ask DJ), `date` (YYYY-MM-DD PT), `time` (24h HH:MM PT; keep current time if DJ gives only a day, default 08:00), `customer_name`.
- **Execution REUSES the app's canonical engine** `scheduler.schedule_odoo_so(so_id, dt_pt, set_status=True)` — the same one `/api/schedule/reschedule` + the app's ⋯→Reschedule button use (confirms a draft SO, writes date_order Pacific→UTC, flips status to Scheduled). Do NOT reinvent the date/UTC math ([[feedback_reuse_canonical_endpoint]]). Builds `dt_pt = strptime(f'{date} {time}','%Y-%m-%d %H:%M').replace(tzinfo=_PT)` (ZoneInfo America/Los_Angeles). Posts a chatter note.
- `_describe_write('reschedule_job')` reads the SO's current date_order (UTC→PT) so the confirm shows both old and new times.
- **Safety guards (Lead fresh-eyes ①② + Portal chokepoint catch):** the Done/invoiced guard lives at the **CHOKEPOINT `schedule_odoo_so` (scheduler.py f84b2b9)** — it `raise ValueError` if the SO is `x_studio_x_studio_workiz_status=='Done'` or `invoice_status=='invoiced'`, protecting ALL FOUR of its callers (voice `reschedule_job`, the customer-facing `/book/sched/<token>` `_sched_book` which has NO confirm, `/api/schedule/reschedule`, and the slot-offer link) — NOT just the voice tool. Portal caught that my first guard was only in the voice caller, leaving the customer link open (same "guard the chokepoint both paths pass through" lesson as the cross-company leak). Every caller already try/excepts the mover → graceful refusal, no 500. `reschedule_job` (dashboard.py ecd5e5c) ALSO keeps a caller-level pre-guard (Done/invoiced/past/company + nicer voice message + short-circuit) + prompt guidance to target the UPCOMING job. Also: `/ask` route hardcodes `mode='confirm'` server-side (a `mode:'immediate'` body could otherwise run a WRITE with no confirm tap).
- Prompt: the "RESCHEDULING" block tells the model to use reschedule_job (never a Workiz tool). Postpone/duplicate/cancel/new-job are STILL app-screen only (not built as voice tools yet).

**Context — the Workiz 401 that preceded this ([[project_field_voice_history_sanitize]] era):** before this, a reschedule request called the DEAD Workiz `schedule_job`/`update_workiz_field` → `Workiz API 401 Invalid API credentials`. Fixed first by `_DEAD_WORKIZ_WRITE_TOOLS` guard in dashboard.py `execute_write_tool` (returns a friendly "reschedule on the app" message, not a 401) + a prompt block; then this real Odoo-native reschedule_job replaced the app-only fallback for rescheduling specifically. The dead Workiz WRITE tools are still REGISTERED in dashboard.py (guarded) — a full Workiz-tool strip is still pending. Related: [[project_voice_text_draft_tool]], [[project_voice_deep_think_mode]].
