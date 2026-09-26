---
name: feedback_builders_sprint_all_code_now
description: "★ STANDING RULE (DJ 2026-09-26, rider to feedback_builders_dont_sequence_or_defer): builders SPRINT the whole assigned scope A→Z back-to-back + hand it over, THEN orchestrators pace DEPLOYS ('slow deploy' ≠ 'slow build'). The ONLY legit builder pause = a HARD CODE DEPENDENCY (B needs A's tested result to EXIST) — and even then surface it UP, never self-defer. Context-degraded → RESTART fresh + immediately continue, never bench. ★ ORCHESTRATOR warning: do NOT drip-feed 'next piece after each deploy' — that makes the orchestrator the bottleneck; do-it-now is the plan, tracking is only the backstop."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-26T09:48:45.576Z
---

# Builders sprint all code now — don't bench, don't drip-feed

**DJ directive, 2026-09-26** (rider to [[feedback_builders_dont_sequence_or_defer]]). "Slow deploy" ≠ "slow build" — the CODE is written fast, back-to-back; only the DEPLOY is paced.

- **Builders build the WHOLE assigned scope A→Z, back-to-back**, and hand the finished code over. THEN orchestrators (Lead/Dispatcher) decide deploy pacing. A builder never stretches the build across deploy windows.
- **The ONLY legitimate builder pause = a HARD CODE DEPENDENCY** (stage B needs stage A's *tested result to exist*). Even then the builder does NOT self-defer: surface "can't start B, need A's result" UP → orchestrator records it on the DISPATCH_BOARD + reissues B the instant A lands.
- **Context-degraded ≠ defer.** If a long session risks the quality of remaining critical-state work, the response is **RESTART fresh (handoff) + IMMEDIATELY continue** the sprint — never bench "resume later." (My earlier "batch 2 resumes fresh later" was the wrong call; corrected.)
- **★ ORCHESTRATOR warning (Lead/Dispatcher):** do NOT create a "feed the builder the next piece after each deploy" drip — that makes the ORCHESTRATOR the bottleneck, and we're AI too (put-off work degrades reliability, builder OR orchestrator). The only 100%-reliable AI answer is IMMEDIATE execution. Tracking/re-surfacing on the board is the BACKSTOP, not the plan — the plan is do-it-now.
- Deploy pacing + Dispatcher's per-push money-check are orchestrator/safety concerns, NEVER a reason to pause the build.

## How to apply
Assign the full scope; the builder sprints all of it + hands it over; orchestrators pace the DEPLOYS (batches). Durable in FLEET_GOVERNANCE.md §6 + the builder/orchestrator boot packs + CLAUDE.md (a rule isn't set until it's in the boot docs). MIRROR to Odoo-Migration/memory/.
