# The HUD is a DASHBOARD, not an inbox — every card must recompute or expire

**Type:** project
**Date:** 2026-09-02 (DJ restated the principle; audit run same day)

## DJ's framing
> *"Our goal was to make the HUD more of a dashboard than an inbox and it should be treated like a
> dashboard. So it's constantly showing only things that need confirmations — that takes care of the
> problem we're describing plus it takes care of the old stale information."*

This is not new policy. It is **Attention Feed Contract rule 4** restated:
**"Withdraw (`delete_item`) the moment it's no longer true — stale cards kill trust."**
(`3_Documentation/ATTENTION_FEED_CONTRACT.md`; see [[project_attention_feed_contract]].)
Contract rule 0 is its sibling: **titles stay generic — no counts or $ in a title, they go stale.**

## The test to apply to ANY card
**Does it RECOMPUTE, or does it REMEMBER?** A card that was true when it was written and is never
re-derived is an inbox message. Three ways to pass:
1. rebuilt from live data on the tick, and `delete_item()` when the condition is gone (best), or
2. `delete_item()` on the action that resolves it, or
3. an `expires` stamp, for a pure FYI nobody will ever "resolve".
A card with **none** of the three is a leak. Two failures found 2026-09-02 both looked fine in
review — the bug is invisible until a card sits there for a week.

## What the 2026-09-02 audit found (16 producers)
- **14 pass.** `specialist_digest`/`specialist_morningnews` pass via `expires`; `sched_req`,
  `zelle_engaged` etc. are withdrawn by the action that resolves them.
- **`sched_moved:<so_id>`** (booking.py, added 2026-09-01) — FYI, no withdrawal, no expiry → rotted
  forever. Fixed: 48h expiry.
- **`offer_custom:<offer_id>`** (booking.py) — raised when a customer declines the offered times.
  Keyed by OFFER id, which **nothing can look up from a job**, so rescheduling them left the card
  demanding something already done. Fixed: rekeyed to `offer_custom:<so_id>` so the reschedule path
  withdraws it like `sched_req`, + 7-day backstop.
  ★ **Lesson: key a card by the SUBJECT the resolving action knows about (the SO), not by the
  transient thing that produced it.** A card you cannot address from the place it gets resolved can
  never be withdrawn.

## Two REAL bugs the same lens exposed (not card lifecycle — data)
1. **Confirmations only ever covered ONE day.** `build_batch('confirm')` ran every 30 min but always
   targeted exactly `today + CONFIRM_LEAD_DAYS`. A job booked onto a day ALREADY inside the window
   was never revisited — that day's batch predated the job — so the customer never got a
   confirmation (Debbie Church; William Smith exposed). **The board recorded this as "built once a
   day", which was WRONG** — it rebuilt constantly, at the wrong target. Fixed: `reminders_tick()`
   now rebuilds EVERY day from tomorrow through the lead edge. Safe because each row carries idem
   `reminder_confirm:<so_id>:<day>` and already-sent rows drop out.
2. **Billing "days ago" was computed in UTC.** `date_str = (so['date_order'] or '')[:10]` slices the
   UTC date; `date_order` is UTC, so **every job from 5pm Pacific onward reported TOMORROW's date**
   and one day fewer "days ago". Fixed by converting to `_PT` first.
   ★ **Never slice a date out of `date_order`. Convert to Pacific first.** Same class as the
   Command Center ribbon off-by-one (2026-08-31).

## How to apply
- Before shipping a card: state which of the three mechanisms clears it. If you cannot, it is a leak.
- Auditing: `grep -c submit_item` vs `grep -c delete_item` per file finds candidates fast; then check
  each survivor for `expires`.
- Don't trust a board/memory entry describing a bug's CAUSE — re-derive it. Two "known" causes were
  wrong this week (this one, and "the refresh button broke in the V2 migration" — it never worked).
