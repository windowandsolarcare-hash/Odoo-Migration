---
name: project_res_partner_no_mobile_field
description: "res.partner in this Odoo 19 instance has NO `mobile` field. Secondary phone = x_studio_x_studio_second_phone (the field the SMS inbound matcher searches, ~65 populated) or x_studio_secondary_phone (spouse/2nd-contact, paired with x_studio_secondary_name)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T07:00:04.640Z
---

**Discovered 2026-09-12** (verified via `res.partner` `fields_get` on live Odoo while building the Thumbtack 72h flow).

## The fact
`res.partner` has **NO `mobile` field** in this Odoo 19 SaaS instance — a write/read of `mobile` raises `ValueError: Invalid field 'mobile' on 'res.partner'`. Do NOT assume the standard Odoo `mobile` field exists. The only plain phone field is **`phone`** (char, the PRIMARY).

## The two SECONDARY phone fields (both custom x_studio, both real)
- **`x_studio_x_studio_second_phone`** ("Second Phone", char) — ★ this is the one the **SMS inbound matcher in `sms.py` searches** (`_match`/lookup ~lines 233, 256–262: it matches an incoming text against `phone` AND `x_studio_x_studio_second_phone`). ~65 W&SC partners populated. **Use THIS for any secondary number that still needs to receive/route texts** (e.g. the Thumbtack proxy after the real number is promoted to primary) so inbound replies still match the contact.
- **`x_studio_secondary_phone`** ("Secondary Phone", char) — the spouse / second-contact phone, paired with `x_studio_secondary_name`. Read by brain.py, dashboard.py (~8406), portal.py, specialist_billing.py. NOT searched by the inbound SMS matcher. ~3 populated. Use for an actual second person, not a routing alias.

## How to apply
- Never write `mobile` on res.partner here — it 500s.
- Promoting a new primary number while keeping the old one reachable by text → old number goes to `x_studio_x_studio_second_phone`.
- This is exactly what the Thumbtack `capture_contact` endpoint does: real → `phone` (primary), proxy → `x_studio_x_studio_second_phone` (secondary). See [[project_thumbtack_proxy_numbers]].

Related: [[project_thumbtack_proxy_numbers]], [[feedback_no_guessing_on_fields]].
