---
name: project_outbound_call_callerid
description: "Outbound CALL caller-ID = the 'Call from' line DJ picks in v2_dialer (default Main 760-334-5355), NOT pooled like SMS. CNAM on 5355 currently shows only 'PALM DESERT' (no business name)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-13T21:40:09.640Z
---

**Outbound calls are NOT number-pooled** (unlike SMS — see [[project_twilio_port_complete]]). The number the CUSTOMER sees on an outbound call = the "Call from" line DJ selects in `v2_dialer.html`. Flow: dialer POSTs `/owner/voice/dial` with `caller_id=fromNum`; voice.py sets `biz=cid` and dials the customer with `<Dial callerId="{biz}">` (routers/owner/voice.py ~L592/633). The dialer remembers the pick per-device in `localStorage['wsc_dialer_from']`; if none, it uses the FIRST entry of `/owner/voice/numbers`.

**Default = Main 760-334-5355.** `/owner/voice/numbers` reads `ir.config_parameter` `wsc.voice.numbers` (falls back to `_DEFAULT_NUMBERS` in voice.py). Confirmed 2026-08-13 the saved list's first entry is `{"+17603345355","Main (760-334-5355)"}`, so the default call-from line is 5355. Other labeled lines exist on purpose for lead-source tracking: **5315 = "Thumbtack", 5350 = "Google"**, plus toll-frees, Saunders Printing (800-283-8765), Dan Direct/Hemet (951-927-8680), etc. Caveat: if DJ once tapped a non-Main line, that device sticks to it until he re-picks Main.

**Caller-ID NAME (CNAM):** Twilio Lookup on +17603345355 (2026-08-13) returns `caller_name = "PALM DESERT"` (just the rate-center city), type CONSUMER — i.e. **no business name is registered**, so recipients don't see "Window & Solar Care." To show the business name to people who don't have DJ in contacts requires either (a) registering a CNAM record (~15 chars, helps landline/VoIP recipients; many WIRELESS carriers ignore CNAM), and/or (b) enrolling in **Branded Calling** (name+logo+reason on cell phones) via Twilio Branded Calls / STIR-SHAKEN RCD, or third-party business profiles (Google Verified Calls, Truecaller, Hiya). All require business verification + have cost/propagation time. NOT set up yet as of 2026-08-13 — DJ asked about doing it.

**How to drive Twilio for this:** REST API via curl, Account SID `[TWILIO_ACCOUNT_SID — in Render env]`, Auth Token from DJ's Drive doc "Twilio" (his file-based key sharing). CNAM current state via `GET https://lookups.twilio.com/v2/PhoneNumbers/{E164}?Fields=caller_name,line_type_intelligence`.

**CNAM registration filed 2026-08-13 (FREE).** DJ chose display name **`WindowSolarCare`** (15 chars). Filed via Trust Hub:
- CNAM policy SID = `RNf3db3cd1fe25fcfd3c3ded065c8fea53` (requires an `end_user` type `cnam_information` with field `cnam_display_name` + a business customer profile attached).
- Business/Customer Profile (already twilio-approved) = `BUd18bb9a6d9aeddf24981a3a1de1d9afb`.
- Created TrustProduct `BUffaf18ea06b85dc83719bed11b0a04c4` (FriendlyName "WSC CNAM Caller ID") + EndUser `IT2e0168c0a4b744216ad070c3694c5cc4` (cnam_display_name=WindowSolarCare). Assigned both to the TP, Evaluation=compliant, submitted → status **in-review** (Twilio approves async).
- **PENDING NEXT STEP after approval:** assign phone number **+17603345355** to the approved CNAM TrustProduct so the name goes live. Check status: `GET https://trusthub.twilio.com/v1/TrustProducts/BUffaf18ea06b85dc83719bed11b0a04c4`. Steps recap = create TrustProduct(PolicySid=CNAM) → create EndUser(cnam_information) → 2x EntityAssignments (EndUser + BizProfile) → Evaluation → PATCH Status=pending-review.
- Reality check: CNAM is reliable on landline/VoIP; the 3 big WIRELESS carriers largely ignore CNAM now (they use branded calling). **Branded calling = still NOT set up** (DJ chose "free CNAM only for now" 2026-08-13; revisit if answer rates suffer — Twilio Branded Calling covers T-Mobile+Verizon, Hiya Connect ~$29/mo covers AT&T).
