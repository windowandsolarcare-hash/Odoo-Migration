---
name: project_personal_time_schedule_desc
description: "Schedule rows for \"Personal Time\" show the job description instead of job type"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Shipped 2026-06-10.** On the field **schedule screen**, any row whose customer is **"Personal Time"** shows the **job description** (wide, spanning to the price) instead of the service-type subtitle. Regular jobs unchanged.

## Detection + data
- Detector: `j.customer === 'Personal Time'` (partner **24177**, "Personal Time, 8401 Maruyama Drive" → split(',')[0] = "Personal Time"). See [[project_personal_time_direct_odoo]].
- Description source: SO field **`x_studio_x_studio_notes_snapshot1`**, which for Personal Time is stored as `"[Job Notes] <text>"` (sometimes `[Job Notes]\n<text>`). Backend helper `_personal_time_desc()` (dashboard.py) strips the `[Job Notes]` prefix. Verified via API 2026-06-10.

## Schedule data flow (IMPORTANT — THREE builders feed the schedule screen)
field.html `loadField()` fetches `/api/dashboard` + `/api/upcoming`; the Past Jobs accordion lazy-fetches `/api/past_jobs`:
- **`/api/dashboard`** → `jobs` (today) → **`tool_get_schedule()`** (dashboard.py ~L517)
- **`/api/upcoming`** → `futureDays` → **`api_upcoming`** loop (~L5193, uses `tasks_by_so_up`)
- **`/api/past_jobs`** → Past Jobs accordion → **`api_past_jobs`** `day_map` builder (~L8382, uses `tasks_by_so`, groups by `date_key`)

ALL THREE now query `x_studio_x_studio_notes_snapshot1` and add `'description': _personal_time_desc(...) if customer == 'Personal Time' else ''`. (The `day_map` builder is the past-jobs one — earlier I mistook it for future days; future days = api_upcoming.)

## Customer tab (added 2026-06-10)
`/api/customer_jobs` also covered. Detection there is by the **resolved customer being "Personal Time"** (the endpoint walks a Property up to its Contact; the Personal Time Contact is **id 23054 'Personal Time'**, Property **24177 '8401 Maruyama Drive'**). NOT by job_type — Personal Time blocks are a MIX of job_type `Personal Time` AND `Dr. Appointment`, so job_type is an unreliable detector. `description` is only populated when `is_personal`. Frontend: the 3 customer-job list `meta` lines use `[(j.description || j.job_type), j.status]` — shows description when present (Personal Time), else job type.

## Frontend (field.html) — THREE schedule row templates
- Today (`renderSchedule`, `openJob(jobs[i])`) and future-days (`openUpcomingJob`): Personal Time → description subtitle (`.job-svc` `white-space:normal`), tags+links suppressed so it spans to the price (`job-name-wrap` is `flex:1`).
- Past Jobs (`renderPastDays`, `openPastJobRow`): swap `svcHtml` to the description; that row already has no tags/links so it spans naturally.
