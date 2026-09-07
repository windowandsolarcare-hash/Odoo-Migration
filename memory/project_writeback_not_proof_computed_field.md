---
name: project_writeback_not_proof_computed_field
description: "Writing a value to an Odoo field and reading it back does NOT prove the field is freely writable — a computed+store=True field accepts and persists a write until a dependency recomputes over it. To prove writability, read ir.model.fields for a `compute`, or write→change a dependency→re-read."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-07T08:19:04.813Z
---

**Write-then-read-back is NOT proof an Odoo field is durably writable.** Caught 2026-09-06 (Cheryl's cloud, on `project.task.progress`): a field declared `compute=... store=True` (a computed *stored* field, especially with an inverse) will ACCEPT a `write()` and PERSIST it — a read immediately after returns the value you wrote — **right up until any dependency changes and Odoo recomputes straight over the top.** So `write(75) → read 75.0` distinguishes nothing; the value silently reverts later, invisible to the test because nothing has recomputed at read time.

**The concrete trap that prompted this:** stock `project.task.progress` is commonly `fields.Float(compute='_compute_progress_hours', store=True)` off `effective_hours` + `allocated_hours` — and `allocated_hours` is the same field the plan payload exposes as `hours`. So a manual "progress" write would revert the moment a timesheet is logged or hours are edited — a user taps a stage and watches it snap back a day later.

**The tests that ACTUALLY prove writability:**
1. ★ THE DEFINITIVE ONE (behavioral): write a value → **change a dependency** on the same record (e.g. `allocated_hours`, or log a timesheet) → re-read. If it moved, it recomputes and a manual write is not durable.
2. Read the field definition — `ir.model.fields` for `compute` — is a WEAKER check and can give a FALSE NEGATIVE: verified 2026-09-06 that `project.task.progress` reported `compute=false, store=true` yet STILL recomputed to `effective_hours/allocated_hours` on an hours change (an override/inverse/onchange not surfaced as `compute`). So `compute=false` does NOT clear a field — only the behavioral test #1 does. Use the field-def read to CONFIRM a suspicion, never to rule it out.

**If the field IS computed:** don't fight it — write the manual value to a **separate stored field** (a custom `x_` field), point the endpoint/read at that instead. The UI doesn't change, only which field is touched.

**★ CONCLUSIVELY RE-RUN 2026-09-07** (Cheryl's-cloud progress-control blocker, throwaway task, cleaned up): task with `allocated_hours=10`, wrote both `progress=75` and `x_manual_progress=75` → read back 75/75; then **changed `allocated_hours` 10→20** → re-read: **native `progress` reverted 75.0 → 0.0**, **`x_manual_progress` stayed 75.0**. So `project.task.progress` is NOT durable and `x_manual_progress` IS. The live control already writes `x_manual_progress` (goals.py `set_task_progress`, served on `/cheryl/api/task/progress`) → Cheryl's 5-stage progress persists. See [[project_phase2_workspace_verified]].

**Why:** third "verification insufficiency" gotcha on this stack, all the same shape — *a positive result from the obvious test doesn't mean what it looks like.* Siblings: [[project_odoo_200_not_success]] (200 ≠ success — denied assets serve a 200 placeholder) and [[project_401_not_route_exists]] (401 ≠ route-absent — the auth wall answers before routing). Add this: **write-back ≠ writable for a computed-stored field.** General rule for this project: prove a claim with a test that can actually *fail* for the reason you care about, not one that passes for an unrelated reason. Lead over-claimed "writable confirmed" here off a write-back and was corrected — verify at the definition/behavior level, not the surface.
