---
name: Reactivation Attempt 2 Design
description: Planned but not yet built — Attempt 2 follow-up text for non-responders to Attempt 1
type: project
originSessionId: bde61778-fbed-44ee-8f60-90475187f32a
---
Attempt 2 follow-up SMS for reactivation non-responders. Design agreed, not yet built.

**Why:** People who didn't respond to Attempt 1 (pricing given) need a closing nudge. They didn't STOP, just didn't reply.

**Trigger:** 40 days after x_studio_last_reactivation_sent on res.partner
**Cadence:** Daily automated run — picks up anyone hitting 40-day mark that day
**Stage:** Move CRM opp from "Attempt 1 - Sent" (ID 5) to new "Attempt 2 - Sent" stage
**After Attempt 2:** TBD — DJ to decide, nothing automated yet

**How to apply:** When DJ says "build Attempt 2", create: new CRM stage, daily Odoo server action (or Zapier schedule), SMS text focused on closing (pricing already seen, now nudge to book). Use x_studio_last_reactivation_sent + 40 days as filter.
