---
name: project_hr_attendance_unlink_context
description: "Deleting/editing hr.attendance over XML-RPC fails with an enterprise work-entry addon crash (\"unhashable type: 'list'\") UNLESS you pass context {'tracking_disable': True}."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-21T20:30:31.799Z
---

**Discovered 2026-08-21 (deleting DJ's stray 19-min payroll shift).** `hr.attendance` `unlink` (AND `write`) over XML-RPC blows up server-side inside the enterprise addon `hr_work_entry_attendance/models/hr_attendance.py:126` with `TypeError: unhashable type: 'list'` (at `Domain("employee_id","in",self.employee_id.ids)` → `field_cache[record_id]`). It's the work-entry regeneration override choking, not a bad call — plain `unlink([id])` is correctly formed.

**FIX — pass context `{'tracking_disable': True}`:** `execute_kw(DB,UID,KEY,'hr.attendance','unlink',[[att_id]],{'context':{'tracking_disable':True}})` succeeds cleanly (skips the buggy work-entry recompute). Tried first without context → crash; `{'tracking_disable':True}` worked on the first try. (Other guesses `no_work_entries` / `hr_attendance_bypass` are NOT needed — `tracking_disable` alone did it.)

**How to apply:** any time Lead-side code deletes or edits an `hr.attendance` (payroll clock) record via RPC — stray shift cleanup, shift corrections — include `context={'tracking_disable': True}`. Verify after: `search_count([['id','=',att_id]])==0`.

**Context (payroll model facts):** clock = `hr.attendance`; fields `employee_id` (m2o hr.employee), `check_in`/`check_out` (UTC datetime; `check_out==False` = open shift), `worked_hours` (computed float). DJ = `hr.employee` id **1** ("Daniel J Saunders"); other employees: 2 Danny Saunders, 3 David Osuna. The app's clock-in endpoint = `routers/owner/timeclock.py` `/api/payroll/clockin_crew` (creates hr.attendance); status bar = `/api/payroll/status` (open attendance → "Clocked in since"). See the zero-checked-still-clocks-in bug: [[[project_zero_crew_clockin_bug]]] (client fallback substitutes DJ's id when no crew checked).
