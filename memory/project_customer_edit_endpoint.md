---
name: project_customer_edit_endpoint
description: "POST /owner/api/customer/edit (brain.py) = the CANONICAL app path to edit a customer's basic res.partner fields (name/phone/email/street/city/zip). Whitelisted fields only, refuses non-W&SC partners (company_id not in [1,False]), audit-logs each change to the partner's chatter. Operator/voice/UI use THIS, never a raw res.partner write."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-07T07:01:49.299Z
---

**Built + QC'd 2026-09-06 (Lead-greenlit), brain.py.** Closes a real gap surfaced by the Mark→Darcella Seiler widow update: there was NO Render pathway to EDIT a customer's name/phone/email — intake routes only CREATE, brain/job writes the SO — so Operator (charter = app-endpoints-only) had to hand the raw res.partner write to Specialists. Per the governing rule ([[feedback_never_send_dj_to_odoo]] — DJ never touches Odoo, every field needs a Render pathway; [[feedback_assistant_use_app_workflow_not_raw_api]] — ops go through app endpoints), this is now the canonical edit path.

**`POST /owner/api/customer/edit`** — Body `{partner_id, name?, phone?, email?, street?, city?, zip?}`.
- **Whitelist ONLY** `_CUST_EDIT_FIELDS = ('name','phone','email','street','city','zip')` — any other body key is ignored (QC-proved: an `x_gate_code` in the body was not written). No arbitrary field writes.
- **W&SC guard:** reads `company_id` first; refuses if `company_id not in (1, False)` → can NEVER touch Cheryl (2) / Saunders (3) contacts (QC-proved: a company-2 partner was refused, unchanged). Matches the res.partner rule `company_id in [1, False]` (W&SC contacts are mostly False/shared).
- **Diff-only + idempotent:** computes the real diff vs current; a no-op returns `{ok:true, unchanged:true}` and writes nothing.
- **Audit-log:** posts a chatter note to the partner `"✏️ Contact edited via app by <who> | field: old -> new | ..."`, `who` = `session_actor(request)` ('dan'/'cheryl'/None→'app'). (Odoo escapes the `->` to `-&gt;` in chatter — harmless, readable; plain-text pipe format per [[feedback_chatter_format]].)
- Whole body guarded → a bad partner/id degrades to a clean error, never a 500.

**Use it for every customer rename / phone / email / address fix** (death, marriage, new number, typo) — Operator and any future voice tool call THIS, never a raw write. Lives in brain.py next to /api/job/set_service + /api/job/set_job_type (imports `from routers.authz import session_actor`). See [[project_maint_headsup_ack_combo]] (the Seiler update that surfaced the gap).
