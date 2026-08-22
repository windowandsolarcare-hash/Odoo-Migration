---
name: project_property_rollup_on_sync
description: "SA 955 (Sync from Workiz) rolls up gate/pricing/frequency/type-of-service to the Property master ONLY when the synced job is the property's latest. Field sync repaints meta in place."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ's data model (key):** SO fields = HISTORICAL SNAPSHOT (frozen at the visit); **Property record = CURRENT master** ("roll-up fields"). The master should reflect the LATEST job. See [[project_type_of_service_read_order]].

## ROLL-UP ON SYNC (built 2026-06-15, SA 955 live + GitHub `1_Production_Code/odoo_sa_955_sync_from_workiz.py` commit a597578)
**SA 955 "Sync from Workiz"** (run by the field 🔄 Sync button via `/owner/api/sync_job_from_workiz` → `ir.actions.server.run([[955]])`) syncs the Workiz job → the SO. **Fields it copies (any status incl. Done):** frequency→`x_studio_x_studio_frequency_so`, status, tech, **gate→`x_studio_x_gate_snapshot`**, pricing→`x_studio_x_studio_pricing_snapshot`, notes→notes_snapshot1, job_type, tos→`x_studio_x_studio_type_of_service_so`, lead_source, workiz_link, line items (skipped if a posted invoice exists). Done-only skips: the pricing-mismatch badge + line-item changes when invoiced. **Gate is NOT skipped on Done.**
**NEW roll-up step** (after the header write): if THIS job is the property's most-recent non-canceled `sale/done` job (`partner_shipping_id`, `date_order desc limit 1`, id == record.id), push the CURRENT values UP to the **Property master**: gate→`x_studio_x_gate_code`, pricing→`x_studio_x_pricing`, frequency→`x_studio_x_frequency`, tos→`x_studio_x_type_of_service`. **Non-empty only** (a blank never wipes the master). Older jobs DON'T touch the master (fixing an old visit can't overwrite the current code). Logged to chatter "Rolled up to property (latest job): …".
**Why:** DJ fixed Steve Bluestein's gate in Workiz on last week's Done job (003789) → wanted future jobs to carry it. Sync only wrote the SO snapshot, never the property (5 University Cir stayed old #1910). Now the latest job rolls up. Verified: re-sync of 003789 set property gate='new code #1933', pricing, freq=4 Months, tos=On Request. (DJ wanted the literal "new code" text kept.)

## FIELD SYNC REPAINT (field.html commit 3726644)
The field detail 🔄 Sync used to update the data but NOT repaint the open panel's gate/status/type/frequency — DJ had to close+reopen to see it. Added **`_repaintActiveMeta(job)`** called after sync (alongside `_repaintActiveLines`); the so_history fallback now also returns gate_code/status/job_type/frequency/type_of_service so a past-job sync repaints in place. See [[project_field_sync_button_repaint]].
