---
name: project_res_partner_no_mobile_field
description: "res.partner has NO `mobile` field in this Odoo 19 DB — reading it raises \"Invalid field 'mobile'\" and kills the WHOLE read, blanking every other field in the same call."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-18T13:30:46.837Z
---

`res.partner` in this Odoo 19 instance has **no `mobile` field**. Confirmed by direct API call
2026-08-18 while building the customer portal: `odoo_rpc('res.partner','read',[[23376]],{'fields':['mobile']})`
→ `Invalid field 'mobile' on 'res.partner'`. The only phone field is **`phone`**.

**Why:** the failure is silent and total, not partial. A `read`/`search_read` with a bad field name in
the `fields` list raises for the ENTIRE call — so one stray `'mobile'` in a 20-field list returns
nothing, and any `try/except` that falls back to `[]` makes the record look like it doesn't exist.
The portal's `account()` returned `{'ok': False, 'error': 'not found'}` for a customer who plainly
exists, purely because `mobile` was in `_PARTNER_FIELDS`.

**How to apply:** never include `mobile` on res.partner — use `phone`. More generally, when an Odoo
read of a real record mysteriously returns empty, suspect a bad field name in the list before
suspecting the record: bisect the `fields` list (loop one field at a time) rather than guessing.
Same class of bug as [[feedback_no_guessing_on_fields]] — verify the field exists first.

Related: [[project_customer_portal]]
