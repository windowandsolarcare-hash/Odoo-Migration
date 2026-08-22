---
name: project_workiz_end_before_start_400
description: "Workiz job create returns HTTP 400 if JobEndDateTime <= JobDateTime (end at/before start). New Job's start dropdown left a stale earlier end -> 400 -> no job. NOT a line-item issue."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# Workiz rejects end-before-start with 400 (New Job silent fail, 2026-07-02)

**Symptom:** DJ booked a New Job (Elsa Sandvold, 78770 Falsetto Dr Indio, Pressure Washing, $125) — no Workiz job got created. DJ assumed the LINE ITEM caused it. It did NOT.

**Root cause:** Workiz's job-create API returns **HTTP 400** when `JobEndDateTime` is <= `JobDateTime` (end at or before start). The failing payload had `JobDateTime 2026-07-03 12:30:00` but `JobEndDateTime 2026-07-03 11:00:00` (end 90 min BEFORE start). SA 1338 got the 400 → `[NEW-JOB] SA1338 returned no Workiz uuid: {... 'create_status': 400 ...}` → `/owner/api/intake/create-job` returned 500 → nothing created. Line items (`next_job_line_items` note) were in the payload and are irrelevant to creation.

**How the bad end happened:** new_job.html has separate `#job-start` / `#job-end` `<select>`s (initial defaults 09:00 / 11:00). Tapping a "Pick a time" day-slot (`pickNJSlot`) sets BOTH (end = start+90). But changing the **Start dropdown** (`onchange="S.timeManuallySet=true;njRedrawMap()"`) updated start only, leaving end at the stale 11:00 default → start 12:30 / end 11:00.

**Fix (both, commits 9cd2ca0 + 3f2ddf9):**
- Backend `new_job.py`: GUARD before building JobEndDateTime — if `end_min <= start_min`, force `end = start + 90` (recompute end_time + job_len_min). Prevents the 400 no matter what the client sends.
- Frontend `new_job.html`: added `njSyncEnd()` on the Start dropdown onchange — if End is empty or <= Start, set End = Start + 90 (mirrors the slot picker).

**★ Debug method that nailed it:** Render logs. `mcp__render` (workspace `tea-d78l9fqdbo4c7388n9og`, service `srv-d78le0fkijhs738dsli0` = wsc-field-assistant): `list_logs` type=`app`, text filter `["NEW-JOB","1338","Traceback",...]` printed the full failing Workiz payload + `create_status 400`. For "did the booking work / why did it fail" questions, pull the app logs — they show the exact payload and status. Also verified via Workiz API `job/all/?start_date=` (GET, needs `User-Agent` header) that no job was created that day. See [[project_new_order_tech_field]] [[project_job_end_time]].
