---
name: project_twilio_port_complete
description: "Twilio port COMPLETE 2026-07-31 — all 7 Workiz numbers now in DJ's Twilio acct, reconfigured via REST API; how to drive Twilio from here."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-13T14:45:32.694Z
---

**The Workiz→Twilio number port is COMPLETE (2026-07-31).** All 7 numbers transferred from Workiz's Twilio account (`[TWILIO_ACCOUNT_SID — in Render env]`) into DJ's own Twilio account (gaining SID `[TWILIO_ACCOUNT_SID — in Render env]`) via Twilio ticket 27332980 / Workiz-side ticket 28681832. Numbers: 760-334-5315/5350/5355, 951-223-4602, 951-927-8680 (local) + 800-283-8765, 855-245-2273 (toll-free). Supersedes the "port pending" state in [[project_twilio_port_details]] and [[project_twilio_port_from_workiz]].

**Why:** ends a ~2-month port saga. On transfer, Twilio WIPES each number's config (all 7 landed on demo.twilio.com URLs), so they had to be re-pointed at the field app.

**How to apply / drive Twilio from Claude Code:**
- No Twilio MCP. Use the **REST API via curl** with Account SID + Auth Token (same pattern as Odoo/Render). Credentials are NOT in memory/CLAUDE.md by design — they live as **Render env vars `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` on service `srv-d78le0fkijhs738dsli0`** (wsc-field-assistant), and the app's `routers/owner/voice.py` + `sms.py` use them. Render MCP can WRITE/merge env vars but CANNOT read secret values back, so to curl from here DJ must supply the Auth Token via a file (his standard key-sharing method).
- Reconfigured all 7 to match the known-good template number 760-343-5762: **Voice** `POST https://wsc-field-assistant.onrender.com/owner/voice/incoming`, **SMS** `POST https://wsc-field-assistant.onrender.com/owner/api/sms/incoming` (via `POST .../IncomingPhoneNumbers/{PN_SID}.json` with VoiceUrl/VoiceMethod/SmsUrl/SmsMethod).
- Added the **5 local** numbers to Messaging Service "WSC Sender" `MG9d920513cc6e7f7963a4334a818fbf05` for outbound A2P sending (`POST https://messaging.twilio.com/v1/Services/{MG}/PhoneNumbers` PhoneNumberSid=...). Toll-frees excluded — separate toll-free verification program (still pending; SMS on 800/855 blocked until verified, voice works).
- **⚠ CORRECTED 2026-08-13 — WSC Sender pool must contain ONLY `+17603345355`.** Putting all 5 local numbers in the pool was a MISTAKE: the app sends every outbound customer text via `MessagingServiceSid=MG9d92…` (routers/owner/sms.py `_send_sms`, lines ~63-66), and Twilio then pool/sticky-picks ANY number in the pool as the `From`. Customer **Sally Suchil** (+13104221502) got texted from `+17603345350` and flagged it: *"+1 (760) 334-5350 is new text number… +1 (760) 334-5355 old text number."* Fix = removed the other 5 senders from the messaging service (`DELETE https://messaging.twilio.com/v1/Services/{MG}/PhoneNumbers/{PN_SID}`), leaving only `+17603345355` (sid `PN5cf4cce2134594e3e9d31437982eb1d5`). Verified: a test via the messaging service resolved `from=+17603345355`, delivered. **NEVER re-add numbers to this pool** — customers must always see the one recognized line. Removed sender PN sids (if ever needed to re-add): 5350=PN429f6ec7015dbfec2e9aaa48573ae28f, 5315=PN7561a9f6c4e79ec28a0cc0757e2bf0df, 5762(760-343-5762)=PN0691d6f60f06a35db527557466e471e1, 951-223-4602=PNabf581b4838fe5633cc2a1a4df9c47ad, 951-927-8680=PN059f38456eb7de45a9725eedad5f1534. (Removing from the pool does NOT touch each number's own inbound SmsUrl webhook — inbound to them still hits the app.)

**Voice greeting:** `routers/owner/voice.py` constant `VOICE` controls Twilio TTS voice for greeting/voicemail/whisper. Changed from robotic `"man"` → **`"Polly.Matthew-Neural"`** (natural neural) on 2026-07-31 per DJ. Swap that one constant to change the voice. Call flow = greet caller → hold in conference → ring DJ. A full conversational "Claude answers" AI receptionist (Media Streams + Claude API + premium TTS) was discussed as a separate future project, not built.

**DJ's MAIN OUTBOUND TEXTING number = `760-334-5355` (local).** Corrects the stale note in [[project_twilio_port_details]] that tagged toll-free 855-245-2273 as "main business line" — 855 may be a main VOICE/inbound line, but DJ texts customers FROM the local 760-334-5355 (confirmed by DJ 2026-07-31: "main number is 760 and ends in 55"). It's attached to WSC Sender (MG9d92…, `us_app_to_person_registered=True`) and reconfigured, so it can send outbound A2P texts now — NO toll-free verification needed for it. Toll-free verification only matters if DJ ever wants to send FROM 800/855 (none on file as of 2026-07-31; inbound to them works, outbound blocked until verified).

**Still open:** Workiz account extension to mid-August (asked of Jay Kelkar + Breanna/porting so DJ can export his data before cancellation — [[feedback_ported_means_twilio]]).
