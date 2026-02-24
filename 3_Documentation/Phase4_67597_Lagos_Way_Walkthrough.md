# Phase 4 Walkthrough — 67597 Lagos Way (Workiz UUID `UJ4S1W`, Odoo SO `004126` / `so_id=16899`)

## Odoo ⇄ Workiz logic map (for this case)

| Step | Source Event/Data | Phase 4 Action | Destination Effect | Result in this case |
|---|---|---|---|---|
| 1 | Workiz status webhook (`job_uuid`) | Fetch full Workiz job by UUID | In-memory payload for routing | `UJ4S1W` fetched |
| 2 | UUID lookup in Odoo | Search `sale.order` by Workiz UUID field | Existing SO path or create path | Existing SO found (`004126`) |
| 3 | Existing SO found | Update SO fields (date/frequency/type/etc.) | `sale.order.write` | SO write succeeded |
| 4 | Existing SO found | Update Property fields from job | `res.partner.write` (property) | Property write succeeded |
| 5 | Existing SO found | Run task sync from SO + job | `project.task.write` | **Failed** on tags FK |
| 6 | Task sync payload | Copy SO `tag_ids` to task `tag_ids` | M2M relation update | Included deleted/missing tag id (`10`) |
| 7 | Odoo DB constraint | Reject invalid tag relation row | FK violation | Zapier step reports `ValidationError` |

## Step-by-step execution path in `zapier_phase4_FLATTENED_FINAL.py`

1. **Entry point receives `job_uuid`** from Zapier and loads Workiz job fields (`Status`, `SubStatus`, dates, team, tags, etc.).
2. **Phase 4 skips only `Submitted` status**; this job is `Pending`, so processing continues.
3. **Search by Workiz UUID** finds existing SO (`004126` / `id=16899`), so it enters the update branch, not create branch.
4. **`update_existing_sales_order(...)` builds SO update payload** (date/job metadata/etc.) and writes to `sale.order`.
5. **After SO write succeeds**, function calls task sync (`sync_tasks_from_so_and_job(...)`) to keep FSM task aligned with Workiz date/team/customer/tags.
6. **Task sync reads SO fields** including `tag_ids`, and if any exist, it sets task payload to `tag_ids=[(6,0,[...])]`.
7. **Task write to `project.task` fails** because one SO tag ID in payload (`10`) no longer exists in `project_tags`.
8. Odoo returns `ValidationError` / FK violation `project_tags_project_task_rel_project_tags_id_fkey`, which is exactly the error shown in Zapier logs.

## Why this breaks now

- SO update and property update are fine.
- The failure is isolated to **task tag synchronization** (SO tags → task tags) when SO contains a stale tag reference.
- That means Phase 4 currently does one extra thing you may not need for this migration pass: enforcing tag parity onto tasks.

## Practical fix options (in order)

1. **Fastest (recommended for immediate operations):** disable task tag sync in Phase 4 so task updates still happen for assignee/date/phone without touching tags.
2. **Safer long-term:** before task write, validate SO tag IDs against existing `project.tags` and write only valid IDs.
3. **Data cleanup adjunct:** remove stale tag IDs from affected SOs/tasks so tag sync can remain enabled.

## Direct answer to your earlier question (Step 6/7 behavior)

- If Phase 4 **finds existing SO**: yes, SO update occurs, property update occurs, and task sync runs.
- If Phase 4 **does not find SO** and falls back to Phase 3 create path: property updates are handled in Phase 3 creation flow, but this Phase 4 file does **not** run the same post-update task sync block after that create return.
