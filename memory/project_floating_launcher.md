---
name: project_floating_launcher
description: "The floating app-launcher shortcut (ql_panel.js) — what it is, its app list, and how to add it to a page"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
---

**Floating shortcut = `static/owner/ql_panel.js`** (the "Quick Launch Panel"). A self-injecting IIFE: a draggable round button (`#ql-toggle`, bottom-right, position saved, glyph **🚀** — changed from "+" 2026-07-07 because DJ kept confusing it with the My Day add-task **+** FAB; the launcher isn't "add" so it must never be a plus) that opens a panel of links to other owner apps so DJ can jump app→app without going back to the hub. Also injects a Commands tab into the voice modal + a built-in calculator. Add it to any page with one line before `</body>`: `<script src="/static/owner/ql_panel.js"></script>`.

**2026-06-30 redesign (DJ: "icons are not easy to remember"):** the panel was an icon-only grid → rebuilt as a LABELED vertical menu (`.ql-row` = `.ql-ic` icon + `.ql-lbl` name; sections `.ql-sec` "Shortcuts"/"Apps"; `max-height:72vh;overflow-y:auto`). Shortcut buttons KEEP their IDs (`ql-cust-btn`/`ql-mic-btn`/`ql-help-btn`/`ql-calc-btn`) — handlers bind by ID, so never rename them. `positionPanel()` reads offsetWidth/Height and clamps to viewport, so a taller menu just works.

Current app list (DJ's "current needs"): Command Center, My Day, Field Assistant, Vault, Quote, Maintenance, New Order, Activities, Reactivation, Analytics, Time Clock, Home + shortcuts Customer/Microphone/Voice Commands/Calculator. Dropped older Calendar/Stale SOs/Shift Review/Submitted Jobs/Hemet. To change the lineup, edit the `wrap.innerHTML` `#ql-panel` block.

**Coverage:** added to all important screens 2026-06-30 — was already on activities/calendar/field/hemet/index/planner/quote/reactivation/shift_review/stale_sos/submitted_jobs/timeclock; ADDED to schedule_hub(Command Center)/vault/myday/new_order/new_job/maintenance/analytics/hiring/hr/booking_requests/reengage/reeng_review/pre_deposit/quick/inbox/weekly_reports. Intentionally skipped: index_classic, reports_demo, jd_window_cleaning_assistant, deleted_jobs, notes+reference (redirect to vault). DJ: "if I needed it on a screen you skipped, I'll tell you." See [[project_command_center]].
