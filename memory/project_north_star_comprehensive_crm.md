---
name: project_north_star_comprehensive_crm
description: "★ THE NORTH STAR (read for any strategic/architecture decision): the whole Workiz→Odoo migration exists to build a COMPREHENSIVE CRM. Approach = use Odoo's engine, wrap in friendly Render field-UI, extend where Odoo's stock UI/logic is weak. All the apps we've shipped are pillars of this one CRM."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ confirmed 2026-06-17: the entire reason for migrating off Workiz to Odoo was that Workiz lacks a real CRM, and Odoo (customized) can be one. The North Star = a COMPREHENSIVE CRM, not a light one.** Check every substantial build against "does this advance the CRM?"

## The approach (PROVEN pattern — apply everywhere)
**Use Odoo's engine + build a friendly Render UI on top + extend only where Odoo's stock UI/logic is lacking.** Odoo's CRM engine is strong (real pipeline `crm.lead`, the `res.partner` contact model, activities, marketing automation); its stock UI is clunky for a phone in the field. So: lean on the engine, build field-grade UX on Render, add logic where weak. (We just proved this on tasks via `project.task`; it scales to the full CRM. Constraint stays: NO custom Odoo models — `project.task`/`crm.lead`/`res.partner` are all standard, fine.)

## Reframe: the "separate apps" are PILLARS of ONE CRM
Everything shipped under different names is actually one CRM being assembled:
| Shipped as | CRM module | State |
|---|---|---|
| Customer "brain" / Customer tab (field.html) | **Contacts** (360° customer) | in progress |
| My Day / action items / command-center | **Activity Management** (tasks + follow-ups) | active build |
| Reactivation engine + graveyard (`crm.lead`) | **Pipeline / Leads + Campaigns** | partial |
| Customer Analytics (active/lapsed, segments) | **Segmentation & Insights** | built |
| Texts via Workiz / future Twilio A2P | **Communications log** (per-customer) | partial |
| Reviews / blasts (planned) | **Marketing automation** | planned |

→ Stop treating these as standalone; design them to interlock around the customer record.

## "Light CRM" terminology
When discussing tasks/follow-ups, "light CRM" = just the Activity-Management layer (that layer being light-touch is fine). It does NOT describe the destination. The destination is comprehensive. Don't let the term shrink the vision.

## How the current command-center work fits
The Action-Item model ([[project_gcal_to_work_schedule]] command-center thread) = the **Activity Management pillar**. Model agreed 2026-06-17: **Jobs (`sale.order`) + ONE Action-Item entity (`project.task`)** typed `Task | Follow-up` (Reactivation = a Follow-up reason), optional date, optional customer link (`partner_id`), priority, tags, subtasks. project.task already natively supports subtasks/customer-link/priority/tags — underused. Customer "circle-back" (customer brain shows their tasks/follow-ups) falls out of `partner_id` for free.

## Build sequence
- **0 ✅ kill Planner** (commented out, reversible).
- **1 ✅ add Type field (DONE 2026-06-17).** Custom char field **`x_myday_type`** (id 20879) on project.task (model id 856), values `'task'` | `'followup'`. Backfilled 203 My Day tasks (35 task / 168 followup, derived from name: `Re-engagement:`/`[Render] Follow-up:`/`Follow up…` → followup, else task). myday.py: add/update/list/recur-spawn handle it; output key **`kind`** (activities hard-coded `kind:'followup'` — a mail.activity = a reminder to contact = Follow-up). myday.html: **Type select (✅ Task / 📞 Follow-up) in Add + Edit sheets**, kind chip on cards, new **Type grouping mode** (segment row Date/Type/Category/Priority). Verified end-to-end. See [[project_myday_reminders]].
- **2 ✅ customer circle-back (DONE 2026-06-17).** `/api/customer_jobs` (dashboard.py) now also returns **`actions`** = open `project.task` (partner_id in [contact + property ids], project_id=False, not done/canceled) + `mail.activity` (res_model='res.partner', res_id in same), each with `kind`/title/date/priority, sorted by date. field.html customer brain (`openCustJobRow`) renders a **"☀️ Action Items (N)"** section between the property header and Jobs (✅/📞 icon, 🔴/🟡 priority, date or "no date"). Verified (Joan Flickinger 23261 → her follow-up shows). So from a customer you now see everything pending for them (the back-and-forth). Customer-side is display-only (tap-to-edit = future). **REVERSE link DONE 2026-06-17:** the My Day task editor's Customer field has a **"🧑 Open customer card →"** button (`tkOpenCustomer` → `/owner/field?tab=customers&cust_q=&cust_pid=` — field.html's existing deep-link). So both directions: customer→their tasks, AND task→the customer brain.
- **3 ✅ Upcoming advance-look (DONE 2026-06-17).** calendar.html: new collapsible **"🔜 Upcoming"** section (above Today's List) = next 21 days, day-grouped (Today/Tomorrow/Wed Jun 25…), each day showing jobs (🧰) + action items (✅/📞, 🔁 projected-recurring) + Google events (📅), untimed last; tap a day header → opens that day-sheet. **Each ROW is clickable too (2026-06-17):** job→`goToField`, task/followup→`/owner/activities?open=id`, gcal→its link. Respects the Jobs / ☀️ My Day toggles; excludes done items. Own data: `loadUpcoming()` fetches `/api/calendar_jobs?start=&end=` (next 20d) into `upcomingJobs` (separate from month-only `calData`) + `actsByDate` + `gcalEventsForDate`. ⚠ **SHADOWING:** `/api/calendar_jobs` is defined in BOTH dashboard.py AND calendar.py — dashboard registers first and WINS. Added the start/end range to the **dashboard.py** copy (editing calendar.py's did nothing). See [[project_reactivation_route_shadowed_in_dashboard]].
- **4 consolidate** `mail.activity` reactivation/followup reminders → `project.task` Follow-ups (deep; touches the automation that creates them).

## CANONICAL SPEC
**`3_Documentation/ACTIVITY_MANAGEMENT_SPEC.md`** (in Odoo-Migration repo, pushed 2026-06-17) = the authoritative Activity-Management pillar spec: the 2-entity model (Job=sale.order + Action Item=project.task typed Task/Followup), field reference, the views, built steps 0-3, and the **detailed Step 4 consolidation plan**. Read/update it for any action-item work.

## NEXT
**STEP A ✅ DONE (2026-06-17):** My Day editor is now the COMPLETE view (toward dumping Activities).
- My Day card tap on a TASK → opens the rich editor (`openTask`), NOT Activities (`openRecord` branches on source; activities still → Activities until Step B migrates them).
- Editor gained a **Customer** field (search, generalized `custSearch(val,px)` px='a'/'tk'; `/api/myday` outputs `partner_id`; `/api/myday/update` saves it).
- Editor gained a **🚀 Launch re-engagement text** button (shown when kind='followup' && partner_id): `tkLaunchPrep` → `/api/followup/preview` (builds SMS, shows editable textarea) → `tkLaunchSend` → `/api/followup/launch` (NO activity_id — that param archives a mail.activity; for a project.task we instead call `/api/myday/done` after a successful send). Reuses the EXACT endpoints + all gates (cooldown/STOP/DNC/phone).
- **Calendar** task action-items route to `/owner/myday?open=<id>&from=calendar` (activities → `/owner/activities?...`). My Day `handleDeepLink()` opens that task's editor and `closeTask` returns to `_returnTo` (the origin) on close.
- ⚠ Launch currently works for `project.task` follow-ups (the bulk). mail.activity follow-ups still open in Activities — resolved by Step B (migrate them to tasks).
**STEP B mostly DONE (2026-06-17) — AUDIT REFRAMED IT (it was ~95% already done):**
- Re-engagement/reactivation items are ALREADY 152 `project.task`s, **ZERO mail.activity** — Step A handles them in My Day w/ Launch. The big feared migration didn't exist.
- Open mail.activity for DJ was only **3**: 2 personal dev to-dos → MIGRATED to project.task (ids 993/994, activities archived); 1 = the transient "Add tech + line items" booking reminder.
- **Activities TILE removed** from the dashboard (index.html ~L474, commented out; route `/owner/activities` KEPT as a fallback). My Day is the single home now.
- **CLARIFIED 2026-06-17 (DJ): "Phase 5 creates an activity" is OUTDATED.** Phase 5 ALREADY creates a **project.task** "Re-engagement: {name}" (zapier_phase5 ~L592; "Follow-up" term retired 2026-04-30) when a NON-maintenance customer is invoiced (maintenance → new job instead). So there is **NOTHING to convert in Phase 5** — re-engagement is already a task. RE-ENGAGEMENT ≠ REACTIVATION: re-engagement = Phase 5 task + the followup text (uses OUR online booking link `_booking_link`=wscare.pro+token, NOT Calendly); reactivation = the separate Calendly program. The re-engagement SMS (`_build_followup_sms`, reactivation.py) DOES include the online booking link. The "convert Phase 5" worry was a naming/terminology confusion, NOT a real code gap.
- **STILL a mail.activity (left intentionally): the "Add tech + line items" booking reminder** (a SEPARATE post-booking "finish Workiz setup" reminder, NOT the re-engagement reminder). ⚠ COUPLED: created by `reactivation.py` (~L1144, activity_type 15 on the crm.lead) + zapier (phase3, calendly) AND **auto-closed by Phase 4** (`zapier_phase4` ~L2747/2803: searches `mail.activity` summary like 'Add tech + line items' → unlink on schedule). Converting it to a project.task requires a COORDINATED change to ALL creators + Phase 4's auto-close, or it orphans. Per spec ("don't big-bang, touches live text automation") + near-zero practical value (it's auto-managed + already shows in My Day), LEFT AS-IS. The DJ "Phase 5 creates a My Day not activity" flag = this reminder; it's the one optional purity cleanup remaining (do as a coordinated, verified pass if ever wanted).
- To FULLY delete the Activities screen (route + file): only after that reminder is converted (so nothing creates/needs mail.activity).

Step 4 = consolidate mail.activity reactivation/followup reminders into project.task Follow-ups (the deep "streamline old code"; touches the automation that creates them — reengage.py, phase5, reactivation). Incremental, one creator at a time, verifying the SMS-send path each time — do NOT big-bang. Full plan in the spec. Pillar's UI is solid; this is the data-model cleanup. A full comprehensive-CRM module spec (the other pillars) is still to write later. Pending: write the canonical Activity-Management spec; later a full comprehensive-CRM module spec. See [[project_system_roadmap]] (fold CRM in as the overarching frame).

**✅ STEP 4 CONFIRMED DONE (2026-07-06, live Odoo query).** Open `mail.activity` total = **6**, and ZERO are re-engagement/reactivation follow-ups: 4 = the intentionally-left "Add tech + line items" booking reminders on crm.lead (auto-managed by Phase 4), 2 = HR reminders on hr.employee (probationary / 90-day review — separate legit use). All outreach reminders are `project.task`. Nothing left to convert for the CRM consolidation. (The Activities screen route can be fully retired only if/when the "Add tech + line items" reminder is ever moved off mail.activity — optional purity, near-zero value, left as-is.)

**NEXT PILLAR DJ NAMED (2026-07-06): the per-customer VISUAL outreach timeline** — "one area per customer that shows when + what I did to reach out (a paper trail), AND when my next reach should happen, always looking ahead." DJ calls this "the start of a visual CRM." Building blocks ALL exist, just not assembled into one look-ahead+history view: `res.partner.x_last_communication` (last reach date, any channel — [[project_last_communication_rollup_field]]), customer chatter "📨 Text sent" posts (the paper-trail entries — written by /api/followup/launch), the open "Re-engagement:" `project.task` due date (= next scheduled reach), reactivation `crm.lead`, `x_studio_next_job_date` (next job). Customer brain (field.html `openCustJobRow`) already shows an "☀️ Action Items" section (forward tasks) but NOT a chronological outreach LOG with next-reach on top. The gap = a "Communications / Outreach timeline" panel on the customer card = past sends (from chatter + send-date fields) + the next reach date. Design/confirm scope with DJ before building. See [[project_reeng_reactivation_closed_loop]].
