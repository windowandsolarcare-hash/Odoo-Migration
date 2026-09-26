---
name: feedback_no_idle_with_unblocked_work
description: "★ STANDING RULE (DJ 2026-09-25): a session NEVER goes idle while it has UNBLOCKED assigned work undone. Idle is permitted ONLY when everything remaining is BLOCKED on DJ (or another party). 'Low-priority' / 'nightly' means done LATER, never dropped — parking an unblocked item forever is NOT allowed. Every session sweeps its own unblocked backlog to done (or QC-staged for the next deploy) and reports anything genuinely blocked-on-DJ so it's parked for a clear reason. This is the upstream fix for the goal-line problem."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-26T06:18:43.994Z
---

# Never idle with unblocked work — "later" ≠ "dropped"

**DJ directive, 2026-09-25.** The launcher "Jump to an app" search fix got marked "low-priority / nightly" and then just sat there dead — the exact goal-line failure DJ is stopping. New rule:

- **A session NEVER goes idle while it has UNBLOCKED assigned work undone.** Work it to done, or QC-stage it for the next deploy batch.
- **Idle is permitted ONLY when everything remaining is BLOCKED** — on DJ (a decision/config/content only he can give) or on another party. Then it's legitimately parked.
- **"Low-priority" / "nightly" = done LATER, never dropped.** Parking an unblocked item indefinitely is not allowed. Low-pri means it rides a later batch, not that it dies.
- **Every session sweeps its OWN unblocked backlog** and works it down; anything that's actually blocked-on-DJ gets REPORTED as parked-for-a-reason (so a real block is visible, not a silent drop).
- **This is an enforcement dimension of the goal-line / open-loops sweep:** an unblocked register item with no owner-activity flags to DJ + Dispatcher. (See [[feedback_deploy_cadence_nightly_window]] for the batch cadence unblocked work ships on.)

## How to apply
Before signing off as idle (🟢 OVER), ask: "Is everything left genuinely blocked on DJ/another party?" If any unblocked assigned item remains, work it (or QC-stage it) first — don't sign off. For Lead specifically: unblocked = ensure every open item is ROUTED to its owner and moving; a design doc awaiting DJ's approval IS legitimately blocked-on-DJ (parked), but an unrouted/idling build item is not. MIRROR to Odoo-Migration/memory/.
