---
name: feedback-dispatcher-speed-offload-bookkeeping
description: "Dispatcher speed target ~1 min/turn; answer DJ first, offload slow GitHub/board bookkeeping to a scribe helper."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37ab6931-9f7f-4820-ae3e-c45ec4a17730
  modified: 2026-09-18T16:54:52.451Z
---

Dispatcher is DJ's always-available front desk — his channel to Dispatcher must stay open, so per-turn latency is the core KPI. DJ set the target (2026-09-18): keep each Dispatcher turn **under ~1 minute** of thinking/latency. A minute is fine; CONSISTENT overage is the alarm that Dispatcher is doing something INLINE it should be routing or handing to a helper.

**Why:** DJ was once blocked ~3 minutes while Dispatcher did GitHub bookkeeping inline (reading/rewriting DISPATCH_BOARD.md, retrying a failed push, posting AGENT_MAIL). That mechanical plumbing must never sit in front of DJ.

**How to apply:**
- **Answer DJ FIRST** (text streams immediately), THEN do the writes — or hand them off.
- **Offload slow/multi-step GitHub writes** (board updates, mail posts, memory pushes, closing/adding A-rows) to a general-purpose scribe subagent with exact paths + compare-and-swap instructions. Dispatcher stays free; the scribe reports back one line.
- Serialize board edits through ONE scribe (never run concurrent PUTs on DISPATCH_BOARD.md → 409s).
- Fast single SendMessage nudges/routes are fine inline (<1s). Reading code, querying Odoo, long analysis, batched gh writes → always a helper.
- Consistent turns >1 min = signal to route/offload harder, not to make DJ wait. See [[feedback_lead_delegate_dont_do]].
