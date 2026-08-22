---
name: project_maint_stacked_message
description: "Maintenance heads-up (future jobs) rebuilt to DJ's OLD stacked format (When/Service/Where/Tech) + a 'confirm it works' CTA — dropped the run-on 'you're all good, nothing you need to do'. Text = reminders.py MAINT_TEMPLATE + _maint_row; branded /appt page = calfeed.py (2-col facts, one screen). Live+verified 2026-08-07."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-08T01:14:18.713Z
---

**DJ 2026-08-07:** showed his old Workiz maint text — facts STACKED (When/Service/Where/Tech), scannable — vs ours (run-on "your next service is set for X — you're all good, nothing you need to do"). Wanted: (a) his stacked format, (b) drop "nothing you need to do" → make them VERIFY (do something), (c) same on the branded page, (d) branded page must fit ONE screen (2-col if needed, no scroll). Approved the wording.

## Built (both live + verified)
- **`reminders.py` `MAINT_TEMPLATE`** → stacked:
  ```
  Hi {first}, it's Dan with Window & Solar Care. Here's your next service coming up:

  When: {when}
  Service: {service}
  Where: {where}
  Tech: Dan

  Please tap to confirm it works for you — or pick a different day: {link}
  ```
  NO sign-off in the template — the auto-signature (`sms.py _send_sms`, [[project_wsc_signature_on_every_text]]) appends "Dan Saunders / Window & Solar Care / 855-245-2273".
- **`reminders.py` `_maint_row`** now computes the stacked fields: `_when_str = day + ' at ' + _clock(when)`, `_service = SO job_type`, `_where = prop street+city` (extra `res.partner.read` by pid). Link = `calfeed.appt_link(so_id)` = `wscare.pro/appt/<token>`.
- **`calfeed.py` `/appt` page** (`_APPT_PAGE`): facts = compact **2-col label/value grid** (`.facts`, When/Service/Where/Tech); lead → "Please take a look and **confirm it works for you** — or pick a different day below" (dropped "nothing you need to do"); buttons tightened (14px). KEPT the good options: 📅 Add to my calendar (ICS) · ✓ I'll be there (confirm) · 📅 pick a different day (reschedule, loads route-tight open days) · Can't make it (cancel).

Verified: Brenda SO 17456 body stacked; /appt/17456-… renders the 2-col facts + confirm wording; "nothing you need to do" gone. Both reminders.py + calfeed.py touched (shared/collision-prone — fetched live first). See [[project_auto_confirm_branded_page]] [[project_request_confirm_flow]].
