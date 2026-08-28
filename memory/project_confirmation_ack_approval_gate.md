---
name: project_confirmation_ack_approval_gate
description: "★ DJ 2026-08-27 standing rule: NO customer-facing text auto-sends without DJ approval, EXCEPT STOP/START (carrier compliance). The YES/maint confirmation ACKs in reminders.py no longer auto-text — they RECORD the confirmation automatically but HOLD the outbound 'see you then' as a one-tap approve card."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-28T06:24:09.936Z
---

**Standing rule (DJ approved 2026-08-27):** no customer-facing text sends without DJ's approval. **Sole exception: STOP/START** carrier-compliance replies (TCPA — legally required, stay automatic). Trigger: DJ caught the confirm flow auto-sending "Great — see you then!" (`reminder_ack`) to Robert Hollenbeck (SO 264957) on a YES, with no approval.

**What changed (`routers/owner/reminders.py`, commit e3330a7):**
- The 4 confirmation-ACK auto-sends are gated. They previously did `messaging.send(..., kind='reminder_ack'|'maint_advance_ack'|'maint_confirm_ack', ...)` right after recording the confirmation. Sites: `handle_reply` YES path (~486), `_maint_late_ack` (~919), `_maint_handle_inbound` confirm stage (~963) + advance stage (~972).
- **The confirmation is STILL recorded automatically** — `CONFIRM_KEY`/`MAINT_CONFIRM_KEY` set, `appt_confirm()`, Odoo chatter, clear-awaiting all unchanged. ONLY the outbound "see you then" text is held.
- New helper `_queue_ack_approval(to, partner_id, so_id, body, kind, so_name='', name='')` posts a **one-tap approve card** to the HUD Needs-You (reuses the existing `submit_item` + `draft.on_approve` pattern). Card id `reminders:ack:<kind>:<so_id>`.
- New endpoint **`POST /owner/api/reminders/send_ack`** (payload `{so_id,to,partner_id,kind,body}`) is the ONLY path that now sends a confirmation ack — DJ taps approve → it `messaging.send`s (idempotent on `<kind>:<so_id>`) + deletes the card. Verified live by content (empty POST → 400 "to, body, so_id required").

**How to apply / gotchas:**
- Do NOT re-add an auto `messaging.send` of any customer-facing ack in the reminders/confirm flow. Route new customer texts through an approval card (`_queue_ack_approval` or the inbox draft mechanism), never a direct auto-send. Claude-drafted inbox replies were already approval-gated (drafts never auto-send) — that's the model.
- The inbound path (`sms.py` ~1295) sets a handled thread to **`'open'`, never `'done'`** — there is no auto-file-to-done bug; the "buried thread" DJ hit was the auto-sent ack + thread leaving Needs-Reply. The approve card is now the surfacing mechanism.
- STOP/START stays automatic (`messaging.py record_optout`) — do not gate it; it must stay visible/threaded per DJ.
- These are the LIVE handlers (function imports from sms.py, not shadowed routes). See [[feedback_never_send_dj_to_odoo]] and the maint attribution memory [[project_maint_confirm_ack_attribution]].
