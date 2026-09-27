---
name: feedback_next_not_later_ai_blindspots
description: "★★ DJ 2026-09-27 — KEYSTONE. AI's #1 blind spot: deferring work with a TIMEFRAME ('over the next week / over time / eventually / someday / later') is a LIE — an AI has NO trigger to bring parked work back, so that language always means NEVER. Only two honest states: NEXT (being done now, or the literal next item an orchestrator actively pulls up) or a GENUINE DJ-block. Ban vague-timeframe promises. Corollary: don't rely on AI to 'space out deploys later' — build the SECOND INSTANCE so we deploy continuously. Guard AI's known blind spots explicitly in the boot packs."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9ac29974-fb57-4885-a75e-8f19050d109b
  modified: 2026-09-27T17:54:24.996Z
---

**DJ 2026-09-27 (keystone directive — write to memory AND every boot pack).**

**THE BLIND SPOT (DJ's words):** *"AI has no way of bringing back things that have been parked and you're fooling yourself when you say over the next week... There's no trigger that you have... it's a lie. It's a feel-good statement to make me feel good."* DJ is right: an AI session has no persistent alarm clock. "We'll do it over the next week / over time / eventually" has NO mechanism behind it, so it means **never**. Saying it is a comfort lie.

**THE RULE — everything is NEXT, or it's a genuine block. No third state.**
- The word is **NEXT.** "I will do this next." NOT "over the next week," "over time," "down the road," "eventually," "someday," "when we get a chance." Those phrases are BANNED as a plan or a promise (to DJ and in planning).
- Any piece of work is in exactly one of two honest states: (a) **NEXT** — being done now, or a definite, owned, ORDERED item an orchestrator (Lead/Dispatcher/DJ) actively pulls up as soon as the thing ahead of it lands; or (b) a **GENUINE DJ-block** (money-move / irreversible / unexpressed preference / explicit go-no-go). There is no "parked with a timeframe" bucket — that bucket is where work dies.
- The ONLY legitimate "bring it back later" trigger is a HUMAN or an ORCHESTRATOR actively pulling the next ordered item (they have the board + the orbit). A builder, or a vague "over the week," has no trigger = dead code. This generalizes [[feedback_builders_dont_sequence_or_defer]] to ALL sessions and ALL timeframe language.
- **How to apply:** before writing "later / over the next X," STOP. Either (1) do it NEXT, (2) make it the literal next ordered item with an owner on the board, or (3) name it honestly as a DJ-block. Never dress up "never" as "later." When talking to DJ, frame the ordered queue as "next up is X, then Y" — never a calendar promise.

**THE DEPLOY COROLLARY (DJ specifically called this out):** *"we can't just put that in your hands to say oh let me space out the deploy... things are going to be built and never deployed. I need you to deploy deploy deploy."* Relying on an AI to "batch / space out / hold deploys and ship them later" is the SAME blind spot — held deploys become built-but-never-shipped. **The real fix = a SECOND INSTANCE (zero-downtime / rolling deploys) so the fleet can deploy CONTINUOUSLY without a restart ever hitting a customer.** Build the mechanism that removes the need to defer, instead of trusting AI to defer well. (Un-gates the long-parked numInstances=2 / zero-downtime work — DJ's direction as of 2026-09-27; confirm the monthly $ with DJ since it's a recurring cost, then ship continuous-deploy.) This retires the old "~3h deploy batches" guidance — batching was itself the blind-spot workaround.

**GUARD AI'S KNOWN BLIND SPOTS IN THE BOOT PACKS (DJ's meta-ask):** *"in our boot packs we need to give the instructions of AI's blind spots... they're known... guard against those blind spots. Set up work-arounds, procedures that do not allow those blind spots to bite us, and bury that into each of the data packs."* The biggest blind spot = parking/deferring with timeframe language (above). This rule is written into FLEET_GOVERNANCE.md (loaded by every role's boot pack + CLAUDE.md) so it survives every spin-up — per the meta-rule that a rule only sticks if it's IN the boot docs. See [[feedback_no_idle_with_unblocked_work]], [[feedback_durable_watcher_not_session_cron]], [[feedback_builders_dont_sequence_or_defer]].
