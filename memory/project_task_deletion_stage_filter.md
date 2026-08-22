---
name: Task deletion on Submitted — stage filter
description: Only delete tasks in New/Planned stages on Submitted status — never touch In Progress or Done
type: project
---

When a Workiz job goes back to Submitted (unscheduled), Phase 4 and sync_action_955 delete linked tasks. Fixed to only delete tasks in stage New (16) or Planned (17).

Tasks in In Progress (18) or Done (19) are protected — they have timer/timesheet data.

**Why:** DJ uses Submitted→Scheduled as a forced re-sync cycle (e.g. price update at the door). Old code deleted ALL tasks including ones with timer data, wiping timesheet records.

**How to apply:** Any task search before unlink must include `('stage_id', 'in', [16, 17])` filter. Both sync_action_955.py and zapier_phase4_FLATTENED_FINAL.py have this fix as of 2026-04-08.
