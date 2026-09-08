---
name: project_maint_confirm_state_sync
description: "TWO confirm keys existed for ONE fact: a MAINTENANCE Stage-1 confirm writes wsc.maint.confirmed.<so>, but the Command Center (/api/sched/states conf[]), the job-detail (is_confirmed→api_maint_state), and the HUD replies blob all read only wsc.reminders.confirmed.<so> → a confirmed maint job showed 'NOT SENT' + re-send buttons. Fix: is_confirmed + sched/states read BOTH keys; the confirm-reply branch now lands in the replies blob."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T14:16:38.077Z
---

**DJ-hit bug fixed 2026-09-08 (Bill Winkill SO 17063 / 004334).** A maintenance confirmation was genuinely recorded (`wsc.maint.confirmed.17063` set + chatter "Customer CONFIRMED by text") yet every UI surface showed the opposite — Command Center card "⚠ NOT SENT", job-detail still offering "Send confirmation / Mark confirmed", and Bill missing from the HUD "Next service confirmed" card.

**Root cause = two-places-for-one-fact (the recurring class).** There are TWO confirm keys in reminders.py:
- `CONFIRM_KEY = 'wsc.reminders.confirmed.<so>'` — the PLAIN reminders confirm (non-maint + manual).
- `MAINT_CONFIRM_KEY = 'wsc.maint.confirmed.<so>'` — the MAINTENANCE Stage-1 confirm (set by the text-reply 'confirm' branch in `_maint_handle_inbound`).

A maint confirm wrote only the maint key, but the read surfaces checked only the reminders key:
- `is_confirmed(so_id)` (used by `api_maint_state` → the **job-detail** confirm/ack buttons, and by the night-before eve branch) read only `CONFIRM_KEY`.
- `/api/sched/states` `conf[]` (the **Command Center** ✓CONFIRMED / ⏳SENT / ⚠NOT SENT strip reads `d.confirmed`) searched only `wsc.reminders.confirmed.%`.
- the `_maint_handle_inbound` **'confirm' stage** YES-branch set `MAINT_CONFIRM_KEY` + chatter but — unlike the **'advance' stage** branch (which calls `appt_confirm → _maint_result_card('ok')`) — never wrote the `wsc.maint.replies` blob, so the HUD reply card missed it. (That's why advance-stage confirmers 17327/17486 WERE in the blob and Stage-1 Bill wasn't.)

**Fix (one source of truth):**
1. `is_confirmed()` now returns `_pget(CONFIRM_KEY+so) or _pget(MAINT_CONFIRM_KEY+so)` — both confirm paths count everywhere it's read. (`_maint_confirmed_batch` already read both.)
2. `/api/sched/states` `conf[]` query is now an OR over `wsc.reminders.confirmed.%` AND `wsc.maint.confirmed.%`.
3. `_maint_handle_inbound` 'confirm' branch now also calls `_maint_state_set(so,'ok',{'via':'text-confirm'})` + `_maint_result_card(so,'ok')` so a Stage-1 confirm lands in the replies blob + "Next service confirmed" card (matching the advance branch).
Bill 17063 was backfilled into `wsc.maint.replies.confirmed` (fix 3 only helps future replies). Verified: the new OR-query returns 17063; deploy boots clean.

**The send side was already fine:** `_send_stage_row` marks `wsc.maint.advance.awaiting` for stage='confirm', and `/api/sched/states` reads that key → the ⏳ "SENT — NO REPLY" strip works pre-reply; the hole was only the confirmed read. Ties into DJ's open #4 (ack-vs-confirm) but is a real bug regardless. Sibling pattern: [[project_writeback_not_proof_computed_field]] and the general "one fact, one store" rule; see [[project_command_conf_pills_cached]].
