---
name: project_operator_playbook
description: "Operator execution cheat-sheet — proven app-endpoint recipes, common product IDs, HUD-card deep-link patterns, and gotchas so turns are \"do\" not \"rediscover\". All via app endpoints (charter), never raw Odoo writes."
metadata: 
  node_type: memory
  type: project
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-05T07:44:10.672Z
---

Operator's ready recipes (all PROVEN live 2026-09-03/04). Execute from here; only read code for something not listed. First stop for any endpoint = [[project_endpoint_map]].

**Base:** app `https://wsc-field-assistant.onrender.com`, owner routes under `/owner`, JSON bodies, curl/requests server-side. Auth: a DEDICATED Operator owner login now EXISTS (set up 2026-09-05). Login file `C:/Users/dj/_operator_owner_login.json` = {name:"Operator", pin:4-digit}. Flow: `POST /api/login {"name":"operator","pin":<pin>}` → capture the `wsc_session` cookie (curl `-c /c/Users/dj/_operator_cookies.txt`), then send it on EVERY /owner/* call (curl `-b /c/Users/dj/_operator_cookies.txt`); on any 401, re-login + retry. Verified end-to-end (role "owner", /owner calls 200). AUTH_ENFORCE is currently 0 (rolled back) so the cookie isn't strictly required yet, but INCLUDE it so nothing breaks when enforcement returns. PT = UTC-7 (summer); `date_order` = job START in UTC (15:00 UTC = 8am PT). **SO NAME ≠ Odoo id** — app endpoints need the Odoo record id (`so_id`); resolve name→id via Odoo search. Odoo read-only key in `/c/Users/dj/_odoo_key_val.txt` (the old odoo_lookup.py key is DEAD); url `window-solar-care.odoo.com`, db `window-solar-care`, uid 2. Customer searches: `company_id in [1, False]`.

**RECIPES (endpoint | body):**
- Find customer: `GET /owner/api/intake/search?q=<name|phone>`
- New contact: `POST /owner/api/intake/contact {first_name,last_name,phone,email,street,city,zip}` → {id}
- New property: `POST /owner/api/intake/property {contact_id,street,city,zip,gate_code,ok_to_text,has_window}` → {id}
- Products: `GET /owner/api/intake/products` (set price explicitly)
- Create job (Submitted draft): `POST /owner/api/intake/create-job {contact_id,property_id,date_pt:"YYYY-MM-DD HH:MM:SS",lines:[{product_id,name,qty,price}],job_type,tech_name}` → {so_id,so_name}
- Reschedule / move / promote: `POST /owner/api/schedule/reschedule {so_id,date:"YYYY-MM-DD",time:"HH:MM"}` — moves + promotes Submitted→Scheduled + AUTO-clears confirm state; sends nothing.
- Change service line/price: `POST /owner/api/job/lines {so_id,lines:[{product_id,name,qty,price}]}` — REPLACES all lines (send existing + new); safe on confirmed jobs. Does NOT change the `x_studio_...job_type` label (no endpoint for that field).
- Confirm preview msg: `POST /owner/api/schedule/confirm_preview {so_id}`. Confirm/reschedule LINK: `POST /owner/api/sched/launch {so_id,mode:'confirm',send:false}` → {link} (`wscare.pro/book/sched/<tok>?c=1`).
- Slot offer (tap-to-book): `POST /owner/api/offers/reserve {so_id,partner_id,name,slots_pt:[{date,time},...]}` → {offer_id, link `wscare.pro/c/<tok>`}. Clear: `POST /owner/api/offers/clear {offer_id}`. Send: `POST /owner/api/offers/send {offer_id,body}` (or send the link via inbox).
- Job photos: `GET /owner/api/job_photos?so_id=` (count). Select+send lives in v2_field job detail → `POST /owner/api/job/photos_send {so_id,send,att_ids}`.
- Inbox: `GET /owner/api/inbox/list?filter=active`; thread `GET /owner/api/inbox/thread?c=<phone_norm>` (thread_by_partner often returns empty — use ?c= with the phone).
- Board: `GET /owner/api/calendar_jobs?start=YYYY-MM-DD&end=YYYY-MM-DD` → days{date:[jobs]}.
- Route-best slots: `GET /owner/api/scheduler/so-suggest?so_id=&window=&ordering=route|soon` → {best,options}.
- Confirm state: `GET /owner/api/sched/state?so_id=` → {state:none|sent|accepted,confirmed}.
- HUD card: `POST /owner/api/feed/submit {item:{id,kind:'attention',source:'operator',title(≤80),why_now(≤400),urgency:'today',badge,action:{label,href},created(ISO),expires}}`. Delete `POST /owner/api/feed/delete {id}`. List `GET /owner/api/feed/list`.
- Card-at-door payment: `POST /owner/api/carddoor/record {payment_intent,invoice_id,so_id}` (idempotent).
- My Day: add `POST /owner/api/myday/add {title,date,time,pinned,note}`; update `/owner/api/myday/update {id,...}`; attach `/owner/api/myday/attach {task_id,filename,content_type,data(b64)}`.
- Vault: search `GET /owner/api/vault/search?q=`; upload `POST /owner/api/notes/upload_file` (multipart: file, category, tags) — Reference folder = `category=Reference` (it's Quick Notes/Reference); read doc text `GET /owner/api/notes/{id}/text`.

**Common product IDs:** 103 Outside Windows And Screens · 141 Windows In & Out - Full Service · 90 Garage Door Windows Cleaned-No Cut Outs · 98 Lights and Ceiling Fan Cleaned · 99 Mirrors Cleaned · 634 Quote ($0 placeholder) · 100 Miscellaneous · 2 Tip.

**HUD deep-links:** confirm (routes through confirm machinery + auto-clears): `/static/owner/v2_inbox.html?open=<pid>&confirm_so=<so>&draft=<urlenc>`. Plain prefill: same without `confirm_so`. Job detail: `/static/owner/v2_field.html?open_so=<so>`. (`open=` path applies the draft; `?c=` does NOT.) Card ids: `operator:confirm:<so>` / `:offer:<so>` / `:photos:<so>` / `:reply:<so>`.

**★ MAINT-ADVANCE TIGHTENING (2026-09-05, learned the hard way):** NEVER use `/api/schedule/reschedule` to tighten a maintenance-advance (Submitted, in-pile) job's time — reschedule AUTO-PROMOTES Submitted→Scheduled/sale, dropping it off `_maint_pending_rows()` and marking it confirmed BEFORE the customer was contacted (double-message risk). Use the dedicated **`POST /owner/api/maint/advance/set_time {so_id,date,time}`** (Submitted-only guard, keeps it in the pile) to tighten maint times. reschedule is only for real (confirmed/to-be-confirmed) jobs. Rule: understand a mover's side effects before batch-acting.

**GOTCHAS:** ASCII-only in curl `-d` (em-dash 0x97 → UTF-8 500). Python file writes use `C:/Users/dj/…` not `/c/Users/…`. `/tmp` doesn't persist across Bash calls → use `/c/Users/dj/`. feed/submit reusing an id keeps old 'seen' status → delete+new id to force 'new'. reschedule auto-un-confirms so the 4-day re-fires for the new date. Confirm flow (Path-B, live 2026-09-04): confirm card `confirm_so` → Send → state='sent' + arm reply + 4-day skip (no double-text) + card auto-clears.

Related: [[project_endpoint_map]], [[feedback_assistant_use_app_workflow_not_raw_api]], [[project_new_job_via_app_endpoints]].
