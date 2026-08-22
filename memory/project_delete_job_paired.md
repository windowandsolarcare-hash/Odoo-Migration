---
name: project_delete_job_paired
description: The safe job-delete process now exists in TWO places that must stay in sync — Render Claude tool (field.py delete_workiz_job) AND the field-app UI endpoint (dashboard.py /api/delete_job). Read before changing either.
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Job delete — PAIRED CHANGE (2026-06-09)

DJ wanted a "🗑 Delete Job" option in the field app's job 3-dot menu (open job detail + per-row, both via `toggleJobMenu` in field.html). It calls a NEW REST endpoint `POST /owner/api/delete_job` (no AI, no token cost) added to **dashboard.py**.

**The safe delete process (the "certain way" — same in both places):**
1. Find the linked Odoo SO by `x_studio_x_studio_workiz_uuid`.
2. **REFUSE if any invoice is linked** (`invoice_ids`) → return blocked, tell DJ to cancel/refund first. Never delete a job with an invoice.
3. Delete linked `project.task` records first (they reference the SO via `sale_order_id`).
4. If SO `state in ('sale','done')` → `action_cancel` first (Odoo constraint), then `unlink` the SO.
5. **Delete the Workiz job LAST** via `workiz_post('job/delete/{uuid}/', {})` — so an Odoo failure aborts before the Workiz job is gone.

**⚠ PAIRED CHANGE — keep these two in sync (do BOTH or neither):**
- `routers/owner/field.py` — Render Claude tool `delete_workiz_job` handler (~line 1374). This is the original/source.
- `routers/owner/dashboard.py` — `api_delete_job` / `POST /api/delete_job` (after `api_sync_job_from_workiz`). UI path. Mirrors field.py exactly, returns JSON `{ok, blocked?, partial?, error?, message}`.

**Frontend callers of `POST /api/delete_job` (all keyed by Workiz `uuid`):**
- field.html `deleteJobFromMenu(btn)` — confirm dialog, `_jobDeletePending` double-tap guard, NOT offline-queued (destructive). On success closes the open detail if it's the deleted job + `loadField()`. `data-uuid`.
- **calendar.html `cancelJob(soId, dk, uuid)`** (added 2026-06-18, commit 75ac803b) — the Schedule Calendar day-view 🗑 button. **WAS Odoo-only** (`/api/cancel_so/{soId}`) which left the Workiz job behind — DJ reported it; fixed to call `/api/delete_job` with `{uuid}` when a uuid exists, falling back to `cancel_so` only for Odoo-only SOs (no Workiz link). So a calendar delete now removes BOTH systems.

Why duplicated rather than shared: avoided refactoring the working Render Claude tool (regression risk on a destructive path). If the process changes, update BOTH. [[session_may22_summary]]
