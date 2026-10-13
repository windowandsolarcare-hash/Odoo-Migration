---
name: project_confirm_milestone_record_only_not_send
description: "Confirm-flow fact (2026-10-13): the '✅ Confirmed for <day> at <time>' line on a customer's inbox thread is a RECORD-ONLY timeline milestone (reminders._append_confirmed_milestone → append_inbox_event source='system', index=False), NOT a text to the customer — set_confirmation never messaging.send's. An inbound YES auto-RECORDS the confirm (CONFIRM_KEY + milestone); the OUTBOUND reply stays review-first (DJ sends). Do NOT re-panic at 'Confirmed for <wrong date>' on a thread — nothing was sent. Known stale-stamp bug: the milestone reads the SO's date_order AT reply-time, so if the reply names a different date than the SO's current one, it stamps the stale date."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-13T20:44:34.575Z
---

## The fact (so no future session re-panics)
A customer inbox thread showing **"✅ Confirmed for Friday, October 16th at 8:30 AM"** is a **RECORD-ONLY internal timeline milestone**, NOT a text that was sent to the customer. Verified firsthand 2026-10-13 (Karen Bellamy case, DJ also verified):
- `reminders.set_confirmation(so_id, by, maint)` (reminders.py:726): `_pset(CONFIRM_KEY+so, now)`, optionally `_pset(MAINT_CONFIRM_KEY+so, now)`, then `_append_confirmed_milestone(so_id)`. **No `messaging.send` anywhere in set_confirmation.**
- `_append_confirmed_milestone` (reminders.py:845): reads the SO's current `date_order` → builds `✅ Confirmed for <day> at <clock>` → `append_inbox_event(body, source='system', label='confirmed', **index=False**)`. `index=False` = threads + carries its chip but does NOT re-surface as needs-action. **Record-only; never a customer send.**
- So an inbound "YES" **auto-RECORDS** the confirmation (CONFIRM_KEY + the milestone) — that is the designed §9-compliant behavior. The **outbound** reply ("see you then") is NOT auto-sent — the reminders:ack card has NO on_approve; DJ reviews+sends it himself.
- **Takeaway:** "Confirmed for <date>" on a thread ≠ a wrong text went out. Check whether the line is `source='system'` (a milestone) before alarming. 120s dedupe guards against stacking.

## The real (LOW-pri) bug — stale confirm stamp on a date-mismatch reply
The milestone (and the CONFIRM_KEY stamp) use the SO's `date_order` **at reply-time**. If the customer's reply **names a different date** than the SO's then-current date (Karen's reply named the 23rd while the SO was still Oct 16; Operator later moved it to Oct 23), the milestone stamps the **stale** date (16th). Internal record quality only — nothing wrong reaches the customer. Fix (queued LOW, after HUD, its own §15): don't stamp "confirmed for <SO date>" when the reply names a DIFFERENT date — detect reply-date-vs-SO-date mismatch first.

## ★ CROSS-DEPENDENCY with the HUD-cards fix (Lead, honor this ORDER)
The HUD confirm-card fix keys the per-SO `reminders:ack:{kind}:{so_id}` card's `created` on **CONFIRM_KEY/MAINT_CONFIRM_KEY** (stable-created → the ack card re-opens when the stamp advances on a genuine re-confirm). The residual stale-stamp fix **changes WHEN/WHETHER CONFIRM_KEY stamps**. Therefore: **(a) land the HUD fix FIRST; (b)** when the residual later suppresses/corrects a stamp on a date-mismatch, **prove it doesn't break the HUD stable-created re-open** — a suppressed stamp must NOT wrongly freeze or hide the ack card. Flag this in the residual's own §15.

See [[project_inbox_audio_range_and_allpill_cache]], [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_hud_cards_live_not_inbox]], [[feedback_times_in_pacific]].
