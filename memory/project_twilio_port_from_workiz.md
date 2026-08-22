---
name: project_twilio_port_from_workiz
description: "Porting W&SC phone numbers off Workiz into DJ's own Twilio account — it's a Twilio-to-Twilio internal transfer (Workiz runs on Twilio), SIDs/PIN/numbers, and the A2P-wipe caveat."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Porting the business phone numbers off Workiz (Workiz is leaving ~2026-06-29).**

**Key insight:** Workiz's telephony RUNS ON TWILIO. So the numbers physically live in *Workiz's* Twilio account, and moving them to DJ's own Twilio account is an **internal Twilio-to-Twilio account transfer**, NOT a normal carrier port. Twilio's porting team confirmed this (Gaurav Chaudhary, 2026-06-12) and routed it to Twilio Support.

**Twilio ticket 27332980** (subject "LOA submitted on 5/10/26 with no response"). Reply address that adds to the ticket: `support+id00D20P-0165K@twilio.zendesk.com`. Twilio (Rakesh Kumar) requires 5 things for the transfer: Losing Account SID, Gaining Account SID, **approval from the losing account**, approval from the gaining account, desired date/time. Critical rule he stated: **"Twilio can only accept approvals from users listed on the Twilio account"** — DJ could NOT approve on Workiz's behalf; Workiz had to act. That was the blocker = "waiting for Workiz permission." Twilio auto-closed the ticket 2026-06-21 (no losing-side approval received); it reopens on reply.

**The IDs:**
- Losing Account SID (Workiz's Twilio acct): `[TWILIO_ACCOUNT_SID — in Render env]`
- Gaining Account SID (DJ's Twilio acct): `[TWILIO_ACCOUNT_SID — in Render env]`
- PIN for local numbers: **9634**
- Toll-free numbers need NO PIN — they port via Console approval.

**2026-06-22 unblock:** Workiz Porting Team (porting@workiz.com) sent "Window & Solar Care (25699) - US Port-Out Request Submitted" with the losing SID, PIN 9634, CSR (Twilio Inc, 548 Market St, SF #14510), Account Number AC79582... This gives the losing-side info.

**2026-06-23 — OPEN QUESTION RESOLVED (Rakesh, ticket reply ~11:47PM PDT): the CSR/PIN is NOT enough.** The disconnect that stalled everything: Workiz's porting team handed over a **CSR + PIN** = the artifact for a NORMAL port-out to an OUTSIDE carrier. But because the gaining account is ALSO on Twilio, Twilio does an **internal account-to-account transfer** and does NOT use the CSR/PIN — it needs **Workiz (losing account) to submit a TRANSFER APPROVAL directly to Twilio** (reply to ticket 27332980 or open their own, naming the gaining SID). Twilio says they have everything from DJ's (gaining) side and are ONLY waiting on Workiz's transfer approval. Workiz raised a ticket about the CSR PIN but NOT the transfer approval → STILL BLOCKED ON WORKIZ. Rakesh also confirmed: don't release the numbers, don't remove E911 (transfer wipes all config either way). NEW Gmail DRAFT written (reply to porting@workiz.com, NOT the Twilio ticket) explaining the internal-transfer requirement + giving Workiz the exact info to submit — see Status below.

**Numbers to transfer (7 — DJ confirmed ALL 7; submit in ONE porting request):**
Local: 760-334-5315, 760-334-5350, 760-334-5355, 951-223-4602, 951-927-8680
Toll-free: 800-283-8765, 855-245-2273
(DJ originally asked Workiz for only 5; Workiz released 2 extra — 760-334-5350 and 951-223-4602 — DJ keeps all.)

**Cutover:** originally requested Fri 2026-06-26, but DJ DECIDED to DECOUPLE — do NOT rush Friday. Send the Workiz transfer-approval email ONLY AFTER A2P is fully approved, so the port can't complete before A2P (porting in first = numbers on his account but unregistered = can't text = forced onto personal phone, which he refuses). Approve A2P first → then port. A slipped cutover is FINE as long as Workiz keeps numbers active. DJ controls the timing via when he sends the Workiz email.

**⚠ CAVEATS (must handle after/around the port):**
- Transfer **WIPES existing config, opt-outs, and A2P 10DLC registration** — must reconfigure + **re-register A2P** afterward. Ties into [[project_twilio_a2p_and_entity]] (register Standard Low-Volume under Saunders Printing EIN 87-3872426).
- Workiz: do NOT release the numbers (must stay active until port completes) + disable emergency/E911 config before submitting.
- Separate UNRESOLVED ask: SMS/text-message conversation history export from Workiz — escalated to Workiz Account Manager (2-3 business days), not yet delivered. DJ wants this before the numbers leave.

**A2P registration is a REAL blocker, not "fine":** DJ tried to register A2P 10DLC himself and could NOT complete it — as a sole proprietor that HAS an EIN, he could not find/select a "Sole Proprietor" option (correct: with an EIN you use the **Standard Low-Volume brand** path, not Sole Prop — see [[project_twilio_a2p_and_entity]]), and couldn't finish brand/campaign even on a separate test number he bought to try. He needs Twilio to walk him through it. The Twilio reply draft now explicitly ASKS for A2P registration guidance (not "that's fine").

**STATUS 2026-06-24 (evening):**
- **A2P** is now UNBLOCKED & moving on its own — DJ submitted the Primary Customer Profile (pending review ~2 biz days); watcher running. See [[project_twilio_a2p_and_entity]]. So the "A2P help" the old Twilio draft asked for is no longer needed — Claude did it directly via the TrustHub API.
- **Port action item = ONE Gmail DRAFT, PARKED, addressed to porting@workiz.com** (reply to their 6/22 "US Port-Out Request Submitted" thread, msg id 19ef01dcbcd684ee). It explains the internal-transfer-vs-CSR disconnect and asks Workiz to submit the transfer approval to Twilio (gives losing SID AC79582..., gaining SID ACc937..., all 7 numbers, authorization statement). DJ will SEND it ONLY AFTER A2P approval (his decision — see Cutover above). The OLD drafts to the Twilio ticket are obsolete (ignore).
- Still pending from Workiz separately: SMS conversation-history export (Account Manager, not yet delivered) — DJ wants before numbers leave. [[project_workiz_chat_export_to_odoo]] is the per-customer manual path already in use.
- NEXT TRIGGER: A2P approved → Claude registers brand/campaign → THEN DJ sends the parked Workiz email → Workiz approves transfer → cutover scheduled.
