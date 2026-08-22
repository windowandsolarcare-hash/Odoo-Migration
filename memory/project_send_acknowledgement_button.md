---
name: project_send_acknowledgement_button
description: "Job detail (v2_field.html) has a \"📩 Send acknowledgement\" button that sends the Stage-0 maintenance heads-up (branded add-to-calendar / \"I'll be there\" page) per job, reusing /api/maint/advance/send."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-11T16:03:35.880Z
---

**DJ's need (2026-08-11):** For a far-future maintenance job (e.g. Caroline & Graham, SO 004932, Nov 24), DJ wanted a per-job button to send the "acknowledgement" heads-up — the branded page that lets the customer add it to their calendar and tap "Yes, I'll be there." He noted the logic already exists; asked which button. It didn't exist on the job screen (only Send scheduling options / Send confirmation, plus Mark confirmed / Mark acknowledged which only RECORD, no text). So I added it, reusing the existing Stage-0 flow.

**Distinction:** acknowledgement = Stage-0 heads-up (far-future, "your next service is <date>, reply OK / I'll be there", branded `calfeed.appt_link`). Confirmation = Stage-1 (~4 days out, "confirm the time"). Different texts, different pages.

**Build (commits reminders e7b4e5e, v2_field 5f737ac):**
- reminders.py `send_maint_advance(so_id, body=None)` — optional body sends DJ's edited wording (branded link already baked into the previewed text).
- reminders.py `POST /api/maint/advance/send` — now supports `send:false` → returns the preview `{message, first, has_phone, skip_reason}` WITHOUT texting; and `message` on a real send passes edited text. The old HUD-card call (`{so_id}` only, send defaults True) is unchanged.
- v2_field.html: `📩 Send acknowledgement` button (`ackLaunch()`) → previews via send:false, opens the shared `_openSendBox` (same box as Send confirmation, no AI-rewrite), sends via send:true, then `loadAckState()`. Reuses `send_maint_advance` → `_maint_row` → `MAINT_TEMPLATE` + `calfeed.appt_link` — no new message/page logic.

Related: [[project_maint_ack_backfill]], [[project_status_scheduled_now_confirms]]. The broader maintenance-confirm redesign DJ flagged is still open (he's questioning the maint layer generally) — but he explicitly wants the acknowledgement send, so this is aligned.
