---
name: project_appt_confirmation_odoo
description: "Odoo-native appointment CONFIRMATION text (built 2026-08-03) — replaces the Workiz 'change status → text' hand-off after scheduling. scheduler.py /api/schedule/confirm_preview + /send_confirm (preview-gated, messaging.send). field.html apptConfirm()."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T04:18:30.118Z
---

**After scheduling/rescheduling, the customer confirmation text is now Odoo-native — no Workiz.** (Workiz retires Mon 2026-08-03; the old flow popped Workiz open so DJ could flip the job status and let Workiz text the customer — that would break Monday.)

## Backend (scheduler.py, lead lane)
- `POST /api/schedule/confirm_preview {so_id}` → `{ok, first, name, phone, partner_id, when, day_key, message}`. Composes `"Hi <first>, you're scheduled for <PT date/time>. See you then! – Dan"`. **Phone/name come off the CONTACT (parent of the property)** — phone lives on the Contact, not the Property/SO ([[project_respartner_no_mobile_field]]). Errors if no phone.
- `POST /api/schedule/send_confirm {so_id, message, force_now?}` → `messaging.send(phone, message, partner_id, so_id, kind='appt_confirm', idem='appt_confirm:<so>:<YYYY-MM-DD>')`. STOP/DNC + quiet-hours HOLD all enforced by messaging.send ([[project_quiet_hours_hold_queue]]); returns `{ok, held, reason}` (held=queued for 8am). Preview-gated: preview first, DJ approves/edits, then send.
- Helper `_confirm_ctx(so_id)` resolves contact+phone+PT label.

## The RESCHEDULE ACTION itself is now Odoo-native too (2026-08-03)
Two separate Workiz dependencies were in this flow — fixing the confirmation alone didn't cut Workiz. `POST /api/schedule/reschedule` (scheduler.py) USED TO, for any job with a Workiz UUID (all migrated jobs), call `workiz_post('job/update/{uuid}/', ...)` to move the WORKIZ job + rely on Phase-4 sync back (returned `workiz:True`+`workiz_link` → frontend popped Workiz). DJ: "this reschedule button still goes through workiz." REWRITTEN Odoo-native: always `schedule_odoo_so(so_id, dt_pt, set_status=promote)` (writes date_order directly; promote=Submitted/blank→'Scheduled'); NO workiz_post, no review-task, returns `workiz:False`. Job length stays in `x_job_length_min`. So move-the-job AND confirm-the-customer are both Odoo now.

## Frontend (field.html)
`submitJobRs` success now calls **`apptConfirm(soid, name)`** (added near it) instead of `window.open(d.workiz_link)`. apptConfirm = confirm_preview → `window.prompt` (edit-or-cancel preview, reusing the addWorkizNote prompt pattern, no new modal) → send_confirm; toasts "held for quiet hours" / "sent" / error.

## ★ STILL OPEN: field.html is Workiz-entangled (~15 touchpoints)
`grep workiz_link static/owner/field.html` = ~15 hits across scheduling/duplicate/notes/links. Only the reschedule-confirmation one is converted. Notably **line ~5235 = DUPLICATE-job flow still pops Workiz "for line items"** → should point at the specialist's Odoo line-items editor `POST /api/job/lines` instead. Retiring Workiz from field.html end-to-end = a coordinated lead↔specialist pass (flagged via AGENT_MAIL 2026-08-03; split: lead=scheduling/confirm, specialist=billing/line-items). field.html is the collision-prone V1 file — don't both edit at once. See [[project_workiz_retirement]].
