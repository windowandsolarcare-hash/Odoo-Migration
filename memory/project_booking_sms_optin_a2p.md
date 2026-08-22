---
name: project_booking_sms_optin_a2p
description: The /book form has an A2P SMS opt-in checkbox (Twilio 10DLC approval gate). What it is + where consent is stored. It is a PASSIVE form checkbox — NOT outbound to existing customers.
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-18T15:29:31.985Z
---

**Built 2026-08-18 (Lead launch-blocker → Specialists).** The public booking form at **wscare.pro/book** (routers/booking.py + static/booking/index.html) now has an SMS opt-in checkbox. It is the **Twilio A2P 10DLC approval GATE** — the old WordPress quote form had it; the new site routes all booking to /book, so it had to be restored there or the SMS campaign approval is at risk.

**★ What it is / DJ's concern (he asked while driving):** it is a **passive, optional checkbox on the booking form only** — NOTHING is sent to anyone, and it does NOT go out to existing customers asking them to opt in. DJ explicitly does NOT want mass consent-outreach and there's no rule requiring it. This is just a form field a NEW customer can tick. DJ approved on that understanding.

**Spec (Lead, verbatim):** UNCHECKED by default, OPTIONAL (booking submits fine without it), **service/account ONLY, NOT marketing** (marketing bundling = Twilio rejection err 30913). Exact wording on the page: "Yes, please text me. I agree to receive text messages from Window & Solar Care about my appointments, service, and account at the number provided. Msg frequency varies. Msg & data rates may apply. Reply STOP to opt out, HELP for help. Consent is not a condition of purchase." Placed just above the "Request Appointment" button.

**Wiring:** checkbox `#smsConsent` (unchecked) → submit() adds `sms_consent: !!checked` to the `POST /book/api/request` body. `api_request` reads `sms_consent = bool(body.get('sms_consent'))`; on TRUE it posts a **timestamped consent proof (PT) to BOTH the SO chatter AND the contact** (res.partner, where the phone lives) with the exact language shown + phone, and stores `sms_consent` in the `booking.requests.pending` queue dict. Unchecked = nothing recorded (default). Commits: index.html ac53a8b, booking.py 4edc8ec.

**NOT mine:** the domain/Twilio-campaign side — Lead updates the live Twilio campaign's Privacy/Terms/opt-in URLs + Message Flow at DNS cutover (moving to wscare.pro changes the URLs the campaign cites). Privacy Policy + Terms pages w/ SMS clauses + footer links are the WEB session's (marketing site). See the WEBSITE_REBUILD_BRIEF §Twilio A2P. [[project_calendly_retired]] (booking replaced Calendly).
