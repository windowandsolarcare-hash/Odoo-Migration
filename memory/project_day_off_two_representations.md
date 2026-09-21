---
name: project_day_off_two_representations
description: "A day is \"off\" in TWO independent ways — a capacity override (wsc.capacity.overrides ≤0) OR a full-day \"Personal Time\" SO block (job_type='Personal Time', partner 23054, x_job_length_min>=480). shared.is_day_off(d, fresh=False) is the single enforcement point and now unions BOTH. Every slot source must route through it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-21T14:27:30.704Z
---

**Scheduling #4 (2026-09-21, commit 5e3d7de4, Lead-QC'd):** a customer was offered Oct 7 (Cheryl's birthday, a day DJ blocked off). Root cause = **two independent "day off" representations, and the check only knew one.**

## The two representations
1. **Capacity override** — `ir.config_parameter` key `wsc.capacity.overrides` = `{'YYYY-MM-DD': capacity}`; ≤0 = off. Read by `shared._dayoff_overrides()` (30s cache).
2. **Full-day "Personal Time" SO block** — how DJ actually marks a day off from the calendar/Command Center: a `sale.order` with `x_studio_x_studio_x_studio_job_type='Personal Time'`, `partner_id=23054` ("Personal Time"), `state='sale'`, `date_order` at the start time (UTC), `x_job_length_min` = block minutes. A **full-day** OFF = a Personal Time block with `x_job_length_min >= 480` (8h). DJ's real OFF days carry TWO blocks (a 720-min 7am + a 480-min 9am). A shorter Personal Time block is a partial appt (handled by job-length spacing, NOT a day closure). date_order is UTC → convert to Pacific to get the block's calendar day.

## The fix / architecture (how OFF-day exclusion works now)
- **`shared.is_day_off(d, fresh=False)` is the SINGLE enforcement point** — it now returns True if capacity≤0 OR the Pacific date is in `_pt_off_days()`. `_pt_off_days(fresh)` = ONE search_read of Personal Time SOs → set of full-day-off Pacific dates, **~300s cached** for loop-heavy suggesters; **`fresh=True`** bypasses the cache for the low-frequency offer/reserve path (so a just-added day off is honored immediately). Fails OPEN to last-known (never crashes a slot source).
- **Two engines already funnel through is_day_off** — so most slot sources inherit the fix for free:
  - `scheduler.build_day_plan(lat,lon,date)` returns `{'slots':[], 'day_off':True}` when `is_day_off` → every consumer that reads `slots` drops the day (openings, the day view).
  - `scheduler._rank_days_at` / `rank_days` call build_day_plan per candidate and skip empty-slot days → **so-suggest, city-suggest, reactivation suggest, specialist_booking, new_job suggests** all inherit it. NO per-source change needed.
- **Two sources bypassed both engines and needed a direct guard** (this was the actual bug surface):
  - `slot_offers.record_offer` (offers/reserve) had ZERO day-off validation — it recorded whatever manual slots were passed. Now filters via is_day_off(fresh=True), returns `(oid, dropped)`; the API layers DROP off-day slots + SURFACE them (`{dropped, warning}`) and REFUSE if all slots are off (never silent — Operator hand-builds offers).
  - `booking._open_dates_for_city` (customer page + new_job day suggestions) built candidate days by weekday only — now skips is_day_off days.

**How to apply:** any NEW slot/offer/suggest source MUST call `shared.is_day_off(date)` (or route through build_day_plan/rank_days). Use `fresh=True` on customer-offer paths. Verified live: Tuesday cities (Indio/La Quinta) skip Oct 7, Monday (Hemet) skips Oct 6, zero leaks. See [[feedback_reuse_canonical_endpoint]], [[feedback_never_send_dj_to_odoo]].
