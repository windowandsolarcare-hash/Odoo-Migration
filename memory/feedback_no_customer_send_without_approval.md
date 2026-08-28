---
name: feedback_no_customer_send_without_approval
description: "★ STANDING RULE (DJ 2026-08-27): NO customer-facing text sends without DJ's approval — the SOLE exception is STOP/START carrier-compliance replies (legally required, stay automatic). AND every outbound must stay visible in the inbox (never auto-filed to done)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-28T06:14:29.159Z
---

**DJ 2026-08-27, reaffirming a long-standing understanding:** *"all communications should run through the inbox so I'm aware of what was last sent… nothing should be sent without my approval."*

**What triggered it:** DJ noticed the reminder confirm flow AUTO-SENT a customer text without him. When a customer texts YES to confirm, `reminders.py handle_reply` fired `messaging.send(..., kind='reminder_ack', idem='reminder_ack:<so_id>')` (~line 488) — the canned *"Great — see you then! – Window & Solar Care"* — with no DJ approval. Same auto-ack pattern: `maint_advance_ack` (~921), `maint_confirm_ack` (~965/974). (Real example: Robert Hollenbeck SO 264957 — reminder_eve sent Thu 2026-08-27 7:03 PM PT, he replied "Yes sir" 7:04 PM, system auto-acked "Great — see you then" 7:04 PM — none of the ack approved by DJ.)

**The rule going forward:**
1. **No customer-facing text sends without DJ's approval.** Reminders (DJ taps send on the review card) and Claude-drafted replies (drafts sit in the inbox, DJ sends) were ALREADY gated — good, leave them. The YES/confirmation auto-ack must ALSO be gated: still RECORD the confirmation automatically (✅ chatter + CONFIRM flags), but the outbound "great, see you then" text waits for DJ (1-tap approve in Needs-You / inbox).
2. **SOLE exception = STOP/START** carrier-compliance auto-replies. Legally required (TCPA/carrier) — MUST stay automatic. Never gate these. **Flag this exception to DJ rather than silently obeying "nothing auto-sends" — blindly gating STOP breaks compliance.** DJ explicitly approved keeping STOP/START automatic.
3. **Every outbound stays VISIBLE in the inbox** and the conversation must NOT be auto-filed to `done` after a send — DJ must always be able to see "what was last sent." The confirm flow was burying the thread (DJ couldn't find Robert's ack in the inbox even though it sent + threaded).

**Key clarification for DJ's peace of mind:** Claude does NOT text customers on its own. `_draft_reply` in `sms.py` only produces a DRAFT shown in the inbox; nothing Claude drafts auto-sends. The only unapproved auto-sends were the YES-ack and STOP/START. (Verified in code 2026-08-27.)

Owner of the fix: Specialists (messaging.py / reminders.py / sms.py). Money/customer path → Lead fresh-eyes review before go-live. Related: [[feedback_email_draft_first_always]], [[feedback_assistant_use_app_workflow_not_raw_api]], [[feedback_never_send_dj_to_odoo]].
