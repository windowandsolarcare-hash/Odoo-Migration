---
name: SO date_order is always the job START time
description: date_order on sale.order always = Workiz JobDateTime (start) in UTC — never end time, never date_deadline
type: project
---

SO `date_order` is always set to the Workiz `JobDateTime` (start time) converted to UTC. This has been the rule since the beginning of the project.

**Why:** The schedule display, the Render field assistant app, and all date-based reporting rely on `date_order` being the start time. Using the end time causes jobs to appear at the wrong time slot.

**How to apply:** Whenever writing `date_order` on a sale.order — whether in Phase 3, Phase 4, a manual fix, or any other context — always use `JobDateTime` → `convert_pacific_to_utc()`. NEVER use `JobEndDateTime`, task `date_deadline`, task `planned_date_end`, or any other end-time field.

Workiz fields:
- Start time: `JobDateTime` → maps to SO `date_order` and task `planned_date_begin`
- End time: `JobEndDateTime` → maps to task `date_deadline` / `date_end` only
