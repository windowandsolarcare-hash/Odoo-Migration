---
name: project_so_partner_id_is_property
description: "★ A W&SC sale.order's partner_id is the PROPERTY child (record_category='Property', type='delivery'), NOT the person. The person is partner_id.parent_id. Matters anywhere you need the customer PERSON id from a job."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-21T16:07:24.450Z
---

**★ On a W&SC `sale.order`, `partner_id` points at the PROPERTY (the child address record), NOT the person.** Verified live 2026-08-21 across recent SOs: e.g. SO S00252 `partner_id = 27187 '25 Toledo'`, `record_category='Property'`, `type='delivery'`, `parent_id = [23058, 'Nancy Tohl']`. The actual customer PERSON is **`partner_id.parent_id`** (or the `commercial_partner_id` root). `partner_shipping_id` is also the property.

**Where this bites — the field app.** `dashboard.py api_so_history` returns `partner_id = so['partner_id'][0]` raw, so **`activeJob.partner_id` in `v2_field.html` is the PROPERTY id, not the person.** Anything that needs the customer person from a job (creating a sibling property, opening the person's Customer-Brain record, etc.) must resolve the parent, or it operates on the wrong record. (Passing `activeJob.partner_id` straight into intake would create a property-under-a-property grandchild.)

**Where it does NOT bite.** Customer search results are already persons — `api_intake_search` / `search_customers` EXCLUDE `record_category=='Property'`, so `v2_customers.html` `CUSTS[i].id` is the person. That's why the Customer-Brain [[project_price_history_by_service]] add-property (which passes `c.id`) was correct, but the JOB-detail one needed the walk.

**The fix that's in place (2026-08-21, new_job.py 282136a).** The ONE canonical intake endpoint `api_intake_create_property` now **detects a Property `contact_id` and walks up to its `parent_id` (the person) before creating** — backward-compatible (a person id passes straight through), so New Job + Customer Brain are unaffected and the Job-detail 🏠 Add-property button can safely pass `activeJob.partner_id`. Verified live: POST with property 27187 → new address parented to 23058 (the person), not 27187.

**Rule of thumb:** to get the customer PERSON from a job/SO, read `partner_id` then `parent_id` (or `commercial_partner_id`); never assume the SO partner is the person. Pairs with the household `child_of` rule in [[project_price_history_by_service]] (resolve the whole household via `res.partner child_of` the commercial root).
