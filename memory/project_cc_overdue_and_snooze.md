---
name: project_cc_overdue_and_snooze
description: "Command Center \"Overdue — schedule now\" logic + new 🔕 Not ready snooze on the field job 3-dot menu"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Command Center "⚠️ Overdue — schedule now" logic** (schedule_hub.html `loadNeed` → `mapJob(j,true)`, backed by `GET /api/scheduled_sos?overdue=1`, dashboard.py `api_scheduled_sos`):
- `x_studio_x_studio_workiz_status = 'Submitted'` (Phase 3 next-jobs are DRAFT quotations, NOT on the schedule until confirmed) + `state != 'cancel'` + `company_id = 1`
- `date_order` (the target date) between **1 year ago and today-start** → already passed
- `job_type` NOT in [Reactivation Lead, Personal Time, Quote, Touch up] and not blank
- EXCLUDES snoozed (`x_snooze_until` future, via parent-preferring `_cust`) + test customers
- Frontend also drops DNC + recently-contacted (`_recentContact(last_contacted)`)
- `days_overdue` = today − target date; badge red >90d. "unscheduled" badge = never placed on the schedule. `$0` = no line items/price yet.
- Sibling buckets: "🔁 Skipped — reschedule" (`_isSkipped`, past confirmed job that didn't happen) and "📋 Upcoming next-jobs to place" (`/api/scheduled_sos` non-overdue).

**🔕 Not ready — snooze (2026-07-11):** field.html job 3-dot menu → `openSnoozeFromMenu` → overlay (Why/reason input + In 3 months / In 6 months / Next season, `_nextSeasonISO` = next Mar/Jun/Sep/Dec 1) → **`POST /api/outreach/defer` `{kind:'partner', partner_id, reason, months|date}`** → writes `res.partner.x_snooze_until` (+ logs reason to the customer timeline) and drops the customer off Overdue/Needs-scheduling. Reversible (just a date). Menu item shows for any real customer (`partner && customer !== 'Personal Time'`). Needs `partner_id` (menu has it; scheduled_sos returns it).

**★ ONE canonical snooze endpoint — do NOT duplicate:** DJ's rule (2026-07-11) — reuse `/api/outreach/defer` (reactivation.py), don't fork. I first built a separate `/api/schedule/snooze` in dashboard.py; DJ (rightly) said reuse the old one so there's one place to maintain — it was removed (commit 953c823), and defer is now the single source for the Waiting list AND the field/scheduling snooze.

**★ Snooze gotcha (why defer needed a fix):** the scheduling filter reads `x_snooze_until` from the **parent-preferring `_cust`** (SO `partner_id` is usually the PROPERTY child; the customer is the PARENT contact). `/api/outreach/defer kind:'partner'` originally wrote only the single partner_id → would NOT hide the overdue job. Fixed 2026-07-11 (commit 1ecfe60): defer's `kind:'partner'` branch now resolves `parent_id` and writes `x_snooze_until` on BOTH partner + parent. Any snooze/defer affecting a scheduling report MUST target the record `_cust` reads. See [[project_field_delete_odoo_only]] (2-partner Contact+Property model), [[project_waiting_screen]], [[feedback_never_remove_working_code]].
