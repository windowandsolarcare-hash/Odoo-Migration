---
name: project_shared_send_box
description: "DJ's rule (2026-08-06): ONE shared AI-assisted send/preview widget everywhere — don't rebuild it per screen/card. WSCThread already does reply+suggest+edit+send; the specialist's _openSendBox does the branded schedule/confirm ✨ box. Plan = promote to a shared wsc_sendbox.js. PENDING specialist reply on who authors it."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T23:20:01.957Z
---

**DJ 2026-08-06:** "we already have AI-assisted text replies. Don't rebuild it. Make it shared." Triggered when the specialist asked lead to add the "✨ AI tailor" button to the 4-day-confirm + night-before HUD approval cards.

## The already-shared piece (all 4 steps, ONE widget)
**`static/owner/wsc_thread.js` = WSCThread** — shows the thread → **✨ Suggest a reply** (`/api/inbox/suggest`) → editable box → **Send** via the canonical inbox send (lands in the thread). Used by v2_field, v2_customers, v2_command, v2_reeng_review; v2_inbox shares its bubble renderer + suggest. So "show prior text + suggest + edit/preview + send→thread" is ALREADY one shared thing for free replies.

## The second (not-yet-shared) flow
**`_openSendBox` in v2_field.html (specialist)** — branded preview + **"✨ AI tailor"** (`POST /api/sched/ai_message`, `ai_sched_message(intent='schedule'|'confirm')`) for SCHEDULE/CONFIRM messages carrying the branded booking link. Job detail ONLY. This is the second AI-assist flow DJ wants folded into one.

## Plan (doc: `3_Documentation/SHARED_SENDBOX_PLAN.md`, in the app repo)
Promote `_openSendBox` → self-contained shared **`wsc_sendbox.js` `WSCSendBox.open({so_id,mode:'reply'|'schedule'|'confirm',prefill,link,onSent})`** (✨ tailor → sched/ai_message or inbox/suggest, link kept verbatim; Send → messaging.send / sched/launch → inbox thread). Consumers call it; none rebuild.
**Ownership split:** SPECIALIST authors wsc_sendbox.js (it's their box + in v2_field.html — we've collided there, see [[feedback_multiagent_collision_field_html]]); LEAD wires the HUD 4-day-confirm + night-before approval cards (my reminders review: v2_maint_comms.html + reminders review page) once it exists.

## STATUS: PENDING
Posted the plan + ask to AGENT_MAIL 2026-08-06 — waiting on the specialist to say who authors `wsc_sendbox.js`. Lead is ready to wire the HUD cards the moment it's in. On DJ's next "mail", check for their reply and proceed. Do NOT bolt a copy of the ✨ box onto the cards. See [[project_auto_confirm_branded_page]] [[feedback_reuse_canonical_endpoint]].
