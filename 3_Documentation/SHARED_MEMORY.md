# SHARED MEMORY - Window & Solar Care
# Synced between Claude Code (local) and Render Claude (field assistant)
# Last updated: 2026-04-25
# Format: key facts only - both Claudes read this on every session

## OWNER
- Dan Saunders (goes by DJ) - owner and sole technician, Window & Solar Care, Southern California
- Email: windowandsolarcare@gmail.com

## PLATFORMS
- Odoo: https://window-solar-care.odoo.com (DB: window-solar-care, User ID: 2)
- Workiz: job scheduling - IP-restricted, proxy through Odoo if calling from local machine
- GitHub: windowandsolarcare-hash/Odoo-Migration (main branch only)
- Render: mobile field assistant at https://[render-url] - always-on paid plan
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


## GITHUB DEPLOYMENT (2026-04-26)
**RULE: Use bash + base64 + temp file approach. NEVER use PowerShell ConvertTo-Json.**
- PowerShell ConvertTo-Json causes "Problems parsing JSON" HTTP 400 errors (4-5 retries typical, 50-100 wasted tokens per error)
- Root cause: [System.Convert]::ToBase64String() adds MIME line breaks; PowerShell escapes JSON in ways that break API validation
- Solution: bash + base64 + temp file = 99%+ first-try success rate
- Deploy script: `deploy_to_github.sh` (in both repos) handles Windows file paths, base64 encoding, temp JSON, gh API push
- Usage: `./deploy_to_github.sh <repo> <file_path> <local_file> <commit_message>`
- Example: `./deploy_to_github.sh windowandsolarcare-hash/Odoo-Migration 1_Production_Code/phase3.py "/path/phase3.py" "2026-04-26 | phase3.py | fixed bug"`
- CLAUDE.md updated 2026-04-26 with full documentation + fallback bash command

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

## RENDER APP STATE - 2026-04-18

### Endpoints
- GET /api/dashboard - today's schedule + stats
- GET /api/upcoming - 14 calendar day lookahead (~10 work days)
- POST /api/timer/start - starts Render timer
- POST /api/timer/stop - stops timer, creates timesheet, reverse-geocodes GPS
- POST /api/payment - records payment, creates invoice, posts chatter
- POST /api/attachment - uploads base64 image to Odoo SO as ir.attachment

### Claude Tools (full list)
Read: search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job,
      get_sales, get_sales_week (Mon-Sat), get_sales_month (Mon-Fri, returns days dict),
      get_jobs_list, navigate_to, odoo_query, github_read_file, github_list_dir, refresh_shared_memory
Write (confirm required): update_workiz_field, update_odoo_contact, post_odoo_note, create_todo,
      mark_job_done, create_workiz_job, duplicate_workiz_job, start_task_timer, stop_task_timer,
      record_check_payment, odoo_write, github_push_file, update_shared_memory
Utility: save_memory, delete_memory

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

## QB TO ODOO ACCOUNTING MIGRATION STATUS (2026-04-18)
- File: C:\Users\dj\Downloads\Window & Solar Care_Transaction Detail by Account.csv
- 6,318 expense rows. Only 62 blank-category rows (28 loan payments, 26 blank name, 7 owner draws, 1 USPS, 2 true uncategorized)
- Phase 1 (expense categorization) essentially DONE - almost no cleanup needed
- Still need from DJ: QB Fixed Asset List, 6x Workiz Payment CSVs (one per year)

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
