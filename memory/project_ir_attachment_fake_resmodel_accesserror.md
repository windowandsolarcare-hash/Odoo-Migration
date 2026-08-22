---
name: project_ir_attachment_fake_resmodel_accesserror
description: Creating an ir.attachment with a res_model that is not a real Odoo model throws AccessError on upload
metadata: 
  node_type: memory
  type: project
  originSessionId: ac2aeda5-6609-487b-94e3-132715d60520
---

Creating an Odoo `ir.attachment` with `res_model` set to a **made-up model name** (one not in the Odoo registry, e.g. `'owner.reference'`) throws `odoo.exceptions.AccessError: Sorry, you are not allowed to access this document.` at create time — Odoo runs an access check against the "linked" record's model and fails because the model doesn't exist.

**Why:** ir.attachment validates access to whatever res_model/res_id it points at. A real model (`sale.order`, `res.partner`, `hr.employee`) passes; an app-invented pseudo-model does not.

**How to apply:** For attachments that belong to a JSON-backed pseudo-record (Reference cards live in `ir.config_parameter`, not a model), create the attachment **standalone** — only `name`, `type:'binary'`, `mimetype`, `datas`. Track the returned `att_id` yourself and serve it by id via `/owner/api/attachment_image` (reads `ir.attachment` by id, ignores res_model). Do NOT set res_model/res_id to a fake model.

Hit on the Reference app (`routers/owner/reference.py` attach endpoint) 2026-06-28 — it had `res_model:'owner.reference'`; failed on first real upload. Fixed by dropping res_model/res_id. The dashboard.py job-attachment path (`res_model:'sale.order'`) is fine because sale.order is real. See Reference app = `static/owner/reference.html` + `routers/owner/reference.py` in repo windowandsolarcare-hash/saunders-render-app (deploys wsc-field-assistant).
