---
name: feedback_times_in_pacific
description: "Any time told to DJ must be in Pacific time (e.g. \"7:47 AM\"), never UTC; convert logs (UTC) before reporting"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 66a9262c-f30f-42dd-96ba-6b96f344343d
  modified: 2026-09-23T14:56:22.951Z
---

When telling DJ a time, always use Pacific time in plain 12-hour form (e.g. "7:47 AM"), never UTC. Render logs and most tooling are UTC; convert before speaking (PDT = UTC−7 during daylight time, PST = UTC−8 in winter).

**Why:** DJ, 2026-09-23: "don't tell me about it in UTC time. That means nothing to me. I'm not gonna sit there and convert." Timing mattered in the sporadic HUD/inbox debugging, and UTC made it impossible for him to match events to what he was doing.

**How to apply:** Every DJ-facing message and summary uses Pacific time. Peer/fleet messages may keep UTC for log-matching, but anything relayed to DJ gets converted. See [[feedback_spoken_friendly_responses]].
