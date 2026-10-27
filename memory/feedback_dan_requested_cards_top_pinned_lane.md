---
name: feedback_dan_requested_cards_top_pinned_lane
description: "A HUD/card Dan explicitly ASKS for goes to a top pinned lane (single card, immediate), never buried in the automated attention feed; system-generated cards stay in the feed."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-27T15:14:23.930Z
---

When Dan EXPLICITLY ASKS for a HUD/card for a specific thing, it is pinned as a SINGLE card at the TOP of the HUD — a dedicated **pinned lane above the automated attention feed** — one glance, one tap, drops when actioned. System-GENERATED cards (auto-confirmations, attention items, badges) stay in the general feed; that's correct. **The distinction is the SOURCE:** Dan-requested → top pinned lane; system-generated → general feed.

**Why:** when Dan asks for a card he wants it RIGHT NOW, often while driving — burying a specifically-requested item among ~28 feed items / 226 badges makes him dig for the thing he just asked to see. Origin 2026-10-27: Dan blocked in the field wanting Linda Willingham's Nov 17 confirmation as a top single card, not dug out of the confirmations pile.

**How to apply:** any build for a Dan-requested card renders it in the pinned top lane, live-revalidated (drops when sent/actioned), backed by a durable pin source (not a hardcoded single card — the lane is general). Any customer-send action on such a card STILL obeys the §9 absolute: opens the thread PRE-FILLED, never one-tap-send. Instituted in `3_Documentation/roles/FLEET_GOVERNANCE.md` §8c. Ties [[feedback_hud_cards_live_not_inbox]], [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_route_dj_questions_to_dispatcher]].
