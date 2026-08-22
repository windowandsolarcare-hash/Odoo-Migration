---
name: Workiz scheduling toggle quirk
description: Workiz may require going through Submitted status before Send Confirmation - Text works after Calendly booking
type: project
---

When manually scheduling a Calendly-booked job in Workiz, the status change from "API SMS Test Trigger" (reactivation) directly to "Send Confirmation - Text" sometimes requires hitting Save more than once. Possible workaround: change SubStatus to Submitted first (which resets/submits the job), then come back and set "Send Confirmation - Text" — this might allow it to work in one save.

**Why:** Workiz appears to have a quirk where the scheduling toggle and status change don't always commit together in a single save when coming from the reactivation SubStatus.

**How to apply:** This is a future test item only. Current workflow (manual review → schedule → set Send Confirmation - Text) is intentional and preferred because DJ needs to: (1) verify the schedule, (2) know the job exists, (3) add pricing line items. Do not automate this away.
