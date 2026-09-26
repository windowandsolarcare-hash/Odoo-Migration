---
name: feedback_restart_sessions_at_fleet_idle
description: Restart/refresh long-context sessions during a FLEET-IDLE window, not while Lead/Specialists (or others) are mid-active-work — swapping a session mid-sprint risks a handoff drop
metadata:
  type: feedback
---

Restart worn-down sessions (esp. the Dispatcher/orchestrators) when the WHOLE fleet is IDLE, not while others are mid-active work. Swapping a session while Lead/Specialists are mid-sprint risks something dropping in the handoff seam (e.g. a pending deploy-clear/money-check going to the outgoing session or being missed during the new one's boot).

**Why:** DJ, 2026-09-26, after swapping the Dispatcher (at 82% context) while Lead + Specialists were mid confirmation-flow sprint: "next time I'll wait until we're at an idle stage for everybody… right now I'm taking you out of the loop of Lead and Specialist who's working away, and something could get dropped with the new dispatcher."

**How to apply:** batch session-restarts into a fleet-idle window. If a restart must happen mid-flight, cover the seam explicitly: notify the sessions still working that the role is being swapped, route their pending clears to the NEW session once it's green (hold if it's not up), and commit the handoff doc before the new session reads it. Idle-window restart avoids all of that. See [[feedback_respawn_session_procedure]] and [[feedback_agent_handoff_via_doc]].
