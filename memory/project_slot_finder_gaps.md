---
name: project_slot_finder_gaps
description: "Slot suggestion has 3 gaps (2026-08-15): AI drafter (open_days_for_partner, day-level) ≠ reschedule modal (_find_scheduling_openings, route-optimized) on TIME; no offered-slot tracking (double-offer); finder ignores x_job_length_min (fixed 90 min)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-17T05:40:59.512Z
---

**Two DIFFERENT slot-suggestion engines → they disagree on TIME (same days).**
- **Reschedule modal** ("Best for your route") = `field.py _find_scheduling_openings` (tool name `find_next_opening`): route-optimized, returns day + best time + mileage.
- **AI text drafter** (inbox replies / reminder drafts) = `new_job.open_days_for_partner(partner_id, 3)` (called from sms.py `_customer_context` L294 + `_inbox_brain` L653): DAY-level only, applies a generic time (~11:00). So a drafted text offers the right DAYS but not the route-best TIME. (Larry Clarke 2026-08-15: text said Fri Aug 21 @ 11:00, modal said 9:30 for the same day.) Fix = point the drafter at the route finder.

**No OFFERED-slot tracking → double-offer + forget.** Both finders only know about BOOKED jobs (the calendar's per-day counts). Slots DJ (or the AI) has OFFERED but not yet booked are invisible, so the same slot gets offered to two people and DJ forgets he floated it. Fix = a "Pending Offers" store (`ir.config_parameter wsc.slot_offers`) written on every slot-text, consumed (exclude/flag) by both finders, auto-expiring after **48 hours** (DJ 2026-08-15), + an "awaiting reply" surface. **★ An OFFER ≠ a BOOKING (DJ 2026-08-15):** scheduling/confirming a job via an app tool (reschedule modal, booking) BOOKS the slot (occupied, already tracked) — NOT a pending offer. A pending offer = DJ floated 2+ TENTATIVE times and nobody booked yet — almost always a text (mostly freehand). The tell: multiple times + "which works?" = offer; ONE locked time = confirmation (leave alone). **Detection** = AI-parse the OUTBOUND text at the send funnel for multi-option offers (resolve relative dates), one-tap confirm so a bad parse can't wrongly block a slot; the AI-drafted "3 options" case is exact (AI knows what it wrote). When one option gets booked, the other held slots free.

**★ SHIPPED 2026-08-16 — item-3 Option A (ADVISORY, additive).** `scheduler.py so-suggest` now reads the target SO's `x_job_length_min` and tags each `best`/`option` with `fits:bool` + `warn:str` via new helper `_job_fits_at(date,start,new_dur,exclude_so_id)` (warns "overlaps <name>" / "runs past 5pm" = WORK_END_MIN). Only fires when a length is set. `v2_field.html` reschedule chips render a soft red ⚠ on non-fitting options (still tappable — advisory, DJ override wins). ZERO change to slot generation (build_day_plan/_free_slots/rank_days untouched). NOT yet on v2_command reschedule, WSCDayPlan calendar, or the field.py AI tool. **Option B (hard-filter the shared 1.5h-grid model) still deferred.** The deeper truth below is why B is risky:

**Slot finder IGNORES job length — assumes every job = 90 min.** `_find_scheduling_openings` (field.py ~L2280) uses a FIXED `JOB_DURATION_MIN = 90` for BOTH the required gap AND how long each existing job blocks; workday window `WORKDAY_START_H=8`..`WORKDAY_END_H=15` (8am–3pm PT). It does NOT read `x_job_length_min` (a real sale.order field used in new_job/scheduler/goals/booking_requests). So marking a job 4 hours on the job detail is NOT honored — it reserves only 90 min, and a 4-hour existing job is under-blocked (overlap/too-close suggestions). Fix = read `x_job_length_min` (fallback 90) for both the target job's gap and each existing job's block span.

**Plan:** all three folded into `3_Documentation/SCHEDULING_OFFERS_BRIEF.md` (pushed 2026-08-15) + AGENT_MAIL co-plan note. Scheduling is CO-OWNED with the specialist session (they: scheduler.py/reschedule/reminders; lead: sms drafter + field finder) — agree the split before coding. DJ approved building all three. See [[project_reactivation_sent_book]] (booking flow) and the reschedule modal in v2_command.html (`openReschedule`/`submitReschedule` → `/api/schedule/reschedule`).
