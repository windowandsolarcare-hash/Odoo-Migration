---
name: Phase 6 tech gate — check SO before any action
description: Phase 6 gates on x_studio_x_studio_workiz_tech at start — blocks entire run if no tech assigned
type: project
---

Phase 6 checks `x_studio_x_studio_workiz_tech` on the SO as step 2 (right after finding the SO), before posting payment or touching Workiz. If empty, returns error immediately.

Error message: "SO {name} has no technician assigned. Assign tech in Workiz, run Sync on the SO in Odoo, then re-invoice."

**Why:** Workiz rejects Mark Done with "Must assign technician" if no tech is on the job. Better to catch it at the Odoo level before any payment is posted (avoids needing to delete/recreate invoice).

**How to apply:** If Phase 6 fails with no-tech error: assign tech in Workiz → run Sync from Workiz button on SO → re-invoice. No need to delete old invoice.
