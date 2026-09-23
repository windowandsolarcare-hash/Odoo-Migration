---
name: feedback_deploy_cadence_nightly_window
description: "★ STANDING RULE (DJ 2026-09-23): STOP rapid-fire deploys. Group all changes into ONE scheduled deploy window per day — nightly 8:07 PM PT, money-checked by Dispatcher — with an emergency exception ONLY for a live break. Batch + QC through the day; flip in the window."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-23T20:46:07.049Z
---

# Deploy cadence: ONE nightly window per day, not rapid-fire

**DJ directive, 2026-09-23** (after a day of ~6+ verified deploys — "it is flying faster than it's ever flown"). Rapid-fire deploys, even when each is gated + verified, are unsettling and stack restart-risk. New standing rule:

- **ONE scheduled deploy window per day: nightly ~8:07 PM PT**, money-checked by Dispatcher before the push.
- **Batch changes through the day**: build + QC + stage everything, but HOLD the push for the nightly window. Multiple ready items ship together in that window (grouped, one restart pass).
- **Emergency exception ONLY for a live break** (something is actively broken for DJ/customers) — then a targeted fix can deploy off-cycle, money-checked.
- **Why:** predictability + fewer restarts + a real settle/telemetry-collect period between deploy days. It complements [[feedback_no_deploy_during_customer_payment]] (money-check each push) and the "let telemetry collect over hours before a 'fixed' call" discipline ([[feedback_no_conclusion_from_single_test_sporadic]]).

**How to apply:** default answer to "can we push X?" is now "stage + QC it for tonight's 8:07 PM window," not "push on the next clear." Lead QCs items through the day → they queue window-ready → Dispatcher money-checks + clears the batch at the window. Only a live break justifies an off-cycle deploy. Written to the fleet BUILD_LOG/AGENT_MAIL so all sessions adopt it. Mirror to Odoo-Migration/memory/ (docs don't redeploy — buildFilter ignores 3_Documentation/**, so a docs/memory push is deploy-safe even under a freeze).
