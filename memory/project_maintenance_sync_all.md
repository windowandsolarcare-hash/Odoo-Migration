---
name: project_maintenance_sync_all
description: "Why Submitted jobs get stuck on the Maintenance/Upcoming list after being scheduled in Workiz, and the 'Sync all from Workiz' button (chunked, frontend-driven) that clears them."
metadata: 
  node_type: memory
  type: project
  originSessionId: 65d82725-62b9-4564-8ede-09606413c213
---

**Built 2026-07-10.** DJ scheduled Rosemary + Pat M in Workiz overnight; Pat dropped off Upcoming (he tapped per-job Sync), Rosemary didn't.

## Root cause — stale Odoo status, no auto-reconcile for Submitted jobs
The Maintenance "Upcoming/Overdue" tabs (`/api/scheduled_sos`) key on **`x_studio_x_studio_workiz_status == 'Submitted'`** + a date window (Upcoming = date_order≥today; Overdue = prior 365d). A job only leaves when that Odoo field changes off 'Submitted'. **Scheduling a job IN WORKIZ does not push the new status back to Odoo by itself.** Only two things update it: Phase 4 (Zapier — unreliable on a manual Workiz UI edit) or DJ's per-job **Sync button** (= `/api/sync_job_from_workiz` → **Odoo SA 955 "Sync from Workiz"**). The **daily-sync cron EXCLUDES these**: its domain requires `state in ['sale','done']` + `invoice_status='to invoice'`, but a Submitted next-job is a DRAFT quotation (`invoice_status='no'`) → never swept. So scheduled-in-Workiz jobs sit on Upcoming with stale 'Submitted' until manually synced. Confirmed live: Rosemary SO 004701 = Odoo 'Submitted' / Workiz SubStatus 'Next Appointment - Text'.

**SA 955 behavior** (verified from its code): updates `x_studio_x_studio_workiz_status` from the live Workiz `SubStatus or Status`, and **confirms a draft** (`if record.state in ('draft','sent'): action_confirm()`) — but that confirm is INSIDE the line-item-mismatch branch (`if _wkz_set != _odoo_set`), so it only fires when Workiz line items differ from Odoo's (they usually do for a freshly-scheduled job). This is exactly what the per-job Sync button runs.

## The fix — "🔄 Sync all from Workiz" button (submitted_jobs.py + maintenance.html)
On the Maintenance screen (Upcoming/Overdue tabs; hidden on "In Workiz"/stranded). Reconciles the tab's Submitted jobs: for each, live `workiz_get`; **only if live status != 'Submitted'** run SA 955 (`ir.actions.server run [955]`). Genuinely-unscheduled jobs (still Submitted in Workiz) are pre-check-skipped → never confirmed by accident. DJ chose an on-demand BUTTON over a cron (wanted control).

### ★ Two design lessons that cost real debugging
1. **Scope to the tab's date window** — a first version had NO date bound → pulled all **570** ever-Submitted jobs (ancient), hit the 400 limit, and sorted so the future-dated jobs DJ wanted (Rosemary, Sept) were past position 400 → MISSED. Fix: `scope=upcoming` (date_order≥today, ~47) | `overdue` (prior 365d), mirroring `api_scheduled_sos`.
2. **Frontend-driven CHUNKS, not a background thread** — a fire-and-forget `threading.Thread` worker STALLED at 21/47 (Render recycles long bg threads mid-run). Rewrote as: `POST /sync_all?scope=` snapshots the job list (id+uuid+name) into `ir.config_parameter render.submitted_sync_all` with a cursor; `POST /sync_all_step` processes 5 jobs/call (2s spacing for the Workiz ~30-call limit) and advances the cursor; the frontend `doSyncAll()` loops step→step (3-retry per chunk) until `done`, updating the status line, then reloads. Short requests can't be killed mid-flight. Snapshot (not offset paging) so the shrinking Submitted set doesn't skip jobs. Verified E2E: 44 jobs → done in 9 chunks (~90s), synced only the moved ones, left 43 Submitted alone.

Endpoints: `POST /owner/api/submitted_jobs/sync_all?scope=`, `POST .../sync_all_step`, `GET .../sync_all_status`. See [[project_customer_jobs_status_selfheal]] (same stale-Workiz-status family, self-heal on read) and [[project_daily_sync_date_window_excludes_old]] (the sync-window gap).
