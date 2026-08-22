---
name: project_daily_sync_date_window_excludes_old
description: "Daily Workiz sync cron only sweeps date_order −7/+90 days, so old past-dated Submitted jobs never sync → blank job_type in Odoo"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e8d15b5-9a20-4187-90d6-6f63266f2498
---

The daily SO↔Workiz sync cron (`_run_daily_sync`, dashboard.py; endpoint `/owner/api/cron/daily_sync`, cron [68]) selects SOs with a **narrow scope** (verified 2026-07-04):
`state in [sale,done]` AND `invoice_status='to invoice'` AND `workiz_status!='Done'` AND has UUID AND **`date_order` within now−7d .. now+90d** (limit 90, 3s/call rate-limit pacing).

**Consequence:** old past-dated open jobs are permanently OUT of scope. Found 85 company-1 SOs (with UUID) whose Odoo `x_studio_x_studio_x_studio_job_type` was blank — **0 of 85 fell inside the −7/+90 window** (84 were `to invoice`, so it's the DATE window excluding them, not the invoice filter). 61 were Submitted status. These are old Submitted quotes that never progressed to Done, so Phase 4 never filled job_type and the daily cron can't reach them.

**Symptom this caused:** online booking portal (`/api/me`, booking.py) showed the filler word "Service" for job 3787 because Odoo's job_type was blank even though Workiz had `JobType='Windows Inside & Outside Plus Screens'` since Feb. DJ's manual broad sync run 2026-07-04 22:53 finally filled some (3787), but ~85 remained.

**Key facts / corrections:**
- The cron is HEALTHY and running CURRENT code — ran 2026-07-04 09:25 PDT, 49 SOs, 0 errors. Live deployed dashboard.py (12,679 lines) has the casing fix (`get('pricing')` lowercase, L9491). NOT a "cron running stale code" problem.
- `_sync_so_with_workiz` DOES map Workiz `JobType` (capital, correct casing) → Odoo `x_studio_x_studio_x_studio_job_type`, and fills blanks (`_sync_field` writes when Workiz has a value and Odoo differs). So a per-SO sync of any of the 85 fixes it — they're just never selected.
- `C:\Users\dj\wsc-repo` local copy is STALE (had capital `'Pricing'`); always trust the live GitHub file.

**Fixes (discussed w/ DJ, not all done):** (1) one-time backfill job_type from Workiz for the ~85 blanks; (2) portal "recent visits" should show only `workiz_status='Done'` real visits, not Submitted quotes (drops the misleading "Service" row for 3787 entirely — matches the CLAUDE.md Done-jobs rule); (3) post-Workiz, New Job/booking/Phase-3 successor must SET job_type at creation since there's no Workiz to backfill from. See [[project_workiz_sync_field_casing.md]] [[feedback_done_jobs_definition.md]].
