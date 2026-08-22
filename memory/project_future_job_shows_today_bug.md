---
name: project_future_job_shows_today_bug
description: "Fixed — future jobs opened in the field detail showed TODAY's date instead of their real date (missing date_raw)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
---

**BUG (fixed 2026-07-01): a FUTURE job opened in the field job-detail panel showed TODAY's date, not its real scheduled date.** Symptom: DJ opened Donna Parrish's job (SO 004518, genuinely scheduled Jul 22), the detail header read "Wed, Jul 1" (today), so he thought it was a today job and couldn't find it in her Customer Brain (which correctly listed it under Jul 22) → thought it was missing/orphaned. It was NOT missing (customer_jobs returned it fine) and NOT a Workiz↔Odoo desync (both agreed Jul 22). Recurring across all future jobs.

Root cause: `/api/upcoming` (and `/api/past_jobs`) job dicts carried NO `date_raw` — the date lived only in the day-grouping key. So when a future job opened, `_apHeaderWhen(job)` (field.html) found no `job.date_raw` and hit its fallback `if(!draw && t) draw = TODAY`, stamping today's date on it.

Fix:
- dashboard.py: new `_pt_date(date_order_utc)` → Pacific 'YYYY-MM-DD'; added `'date_raw': _pt_date(so.get('date_order'))` to the `api_upcoming` + `api_past_jobs` job dicts (today builder already effectively = today, fine).
- field.html `openJobById`: futureDays/pastDays cache hits now set `_fj.date_raw = _fj.date_raw || _d.date`; the so_history fallback now prefers the LIVE SO date (`date_raw: d.so.date || dateRaw`) over the (possibly stale) URL `date_raw` from the CC card.
Lesson: any job payload the detail panel can open MUST carry `date_raw` — the `_apHeaderWhen` today-fallback masks a missing date as "today". See [[project_job_end_time]] (the length/end work that touched the same builders).
