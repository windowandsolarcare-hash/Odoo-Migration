---
name: project_workiz_retirement
description: "★ NEXT BIG PROJECT (DJ 2026-07-31): Workiz is being RETIRED — get every Workiz API call out of the loop, Odoo becomes the single source of truth. DISCUSS each touchpoint first, don't rip out blindly. Inventory + approach here."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-08-01T05:10:07.020Z
---

**DJ, 2026-07-31: "Workiz no longer exists. Everywhere a Workiz API call is used, I want to discuss how to get it out of the loop."** This is the next big project, to be started in a FRESH context. **This is a DISCUSSION/PLANNING task first — do NOT start ripping Workiz out blindly.** Many live flows depend on it; each touchpoint needs a replacement decided with DJ before it's removed. **Workiz goes dark Monday AM (2026-08-03); historical data still readable.**

## PROGRESS (2026-07-31, this session)
- **FULL INVENTORY DONE** → `3_Documentation/WORKIZ_RETIREMENT_INVENTORY.md` (Odoo-Migration repo). Every `api.workiz.com` call classified by the 7 roles + Monday severity, plus the Zapier phases + Odoo SAs. ~70 live call sites in the app.
- **Structural finding:** Workiz access is NOT centralized — token+get/post helpers re-implemented in ~7 places (shared.py canonical; dashboard.py own copy; hemet.py, submitted_jobs.py, booking_requests.py owner, payments.py, provenance.py each have their own). `execute_write_tool` (create/update/delete dispatcher) exists TWICE: dashboard.py AND field.py. A single kill-switch would need ~7 edits unless funneled through one client first.
- **PHASE A FIX SHIPPED (money-critical):** payments were about to be BLOCKED Monday. `_sync_so_with_workiz` runs before every payment record and hard-refused if the Workiz fetch failed. Flipped the two Workiz-UNREACHABLE branches (429 + fetch-exception) from `ok:False`→`ok:True` in BOTH twins — payments.py (~L1044/1053) and dashboard.py (~L10059/10068) — so a dead Workiz silently no-ops and the payment records anyway. Legit no-tech gate untouched; Zelle exact-match gate self-skips (wiz_total=0). Deployed to main 2026-07-31.
- **Severity ranking for Monday (in the doc):** 1) payments block (FIXED), 2) booking-confirmation texts still on Workiz status (reminders.py/messaging.py already do 3-day/night-before via Twilio), 3) reactivation/re-engagement SMS die entirely (sent via Workiz status flip — hemet L391, reactivation L1208, SA 563), 4) mark-Done/schedule/reschedule (drives Phase 5/6), 5) job creation (Odoo SO already made; drop Workiz twin), 6) notes/delete/display reads degrade quietly.
- Suggested cutover order: Phase A defensive fail-silent (done for payments) → B reactivation onto messaging.send() → C mark-Done+schedule app-driven → D job-creation Odoo-only → E retire Zapier phases/SAs + vestigial fields, update CLAUDE.md. NEXT ROLE not started — awaiting DJ.

## What already changed
- The phone number was **ported to Twilio** (~2026-07-30/31). Customer texting is now Twilio via `messaging.send` — NOT Workiz. Port is done and verified live. See [[project_hud_followups_surface]].
- So the biggest Workiz role — **status-driven confirmation texts** (Workiz job status → automated SMS) — must now be fired from the app/Odoo via Twilio, not Workiz.

## The goal
Remove Workiz from EVERY loop. **Odoo becomes the single source of truth** for jobs/schedule; the **Render field app + Twilio** take over the roles Workiz played (job status changes, confirmations, job records). Keep the *behavior* (schedule, confirmations, reactivation, etc.) — replace the *source/engine* underneath.

## Workiz roles that need a replacement (decide each with DJ)
1. **Job creation** — Phase 5 / booking / New Job currently create a Workiz job (and an Odoo SO). → Odoo SO becomes the only record; drop the Workiz job create.
2. **Job status → confirmation texts** — Workiz statuses (Scheduled / Send Confirmation - Text / Next Appointment - Text / Next Appointment 2 - Text) fired customer texts. → App sets status + fires Twilio confirmations directly.
3. **Phase 4 SO confirmation** — confirms the Odoo SO when Workiz status flips. → Trigger SO confirm from the app action instead of polling Workiz.
4. **The "schedule"** — already Odoo-driven (field app gate = SO state in ['sale','done'] AND date_order = that day). Workiz was just where DJ set status. → Status changes move into the app.
5. **Reactivation / re-engagement** — Odoo server actions + reactivation.py create/convert Workiz jobs and read Workiz job data. → Rework to Odoo-only.
6. **"Open in Workiz" / "Use this job" links** — job detail + New Job `openJob` open the Workiz job URL. → Point at the Odoo SO / app job detail instead.
7. **SO Workiz custom fields** — `x_studio_x_studio_workiz_uuid`, `_workiz_status`, `_workiz_link`, `_workiz_tech`, graveyard/historical UUIDs on crm.lead — become vestigial (keep for history, stop writing/reading as live).

## Code inventory (where Workiz API calls live — grounding for the plan)
- **App repo (`saunders-render-app`) routers** (grep `api.workiz.com`, `workiz_post`, `workiz_get`, `WORKIZ_TOKEN`, `job/{get,create,update,delete}`): `shared.py` (the `workiz_post`/`workiz_get` helpers + token), `field.py`, `reactivation.py`, `hemet.py`, `booking_requests.py`, `submitted_jobs.py`, `quotes.py`, `timeclock.py`, `provenance.py`, `payments.py`, `activities.py`, `stale_sos.py`, `scheduler.py`, `brain.py`. (~15 files.)
- **Zapier phases** (`Odoo-Migration` repo, `1_Production_Code/`): Phase 3 (new job), Phase 4 (status sync), Phase 5 (auto-schedule), Phase 6 (payment sync) — the whole Workiz↔Odoo sync engine. Phase 2/2B reactivation + STOP.
- **Odoo server actions**: reactivation LAUNCH (SA 563) and others create/read Workiz jobs via `requests.get/post` to api.workiz.com.

## Approach for the fresh session
1. Do a precise inventory: for each file above, list each Workiz call and WHAT it does (read job / create / update status / delete / link).
2. Group by role (the 7 above). For each, propose the Odoo/app/Twilio replacement and confirm with DJ before changing anything.
3. Migrate one role at a time; keep behavior identical; verify each before the next. Don't remove working code without DJ's OK ([[feedback_never_remove_working_code]]).
4. **Heads-up:** CLAUDE.md and many memories still describe Workiz as the live system (status rules, API quirks, phases, "the schedule" gate). Treat all of that as LEGACY pending this migration — but do not delete it until each piece is actually replaced. Update CLAUDE.md's Workiz sections as part of the migration, not before.

DJ wants to talk through HOW before execution. Start there. See [[feedback_ported_means_twilio]], [[feedback_question_when_big_picture_wrong]], [[project_calendly_retired]] (prior retirement pattern).
