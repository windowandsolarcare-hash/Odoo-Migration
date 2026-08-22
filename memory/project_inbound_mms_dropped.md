---
name: project_inbound_mms_dropped
description: "Inbound MMS (picture texts) are DROPPED — sms.py sms_incoming early-returns on empty Body and never reads NumMedia/MediaUrl, so image-only texts vanish and images are lost even with a caption. Emoji inbound works fine. Fix routed to specialist 2026-08-05."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T06:42:45.449Z
---

**DJ 2026-08-05:** had someone text him an image → got NOTHING.

**Root cause — `sms.py` `sms_incoming` (L971):**
- `body=(form.get('Body') or '').strip(); if not from_number or not body: return 200` → an **image-only MMS has empty Body → early-returns → dropped entirely.**
- Handler never reads `NumMedia` / `MediaUrl{i}` / `MediaContentType{i}` → images lost even when there's a caption (only the caption text threads).

**Fix (specialist lane, sms.py inbound + v2_inbox thread):**
1. Read `NumMedia`; if >0 don't early-return on empty body; capture MediaUrl/ContentType per media; thread an inbound msg carrying the media (marker "📷 Photo" + store URL).
2. **Display needs a PROXY:** Twilio media URLs (api.twilio.com/.../Media/...) require HTTP Basic auth (AccountSID:AuthToken) → browser `<img>` gets 401. Add `GET /owner/api/sms/media?...` that fetches with Twilio creds + streams the image; v2_inbox thread renders `<img>` at the proxy. Mirror the existing voicemail-audio embed (`_txtBody` → `<audio>`). Proxy is DJ-facing → leave PROTECTED (his browser is authed).

**Emoji INBOUND works — no change.** Twilio delivers UTF-8 Body incl. emoji; stored via `_conv_append`→`json.dumps` (round-trips) → displayed via esc() (passthrough). DJ asked; answer = yes he'll see them.

Mailed specialist 2026-08-05. Real gap (customers send job-site photos). See [[project_inbox_hides_done_outbound.md]].
