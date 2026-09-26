---
name: feedback_no_idle_with_unblocked_work
description: A session never goes idle while it has UNBLOCKED work undone; idle is only OK when everything left is blocked on DJ. "Low-priority" means done later, never dropped.
metadata:
  type: feedback
---

Standing rule (DJ 2026-09-25): a session NEVER goes idle while it has UNBLOCKED assigned work still undone. Going idle is only permitted when everything remaining is BLOCKED — waiting on DJ (or another party). "Low-priority" / "nightly" means done LATER in the queue, NOT dropped. Parking an unblocked item indefinitely is not allowed.

**Why:** DJ: "an agent marks it low priority and it dies never to be done… the standing rule is an agent NEVER goes idle without all UNBLOCKED requests done. If it's blocked waiting on me, then OK to go idle." Concrete miss: the launcher search-keyboard fix was logged low-priority and never built. This is the upstream cause of the goal-line problem — items dropped before they even reach the "built but not flipped" stage.

**How to apply:** before going idle, a session checks its backlog: any unblocked item (needs nothing from DJ/another party) must be worked to done or QC-staged for the next deploy batch first. Only genuinely blocked-on-DJ items may be parked, and they're reported as such. This is an enforcement dimension of the goal-line/open-loops sweep: an unblocked item with no recent owner activity flags. Complements [[feedback_deploy_cadence]] (building ≠ deploying — build unblocked work now, ship on the cadence).
