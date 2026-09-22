---
name: feedback_move_the_ball_decide_correct_at_test
description: "★ Don't wait on DJ's yes for REVERSIBLE build/design/wording calls — make the sensible call, ship it, DJ corrects at test. 'Move the ball 5 yards.'"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-22T15:20:21.927Z
---

★ **For reversible build/design/wording decisions, DON'T gate on DJ's yes — make the sensible call, move forward, and let DJ correct it when he tests it.** Forward progress beats waiting on approval. "I need the five-yard move. There's no reason why you're waiting on a yes. Let's just correct it on the back end when I test it."

**Why:** DJ 2026-09-21 (in the truck, being asked to approve template wording, personalization, speed-fix greenlights one by one). He'd rather we PICK a reasonable option and ship it: when he tests and something's wrong (e.g. we'd chosen "window cleaning" instead of personalizing), he'll say "that's not right, let's redo" — and THEN we discuss the better option. "At least the ball got moved. Five yards didn't get across the first-down line, but it got five yards." Waiting on his yes makes him the bottleneck on things he'll catch at test anyway.

**How to apply:**
- Default to DECIDE-AND-PROCEED on anything reversible/correctable that DJ will see or test before it's truly live: wording, personalization, layout, which quick-fix first, build sequencing, design choices. Make the call, ship it, tell him what you chose in one line. He redirects at test if needed.
- ★ **This INCLUDES "want me to build X?" — DON'T ASK IT for obvious functionality.** DJ 2026-09-22 (2nd time, mildly frustrated): I kept asking "want me to build the family-alert / appetite tracking?" — for an eldercare app, a family alert when Mom falls or reports a bad symptom is OBVIOUS. "These are obvious... even if you make the decision and it's wrong, it's all reversible, I'll test it and say I don't want that... don't lose that functionality because it's waiting on me." So: an obvious missing feature or a plainly-needed safety/functionality gap = JUST BUILD IT, place it sensibly, tell him — do NOT surface it as a yes/no question. Losing/deferring obvious functionality because it's "waiting on DJ" is the failure. Asking a needless build-permission question is the same bottleneck as waiting on a yes.
- ★ **Never let obvious work get BURIED.** DJ's related worry: needed things "get buried in our stuff and we don't surface it like we should." Everything requested/discovered goes on the running open-item trackers (MOMS_CARE_BOARD.md + the W&SC DISPATCH_BOARD.md) with owner + status — and Dispatcher can hand DJ a clean "everything open" list on request. Nothing waits silently.
- This is the football model: keep advancing. A wrong-but-reversible choice that moves forward > a correct choice that waited hours for a yes.
- **The hard stops that STILL wait for DJ** (do NOT auto-proceed): an actual send OUT to a customer (text/email/link — still his HUD press, [[feedback_customer_sends_through_dj_hud]]), money movement, anything irreversible/destructive, and anything only DJ knows (business facts, content, account decisions).
- When you do decide, say so plainly ("I went with X — flag it at test if you want it different"), don't bury it.
- Reinforces + extends [[feedback_escalate_to_dj_sparingly]], [[feedback_raise_bar_on_dj_alerts]], [[feedback_ship_dont_park]]; pairs with [[feedback_roll_into_next_question]] (when a genuine DJ-only decision IS needed, one at a time, roll straight through).
