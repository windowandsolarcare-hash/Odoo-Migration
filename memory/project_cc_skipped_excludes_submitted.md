---
name: project_cc_skipped_excludes_submitted
description: "Why a confirmed past job can be missing from the Command Center \"Skipped — reschedule\" list"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2e08d0c0-852b-4eba-bb29-83bbb075a3a6
---

**Command Center "🔁 Skipped — reschedule" list (schedule_hub.html `_isSkipped()` / `loadNeed()`) EXCLUDES any job whose Workiz status is `Submitted`** — line: `if(st==='Submitted') return false;` with comment "next-job, not a missed appt". `st` = `j.status` = `x_studio_x_studio_workiz_status` (set by calendar.py `/api/calendar_jobs`, which returns `status` from that field).

**Why this bites:** the Skipped list is built ONLY from `/api/calendar_jobs` (past 90 days), and calendar_jobs already filters `state in ['sale','done']` — so every job it returns is a CONFIRMED, scheduled job. A confirmed job that still shows Workiz status "Submitted" is NOT a draft quote — it's a real scheduled job whose status went stale (never advanced past Submitted after confirm). The Submitted guard was meant to hide Phase-3 DRAFT quotations (state=draft, which never reach calendar_jobs anyway), so inside this list the guard only ever drops stale-status confirmed jobs.

**Other `_isSkipped` gates (all must pass):** dk < today; not `paid`; status has no "done"; not Sunday; job_type not in [Personal Time, Reactivation Lead, Quote, Touch up]; name not /personal time|test/. Also dropped if already `seen` in the Overdue/Upcoming buckets (`/api/scheduled_sos`). Window = last 90 days only.

**Concrete case (2026-07-01):** SO 004440 (Scott Cunningham) — state=sale, date_order 2026-06-20 (Sat), unpaid, job_type "Windows Inside & Outside Plus Screens", Workiz status "Submitted" → missing from Skipped SOLELY because of the Submitted guard. Query found **18** confirmed+Submitted+past jobs in the last 90d (~16 after Personal Time/Reactivation exclusions), incl. a suspicious cluster of **10 jobs all dated 2026-04-05 with BLANK job_type** (looks like a bad batch — verify before surfacing).

**★ RESOLVED 2026-07-01 (commit d7f88595, option b).** Removed the `if(st==='Submitted') return false;` line in `_isSkipped`. Now past confirmed Submitted jobs DO show on the Skipped list. Safe because the two upstream locks stay: the in-function `dk>=isoPlus(0)` date guard (future jobs never reach it) + calendar_jobs is confirmed-only (drafts never reach it) — so the only jobs newly surfaced are exactly past+confirmed+Submitted.

**★ WHY DJ FLIPS JOBS TO "Submitted" (the real business reason — key context):** Submitted is DJ's **manual kill switch for a specific job**. When he decides to skip/postpone a job or tells a customer "not tomorrow," he flips that job's Workiz status to Submitted to STOP Phase-4 customer automation (confirmation text, gate-code reminder, "see you tomorrow"). So a past confirmed Submitted job = a job HE intentionally skipped and still owes a reschedule = *exactly* what the Skipped list is for. Hiding them was the bug. **The Skipped list is display-only — it sends nothing to customers, so surfacing these does NOT re-trigger any automation or counter what DJ told the customer.** Phase-4 automation is separate code, still fully killed by the Submitted flip. This fix only changed what shows on DJ's own CC screen.

**How to apply:** If a confirmed past job is missing from CC Skipped now, it's NO LONGER the Submitted guard (removed). Check the other gates: `paid`, Sunday, job_type in [Personal Time, Reactivation Lead, Quote, Touch up], name /personal time|test/, or already `seen` in Overdue/Upcoming. NOTE the 10-job 2026-04-05 blank-job_type cluster will now appear — if it's a bad batch, clean the data, don't re-add a filter. See [[project_cc_reschedule_via_workiz]] [[project_command_center]].
