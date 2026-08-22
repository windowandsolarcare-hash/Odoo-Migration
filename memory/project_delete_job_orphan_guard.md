---
name: project_delete_job_orphan_guard
description: "Delete endpoints auto-close orphaned reactivation leads — /api/delete_job + /api/delete_so detect a graveyard lead by workiz uuid and flip it Lost, else plain delete."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-09T15:34:10.159Z
---

Deleting a reactivation graveyard job used to orphan its crm.lead: the booked job flips the lead to **Won** (stage 4), so deleting the SO alone left the lead falsely "Won" pointing at a job that no longer exists.

**Fix (dashboard.py, 2026-08-09, commit ebdd482):** shared helper `_close_orphaned_reactivation_lead(uuid, source)` (defined just above `api_delete_so`). It searches `crm.lead` where `x_workiz_graveyard_uuid == <SO's workiz uuid>`; any matching lead not already Lost gets `stage_id=6` (Lost) + `x_workiz_graveyard_uuid=False` + `x_workiz_graveyard_link=''` + a chatter note. Wired into BOTH `/api/delete_job` (uses input uuid or the SO's `x_studio_x_studio_workiz_uuid`) and `/api/delete_so/{so_id}` (reads the uuid field, calls after unlink).

**Key design (DJ's exact ask):** it's a smart check, not a separate flow. If the deleted job is NOT a reactivation graveyard job, nothing matches and it's a **pure no-op** — a normal delete stays a normal delete. Only when an orphan would be created does the cleanup run.

Reactivation crm.lead stages: **5=Attempt1-Sent, 4=Won, 6=Lost**. Graveyard fields on crm.lead: `x_workiz_graveyard_uuid`, `x_workiz_graveyard_link`, `x_odoo_contact_id`, `x_historical_workiz_uuid` (historical uuid is NOT cleared — keep the reactivation history). See [[project_reactivation_sent_book]].

**Terri Jones (2026-08-09):** first real case, done by hand before the code fix — SO 004409 (uuid HOPRZB) deleted, crm.lead 225 flipped Won→Lost, graveyard link cleared, note "customer declined — found another provider". Contact + historical uuid PEBCD1 left intact.
