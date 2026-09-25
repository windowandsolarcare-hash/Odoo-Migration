---
name: feedback_deploy_cadence_nightly_window
description: "★ STANDING RULE (DJ 2026-09-25, SUPERSEDES the once-nightly rule): deploy cadence = ~3h EVENT-DRIVEN batches during DJ's day (ship QC'd work when ready AND ~3h since last deploy; no empty windows, no waiting for night) + an EXPEDITE lane for Operator/live-ops + customer-facing blockers (ship as soon as QC'd + money-checked). Guardrails UNCHANGED: Dispatcher money-checks every push (no mid-payment deploy), NEVER stack restarts (space ≥ a few min), QC before ship — those (not frequency) are what stabilized it."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-25T14:53:12.025Z
---

# Deploy cadence: ~3h event-driven batches + expedite lane (SUPERSEDES nightly)

*(The slug still says "nightly_window" for link-stability — other memories/docs reference it — but the RULE is no longer nightly.)*

**DJ directive, 2026-09-25** — supersedes the 2026-09-23 once-nightly-window rule:

1. **Regular QC'd fixes/features ship in BATCHES ~every 3 hours during DJ's day, EVENT-DRIVEN:** ship when work is ready AND ~3h have passed since the last deploy. Do NOT fire empty windows; do NOT wait for night.
2. **★ EXPEDITE lane:** Operator / live-ops + customer-facing blockers ship **as soon as QC'd + money-checked** — don't wait for the ~3h window. DJ: "anything through Operator I need now."
3. **GUARDRAILS UNCHANGED (these are why it stabilized — NOT the frequency):**
   - Dispatcher **money-checks every push** — no deploy mid-customer-payment ([[feedback_no_deploy_during_customer_payment]]).
   - **NEVER stack restarts** — space ≥ a few minutes after a deploy. (The 502s were caused by STACKING + payment-window deploys, not by frequency, so a ~3h cadence is safe with these held.)
   - **QC before ship.**

**How to apply:** default answer to "can we push X?" is now "QC it → Dispatcher money-check → ship in the next ~3h batch, OR expedite now if it's Operator/live-ops/a customer-facing blocker." Route deploy-clears to Dispatcher as usual. Ties to [[feedback_token_budget_discipline]] (batch-and-ship keeps churn down). Mirror to Odoo-Migration/memory/.
