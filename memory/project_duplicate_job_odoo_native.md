---
name: project_duplicate_job_odoo_native
description: "Customer Brain 'Duplicate job' is now ODOO-NATIVE (was Workiz — dead). Clones the source SO in Odoo (customer/property/line items/gate/service copied), with two choices: Create as Submitted (draft) or Create & Schedule (confirm onto the calendar). No Workiz, no clipboard-paste."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T05:00:28.624Z
---

**Was (broken):** `/api/duplicate_job` (dashboard.py) fetched the source job FROM Workiz, created a NEW Workiz job via server action 1338, copied line items to the clipboard, and opened Workiz to paste. All dead post-Workiz-retirement. DJ flagged it 2026-08-05 ("Create duplicate in Workiz — doesn't look right").

**Now (Odoo-native, dashboard.py `api_duplicate_job`):** reads the source `sale.order` and creates a NEW SO in Odoo:
- Copies: `partner_id`, `partner_shipping_id`, **order_line** (each line `(0,0,{product_id,name,qty,price})`, skips display_type notes), `x_studio_x_gate_snapshot`, `x_studio_x_studio_type_of_service_so`, `x_studio_x_studio_frequency_so`. Overrides `x_studio_x_studio_x_studio_job_type` with the picked type. `date_order` = picked PT date/time → UTC (job start). `x_studio_x_studio_workiz_status='Submitted'`.
- Body: `{so_id, job_type, date, time, schedule}`. **schedule=true** → `action_confirm` + write date_order back (confirm resets it) → lands on the schedule. **false** → stays draft 'Submitted' for review. DJ wanted BOTH as choices.
- Returns `{ok, so_id, so_name, amount_total, scheduled}`. No Workiz, no clipboard.

**Frontend (v2_customers.html):** Duplicate sheet now has TWO buttons — **📋 Create as Submitted** (`doDuplicate(false)`) and **📅 Create & Schedule** (`doDuplicate(true)`). Removed the Workiz open + `copyDupItems` clipboard flow (copyDupItems left as dead code). Verified live end-to-end (create + delete).

**SO NAME — FIXED 2026-08-05:** duplicate now sets `name` via the shared **`new_job._next_job_name(date_str)`** helper (agreed **YY + climbing counter** scheme, e.g. `264938` = 2026 + counter 4938), NOT Odoo's default `S00xxx`. Lazy-imported (`from .new_job import _next_job_name`), passes the PT service date; falls back to Odoo's S-sequence only if the helper/sequence is down. Counter = ir.sequence `wsc.job.seq` (shared with new_job; was at 4937, next 4938). Verified live: dup got `264938`. See [[project_so_numbering_post_workiz]], [[project_status_label_vs_so_state]], [[project_confirmed_so_line_edit]].
