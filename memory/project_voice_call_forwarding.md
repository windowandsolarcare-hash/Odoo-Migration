---
name: project_voice_call_forwarding
description: "How the Twilio voice/call-forwarding flow works (routers/owner/voice.py) + why a spam call LOOKS like it's from Window & Solar Care, and the dead-air + block-list fixes (DJ 2026-08-10)."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-10T19:00:59.340Z
---

**The flow (voice.py):** a customer calls the business line **855-245-2273** → `/voice/incoming` puts the caller in a hold conference + places an outbound leg to DJ's cell **951-972-6946** using the **business number as caller ID** (`_dial_dj`). So on DJ's phone it LOOKS like "Window and Solar Care" is calling him — it's really the forwarding leg. When DJ answers (human, via Twilio AMD) → `/voice/dj-bridge` whispers **"Call for Window and Solar Care from <name/Unknown (number)>"** then joins him into the conference. Non-human answer (carrier VM) → hang up so caller falls to OUR voicemail (`/voice/dj-status` → `voicemail-redirect` → `_vm_block`). `room = "room-<callsid>"` so the caller's CallSid = `room[5:]`. Rich web-push on every call (`_notify`) + a text backup for KNOWN customers.

**DJ's 2026-08-10 confusion (spam):** he got a call "from Window and Solar Care", answered, heard "a call from Unknown + number", then his Samsung **Bixby** started. Cause (confirmed in Twilio `/voice/recent`): a spam number **+1 586-222-1972** hit the business line, was forwarded to his cell (biz caller ID = looks like a self-call), the screening whisper announced it, BUT the spammer had already hung up (~9s inbound leg) — so DJ was joined to an EMPTY conference = dead air, and his phone's Bixby activated on the silence. The "Bixby playing" was his phone, not our system.

**Fixes shipped (commit 1ad7c59, voice.py):**
1. **No dead-air ring.** `/voice/dj-bridge` now, after the human check, GETs the caller's Twilio call status (`_API/Calls/{room[5:]}.json`); if it's no longer `in-progress/ringing/queued` (caller gone), it plays "The caller already hung up. Goodbye." + `<Hangup/>` instead of joining an empty conference. Best-effort (API fail → normal behavior); never affects a still-connected caller.
2. **Block-list = straight to voicemail.** `_blocked(norm)` reads `BLOCK_KEY = 'wsc.voice.blocklist'` (JSON list of normalized numbers) — already gated `/voice/incoming`. Changed that gate from a hard `<Reject>` to greeting + `_vm_block` (blocked spam → voicemail, never rings DJ). NEW endpoints (token = CRON_SECRET `wsc-daily-sync-2026`): `POST /voice/block {number}` (empty number = block the last inbound caller from `wsc.voice.incoming`), `POST /voice/unblock {number}`, `GET /voice/blocklist`. Verified live: blocklist → `{ok:true,blocked:[]}`.

**DJ chose NOT to do** "all unknown callers → voicemail" (would send new customers/leads to VM — a service business needs unknown first-time callers to ring through). To block a spammer: DJ tells me the number (or "block the last caller") → I POST /voice/block. A "Block" button on the call card (v2_callcard.html) would be the self-serve next step (not built yet). Business=855-245-2273, DJ cell=951-972-6946.
