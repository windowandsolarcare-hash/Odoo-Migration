---
name: feedback_durable_foundation_over_shortcut
description: "DJ wants FOUNDATION/vision work built durable-first, NOT the cheap temp version by default. Surface shortcut-vs-durable tradeoffs EXPLICITLY before choosing, and let DJ decide. He's seen the shortcut get defaulted more than once."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-15T20:53:40.026Z
---

DJ 2026-09-15 (Memory Pillar convo): he learned the brain's records sit on a v1 **JSON-blob backend** (one `ir.config_parameter` JSON document per store, loaded/rewritten whole) rather than a true indexed/relational DB — the "start simple, swap the DAL to Render Postgres later" pattern in `memory_store.py`. His core vision (records, not Vault document-search) DID get built; but the durable, scale-proof STORAGE foundation he pictured is the deferred upgrade, not the current base. He's concerned — and says it's a REPEAT pattern — that the fleet **defaults to the cheap/temporary shortcut** when he asked for a lasting foundation, so the long-term intent gets "lost in translation" (built to the literal ask, not the vision).

**Why:** When DJ frames something as a foundation / his vision, he ASSUMES it's built to last and that "I want X" is understood as intent, not a literal minimal spec. A silent shortcut violates that trust, and he shouldn't have to micromanage implementation to get durability.

**How to apply:**
1. For anything DJ frames as foundational / core / "the vision," do NOT silently pick the minimal-working option. **Surface the shortcut-vs-durable tradeoff** (cost, scale ceiling, upgrade path) and let DJ decide BEFORE building.
2. Treat "I want X" on a foundation as "build X to LAST," not "the quickest thing that technically does X."
3. The real constraint that pushed the shortcut here was legit: CLAUDE.md hard rule **"no new Odoo custom models"** → JSON-in-config was the no-new-model path; a true DB = a separate Render Postgres (deferred). Name the constraint honestly rather than pretend it was free choice.
4. The DAL abstraction (`memory_store.py`) DOES let the backend swap to Postgres without rewriting the brain — so upgrading later is real; but the decision to STAY on the shortcut should be DJ's, made with full info, not defaulted.
5. Behavioral root cause to own: AI assistants (incl. me) bias toward the least-complex path that satisfies the literal request unless durability/scale is made an explicit requirement. Counter it by weighting "5–10 years from now" on foundational asks by default.

Links: [[feedback_question_when_big_picture_wrong]] (STOP and ASK when the shape looks wrong), [[feedback_planning_constraints]] (no new Odoo models / one instance — the constraint behind this), [[feedback_escalate_to_dj_sparingly]] (this IS a case worth surfacing — a foundational tradeoff is DJ's call).
