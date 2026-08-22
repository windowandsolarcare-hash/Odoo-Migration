---
name: project_odoo19_no_mobile_field
description: "res.partner has NO `mobile` field in Odoo 19 — reading it raises ValueError: Invalid field 'mobile'. There is only `phone`."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# res.partner has no `mobile` field in Odoo 19 (confirmed 2026-07-15)

Reading `mobile` on `res.partner` throws:
`ValueError: Invalid field 'mobile' on 'res.partner'` (KeyError inside `_determine_fields_to_fetch`).

Odoo 19 **merged mobile into `phone`** — there is exactly ONE phone field on a contact. Same for the DNC compute: `phone_blacklisted` keys off `phone` alone.

**Why it matters:** `mobile` exists on res.partner in older Odoo versions and all over training data, so it's an easy autopilot include in a `read()` field list — and **one bad field name fails the WHOLE read call**, not just that field. Cost a wasted round-trip on 2026-07-15 pulling customer records.

**How to apply:** never put `mobile` in a res.partner field list. Use `phone`. If a read blows up with `Invalid field X`, drop X and retry rather than assuming the record or auth is broken. Fits [[feedback_no_guessing_on_fields]] — verify against the live model, don't infer from Odoo defaults. Related: [[project_dnc_false_positive_dj_number]].
