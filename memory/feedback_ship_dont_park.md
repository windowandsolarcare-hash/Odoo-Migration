---
name: feedback_ship_dont_park
description: "★ Bias to SHIP code, not park it — solve the request and engineer AROUND blockers; never freeze/stall the queue on an obstacle"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-19T06:23:42.665Z
---

★ **The goal is to SHIP code, not park it.** Solve the problem/request and **work AROUND** whatever's in the way — never freeze, stall, or park the whole queue waiting on a blocker.

**Why:** DJ 2026-09-18. Specialists imposed a deploy-hold "until Bob pays," which parked A7's fix, the Timeline work, and Memory Pillar slices — on a blocker that wasn't even real (Bob had never been sent a working link). DJ: "The goal needs to be to ship code not park it. Solve the problems (requests) and tell them to work around it." A self-imposed freeze that stalls delivery is the anti-pattern.

**How to apply:**
- Hit a blocker (deploy-timing conflict, a dependency, a risky shared file)? **Engineer around it** — sequence, feature-flag, isolate, time the one risky moment — and keep shipping everything else. Don't halt the queue.
- A safety constraint is a *targeted* guard, not a blanket freeze: e.g. "don't deploy at the exact second a customer's payment link is being sent" is one narrow moment to avoid, NOT a reason to freeze all deploys for hours.
- Default to forward motion: solve the request, deploy it, QC it. Parking is the exception, and it needs a real, current reason — not a hypothetical.
- Dispatcher: when a session proposes to park/freeze, push back — ask what the actual live blocker is and whether it can be worked around instead.
- Does NOT override the real safety rules ([[feedback_customer_sends_through_dj_hud]], surgical edits, no removing working code) — those govern HOW you ship, not WHETHER you keep moving.
