---
name: Never remove or comment out working code without DJ approval
description: Commenting out or deleting existing working code requires DJ's explicit approval first — adding code is fine, removing is not
type: feedback
---

NEVER comment out, delete, or disable existing working code without DJ's explicit approval first.

**Why:** This codebase was built over months, debugged, and agreed to work. Every line exists for a reason that may not be obvious in the moment. Removing code unilaterally — even with good intentions, even "temporarily" — can silently break things that took significant effort to get right. The `update_sales_order_date` calls in Phase 3 were commented out with a plausible-sounding reason ("date_order now set at creation time") that turned out to be wrong, causing a recurring date bug.

**How to apply:** Adding new code, new features, new logging = fine, do it. But if you think existing code should be removed or commented out, STOP — explain to DJ why you think it should be removed and wait for explicit approval before touching it. If in doubt, leave it in and add a comment explaining the concern instead of removing it.
