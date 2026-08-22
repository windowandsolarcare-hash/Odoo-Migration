---
name: Phase 3/4/5 Flowcharts (2026-04-24)
description: SVG + PNG flowcharts for Workiz→Zapier→Odoo automation phases with narrative markdown explaining routing logic and date field handling
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## Location
`3_Documentation/phase_diagrams/` in GitHub repo windowandsolarcare-hash/Odoo-Migration

Files per phase: `.md` (narrative), `.mmd` (Mermaid source), `.svg` (infinite-scale rendering), `.png` (3200px wide, mobile-readable)

**Why:** Diagrams make automation flow visible to non-technical stakeholders. SVG + PNG covers desktop (zoom) + mobile (readable at 3200px).

## Phase 3 - New Job Creation
**Trigger:** Workiz webhook sends new job (Status=Submitted)
**Path:** Workiz → Zapier HTTP request → Odoo sale.order + tasks

### Flow Routing
1. New job received with Workiz UUID
2. **Path A (New Customer):** Workiz ClientId not found in Odoo → create new res.partner + SO
3. **Path B (Existing Customer, New Property):** ClientId exists, property (partner_shipping_id) not found → reuse contact, create new property partner
4. **Path C (Existing Customer, Existing Property):** Both exist → reuse both

### Key Date Handling
- `date_order` on SO = Workiz `JobDateTime` (start time, UTC) — **never end time**
- `x_studio_next_job_date` on contact = copy of date_order for reactivation tracking
- Task created with deadline = date_order + 3 hours buffer (scheduling)

### Fields Created on SO
- `x_studio_x_studio_workiz_uuid` = job UUID (lookup key)
- `x_studio_x_workiz_link` = link to Workiz job
- `x_studio_x_studio_workiz_status` = "Submitted"
- `x_studio_x_studio_workiz_tech` = Workiz tech assignment
- `x_studio_x_gate_snapshot` = gate code at creation time
- `x_studio_x_studio_pricing_snapshot` = pricing at creation time

### Custom Fields Required for Validation
- `type_of_service_2` = Workiz custom field (NOT type_of_service) — required, default "On Request"
- `frequency` = required, default "Unknown"
- `confirmation_method` = required, default "Cell Phone"
- `JobSource` = required, always "Referral"

**Why:** If any of these are empty string, Workiz API rejects the record on Phase 5 (create new job for next visit).

## Phase 4 - Job Status Updates
**Trigger:** Zapier polling (every 5 minutes)
**Path:** Odoo query → Workiz API → update Odoo fields + tasks

### Polling Logic
1. Find all SO where `x_studio_x_studio_workiz_status` != "Done" (incomplete jobs)
2. For each SO, fetch Workiz job by UUID
3. Compare `SubStatus` in Workiz to current Odoo status
4. Update task stage and SO fields

### Task Lifecycle (Phase 4 + Phase 5)
- `New` (16) → `Planned` (17): Phase 4 first sync, stays until job scheduled in Workiz
- `Planned` (17) → `In Progress` (18): Field Assistant starts timer (Render app)
- `In Progress` → `Done` (19): Field Assistant stops timer + photos
- `Done` → (archive): Phase 4 skips; field manual only

**Deletion Rule:** Only delete tasks in New(16) or Planned(17) on Submitted status. Protect In Progress(18) and Done(19) — never auto-delete active/completed work.

### SubStatus Routing
- `Scheduled`, `STOP`, `Lead` → task stays Planned
- `Next Appointment X - Text` (after Calendly confirmation) → task stays Planned
- `In Progress` → task moves to In Progress (if Field Assistant hasn't started)
- `Done` → task moves to Done, SO status updated
- `Canceled` → task deleted if safe (New/Planned only)

### Critical Bug: Task Re-Entry
**Symptom:** Task deleted on Workiz substatus exit from Scheduled, NOT recreated on return
**Example:** Workiz cycle: Scheduled → Next Appointment - Text → back to Scheduled = task deleted, not recreated
**Impact:** SO shows tasks_count=1 but no task exists; Field Assistant shows no timer
**Status:** Bug found + diagnosed (Phase 4 logic, task cache expires). Permanent fix not yet built.
**Workaround:** Manual task creation in Odoo (task 297 on SO 15916).

### next_job_date Clearing
- Phase 4 clears `x_studio_next_job_date` on property partner when SO status = "Done"
- If future job exists, it should be re-written by Phase 5 (see below)
- If no future job, date stays null until reactivation triggers

**Why:** Reactivation screen uses next_job_date to plan outreach. Stale dates block campaigns.

## Phase 5 - Auto Job Scheduling
**Trigger:** Phase 6 webhook payload (payment recorded) or manual Phase 5 run
**Path:** Completed SO → Workiz API (create new job for next visit)

### Load-Bearing Path
1. Query completed SO (workiz_status="Done", frequency != "One Time")
2. Calculate next visit date: last_completed_date + frequency interval
3. Fetch last_date_cleaned from current job (Workiz field)
4. **Create new job** in Workiz for next visit with:
   - JobDateTime = calculated next visit date (start of business day)
   - last_date_cleaned = copy from completed job (preserve history)
   - All other fields (type_of_service_2, frequency, pricing, etc.) = copy from completed SO snapshot fields

### Field Mapping (Completed SO → New Workiz Job)
- Service type: `x_studio_x_type_of_service` (from property partner)
- Frequency: `x_studio_x_frequency` (from property partner)
- Type of service: `x_studio_x_studio_x_studio_job_type` (from SO snapshot)
- Gate code: `x_studio_x_gate_code` (from property partner, NOT snapshot)
- Pricing: `x_studio_x_pricing` (from property partner, NOT snapshot)
- Phone: contact phone (from res.partner, required)
- Address: contact address (required)

**Why:** Some fields should update dynamically (pricing, gate code) even if SO snapshot is stale. Others must preserve snapshot from original job date (initial pricing offered).

### New Job Validation
All Workiz API defaults must be applied:
```
type_of_service_2: str(value or 'On Request')
frequency: str(value or 'Unknown')
confirmation_method: str(value or 'Cell Phone')
JobSource: str(value or 'Referral')
ok_to_text: str(value or 'Yes')
```

If any is empty string, Workiz validation rejects the POST.

### next_job_date Write (Phase 5A)
After new job created in Workiz:
- Write `x_studio_next_job_date` on property partner = new job's JobDateTime
- Enables reactivation screen to show "Next scheduled: [date]" as visual confirmation

**Why:** Reactivation team uses this date to avoid scheduling duplicate jobs.

### last_date_cleaned Population (Phase 5B)
When creating new maintenance job:
- Populate `last_date_cleaned` from completed job
- Format: Workiz date field (YYYY-MM-DD or timestamp)
- Enables technician to track service history without jumping between jobs

### Orphaned Future Jobs
- **Rule:** Leave alone. Do NOT auto-delete.
- **Example:** SO 17066 (Wayne Geringer, Aug 20 2026) has a future job but Phase 4 task sync deleted the Odoo task and won't recreate it.
- **Workaround:** Manual task creation in Odoo; keep Workiz job intact for continuity.

## Graveyard Job Creation (Special Case)
When SO marked "Do Not Contact" (x_studio_activelead = "Do Not Contact"):
- **Always create new graveyard job** instead of reusing future job
- DO NOT update/overwrite existing future job
- Create separate crm.lead record with Workiz link for audit

**Why:** Graveyard = inactive but trackable; preserve original job in case status changes back.

## How to Apply

**Debugging a job flow issue:**
1. Find SO in Odoo → check `x_studio_x_studio_workiz_uuid` (Phase 3 key)
2. Fetch Workiz job by UUID → check JobDateTime + SubStatus (Phase 4/5 keys)
3. Check SO `date_order` matches Workiz JobDateTime (if mismatch, Phase 1 error)
4. Check task stage vs Workiz status (if wrong, Phase 4 sync issue)
5. Check `x_studio_next_job_date` populated (if blank, Phase 5 didn't complete)

**Adding custom logic:**
- Phase 3: add conditions before Path A/B/C routing
- Phase 4: add SubStatus handlers before task sync
- Phase 5: add field mappings before Workiz POST, but always apply validation defaults

## Files Generated
- `phase3_flow.md` — narrative explanation of new job creation, all paths
- `phase3_flow.mmd` — Mermaid source (Flowchart syntax with shapes)
- `phase3_flow.svg` — infinite-scale vector rendering
- `phase3_flow.png` — 3200px wide raster (mobile-readable)
- Same 4 files for Phase 4 and Phase 5

## Rendering Notes
- Mermaid `%%init%%` block sets fontSize to 14px (larger than default for readability)
- PNG rendered at `-w 3200` pixels wide (verified readable on phone with pinch-zoom)
- SVG supports browser pinch-zoom + pan (infinite scale)
- Phase 5A identified as critical load-bearing path (next_job_date writes) — verify on every new feature
