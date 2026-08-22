---
name: session_may28_summary
description: "2026-05-28 session — task sync disabled, Phase 5 reminder activities, Follow-up type, ql_panel calculator, note sharing"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## 2026-05-28 Session Summary

### Task sync disabled (Phase 3 + Phase 4)
All task creation/sync/removal logic commented out in both scripts. Kept:
- `update_existing_sales_order()` — all data sync intact
- `confirm_sales_order()` — SO confirmation still fires on scheduling triggers
- `is_task_trigger_status()` — gate for SO confirmation, still needed
- `sync_tasks_from_so_and_job()` function body still in files as dead code (never called)

**Why:** Tasks are obsolete — field assistant gate is `state in ['sale','done']` on SO, not tasks.

### Phase 5 → Activity reminder flow (NEW)
When Phase 5 creates a Submitted Workiz job, Phase 3 now creates a `mail.activity` on the new draft SO:
- **Type:** "Follow-up" (`activity_type_id: 15`) — NEW type created 2026-05-28
- **Summary:** `"Add tech + line items — [Customer] · [City] · [Date]"`
- **Note format:** `WORKIZ_UUID:{uuid}\n{JobNotes text with line items}`
- **Deadline:** job date (or today + 14 days if unscheduled)
- **User:** ODOO_USER_ID (2)
- **res_model_id:** 670 (sale.order), **res_id:** SO id

**Auto-close:** Phase 4 searches for and unlinks these activities when confirming the SO (scheduling trigger). Search: `res_model='sale.order', res_id=so_id, summary like 'Add tech + line items'`.

### Activities page special rendering (activities.html)
`isP5Reminder(t)` checks `t.summary.startsWith('Add tech + line items')`.
`buildP5Card(t)` renders item list + "📋 Copy Items & Open in Workiz → Items" button.
`p5CopyAndOpen(btn)` — same logic as submitted_jobs.html: copies items to clipboard (LIFO), opens Workiz items tab.
`p5ParseItems(text)` — skips WORKIZ_UUID/AUTO-SCHEDULED/Previous Job/LINE ITEMS lines, parses "Name: $price".
`p5ExtractUuid(text)` — regex `WORKIZ_UUID:(\S+)`.

### Odoo system constant
`mail.activity.type` "Follow-up" = ID **15** (created 2026-05-28 via API).

### Earlier in session (from context summary)
- ql_panel.js: offline calculator added (🔢 button, full modal, z-index 9300)
- notes.html: 📤 share button — fetches note text via Drive export, uses Web Share API / clipboard fallback
- dashboard.py: fixed `requests` import (was missing from top-level), fixed `paid_count` in pre-deposit endpoint
- index.html: fixed help overlay z-index (200→1100), moved *i* button to `top:8px right:44px`
- WW6KDG (José Merelies) — orphan Submitted job, confirmed no Odoo SO (pre-Phase 4 update). Goes forward correctly now.
