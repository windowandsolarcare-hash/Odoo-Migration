---
name: feedback_token_budget_fleet
description: "DJ hits weekly Claude limits — no ack messages, short peer msgs, no big browser test suites (phone telemetry measures for free), idle sessions silent"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 66a9262c-f30f-42dd-96ba-6b96f344343d
  modified: 2026-09-24T05:11:42.460Z
---

Token budget rules for the whole fleet (DJ, 2026-09-23, approaching his weekly limit on the $200 plan):
1. No acknowledgement messages ("copy", "holding", "standing by"). Message only for a result, a decision needed, or a problem.
2. Peer messages ≤5 lines; details go in a doc and the message links to it.
3. No large browser-automation suites. A 50-cycle desktop test cost ~150–190K tokens per run; post-deploy smoke tests of all 48 pages cost ~140K. Use phone telemetry instead (it runs on Render/Postgres and costs zero Claude tokens), and limit post-deploy checks to the 2–3 touched screens.
4. Idle sessions stay silent: no heartbeats or status pings.
5. Smallest query that answers the question; don't re-read big files that are already summarized.
6. Use cheaper subagents for routine lookups.

**Why:** DJ: "I increased to 200 to get more tokens… I'm approaching my weekly limit again." Some of these rules already existed but weren't followed.

**How to apply:** Before spawning an agent or sending a peer message, ask whether it's necessary and how small it can be. See [[feedback_peer_message_brevity]] and [[feedback_dispatcher_terse_replies]].
