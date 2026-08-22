---
name: project_pending_catchup_paid_undone_sweep
description: "DEFERRED one-time sweep — jobs already fully paid but never marked Done (Workiz-retirement gap) need Done + next-visit created. DJ said bring it up when he asks \"what's next\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T01:10:43.580Z
---

**Pending / deferred task (DJ 2026-08-06).** When the Workiz→Phase5/6 chain died over the Aug-3 weekend, some jobs got worked and paid but never got marked Done and never spawned their next maintenance visit. Going forward the paid-in-full closeout in `_execute_payment` handles this automatically (see [[project_mark_done_refuses_workiz_uuid]]), but the ones already fully paid + still un-Done need a ONE-TIME catch-up:

- Find company-1 sale.orders that are effectively PAID IN FULL (posted invoice `payment_state in ('paid','in_payment')`) but `x_studio_x_studio_workiz_status != 'Done'`.
- For each: mark Done, roll gate/pricing snapshot up to property, and call `create_next_maintenance_so` (idempotent via `wsc.maint.next_created.<so_id>`; maintenance-only).
- Review the list with DJ BEFORE running (he wants no surprises — "so nothing surprises you").

**DJ's instruction:** "deal with those few past jobs later. bring them up when I ask, what's next." → Surface this proactively when DJ asks "what's next" / for the backlog. Do NOT run it unprompted.
