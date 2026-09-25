---
name: feedback_deploy_cadence
description: Deploy cadence — batch every ~3h (event-driven, not nightly), Operator/live-ops blockers expedite immediately; keep money-check + no-stacking + no-mid-payment guardrails
metadata:
  type: feedback
---

Deploy cadence (DJ 2026-09-25, SUPERSEDES the earlier once-nightly rule):
1. Regular QC'd fixes/features ship in batches roughly **every ~3 hours** during DJ's working day — EVENT-DRIVEN (ship when something's ready AND ~3h since last deploy), never fire an empty clock window. Don't wait for night.
2. **Operator / live-ops + customer-facing blockers = EXPEDITE lane**: ship as soon as QC'd + money-checked, no waiting for the window. DJ: "anything that's coming through Operator, those are things I need now."
3. Guardrails UNCHANGED (these stabilized the app, not the low frequency): Dispatcher money-checks every push (no deploy while a customer is mid-payment), NEVER stack restarts (space each by several minutes), QC before ship.

**Why:** DJ found once-a-day too slow — too many things he hits during field work need answers now. The 2026-09-23 502 instability came from STACKING restarts + deploying during payment windows, NOT from deploy frequency itself, so a ~3h cadence is safe as long as the guardrails hold.

**How to apply:** batch-and-ship on the ~3h/expedite model; route deploy-clears to Dispatcher. See [[feedback_no_deploy_during_customer_payment]] and [[project_render_log_filter_no_regex]] (the money-check method).
