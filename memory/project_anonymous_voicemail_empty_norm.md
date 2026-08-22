---
name: project_anonymous_voicemail_empty_norm
description: "Anonymous/blocked-caller voicemails are keyed under the EMPTY norm ('') in the inbox. inbox_status's `if not c` guard rejected empty c → Done/Snooze silently failed on those VMs. Fixed by dropping `not c` (conv-existence is the real guard)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-15T18:30:42.328Z
---

**Symptom (DJ 2026-08-15):** an inbox voicemail from "Unknown (Anonymous)" (Aug 13) — tapping **✓ Done** (or Snooze) did nothing; the card wouldn't clear. Viewing/playing the VM worked fine.

**Root cause:** Twilio sends `From='Anonymous'` for a blocked caller ID. In `voice.py` voicemail-saved handler, `norm = _norm(caller)` strips non-digits → `''` (empty). The conversation is stored under the **empty-norm key** `ir.config_parameter wsc.sms.conv.` and surfaced with name "Unknown (Anonymous)". The thread view works because `/api/inbox/thread` just does `_conv_get(c)` (finds the empty-key conv). But `POST /api/inbox/status` (sms.py, powers markStatus Done/Snooze) opened with `if not c or status not in STATUSES: return bad status` — **empty string c is falsy → rejected before it ever looked up the conv.** Frontend `markStatus` (v2_inbox.html) ignores `r.ok===false`, so it failed silently → "Done doesn't do anything."

**Fix (commit sms.py 2d18118):** dropped the `not c` from the guard → `if status not in STATUSES: ...`. The very next `conv = _conv_get(c); if not conv: return 'not found'` is the REAL existence guard (handles c=None/missing safely too: `_conv_get(None)`→None→not found). So empty-norm anonymous VMs are now actionable; genuinely-missing convs still rejected.

**Notes:** ALL anonymous/blocked VMs collide into the one empty-norm thread (a rolling "Anonymous" bucket) — acceptable (can't tell blocked callers apart anyway; a new anonymous VM re-opens the bucket to needs_reply). Did NOT redesign the keying (surgical). You can't text back a blocked number, so Done/Snooze are the only actions needed — both go through inbox_status, so this one fix covers both. General gotcha: any inbox endpoint guarding `if not c` will mis-reject the empty-norm anonymous conversation — use conv-existence, not truthiness of the key. Related: [[project_ai_rewrite_grounding]] (same file family, sms.py inbox).
