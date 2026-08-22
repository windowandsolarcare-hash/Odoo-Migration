---
name: project_field_delete_return_origin
description: "Field app: after deleting a job, return to where the job was opened FROM (Customer Brain / Command Center), not the empty today schedule. The _returnToCust / _backToCC / apBack origin-navigation model."
metadata:
  node_type: memory
  type: project
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

**Fixed 2026-07-09 (field.html, commit 65df757d).** DJ deleted a job for "Kahn" and got dumped on the empty today schedule (nothing scheduled today → looked like a dead end); the Android back button took him to the correct place. He wanted delete to go there DIRECTLY.

**Root cause:** `deleteJobFromMenu` success path always did `closeActive(); loadField();` — loadField() reloads the TODAY field schedule regardless of where the job was opened from.

**The origin-navigation model in field.html (reuse this for any "return after action"):**
- `window._returnToCust = {pid, name}` is set by `openCustJob` (~L5808/5823) when a job is opened from the Customer Brain.
- `window._backToCC = true` is set when opened from the Command Center (`?from=cc`).
- `apBack()` (~L3166) is the panel back-arrow: `_returnToCust` → closeActive + openCustomersTab + preloadCustomer(name,pid,true); `_backToCC` → history.back(); else closeActive (reveal schedule).
- `_custJobsCache[pid]` (module-level, L1528) caches a customer's job list — `delete _custJobsCache[pid]` busts it so a re-open re-fetches (pattern also at L5861).

**Fix:** added `_returnToOrigin() (was _returnAfterDelete, renamed 2026-07-09)` (mirrors apBack but busts the cust job cache so the deleted job vanishes, and keeps `loadField()` as the schedule fallback). Both delete branches (Workiz+Odoo delete AND the SO-only/Personal-Time cancel branch) now call `_returnToOrigin() (was _returnAfterDelete, renamed 2026-07-09)` instead of `closeActive();loadField();`.

**2026-07-09 extended to Record Payment:** same bug — after `doPayment()` and the Stripe-paid poll, the code did `loadField(); closeActive();` → dumped DJ on the field schedule instead of back to his origin (Command Center / Customer Brain). Renamed the helper `_returnAfterDelete`→`_returnToOrigin` (action-agnostic) and wired doPayment + the Stripe-payment poll to it. So payment now returns to origin too.

**Rule:** any destructive/end-action in field.html that currently falls back to `loadField()` should instead honor the origin model — the today schedule is frequently empty and reads as a dead end. See [[project_navigate_next_address]] [[project_command_center_offline]].
