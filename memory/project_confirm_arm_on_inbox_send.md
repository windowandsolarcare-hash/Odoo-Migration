---
name: project_confirm_arm_on_inbox_send
description: Manual inbox-thread confirm send now arms reply→auto-confirm (_arm_confirm_if_pending) — closed the Galen SO 17677 gap
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-27T00:08:51.608Z
---

**Shipped 2026-09-26 (commit 4821bf62, sms.py).** A customer's "Confirmed!" reply auto-marks their SO only if `_mark_awaiting(phone, so_id, so_name)` (reminders.py:571) was armed for that phone. It was armed on the reminder / scheduler / `sched/launch mode=confirm` paths — but NOT on the **manual inbox-thread send** (`/owner/api/inbox/send` = `inbox_send` in sms.py). Since the HUD gold-standard confirm IS a manual inbox-thread send (card opens thread → DJ presses Send), EVERY HUD-card confirm had this gap → DJ hand-marked each one via `/owner/api/sched/mark_confirmed` (Galen Wood SO 17677, hit live by Operator).

**Fix (Lead-decided b-ii = ARM-ONLY):** new helper `_arm_confirm_if_pending(conv)` in sms.py (right after `_find_upcoming_job`), called in BOTH `inbox_send` return branches — the immediate successful-send branch AND the quiet-hours HOLD branch (a night confirm is held → released 8am by `release_holds→messaging.send`, which never runs the belt; the customer can't reply until then, so arm now and the marker waits). It uses `_find_upcoming_job(pid)` (soonest `state='sale'`, not Done/Canceled, `date_order asc limit 1`) and skips if `so_id in awaiting_so_ids()`. ARM-ONLY = no `state='sent'` / no confirm-idem burn / no operator-card clear (those belong to the formal confirm path). Best-effort try/except; deferred `from routers.owner.reminders import _mark_awaiting, awaiting_so_ids` (messaging↔sms circular).

**Why:** without arming, the reply→auto-confirm listener has no phone→so_id marker to match, so the SO stays unconfirmed + thread stays needs_reply even though the customer said yes.

**How to apply:** the GOLD-STANDARD HUD confirm is a manual inbox-thread send — any new confirm entry-point that sends via `inbox_send`/`messaging.send` (kind='manual'/'reply') must arm the belt or it inherits this gap. The formal `api_confirm_card`→`confirm_so`→`sched/launch mode=confirm` path already arms + targets a SPECIFIC SO; the belt's soonest-SO heuristic can arm the wrong job only if DJ confirms a LATER job while a sooner one is also pending (rare, accepted). Related: [[feedback_no_inventing_customer_lines_hud_confirm]] (gold-standard HUD confirm opens the pre-filled thread), [[feedback_reuse_function_follow_full_logic]].
