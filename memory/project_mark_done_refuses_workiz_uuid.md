---
name: project_mark_done_refuses_workiz_uuid
description: "Odoo-native Mark Done (/api/set_block_status) REFUSES any SO with a Workiz UUID — blocks ~96% of real jobs (79/82 upcoming) from being marked Done + spawning the next maintenance job, now that Workiz is retired."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T20:53:10.349Z
---

**How a job is marked Done in Odoo (post-Workiz), and the blocker.** Found 2026-08-06 tracing DJ's payment→Done→next-job flow.

The Odoo-native "Mark Done" = the job ⋯-menu "✅ Mark Done" (`markBlockDone` in v2_field.html) → **`POST /owner/api/set_block_status {so_id,done}`** (dashboard.py L8828). On done it:
1. writes `x_studio_x_studio_workiz_status = 'Done'`,
2. rolls the SO's gate/pricing SNAPSHOT up to the PROPERTY master (`x_studio_x_gate_code` / `x_studio_x_pricing`),
3. calls **`new_job.create_next_maintenance_so(so_id)`** (new_job.py L443) — the Odoo-native "Phase 5": a finished MAINTENANCE job spawns its next one. Returns `next_so_id`.

So the full pipeline (mark Done + create next visit) IS rebuilt Odoo-native. BUT set_block_status **REFUSES any SO with a Workiz UUID**: `if x_studio_x_studio_workiz_uuid: return "This job is linked to Workiz — set its status in Workiz, not here."` That guard predates the Workiz retirement (2026-08-03) and is now obsolete + actively blocking.

**Scope (Odoo query 2026-08-06, company 1):** upcoming not-Done jobs from today = **82 total, 79 have a Workiz UUID → REFUSED** (only 3 work). Overall state sale/done = 2788, of which 2753 carry a UUID. So Mark Done is blocked for ~96% of real jobs. The OTHER mark-done path — the `mark_job_done` AI tool (dashboard.py/field.py) — still does `workiz_post(job/update, Status='Done')`, i.e. writes to dead Workiz. So there is currently NO working Mark Done for a normal migrated job → the whole "job Done → next maintenance visit created" cycle is stuck.

**Also:** `_execute_payment` (dashboard.py, used by BOTH the job-screen Record-Payment button AND the paywatch Approve card) records invoice+payment only — it does NOT mark Done or create the next job (that never lived in the button; it rode the Workiz+Zapier Phase 5/6 chain, which died with Workiz). It also still front-runs `_sync_so_with_workiz` (a Workiz call) as a hard gate. Journal is hardcoded to **6 = Chase Checking** for ALL methods — that's CORRECT by design (DJ: Zelle journal obsolete, all Zelle goes to Chase). See [[project_sched_lifecycle_one_page]].

**RESOLVED 2026-08-06 (DJ rule): a customer job isn't Done until PAID IN FULL.** So "done" and "paid in full" are the same moment — done is now payment-driven, not a manual tap. Shipped in dashboard.py:
- `_execute_payment` (used by BOTH the job-screen Record-Payment button AND the paywatch Approve card): after registering the payment, if the invoice `payment_state in ('paid','in_payment')` (full) → writes `x_studio_x_studio_workiz_status='Done'`, rolls gate/pricing snapshot up to the property, and calls `create_next_maintenance_so(so_id)`. A PARTIAL payment does none of it — job stays not-Done, on the schedule to collect later. This works regardless of Workiz UUID (the payment path has no UUID gate), so it unsticks the 79 blocked jobs going forward — recording their full payment closes them.
- `set_block_status` (manual ⋯ "Mark Done") NO LONGER spawns the next job — it's now just Personal Time's green-dot toggle. Its Workiz-UUID refusal was LEFT IN PLACE (customer jobs are closed by payment, not this toggle).
- `_sync_so_with_workiz` NOW DISABLED everywhere (DJ 2026-08-06 "remove it everywhere"). Neutered at its single definition (dashboard.py ~L10429) with an early `return {'ok': True, 'synced': False, ...}` — body kept dead. It's the ONLY definition; every caller (both payment paths `_execute_payment` L4332 + field.py L3193-which-already-NameError'd-into-except, plus sync/refresh/batch endpoints L9754/9807/10115/12958) now proceeds without touching Workiz. Removed the pre-payment Workiz call that (a) dragged stale Workiz data back over DJ's Odoo edits (the 004557 revert), and (b) hard-BLOCKED payment when the Workiz job had no tech. Verified on John 004557 (SO 17389): Workiz job still live w/ tech 'Dan Saunders' — sync would have run + risked revert; now bypassed.

**DEFERRED (DJ: "deal with those later, bring up when I ask what's next"):** a one-time catch-up sweep to mark already-fully-paid but still-un-Done jobs Done + create their next visits. See [[project_pending_catchup_paid_undone_sweep]].

**Same theme — another stale Workiz-UUID gate (fixed 2026-08-07):** the v2_field ⋯-menu **"🔁 Reschedule"** item was gated `if(uuid && soid)` → HIDDEN on Odoo-native jobs with no Workiz UUID (e.g. Ed Dismukes' next-maintenance SO 264940, created by create_next_maintenance_so). DJ couldn't reach the reschedule day-planner. Fixed → `if(soid && customer!=='Personal Time')` (reschedule is Odoo-native now — no UUID needed; Personal Time keeps its own "📅 Move / Reschedule"). LESSON: legacy `uuid`-gated UI on Odoo-native jobs is a recurring bug class as Workiz retires — audit other `if(uuid` guards when a feature "disappears" on a new job.
