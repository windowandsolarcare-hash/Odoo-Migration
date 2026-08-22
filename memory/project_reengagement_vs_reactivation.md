---
name: project_reengagement_vs_reactivation
description: "RE-ENGAGEMENT (Phase 5 On-Request/Unknown follow-up cycle) vs REACTIVATION (1yr+ dormant campaign) — two DIFFERENT flows, both in reactivation.py. Never conflate the terms."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**These are TWO DIFFERENT flows. Do not conflate them (Claude has repeatedly).** Verified from code 2026-06-22.

## RE-ENGAGEMENT — the Phase-5 On-Request/Unknown follow-up cycle
The normal "your On-Request/Unknown customer's cycle came due, contact them" flow.
- **Phase 5 (`zapier_phase5`) fork:** reads type_of_service (Workiz `type_of_service_2`, fallback Odoo property `x_studio_x_type_of_service`/`x_studio_x_frequency`).
  - `maintenance` → PATH 5A `schedule_next_maintenance_job`: creates next job IN WORKIZ (job/create, no tech/time/status set, date hidden), Phase 3 then clones it → Submitted-status DRAFT SO. = the **schedulable** job (finish it in Workiz: add line items, flip toggle to reveal date, set status to send).
  - `on request`/`unknown`/blank/`on demand` → PATH 5B `create_ondemand_followup`: **NO Workiz job**; creates Odoo **`project.task`** titled **"Re-engagement: {customer} — {service}"**, due = now + frequency days (default **180/6mo**, Sunday-adjusted), partner_id=contact.
- **The send button on that To-Do = "Launch Re-engagement Text"** → backend **`POST /api/followup/launch`** (lives in `reactivation.py` L731 despite filename). It: finds contact's latest Workiz UUID → clones it → creates new Workiz job **JobType=`Re-engagement Lead`** (unscheduled), SMS in `information_to_remember` → sets **SubStatus=`Re-engagement Trigger`** (parent Status=Pending) → **Workiz automation fires the SMS**. Cooldown **45 days** (`FOLLOWUP_COOLDOWN_DAYS`). Skips STOP/Do Not Contact. Marks To-Do done, posts "Text sent" on contact.
- Endpoints (all in reactivation.py): `followup/preview` L607, `followup/launch` L731, `followup/markdone` L907. Constants L536-541.
- **Auto-pilot** = `reengage.py` → `/owner/reengage`: daily 8AM scans open "Re-engagement:" project.tasks past gates, pushes DJ a digest, batch-send — reuses preview→launch→markdone. Params `reengage.due`/`reengage.log`.

## REACTIVATION — the 1yr+ dormant campaign (SEPARATE; DJ: leave it alone for now)
Customers not heard from in **over a year**, run as a campaign.
- SA 563 (LAUNCH) / `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` / reactivation.py campaign routes → creates Workiz job **JobType=`Reactivation Lead`** + SubStatus trigger → reactivation SMS. 365-day cooldown. Different animal. OUT OF SCOPE for the Needs-Scheduling work.

## KEY DISTINCTION TABLE
| | Re-engagement | Reactivation |
|--|--|--|
| Trigger | Phase 5 cycle due (On-Req/Unknown) | 1yr+ dormant, manual campaign |
| Odoo object | project.task "Re-engagement:" | crm.lead opportunity |
| Workiz JobType | `Re-engagement Lead` | `Reactivation Lead` |
| Workiz SubStatus | `Re-engagement Trigger` | (reactivation trigger) |
| Cooldown | 45 days | 365 days |
| Button | "Launch Re-engagement Text" | "Launch Reactivation" |

## BUG — FIXED 2026-06-23 (was the whole re-engagement↔reactivation tangle)
The Activities-screen detail button for a "Re-engagement:" `project.task` was **wired to the REACTIVATION campaign**, not the re-engagement send → errored "no sales order" every time (DJ hit it on Rita Johnson). Root cause in `static/owner/activities.html`: `isFollowupTodo(t)` returns false for `source==='task'` → the WORKING "Open Follow-Up Editor →" button (`dt-btn-followup` → `detailOpenFollowup()` → `/api/followup/launch`) was HIDDEN for these tasks; only `isReengagementTask(t)` was true → the BROKEN `dt-btn-reactivate` "Launch Reactivation" button showed (→ `launchReactivation()` → `/api/reengagement/launch_so` → finds SO → SA 563 reactivation campaign). So for all 121 tasks the only visible button was the broken reactivation one.
**FIX (3 parts):**
1. `activities.html` L741: button relabeled "Launch Reactivation"→**"Launch Re-engagement Text"** and onclick `launchReactivation()`→**`detailOpenFollowup()`** (the proven working path; same engine reengage.py uses). `/api/todos` already returns partner_id for project.task (activities.py L90/102) so the follow-up flow has what it needs. Predicates are mutually exclusive → no duplicate button. (Dead `launchReactivation`/`launchReengCampaign`/`runReengAction` left in file, not removed.) Commit d4756f8.
2. **121 existing project.task descriptions** bulk-fixed in Odoo: "Launch Reactivation"→"Launch Re-engagement Text", "reactivation SMS"→"re-engagement SMS" (0 remaining).
3. `zapier_phase5` L588 description wording fixed so NEW tasks are correct. Commit afe75c0 (Odoo-Migration).

## My Day shows the SAME re-engagement tasks as Activities (DJ confused 2026-06-24)
The Activities screen (`/owner/activities`) and **My Day** (`/owner/myday`) are TWO UI views over the SAME Odoo `project.task` records — a "Re-engagement: …" task appears in both. Each screen has its own "Launch re-engagement text" button, but they GATE it differently:
- **Activities** gates on the **name**: `isReengagementTask = source==='task' && summary.startsWith('Re-engagement:')`. Button = `detailOpenFollowup()` (detail modal).
- **My Day** gated on the **type field**: `canLaunch = it.kind==='followup' && it.partner_id`, where `kind = project.task.x_myday_type` (default `'task'`). My Day's `tkLaunchPrep`/`tkLaunchSend` call the SAME `/api/followup/preview` + `/api/followup/launch` endpoints (nicer inline edit→send→auto-done).
**BUG (fixed 2026-06-24):** my batch of 44 recovery re-engagement tasks were created WITHOUT `x_myday_type` → `kind='task'` → My Day hid the button (150/196 had `followup` and worked; 46 were empty). Two fixes: (1) data — set `x_myday_type='followup'` on the 46; (2) `myday.html` L794 gate broadened to `(it.kind==='followup' || (it.title||'').startsWith('Re-engagement:')) && it.partner_id` (commit 618ed6b) so an untyped Re-engagement task still shows the button. **RULE: any new "Re-engagement:" project.task MUST set `x_myday_type='followup'`** (Phase 5 path 5B should; ad-hoc batches must too). Also added no-store to `/myday` + `/activities` routes (see [[project_owner_page_nostore_stale]]).

## Needs-Scheduling 2-pill design (DJ 2026-06-22)
- **📅 Schedule pill** = Maintenance Submitted draft SOs (`/api/scheduled_sos`) → action: open in Workiz (SO `x_studio_x_studio_workiz_uuid`).
- **☎️ Contact pill** = RE-ENGAGEMENT "Re-engagement:" project.tasks (NOT Submitted SOs) → action: Launch Re-engagement Text (followup/launch). Reactivation NOT involved.
- Both SMS paths currently depend on Workiz automation (Workiz leaving ~2026-06-29) — post-Workiz the "send text" must move to Twilio (see [[project_twilio_port_from_workiz]], [[project_twilio_a2p_and_entity]]). Relates to [[project_report_hub_redesign]], [[project_type_of_service_fields_map]].
