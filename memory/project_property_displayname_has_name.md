---
name: project_property_displayname_has_name
description: "GOTCHA: a parented Property res.partner's display_name (and partner_shipping_id[1]) = 'Customer Name, Street' — use the `street` field for customer-facing text or the name double-prints. Fixed the re-engagement SMS (2026-06-17)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**An Odoo Property record's display name carries the customer's NAME, not just the address.** For a Property `res.partner` that has a `parent_id` (the contact), Odoo renders `display_name` (and therefore `partner_shipping_id[1]` on a sale.order) as **"Customer Name, Street"** — e.g. `"Adam Ruelas, 18166 Andrea Court"`, `"Dwight Fichtner, 404 Tewell Drive"`. The record's own `name`/`street` field is just the address (`"18166 Andrea Court"`). Properties with NO parent show the full address as display_name (no name).

**Why it matters:** any customer-facing text that drops `partner_shipping_id[1]` (or property `display_name`) in next to a greeting will print the name twice.

**Bit us in the re-engagement SMS (2026-06-17, DJ: "remove the person's name before the address, it's redundant").** `_build_followup_sms` (reactivation.py) said *"Hi Dwight … We last cleaned at Dwight Fichtner, 404 Tewell Drive on …"* — the `property_addr` came from `partner_shipping_id[1]`. **Fix:** the preview endpoint now reads the property's `street` field (`prop_street_by_id`) and passes that as `property_addr`, falling back to the display name only if street is empty. Verified: now reads "We last cleaned at 404 Tewell Drive". The launch endpoint sends the front-end's edited `sms_text` (doesn't rebuild), so the SMS is generated in ONE place (preview) — not a paired change.

**How to apply:** for any customer-facing string (SMS, email, booking confirmation), build the address from the property's `street` (+ `city` if wanted), NOT from `display_name`/`partner_shipping_id[1]`. See [[project_reactivation_sent_book]], [[project_type_of_service_read_order]].
