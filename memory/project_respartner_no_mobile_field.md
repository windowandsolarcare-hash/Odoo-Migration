---
name: project_respartner_no_mobile_field
description: "Odoo 19 (window-solar-care) res.partner has NO `mobile` field — only `phone`. Reading/writing `mobile` raises ValueError: Invalid field 'mobile'. Verified 2026-08-03."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T01:16:29.271Z
---

**`res.partner` in this Odoo 19 instance has NO `mobile` field — only `phone`.** Confirmed 2026-08-03 by API: `search_read` with `mobile` in fields → `ValueError: Invalid field 'mobile' on 'res.partner'`. So all customer phone numbers live in the single `phone` field. Any code that reads/writes `mobile` (Odoo-default in many DBs) will crash here — use `phone` only.

## Where the phone lives — person vs property (Ella Collins example)
The migration's person/property split means **the phone is on the PERSON (parent) record, NOT the property (child)**:
- Person: id 27137 "Ella Collins", `phone` = 9516627175, record_category = **Contact**, parent_id = False.
- Property: id 27138 "8401 Maruyama Drive", `phone` = **False/empty**, record_category = **Property**, parent_id = 27137. **Jobs/SOs live here** (SO 264935 etc.).

Consequence (DJ 2026-08-03): the **inbox** matches an inbound text's number via `res.partner.phone` → hits the CONTACT → shows the name. But any screen showing the **job/property** record shows a **blank phone**, because the property carries no phone. **Fix pattern for job/property screens: fall back to `parent_id.phone`** when the record's own phone is empty (same parent link the SO contact uses). See [[project_property_partner_naming_quirk]], [[feedback_no_guessing_on_fields]].

## Terminology (DJ 2026-08-03): it's "Contact", not "Person"
The parent record's `x_studio_x_studio_record_category` = **"Contact"** (child = "Property"). There is NO separate "Person" record — use **Contact** / **Property**. The Contact is sparse: name + `phone` + `ref` (Workiz client id); service data (gate/pricing/frequency/type/service_area) lives on the Property.

## PHONE BACKFILL DONE (2026-08-03)
DJ wanted the phone on BOTH Contact and Property. Reality was small: of 920 W&SC Property records, 877 already had the phone; only 43 blank; 0 Contacts blank-with-child-phone. **Backfilled 25** blank Property phones from their parent Contact (fill-blanks-only, never overwrite, company in [1,False]); 18 had no phone on either side (skipped, need real data). Log: `scratchpad_phone_backfill_log.json`. GOING-FORWARD fix (not yet built): have new job/property creation in new_job.py copy `parent Contact.phone` onto the new Property so it never recurs.

## GOTCHA: never `read` res.partner with NO fields (all-fields)
A broken Studio computed field **`x_studio_number_of_sales_orders`** has invalid stored code (`STORE_ATTR` forbidden opcode in safe_eval) and **throws on read**. Reading all fields (`read([[id]], {})`) crashes with `forbidden opcode(s) ... STORE_ATTR`. ALWAYS pass an explicit `fields` list on res.partner reads/search_reads and never include `x_studio_number_of_sales_orders`.
