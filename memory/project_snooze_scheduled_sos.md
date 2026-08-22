---
name: project_snooze_scheduled_sos
description: Customer snooze (x_snooze_until) now cuts across the Command Center / overdue / maintenance scheduling reports — filtered at the shared api_scheduled_sos endpoint
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

DJ snoozed customers in outreach/waiting screens but they still showed in the **Command Center schedule** (schedule_hub.html → "🗓️ Schedule — Command Center", the overdue/needs-scheduling reschedule list). Snooze was not cutting across scheduling reports.

**Where snooze lives:** `res.partner.x_snooze_until` (a date). Written by `api_outreach_park` (outreach.py, action='snooze') on the **parent customer** (it resolves property→parent first). Auto-resurfaces when the date passes. Outreach lists already honored it; scheduling reports did not. (~40 customers carry a future snooze as of 2026-07-10.)

**The shared endpoint:** `GET /owner/api/scheduled_sos?overdue=1` (dashboard.py `api_scheduled_sos`) feeds THREE consumers — schedule_hub Command Center, the index.html cockpit overdue count, and maintenance.html. Fixing it once = cross-cutting.

**Fix (2026-07-10, commit 73a64d2):** added `x_snooze_until` to `_CFIELDS`, added a `_snoozed(so)` helper (checks `_cust(so)` — the same parent-or-self record `_dnc`/`_last_contacted` use — for a future date), and `continue` past snoozed jobs in the build loop. Excluded server-side so the count drops too (snoozed shouldn't inflate the overdue count). Same treatment as the existing DNC / recent-contact suppression.

**How to apply:** any NEW "needs scheduling / overdue / worklist" surface must also filter `x_snooze_until > today` (parent-or-self record). Snooze is a global "not pursuing this customer right now" signal — it belongs in every scheduling/outreach report, not just outreach lists. See [[project_waiting_screen]] [[project_cc_skipped_excludes_submitted]] [[project_open_items_2026-07]].
