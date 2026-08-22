---
name: project_status_scheduled_now_confirms
description: "Setting a job's Status to an on-schedule state (Scheduled / Send Confirmation / Next Appointment) now auto-confirms the SO (draft→sale) in brain.py, so it actually appears on the schedule. Fixes invisible \"Scheduled\" drafts."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-11T13:39:58.804Z
---

**Problem (DJ, Van Eychaner 2026-08-11):** DJ duplicated a job via Customer Brain as **Submitted (draft)**, then opened job detail and changed the **Status** dropdown to **Scheduled**. The job then read "Scheduled" but never showed on the schedule. Cause: changing the Status field only WROTE the label (`x_studio_x_studio_workiz_status`) — it did NOT confirm the sale order. The schedule/today builders require `state in ['sale','done']`, so a draft-with-Scheduled-status is invisible.

**How jobs are created (the two paths):**
- **Create from scratch** (`/api/intake/create-job`, new_job.py): ALWAYS a DRAFT, `workiz_status='Submitted'` — "reserved, not on schedule." By design.
- **Duplicate** (`/api/duplicate_job`, dashboard.py): two buttons — "📋 Create as Submitted" → draft; "📅 Create & Schedule" (`schedule:true`) → `action_confirm` → state=sale, on schedule.
- So a from-scratch job (or a duplicate-as-Submitted) is a draft until confirmed.

**Fix (brain.py `brain_job_save` / POST `/api/brain/job`, commit a2f3e76):** after writing `vals`, if `x_studio_x_studio_workiz_status` was set to one of `('Scheduled','Send Confirmation - Text','Next Appointment - Text','Next Appointment 2 - Text')` AND the SO is `state in ('draft','sent')`, snapshot `date_order`, `action_confirm`, then write `date_order` back (confirm resets it to now()). Now the label and the actual state can't disagree — anything you mark on-schedule lands on the schedule.

This is the same save the so_full editor (v2_field.html `saveFullDetails`) posts to. No other path changed; non-schedule statuses (Submitted/Canceled/Done) are untouched.
