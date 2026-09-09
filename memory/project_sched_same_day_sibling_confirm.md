---
name: project_sched_same_day_sibling_confirm
description: "Self-schedule confirm/move/request cover a customer's WHOLE same-day job set (house+condo), not one — via booking._sched_siblings (group by parent contact, awaiting-gated). Built+QC'd 2026-09-09."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T18:51:14.338Z
---

The customer self-schedule page (`routers/booking.py`, /book/sched/<SO-signed token>) used to show/confirm only the ONE SO its token was signed for — so a customer with 2+ same-day jobs (e.g. Wayne Geringer: house 17066 + condo 17067, both a Thu) confirmed only one. Fixed 2026-09-09 so ALL three customer actions cover the whole same-day set.

**The shared primitive — `_sched_siblings(c)`** (c = `_sched_ctx(so_id)`): returns the same-day appointment SET as `[{so_id, so_name, address, job_type, when, date_key, time}]`.
- **Group by the CUSTOMER = the parent CONTACT** (`contact_id`), not the property. House+condo are two `res.partner` **Property** records (different `partner_shipping_id`) under ONE parent contact — `_sched_ctx` already resolves `contact_id` = that parent. cust_ids = [contact_id] + res.partner children (parent_id==contact_id); SOs matched by `('|', partner_id in cust_ids, partner_shipping_id in cust_ids)`.
- **Same PT day** (day_key 00:00–23:59 PT → UTC window on `date_order`).
- **AWAITING-confirmation gate** (the narrow, correct set): a sibling qualifies only if its so_id is in **`reminders.awaiting_so_ids()`** (the `wsc.reminders.awaiting` / PENDING_KEY set that `confirm_on_link_booking`/`clear_awaiting_for_so` key on). The token SO is ALWAYS included. So an already-confirmed or unrelated same-day job is never swept in.
- **Size 1 in the normal case** → every path below is byte-equivalent to the old single-SO code.

**All three paths reuse it** (mirror the single-SO writes per sibling; tapped SO must succeed else error, a sibling failure never fails the tap):
- **b1 confirm-all** + **b2 move-all** → `sched_confirm` loops: per sibling `_sched_book` + `_sched_state_set` + `confirm_on_link_booking` + `clear_awaiting_for_so`. Confirm books each at its own day/time; a MOVE moves all to the picked day/time. ONE consolidated HUD "moved" feed card (not N), moved-marker + chatter per SO.
- **choice-3 request-all** → `sched_request` loops: each sibling → state 'requested' + chatter; ONE consolidated HUD approval card ("<first> picked their own day for their N jobs"), "Set the time" → the day-planner.
- The page (`_SCHED_HTML`) renders `CTX.jobs` as a per-job list ("One tap confirms all N appointments") when >1; 1-job page unchanged.

**Added helper:** `reminders.awaiting_so_ids()` (reuse, not fork). **Reuse rule honored:** every per-sibling write is the exact single-SO call; nothing duplicated.

See [[project_render_coalesces_rapid_pushes]] (verify-the-tip after multi-file pushes) and [[feedback_reuse_canonical_endpoint]].
