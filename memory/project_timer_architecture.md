---
name: project_timer_architecture
description: "Field app timer: localStorage start → POST /api/timer/log on stop → ir.config_parameter timer.so.{so_id}. Crew cost from hr.employee.hourly_wage. READ before touching timer code."
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

## Timer Architecture (as of 2026-05-23)

### Storage
- **Active timer**: `localStorage['wsc_timer']` = `{so_id, start_ms, employee_id}` — written on Start tap, removed on Stop
- **Permanent records**: `ir.config_parameter` key `timer.so.{so_id}` = JSON array of completed sessions
- **Crew snapshot**: `ir.config_parameter` key `crew.today.YYYY-MM-DD` = `[{id, name}]` — set by clockin_crew "Let's Go"

### Endpoints (timeclock.py)
- `POST /owner/api/timer/log` — body: `{access_code, so_id, start_iso, stop_iso, duration_min, employee_id?}`
  - Reads crew from `crew.today.YYYY-MM-DD`
  - Reads `hr.employee.hourly_wage` for each crew member
  - Writes record to `timer.so.{so_id}`, posts chatter on SO
  - Returns `{ok, record, total_labor_cost}`
- `GET /owner/api/timer/records?so_id=X` — returns records array for display

### Labor Cost
- Rate source: `hr.employee.hourly_wage` (Odoo standard field, not standalone config)
- DJ = $30/hr, Danny = $25/hr (as of 2026-05-23)
- Both calculated per session; `crew[]` array in record has per-person breakdown
- Rate is snapshotted at Stop time — historical accuracy even if rates change later

### employee_id handling
- `employee_id` is OPTIONAL in `/api/timer/log`
- Fallback chain: crew list first member → employee ID 1 (DJ)
- **Why optional**: DJ's access code `owner` doesn't return `employeeId` from `whoami`, so `_fieldGpsEmpId=null`

### UI (field.html)
- `wsc_timer` localStorage: instant Start (no network), single API call on Stop
- `renderTimerBtns('idle'|'running'|'none')` — controls Start/Stop/disabled
- `#timer-start-label` shows "▶ Started 10:40 AM" when running
- `refreshTimerDisplay()` fetches `/api/timer/records` and calls `renderTimerLog()`
- `renderTimerLog()` shows per-crew breakdown + total cost per session
- `#timer-gate-hint` in timer card header — shows gate code without scrolling

### ONE TIMER AT A TIME (single `wsc_timer` key — guaranteed, 2026-06-10)
- `wsc_timer` is ONE localStorage key → system literally cannot track two timers. Starting job B overwrites job A's slot.
- **Looking at a job does NOT stop a running timer** (2026-06-10 — DJ previews the next job while timing the current). `openJob` only resets the VIEW; the running timer stays in `wsc_timer` in the background and its clock resumes when you reopen that job. (The old openJob auto-stop-on-open was REMOVED — that was the wrong trigger.)
- **`doStartTimer()` is the SOLE stop trigger:** pressing Start on job B stops+logs any timer still running on a different job (`/api/timer/log`), THEN starts B. So one timer at a time, A always recorded, never orphaned.
- **The "job A still running in the background / multiple timers" perception was an ILLUSION** caused by the leftover green `#field-status` "▶ Timer started" banner persisting on job B. The actual timer was already stopped. Fixed 2026-06-10: `openJob` now calls `hideStatus(); hideTimerMsg()` so the banner + result msg clear on job switch.
- Banner clearing history: only cleared on Stop (Jun 8, commit 7848381f); never on job-switch until 2026-06-10. The openJob timer-reset code was byte-identical Jun-5→Jun-10 — this was a pre-existing gap, NOT a fresh regression.

### DO NOT USE for timer records
- `hr.attendance` — payroll clock-in/out (OwnTracks writes here)
- `account.analytic.line` — billable client hours (wrong use case)
- `project.task` timesheet timers — tied to tasks that get deleted
