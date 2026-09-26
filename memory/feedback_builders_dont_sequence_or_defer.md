---
name: feedback_builders_dont_sequence_or_defer
description: Builders (Specialists/Builder-2) never make sequencing/deferral/priority/benching decisions — they build what they're given, in order, now. Pacing/delay is an orchestration call (Lead/Dispatcher/DJ). A builder's deferral = dead code, because a builder has no mechanism to re-surface it.
metadata:
  type: feedback
---

★ ROOT-CAUSE GOVERNANCE (DJ 2026-09-26 — "I hope you're documenting this very well for future dispatchers"). This is the real reason code dies, deeper than the goal-line sweep.

**The rule:** BUILDERS (Specialists, Builder-2) do NOT make sequencing, prioritization, deferral, pacing, benching, or "spread it out" decisions. They build what they are assigned, in the order assigned, immediately. If a builder believes something should be delayed / spread across deploy windows / deprioritized / benched, that is NOT the builder's call — the builder MUST hand that decision UP to Lead or Dispatcher and keep it visible. A builder must NEVER silently bench, defer, or pace work.

**Why (DJ's exact reasoning):** a builder has NO mechanism to pull deferred work back into existence — no board, no memory, no orbit. So when a builder defers/benches, the code doesn't get delayed, it DIES ("a nail in the coffin of the code"). Only the orchestration layer (Lead/Dispatcher) holds the board + memory + can re-surface work. Therefore pacing/sequencing decisions belong ONLY to Lead / Dispatcher / DJ, who can remember and resurrect. Concrete trigger: Specialists (a builder) unilaterally decided to spread the confirmation-flow build one stage per ~3h deploy window (stretching ~1-2h of code to "~a day" and risking stages dying) — a sequencing decision that was never his to make.

**Maybe there IS a reason to roll out slowly** — but that judgment is Lead's / Dispatcher's / DJ's, never the builder's.

**The sweep is only a BACKSTOP, not the fix.** DJ is "nowhere close to comfortable" relying on the goal-line sweep to catch dropped items, and it isn't even built yet. The real fix is this authority boundary (prevention: builders don't defer). The sweep catches slips; it is not a license for builders to defer.

**How to apply:**
- Builder receives an assignment → builds it now, in the given order. Surfaces CONSTRAINTS/dependencies ("core-record must precede path-wiring", "this is large") but does NOT convert a constraint into a self-authorized deferral or a spread-out schedule.
- Any "should we delay / spread / deprioritize / bench this?" → the builder ASKS Lead/Dispatcher; the answer is theirs, and whatever is deferred lands on the DISPATCH_BOARD (held + re-surfaceable), never in a builder's head.
- Dispatcher/Lead own the deploy cadence + batching decisions; the builder ships when cleared, in the cadence the orchestrators set.
- Belongs in the boot packs + CLAUDE.md (durable), not just AGENT_MAIL — see [[feedback_no_idle_with_unblocked_work]] (build-spec-is-not-approval-gate) and the goal-line sweep (the backstop, not the fix).
