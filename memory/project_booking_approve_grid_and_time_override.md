---
name: project_booking_approve_grid_and_time_override
description: "Root-cause (2026-10-12, SO 17758 odd-minute 1:23): the app scheduler is a RIGID 90-min grid (8:00/9:30/11:00/12:30/2:00/3:30) and can NEVER emit an off-grid minute like :23; and the booking-approve review screen (v2_booking.html) auto-selects the route-tightest SUGGESTED slot on load, silently overriding the customer's requested TIME. /approve has no idempotency. The exact 20:23 writer is UNRESOLVED — the one logged approve (chatter 12:30) wrote 19:30, so a non-approve writer set 20:23; request bodies aren't in Render logs."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T13:54:28.038Z
---

Triage from Lead: booking-approve for Kathy Sell SO 17758 (→265029) stored `date_order` 2026-10-22 20:23 UTC = **1:23 PM PT**, customer requested **12:30**. DJ says he's seen it before → RECURRING class. Diagnosed worst-first (Specialists owns scheduler.py + booking_requests.py).

## DECISIVE: the scheduling engine is GRID-ONLY — it cannot produce an odd minute
`booking.py:150 _all_slots()` → `[480, 570, 660, 750, 840, 930]` = **8:00 / 9:30 / 11:00 / 12:30 / 2:00 / 3:30** (90-min grid; `SLOT_MIN=90`, `WORK_START_MIN`→`WORK_END_MIN`). Everything downstream derives from it:
- `scheduler.py:595 build_day_plan`: `free = [s for s in _all_slots() if _reachable(s)]`; `suggested = free[0]` or `min(free, key=cost)` → always a grid minute.
- `rank_days` / `best_fit_plan` / `api_scheduler_so_suggest` build `time` from `sm % 60` → always `:00`/`:30`.
- `_job_fits_at` (scheduler.py:943) is **advisory only** — returns `(fits:bool, warn:str)`, emits NO minute.
=> **No best-fit / route-tight / coord / suggest path can ever write an off-grid minute like `:23`.** So "odd-minute = best-fit signature" is FALSE here — there is no sub-grid writer anywhere in the app. 12:30 (750) is itself a valid grid slot.

## The recurring class: approve auto-picks the route-tight slot with no prominent time confirm
`static/owner/v2_booking.html:363-364` on load: `var sug=slots.filter(s=>s.suggested)[0]; if(sug) pickSlot(sug.minute);` — auto-selects the **route-tightest SUGGESTED** slot and `pickSlot` (:399-405) writes it into the editable `#t-start` box. **IMPORTANT (Lead correction):** there is NO captured customer clock time — the self-booking stores only a half-day **pref** + am/pm + date (`booking.py:1547`), and the review GET filters offered slots to that pref half. So the auto-pick DOES honor the half-day; the gap is NOT "it ignored the requested time" (there isn't one) — it's that the chosen time isn't surfaced prominently for a deliberate confirm before booking, so a time DJ didn't expect lands silently. Do NOT frame the fix as "default to the requested time." (It yields a GRID time, not `:23`.)

## The specific `:23` — UNRESOLVED; the logged approve can't have written 20:23
`/approve` (`booking_requests.py:260`) writes `body['start']` exactly: `start_min` (:271) → `date_utc` (:310-311) → `write date_order` (:333) → `schedule_odoo_so(dt_pt)` (scheduler.py:1084, writes `dt_pt.astimezone(UTC)` exactly at :1130-1133, no nudge). Within ONE handler invocation the `date_order` write (:333/:1133) and the chatter time (`:402`, `_slot_label(start_min)`) use the SAME `start_min`, so they MUST agree.
**Operator's log evidence (request bodies are NOT logged):** exactly ONE completed approve POST for 17758 at 13:27:31 (200 OK, phone IP); the ClientDisconnect traceback is at `request.json()` (**:262, the first line — body read**), which writes NOTHING; Odoo shows confirm-tracking 13:27:12, SO `write_date` 13:27:13, chatter posted 13:27:29 saying **12:30 PM**.
=> chatter 12:30 ⟹ `start_min`=750 ⟹ that handler wrote `date_order` **19:30** (:333 + schedule_odoo_so:1133; the schedule_odoo_so TAIL — A12 threader, maint_resolve_needs, delete_item, cache-bust — writes NO date_order). Yet stored is **20:23** with `write_date` 13:27:13. **The logged approve CANNOT have produced 20:23 — it's a PHANTOM write** (concurrent, at the same 13:27:13 second, winning over the approve's 19:30). Verbatim chatter (res.partner 27296, 13:27:29 UTC): "📅 Online booking approved | requested 2026-10-22 (Afternoon) | Solar Panel Cleaning | scheduled 2026-10-22 12:30 PM"; booking approved-log also 12:30 PM. Earlier "double-POST, approve B=13:23" theory RETRACTED (Operator: one completed POST; the ClientDisconnect is at request.json() :262 = body read → wrote nothing; the 2nd attempt wrote nothing).

RULED OUT for the 20:23 (all firsthand / Operator): the approve handler itself; schedule_odoo_so's tail; Odoo base.automation id 9 / SA 1364 (no date_order write); SA 955 Workiz-sync (only cron 68 at 11:00, Workiz dead, 17758 has no Workiz source); any other sale.order cron (none); all 18 live main.py `_scheduled_*` APScheduler jobs (none writes date_order; no heal/tighten job exists); every app date_order writer is an explicit endpoint (booking/brain/dashboard/maint_regen/new_job + reschedule/set_slot) and Operator's log shows only the one approve POST + GETs at 13:27. Render logs don't record request bodies; date_order isn't field-tracked so Odoo has no value history; the telemetry beacon is failure-only (no client body).

**UNRESOLVED — needs runtime instrumentation to catch the next occurrence** (recommended to Lead, gated by §15): (1) enable Odoo field TRACKING on `sale.order.date_order` (logs every change w/ user+timestamp+old→new — the single best catch; reversible config, DJ/Lead call since it's a field-attr change); and/or (2) a temporary server-side write-trace logging so_id+value+caller on every date_order write (booking_requests:333 + scheduler.py:1130). `#t-start` is `<input type=time step=300>` = editable, so if the next trace shows an off-grid start it came through that box or a direct caller.

## Reliability gap that enables the mismatch
`/approve` has **no idempotency**: `approve()` guards with `b.disabled` but has **no try/finally**, and the server re-runs the whole path on any replay (re-confirm, re-write date_order, dup chatter/line-items). Two POSTs with different starts → silent last-write-wins.

## Proposed fix direction (Lead-reframed; Audit §15 + Lead firsthand stamp before build — scheduling/behavior, NOT a customer send)
1. **Prominent about-to-book-time display** on the review screen so the chosen time is confirmed deliberately before Approve (addresses "a time DJ didn't expect landed"). NOT "default to requested time" — there's no captured clock time.
2. **Off-grid = SOFT confirm, never a hard reject/snap.** The editable `#t-start` is intentional (rules 10/11); if `start` is off-grid, show a soft "booking at 1:23 PM — confirm?" rather than blocking or snapping.
3. Per-`so_id` idempotency guard on `/approve` (no-op a 2nd approve within N s) + wrap `approve()` in try/finally so the button can't lock.
4. For the PHANTOM: enable Odoo field tracking on `sale.order.date_order` (and/or a temporary write-trace) to catch the next occurrence BEFORE closing — the :23 is unexplained and must not be closed on assumption.

See [[feedback_dj_operating_instincts]] (tap-to-book, review-then-send), [[feedback_builders_dont_sequence_or_defer]], [[feedback_audit_stamp_confirm_firsthand]].
