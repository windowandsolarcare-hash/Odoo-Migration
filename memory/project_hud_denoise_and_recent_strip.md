---
name: project_hud_denoise_and_recent_strip
description: "HUD de-noise (badge = card COUNT not sum; 19 inbox_ai cards → ONE 'Inbox — N need you' rollup; clear-once) + recent-thread strip above every send draft (GET /api/inbox/recent, shown in wsc_sendbox + _openSendBox)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-08T00:29:08.526Z
---

**HUD de-noise (DJ 2026-08-07 — "70 is way too high", same people in multiple lists):**
1. **FAB badge = COUNT of live cards**, not the sum of each card's inner badge. `feed.py /api/feed/badge` → `len(list_items())` (list_items already excludes done/snoozed/expired). Each card keeps its own inner badge; only the 🚀 total changed.
2. **19 per-customer `inbox_ai:*` cards → ONE rollup** `📥 Inbox — N need you` (id `inbox:queue`, opens v2_inbox). sms.py: new **`_sync_inbox_card()`** (N = `_needs_reply_count()`; deletes at 0; PURGES legacy `inbox_ai:*`). `_inbox_ai_card` now = triage + light the inbox thread + `_sync_inbox_card()` then `return` (the per-customer card branches below are SUPERSEDED/unreachable). "A customer texting lives in the Inbox only" — DJ handles reply/reschedule/cancel in the inbox thread (intent buttons), not per-customer HUD cards.
3. **Clear-once:** `_sync_inbox_card()` re-runs on `/api/inbox/send`, `/api/inbox/status`, `_inbox_ai_resolved`, and `/api/inbox/list` load → N drops, card removed at 0.
Existing 19 cards purge on the next inbound text or when DJ opens the inbox.

**Recent-thread strip (DJ 2026-08-07 — "anytime I send a text I want to see the last text above it, come to me, don't make me look"):**
- NEW **`GET /owner/api/inbox/recent?so_id=&partner_id=&phone=`** (sms.py) → `{recent:[{dir,body}] last ~3, norm}` (resolves phone→partner→so_id).
- Rendered as a compact in/out bubble strip ABOVE the draft in **wsc_sendbox.js** (`_recentHtml`) AND **v2_field `_openSendBox`** (async-injected when `opts.so_id`). Tap → opens the inbox thread (`v2_inbox.html?c=<norm>`).
- REMAINING: reminder-texts cards (v2_maint_comms — LEAD's file, mailed) + followups.py cards (mine, next) should render the same strip via `/api/inbox/recent`.

Both DJ-approved via lead spec. See [[project_wsc_sendbox_shared]] [[project_inbox_intent_buttons]] [[feedback_multiagent_collision_field_html]] (reminders.py/sms.py = hot shared files).
