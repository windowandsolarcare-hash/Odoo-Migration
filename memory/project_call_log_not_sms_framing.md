---
name: project_call_log_not_sms_framing
description: "_log_odoo (sms.py) prefixes every 'in' log with '📩 Received SMS:' — which made call recording/transcript + voicemail logs read as inbound TEXTS in the customer chatter. Fix: bodies starting 📞/📄/🎙️/📝 post AS-IS (self-describing), no SMS wrapper; real texts keep 📩/📤."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T18:22:50.254Z
---

**DEPLOYED 2026-10-11 to main (commit 3e6ba155, live 11:11 AM PT; DJ picker deploy; Lead QC-GREEN). HR-reported (res.partner 23243 Oct 10, 22990 Aug 31): chatter showed "📩 Received SMS: 📞 Outgoing call recording…" / "📩 Received SMS: 📄 Outgoing call transcript…".**

**Root cause:** `_log_odoo(partner_id, direction, body)` in `routers/owner/sms.py` did `label = '📩 Received SMS' if direction=='in' else '📤 Sent SMS'` and posted `f"{label}: {body}"`. Call recording (`📞 {who} call recording…`), call transcript (`📄 {who} call transcript:…`) and voicemail (`🎙️ Voicemail received…`, `📝 Voicemail transcript:…`) are all logged with direction `'in'` (voice.py), so they inherited the inbound-SMS wrapper and read like texts.

**Fix (surgical, _log_odoo only):** `if _b[:1] in ('📞','📄','🎙','📝'): msg = body` (post self-describing AS-IS) `else: msg = f"{label}: {body}"`. Real texts keep the 📩/📤 wrapper. **Unicode gotcha:** the voicemail body is `🎙️…` = U+1F399 **+** U+FE0F (VS16); `_b[:1]` returns only the first code point U+1F399, so the tuple must contain bare `'🎙'` (U+1F399), NOT the VS16 composite — verified against the real bodies. Record/transcribe/voicemail-capture flows untouched. The APP INBOX was already fine (stores the raw self-describing body via `_conv_append`, no "Received SMS" there) — only the Odoo chatter had the wrong framing. See [[project_transcript_accessor_compare_fill]].
