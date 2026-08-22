---
name: project_call_recording_transcript
description: "Call recording + readable TRANSCRIPT (built 2026-08-04). Records inbound + outbound calls (consent line — CA 2-party), saves audio to the customer's thread/Odoo, and transcribes via Twilio Voice Intelligence → text lands in the same thread. DJ prefers reading."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T06:00:43.780Z
---

**Every call is recorded + transcribed to READABLE text** (DJ: "much bigger reader than listener"). voice.py, lead lane, built 2026-08-04.

## Flow
- **Consent (CA is two-party):** inbound GREETING now includes "This call may be recorded for quality"; outbound plays `CONSENT` to the CUSTOMER via a nested `<Number url=/voice/consent-whisper>` before the legs bridge. Non-negotiable legally.
- **Recording:** inbound `<Conference record="record-from-start">`; outbound `<Dial record="record-from-answer-dual">`. Both set `recordingStatusCallback=/owner/voice/recording-saved?phone=<norm>&dir=in|out`.
- **`/voice/recording-saved`:** logs "📞 {incoming|outgoing} call — recording. Listen: /owner/voice/rec?sid=<sid>" to the customer's inbox conv (`_conv_append`) + Odoo chatter (`_log_odoo`), then kicks off transcription.
- **Transcript = Twilio Voice Intelligence** (app moved off OpenAI→Claude which can't do audio; Twilio classic `transcribe` only works on `<Record>`/voicemail, not bridged calls). Service created via **`GET /voice/vi-setup?token=CRON_SECRET`** → SID stored in `wsc.voice.vi_service` = **`GAe3e7587849d0c1c5b8d79fcfd1b4b75b`** (webhook → /voice/transcript-ready). recording-saved POSTs `intelligence.twilio.com/v2/Transcripts` {ServiceSid, Channel:{source_sid:RecordingSid}, CustomerKey:phone}; stashes `wsc.voice.trans.<tsid>` = {phone,dir}.
- **`/voice/transcript-ready`** (VI webhook): fetches `/Transcripts/<sid>/Sentences`, builds "Dan: … / Customer: …", saves the readable transcript to the customer's inbox thread + Odoo chatter.

## Caveats / next
- Transcript has a short delay after the call (VI processes the recording async).
- Outbound = dual-channel (clean Dan/Customer separation). **Inbound conference = single mixed track** → speaker labels are rough (all one channel). Fine for v1; improve later if needed.
- Not yet tested on a REAL call (recording flow can't be curled without placing a call). Verify on DJ's next inbound + an outbound dial. Per-minute cost for recording + VI (small). See [[project_voice_inbound_plan]], [[project_click_to_call]].
