---
name: feedback_call_opens_dialer_never_dials
description: STANDING RULE — no Call button anywhere may place a call on tap; every Call opens the dialer PREFILLED so DJ picks the FROM line + taps Dial deliberately.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T05:05:09.042Z
---

**DJ standing rule (2026-08-04, via lead):** a one-tap direct call is too easy to fire by mistake. **NO frontend Call action may POST `/owner/voice/dial` directly.** Every Call button must navigate to the dialer, prefilled:

`location.href='/static/owner/v2_dialer.html?to='+encodeURIComponent(phone)+'&name='+encodeURIComponent(name)`
or `...?partner_id='+id` (dialer resolves phone via `GET /owner/voice/resolve?partner_id=`).

The ONLY place that calls `/owner/voice/dial` is the **Dial button inside v2_dialer.html itself**. The dialer prefills the number from `?to=`/`?name=`/`?partner_id=`; DJ then picks the caller-ID (FROM) line and taps Dial.

**Why:** DJ misfires taps; a deliberate two-step (open → Dial) prevents accidental calls, and dialing must go out on the BUSINESS line (never his personal cell), which the dialer enforces.

**How to apply:** any new Call button → nav to the dialer, never a direct dial. Converted 2026-08-04: `followups.py` callFU, `v2_field` callFromField + the job-detail 🔄 Sync→📞 Call button (opens dialer with `activeJob.partner_id`), `v2_customers` callCust. (This SUPERSEDED the earlier click-to-call wiring that POSTed /voice/dial from those buttons.) See [[project_click_to_call_business_line]] if present.
