---
name: project_slot_offer_record_no_held_check
description: "Two customers held the SAME slot (Anne Sandberg + Desiree Wesson, Thu 10/8 8:30, 2026-10-02) because the 'no double-offer' invariant was enforced ONLY in the slot FINDER (scheduler.build_day_plan unions pending offers into occupied), NOT at slot_offers.record_offer — the single choke point every offer path shares did no held check. Plus the single ir.config_parameter store (wsc.slot_offers) is read-modify-write, so near-simultaneous records race (duplicate not collapsed, sibling not cleared on booking). Fix = record-time held-slot guard + clear same-SO siblings on booking (slot_offers.py)."
metadata:
  node_type: memory
  type: project
  originSessionId: 8a97aa73-5f27-4f02-a0f6-64f2dd10d242
  modified: 2026-10-02T07:42:34.456Z
---

**Bug (2026-10-02, customer-facing scheduling):** Command Center showed Thu Oct 8 8:30 AM held for BOTH Anne Sandberg (offer `a298f3c5c341`, SO 17108) and Desiree Wesson (SO 17728) — two customers offered one slot → double-book if both pick it. Desiree had also already *booked* it (SO 17728 = draft/Submitted reserve at Oct 8 8:30) while her 20-sec-apart duplicate offer kept holding it, and Anne's pending offer (expiring the same morning) also held it.

**Root cause (code-proven):**
1. **The held/occupied predicate runs only in the slot FINDER, not at RECORD.** `scheduler.build_day_plan` (via `held_intervals_for_day`/`_for_range`, "Reserve Stage 1" 2026-09-26) unions (a) submitted/draft maintenance reserves and (b) pending `wsc.slot_offers` into `occupied`, so SUGGESTIONS skip held slots. But **`routers/owner/slot_offers.record_offer`** — the ONE choke point every offer-creation path flows through (`POST /owner/api/offers/record`, `/offers/reserve`, and `sms.py` reschedule-offer ~line 1925) — did **no held check**. It only normalized, dropped day-off slots, and deduped by `(partner_id, so_id)`. So any slot not freshly finder-filtered (a manual/fixed pick, a stale suggest, or a 2nd offer suggested before the 1st was saved) was recorded on top of an existing hold.
2. **The offer store is a single `ir.config_parameter` key `wsc.slot_offers`, mutated read-modify-write** (`_load()`→modify→`_save()`). Two near-simultaneous records (Desiree's twin, 20 sec apart, same partner+SO) each loaded before the other saved, so the in-call replace-in-place dedupe didn't collapse them (plausibly amplified by Render's 2 instances each caching `get_param` independently — likely, not proven). Booking one offer did NOT clear its twin → a phantom pending hold on the booked slot.

**Fix (3 surgical edits, `slot_offers.py` ONLY — signature `(oid, dropped)` unchanged so the 3 callers incl. sms.py need no edit, avoiding a stale-base collision with the staged inbox Phase 1):**
- **record_offer** re-checks holds at record time: drop any candidate slot already held by a pending offer of a **DIFFERENT partner** (parsed-instant match via `_parse`/`_iso`; same partner excluded so a customer's own re-offer still replaces-in-place). Dropped conflicts are surfaced in the existing `dropped` return; refuse `('', dropped)` if all conflict.
- Genericized the two refuse messages + the warning (was hardcoded "day off") so a conflict drop isn't mislabeled.
- **clear_offer** on `reason=='booked'` cancels other pending offers for the same `(partner, so_id)` (`clear_reason='sibling_of_booked'`) → booking a reschedule can't leave a phantom twin holding the slot.

**How to apply / lesson:**
- **An invariant enforced only at the "suggest/read" step is not enforced** — the WRITE step (record) is the authoritative choke point and must re-validate. Finders filtering suggestions ≠ the record refusing a conflicting write.
- **A single `ir.config_parameter` JSON list is not concurrency-safe** (read-modify-write, multi-instance `get_param` caching). A record-time re-check closes the common sequential + non-finder cases but NOT two simultaneous records (TOCTOU). The durable fix is a transactional Postgres table with a per-slot claim/unique guard (operational high-write data → Postgres per [[feedback_data_location_odoo_vs_postgres]]) — flagged for Lead/DJ, not built in the surgical pass.
- Store = `wsc.slot_offers` (`routers/owner/slot_offers.py`); finder held-union = `scheduler.held_intervals_for_day`/`_for_range` + `build_day_plan`. Related: [[feedback_reuse_function_follow_full_logic]], [[feedback_sporadic_bugs_repeat_test]].
