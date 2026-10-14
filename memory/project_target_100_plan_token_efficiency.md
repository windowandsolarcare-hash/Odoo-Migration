---
name: project_target_100_plan_token_efficiency
description: "DJ 2026-10-13: moving from the $200/mo Max plan to the $100/mo plan; everything built or changed must be token-efficient. Lead's context bloat and \"Lead touches everything\" are the real costs, not \"overload.\""
metadata:
  node_type: memory
  type: project
  originSessionId: f9d25f0d-f892-4864-829e-2fda94efd70c
  modified: 2026-10-14T04:45:30.495Z
---

DJ (2026-10-13): he is trying to drop from the $200/month plan to the $100/month plan. Still on $200 and "looking pretty good", but $100 will be tight, so whatever we build or modify must be token-efficient.

DJ's framing on routing: AI isn't "overloaded" — over 24h it's mostly idle. Lead was too busy to TALK to DJ, which is why Dispatcher exists. The real concerns are (a) Lead's CONTEXT growing too fast when it touches every handoff, and (b) token cost of having Lead touch everything. Balance: Lead knows what's going on without being in every path.

**Why:** the plan downgrade makes token cost a hard constraint, not a nice-to-have.

**How to apply:** before proposing any process, rule, or build, state its token cost/ceiling and prefer the cheapest version. Keep Lead's context lean (details to AGENT_MAIL, nudges only, board for visibility). Ties [[feedback_token_budget_fleet]], [[feedback_adopt_ideas_token_bounded]], [[feedback_lazy_on_demand_not_prefetch]].
