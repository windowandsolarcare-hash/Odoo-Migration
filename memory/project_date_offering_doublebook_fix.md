---
name: project_date_offering_doublebook_fix
description: The 3-layer fix that stops the voice/text assistant from offering appointment days that double-book — and the deferred merge of the old find_next_opening engine into rank_days.
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T23:04:05.620Z
---

The LIVE `/owner/ask` text-rewrite/date-offering path used to invent appointment openings from the model without checking the live schedule → real double-books. Concrete incident (2026-09-09): DJ's Nick Conway postpone draft offered Sep 17/23/24 — two hard conflicts (Jeff Barber Sep 23 8:00, Lisa Scarpelli Sep 24 9:30). DJ didn't send; Operator redid it correctly. Lead approved building all 3 layers.

**The fix (shipped 2026-09-09, both files deployed via gh api):**
- **L1 — `routers/owner/sms.py` `_grounded_context`:** added `_implies_scheduling(text)` (keyword cues: reschedul/postpone/move/when works/available/offer/slot/etc., `_SCHED_CUES`). When the steer OR thread implies scheduling, FORCE `'availability'` into `data_needed` so `_inbox_ai_facts` injects the REAL open days (`new_job.open_days_for_partner` → `scheduler.rank_days`). Before this, Haiku triage only listed `data_needed` for a 'respond' intent, so reschedule/postpone drafts carried NO availability facts and the drafter invented dates. `_grounded_context` is the single live funnel for every drafter (voice `text`/open_text_draft, ✨ rewrite, /suggest, /redraft) — the inbound `_inbox_ai_facts` branch at sms.py:1051 is DEAD (hard `return` at :1050).
- **L2 (the most important — the safety net) — `routers/owner/dashboard.py` `reschedule_job` execute (execute_write_tool ~1305):** BEFORE `scheduler.schedule_odoo_so`, run `scheduler._job_fits_at(date_str, start_min, new_dur, exclude_so_id=so_id)`. `new_dur` = SO `x_job_length_min` or `scheduler._job_block_min(job_type)` (90m default) so overlap detection runs even with no explicit length. On no-fit: DON'T write; return a message with the soonest genuinely-open times from `scheduler.api_scheduler_so_suggest(so_id)` (parse `_sg.body` JSON — it returns a JSONResponse). Fail-open on any error (never blocks). Makes a fabricated date physically unable to become a double-book.
- **L3 — dashboard.py SYSTEM_PROMPT:** added to TEXT A CUSTOMER ("NEVER invent an appointment day/time in a text — put the ASK in `intent`, not a date; the drafter is fed real open days") + the RESCHEDULING paragraph ("reschedule_job now conflict-checks and REFUSES to book over another job — relay the open times it offers, never assert a slot is free unless a scheduler tool said so").

Canonical engine throughout = `scheduler.rank_days` (route-aware + conflict-checked via `build_day_plan`). `_job_fits_at` returns `(fits, warn)` and is advisory-only elsewhere; here it's the gate.

**DEFERRED (Lead-approved to defer):** `dashboard.py find_next_opening` → `_find_scheduling_openings` (dashboard ~3788) is a SEPARATE, OLDER scheduling engine with its OWN `CITY_SCHEDULE` constant, parallel to `scheduler.rank_days`. It should be merged into `rank_days` so there's ONE slot/route source of truth, but that merge was deferred out of this fix to keep it surgical. Until merged, two engines can disagree — if you touch scheduling suggestions, prefer `rank_days`/`api_scheduler_so_suggest` and treat `_find_scheduling_openings` as legacy. See [[feedback_reuse_canonical_endpoint]].
