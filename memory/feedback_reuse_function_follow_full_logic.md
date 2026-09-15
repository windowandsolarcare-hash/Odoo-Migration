---
name: feedback_reuse_function_follow_full_logic
description: "Reusing/keeping ANY existing app function = follow its FULL logic, every unique step — never a simplified re-implementation. DJ's carefully-built owner flows are the reference of truth."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 561c5d7a-5bd6-416a-8a5e-02c57aaed43d
  modified: 2026-09-15T03:23:56.157Z
---

DJ (2026-09-15, during the tech-app build): **"Look at my app carefully — we spent a lot of time getting this correct. If we chose to keep a function we must follow the logic. Lots of unique steps associated with a function."**

**Why:** The owner app (field/payment/charge flows) was built and debugged over months; each function carries many non-obvious unique steps that all exist for a reason (side effects, snapshots, status writes, chatter, next-SO spawn, edge cases). When a NEW surface (the tech app) reuses one of those functions, a simplified/happy-path re-implementation silently drops those steps and ships a subtly-wrong flow that looks fine in a demo. Concrete miss this triggered: the tech app's **Credit** payment just recorded method='Credit' as PAID — but DJ's owner app's Credit path **actually RUNS the card charge** (the at-door credit flow → `doChargeAtDoor` → Stripe). "Book paid, no charge" was wrong; Credit must run the real charge.

**How to apply:**
1. Before wiring any reused owner function into a new surface, **TRACE the owner path end-to-end** — the exact endpoint/fn it calls and EVERY side effect (charge, invoice/payment records, pricing/gate snapshots, chatter, status writes, next-SO spawn, the JobAmountDue=0/Status handling, etc.). Replicate ALL of it.
2. **REUSE the canonical function**, don't re-implement or simplify (ties to [[feedback_reuse_canonical_endpoint]]). Don't map a rich flow down to a bare record.
3. This is the same spirit as the platform-migration rule (copy ALL functionality 1:1, only change what the new platform technically requires) and rules 10/11 (never drop/rewrite working logic). Applies to payment especially — money-touching, post the traced flow to Lead for QC BEFORE shipping.
4. Treat DJ's existing owner flows as the **reference of truth** — if the new surface behaves differently from the owner app, the new surface is wrong until proven otherwise.
