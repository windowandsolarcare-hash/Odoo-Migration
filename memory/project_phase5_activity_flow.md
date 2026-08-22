---
name: project_phase5_activity_flow
description: Phase 5 reminder activity flow — how Submitted jobs become Follow-up activities with Copy+Open Workiz button
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Phase 5 Reminder Activity Flow

**Why:** Phase 5 creates Workiz jobs (Submitted status, no tech, no items) for future maintenance. DJ needs to be reminded to go add tech + line items in Workiz so the job gets confirmed and appears on the field assistant.

**Full loop:**
1. Phase 5 creates Workiz job → Phase 4 polls it → calls Phase 3
2. Phase 3 creates draft SO (skip_confirm=True for Submitted status)
3. Phase 3 calls `_create_submitted_job_activity(so_id, workiz_job)` (at end of paths A/B/C when `skip_confirm=True AND status == 'Submitted'`)
4. Activity appears in Render app Activities page under **Follow-up** filter pill
5. DJ taps "📋 Copy Items & Open in Workiz → Items" → clipboard loaded → Workiz items tab opens
6. DJ adds items + tech in Workiz, changes SubStatus to Scheduled
7. Phase 4 confirms SO → activity **auto-deleted** → job appears on field assistant

**Activity fields:**
- `res_model_id`: 670 (sale.order)
- `activity_type_id`: 15 (Follow-up — created 2026-05-28)
- `summary`: `"Add tech + line items — [Customer] · [City] · [Date]"`
- `note`: `"WORKIZ_UUID:{uuid}\n{JobNotes text}"` — plain text, Odoo wraps in HTML but `_strip_activity_html` restores newlines
- `date_deadline`: job date YYYY-MM-DD, or today+14 if unscheduled

**Note parsing in Activities page:**
- UUID extracted: `text.match(/WORKIZ_UUID:(\S+)/)`
- Items parsed: `p5ParseItems()` — skips lines starting with WORKIZ_UUID/AUTO-SCHEDULED/Previous Job/LINE ITEMS
- Button opens: `https://app.workiz.com/root/job/{uuid}/items`

**Auto-close in Phase 4:** After `confirm_sales_order()`, searches `mail.activity` where `res_model='sale.order' AND res_id=so_id AND summary like 'Add tech + line items'`, then unlinks all matches. Non-fatal (wrapped in try/except).

**How to apply:** READ when editing Phase 3 activity creation, Phase 4 confirm flow, or activities.html rendering.
