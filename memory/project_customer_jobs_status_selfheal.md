---
name: project_customer_jobs_status_selfheal
description: "customer_jobs self-heals stale Workiz status on OLD non-terminal jobs (the daily-sync −7/+90 window never revisits them) — fixed reactivation-lead jobs showing 'Scheduled' when Workiz says 'Submitted'."
metadata: 
  node_type: memory
  type: project
  originSessionId: 65d82725-62b9-4564-8ede-09606413c213
---

**Fixed 2026-07-09.** DJ opened a reactivation lead's job history (Cheryl Moody) and the top job read **"Reactivation Lead · Scheduled"** — but in Workiz that job's real status is **Submitted** (it was unscheduled/parked). He was right.

**Root cause = stale Odoo field, not wrong display logic.** The app correctly reads `x_studio_x_studio_workiz_status` (same field that gives "Done" on completed jobs). But that field is only refreshed by the daily Workiz sync, which sweeps `date_order` within **−7/+90 days** only (see [[project_daily_sync_date_window_excludes_old]]). An OLD job (SO 004254, date_order 2026-03-17, UUID EPX7TJ) never re-syncs, so its status froze at 'Scheduled' from months ago while Workiz moved it to 'Submitted'. Verified live: Workiz `Status='Submitted' SubStatus=''`, Odoo field `='Scheduled'`.

**Fix (dashboard.py `api_customer_jobs`, after the jobs-list build):** a self-healing refresh pass —
- Skip **terminal** statuses (`done`/`canceled`/`cancelled`) — they never drift, so NO Workiz call for normal customers (keeps the hot endpoint fast).
- Skip jobs whose `date_raw >= today−7` — those are inside the daily-sync window and already fresh.
- For the remaining OLD non-terminal jobs (usually just the 1 reactivation-lead job): `workiz_get('job/get/{uuid}/')`, derive `SubStatus or Status` (the canonical mapping, same as `_sync_so_with_workiz` L9587 and `get_job_details` L544), correct the displayed `status`, AND `write()` it back to Odoo so it heals **permanently**.
- **Capped at 4 Workiz GETs per request** to respect the ~30-call/429 rate limit.

★ Did NOT reuse `_sync_so_with_workiz` for this — it's heavy (full line-item cancel→draft→delete→confirm) and HARD-FAILS with "No tech assigned" on a $0 reactivation lead. Status-only lightweight refresh is the right tool.

Verified E2E: after deploy, `/api/customer_jobs?partner_id=23600` returned SO 004254 status='Submitted' and the Odoo field itself is now 'Submitted' (self-healed). `workiz_get` works from Render with no User-Agent (the UA-or-403 rule is LOCAL-only).

Terminal-status truth: **Done / Canceled** never change in Workiz; everything else (Scheduled, Submitted, Pending, In Progress, Send Confirmation - Text, Next Appointment…) can drift and is a refresh candidate when old. Reuse this "terminal vs drift" split anywhere else that displays a possibly-stale Workiz status off an old SO.
