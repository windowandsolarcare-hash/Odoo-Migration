---
name: session_may28_hiring_retention
description: "2026-05-28 evening session — Indeed job posting, retention analysis, reactivation gaps, blast architecture"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Session Summary — 2026-05-28 Evening

### Hiring
- Indeed job posting live: "Window Cleaner", Coachella Valley CA, $21-26/hr, $25/day budget
- Job Overview rewritten — plain language, growth path framing (not "assistant to owner")
- Auto-message configured with 3 screening questions (driver's license, heights, part-time hours)
- Company name confirmed: **Window & Solar Care** (no "A" prefix — folder name is just filing convention)
- Facebook Jobs > Craigslist for trade hiring in Coachella Valley
- Nextdoor is locked to registered neighborhood — can't post across the valley directly

### Retention Analysis (W&SC only, parent contacts, Done jobs)
| Period | Retained | Rate | New | Lost |
|---|---|---|---|---|
| 2022→2023 | 118/180 | 65.6% | 145 | 62 |
| 2023→2024 | 169/263 | 64.3% | 105 | 94 |
| 2024→2025 | 178/274 | 65.0% | 66 | 96 |

- Retention consistently ~65% for last 3 years
- Losing ~96/yr but only gaining 66 new in 2025 — reactivation program is critical
- 2021→2022 dip to 51.8% was post-COVID anomaly (big 2021 new customer wave didn't stick)

### Reactivation Coverage
- 890 total contactable W&SC customers
- 234 actually sent a reactivation text (2026 sends)
- 255 initialized with 2019 stamp but never actually sent
- 401 no date at all (many are inactive/historical contacts)
- **283 active customers never reactivated** (after removing archived)
- **182 after removing maintenance customers** (type_of_service on PROPERTY record, not contact)
- **106 lapsed (no work in last 12 months), not maintenance, never reactivated** — these are the true gap

Key findings:
- type_of_service_2 / x_studio_x_type_of_service lives on the PROPERTY child record, not the parent contact
- Reactivation report includes blank-field customers (OR condition: sent > 1yr ago OR field = False)
- New customers appear on report prematurely because field is blank → fix via new initialized field

### Future Builds Logged
- [[project_zapier_to_render_migration]] — near-term, prerequisite for referral blast
- [[project_employee_referral_program]] — SMS blast to clients, full architecture designed
- [[project_reactivation_initialized_field]] — add x_studio_reactivation_initialized to fix new customer false positives on reactivation report

### Cleanup Needed
- DJ needs to go through lapsed customer list and archive dead/disliked customers in Odoo — this will clean up reactivation report automatically
