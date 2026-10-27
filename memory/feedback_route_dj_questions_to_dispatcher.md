---
name: feedback_route_dj_questions_to_dispatcher
description: "Need Dan's input? Route the question to Dispatcher — the single surface he watches — never park a DJ-question in your own session window."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-27T14:58:53.595Z
---

**Dan works ONLY with Dispatcher; it is the single surface he watches.** He does NOT watch other sessions' windows. Any session that needs DJ input — a picker, a decision, a clarification — ROUTES the question to Dispatcher (SendMessage; + AGENT_MAIL →Dispatcher if it must survive a restart). Dispatcher relays the answer back. NEVER leave a picker/prompt sitting in your OWN session window waiting on Dan.

**Why:** a DJ-question parked in a non-Dispatcher window = Dan never sees it and the work silently stalls. Origin 2026-10-27: Operator parked a "Kathy Sell?" question in its own window; Dan found it himself after wondering why things had stalled.

**How to apply:** before you end a turn holding an open DJ-question, ask "is this sitting in my own window?" If yes, route it to Dispatcher instead. One-liner: *"Need Dan's input? Route the question to Dispatcher; never park a DJ-question in your own window."* Instituted in `3_Documentation/roles/FLEET_GOVERNANCE.md` §8b (canonical, every boot pack reads it). Ties [[feedback_alert_dj_when_input_needed]], [[feedback_escalate_to_dj_sparingly]], [[feedback_dispatcher_speed_offload_bookkeeping]].
