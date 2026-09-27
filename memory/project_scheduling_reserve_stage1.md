---
name: project_scheduling_reserve_stage1
description: Scheduling-reserve Stage 1 — the shared occupied-or-held predicate that makes every slot-finder reserve + duration aware (offers + draft reserves)
metadata:
  node_type: memory
  type: project
  originSessionId: 4a3934c7-cb02-4949-8807-74eee8a68861
  modified: 2026-09-27T05:39:59.180Z
---

**Scheduling-reserve Stage 1 (shipped to main 2026-09-26, Lead re-QC clear + live-pipe verified).** Design: `saunders-render-app/3_Documentation/review/SCHEDULING_RESERVE_DESIGN.md`. Root cause it fixed: reserves were ADVISORY-only — NO slot-finder consulted `wsc.slot_offers` (pending offers) or draft/sent maintenance reserves, and every availability query filtered `state in ['sale','done']` only, so a new offer OR job could land on a reserved/offered time.

**The fix = ONE shared "occupied-or-held" predicate, consulted by every finder:**
- `scheduler.py` → `held_intervals_for_day(date_str)` and `held_intervals_for_range(date_from, date_to)->{ds:[(start_min,dur_min)]}` — return the two occupancy sources the sale/done filter can't see: (a) **submitted/draft maintenance reserves** (`sale.order` state in `('draft','sent')`, workiz_status not Canceled/Postponed, **`company_id in [1,False]`** rule 8) + (b) **pending slot offers** (`slot_offers.list_offers('pending')`). Duration = `x_job_length_min` or `_job_block_min(jobtype)` or SLOT_MIN. **FAIL-OPEN to []/{}** (a hold lookup must never dead-end booking).
- `build_day_plan` unions `held_intervals_for_day()` into its `occupied` reachability set (NOT into `schedule` display) → makes `rank_days`/`best_fit_plan`/`so-suggest`/day-plan + the maint-spawn anchor reserve-aware (they were already duration-aware).
- `booking.py` customer finders (were exact-start-only, offer-blind): new `_free_slots_dur(intervals)` (duration-aware, mirrors `scheduler._reachable`, drive+buffer both sides, SLOT_MIN proxy for the unknown new-job length) + `_held_intervals_range` (lazy import; single source of truth). `_jobs_by_day_geo` now carries `rec['intervals']=[(start,dur)]` (reads `x_job_length_min`+jobtype) and folds held reserves into intervals; `_open_dates_for_city` uses `_free_slots_dur`. `_occupied_by_day` folds held STARTS (provisional-time path, start-granularity).

**Why:** closes the double-book hole where a booking could land on a held/offered time. **How to apply:** any new slot-finder must consult `held_intervals_for_range` (range) — NEVER re-roll a bare `state in ['sale','done']` filter. Two Lead-QC catches that MUST be honored: (1) use the RANGE-batched fn in booking (per-day across ~44 days = 130+ Odoo calls → 429-storm → fail-open drops holds → double-book returns); (2) `company_id in [1,False]` on the draft/sent query or Cheryl/Saunders quotations phantom-hold W&SC slots. Circular import avoided: scheduler imports booking at top, so booking's uses of scheduler are LAZY inside functions.

Stage 2 (next) = maint-spawn single-frequency path (`new_job.py:659` `create_next_maintenance_so`) still does a BLIND `base_dt + timedelta` — replace with a `best_fit_plan` call (now reserve+duration-aware). The cadence path (`_create_cadence_next`) already anchors via `rank_days`. Stage 3 = promote reserve→firm on ACK + auto-ack@36-48h via SERVER-SIDE APScheduler (see [[feedback_durable_watcher_not_session_cron]]).

Live-pipe verify method (reusable): see [[project_livepipe_verify_booking_availability]].
