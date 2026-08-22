---
name: project_delete_audit_and_log_forensics
description: "Job-delete audit trail (render.audit.delete + [DELETE-AUDIT] stdout) and how to forensically trace a deletion: Render log querying (text not path), render.log conversation logs, next_job_date breadcrumb, SO-on-Property gotcha."
metadata:
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**2026-06-11 incident:** DJ deleted Norma Gould's June-16 maintenance job by mistake via the field **3-dot menu → Delete Job** (`POST /owner/api/delete_job`). Tracing WHAT got deleted was hard because the delete left no record. Fixes + the forensic playbook:

## Delete audit trail (added to dashboard.py `_log_delete_audit`)
Every `/api/delete_job` outcome now writes a full job snapshot to TWO places:
1. **stdout** — one line prefixed `[DELETE-AUDIT]` (search Render logs by `text:["DELETE-AUDIT"]`).
2. **Odoo `ir.config_parameter` `render.audit.delete`** — rolling JSON list, last 200 entries. Durable (Render logs roll off). Fields: ts (PT), source (`field_3dot_menu`), result (DELETED/BLOCKED/ERROR/PARTIAL), customer, so_name, uuid, job_type, amount, date_order, detail. Read anytime: `odoo_rpc('ir.config_parameter','get_param',['render.audit.delete'])`.

**In-app view (2026-06-11):** `/owner/deleted_jobs` (static `deleted_jobs.html`) + `GET /owner/api/deleted_jobs?limit=` (reads `render.audit.delete`, newest first). Linked from the owner hub (index.html → Reports group tile "🗑 Recently Deleted"). Shows badge (DELETED/BLOCKED/error), customer, SO#, job type, amount, scheduled date, when deleted, source, detail. Informational only — restore = open customer → Duplicate (no auto-restore). List is empty until the first delete AFTER 2026-06-11 (prior deletes predate the audit).

Asymmetry (intentional): the **voice** delete (`delete_workiz_job` in field.py) was ALREADY traceable — the whole Render Claude conversation incl. the delete tool call + summary is logged to Odoo `render.log.YYYY-MM-DD`. Only the **menu** path was the gap. [[project_delete_job_paired.md]]

## How to query Render logs (this service)
- The web service emits **`type: app`** logs only (uvicorn access lines printed to stdout). It does NOT emit `type: request` logs.
- ⇒ The `path`/`method`/`statusCode` filters on `mcp__render__list_logs` return NOTHING here. **Filter by `text` instead**, e.g. `text:["delete_job"]`, `text:["DELETE-AUDIT"]`.
- Access lines show `"POST /owner/api/delete_job HTTP/1.1" 200 OK` — path + status but **NOT the request body**, so the uuid/customer is NOT in the HTTP log. HTTP 200 also returns on logical failure (the endpoint returns `{ok:false}` with 200), so 200 ≠ confirmed delete.
- Render log retention is short (~days). `render.log.*` (Odoo) and `render.audit.delete` (Odoo) are the durable trails.
- `render.log.*` conversation logs ARE working (verified reading 2026-06-08 → found the Karp voice-delete). Supersedes the old "not working 2026-05-25" note in [[project_render_conversation_log]].

## Recovery breadcrumbs when an SO is hard-deleted (unlink)
- An unlinked `sale.order` is gone (no chatter survives), BUT:
- **`res.partner.x_studio_next_job_date` SURVIVES** — Phase 4 clears it only on Done/Canceled through the normal flow; a hard unlink bypasses that, so it still holds the deleted job's date. Used 2026-06-11 to recover that Norma's deleted visit was scheduled **2026-06-16**.
- Reconstruct service/price from the customer's history (same job_type + amount + cadence).
- **GOTCHA:** SOs link to the **Property child** (`partner_id` = the Property whose `parent_id` is the Contact), NOT the Contact. Searching `sale.order` by the Contact id alone returns 0 — always include the Property children (`parent_id = contact, record_category='Property'`).
- The delete is **invoice-guarded** (refuses if any invoice linked) → a deleted job never had a payment, so nothing financial is ever lost to a delete.
