---
name: project_cheryl_workspace_hud_pattern
description: "DJ's design directive for the Cheryl/DJ workspace: it must be a HUD (always-live, never stale), with activity-GROUPED cards (not flat lists), and an alert-and-teleport superpower that brings the room to you instead of making you tour destinations."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-04T17:46:27.148Z
---

**DJ's HUD vision for the DJ+Cheryl workspace (stated 2026-09-04, driving).** DJ likes his field-app HUD and wants the SAME pattern to be the front door of Cheryl's cloud workspace. Three non-negotiables:

1. **It's a HUD, not a dashboard — ALWAYS LIVE, never stale.** It checks things all the time and updates all the time. "Nothing stale, so it needs to be BUILT that way." This is the anti-decay principle again (see [[project_cheryl_workspace_blueprint]] §4.0) applied to the surface, not just the store.

2. **Activity-GROUPED cards, not flat item lists.** Like his HUD: a card says "hey, there are 4 things here that need to be done" — ONE card per activity with a count/summary, NOT four separate line items. Listing every item "gets too messy." Group into activities → drill in from the card.

3. **Alert-and-teleport "superpower" — bring the destination to ME.** As the workspace grows they'll "build rooms all over the place" (modules/destinations in Cheryl's cloud's app). DJ does NOT want to GO to each room to check it — too cumbersome for him OR Cheryl. Instead: the HUD **alerts him there's a problem, then transports him straight to the room to deal with it** ("boom, it takes me to the room"). The room comes to you; you don't tour the rooms. That IS the heads-up display.

**Why:** DJ's governing dislike is orphan standalones + cumbersome navigation ([[feedback_never_send_dj_to_odoo]], blueprint "no standalones unless hooked together"). The HUD is the UNIFYING attention-routing layer that stops the workspace from becoming N disconnected rooms nobody visits. It's the seed already present in Cheryl's-cloud Workbench "what's waiting on you" top section — this extends it into the always-live, grouped, alert+teleport pattern.

**How to apply:** treat the HUD as a first-class pillar in blueprint v2 (the attention/routing layer over all modules). Reuse DJ's existing field-HUD pattern, don't reinvent. Key constraint to solve (Lead flagged to Cheryl's cloud): "always live" is hard in a published-artifact context (CSP blocks outbound calls; artifacts can't poll) — so live-ness needs either the ERP endpoint (server-side) or a republish-on-change model; the §4.0 stale-surface check is a natural HUD alert source. DJ asked Lead + Cheryl's cloud to design the solution together.
