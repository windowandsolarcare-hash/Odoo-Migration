---
name: project_click_to_call
description: "Outbound click-to-call (built 2026-08-04) — DJ dials customers on the BUSINESS line from the app. voice.py POST /voice/dial rings DJ's cell then bridges to the customer with the business number as caller ID (customer never sees DJ's personal cell)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T04:13:51.950Z
---

**DJ can now call OUT on the business line from the app** (before: Call buttons were `href="tel:"` = native dialer = his personal cell showed to the customer; no business-line dialing existed).

## Backend (voice.py, lead lane) — LIVE 2026-08-04
- **`POST /owner/voice/dial {to, name?}`** — Twilio REST-creates a call **To=DJ_PHONE_NUMBER, From=TWILIO_BUSINESS_NUMBER** (DJ's cell rings, showing the business line), `Url=/voice/outbound-bridge`. Returns `{ok, name, message:"Calling you now — pick up and I'll connect <name>."}`. Resolves name via `_find_customer` if not passed. Guards: valid 10-digit `to`, creds present.
- **`GET/POST /owner/voice/outbound-bridge?cust=&name=`** — when DJ answers: whisper "Connecting you to <name>" then **`<Dial callerId=TWILIO_BUSINESS_NUMBER answerOnBridge=true>{customer}</Dial>`** → customer's phone rings showing the BUSINESS number, never DJ's cell. Sibling of the inbound flow (`_dial_dj`).
- NOT auto-testable safely — curling /voice/dial places a REAL call to DJ's cell (same caveat as /voice/incoming). DJ tests on first tap.

## DIALER SCREEN + caller-ID selection (built 2026-08-04, lead)
DJ wanted a Workiz-style dialer: pick which of his numbers to dial OUT from + search a customer + keypad.
- **`static/owner/v2_dialer.html`** (NEW, launcher tile 📞 Dialer): top **"Call from" dropdown** (his numbers, persisted localStorage) + **customer search** (`/owner/api/intake/search` → name/phone) + **keypad** → **📞 Dial** → `POST /owner/voice/dial {to, caller_id, name}`.
- **`/voice/dial` + `/voice/outbound-bridge` now take `caller_id`** (the chosen From) → that number is what the CUSTOMER sees (default `TWILIO_BUSINESS_NUMBER`). So DJ picks which line per call.
- **`GET /owner/voice/numbers`** → the dropdown list; labels editable via `ir.config_parameter wsc.voice.numbers` (JSON [{number,label}]); defaults `_DEFAULT_NUMBERS` (Main/Thumbtack/Google/toll-frees/locals — DJ to confirm/relabel).
- **How an INBOUND call patches through (DJ asked):** the card is a heads-up; his CELL rings in parallel (the `_dial_dj` leg) — he answers his phone to talk. A web page can't answer a PSTN line; the card just says who it is.

## ★ STANDING RULE (DJ 2026-08-04): NO place dials directly — every "Call" DROPS INTO THE DIALER
A one-tap direct call is too easy to misfire. So EVERY Call action (call card "Call back", followups.py Call buttons, job-detail Call replacing Sync, any inbox Call) must **navigate to the dialer PREFILLED**, where DJ picks the FROM line + taps Dial deliberately. The **ONLY** thing that POSTs `/owner/voice/dial` is the Dial button INSIDE `v2_dialer.html`. Prefill contract: `v2_dialer.html?to=<phone>&name=<name>` OR `?partner_id=<id>` (resolves via `GET /owner/voice/resolve?partner_id=` → {phone,name}). Call-card "Call back" done (lead); followups/inbox/field routed to specialist.

## Frontend (specialist lane — routed via AGENT_MAIL 2026-08-04)
The Call buttons (`followups.py` L205-221 `href="tel:"`, plus any in v2_field/v2_inbox) need to switch to: onclick → `POST /owner/voice/dial {to, name}` → toast the returned `message`. Until wired, Call still opens the native dialer (personal cell). See [[project_voice_inbound_plan]].
