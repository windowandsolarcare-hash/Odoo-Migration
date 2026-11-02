---
name: project_ok_to_text_is_selection_not_bool
description: "x_studio_x_studio_ok_to_text (res.partner) is a Yes/No SELECTION field, NOT a boolean — handing it a raw Python bool 500s Odoo. UI sends 'Yes'/'No' strings; API callers may send a bool, so write paths must coerce."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-11-02T21:32:43.458Z
---

**Fact (verified via Odoo fields_get 2026-11-02):** `res.partner.x_studio_x_studio_ok_to_text` ("OK to Text") is a **selection** field with values `[['Yes','Yes'],['No','No']]` — NOT a boolean. Writing a raw Python `True`/`False` to it 500s: `Wrong value for res.partner.x_studio_x_studio_ok_to_text: True`.

**Bug it caused:** `POST /owner/api/intake/property` (routers/owner/new_job.py) did `'x_studio_x_studio_ok_to_text': body.get('ok_to_text') or False` — forwarded the raw request value straight to the selection column. The UI clients (v2_customers.html, v2_new_job.html, _job_detail_panel.js, archived new_job.html) all send the `'Yes'`/`'No'` STRING via `...classList.contains('on')?'Yes':'No'`, so they never broke (a non-empty 'No' string is truthy and passed through). The 500 only fired when a **direct API caller** (Operator building its own POST body) sent a JS/Python **boolean `true`**. Fixed 2026-11-02 (commit c6beb100): a normalize block coerces bool→Yes/No, passes case-insensitive Yes/No strings, blank/missing→False (unset — preserves prior behavior).

**★ The trap to avoid:** a naive `'Yes' if v else 'No'` is WRONG — the string `'No'` is truthy, so it'd map to `'Yes'`. Any coercion must handle bool AND string explicitly (unit-tested 9 shapes incl. `'No'`→`'No'`).

**PARKED low-pri follow-up (Operator flagged 2026-11-02, Specialists' call = park):** there is NO edit path to set `ok_to_text` on an EXISTING res.partner — `/api/customer/edit` (brain.py:620) whitelists only name/phone/email/street/city/zip (`_CUST_EDIT_FIELDS`, brain.py:617) and has no UI control for it. Parked (not built) because: unset is harmless (messaging.send gates on STOP/DNC/quiet-hours, NOT ok_to_text) + no current edit-form toggle, so it's a small multi-file feature, not a one-liner. **★ When built: `/api/customer/edit` does `str(body.get(f)).strip()` on every whitelisted field, so naively adding `ok_to_text` would RE-INTRODUCE this exact 500 (`str(True)`='True'). It needs a Yes/No coercion carve-out there AND an edit-UI toggle.** Verified firsthand PASS on the intake fix (Operator: POST→200, stored 'Yes', cleaned up).

**How to apply:** any NEW write path that sets this field must send `'Yes'`, `'No'`, or `False` (unset) — never a bool. Canonical dashboard.py write paths already do `str(args.get('ok_to_text') or 'Yes')` (string, default Yes). Sibling Yes/No selection fields on res.partner likely behave the same — don't hand any `x_studio_*` selection a bool. Related: [[feedback_no_guessing_on_fields]] (I queried fields_get before fixing), [[feedback_odoo_verify_content_not_status]], [[project_new_job_via_app_endpoints]].
