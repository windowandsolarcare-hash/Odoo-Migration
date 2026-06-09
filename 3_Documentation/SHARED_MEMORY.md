OK
OK
# SHARED MEMORY - Window & Solar Care
# Synced between Claude Code (local) and Render Claude (field assistant)
# Last updated: 2026-05-20
# Format: key facts only - both Claudes read this on every session

## MULTI-COMPANY DATABASE
This Odoo database has multiple companies. WSC is company_id = 1.
- company_id = False (global/unset) or 1 → WSC data — include these
- company_id = anything else → another business — EXCLUDE (Cheryl, Saunders Printing, future companies)
For any res.partner analytics/counts: ALWAYS add ["company_id", "in", [False, 1]] to the domain.
This rule is permanent — do not change even if new companies are added.

## ⚠ SYSTEM CONSTANTS — READ FIRST, NEVER GUESS THESE
- **Odoo SO name format:** 6-digit zero-padded number, NO prefix. e.g. `003575`, `004659`. NEVER `S00123`.
  Normalize any number DJ gives you: `str(n).zfill(6)`. Verified by API 2026-05-20.
- **Workiz Job UUID:** Long UUID string (internal only). DJ never knows/provides this directly. Look it up from SO.
- **Workiz Job Number:** Short sequential number shown in Workiz UI — DIFFERENT sequence from Odoo SO numbers.
- **Odoo User ID:** `2`. Odoo DB: `window-solar-care`.
- **Render app:** `https://wsc-field-assistant.onrender.com`
- RULE: If a format is not listed here or in CLAUDE.md SYSTEM CONSTANTS table → make an API call to confirm. Do not guess.

## OWNER
- Dan Saunders (goes by DJ) - owner and sole technician, Window & Solar Care, Southern California
- Email: windowandsolarcare@gmail.com

## PLATFORMS
- Odoo: https://window-solar-care.odoo.com (DB: window-solar-care, User ID: 2)
- Workiz: job scheduling - IP-restricted, proxy through Odoo if calling from local machine
- GitHub: windowandsolarcare-hash/Odoo-Migration (main branch only)
- Render: mobile field assistant at https://wsc-field-assistant.onrender.com - always-on paid plan
- Zapier: Phases 3-6 automation - fetches code from GitHub main on every trigger

## AUTOMATION PHASES
- Phase 3: New job creation (Workiz webhook  Zapier  Odoo)
- Phase 4: Job status updates (Zapier polling every 5 min)
- Phase 5: Auto job scheduling (triggered by Phase 6)
- Phase 6: Payment sync (Odoo webhook  Zapier)
- Phase 2: Reactivation engine (Odoo Server Action, manual run)
- Phase 2B: STOP compliance (Workiz  Odoo webhook)

## KEY ODOO SERVER ACTION IDs
- LAUNCH (reactivation): 563

## CRITICAL FIELD NAMES
- Workiz UUID on SO: x_studio_x_studio_workiz_uuid
- Workiz Status on SO: x_studio_x_studio_workiz_status (values: Done, Pending, Submitted, Canceled, etc.)
- "Done jobs" ALWAYS means x_studio_x_studio_workiz_status = 'Done' — NEVER use invoice_status, state='done', or date filters as proxy
- Workiz custom service field: type_of_service_2 (NOT type_of_service)
- Property partners: x_studio_x_studio_record_category = "Property"
- Contact type of service: x_studio_x_type_of_service
- Gate code (contact): x_studio_x_gate_code
- Gate code (SO snapshot): x_studio_x_gate_snapshot
- Pricing (contact): x_studio_x_pricing
- Workiz client ID on contact: ref field

## KNOWN BUGS / RULES
- After action_confirm() on SO, write date_order back - Odoo resets it to now()
- date_order = Workiz JobDateTime (start time, UTC) - never use end time
- No imports in Odoo server action code
- No "response" or "result" variable names in Odoo 19 server actions (reserved)
- HTML in chatter gets escaped - use plain text with | separators, unicode emoji OK
- Workiz filter on SubStatus not Status
- Deleted Workiz job returns HTTP 204 not 404
- TIMER: Do NOT use action_timer_start/action_timer_stop - Odoo timer_start unreliable. Render uses ir.config_parameter key render.timer.{task_id}, creates account.analytic.line on stop.
- Render timer start: moves task to In Progress (stage 18), clears Odoo timer_start
- Render timer stop (button): GPS via Nominatim  "[Render Timer] 1234 Main St, Palm Desert, CA 92211 | 8:15 AM - 10:32 AM"
- Render timer stop (voice): "[Render Timer] | 8:15 AM - 10:32 AM"
- Timer log includes PT start + end times in description (added 2026-04-18)
- Task stage IDs: New=16, Planned=17, In Progress=18, Done=19
- Phase 4 task sync moves New(16) to Planned(17); never regresses In Progress/Done
- Phase 4 / sync_action_955 task re-entry BUG: when Workiz substatus cycles Scheduled → "Next Appointment X - Text" → back to Scheduled, the Planned task is deleted on the outbound trip and NOT recreated on return. SO's cached tasks_count stays at 1 but project.task is empty — Field Assistant shows no timer. Balser SO 15916 hit this 2026-04-20 (fixed manually as task 297). SO 17066 (Wayne Geringer, Aug 20 2026) still orphaned. Permanent fix not yet built.
- Render timer UI shows elapsed-since-resume instead of cumulative total on reopen — UI-only cosmetic bug, backend timesheet data is correct (verified 2026-04-20, 7 jobs, 7 single timesheet lines, zero duplicates).
- action_create_invoices does NOT exist in Odoo 19. Use sale.advance.payment.inv wizard.
- Workiz job create/duplicate: State field is REQUIRED - always include, default "CA"
- Render payment recording writes chatter on SO + invoice for audit trail
- New job for existing customer: use duplicate_workiz_job with partner_id
- duplicate_workiz_job (fixed 2026-04-26, commit a6ae157): now copies ServiceArea + sets last_date_cleaned = source JobDateTime[:10]. Previously these two fields were dropped — the tool description said "Copies all fields" but the implementation lied. If you see new duplicate jobs missing ServiceArea or last_date_cleaned, it means Render hasn't picked up the deploy yet — wait or trigger a manual deploy.
- Workiz API quirk: job/update/{UUID}/ requires "UUID" in body, job/delete/{UUID}/ requires "ID" in body. URL path alone returns 400 "UUID: Field is Required". Fixed 2026-04-26 (commit 7cbd848) by auto-injection in workiz_post() — affects update_workiz_field, mark_job_done, and any future call site using these endpoints.
- Workiz API quirk: setting SubStatus requires parent Status="Pending" in same body. 400 "Could not update sub status with no parent status provided" otherwise. Fixed 2026-04-26 (commit 405a31d) by auto-injection in workiz_post(). All our SubStatuses (Scheduled, Send Confirmation - Text, STOP, Lead, Next Appointment...) live under Pending.
- WORKIZ STATUS MODEL (clarified by DJ 2026-04-26): Only Submitted and Done are true top-level Status values we use. Everything else — Scheduled, STOP, Lead, Send Confirmation - Text, Next Appointment - Text, Next Appointment 2 - Text, In Progress, Canceled, all of them — lives under Status="Pending" as a SubStatus. Always filter and report on SubStatus.
- Render Claude session history is now persisted to Odoo (key=render.session.{session_id}) — fixed 2026-04-26 commit 455754d. Conversation memory survives Render redeploys and free-tier sleep. This means context (active customer, UUID, partner_id) carries across turns even after code pushes.
- Render Claude system prompt rules (effective 2026-04-26): pronouns default to most recently discussed customer; once a UUID/partner_id is known KEEP it; never re-search active customer; no trial-and-error API calls — use existing tools as documented; if a tool errors, fix input rather than retry; if no tool exists, plan with DJ first.

## PHASE 4A: PRE-PAYMENT SYNC (2026-05-01)
- Triggered before payment acceptance (manual via Render Claude tool or stale SO endpoint)
- Syncs comprehensive field set: status, tech, gate code, pricing, notes, job type, lead source, date_order, tags, + line items
- Line items compared as (name, qty, price) tuples - detects scope changes at customer door (e.g., Inside+Outside → Outside only)
- If all fields match AND lines match exactly: returns early, no cancel/confirm cycle (early-exit optimization)
- If mismatch found: cancel SO → draft → delete unmatched lines → write updates → re-confirm
- Returns: {'ok': bool, 'synced': bool, 'message': str, 'fields_updated': int}
- **Phase 4 vs 4A logic**: Field-sync logic is identical. Phase 4 (status changes) also handles task lifecycle; Phase 4A (pre-payment) is sync-only.

## RENDER TOOLS ARCHITECTURE
- **Location**: Saunders Render App, routers/owner/dashboard.py
- **TOOLS list** (line ~1962): Array of tool definitions (name, description, input_schema)
- **WRITE_TOOLS set** (line ~2496): Names of tools requiring confirmation
- **Tool handlers** (line ~977+): `if tool_name == 'name':` blocks implementing each tool
- **_describe_write function** (line ~1895+): Human-readable descriptions for confirmation prompts
- **Adding a tool**: 5 steps: (1) add to TOOLS, (2) add to WRITE_TOOLS if write, (3) add handler, (4) add description, (5) push to GitHub main
- **Natural language resolution**: Use `_find_so_by_identifier()` helper - tries ID, name, UUID, then customer name (resolves to most recent open invoiceable SO)

## WORKIZ API DEFAULTS (required to avoid validation errors)
- type_of_service_2: "On Request"
- frequency: "Unknown"
- confirmation_method: "Cell Phone"
- JobSource: "Referral"

## ODOO INVOICE + PAYMENT API PATTERN
# Journal: Bank (ID=6) | Check method line: ID=8 "Check (Bank)"
# Step 1: Create invoice via sale.advance.payment.inv wizard (action_create_invoices removed Odoo 19)
# Step 2: Confirm: odoo_call("account.move", "action_post", [[invoice_id]])
# Step 3: Register payment via account.payment.register wizard (handles reconciliation)
# payment_method_line_id values: 8=Check, 6=Cash, 7=Credit, 1=Manual(bank transfer)

## RENDER ENV VARS (project-scoped)
- GITHUB_REPO: windowandsolarcare-hash/Odoo-Migration
- SHARED_MEMORY_PATH: 3_Documentation/SHARED_MEMORY.md
- To switch to a new project: update both env vars on Render dashboard, no code change needed


### OwnTracks Monitoring Modes — CRITICAL (2026-05-21)
- Move (2): frequent pings + geofence events fire. Use while working.
- Significant (1): cell-tower only pings (low battery) + geofence events still fire. Use at home.
- Quiet (-1): NO pings AND NO geofence events on Android. **NEVER USE** — kills leave/enter events that drive clock-in/out.
- Bug 2026-05-21: server was sending monitoring:-1 on home arrival → geofence died → stuck forever.
- Fix: server now sends monitoring:1 (Significant) on home arrival. Move(2) on leaving home.
- If clock-in/out stops working: check OwnTracks monitoring mode isn't stuck on Quiet(-1).

### OwnTracks Ping-Based Home Detection (2026-05-15)
- Geofence enter/leave events are unreliable on mobile — OS drops them when app is backgrounded
- Location pings ARE reliable — server now checks home distance on every ping
- Home coords in Odoo ir.config_parameter: owntracks.home.{emp_id}.lat/lng/radius
- DJ (emp_id=1): 33.8110, -116.3822, 200m radius — Thousand Palms home
- Logic: within radius + clocked in → <30min cancels attendance, >=30min clocks out
- Commit 5ea5f589 in saunders-render-app

### CLOCK SYSTEM REBUILD — offline-first + whole-crew (2026-06-08)
Live in dashboard.py (NOT timeclock.py — its payroll routes are shadowed; dashboard registered first in main.py).
- **clock-IN** `POST /owner/api/payroll/clockin_crew {employee_ids, check_in?}` — `check_in` is the device tap time (ISO/UTC), honored so an offline clock-in records the real start, not the sync time. Same-day re-tap never overwrites (returns `already[]`). Prior-day open shift = closed (forgot-to-clockout, flagged) + fresh one created — never overwritten.
- **clock-OUT (manual "End Day")** `POST /owner/api/payroll/clockout_crew {employee_ids?, check_out?}` — clocks out the WHOLE crew, offline-safe (device check_out), idempotent (skips already-out), falls back to crew.today.{date} snapshot if ids omitted. ⚠ Empty body = clocks out the live snapshot crew — NEVER call to "test."
- **clock-OUT (auto at home)** now clocks out the WHOLE crew, not just the device owner. All 3 home-arrival sites (gps_ping, OwnTracks transition-enter, OwnTracks location-ping) call `_crew_home_clockout()` over crew.today.{date} after handling the driver.
- Frontend (field.html): clock bar shows `● Clocked in <time> · Crew: N`, 🏁 End Day button (double-tap guarded, queues to localStorage wsc_pending_clockout, flushes on load + `online` event). Crew persisted in localStorage wsc_crew_today.

### Render Env Vars — Missing as of 2026-05-15
Three vars still need to be set by DJ:
- GCAL_1_URL: Google Calendar ICS URL (Settings → Secret iCal address)
- GITHUB_TOKEN: GitHub personal access token with repo scope
- GMAIL_SCENIC_APP_PASSWORD: dan@scenicartprint.com app password (Google Account security)

### CRITICAL: Render Env Var API Rule
- NEVER use PUT /env-vars to add a single key — PUT replaces the entire list and wipes unspecified vars
- 2026-05-14 incident: PUT wiped STRIPE_SECRET_KEY, OWNTRACKS_SECRET, GCAL_1_URL
- To add/update one var: POST /v1/services/{id}/env-vars with single {key, value}
- To update multiple: fetch full list first, merge, then PUT the complete merged set

## RENDER APP STATE - 2026-04-18

### Endpoints
- GET /api/dashboard - today's schedule + stats
- GET /api/upcoming - 14 calendar day lookahead (~10 work days)
- POST /api/timer/start - starts Render timer
- POST /api/timer/stop - stops timer, creates timesheet, reverse-geocodes GPS
- POST /api/payment - records payment, creates invoice, posts chatter
- POST /api/attachment - uploads base64 image to Odoo SO as ir.attachment

### Claude Tools (full list) - 2026-05-01
Read: search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job,
      get_sales, get_sales_week (Mon-Sat), get_sales_month (Mon-Fri, returns days dict),
      get_jobs_list, navigate_to, odoo_query, github_read_file, github_list_dir, refresh_shared_memory
Write (confirm required): update_workiz_field, update_odoo_contact, post_odoo_note, create_todo,
      mark_job_done, create_workiz_job, duplicate_workiz_job, start_task_timer, stop_task_timer,
      record_check_payment, odoo_write, github_push_file, update_shared_memory,
      sync_so_verify, process_payment_with_sync (NEW 2026-05-01)
Utility: save_memory, delete_memory

### NEW: Payment + Sync Tools (2026-05-01)
- **sync_so_verify**: Verify SO sync w/ Workiz. Input: so_identifier (SO ID, name, UUID, or customer name). Returns: detailed report of what changed.
- **process_payment_with_sync**: Accept payment w/ auto-sync. Input: so_identifier, payment_method (check|cash|zelle|venmo|credit), amount, optional date + memo.
  Both tools support natural language customer name resolution: "Fred Jones open job" → finds open SO → grabs UUID → syncs automatically
  Commits: cd8a16a (endpoints), 73ed4ac (registration), ff7829c (natural language), 62061dc (payment method + memo)

### UI Features added 2026-04-18
- Saved request library: localStorage wsc_saved_qs, max 15 recents + unlimited starred. Pin with star. Below Send button in Command tab.
- Timer stop: GPS timeout 2s (was 5s). _timerStopping guard prevents double-tap. Button disables immediately.
- Photo section: above payment, gallery picker (not camera-only), multiple files, uploads to Odoo ir.attachment, thumbnail previews.
- Mic button: moved into header between date block and theme button. No longer fixed/floating overlay.
- Tab renamed: 7-Day to 10-Day
- Time label on done jobs: shows 2.5h or 45m LEFT of $/hr rate - visual check if timer logged correctly
- Future day rows: job-name-wrap div (dollar right-justified), Solar/Window service subtitle from task_names
- api_upcoming now fetches task_names for each SO to show service type on future rows

## MULTI-BUSINESS PLATFORM PLAN (2026-04-18)

### Architecture
- One Render Service (existing paid plan)
  - DJ: W&SC field assistant (LIVE)
  - Danny: Payroll clock in/out (planned)
  - Cheryl: Real estate assistant (planned)
- One Odoo Instance (existing subscription)
  - Company: Window & Solar Care (existing)
  - Company: Cheryl Real Estate (planned - multi-company)
  - Company: Artwork / AI Prints (planned - multi-company)
  - Company: Saunders Printing (planned - multi-company)
- Odoo Website (included in full package)
  - W&SC marketing site (planned)
  - Cheryl real estate site (planned)
  - Saunders Printing storefront (planned - primary eCommerce)

### Businesses Summary
- Window & Solar Care: LIVE - field assistant, full automation
- Cheryl Real Estate: planning - need info from Cheryl
- Artwork / AI Prints: green-lighted - Flux/DALL-E 3, Printify fulfillment, Etsy/Shopify APIs
- Saunders Printing: green-lighted - web-to-print, Odoo Website + Stripe, DJ prints/ships
- Payroll DJ+Danny: ready to build - no blockers

### Build Priority Order
1. W&SC accounting migration (QB to Odoo) - waiting on DJ to gather files
2. Cheryl Odoo company setup - need her business name
3. Cheryl real estate Render screen - need MLS info + stage checklist from Cheryl
4. Cheryl accounting setup - need her expense categories + bank info
5. DJ + Danny payroll tracker - READY TO BUILD, no blockers
6. Artwork eCommerce - Flux/DALL-E 3 + Printify + Etsy/Shopify APIs
7. Saunders Printing - Odoo Website storefront, Stripe, file prep automation
8. W&SC + Cheryl websites in Odoo - future

## PAYROLL TRACKER - DJ + DANNY (ready to build)
- Workers: DJ + Danny, both hourly
- Clock in/out via Render app (their own screen/route)
- Storage: Odoo account.analytic.line (same model as job timer)
- Payroll processing: stay on Gusto for now. DJ manually enters weekly hours.
- Danny sees only his own hours. DJ sees everything (both workers, daily, weekly totals, $ owed).
- Rates: DANNY_RATE + DJ_RATE env vars on Render - never hardcoded
- Odoo: create "Payroll" project for these entries. Separate from job timer entries (no task_id).
- Routes: /danny (Danny clock in/out), /payroll-admin (DJ summary view)

## CHERYL REAL ESTATE ASSISTANT
**Project moved to its own repo on 2026-04-20.**
- Repo: `windowandsolarcare-hash/cheryl-real-estate`
- Local: `C:\Users\dj\Documents\Business\A Cheryl Real Estate`
- All planning detail, status, and shared memory live there. Do not duplicate Cheryl content into this file.

## QB TO ODOO ACCOUNTING MIGRATION STATUS (updated 2026-05-09)
- **QB expenses: DONE** - 3,324 JEs imported (2019-2025), 0 failed. Journal 3, credit Chase acct 100.
- **Revenue invoices: DONE** - 2,109 invoices, dates corrected, payments applied via direct JE + reconcile.
- **2025 P&L:** Revenue 79062 | Expenses 46502 | Net 32560
- **2026 YTD:** 28979 (Jan-May partial)
- **7 missing 2025 invoices** (3284/3632 Brooke Coldren, 3478 Mike Mansi, 3647 Rik Ports, 3462 Claudia Duran, 2963 Jim Hitt, 3337 Robinson) - all have SOs, not invoiced.
- **Still needed:** Opening balances, fixed assets, loan accounts, CC bank feeds
- Cross-reference tip: Odoo origin zero-padded (003735) vs Workiz plain int (3735) - int() both sides.

## CALENDLY CITY SLUG MAPPING (paired change required)
- pmsg=Palm Springs, cathedral-city-service=Cathedral City, rm=Rancho Mirage
- pd=Palm Desert, iw=Indian Wells, indlaq=Indio/La Quinta, ht=Hemet, gb=General Booking (Monday 8:30-12 only)
- Adding new Calendly event type: MUST update reactivation code + Odoo SA 563 (see PAIRED CHANGES in CLAUDE.md)
## SAUNDERS PRINTING - COMMERCIAL WEB-TO-PRINT (green-lighted 2026-04-18)
- Business: commercial print shop - business cards, flyers, postcards, banners, etc.
- DJ has his own printer. He enters jobs, prints, ships under Saunders Printing brand.
- Platform: Odoo Website (already included) + Stripe for payments
- Three customer paths:
  1. Upload own file  Claude checks (DPI, bleed, CMYK, safe zone)  auto-converts to print-ready PDF
  2. Self-design (Canva embed SDK) - skip for v1, add later
  3. Commission design  customer fills brief + pays fee  Claude drafts  DJ approves  print
- File prep automation: Python checks resolution (300 DPI), adds bleed (0.125"), converts RGBCMYK, outputs PDF
- DJ only does: enter PDF in printer software, print, ship
- Odoo: separate company "Saunders Printing," product catalog with quantity pricing tiers, Stripe native connector
- Status: planning complete, nothing built. Build after artwork eCommerce.

## ARTWORK / eCOMMERCE (future, green-lighted 2026-04-18)
- AI artwork: Midjourney (manual only - no API), or DALL-E 3 / Stable Diffusion (real APIs)
- Sell on Etsy (has API) + Shopify (excellent API) or Odoo eCommerce
- Claude role: resize/optimize, write listings, publish to both platforms, manage orders + inventory
- Status: not started. Revisit after payroll + Cheryl are done.

## SAUNDERS RENDER APP — NEW ARCHITECTURE (2026-04-19)

### New GitHub Repo
- Repo: windowandsolarcare-hash/saunders-render-app (private)
- Local: C:\Users\dj\Documents\Business\Saunders Render App\
- Deploy: git push origin main (Render auto-deploys)
- Render service: wsc-field-assistant (same service, repo changed)
- URL: https://wsc-field-assistant.onrender.com

### Router Structure
- main.py — entry point only, mounts routers
- routers/auth.py — login + role routing
- routers/owner/dashboard.py — DJ's world
- routers/tech/jobs.py — Danny + future techs
- routers/cheryl/clients.py — Cheryl's world
- shared/odoo.py — Odoo RPC helper used by all
- static/login.html — login screen

### Login System
- URL: / → login screen (name + PIN)
- POST /api/login → looks up res.partner by name + x_render_pin → routes by x_render_role
- Fields on res.partner: x_render_pin (ID 19167), x_render_role (ID 19170), x_render_business (ID 19173)
- Roles: owner→/owner/, tech→/tech/, cheryl→/cheryl/
- No Odoo seats consumed — uses res.partner not res.users
- DJ record: partner ID 3, PIN=8487, role=owner, business=wsc

### OLD app.py
- Still running separately at old Odoo-Migration repo path (5_Mobile_Interface/)
- NOT yet migrated to new repo — W&SC tools still live there
- New repo has placeholder dashboards only for now

### Render MCP
- Added: claude mcp add render --transport http https://mcp.render.com/sse
- Needs: Render API key from Account Settings + Claude Code restart to activate

---

## RECENT DECISIONS / CONTEXT
- 2026-04-20: Balser orphan task fixed (SO 15916, task 297 created). Root cause = Phase 4 sync re-entry bug. Jose Merelies tech-gate hit (SO 17113) — diagnosed, DJ handled manually. Timer UI confirmed cosmetic-only (backend data clean). Cheryl project shipped: dashboard + client list view + 314 contacts imported. See project_session_apr20_summary.md for full detail.
- 2026-04-19: saunders-render-app repo created — new multi-business Render architecture with login, router separation, res.partner user system. LIVE.
- 2026-04-19: Odoo email font changed from Verdana to Arial (layout template IDs 387 + 388). Use mail.mail JSON-RPC to send emails — not Gmail MCP (can only draft).
- 2026-04-19: next_job_date stale bug — deleting a Workiz job without canceling first leaves stale date on contact, blocks reactivation list. Fix: cancel in Workiz before deleting. 11 contacts found with stale dates (sent email + created Odoo task ID 295).
- 2026-04-19: Reactivation screen updates — SMS box doubled (280px), SO list links open in-app (no target=_blank), main screen WZ/SO links also fixed for mobile viewport.
- 2026-04-18: Major Render UI session - photos, mic move, saved requests, timer PT times, 10-day lookahead, task_names for service type, time label on done jobs. Full state in project_render_app_apr18.md memory.
- 2026-04-18: Saunders Printing added - commercial web-to-print, Odoo Website + Stripe, automated file prep, DJ prints/ships. Full plan in project_saunders_printing.md memory.
- 2026-04-18: Multi-business platform plan finalized - Cheryl real estate, DJ+Danny payroll, artwork eCommerce, Saunders Printing all green-lighted. Build priority set.
- 2026-04-18: QB accounting migration analysis - expenses nearly all categorized, Phase 1 essentially done. Waiting on asset list + Workiz payment CSVs.
- 2026-04-16: Rebuilt Render timer to bypass Odoo entirely with GPS reverse-geocode. Migrated from OpenAI to Claude native. Added power tools and shared memory system.
- 2026-04-15: Migrated Render app from ChatGPT to Claude (Anthropic SDK)
- 2026-04-12: Added orphaned task restore, SO smart button, staggered task times, Sunday tag (508 SOs), Calendly Cathedral City, app.py timer tools
- 2026-04-02: Backfilled x_studio_next_job_date on 48 contacts
- Credit card at-door: JobAmountDue=0 + Status!=Done = CC taken. Invoice using "Credit" method  Phase 6 skips Workiz payment POST

---

## HUB SCREEN ARCHITECTURE (Built 2026-04-18)

### Routes
-   hub.html (landing screen, no auth)
-   index.html (Field Assistant, existing)
-   timeclock.html (clock in/out)
-   reactivation.html (reactivation campaign)

### Auth ()
- Body: 
- Returns: 
- DJ code = ACCESS_CODE env var (default: wsc2026)
- Danny code = DANNY_CODE env var (default: danny951) - MUST add to Render env vars

### Payroll Endpoints
-  - body:  - stores UTC timestamp in ir.config_parameter key 
-  - body:  - calculates hours, creates account.analytic.line, clears param
-  - returns 
-  - Mon-Sat hours by day, total

### Payroll Constants (env vars or defaults)
-  = 1 (Odoo hr.employee)
-  = 2 (Danny Saunders - created in Odoo 2026-04-18)
-  = 3 (Odoo project for payroll timesheets)

### Reactivation Endpoints
-  - queries Odoo: Property records, last visit >= 6mo ago, last reactivation > 1yr or never, not Do Not Contact. Returns list with partner_id, name, city, service, frequency, last_visit, est_price, last_so_id
-  - body:  - calls SA 562 in Odoo, reads x_studio_manual_sms_override, returns 
-  - body:  - writes SMS back to SO field, calls SA 563

### Danny Mode (index.html)
- Auth stores user type in localStorage 
- If danny: hides hdr-total (dollar amount), hides Stats/10-Day/Voice/Customers/To-Dos tabs
- Danny sees: field job list, timer, photos, payment

### Changelog
- 2026-04-18: Hub screen + timeclock + reactivation built and pushed to GitHub
- 2026-04-18: Danny Saunders created in Odoo (employee ID 2, 951-388-8311, nolimetangeredanny@gmail.com)
- 2026-04-19: Auth switched from DANNY_CODE env var to Odoo hr.employee.x_render_access_code field — add employees in Odoo, no Render redeploy needed
- 2026-04-19: Reactivation preview screen major expansion (see below)

## REACTIVATION SCREEN STATE - 2026-04-19

### 3 Views (single-page)
1. **view-list** — candidate cards. Name search (local filter, X to clear, auto-clears on back). Service pills + city filter (server-side).
2. **view-preview** — full detail screen:
   - Property & Contact card (purple): Service Type, Last Property Visit, Pricing Note (amber), Last Reactivation Sent, Prices Per Service block. Pills: 🏠 Property, 👤 Contact, 📋 All SOs
   - Job History card (blue): last 2 Done jobs. Per job: date, property, job type, total $, frequency, pricing note, pricing snapshot. Per job pills: 🔧 Workiz, 🟣 Odoo SO
   - SMS textarea + char count
   - Launch › → confirm bottom sheet ("Send Reactivation?" + "Send It" button)
3. **view-so-list** — all SOs for contact, same card style as candidates. Status color-coded. Tap = opens Odoo SO. Back = returns to preview.

### Done Jobs Rule (CRITICAL)
Filter: x_studio_x_studio_workiz_status = 'Done' on sale.order
NEVER use invoice_status, state='done', or date filters as proxy

### Data Sources for Preview
- Property fields (from SO's partner_shipping_id): x_studio_x_pricing, x_studio_prices_per_service, x_studio_x_studio_last_property_visit, x_studio_x_type_of_service
- Contact fields (from partner_id): x_studio_x_frequency, x_studio_last_reactivation_sent
- Per-job: x_studio_x_studio_workiz_status, x_studio_x_workiz_link, x_studio_x_studio_workiz_uuid, x_studio_x_studio_x_studio_job_type, x_studio_x_studio_pricing_snapshot

### Endpoints
- GET /api/reactivation/candidates?service=&city=
- POST /api/reactivation/preview (body: {so_id, partner_id})
- GET /api/reactivation/so_list?partner_id=
- POST /api/reactivation/launch

## CLAUDE CODE REMOTE CONTROL (set up 2026-04-20)
- DJ controls Claude Code from Galaxy Z Fold 5 via Claude mobile app
- Auto-starts at Windows login via scheduled task "ClaudeRemoteControl"
- Startup script: C:\Users\dj\start-claude-remote.bat (30s delay, cd to Migration to Odoo, launch claude.exe remote-control)
- Session name visible in Claude app: "WSC-Auto"
- Claude CLI at C:\Users\dj\.local\bin\claude.exe (native Windows .exe, not bash script)
- Push notifications: enable via /config → "Push when Claude decides" (Claude mobile app signed in with windowandsolarcare@gmail.com)
- Requires OAuth login (claude auth login); ANTHROPIC_API_KEY env var MUST NOT be set (blocks remote control)
- Requires Claude Code v2.1.110+
- Machine must be awake — sleep pauses the session
- Task registered via PowerShell Register-ScheduledTask (schtasks /create returned Access Denied even for user-scoped tasks)
- Disable: `powershell -Command "Unregister-ScheduledTask -TaskName 'ClaudeRemoteControl' -Confirm:\$false"`

---

## SESSION 2026-04-24 UPDATE — PAYROLL RETROFIT + PHASE DIAGRAMS + GUSTO INTEGRATION

### Major Deliverables

**1. PAYROLL SYSTEM RETROFIT: JSON → hr.attendance (COMPLETE)**
- Replaced ir.config_parameter JSON blobs (90-day rolloff) with Odoo native hr.attendance model
- Quarter-hour rounding (FLSA-compliant, 7-min neutral rule): applies at display/export only
- California 4-hour reporting-time pay minimum (manual toggle per shift)
- Resource calendar "W&SC Field Work" (24/7, no lunch deduction) assigned to DJ + Danny
- Migration executed: 3 shifts for DJ (4/20: 4.83h, 4/21: 5.83h, 4/22: 3.10h)
- New Render endpoints: /shifts, /shift/update, /shift/create, /shift/delete, /gusto_export
- **Manage Shifts UI**: light blue (#60a5fa) button opens modal with employee select (owner), date range, shift list, add/edit/delete, reporting-time toggle
- All hrs computed as `(check_out - check_in)` raw, rounding applied only at Gusto export time
- **Gusto CSV export**: columns `Employee Name, Date, Hours` (rounded + RTP minimum applied)
- Playwright automation skeleton created (110 lines, selectors are TODOs)
- **Documentation**: timeclock_usage_for_danny.md (Danny training), timeclock_rollout_punch_list.md (DJ tasks)
- **Odoo activities**: #52 (Danny training, due 2026-04-25), #53 (rollout tasks, due 2026-04-30)

**2. PHASE 3/4/5 FLOWCHARTS (COMPLETE)**
- Created SVG + PNG flowcharts (3200px wide, mobile-readable) for all three phases
- Flowchart files: .md (narrative), .mmd (Mermaid source), .svg (infinite scale), .png (3200px)
- Location: `3_Documentation/phase_diagrams/` in GitHub
- **Phase 3 Key Detail**: date_order on SO = Workiz JobDateTime (start time), never end time
- **Phase 4 Task Re-Entry BUG**: task deleted on substatus exit from Scheduled, NOT recreated on return (SO 17066 Wayne Geringer still orphaned, Balser SO 15916 fixed manually)
- **Phase 5A Load-Bearing Path**: writes x_studio_next_job_date on property partner after new job creation
- **Phase 5B**: populates last_date_cleaned on new maintenance jobs (service history)
- **Graveyard Rule**: always create new graveyard job, never overwrite existing future job

**3. CHERYL REAL ESTATE INTERVIEW INFRASTRUCTURE (COMPLETE)**
- 20-question behavioral interview template (deal walkthrough: pre-close → during → post-close → system stack)
- 60-minute interview day guide with setup, pacing, redirection, debrief checklist
- Whisper v20250625 transcription pipeline (Windows, local, no cloud)
- **Setup**: ffmpeg + ffprobe at C:\Users\dj\bin\, whisper via pip, models cached locally (~2GB)
- **Env var**: PYTHONIOENCODING=utf-8 (fixes Windows 3.14 Unicode error)
- **Folder per interview**: debrief.md (7-point checklist), hypothesis_before/after, audio_notes, screenshots/, documents/, VTT transcript
- **End-to-end tested**: 3-min test video → Whisper transcription (30s on GPU, accurate)
- **Status**: Waiting on Cheryl scheduling

**4. GUSTO INTEGRATION STATUS (PARTIAL)**
- ✅ CSV export endpoint created (Employee Name, Date, Hours)
- ✅ Download CSV button placed in Manage Shifts UI
- ✅ Playwright skeleton created (TODOs for selectors)
- ❌ BLOCKER: Gusto CSV format not confirmed (exact columns/headers unknown)
- ❌ BLOCKER: Download button scope wrong (exports 1 employee, should be all)
- ❌ BLOCKER: Playwright selectors not calibrated (user must run playwright codegen)

### Known Issues & Upcoming Fixes

**Payroll:**
- Today's shifts (4/23) still open — need DJ end time to close both Dan + Danny's shifts
- Gusto format mismatch will cause import failure if columns don't match Gusto's expected schema
- Button behavior needs fix: remove employee_id param from gusto_export call, query all active employees

**Phase 4:**
- Task re-entry bug (SO 17066 Wayne Geringer) — permanent fix not built; workaround = manual task creation

**Integration:**
- Playwright selectors are account-specific; user must calibrate via codegen before first use

### Implementation Order (Next Session)

1. Get Gusto CSV template from DJ (exact columns)
2. Close today's shifts (DJ provides end time)
3. Fix Download CSV button (omit employee_id, export all)
4. Update CSV export endpoint if columns don't match
5. Push all changes to main
6. DJ calibrates Playwright selectors (runs codegen, provides selectors)
7. Claude adds selectors to gusto_upload.py, push to main
8. At next pay period: DJ runs `python scripts/gusto_upload.py "path.csv"`, approves 2FA

### Memory Files Created
- project_payroll_hr_attendance_retrofit.md — full details of retrofit, rounding, endpoints, UI, Playwright, documentation
- project_phase_flowcharts.md — Phase 3/4/5 routing, date field rules, task lifecycle, next_job_date writes, task re-entry bug
- project_cheryl_interview_infrastructure.md — 20-question template, interview guide, Whisper setup, folder structure, end-to-end test results
- project_gusto_integration_status.md — CSV format blocker, button scope fix, Playwright calibration steps, checklist

### Code Changes (Already Pushed to GitHub)
- saunders-render-app: dashboard.py (payroll endpoints), timeclock.html (Manage Shifts UI), gusto_upload.py (Playwright skeleton)
- All payroll code deployed to Render; timeclock UI live at https://wsc-field-assistant.onrender.com
- Phase diagrams pushed to windowandsolarcare-hash/Odoo-Migration at 3_Documentation/phase_diagrams/

---

## SESSION 2026-04-25 UPDATE — CLEANUP + DATA SYNC

### Completed
- ✅ Summarized huge pasted chat into 4 focused memory files (stored locally + indexed)
- ✅ Updated + pushed SHARED_MEMORY.md to GitHub (session 2026-04-24 summary added)
- ✅ Cleaned up test clock-in data: deleted 4 test records from 4/6-4/18 range (20.25h total, all Dan)
- ✅ Verified Cheryl project Odoo company exists: "Cheryl Johnson, REALTOR®" (ID 2)
- ✅ Synced Dan ↔ Danny payroll records for 4/20-4/24:
  - 4/20-4/22: Updated Danny's times to match Dan's
  - 4/23-4/24: Deleted Dan's test entry, closed Danny's open 4/24 shift, added Danny's late shift
  - Both now have identical records: 4/20 (6.63h), 4/21 (7.83h), 4/22 (3.10h), 4/23 (3.63h), 4/24 (5.09h total)

### Data Integrity Notes
- **90-day limit clarification:** Old JSON system had rolling 90-day deletion (flaw). New hr.attendance has infinite history (correct). Odoo has no expiration.
- **Payroll data is now clean:** test entries removed, real shifts synced between employees, source-of-truth (Dan) propagated to Danny

### Next Steps (Not Session Scope)
- Gusto CSV format confirmation + button scope fix
- Playwright selector calibration (user runbook ready)
- Schedule Cheryl interview (infrastructure ready, waiting on her availability)


---

## SESSION 2026-05-02 UPDATE -- STALE SOs, PHASE 4A, PHASE 5 FALLBACK, DAILY SYNC MONITOR

### Phase 4A: Pre-Payment Sync Improvements
- CRITICAL: Odoo 19 sale.order.line field is product_uom_qty NOT product_qty -- wrong name returns 0 silently
- Hard unlink during cancel->draft cycle (not soft-delete / zero-qty workaround)
- Task snapshot: captures task IDs before cancel, verifies after confirm -- alerts if tasks lost
- Empty-Workiz guard: if Workiz has no line items, preserves SO lines untouched, returns line_warning
- wiz_total (float): _sync_so_with_workiz() now returns wiz_total = Workiz JobTotalPrice
- Payment gate (stale SO endpoint): Zelle must equal Workiz wiz_total within $0.01 -- any gap blocks
  - Zelle < Workiz: "Zelle is $X less than Workiz -- add tip in Workiz first"
  - Zelle > Workiz: "Zelle is $X over Workiz -- add the tip in Workiz first"
  - Orange tip pill is display-only -- does NOT allow payment without exact match

### Stale SOs Page (/owner/stale_sos)
- Lists SOs: state in [sale, done], invoice_status=to invoice, workiz_status != Done
- Zelle CSV upload stored in Odoo ir.config_parameter key render.zelle_transactions
- Matching: fuzzy last name + amount within $100 of SO total + date +-3 days = orange tip pill
- Process Payment: calls _sync_so_with_workiz() first (blocking), creates invoice, records payment
- Duplicate guard: checks invoice_ids before creating -- returns already_paid:true if invoiced
- Post-payment: removes card from memory list + clears search, no full reload

### Phase 5: Odoo Property Partner Fallback (commit f39364e, 2026-05-02)
- When Workiz job type_of_service_2 is blank/unknown:
  - Falls back to Odoo property partner x_studio_x_type_of_service + x_studio_x_frequency
  - Injects effective_frequency into workiz_job dict so schedule_next_maintenance_job picks it up
- Fixed Kristin Acker case: blank Workiz service type was creating Re-engagement Task instead of maintenance job
- Architecture: Workiz job = snapshot; property partner = intended current state (most authoritative)
  Phase 5 must check property partner when Workiz data is incomplete

### Daily Sync Monitor (2026-05-02)
- Odoo ir.cron ID=68 fires at 11am UTC daily -> GET /api/cron/daily_sync?token=wsc-daily-sync-2026
- _run_daily_sync(): syncs up to 300 open non-Done SOs; pauses 20s every 25 calls (Workiz rate limit)
- Tracks error details per SO + Workiz 429 rate-limit hit count
- Log stored: Odoo ir.config_parameter key render.daily_sync_log (JSON)
- Always emails after every run: subject "WSC Daily Sync -- Clean | X updated, 0 errors"
- Auto-alert email if errors > 0 or rate_limit_hits > 2
- Self-renewing CronCreate agent at 7:17am daily (day counter in render.sync_monitor_day in Odoo)
  At day 5 recreates itself + resets counter -- runs indefinitely while Claude session is open
- New Render endpoints (all require token=wsc-daily-sync-2026):
  GET  /api/cron/daily_sync_log          read stored log
  GET  /api/cron/monitor_tick[?reset=1]  increment day counter + return log
  POST /api/cron/notify                  send alert email body:{subject,message}

---

## SESSION 2026-05-03 UPDATE — ACTIVITIES EDIT, SYNC FIXES, CRON RESCHEDULE

### Activities Page — Full Edit Mode
- New `/api/todos/update` endpoint (POST): updates summary/date_deadline/note on mail.activity or project.task
  - mail.activity: fields summary, date_deadline, note
  - project.task: fields name (not summary), date_deadline (appends " 12:00:00"), description (not note)
  - Source field in request body: source=task uses project.task, else mail.activity
- activities.html: Edit button in detail modal opens inline edit fields for Summary, Due Date, Notes

### Stale SOs / _sync_so_with_workiz() Fixes
- CRITICAL empty-Workiz-Items bug: Workiz returns no line items -> lines_match was False
  -> cancel->draft->delete all Odoo lines->confirm -> SO had zero lines -> invoice failed
  Fix: default lines_match=True; only compare when workiz_active is non-empty
- date_order restore: action_confirm() resets date_order to now()
  Fix: write date_order back from workiz_date AFTER action_confirm (not before)
- SO name lookup: _find_so_by_identifier() tries SO name first; numeric ID only if no leading zero
  Fixes "004318" being treated as internal ID 4318

### Render Claude Tool Fixes
- sync_so_verify + process_payment_with_sync used RENDER_BASE_URL (never defined -> NameError/500)
  Fix: handlers now call internal functions directly (no HTTP self-call)
- Sync confirmation now shows customer name + amount before asking for approval

### Zelle CSV Name Matching
- _fuzzy_name_match(): prefix check on first names (GREGORY.startswith(GREG) = True)
  Fixes Greg/Gregory and similar nickname pairs in Zelle CSV matching

### Cron + CRON_SECRET
- CRON_SECRET constant was missing -> all /api/cron/* endpoints returned 500 NameError
  Fix: added CRON_SECRET = os.environ.get("CRON_SECRET", "wsc-daily-sync-2026") to config block
  Deployed commit fb77684d
- Daily sync cron rescheduled 7:17am -> 4:17am (new CronCreate job f31a624d)
  Self-renewal step in cron prompt now uses cron "17 4 * * *"

---

## SESSION 2026-05-04/05 — HEMET PAGE, DAILY SYNC FIXES, SUBMITTED JOBS PLAN

### Hemet Candidates Page (/owner/hemet)
- New page showing Hemet customers not seen 6+ months with no open SO
- Filter: last Done job >= 182 days ago OR no history; excludes Do Not Contact; excludes booked (open SO)
- Cards: name, "X mo ago" badge (red=1yr+, amber=6-12mo), address, tap-to-call phone, last job date/amount/type, pricing, frequency (gold pill), service (gray pill)
- Pill-shaped "Open in Workiz → Text" CTA button (links to app.workiz.com/root/job/{UUID}/1)
- DEDUP BUG FIX: group by parent customer, use most recent Done job across ALL property records
  Jerry Smith had "8244 Parry Dr" + "8244 Parry Drive" — old record showed 1yr ago, new one recent
  Fix: prop_by_parent groups by parent_id; most-recent-across-all-properties determines 6mo filter
- Property record is always the brain: all service data (pricing, frequency, gate code) from property record; parent = name + phone only
- API: GET /owner/api/hemet_candidates (no cache — runs live each time, ~2s)
- Hub card added to /owner/index.html (green border, "Hemet Candidates")

### Daily Sync — Timezone Fix + Cap Removal
- 50/51 SOs had date_order shifted +7h: Workiz times in PDT stored raw (08:30) -> now correctly UTC (15:30)
  _sync_so_with_workiz line ~6057: fromisoformat().replace(tzinfo=_PT).astimezone(UTC) is correct
  Old values were wrong (08:30 UTC = 1:30am PDT); new values correct (15:30 UTC = 8:30am PDT)
- Removed 30-entry cap on update_details in daily sync email (was hiding 20 of 50 changes)
  Three places removed: collection guard, update_details[:30] save, update_details[:20] email render

### Submitted Jobs — UUID Source Confirmed
- UUID for next/submitted Workiz job lives on account.move.x_studio_workiz_job_link (the invoice)
  Phase 5 writes it: update_invoice_with_workiz_link() at phase5 line ~518
  URL format: https://app.workiz.com/root/job/{UUID}/1
- NO Odoo SO exists for these jobs yet — they sit in Workiz as "Submitted"/unscheduled
  Phase 3 creates SO later, after DJ manually schedules them in Workiz
- Correct nightly scanner plan:
  1. Query account.move where x_studio_workiz_job_link is set (last ~6 months)
  2. Extract UUID from URL
  3. Skip if sale.order with that UUID already exists (Phase 3 already processed)
  4. Call Workiz job/get/{uuid}/ to verify Status=Submitted + future date
  5. Cache to ir.config_parameter key submitted_jobs_cache
- NOT YET BUILT — plan confirmed, build pending
- Workiz rate limit: speed-based only (no daily cap), batch sleeps sufficient
- Nightly cron: schedule at 5:00am after daily sync (4:17am) to avoid rate limit overlap


---

## SESSION 2026-05-07 — GPS SHIFT REVIEW PHASE 2 COMPLETE

### shift_review.html — Full Feature Build
File: static/owner/shift_review.html (723 lines, deployed e5cbe08)
URL: /owner/shift_review

**Controls:**
- Day / Range mode toggle (top left)
- Employee dropdown (loaded from /api/payroll/employees)
- Day mode: date picker with prev/next buttons, defaults to yesterday
- Range mode: From / To date pickers, defaults to last 7 days
- Load button + Geocode button

**Day view (stop timeline):**
- Summary bar: Stops, On-site, Matched/Total, Shift $/hr (green) + total revenue
- Drive bar (when drive > 0): Total drive, % of shift, Avg per leg, Total shift time
- Stop cards: time range, customer name, address, $/hr badge (green), GPS distance badge, ping count
- Ambiguous picker: multiple customers within range, tap to pick, saves permanently
- Map anchor + Data button per stop (Data shows ping timeline with accuracy color coding)
- Pinned badge on manually matched stops

**Range view (table):**
- Summary bar: Days, Total on-site, Total revenue, Avg $/hr
- Drive bar: aggregate totals
- Per-day table: Date, Stops, Revenue, On-site, Drive, $/hr
- Totals row at bottom

### New dashboard.py Endpoints (commit e7d753d3, then 1be3a31c, 3a739eef, a548cf03)
All under /owner prefix:
- GET  /api/payroll/employees          -- active hr.employees for dropdown
- POST /api/payroll/stops/match        -- save manual GPS stop to partner match permanently
- POST /api/payroll/geocode_properties -- batch geocode all un-geocoded Property records via Nominatim
- GET  /api/payroll/geocode_status     -- check geocoder progress / last result
- GET  /api/payroll/shift_range        -- per-day summary for date range (max 31 days)

Manual matches stored in ir.config_parameter key: gps.match.{emp_id}.{date}.{stop_num} = partner_id
Geocode status stored in ir.config_parameter key: gps.geocode.last_result (JSON or string "running")

### $/hr Analysis Logic
- Per-stop $/hr = SO amount_total / (duration_min / 60)
  SO lookup: partner_shipping_id IN [property_partner_id, parent_partner_id], date = that PT day
  State filter: not in cancel/draft
- Shift $/hr = total_so_amount / (total_shift_min / 60) -- includes drive time in denominator
- Per-stop $/hr uses on-site time only
- Shift $/hr uses total shift time (on-site + drive) -- DJ explicit requirement

### GPS Partner Matching -- Key Facts
- Match ONLY against res.partner where x_studio_x_studio_record_category = Property
- Fetch parent_id field on partners; display name = parent_id[1] (customer name)
  NOT the property record name (which is just the street address e.g. "221 East Sonora Road")
- Match radius: 150m from GPS centroid to property coordinates
- Ambiguous: second candidate within 30m of best -- show picker to user
- Manual match overrides auto-match; stored permanently in ir.config_parameter

### Geocoder -- Batch Property Geocoding
- Nominatim (OpenStreetMap), free, 1.1s throttle per request
- User-Agent required: WSC-FieldApp/1.0 (windowandsolarcare@gmail.com)
- Ran 2026-05-07: 166 of 878 properties were un-geocoded (712 already had coords)
- Some addresses not found by Nominatim -- fix: write actual GPS coordinates to Odoo property record
- _GEOCODE_IN_PROGRESS global flag prevents double-run; result stored in ir.config_parameter

### Known Geocoding Problem: East Sonora Road, Palm Springs
- Nominatim cannot find "221 East Sonora Road, Palm Springs" -- returns no results
- Moody Nashawaty property (ID=26941) was geocoded to wrong coords (33.8246, -116.5403)
- Actual GPS location confirmed by DJ: 33.8047028, -116.5445317 (1h37m stop on 2026-05-06)
- Fixed 2026-05-07: wrote correct coords to ID=26940 (contact) and ID=26941 (property)
- Rule: when Nominatim fails or gives wrong result, trust GPS -- write actual coords to property record

### Deployment -- shift_review.html Must Use Python
- NEVER use bash + PowerShell base64 for shift_review.html deploys
- $TEMP in bash does not resolve in PowerShell subshell -- silent empty content -- broke page entirely
- Always use Python subprocess + base64.b64encode pattern:
  python3 -c "import base64,json,subprocess; [read file, encode, get sha, PUT via gh api]"
- safe_deploy.py handles dashboard.py correctly (uses Python internally)

### Employee IDs (hr.employee)
- Dan Saunders (DJ): ID = 1
- Danny Saunders: ID = 2

---

## SESSION 2026-05-08 — FIELD.HTML UPGRADES + SHIFT REVIEW IMPROVEMENTS + CRON FIX

### Render Cron — Duplicate Daily Sync Emails (FIXED)
- BUG: Render cron with autoDeploy=yes fires an extra run on every commit push (not just on schedule)
- Overnight session commits caused WSC Daily Sync to run twice → two identical emails
- FIX: Disable autoDeploy via Render REST API:
  curl -X PATCH https://api.render.com/v1/services/{serviceId} \
    -H "Authorization: Bearer {RENDER_API_KEY}" -d '{"autoDeploy":"no"}'
- RENDER_API_KEY: ~/.claude/mcp.json under render → headers → Authorization
- WSC Daily Sync (crn-d7t3c4i8qa3s73f64fhg): autoDeploy disabled 2026-05-08
- Rule: any NEW Render cron job → immediately disable autoDeploy via REST API

### field.html — Stale-While-Revalidate Cache
- loadField() split: _applyFieldData(data, upcomingData) renders; loadField() manages fetch lifecycle
- Cache key: wsc_field_cache_{AC} in localStorage — per access code, instant render on open
- _loadFieldInFlight guard prevents double-fetch
- Refresh button: spins during fetch, flashes ✓ for 1.2s on completion

### field.html — Weather Per Day
- Day headers show high temp + UV index: "82° UV 8" in center of each day header
- Today: navigator.geolocation → city fallback from first job address if denied
- Future days: city parsed from first job address → Open-Meteo geocode → Google Weather forecast
- Google Weather API: https://weather.googleapis.com/v1/forecast/days:lookup (IMPERIAL units)
- Open-Meteo geocoding: https://geocoding-api.open-meteo.com/v1/search (free, no key)
- Cache: _wxCache{} keyed by "lat,lng" — avoids duplicate geocode calls
- GCP key: AIzaSyA2D5Sd7IPOi2h65G4pew7QuXAko3bOO60 — DJ must add "Weather API" in Cloud Console

### field.html — 3-dot Menu on Active Job Panel
- toggleActiveJobMenu(ev, btn) populates data attrs from activeJob then calls toggleJobMenu()
- Button id="ap-menu-btn" — full color var(--text), font-size 22px (was muted/invisible)

### shift_review.html — 3-dot Menu on Stop Cards (770 lines)
- ⋯ button in .stop-actions row per stop card; toggleStopMenu() / closeStopMenu()
- workiz_link added to /api/payroll/stops response (from x_studio_x_workiz_link on SO)

### shift_review.html — Range View Revenue Fix
- Revenue now: confirmed SOs by date_order (state not in ['cancel','draft']) — no GPS match gate
- Fixes $0 revenue on days where GPS stops were unmatched to partners

### CRITICAL: shift_review.html Source of Truth
- Local repo copy (Saunders Render App/static/owner/shift_review.html) = OLD 290-line version
- ALWAYS fetch from GitHub before editing:
  gh api repos/windowandsolarcare-hash/saunders-render-app/contents/static/owner/shift_review.html \
    --jq '.content' | base64 -d > /tmp/sr.html
- Deploy method: Python base64 only (bash+PowerShell silently produces empty content)

---

## Saunders Printing — HOF PO Automation (Step 1 Complete)

### Files Deployed (saunders-render-app)
- `routers/printing/watcher.py` — IMAP + Claude Haiku + Odoo HOF PO watcher
- `routers/printing/jobs.py` — added GET /printing/api/check-po manual trigger
- `main.py` — imports watcher, runs check_hof_emails() every 30 min via APScheduler

### Env Var
- `GMAIL_WSC_APP_PASSWORD=vjuckohpqgwmlmxw` — windowandsolarcare@gmail.com app password (Render srv-d78le0fkijhs738dsli0)

### Email Forwarding
- dan@scenicartprint.com → windowandsolarcare@gmail.com (all mail forwarded, DJ set up)
- Zoo's outgoing email changed to dan@scenicartprint.com

### How check_hof_emails() works
1. IMAP UNSEEN FROM @baseballhall.org in windowandsolarcare@gmail.com INBOX
2. Extracts PDF attachment → Claude Haiku document API → {po_number, card_type, cards[]}
3. Idempotency: skips if po_number already in ir.config_parameter blob
4. Calculates: card_rate x qty + $0.025 x qty (banding) + freight (linear interpolation)
5. Creates Odoo invoice (company=3, journal=21, partner=26947, 3 lines on acct 266)
6. Appends job to saunders.printing.jobs blob with po_received=done
7. Marks email read, notifies DJ via mail.mail

### Manual Test
https://wsc-field-assistant.onrender.com/printing/api/check-po

### Odoo Constants (watcher.py)
- HOF_PARTNER_ID=26947, SAUNDERS_COMPANY_ID=3, SAUNDERS_JOURNAL_ID=21, REVENUE_ACCOUNT_ID=266
- PARAM_KEY=saunders.printing.jobs

### Remaining Steps to Build
- Step 5: Zoo shipping email watcher (similar to watcher.py)
- Step 6: Invoice approval — email DJ PDF + Approve button → smtplib BCC → 8 AM queued send
- Steps 2/3/4/7: Manual (no automation planned yet)

---

## SESSION 2026-05-11 — QL_PANEL UI FIXES + SCHEDULING UUID FIX

### CF Tag Fix (ql_panel.js)
- Partner category tags (e.g. "CF") live on the main contact, not the property child record
- `_get_jobs_for_date` now fetches `parent_id` and merges parent partner categories into child entries
- Without this fix, CF and other tags were invisible on property-address jobs

### Customer Tab — Mobile Fix (ql_panel.js)
- `#office-panel` is `display:none` on mobile (< 600px) — customers pane lives inside it
- Fix: 👤 button sets `#office-panel` to `position:fixed; inset:0` overlay with "✕ Done" dismiss
- From other pages: `localStorage.setItem('ql_open_tab','customers')` before navigating → field.html polling block auto-opens on load

### Voice Modal Autocomplete — #vm-ac-panel (ql_panel.js)
- When a voice command has ____ and field:'customer', selecting it opens a search panel
- Customer: fetches /owner/api/search (350ms debounce); City: filters static CITIES array
- Selecting a result replaces ____ in the textarea and closes the panel
- Panel: top:132px; left:0; right:0; bottom:0 inside .vm-sheet
- iOS autofill: type="search" + autocapitalize="off" suppresses autofill bar

### Sticky Headers (ql_panel.js)
- 6 page headers now position:sticky; top:0; z-index:200 — don't scroll away on any page

### Scheduling — UUID Fix (dashboard.py)
- _find_scheduling_openings now queries for the customer's open/Submitted SO and includes its UUID in the response
- Output includes: Existing open job: S00123 (Submitted) — source_uuid='ABCD1234' pass this to schedule_job
- Claude reads that UUID and passes it directly to schedule_job — was previously passing wrong value
- _create_new() now falls back to Submitted jobs if no Done jobs exist (was: "No Done jobs found" error)

### Other dashboard.py Changes
- get_customer_jobs tool: fast single-call customer job lookup — replaces slow multi-step AI reasoning
- LOOKAHEAD_DAYS extended: 14 to 45 days in _find_scheduling_openings
- System prompt: CARRY CUSTOMER CONTEXT rule (remember named customer across turns); SUBMITTED JOB rule (treat Submitted as reschedulable)

### Reactivation Scheduling Flow — TABLED (2 Tasks Pending)
- Task 1: Check Bruce Johnson tomorrow — should have 3 SOs in Odoo after overnight sync. If only 2, Phase 4 is not picking up reactivation-created Submitted jobs.
- Task 2 (future): When customer has 2 open SOs: ask DJ — reactivation call-in or regular? When 1 open SO from reactivation lead: auto-route: schedule + mark CRM lead won + clear graveyard UUID.
- _update_uuid already clears x_workiz_graveyard_uuid and x_workiz_graveyard_link on the CRM lead. Missing: mark lead won + clarifying question logic.

### Deployed Commits (saunders-render-app)
- ql_panel.js: 914b07f1 (31,622 bytes)
- dashboard.py: 8f0959cd (536,983 bytes)

---

## SESSION 2026-05-12 — OWNTRACKS ARCHITECTURE + CALENDLY FIX + TIMER LOG

### OwnTracks GPS Architecture (MAJOR PIVOT)
- Replaced browser watchPosition GPS with OwnTracks native app (HTTP mode)
- Root cause: iOS Safari suspends background tabs after 30s of screen lock — auto clock-out was never going to work in browser
- OwnTracks runs as a native background location service registered with the OS — works with phone locked
- New endpoint: POST /owner/api/owntracks/webhook?token=<OWNTRACKS_SECRET>
- Transition _type='transition': leave Home → auto clock-in; enter Home → auto clock-out
- Location _type='location': stores ping in x_gps_ping while clocked in (Phase 2 analysis unchanged)
- TID→employee mapping stored in Odoo ir.config_parameter keys owntracks.tid.<TID> = employee_id
- Current mappings seeded: owntracks.tid.DJ=1, owntracks.tid.DS=1, owntracks.tid.DN=2
- Adding new employee: Odoo → Settings → Technical → System Parameters → New (no code deploy needed)
- OWNTRACKS_SECRET env var must be set on Render (prevents unauthorized pings)
- field.html: removed WSC_GPS.start/stop/pause/resume, gps_tracker.js script tag, pollFieldClockStatus, gps-status div
- gps_tracker.js: file still exists but no longer loaded — manual GPS still available via getGPS() for timer entries
- DJ still needs to: install OwnTracks app, set server URL, set TID="DJ", create Home_Base geofence

### Calendly Booking — Address Parsing Fix (zapier_calendly_booking_FLATTENED_FINAL.py)
- Bug: Katie Sullivan typed "1250 North Kirby Street SPC 150" (no comma before unit) → Phase 3A extracted full string → no Odoo match → silent failure
- Fix 1: Strip unit designators (SPC, Apt, Suite, Unit, #, Bldg, etc.) from street before lookup using regex
- Fix 2: Changed Odoo property search from exact "=" to "ilike" for extra safety
- Fix 3: Added fallback project.task To-Do when Phase 3A or 3B fails — never silently drops a booking
  - Fallback To-Do contains: customer name, email, raw address typed, service, date/time, notes
  - Appears in Odoo To-Dos list so DJ can manually correct address and process
- Katie Sullivan manually processed: SO 17237, Workiz H5IBCC, May 26 2026 1:00 PM Pacific, "Outside Windows and Screens"

### Timer Log — Server-Driven Persistence (field.html + dashboard.py)
- Problem: timer log was in-memory JS only — voice-driven start/stop never updated the UI; log cleared on job open
- Fix: new GET /api/timer/sessions?task_ids=X,Y endpoint returns today's timesheets + active config params
- refreshTimerDisplay() fetches from server and rebuilds timerLog — called after voice responses mentioning "timer"
- Multiple simultaneous timers all show in log with task name + time range
- Timer log survives job re-open (loads from Odoo timesheets, not RAM)

### Workiz Status/SubStatus Routing Fix (dashboard.py — schedule_job tool)
- Bug: sending SubStatus=Submitted returned Workiz 400 error
- Rule: Submitted/Done/Canceled/In Progress are top-level Status values — never SubStatus
- _TOP_LEVEL_STATUSES set + _status_payload() + _status_label() helpers route correctly
- job/create/ never sends Status or SubStatus — Workiz auto-assigns Submitted
- After create: if target status is NOT submitted, do separate job/update/ with correct routing

### Hemet → Reactivation Deep Link (field.html + hemet.html + dashboard.py)
- New endpoint: GET /api/reactivation/open_by_partner?contact_id=X
- hemet.html: "Reactivate" button is now a link to /owner/reactivation?contact_id=X
- reactivation.html: detects contact_id URL param, loads single candidate, sets _deepLinkMode=true
- Back button in _deepLinkMode returns to /owner/hemet (not empty candidates list)
- 6-month hard exclude: contacts reactivated within 183 days excluded from Hemet list entirely

### Reactivation Jobs on Schedule — Fixed (dashboard.py)
- Graveyard jobs (JobType=Reactivation Lead) get Workiz date assigned → Phase 3/4 creates Odoo SOs → appeared in upcoming
- Fix: /api/upcoming domain filter adds ['x_studio_x_studio_x_studio_job_type', 'not ilike', 'reactivation']

### Auto-Select Single Open Job (dashboard.py — schedule_job tool)
- When only 1 existing job option found (open SO, invoice job, or graveyard lead), auto-selects it
- Eliminates the "1" reply fragmentation pattern

### Timer Architecture (field.html + timeclock.py) — 2026-05-23
- Active timer: `localStorage['wsc_timer']` = `{so_id, start_ms, employee_id}` — instant Start, no network
- Permanent records: `ir.config_parameter` key `timer.so.{so_id}` = JSON array of completed sessions
- Crew snapshot: `ir.config_parameter` key `crew.today.YYYY-MM-DD` = `[{id, name}]` (set by clockin_crew)
- Stop calls `POST /owner/api/timer/log` — reads crew, reads `hr.employee.hourly_wage` for each member, calculates per-person labor cost, writes record + SO chatter
- `employee_id` is optional — DJ's `owner` access code has no employeeId; backend falls back to crew list
- DO NOT use hr.attendance (payroll), account.analytic.line (billable), or project.task timers for labor tracking

### Source Stamps on project.task Creates — 2026-05-23
All programmatic project.task creates now stamp description with:
- `📍 Source: field.py → create_todo` — voice To-Dos
- `📍 Source: field.py → schedule_job` — Review before sending tasks
- `📍 Source: zapier_calendly_booking → fallback_todo`
- `📍 Source: zapier_phase4 → backfill_task`
- `📍 Source: zapier_phase5 → re-engagement`
No stamp = created natively in Odoo by DJ.

### Follow-Up Context Rule — 2026-05-23
`create_todo` tool now always asks "What do you want to follow up about?" before creating a To-Do if the user hasn't provided a specific note. Never create a vague To-Do with just a name.

### Past Due Section in Calendar — 2026-05-23
`#pastdue-section` at bottom of calendar.html — shows all activities where `t.date < today`. Red header, collapsible, ✓ done button on each item.

### Task Sync Disabled — 2026-05-28
All project.task creation/sync/removal logic in Phase 3 and Phase 4 is **commented out**.
- Kept: SO data sync, SO confirmation on scheduling trigger, partner/property updates
- Removed: sync_tasks_from_so_and_job() calls, backfill task logic, task removal on Submitted
- Field assistant gate is SO state in ['sale','done'] — tasks were never needed for visibility

### Phase 5 Reminder Activity Flow — 2026-05-28
When Phase 5 creates a Submitted Workiz job, Phase 3 creates a mail.activity on the new SO:
- Type: "Follow-up" (activity_type_id=15, created 2026-05-28)
- Summary: "Add tech + line items — [Customer] · [City] · [Date]"
- Note: "WORKIZ_UUID:{uuid}
{JobNotes}" — line items parseable by p5ParseItems()
- Activities page shows special card with "📋 Copy Items & Open in Workiz → Items" button
- Phase 4 auto-deletes the activity when SO is confirmed (job scheduled)
- mail.activity.type IDs: Follow-up=15, To-Do=4
- ir.model sale.order ID = 670 (needed for res_model_id in mail.activity)

### Customer Notes System — 2026-06-03
Three note types on the field assistant job detail screen:

**1. To-Do Notes** (`project.task`, `project_id=False`, `partner_id` set):
- Created via "📝 Note" button on detail screen. Has due date, add/edit/delete.
- Shows in Render Activities tab, Odoo To-do app, and job detail Notes card.
- Endpoint: `POST /api/todos/create`, `GET /api/todos/for_partner?partner_id=X`
- Notes are tied to the **property partner** (not contact) — appear on every future job for that property automatically.

**2. Permanent Property Note** (`x_studio_x_field_note` on `res.partner`):
- Field ID: 20866. Type: text. Store: True. On `res.partner` (model ID 90).
- Always visible on job detail as teal "📌 Property Note" card. Shows "NONE" if empty.
- Endpoint: `POST /api/partner/field_note`
- Fetched in `tool_get_schedule` partner batch read — returned as `field_note` on each job.

### Historical Job View — 2026-06-03
Tapping a past job row in Job History / Customer tab / Calendar opens a read-only view:
- Services (line items + total), Payment (date/amount/method), Photos (3-col thumbnail grid, tap for lightbox)
- Endpoints: `GET /api/so_history?so_id=X`, `GET /api/attachment_image?att_id=X`
- Odoo photos (ir.attachment) are NOT publicly accessible — must proxy through Render.
- `Cache-Control: max-age=86400` on image proxy to avoid re-fetching.
- Future jobs open the full live active panel (not read-only).

### Calendar Tap-to-Open — 2026-06-03
Calendar job rows now navigate to `/owner/field?open_so=X&date_raw=YYYY-MM-DD`.
`openJobById(soId, dateRaw)` in field.html detects URL param, opens correct view:
- Today's job in schedule → full live panel (exact object)
- Future date → live panel (fetches from /api/so_history)
- Past date → historical read-only view

### KEY VOCABULARY (added to CLAUDE.md)
"The schedule" = Render field assistant daily job list. Gate: `state in ['sale','done']` AND `date_order` = that day. Submitted jobs are NOT on the schedule (draft quotations). A job lands on the schedule when Workiz status is Scheduled / Send Confirmation - Text / Next Appointment - Text / Next Appointment 2 - Text.
