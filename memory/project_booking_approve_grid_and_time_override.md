---
name: project_booking_approve_grid_and_time_override
description: "Root-cause (2026-10-12, SO 17758 odd-minute 1:23): the app scheduler is a RIGID 90-min grid (8:00/9:30/11:00/12:30/2:00/3:30) and can NEVER emit an off-grid minute like :23; and the booking-approve review screen (v2_booking.html) auto-selects the route-tightest SUGGESTED slot on load, silently overriding the customer's requested TIME. /approve has no idempotency. The exact 20:23 writer is UNRESOLVED — the one logged approve (chatter 12:30) wrote 19:30, so a non-approve writer set 20:23; request bodies aren't in Render logs."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T13:47:51.999Z
---

Triage from Lead: booking-approve for Kathy Sell SO 17758 (→265029) stored `date_order` 2026-10-22 20:23 UTC = **1:23 PM PT**, customer requested **12:30**. DJ says he's seen it before → RECURRING class. Diagnosed worst-first (Specialists owns scheduler.py + booking_requests.py).

## DECISIVE: the scheduling engine is GRID-ONLY — it cannot produce an odd minute
`booking.py:150 _all_slots()` → `[480, 570, 660, 750, 840, 930]` = **8:00 / 9:30 / 11:00 / 12:30 / 2:00 / 3:30** (90-min grid; `SLOT_MIN=90`, `WORK_START_MIN`→`WORK_END_MIN`). Everything downstream derives from it:
- `scheduler.py:595 build_day_plan`: `free = [s for s in _all_slots() if _reachable(s)]`; `suggested = free[0]` or `min(free, key=cost)` → always a grid minute.
- `rank_days` / `best_fit_plan` / `api_scheduler_so_suggest` build `time` from `sm % 60` → always `:00`/`:30`.
- `_job_fits_at` (scheduler.py:943) is **advisory only** — returns `(fits:bool, warn:str)`, emits NO minute.
=> **No best-fit / route-tight / coord / suggest path can ever write an off-grid minute like `:23`.** So "odd-minute = best-fit signature" is FALSE here — there is no sub-grid writer anywhere in the app. 12:30 (750) is itself a valid grid slot.

## The recurring class: approve silently overrides the customer's requested TIME
`static/owner/v2_booking.html:363-364` on load: `var sug=slots.filter(s=>s.suggested)[0]; if(sug) pickSlot(sug.minute);` — auto-selects the **route-tightest SUGGESTED** slot and `pickSlot` (:399-405) writes it into the `#t-start` box. The review GET (`booking_requests.py:246-257`) returns only the requested **DAY** + `suggested_minute`; the customer's requested **TIME** is never surfaced or pre-selected. So tapping **Approve** as-is books the route-tightest time, NOT what the customer asked — silently (e.g. 12:30 → 2:00). THIS is DJ's recurring "requested X, booked Y". (It yields a GRID time, not `:23`.)

## The specific `:23` — UNRESOLVED; the logged approve can't have written 20:23
`/approve` (`booking_requests.py:260`) writes `body['start']` exactly: `start_min` (:271) → `date_utc` (:310-311) → `write date_order` (:333) → `schedule_odoo_so(dt_pt)` (scheduler.py:1084, writes `dt_pt.astimezone(UTC)` exactly at :1130-1133, no nudge). Within ONE handler invocation the `date_order` write (:333/:1133) and the chatter time (`:402`, `_slot_label(start_min)`) use the SAME `start_min`, so they MUST agree.
**Operator's log evidence (request bodies are NOT logged):** exactly ONE completed approve POST for 17758 at 13:27:31 (200 OK, phone IP); the ClientDisconnect traceback is at `request.json()` (**:262, the first line — body read**), which writes NOTHING; Odoo shows confirm-tracking 13:27:12, SO `write_date` 13:27:13, chatter posted 13:27:29 saying **12:30 PM**.
=> chatter 12:30 ⟹ `start_min`=750 ⟹ that handler wrote `date_order` **19:30**. Yet stored is **20:23** with `write_date` 13:27:13 and no later write. **The single logged approve CANNOT have produced 20:23.** My earlier "double-POST, approve B carried 13:23" theory is RETRACTED (no second completed POST; the disconnect wrote nothing). So either a NON-approve writer set 20:23 at ~13:27:13, or the client actually sent `start=13:23` and the chatter reading needs re-check. Request bodies aren't recoverable from Render logs. NEXT: (a) the telemetry beacon may hold the client-side POST body (Operator) — get the real `start/minute/end`; (b) check for another endpoint write or an Odoo `base.automation`/server-action on `sale.order` confirm/write that touches `date_order`. `#t-start` is `<input type=time step=300>` = editable, so an off-grid `13:23` can only enter via that box being hand-set or a direct caller POSTing it.

## Reliability gap that enables the mismatch
`/approve` has **no idempotency**: `approve()` guards with `b.disabled` but has **no try/finally**, and the server re-runs the whole path on any replay (re-confirm, re-write date_order, dup chatter/line-items). Two POSTs with different starts → silent last-write-wins.

## Proposed fix direction (Lead confirms + §15 before build — scheduling/behavior, NOT a customer send)
1. Stop silently overriding: surface the customer's REQUESTED slot and default-select it when reachable; make route-tightest an opt-in labeled SUGGESTED; if the requested slot isn't open, say so ("12:30 isn't open — nearest 2:00") instead of pre-picking.
2. Server backstop: if posted `start` != requested minute, require an explicit confirm flag.
3. Per-`so_id` idempotency guard on `/approve` (no-op a 2nd approve within N s).
4. Off-grid guard: validate/snap `start` to an offered slot (or warn).

See [[feedback_dj_operating_instincts]] (tap-to-book, review-then-send), [[feedback_builders_dont_sequence_or_defer]], [[feedback_audit_stamp_confirm_firsthand]].
