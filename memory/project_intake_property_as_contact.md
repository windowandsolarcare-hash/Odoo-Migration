---
name: project_intake_property_as_contact
description: My Day task deep links can pass a PROPERTY record as contact= to New Job — backend now resolves Property→parent customer (_resolve_contact in new_job.py).
metadata: 
  node_type: memory
  type: project
  originSessionId: 17f1db69-cc3e-47ab-9387-b6a4dee9ca9a
  modified: 2026-07-21T05:26:13.151Z
---

2026-07-20: DJ's "Walter" My Day task → action button → New Order/New Job passed `contact=25847`, which is Walter Keller's PROPERTY record ("197 Shepard Drive", category Property, parent 23655). `create-job` found no first/last/ref on it, split the name, and created a Workiz job under a brand-new client literally named First "197" Last "Shepard Drive".

**Why:** v2_myday builds the New Job action link from `it.partner_id` (`?contact='+it.partner_id`), and a task's partner_id can be the property, not the person. Intake SEARCH excludes property records, but deep links bypass search.

**How to apply:** `routers/owner/new_job.py` now has `_resolve_contact(cid)` — reads the record; if `x_studio_x_studio_record_category == 'Property'` and it has `parent_id`, returns the parent id. Applied at the top of `api_intake_properties`, `api_intake_recent_jobs`, and `api_intake_create_job`. Any NEW intake endpoint that accepts a contact_id must call it too. Frontends were left unchanged on purpose (canonical-endpoint rule — see [[feedback_reuse_canonical_endpoint]]).
