---
name: feedback_hud_single_workspace
description: "★ GOVERNING: the HUD is DJ's ONE workspace — surface the important/actionable item from every 'room' (feature/screen) as a HUD card with an action button that executes via that feature's OWN endpoint. DJ shouldn't have to visit each room."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-22T15:45:48.134Z
---

★ **The HUD is DJ's single place to work. He should NOT have to walk into each "room" (screen/feature/page) he's built — the important, relevant, ACTIONABLE item from every room should surface IN the HUD as a card with an action button, and the button executes via that feature's OWN endpoint** (so any logic built behind it runs). DJ works FROM the HUD.

**Why:** DJ 2026-09-22. "There's a bunch of rooms I built all over the place. I don't want to have to go to each room — it's too time-consuming, too hard to remember. I want the information that's important, that's relevant in that room, to come through my HUD, and I just want to work in my HUD, one place." First instance: the nightly Meditate habit shouldn't just alert — it should put a HUD card with a ✅ Done button that hits POST /api/planner/checkin (marks done + keeps the streak) so DJ never opens the Daily Planner to do it.

**How to apply:**
- When building/reviewing ANY feature, ask: what's the ONE important, time-relevant, actionable thing a user needs from this room right now? Surface THAT into the HUD as a card with a button — don't make DJ navigate to the room.
- The HUD card's button calls the feature's CANONICAL ENDPOINT (per [[feedback_assistant_use_app_workflow_not_raw_api]] + [[feedback_reuse_canonical_endpoint]]) so built-in logic (streaks, side effects, next-step spawns) runs — never a raw shortcut.
- Design the HUD to be EXTENSIBLE: a "rooms → HUD" pattern where any feature (planner habits, maintenance, reminders, inbound-triage, payments…) can contribute actionable cards that call back to their own endpoints. Meditate is the first; more rooms will feed it.
- Pairs with the HUD live-derived + fire/decay work ([[feedback_hud_cards_live_not_inbox]]): cards compute from live state, order by heat/recency, drop when resolved, force decisions when neglected.
- This is the HUD analogue of [[feedback_never_send_dj_to_odoo]] (the app is the UI, never send DJ to Odoo): here, the HUD is the workspace, never make DJ hunt through separate screens for what's actionable now.
