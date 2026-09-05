---
name: project_operator_plays
description: "DJ's \"plays\" — short spoken shortcuts that trigger a whole Operator operation. DJ says the play name, Operator runs the complex flow, asking numbered one-tap clarifying questions only when needed. Blessed by DJ 2026-09-05 (v1 vocabulary)."
metadata: 
  node_type: memory
  type: project
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-05T05:32:19.954Z
---

DJ says a short name → Operator runs the whole operation (per [[project_operator_playbook]] recipes) in ONE pass, with DJ's tone/timing instincts ([[feedback_dj_operating_instincts]]) baked in. When a detail is missing, ask a **numbered one-tap question** ("reply 1/2/3") — DJ answers with a single keystroke. Always review-then-send; never auto-send.

## v1 PLAYS (blessed 2026-09-05 — DJ can rename/add anytime)
- **"referral"** → new customer: intake search (dedupe) → create contact + property → create Submitted job (price TBD) → reserve tap-to-book slots (batch to an existing run if one's near) → draft the warm pitch card in DJ's HUD. Ask up front: which day(s)/how hard to push if unclear.
- **"quote in" / "quote out"** → push a price onto the CURRENT (picked) job's line items (in&out vs outside), set the job-type label. (Uses the quote-push build once shipped; until then, /api/job/lines.)
- **"photos"** → place the send-job-photos card for the named job (DJ selects + sends).
- **"move"** → reschedule a job (ask new day/time if not given; offer route-best slot).
- **"confirm day"** → send the day's confirmations (the 4-day batch / per-job confirm cards).
- **"who responded"** → status of today's (or a day's) confirmations + who replied + any problems.

## HOW TO RUN A PLAY
1. Confirm the target (customer/job) — resolve name→SO id.
2. Gather constraints from their thread/voicemails FIRST; ask ONE numbered clarifying question if a real ambiguity remains (don't over-ask).
3. Execute the WHOLE flow in one pass (don't do it piecemeal across turns).
4. Draft any customer message into DJ's HUD prefilled for review-then-send.
5. Set a follow-up check on the expected outcome ([[feedback_operator_followup_verify]]).

DJ's exact wording for each play is his to set — update this list when he gives new names. Long-term these plays map 1:1 to the Render-Claude voice tools (capability parity).

Related: [[project_operator_playbook]], [[feedback_dj_operating_instincts]], [[feedback_operator_followup_verify]].
