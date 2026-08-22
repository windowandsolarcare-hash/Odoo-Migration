---
name: project_inbox_ivr_guard_and_back
description: "Inbox — sms.py automated/IVR draft guard (_is_automated, _AUTOMATED_NUMBERS) + v2_inbox.html is the LIVE inbox (inbox.html legacy); thread Back uses history state"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-03T01:54:29.707Z
---

Two inbox facts (2026-08-01):

**1. Robocall/IVR guard (sms.py).** `_is_automated(message, from_number)` decides an inbound is an automated system/IVR menu (robocall or lead-service voicemail transcript) — NOT a customer message. Fires on IVR phrasing (`_IVR_STRONG` single hit like "press 1 to"/"say details"/"repeat lead information"/"to connect with the customer", or 2+ `_IVR_WEAK` hits) OR a known toll-free service number in `_AUTOMATED_NUMBERS` (normalized last-10; currently just `8779473639`). **To silence a new robocall number, add its 10-digit form to `_AUTOMATED_NUMBERS`.** Effects: `_draft_reply` returns '' (never drafts a reply to a robocall — it takes an optional `from_number` now), and the SMS inbound handler treats automated msgs QUIET like an auto-handled one (status `open` not `needs_reply`, no draft, no push, sets `conv['automated']=True`). Verified no false-positives on real texts.

**1b. Lead-service calls (Angi/Thumbtack/HomeAdvisor) are captured as LEADS (sms.py + voice.py).** A voicemail from the lead line ("press 1 to connect with the customer… press 2 to repeat lead information") carries the customer's phone + a lead id in the transcript. `sms.handle_lead_call(caller,text)` creates a **crm.lead** (type lead, company 1, phone, referred=`LEAD_SOURCE_LABEL='Phone Lead Service'`) + a **My Day task** ("🧲 Call new lead <phone>") + a **customer inbox thread keyed to the CUSTOMER's number** (so Call/Text reaches them, not the 877 service) + a push; idempotent per lead id (`wsc.lead.seen.<id>`). Trigger `_is_lead_call` = number in `_LEAD_NUMBERS={8779473639}` OR the connect-with-customer/lead-information IVR pattern + a phone. `voice.py` `/voice/transcription` branches to it and keeps the service thread quiet. **Knobs to tune when DJ confirms the service:** `LEAD_SOURCE_LABEL` + `_LEAD_NUMBERS` in sms.py. NOTE: pressing IVR keys (DTMF) is intentionally NOT built — the menu's "press 2 = details" only repeats the phone+id already parsed; "press 1" connects the customer live (unwanted). Richer lead detail lives in the Thumbtack/Angi app/email/API, not the phone menu. Testing the voice/sms webhooks fires real web-push to DJ — use throwaway data.

**1c. Job-detail "💬 Texts" (v2_field.html).** Brain-row button `openTexts()` opens the customer's live inbox thread in the list-sheet (bubbles + reply box → `/api/inbox/send`). Backed by NEW `GET /owner/api/inbox/thread_by_partner?partner_id=<id>` (sms.py): resolves partner (or parent person) → phone → `_conv_get(norm)`; returns `{ok, phone, norm, name, conv}` (conv null if never texted; norm still returned so the first text can be sent). Reuses the inbox conv store — no new infra.

**2. v2_inbox.html is the LIVE inbox; inbox.html is legacy.** DJ's launcher (v2_apps.js) opens `static/owner/v2_inbox.html`. The `/inbox` route (sms.py) still serves the legacy `inbox.html`, and push notifications link to `/owner/inbox?c=<norm>` (legacy). Edit **v2_inbox.html** for owner-facing inbox changes (rule 10). Thread nav is view-swap (no real routing): `openThread` pushes `history.pushState(...,'#thread')` so the phone Back button / swipe-back returns to the LIST (via a `popstate` handler → `_showList()`) instead of exiting to Home; the ‹ button routes through `history.back()` too. Related: [[project_two_quote_pages_two_launchers]], [[feedback_field_html_js_syntax_check]].
