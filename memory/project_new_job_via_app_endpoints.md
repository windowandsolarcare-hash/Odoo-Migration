---
name: project_new_job_via_app_endpoints
description: "The exact app HTTP endpoints (same ones the phone calls) to create a customer + job the RIGHT way — runs the real job-number sequence, route-aware scheduler, and system confirmation. Use these, not raw Odoo writes. Base = wsc-field-assistant.onrender.com."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T07:02:33.323Z
---

**How to CREATE A NEW JOB via the app's own workflow** (per [[feedback_assistant_use_app_workflow_not_raw_api]]). Base URL `https://wsc-field-assistant.onrender.com`, all under `/owner`, JSON bodies, call server-side with python `requests`.

**AUTH (as of 2026-08-22):** owner endpoints are **OPEN — auth is in MONITOR mode** (`main.py` `_authz_gate`; only enforces if env `AUTH_ENFORCE=='1'`, currently unset). So NO credential needed right now. **If AUTH_ENFORCE is ever set:** POST `/api/login` `{name, pin}` (pin = `res.partner.x_render_pin`, NOT hr.employee.x_render_access_code) → sets HMAC cookie `wsc_session` (secret = env `SESSION_SECRET`||`ODOO_API_KEY`); send that cookie on subsequent calls. No CSRF on the JSON POSTs.

**The 8-call sequence (phone-equivalent):**
1. `GET /owner/api/intake/search?q=<name|phone>` — reuse an existing customer (company-filtered) — OR create:
2. `POST /owner/api/intake/contact` `{first_name,last_name,phone,email,street,city,zip}` → `{id}` (the PERSON).
3. `POST /owner/api/intake/property` `{contact_id,street,city,zip,gate_code,frequency,type_of_service,alternating,pricing_note,notes,has_window,has_solar,ok_to_text}` → `{id}` (the PROPERTY child; job is built against THIS id). Geocodes for the scheduler.
4. `GET /owner/api/intake/products` → `[{id,name,price}]` (pick product_id for lines; set line `price` explicitly — list prices are per-unit tiny e.g. Solar=$5).
5. `POST /owner/api/intake/create-job` `{contact_id,property_id,date_pt:"YYYY-MM-DD HH:MM:SS",lines:[{product_id,name,qty,price}],job_type,tech_name,gate_snapshot?}` → `{ok,so_id,so_name}`. **Assigns the real job number** (`_next_job_name` via `ir.sequence 'wsc.job.seq'`, e.g. 264956) and creates a **Submitted DRAFT** (NOT yet scheduled/confirmed). `job_type` must be in VALID_JOB_TYPES.
6. `GET /owner/api/scheduler/so-suggest?so_id=<id>&window=21&ordering=route|soon` → `{best,options:[{date,time,minute,near_mi,job_count}]}`. **`ordering=route`** = batches near existing jobs (efficient, may be weeks out); **`ordering=soon`** = earliest openings. (Also `/owner/api/scheduler/city-suggest` before an SO exists, and `/owner/api/openings?partner_id=` for the customer-facing list.)
7. `POST /owner/api/schedule/reschedule` `{so_id,date:"YYYY-MM-DD",time:"HH:MM"}` → **confirms the draft (action_confirm + writes date_order back), sets the slot, promotes workiz_status Submitted→Scheduled = lands it on the schedule.** Chokepoint guards: refuses Done/invoiced/past.
8. Confirmation (TWO-step, leave for DJ unless told to send): `POST /owner/api/schedule/confirm_preview` `{so_id}` → `{message}` (system-composed); then `POST /owner/api/schedule/send_confirm` `{so_id,message}` → sends via messaging.send (STOP/DNC/quiet-hours + idempotency enforced; phone pulled off the CONTACT/parent).

**Reference run (Bob Lis, 2026-08-22):** reused person 27192 + property 27193, `create-job` → SO 264956 ($200 solar, product 125), `so-suggest` route-pick was Sep 3 11am but `ordering=soon` gave Aug 27 8am; rescheduled to **Aug 27 08:00** (DJ said "next week + auto-pick"); confirmation left for DJ. Related: [[project_thumbtack_proxy_numbers]], [[project_so_numbering_post_workiz]].
