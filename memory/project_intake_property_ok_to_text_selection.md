---
name: project_intake_property_ok_to_text_selection
description: "res.partner x_studio_x_studio_ok_to_text is a SELECTION field, not boolean — /api/intake/property passes the raw ok_to_text value straight through, so sending True errors \"Wrong value for ...ok_to_text: True\". Omit it (or send the correct selection string)."
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-02T21:24:11.102Z
---

Hit 2026-11-02 (Operator) creating a new customer property via `POST /owner/api/intake/property`. Passing `{"ok_to_text": true}` → HTTP 500, Odoo `ValueError: Wrong value for res.partner.x_studio_x_studio_ok_to_text: True`.

**Why:** `x_studio_x_studio_ok_to_text` on res.partner is a **selection** field (its valid values are selection strings, e.g. "Yes"/"No" — not a Python bool). The endpoint (`routers/owner/new_job.py` `api_intake_create_property`) sets `vals['x_studio_x_studio_ok_to_text'] = body.get('ok_to_text') or False` — it forwards the raw value, so a boolean `True` reaches a selection column and is rejected. `False` is accepted only because Odoo reads it as "unset."

**How to apply:** When creating a property through `/api/intake/property`, **omit `ok_to_text`** (safe — stores as unset) rather than sending `true`. To actually set it, send the correct selection string, not a bool.

**Systemic (flagged to Specialists 2026-11-02):** the endpoint should map a truthy `ok_to_text` to the proper selection value instead of forwarding a raw bool — otherwise the New Job / new-customer UI's "OK to text" toggle 500s whenever it's checked. Instance worked around by omitting; root-cause fix is Specialists' (owns `new_job.py`). See [[feedback_root_cause_not_just_instance]], [[feedback_assistant_use_app_workflow_not_raw_api]].
