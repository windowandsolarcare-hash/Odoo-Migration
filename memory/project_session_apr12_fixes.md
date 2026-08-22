---
name: April 12 session — task/SO fixes and Phase 4 improvements
description: Summary of fixes made April 12: orphaned tasks restored, SO smart button, staggered task times, Sunday tag
type: project
originSessionId: b189e64a-a6d4-46d1-a70f-a6b34dca7361
---
## Orphaned Tasks — Root Cause & Fix (April 12)

133 tasks had lost partner_id and sale_line_id (write_date = 2026-04-11 00:27, same second). Root cause not definitively identified — likely Phase 4 or sync_action_955 edge case.

**Fixed:**
- 131 tasks restored with `sale_line_id` (order line), `sale_order_id` (SO), and `partner_id` (property record with street address)
- Task partner_id must be the PROPERTY record (child partner with street), NOT the contact (parent). SOs are tied to property records.
- `sale_order_id` (not `sale_line_id`) is what drives the SO smart button (`display_sale_order_button`)
- Writing `sale_order_id` clears `partner_id` — must write partner_id AFTER sale_order_id

**Phase 4 backfill fix:** Now sets `sale_order_id` in create_vals alongside `sale_line_id`.

## Task Timer Overlap — Staggered Start/End Times

Multi-task SOs (2+ tasks for same job) previously had all tasks at the same start/end time, causing "scheduling conflict" warnings in Odoo.

**Fix:** Phase 4 now staggers time slots sequentially:
- Task 0: job_start → job_start + per_task_hrs
- Task 1: job_start + per_task_hrs → job_start + 2*per_task_hrs
- etc.

Both the update path (bulk → individual writes) and backfill create path (enumerate loop) now stagger.

**Manually fixed 10 SOs** (003902, 003754, 003935, 003917, 003956, 003913, 003947, 003907, 004277, 004425).

**Why:** DJ noticed overlap warning when clicking a task — it said another task was at the same time.

**How to apply:** If future tasks show overlap warnings for same-SO tasks, check whether stagger is working. Task sort order = sorted(task_ids) by id.

## Sunday Tag — Graveyard Job Identifier

Created `crm.tag` id=17 "Sunday" and applied to all 508 open SOs where date_order (converted to Pacific time) falls on a Sunday.

**Why:** Sunday SOs should not be invoiced — they are graveyard jobs. The tag lets DJ quickly identify them when reviewing the reactivation filter.

**How to apply:** When checking SO invoicing status, Sunday tag = graveyard = skip invoice.

## Phase 4 Changes Pushed (April 12)

Three commits to `zapier_phase4_FLATTENED_FINAL.py` on main:
1. `add sale_order_id to backfill task create_vals for SO smart button`
2. `split allocated_hours equally across all tasks for same SO`
3. `stagger task start/end times for multi-task SOs (no overlap)`

## Calendly — Cathedral City Service Event Type

Created via MCP (April 12):
- URI: `https://api.calendly.com/event_types/b7ca8953-c2ba-468d-b30e-8e7c46be7243`
- URL: `calendly.com/wasc/cathedral-city-service`
- Days: Wednesday + Thursday, 8:30 AM – 4:30 PM Pacific, 90 min
- Custom questions (Service Address, Type of Service, Additional Notes) need to be added MANUALLY in Calendly UI — API cannot set them.

## app.py — Timer Tools Added (April 12)

Added `start_task_timer` and `stop_task_timer` to Render voice assistant app.
- Both are WRITE_TOOLS (require confirmation)
- Accept task_id or task_name (ilike search, returns error if multiple match)
- Call `project.task` `action_timer_start` / `action_timer_stop`
- Pushed to GitHub main
