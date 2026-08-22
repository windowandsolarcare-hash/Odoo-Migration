---
name: project_push_notification_actions
description: Web-push notifications have Done/Snooze action buttons; booking requests push immediately + High priority
metadata: 
  node_type: memory
  type: project
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
---

**My Day / booking web-push notifications have ACTION BUTTONS (2026-07-01).** Architecture:
- **Push payload** built in `myday.py` (`_broadcast(subs, payload)`), sent to all saved subs. To add buttons, include `'actions':[{action,title}]` + `'data':{task_id,url}`. The SW push handler (`auth.py` `_SW_JS`) already passes `d.actions`/`d.data` through to `showNotification`.
- **SW `notificationclick`** (auth.py `_SW_JS`) dispatches by `e.action`:
  - `myday-done` → POST `/owner/api/myday/done` `{id:task_id, source:'task'}`
  - `myday-snooze` → POST `/owner/api/myday/snooze` `{id:task_id, source:'task', days:1}` (pushes a DAY out; endpoint is day-granular — no sub-day snooze yet)
  - `reengage-send`/`reengage-skip` → `/api/reengage/act` (pre-existing)
  - `booking-review` (+ any unhandled action, and body-tap) → opens `data.url`
  Endpoints `/api/myday/done` (id,source) and `/api/myday/snooze` (id,source,days) already existed.
- **Due-time reminder push** (`myday.py myday_notify_tick`, the per-task ping) now carries `data.task_id` + Done/Snooze actions.

**Booking requests notify IMMEDIATELY + High priority (booking.py, the wscare.pro submit path ~L588).** The alert `project.task` now sets `x_myday_type='task'` + `x_myday_priority=3` (High), and after create sends an IMMEDIATE web push (lazy `from routers.owner.myday import _broadcast,_get_subs`) → title "🆕 New booking request", opens `/owner/booking_requests?focus=<so_id>`, actions [Review, Snooze]. Previously it only created the task and waited for the 5-min tick. NOTE: SW-change (auth.py `_SW_JS`) needs one full app close to swap the worker; action buttons only appear on NEW notifications after that. See [[project_calendly_booking_alert]] [[project_command_center_offline]].
