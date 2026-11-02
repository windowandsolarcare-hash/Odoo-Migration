---
name: project_intake_property_ok_to_text_selection
description: "res.partner x_studio_x_studio_ok_to_text is a Yes/No SELECTION field, not boolean. Bug FIXED 2026-11-02 (commit c6beb100): /api/intake/property used to 500 on ok_to_text=true; now coerces bool->Yes/No and still accepts 'Yes'/'No'. Verified firsthand."
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-02T21:31:08.040Z
---

**FIXED 2026-11-02 (commit c6beb100, Specialists) — verified firsthand by Operator.** `POST /owner/api/intake/property` with `{"ok_to_text": true}` now returns HTTP 200 and stores `'Yes'` (confirmed: created a throwaway test property, read back `x_studio_x_studio_ok_to_text == 'Yes'`, cleaned up). The endpoint coerces boolean `true`→'Yes', `false`→'No', and still accepts the 'Yes'/'No' strings the UI sends. No need to omit the field any more.

**Original bug (history):** `x_studio_x_studio_ok_to_text` is a **selection** field (valid values "Yes"/"No", not a Python bool). The endpoint (`routers/owner/new_job.py` `api_intake_create_property`) did `vals['x_studio_x_studio_ok_to_text'] = body.get('ok_to_text') or False`, forwarding a raw bool, so `true` → HTTP 500 `ValueError: Wrong value for res.partner.x_studio_x_studio_ok_to_text: True`. Worked around a live booking (Betty Hanna, Del Webb RM) by omitting the field.

**Remaining small gap (noted to Specialists):** there is NO clean REST path to set `ok_to_text` on an EXISTING partner — `/api/customer/edit` whitelists only name/phone/email/street/city/zip, and `update_odoo_contact` is a `/ask` voice-assistant tool, not a plain endpoint. Setting it post-create needs the voice tool or a raw write. Also: `ok_to_text` does NOT gate outbound SMS — `messaging.send` blocks only on opt-out (STOP), do-not-contact, and quiet hours; an unset ok_to_text does not hold a confirmation. See [[feedback_root_cause_not_just_instance]], [[feedback_assistant_use_app_workflow_not_raw_api]].
