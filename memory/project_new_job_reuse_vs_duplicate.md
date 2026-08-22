---
name: project_new_job_reuse_vs_duplicate
description: "v2_new_job 'Previous jobs' — button is Duplicate this (clones a new Workiz job); a not-done/not-scheduled job also gets Use this job (opens the existing job's Workiz link). recent-jobs now includes draft/sent Submitted jobs + returns workiz_status/link."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-30T01:56:39.953Z
---

# New Job "Previous jobs" — Duplicate vs Use (2026-07-29)

On the Existing-customer New Order path → v2_new_job.html step 2, the "Previous jobs"
list shows the customer's jobs. DJ flagged the old "Use this →" button as misleading:
it never reused anything — it clones the job's property/lines/gate/pricing/job-type into a
brand-NEW job (and, while Workiz is source of truth, New Job creates only a Workiz job via
SA 1338 → Phase 3 builds the Odoo SO). So it was renamed **"Duplicate this →"**.

**New behavior (DJ's spec):** show all jobs, default = duplicate. If a job is **not Done AND
not in the four scheduled statuses** (`Scheduled`, `Send Confirmation - Text`,
`Next Appointment - Text`, `Next Appointment 2 - Text`) **and has a Workiz link**, also show a
primary **"Use this job →"** button that opens that job's existing Workiz link
(`window.open`, fallback `location.href`) — no clone, no new SO. Done jobs and actively-scheduled
jobs get Duplicate only.

**Backend change (`routers/owner/new_job.py`, `/api/intake/recent-jobs`):**
- state filter broadened `['sale','done']` → **`['draft','sent','sale','done']`** so Submitted/
  pending (not-yet-scheduled) jobs surface — those are exactly the reuse candidates. Still
  excludes `workiz_status = 'Canceled'`.
- now also reads + returns `x_studio_x_studio_workiz_status` (→ `workiz_status`) and
  `x_studio_x_workiz_link` (→ `workiz_link`). Frontend uses these to decide Use-vs-Duplicate.

**Frontend (`static/owner/v2_new_job.html`):** `loadRecentJobs` renders a `Status: <wst>` line +
conditional `.prev-open` "Use this job →" button; `openJob(ev,i)` opens `workiz_link`. Existing
`useThis` (the duplicate/template loader) is unchanged, just relabeled.

**Why:** avoid creating duplicate/dangling jobs when a not-done, not-scheduled job already exists
for the customer — pick it up in Workiz instead. See [[project_new_order_parked_surfacing]]
(parked reactivation/re-engagement is a separate dedup on the New Order screen).
