---
name: project_stranded_next_jobs
description: "Maintenance next-jobs Phase 5 created in Workiz that never synced to Odoo (old rule), surfaced via a new '📋 In Workiz' mode in the Maintenance to Schedule app."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**The leak (found 2026-06-23):** Phase 5A creates the next maintenance job IN WORKIZ (Submitted, no tech, no line items) and writes its Workiz link onto the COMPLETED job's invoice (`account.move.x_studio_workiz_job_link`). Under the OLD rule the next job stayed Workiz-only until DJ changed its status (add tech + line items + set status) — that status change is what brought it to Odoo via Phase 3/4. New rule clones to Odoo immediately. So jobs finished under the old rule that DJ never got around to scheduling are STRANDED in Workiz: not on the schedule, not in any Odoo screen. 30 such customers (latest-per-customer) as of 2026-06-23.

**Detection (Odoo-only, no Workiz calls):** invoice (out_invoice, company 1) carries `x_studio_workiz_job_link`; extract next-job UUID (`/job/{UUID}/`); if that UUID is NOT a `sale.order` (`x_studio_x_studio_workiz_uuid`), it's stranded. One row per customer = their LATEST completed invoice's stranded next-job. The stranded Workiz jobs DO carry `next_job_line_items` (the "LINE ITEMS TO ADD:" block), so the copy-paste preload works on them.

**The app (existing — NOT rebuilt):** "Maintenance to Schedule" = `/owner/maintenance` (static/owner/maintenance.html + routers/owner/submitted_jobs.py), under the **Schedule & Dispatch** hub card. Its `launchWorkiz(idx)` = the copy-paste bridge: fetch `/api/maintenance/items?uuid=` (reads Phase 5's next_job_line_items off the Workiz job, alternating-aware), cycle each price→name through the clipboard, then open the Workiz job link. Modes via `setMode()`: Upcoming / ⚠️ Overdue (both from Odoo `/api/scheduled_sos`).

**What was added 2026-06-23 (commits 3ec2c71/33b5c0b/bcf4479):** new mode **"📋 In Workiz"** + backend `GET /owner/api/maintenance/stranded` (in submitted_jobs.py). Endpoint returns {name, uuid, workiz_link, address, job_type, so_name, last_done}, oldest-first. Frontend reuses launchWorkiz (UUID is all it needs). GOTCHA fixed: invoice partner `.name` field = the STREET (property gotcha [[project_property_displayname_has_name]]); use the partner tuple's display_name `[1].split(',')[0]` for the customer name. EDGE: a customer with 2 property records (Workiz dup) appears twice (e.g. Vince Russo) — minor.

**Why these never re-engaged either:** these are Maintenance type → Phase 5 makes a Workiz next-job (NOT a re-engagement To-Do). Pre-Feb-2026 jobs predate Render billing entirely (no Phase 6→5 ran) — see the broader gap analysis. Related: [[project_reengagement_vs_reactivation]], [[project_next_job_link]], [[project_type_of_service_fields_map]].
