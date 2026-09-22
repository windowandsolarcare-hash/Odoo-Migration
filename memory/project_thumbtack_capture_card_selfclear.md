---
name: project_thumbtack_capture_card_selfclear
description: "The Thumbtack \"Save real cell+email\" HUD capture card (thumbtack_capture:<lead_id>) now self-clears when the lead is resolved (real contact on file / an SO exists), fixing DJ's stale \"Bruce\" card. clear_resolved_captures() runs in the 72h sweep AND at HUD build."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T15:33:22.672Z
---

**Self-clearing Thumbtack capture card (2026-09-22, commit 11297fce).** DJ's HUD kept showing a stale "Save Bruce's real cell + email" card. Root cause: the `thumbtack_capture:<lead_id>` card (created by `thumbtack.py surface_capture_card`) only cleared on its OWN approve (`sms.py api_thumbtack_capture_contact` → `delete_item(card_id)`) or a terminal dismiss. If DJ captured the contact by another path, or a job was made, the card went stale forever.

## Fix: `routers/thumbtack.py` → `clear_resolved_captures()`
Deletes any active `thumbtack_capture:*` feed card whose lead is RESOLVED:
- partner has BOTH `email` and `phone` (a TT lead arrives with only a proxy phone and NO email — TT never sends email — so an email present means a human captured real contact), OR
- a `sale.order` exists for the partner (company 1) = a job was made, OR
- flow state `real_captured` is stamped.
Cheap: no-ops instantly when no capture card is active; one batched `res.partner.read` + one `sale.order.search_read` otherwise. Zero Claude calls. Skips cards already `declined`/`done` (leaves DJ's terminal decision alone).

## Two call sites (both required)
1. `thumbtack.sweep_72h()` — hourly server-side APScheduler sweep.
2. **At HUD build** — `feed.py` `_hud_build_reap()` is called at the top of BOTH `/api/feed/list` and `/api/feed/live_list` (deferred `from routers.thumbtack import clear_resolved_captures`, fail-safe). So the card clears on DJ's next HUD open regardless of which list endpoint the HUD uses now or after the live_list flip.

## Context (Lead's 3-part HUD live-derive plan; this was part #1, the quick win)
Part #2 = migrate producers to `feed_live.live_list()` + flip the HUD read `/api/feed/list`→`/api/feed/live_list` (already built as preview). Part #3 = move HUD derived reads onto Render Postgres caches (I7). Separate later spec: HUD heat/decay+neglect (reuse the Idea Board decay curve — it's server-side in `ideas.py _effective_heat`, NOT the static JS). Feed store = one `ir.config_parameter` blob keyed by item_id → {item,status,snooze_until,updated}. See [[project_idea_board_venture_boards]], [[feedback_hud_cards_live_not_inbox]], [[feedback_durable_watcher_not_session_cron]].
