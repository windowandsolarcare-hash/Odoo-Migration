---
name: feedback_no_deploy_during_customer_payment
description: "Don't run/stack deploys while a customer is mid-payment — a Render redeploy restarts the app (~60-90s) and the in-flight Pay fetch fails, looking exactly like a broken payment link. Hold deploys during active/imminent customer payment windows; don't stack back-to-back deploys."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-19T04:43:49.322Z
---

**Incident 2026-09-18 (Bob Lis, $200 solar).** Right after the A11 authz fix landed, Bob tapped Pay on his (now-correct) Stripe link and got **"Network error."** It was NOT a code bug — `create_checkout` returns a valid live Stripe URL for his exact params (verified 3/3 stable). Root cause: Specialists ran **4 deploys in ~5 minutes** (Memory-Pillar Slice 1 + the authz seam + ENDPOINT_MAP), each a **~60-90s Render restart**; Bob's Pay fetch landed in one of those restart windows and failed.

**The lesson (standing rule):**
- A Render redeploy = the app is down/booting for ~60-90s. **Any in-flight customer fetch during that window fails** and, to the customer, reads as "the link is broken." Highest-stakes on money flows (create_checkout / success / cancel / booking / portal).
- **When a customer is actively paying — or a card/booking link was just texted and they're expected to tap soon — HOLD deploys until they complete.** Announce a deploy-hold in AGENT_MAIL during an active payment window so no session ships mid-payment.
- **Don't stack deploys.** Batch code changes and push ONCE; avoid rapid successive deploys generally (each is another restart window + another chance to catch a customer mid-action). Ties to [[feedback_regression_guard_pushes]] (push discipline) and the pre-push gates.

**How to apply:** before any push, ask "is a customer mid-payment or about to tap a link I just sent?" If yes, wait / coordinate. If you must ship several changes, combine them into one deploy, not four. On a live-money incident, verify the endpoint is stable, then tell the customer to **re-tap the same link** (the transient failure is gone once the app is booted). See [[feedback_render_cron_autodeploy]], [[feedback_regression_guard_pushes]].
