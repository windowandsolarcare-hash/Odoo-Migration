---
name: feedback_dj_deploy_control_stage_and_trigger
description: "★ DJ 2026-09-27 (confirmed): the standing deploy workflow = builders BUILD + STAGE (QC'd, held on a review branch, NOT merged to main); DJ triggers the deploy himself with the word 'deploy' (or 'show me what's staged'). Dispatcher keeps a visible 'READY TO DEPLOY' list on the board + proactively surfaces it so staged work never silently sits. The 2nd instance makes any deploy safe (rolling, no customer disruption). Emergency live-customer fix = flag + ship on DJ's quick okay."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9ac29974-fb57-4885-a75e-8f19050d109b
  modified: 2026-10-11T18:09:57.386Z
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

**★ REFINEMENT — RELEASE BY DEFAULT (DJ 2026-09-27, later same day):** DJ shifted the trigger: *"we are going to release them unless I say hold or park."* So the DEFAULT is now RELEASE — Dispatcher gives the builder "merge now" for QC'd/staged work automatically, WITHOUT waiting for a per-item "deploy" word from DJ. DJ intervenes only by saying **"hold"** or **"park"** on a specific item (then Dispatcher holds it). DJ can still say "deploy" to push a batch, and "show me what's staged" to see the list. The board's Ready-to-Deploy list + Dispatcher proactively surfacing it still stand (so DJ can hold/park before it ships). Builders keep staging + waiting for Dispatcher's "merge now"; only the DISPATCHER's behavior changed (auto-relay the merge for QC'd items vs waiting for DJ's explicit per-item word). Emergencies still expedite. This is now the operating default; the earlier "ships on his word" is superseded by "ships by default unless held/parked."

**Net:** Dispatcher ships QC'd/staged work BY DEFAULT (auto "merge now"), stops only on DJ's "hold"/"park", keeps the Ready-to-Deploy list visible, and expedites live-customer emergencies.

**★ ADDENDUM — THE OWNING BUILDER FIRES THE DEPLOY PICKER (Dispatcher broadcast + Specialists correction, 2026-10-11, FLEET_GOVERNANCE §12):** When work is QC-green, the deploy is confirmed via an `AskUserQuestion` picker ("Deploy now (Recommended) / Deploy part / Park it" — plain-English what-changes). **The picker MUST be fired by the session that OWNS the branch** (the builder), so DJ's "Deploy now" tap lands DIRECTLY in that session = valid push authorization. **A non-owning session (e.g. HR) must NOT fire the picker for another session's branch and relay the tap — a relayed tap is NOT push authorization** (same anti-relay/anti-permission-laundering principle as the old "DJ types deploy in the builder's own tab" rule). HR/any coordinating session: hand the staged branch to its owner and let the OWNER fire the picker. **Burned 2026-10-11:** HR fired the deploy picker for Specialists' call-log-label branch and relayed "DJ tapped Deploy now"; Specialists correctly refused to ship on the relay and fired its own picker to get DJ's direct tap — which made DJ tap twice for one deploy. For unfinished/blocked work the picker options are "Continue / Give me the info / Park it"; never silently stall.
