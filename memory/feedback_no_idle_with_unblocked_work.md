---
name: feedback_no_idle_with_unblocked_work
description: "★ STANDING RULE (DJ 2026-09-25): a session NEVER goes idle while it has UNBLOCKED assigned work undone. Idle is permitted ONLY when everything remaining is BLOCKED on DJ (or another party). 'Low-priority' / 'nightly' means done LATER, never dropped — parking an unblocked item forever is NOT allowed. Every session sweeps its own unblocked backlog to done (or QC-staged for the next deploy) and reports anything genuinely blocked-on-DJ so it's parked for a clear reason. This is the upstream fix for the goal-line problem."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-26T06:31:53.541Z
---

# Never idle with unblocked work — "later" ≠ "dropped"

**DJ directive, 2026-09-25.** The launcher "Jump to an app" search fix got marked "low-priority / nightly" and then just sat there dead — the exact goal-line failure DJ is stopping. New rule:

- **A session NEVER goes idle while it has UNBLOCKED assigned work undone.** Work it to done, or QC-stage it for the next deploy batch.
- **Idle is permitted ONLY when everything remaining is BLOCKED** — on DJ (a decision/config/content only he can give) or on another party. Then it's legitimately parked.
- **"Low-priority" / "nightly" = done LATER, never dropped.** Parking an unblocked item indefinitely is not allowed. Low-pri means it rides a later batch, not that it dies.
- **Every session sweeps its OWN unblocked backlog** and works it down; anything that's actually blocked-on-DJ gets REPORTED as parked-for-a-reason (so a real block is visible, not a silent drop).
- **This is an enforcement dimension of the goal-line / open-loops sweep:** an unblocked register item with no owner-activity flags to DJ + Dispatcher. (See [[feedback_deploy_cadence_nightly_window]] for the batch cadence unblocked work ships on.)

## ★ What counts as a GENUINE DJ-block (DJ 2026-09-25 refinement — don't manufacture blocks)
A DJ-block counts ONLY when DJ GENUINELY must decide: a **design direction**, **money**, **customer-facing wording**, or **a preference he's actually expressed**. It does NOT count for **operational sequencing / build-ORDER** — that's the fleet's call to make ourselves. Do NOT manufacture a DJ-block out of a decision we can make.
- Real incident (the origin): Lead parked 4 buildable, ungated customer-facing specs "on DJ" just to get a build-ORDER ranking. DJ: *"why is any of those waiting on me? By the time I say the order, all the code could be written and my answer had no value. You work way faster than I can check. Just do it and when I check in they'll all be done."*
- Rule: if the fleet can decide it (which order, which shared helper, how to structure), DECIDE IT and build — DJ reviews the FINISHED work. Reserve the park-on-DJ for the four genuine categories above. Asking DJ to rank build-order is a FAKE block and violates no-idle just as much as silently dropping the work.

## How to apply
Before signing off as idle (🟢 OVER), ask: "Is everything left genuinely blocked on DJ/another party?" If any unblocked assigned item remains, work it (or QC-stage it) first — don't sign off. For Lead specifically: unblocked = ensure every open item is ROUTED to its owner and moving; a design doc awaiting DJ's approval IS legitimately blocked-on-DJ (parked), but an unrouted/idling build item is not. MIRROR to Odoo-Migration/memory/.
