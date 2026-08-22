---
name: Activities UI — unified detail-first flow with automation buttons inside
description: 2026-04-29 — Every activity opens the detail modal first (shows ALL fields). Specialized automations (follow-up SMS, future voice-activity types) surface as buttons INSIDE the detail modal, not as separate routing paths. This keeps a consistent "see everything, then choose what to do" pattern.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Every to-do/activity in `/owner/activities` opens the **detail modal first**, regardless of type. The detail modal shows every populated field of the `mail.activity` record — Summary, Type, Due, Linked-to record, res_model, res_id, Activity ID, full note (HTML stripped, anchors preserved as text + frontend linkified).

Specialized automations are buttons **inside** the detail modal, not separate routing destinations.

**Why:** Earlier design routed activities through different modals based on a card-level predicate (Calendly → detail, everything else → follow-up). DJ's complaint on 2026-04-29: a generic to-do (his preselect coverage reminder, activity #66) routed to the follow-up modal which hid the actual note text and presented the SMS-send UI that didn't apply. The fix DJ asked for: *"display everything for all activities so I have a full understanding of the activity. then a button for the automation."*

**How to apply:**

When adding a new specialized activity flow (e.g., voice-driven `scheduled_sms`, `reminder`, future automation types):

1. **Don't** add a new top-level routing branch in `loadOpen()`. The card always opens the detail modal.
2. **Do** add a button to the detail modal's `.fu-actions` area, hidden by default with `style="display:none"`.
3. In `openDetailModal()`, show that button only when the activity matches the trigger (e.g., `isFollowupTodo(t)`, `isScheduledSmsTodo(t)`, etc.).
4. The button's click handler should bridge into the specialized modal — synthesize the data attributes the specialized modal expects and call its `open*Modal()` function. Pattern:
   ```javascript
   function detailOpenFollowup() {
     if (!dtActivityId) return;
     const t = openTodosById[dtActivityId] || {};
     const stub = document.createElement('div');
     stub.dataset.actid = String(dtActivityId);
     stub.dataset.pid   = String(t.partner_id || '');
     stub.dataset.name  = String(t.record || t.summary || '');
     closeDetailModal();
     openFollowupModal(stub);
   }
   ```
5. Inside the specialized modal, the existing Send + Mark Done buttons keep working as before — no changes needed there.

**Predicate functions** (top of activities.html `<script>` block):
- `isCalendlyTodo(t)` — summary/type contains "calendly". Currently no extra button needed (note covers it).
- `isFollowupTodo(t)` — `partner_id` set AND summary/type contains "follow up", "follow-up", "followup", "reactivation", or "reach out". Surfaces the "Send Follow-Up SMS →" button.
- Add new predicates here for future activity types.

**Detail modal field list** (in `openDetailModal()`): Summary, Type, Due, Linked to (`record`), Model (`res_model`), Record ID (`res_id`), Activity ID, then the full note. Any populated field → row; missing → skipped. If a future activity type adds new fields to `/api/todos`, just add a `fieldRow(...)` line.

**Files:**
- `Saunders Render App/static/owner/activities.html` — UI + routing
- `Saunders Render App/routers/owner/dashboard.py` `/api/todos` — what fields the frontend sees

**Related memories:**
- `project_activities_module.md` — broader Activities module reference (READ FIRST when editing this area)
- `project_followup_flow.md` — follow-up SMS flow internals
- `session_apr28_29_summary.md` — earlier design decisions for voice-driven activity creation
