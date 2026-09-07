---
name: project_feed_badge_chokepoint
description: "Attention-feed cards: inner `badge` MUST be numeric (it's SUM-rolled outside api_feed_list's try/except → a string badge like 'REPLY' 500s the WHOLE HUD). Two guards: read-side _badge_int (Lead becd7505) + producer-side self-heal at the single write chokepoint submit_item() (Specialists) that coerces badge→int and moves a stray label to `pill`."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-07T01:24:47.967Z
---

**2026-09-06 P0 (DJ's HUD went fully blank in the field).** `GET /owner/api/feed/list` 500'd because a card `operator:reply:16952` had `badge='REPLY'` — a label in a NUMERIC field — and the counts rollup `sum(int(badge)...)` sits OUTSIDE `api_feed_list`'s try/except, so ONE malformed card killed the entire feed.

**Two-layer fix (feed.py):**
1. **Read-side (Lead, becd7505):** `_badge_int(v)` coerces any non-numeric badge → 0 in the list + live_list rollups. Makes a bad card harmless.
2. **Producer-side (Specialists):** the durable Rule-9 fix at the ONE write chokepoint `submit_item()` — before storing, a non-`bool` non-int `badge` is coerced to `int`, and a stray non-empty string label is preserved as `item['pill']` (if not already set). So ANY producer — present, future, or ad-hoc — self-heals; no N-producer hunt needed.

**Facts:** No live producer creates `operator:reply:` cards (grep-clean); the bad card was written ad-hoc during Operator's Clark work that day and was already GONE from the `wsc.feed.items` store by the time it was checked. The HUD renderer `v2_hud.html` reads `+it.badge` (numeric-coerces, only shows if `>0`) and has NO `pill` slot for feed cards, so a string badge never rendered anyway — numeric-at-write is the real fix. Card schema/store: `ir.config_parameter wsc.feed.items`, keyed by card id; stable API = `submit_item()`/`delete_item()`. See [[feedback_question_when_big_picture_wrong]] (one shared chokepoint > N copies).
