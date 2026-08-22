---
name: project_hud_feed_ordering
description: "HUD feed card order (feed.py list_items): urgency band → dollars → NEWEST-first within the band. A newly added card surfaces at the TOP of its urgency group, not the bottom. DJ chose this 2026-08-05."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T14:26:31.345Z
---

**HUD card ranking (routers/owner/feed.py `list_items` / `_rank_key`):**
Order = **(1) urgency** (interrupt → today → glance) → **(2) dollars** (higher first) → **(3) newest-first** within that band.

- Implementation: `_rank_key` returns `(urg, dollars)` only. `list_items` does a **two-pass stable sort** — first `sort(key=created, reverse=True)` (newest first), then `sort(key=_rank_key)`. Python's stable sort preserves the created-desc order within equal (urgency, dollars).
- **Why:** DJ 2026-08-05 — "I need anything new added to the HUD to appear at the top." Before this, the third sort key was `created` ASCENDING (oldest-first), so a new card slotted BELOW older same-priority cards and he'd miss it. He explicitly chose **newest-first WITHIN priority** (NOT strictly-newest-first) — a true interrupt still leads; a new low-priority card does NOT jump above an emergency.
- **How to apply:** do NOT revert the tiebreaker to oldest-first. If a card must pin to the very top regardless of age, give it `urgency:'interrupt'` (and optionally high `dollars`), not a created hack.
