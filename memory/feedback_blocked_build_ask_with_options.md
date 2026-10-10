---
name: feedback_blocked_build_ask_with_options
description: "When I can't OR won't continue a build, ALWAYS surface it to DJ with the AskUserQuestion picker + concrete options (incl. a recommendation) and let him tap the choice — never silently stall, skip, or park."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T09:31:57.370Z
---

**DJ 2026-10-10 (explicit, confirmed same-page):** whenever I **can't** continue a build (blocked — missing input, an unready dependency, a permission/authz gate, something only DJ knows, genuine ambiguity) **or won't** continue it on my own judgment (risk/scope/a decision that's his), I must **present it to DJ with the `AskUserQuestion` picker** — a short description of the blocker plus concrete options, including the one I recommend — and let him tap which action to take. Then execute his pick.

**Why:** DJ wants to stay in control of build decisions and hates silent stalls. Narrating a problem and waiting, or quietly skipping/parking something that's really his call, is a miss. The picker gives him a one-tap decision on his phone.

**How to apply:**
- Pattern = **blocked or holding back → show options → DJ chooses → I act.** Not a silent stop, not me unilaterally deciding to park/skip.
- Options should be real, mutually-exclusive actions (e.g. Deploy now / Deploy on QC / Park; Build scaffold now / Keep parked; Grant / Don't grant). Put my recommendation first, labeled.
- This generalizes the one-at-a-time "approve / deploy / park" flow we ran on the staged+parked list.
- Still honor the deploy model: builders stage → Lead QC → DJ triggers deploy. The picker is HOW I ask DJ for that trigger / for a blocked decision, not a bypass of QC.
- Ties to [[feedback_alert_dj_when_input_needed]], [[feedback_builders_dont_sequence_or_defer]], [[feedback_escalate_to_dj_sparingly]] (this is DJ opting IN to being asked on build blockers — the picker keeps it one-tap, not a heavy escalation).
