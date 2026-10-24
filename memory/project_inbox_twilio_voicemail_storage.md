---
name: inbox-twilio-voicemail-storage
description: "Twilio inbound voicemails are stored as untyped messages inside the shared per-phone SMS Inbox conversation store (NOT a separate VM table); a VM is detected by the 🎙️/📝 + /owner/voice/rec?sid= body text, not by a source flag. Voice blocklist only silences the ring (still records a VM). The VM caller→customer resolver lacks the company_id filter."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-24T03:59:20.172Z
---

**Discovered 2026-10-24 (firsthand, during the spam-VM proposal).** How INBOUND Twilio voicemails work in the Render app:

**Storage — no dedicated VM table.** A Twilio VM is appended as plain messages into the SAME per-phone conversation store SMS uses. Audio webhook `POST /owner/voice/recording-done` (voice.py:329-355) and transcript webhook `POST /owner/voice/transcription` (voice.py:361-400) do `conv=_conv_get(norm) or _conv_new(...)` then `_conv_append(conv,'in','🎙️ Voicemail received. Listen: {rec_url}')` / `'📝 Voicemail transcript: …'`, set `status='needs_reply'` + `unread=True`. TwiML wiring = `_vm_block()` (voice.py:139-144, `<Record transcribe="true" transcribeCallback=…/transcription action=…/recording-done>`). Answered-call recordings use a sibling path `/owner/voice/recording-saved` (voice.py:844) → `📞 …`.
- Conv record = a JSON dict (`_conv_new`, sms.py:464-470: `norm,phone,name,partner_id,status,snooze_until,tags,priority,unread,draft,msgs[],last_ts,last_dir`); each msg (`_conv_append`, sms.py:472-485) = `{ts,dir,body,source,…}`. Backend = `ir.config_parameter wsc.sms.conv.{norm}` + index `wsc.sms.index`, OR Render Postgres via `sms_store` when `sms_store.pg_on()`.
- **A VM carries NO distinguishing source** — voice.py appends without `source=`, so it defaults to `source='text'` (even though an enum value `'voicemail'` exists in `_INBOX_SOURCES`, sms.py:496). VM-ness is detected by the 🎙️/📝 text + the `/owner/voice/rec?sid=` URL, NOT the source field. `has_textvm` (sms.py:412) treats text+voicemail as one home view.

**Surfacing:** `GET /owner/api/inbox/list` (sms.py:2384) → **v2_inbox.html** (the live inbox UI). Thread detail `GET /owner/api/inbox/thread` (sms.py:2672). Audio streamed (Range) by `GET /owner/voice/rec?sid=` (voice.py:407). Client distinguishes a VM by the rec-URL regex (v2_inbox.html:236,393), NOT a glyph/source. There is NO dedicated Twilio-VM tab. Each VM also `_notify(...)`s DJ.

**Reusable infra:** per-number VOICE blocklist `wsc.voice.blocklist` (voice.py:41, `_blocked()`, `/owner/voice/block|unblock|blocklist`) — ⚠ it only silences the RING; a blocked caller STILL records a VM (voice.py:167). SMS opt-out `wsc.msg.optout` (messaging.py:29). No spam/hide/archive flag exists; `STATUSES=('needs_reply','open','snoozed','done')` (sms.py:32). Per-number learning pattern = `ir.config_parameter` keyed (like the blocklist).

**⚠ Caller→customer resolver gap:** the VM/call path uses `_find_customer(phone)` (sms.py:693) which has **NO company_id filter** (can match a non-W&SC partner). The company-scoped resolver `_resolve_partner_by_phone(norm)` (sms.py:710, `company_id in [1,False]`) exists but is NOT used by the voice path. Any "is this a known customer?" bypass (e.g. spam filtering) should use `_resolve_partner_by_phone`, not `_find_customer` (rule 8 res.partner scoping).

**NOT this:** a SEPARATE manual flow exists — `/owner/api/voicemail/ingest|sweep_now|make_task` + `v2_voicemails.html` (myday.py:1146,1319) — DJ uploads a carrier-VM audio file, Whisper-transcribed → Odoo task. That's unrelated to the Twilio inbound pipeline above. Don't confuse them.

Related: [[project_inbox_compose_new_noncustomer]], [[feedback_reuse_canonical_endpoint]].
