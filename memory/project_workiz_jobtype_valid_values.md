---
name: project_workiz_jobtype_valid_values
description: "Valid Workiz JobType values (must match EXACTLY or Workiz 400s). \"Window Cleaning\" is NOT valid — it was the old default in field.py and caused job-create failures. Read before setting JobType anywhere."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Workiz JobType — valid values (verified 2026-06-09)

Workiz `JobType` must match an **existing configured value EXACTLY** or the API returns `400 "Error Validating Fields" {'JobType': 'Could not find matching value for JobType - X'}`.

**There is NO "Window Cleaning" job type.** That was the bogus default baked into `field.py` (create_workiz_job/schedule_job tools + tool description "e.g. Window Cleaning") — it 400'd every job create that fell back to the default. Fixed 2026-06-09 (commit 20b3b740): default → `'Windows Inside & Outside Plus Screens'`, tool description + SYSTEM_PROMPT now list valid values.

**Valid JobType values** (from Odoo `x_studio_x_studio_x_studio_job_type` distinct + live Workiz jobs; count = how common):
- `Windows Inside & Outside Plus Screens` (most common — generic-window default)
- `Outside Windows and Screens`
- `Solar Panel Cleaning`
- `Combination of Services`
- `Inside Only Windows`
- `Windows Inside & Out - No Screens`
- `Gutter - Inspect and Clean`
- `Touch up`
- `Screen(s) - New` · `Screen Repair`
- `Pressure Washing`
- `Commercial Inside & Out` · `Commercial Outside`
- `Service` · `Repair` · `Quote`
- Internal (not customer service jobs): `Reactivation Lead`, `Personal Time`, `Dr. Appointment`

**Note:** `JobType` (the categorical service, exact-match list) is DIFFERENT from `type_of_service_2` (free-ish: 'Maintenance', 'On Request', etc.). Don't confuse them. [[project_lead_source_valid_values]] [[project_personal_time_direct_odoo]]
