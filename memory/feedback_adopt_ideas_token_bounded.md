---
name: feedback_adopt_ideas_token_bounded
description: "When adopting outside suggestions (Gemini etc.) to improve the fleet, implement the bounded, token-cheap version — never an unbounded complex system."
metadata:
  node_type: memory
  type: feedback
  originSessionId: f9d25f0d-f892-4864-829e-2fda94efd70c
  modified: 2026-10-11T20:03:13.450Z
---

DJ (2026-10-11) uses Gemini to bounce ideas and bring in new solutions, but warned there is a balancing act: it is easy to go overboard and build a complex system that burns tokens. Enact the suggestion in a form with a CEILING on token use.

**Why:** single Max plan near its weekly limit; fleet of ~9 sessions compounds token burn. The win from an idea is lost if its upkeep costs more than the problem.

**How to apply:** when evaluating/routing an outside idea, adopt the minimal version (e.g. a 3-5 line ripple list, not a long analysis; a hard gate at QC, not per-turn checks; AI runs on tap, not on every item). Prefer structural gates (cheap, durable) over per-turn LLM policing. State the token cost/ceiling when proposing. Ties [[feedback_token_budget_fleet]], [[feedback_lazy_on_demand_not_prefetch]].
