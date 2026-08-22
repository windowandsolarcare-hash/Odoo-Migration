---
name: project_inbox_hides_done_outbound
description: "Texting a customer whose inbox conversation is status='done' does NOT bring the thread back to the inbox — the All tab (inbox_list filter='active') hides 'done', and messaging.send() only reopens 'needs_reply', not 'done'. So an outbound (Zelle request/confirm/reply) to a resolved customer sends + threads but stays invisible."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T02:28:40.064Z
---

**Symptom (DJ 2026-08-05):** sent the Zelle request to John Bullock; it never appeared in his inbox.

**Root cause:** conversations live in `ir.config_parameter wsc.sms.conv.<norm>` (sms.py) with a `status` (needs_reply / open / snoozed / done). The inbox **All** tab = `GET /api/inbox/list?filter=active` (sms.py ~L1124) does `if filter=='active' and st=='done': continue` — **'done' threads are hidden from All** (only the 'done' filter shows them). `messaging.send()` threads every outbound via `_conv_append(conv,'out',body)` (it DID send + thread — John's conv got the message + paywatch armed), but its resurrect line only handles needs_reply: `if conv.get('status')=='needs_reply': conv['status']='open'`. A **'done'** conv stays 'done' → invisible even though you just texted them.

**Immediate fix done:** hand-set John's conv (`wsc.sms.conv.5026495321`) status → 'open' (data patch), he reappears in All. Verified.

**Durable fix — DJ's directive 2026-08-05 (broad, NOT targeted): "every time a text comes in or goes out, it should leave DONE."** So resurrect on ANY message: outbound `done→open` (messaging.send ~L343, ALL kinds incl. reactivation — DJ accepts; a reply flips to needs_reply anyway); inbound `done→needs_reply` (verify /api/sms/incoming already does regardless of prior status; broaden if not). Mailed specialist (their messaging.py/sms.py lane). Affects the whole Zelle feature.

**Also (display, not the SMS):** the Zelle SMS DOES send with real newlines (verified John's stored body = 13 `\n`, bullets/blank lines/signature intact — the CUSTOMER sees it clean). But the **v2_inbox thread bubble collapses newlines** on screen (run-on). Fix = `white-space:pre-wrap` (or `\n`→`<br>`) on the bubble body so DJ's view matches what the customer gets. Mailed specialist (v2_inbox bubbles = their recent work). See [[project_zelle_customer_ux]].
