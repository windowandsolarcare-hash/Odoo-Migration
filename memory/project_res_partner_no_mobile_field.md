---
name: project_res_partner_no_mobile_field
description: "res.partner in this Odoo 19 instance has NO `mobile` field. Secondary phone = x_studio_x_studio_second_phone (the field the SMS inbound matcher searches, ~65 populated) or x_studio_secondary_phone (spouse/2nd-contact, paired with x_studio_secondary_name)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-15T22:19:02.205Z
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

## Live incident it caused (2026-09-15) — the swallow trap
`carddoor.py` `_carddoor_prefill` requested `mobile` in BOTH res.partner reads (property + person). The read raised `Invalid field 'mobile'`, but the function's broad `try/except` (there to "never raise") **swallowed it and returned phone/email/zip all blank EVERY time**. Symptom DJ hit on a real $1 card-at-door test: "Text the receipt" always said "no cell on file" even though the SO's partner had a `phone`, and email/zip never prefilled. Fixed by dropping `mobile` from both reads (use `phone`) — commit 2ac95a11. tech/carddoor.py imports these owner cores, so the one fix covered both.
**Lesson:** a single bad field name inside a broad `try/except` doesn't error loudly — it silently degrades the WHOLE result to empty and can sit invisibly in a live customer-facing flow. When a prefill/lookup returns all-blank, suspect a swallowed `Invalid field` before assuming the data is missing.

Related: [[project_thumbtack_proxy_numbers]], [[feedback_no_guessing_on_fields]], [[feedback_odoo_verify_content_not_status]].
