---
name: project_myday_action_catalog
description: "My Day task detail has a unified \"action zone\" driven by MYDAY_ACTIONS catalog — one-tap automations attach to tasks (system auto, or manual picker). How to add a new action."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e8d15b5-9a20-4187-90d6-6f63266f2498
---

**DJ's model (2026-07-04):** every My Day task detail looks identical; the only thing that changes is a button (or editor) near the bottom that DOES the thing. Tasks are reminders, and if the work is digital+repetitive it carries a one-tap button. Programmed tasks auto-attach their action; tasks DJ types get a picker to choose one. He will keep ADDING to the catalog as needs arise — adding one is meant to be trivial.

**Storage:** new field **`res project.task.x_myday_action`** (char, id 21350, model 856) = the attached action key. Carried through myday.py: added to both search_read field lists, serialized as `action` in the task dict, accepted in `/api/myday/add` + `/api/myday/update`, and copied in the recurring-spawn `nvals`.

**Frontend = `static/owner/myday.html`:**
- `#tkActionZone` div (replaced the old hardcoded `#tkLaunchWrap`/`#tk-reeng`/`#tkBookingWrap`) — the ONE consistent action spot, above the Today/Snooze row.
- `MYDAY_ACTIONS` = the catalog object. Each entry: `{label, manual:true|false, needs:['customer'], render(zone,it){…}}`. `manual:false` = system-only (not offered in the picker). Helpers: `_mdActBtn(label,color,onclick)`, `_mdNeedCust(msg)`, `_mdToast(msg)`.
- `systemActionKey(it)` infers programmed tasks for back-compat: booking (via `tkBookingTarget`) → `booking_approve`; followup/`Re-engagement:` + customer → `reengage`. Explicit `it.action` (manual attach) overrides inference.
- `renderActionZone(it)`: system task → render its action, no picker (`_tkActionEditable=false`, never persisted). Manual task → `<select id="tkActionPick">` of manual actions + rendered action (`_tkActionEditable=true` → `tkSaveEdit` sends `action:_tkAction`).

**Seed catalog (v1, all real+working):** `booking_approve` (nav to booking_requests, system), `reengage` (WSCReeng inline editor, system+manual, snoozes 60d on send), `reactivation` (→/owner/reactivation), `quote` (→/owner/new-order?contact=pid), `call` (→`GET /api/myday/partner_contact?partner_id=` → tel:; **res.partner has NO `mobile` field in this Odoo 19 SaaS, only `phone`**).

**TO ADD A NEW ACTION:** add one entry to `MYDAY_ACTIONS` with a `render(zone,it)` (usually `zone.appendChild(_mdActBtn(label,color,onClick))`); set `manual:true` to expose it in the picker; if it needs a scalar variable prompt for it in the onClick (DJ: "each button carries a picker for each variable it needs" — customer is the shared `it.partner_id`). NOT yet wired (DJ's future adds, need a target decision): review_request, send_invoice, payment_link. See [[project_reengagement_logic]] [[project_myday_reminders]] [[project_myday_task_done_is_state_not_stage]].
