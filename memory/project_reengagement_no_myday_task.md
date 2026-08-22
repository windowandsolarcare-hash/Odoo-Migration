---
name: project_reengagement_no_myday_task
description: "Re-engagement is DATA-DRIVEN via the outreach tab (no My Day task needed); the 16 legacy \"Re-engagement:\" My Day tasks were cleared 2026-07-12"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Design (confirmed 2026-07-12):** re-engagement no longer needs a My Day task. The **outreach "Re-engage" tab** (`/owner/api/outreach/list?flow=reengage`, `outreach.py` `classify_customers()` + `_reeng_launch_partners()`) is **fresh + bucket-based every load** — its own comment: *"no deletable task … self-healing: qualify → you're on the list, no task required."* A customer surfaces when their last-visit + frequency cycle makes them DUE (not snoozed/booked/recently-texted, not DNC, not maintenance, not lapsed>12mo).

`classify_customers()` buckets EVERY non-property W&SC contact mutually-exclusively: no last visit → **Lead**; last visit >12mo & no upcoming job → **Reactivation**; active & maintenance → **Maintenance**; active & on-request → **Re-engagement**. So every customer is covered by SOME data-driven flow (re-engage tab / reactivation tab / Command-Center maintenance-overdue) — no task required.

**✅ THE TAP IS ALREADY CLOSED.** The auto-creator was **`create_followup_activity()` in `zapier_phase5_FLATTENED_FINAL.py`** (Odoo-Migration repo) — creates a "Re-engagement:" project.task per Done job (name L580, `<b>Last Service:</b>` desc, project_id=False+user DJ, tag 22, deadline ~frequency out). It was **DISABLED 2026-07-07** with an early `return {'success':True,'todo_id':None,'disabled':True}` (original body preserved below it; caller skips the invoice-link when todo_id is None). Gary Marsalone's task (created 7/7 20:06) was the LAST one, made minutes before the disable deployed. **Verified 2026-07-12: ZERO "Re-engagement:" tasks created after 7/7.** So Phase 5 no longer makes them — nothing to change. (Note: the Render app's `create_todo` AI tool CAN still make one on demand, but it's manual, not automatic.)

**Cleanup 2026-07-12:** the 16 lingering active "Re-engagement:" tasks (all project_id=False → showed on My Day) were verified — each falls into a live data flow (6 re-engage tab, 6 maintenance, 4 reactivation; 0 DNC, 0 lead) — then all marked `state='1_done'`. My Day is now clean of re-engagement tasks. See [[project_done_stage_state_mismatch]], [[project_reengagement_autopilot]], [[project_waiting_screen]].
