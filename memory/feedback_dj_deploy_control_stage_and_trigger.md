---
name: feedback_dj_deploy_control_stage_and_trigger
description: "★ DJ 2026-09-27 (confirmed): the standing deploy workflow = builders BUILD + STAGE (QC'd, held on a review branch, NOT merged to main); DJ triggers the deploy himself with the word 'deploy' (or 'show me what's staged'). Dispatcher keeps a visible 'READY TO DEPLOY' list on the board + proactively surfaces it so staged work never silently sits. The 2nd instance makes any deploy safe (rolling, no customer disruption). Emergency live-customer fix = flag + ship on DJ's quick okay."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9ac29974-fb57-4885-a75e-8f19050d109b
  modified: 2026-09-27T20:56:38.427Z
---

**DJ 2026-09-27 (confirmed after building the 2nd instance).** How deploys work now — refines the earlier "deploy-deploy-deploy" directive:

**THE MODEL — DJ is the deploy trigger.**
1. DJ says "work on this, don't deploy it" (or it's routine work) → the builder BUILDS it, QCs it, and STAGES it: held on a review branch, **NOT merged to main** (main auto-deploys, so staging = don't merge yet).
2. Staged work goes on a visible **"READY TO DEPLOY"** section at the top of `DISPATCH_BOARD.md`. Dispatcher **proactively tells DJ** when things are stacked up ("you've got N ready whenever you want") so nothing silently sits.
3. DJ says **"deploy"** (or "show me what's staged" → Dispatcher lists them → "deploy") → Dispatcher tells the builder "merge now" → it ships in one go.
4. **EXCEPTION:** an actual live-customer emergency (broken payment/link a customer is hitting) → flag it + ship on DJ's quick okay, don't wait for a batch.

**WHY this (and why it fixes the blind spot):** DJ doesn't trust AI to group/batch/defer deploys on its own — correctly, per [[feedback_next_not_later_ai_blindspots]] (AI has no reliable self-trigger). This model works because **DJ is the trigger** (a reliable human trigger) AND staged work is **visible** (the board list) + Dispatcher surfaces it — so nothing dies parked. Gives DJ control of *when* without the "built but never shipped" risk.

**SAFETY + COST context:**
- **2nd instance is LIVE** (numInstances=2, 2026-09-27) → any deploy is a rolling, health-gated deploy = **never disrupts a customer** (no freeze/broken-link/double-text). So the old "no deploy mid-payment / no stacking / ~3h batching" guardrails are **retired** — deploys are safe whenever. The advisory-lock guard means the scheduler runs on ONE instance only (no double-texting). See [[feedback_next_not_later_ai_blindspots]] deploy corollary.
- **Cost of frequent deploys is trivial:** Render does NOT charge per deploy — it bills **build-minutes** ("pipeline minutes"): ~500/month included on DJ's plan (≈150–200 deploys), then ~$5 per 1,000 min (half a cent/min). DJ's "if it's a small charge I don't mind" — it is small. Deploy freely; cost is a non-issue.

**Net:** Dispatcher no longer auto-ships QC'd work. It STAGES it on the board's Ready-to-Deploy list, surfaces it to DJ, and ships on his word — except live-customer emergencies.
