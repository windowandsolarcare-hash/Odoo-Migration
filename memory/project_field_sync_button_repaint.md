---
name: project_field_sync_button_repaint
description: "The field-app open-job-detail 🔄 Sync button must re-render the detail's line items after syncing — loadField() alone only refreshes the schedule list, not the open panel. Regression-prone; DJ has reported it \"got lost\" more than once."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Field app Sync button → must repaint the open detail's line items (2026-06-09)

**The recurring complaint:** the 🔄 Sync button (upper-right of the open job detail, `#ap-sync-btn` → `syncFromWorkiz(so_id)`) "doesn't sync the line items." DJ has reported this multiple times — it keeps getting lost (likely stale-push regressions [[feedback_regression_guard_pushes]]).

**Root cause (NOT the backend):** Sync calls `/api/sync_job_from_workiz` → Odoo **server action 955**, which correctly pulls Workiz `LineItems` into the SO when they differ (cancel→draft→delete→recreate; refuses if invoice posted). That part works. The bug was purely frontend: `syncFromWorkiz` only called `loadField()`, which refreshes the global `jobs` array + schedule rows but **never re-renders the open detail panel** you're looking at. So the SO updated in Odoo but the on-screen line items (`#pay-lines`, rendered from `activeJob.lines` in `openJob()`) stayed stale → looked like sync did nothing. (If Workiz items already match the SO, 955 logs "Line items already match" and there's genuinely nothing to change — that's correct, not a bug.)

**Fix (field.html, commit 75c295f9):** after `await loadField()`, `syncFromWorkiz` finds the fresh job in `jobs` (falls back to `/api/so_history` for non-today jobs), updates `activeJob.lines`/`amount`, and calls `_repaintActiveLines()` — a surgical repaint of `#pay-lines` + `#pay-amount` only (NOT a full `openJob()` re-render, so it doesn't reset typed memo / pending photos / running timer).

**If it breaks again:** verify `syncFromWorkiz` still `await`s loadField AND calls `_repaintActiveLines` on the active job. `loadField()` sets `jobs = data.schedule.jobs` (each job carries `.lines` = `[{name, subtotal}]`); `/api/so_history` returns the same `lines` shape.

**Still open (DJ's call):** line-item DESCRIPTIONS (e.g. Workiz "Tape and clean 6 cameras" on Construction Cleanup) are NOT synced — 955 only carries name/qty/price.
