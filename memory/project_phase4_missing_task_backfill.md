---
name: Phase 4 missing task backfill
description: Phase 4 skips task sync when confirmed SO has 0 tasks — needs backfill path to create tasks directly via API
type: project
---

Phase 4 task sync (function `sync_tasks_from_so_and_job`) only UPDATES existing tasks. When it finds `tasks_found=0` on a confirmed SO, it logs "No tasks found linked to this SO's order lines (sale_line_id in line_ids). Task sync skipped." and returns early.

**Root cause of gap:** Tasks are normally created by Odoo's `action_confirm()`. If an SO was created confirmed (historical import, Phase 4 delegation with skip_confirm) without tasks, they never get created.

**Example:** Dianne Hourscht SO 003918 / UUID F7NBU3. Created Feb 12 2026, confirmed, no tasks ever created. Phase 4B ran Apr 4 2026, found 0 tasks, skipped.

**Fix implemented 2026-04-04:** In Phase 4, after `sync_tasks_from_so_and_job` finds `task_ids=[]` on a confirmed SO in a scheduling status, a backfill path runs:
- Get the SO's order line IDs
- For each order line, create a `project.task` directly via Odoo API with:
  - `name`: "{CustomerName} - {City}" (same format Phase 3 uses)
  - `project_id`: DEFAULT_PROJECT_ID (2)
  - `sale_line_id`: order_line_id (this is what links task to SO for future Phase 4 sync)
  - `user_ids`: tech from Workiz job if available
  - `date_deadline`: job datetime UTC
- Log "[OK] Backfilled N task(s) for confirmed SO with no existing tasks"

**Why not cancel/draft/confirm cycle:** Risk of failing if SO has invoice/payment linked.

**How to apply:** Next session, add backfill block in Phase 4 immediately after the early return at line ~330 where tasks_found=0. Only trigger when SO state='sale' (confirmed) AND is_task_trigger_status() is True.
