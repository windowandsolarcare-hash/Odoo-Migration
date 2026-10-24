---
name: feedback_park_writes_its_reason
description: "When any session PARKS/defers a task it must WRITE the reason somewhere durable (an AGENT_MAIL 'waiting on X' line or the task note) so a parked task never silently dies. DJ Gemini-brief decision, 2026-10-24 (via Dispatcher)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-24T07:04:37.153Z
---

DJ (Gemini brief, relayed by Dispatcher, 2026-10-24): adopted — a parked/deferred task must record WHY it's parked, somewhere it won't vanish.

**Why:** the App-Building voice feature died after its write-up with NO handoff — it was effectively parked but nobody recorded the reason or the next step, so it silently dropped. A park with no written reason is indistinguishable from abandonment; the next session can't resume what it can't see.

**How to apply:** whenever you PARK/defer anything, write a one-line reason in a DURABLE place — an AGENT_MAIL `→ <role>` / `→ DJ` "waiting on X" line, or the task/board note — naming WHAT it's blocked on and WHO/what unblocks it. Never park only in your head or inside a dead write-up. Folds into every role's boot pack (posted → All 2026-10-24). Pairs with [[feedback_happy_path_e2e_before_dj]] (no multi-step feature is "done" until Audit runs the happy-path pass) and [[feedback_no_idle_with_unblocked_work]] (park only what's genuinely blocked; keep building the rest).
