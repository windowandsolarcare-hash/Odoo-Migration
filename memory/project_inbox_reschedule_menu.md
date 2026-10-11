---
name: project_inbox_reschedule_menu
description: "v2_inbox thread ACTIONS menu now has 🔁 Reschedule — inboxReschedule() resolves the thread's booked SO via /owner/api/followups/job_link and deep-links v2_job.html?open_so=&rs=1 into the canonical Reschedule/Reserve sheet. v2_inbox is a LIGHT host (no _job_detail_panel.js)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T07:20:04.334Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy"; Lead QC-GREEN). DJ ask via Operator (Myra Lane): "Need reschedule on menu in timeline."**

`openInboxActions()` in `static/owner/v2_inbox.html` added `{icon:'🔁', label:'Reschedule — set a new date', run:inboxReschedule}` AFTER "Confirm the appointment", BEFORE "Postpone". (Postpone = un-schedule/PARK, a SEPARATE flow → `/owner/api/inbox/postpone`; Reschedule is distinct.)

`inboxReschedule()`: resolves the thread's current booked SO via the canonical `GET /owner/api/followups/job_link?phone=<CUR.norm>` (same endpoint "Their current job"/`WSCThread.goJob` uses) → deep-links `location.href='/static/owner/v2_job.html?open_so='+so_id+'&rs=1'`. v2_job's boot reads `rs=1`→`openJobRsModal`→the canonical reschedule sheet (→ [[project_reschedule_false_network_error_fix]], whose fix it inherits). No booked job → `_ppToast` fallback ("use Send booking link"), never an empty sheet. Double-tap guard `_rsBusy`.

**Why deep-link, not mount the sheet:** v2_inbox is a `_WSC_LIGHT_HOST` — it does NOT load `_job_detail_panel.js`/`#job-rs-sheet`, so reuse = deep-link to v2_job which already owns that sheet. No parallel path, no new endpoint ([[feedback_reuse_canonical_endpoint]]). Compliant with [[feedback_no_ai_offered_dates_use_link]] (DJ picks a real slot; the confirm is the booked-job exception).
