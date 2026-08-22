---
name: project_type_of_service_fields_map
description: "Definitive map of Odoo 'Type of Service' fields — there are TWO real ones (Maintenance/On Request/Unknown), the res.users copies are mirrors, and 'Most Recent Service Type' is a DIFFERENT axis (windows/solar)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Verified 2026-06-22 by direct ir.model.fields query. Stop second-guessing which field is which.**

**The TWO real "Type of Service" fields (vocabulary = Maintenance / On Request / Unknown):**
1. `res.partner.x_studio_x_type_of_service` — char, STORED. The MASTER on the customer/property. Values in use (1,452 non-empty): Unknown 1,048 · On Request 245 · Maintenance 159.
2. `sale.order.x_studio_x_studio_type_of_service_so` — selection, STORED, label "Type of Service SO". Per-JOB. Options exactly `['Maintenance','On Request','Unknown']`. Across 3,518 company-1 SOs: Unknown 1,362 · Maintenance 1,010 · On Request 994 · empty 152.

**READ ORDER (the rule):** SO field FIRST (`x_studio_x_studio_type_of_service_so`), fall back to the partner field (`x_studio_x_type_of_service`); never trust a blank/Unknown if the other has a real value. See [[project_type_of_service_read_order]].

**NOT separate fields — ignore:** `res.users.x_studio_x_type_of_service` and `res.users.x_studio_type_of_service` are just the partner field showing through (res.users inherits res.partner). Same data, not a third field.

**The look-alike "third" field — DIFFERENT axis, do NOT use it for scheduling:**
- `res.partner.x_studio_most_recent_service_type` — selection, label "Most Recent Service Type". Options `['windows','solar','both','other']`. Values (1,288): windows 857 · solar 223 · both 135 · other 73. This is WHAT work you do (window vs solar), NOT maintenance-vs-on-request. Siblings: `x_studio_has_window_service` (1,065 true), `x_studio_has_solar_service` (430 true). Irrelevant to the schedulable-vs-contact decision.

**Why this matters (the scheduling work):** "schedulable directly (Maintenance) vs contact-customer-first (On Request/Unknown/blank)" is driven ONLY by the two real fields above (SO→partner fallback). The windows/solar field plays no part. DJ's rule (2026-06-22): only Maintenance jobs can be scheduled directly; everything else requires contacting the customer. See [[project_report_hub_redesign]] (Needs Scheduling tab rework) — the tab's feeder `/api/scheduled_sos` does NOT currently return type_of_service, and SO-level type is mostly blank on auto-created next-jobs (40/42 upcoming blank → must resolve via partner). Live overdue mix: 24 rows = Maintenance 6 / On Request 4 / Unknown 10 / blank 4 (i.e. only 6 truly schedulable).
