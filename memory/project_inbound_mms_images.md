---
name: project_inbound_mms_images
description: Inbound MMS (picture texts) now captured + shown — sms_incoming reads NumMedia/MediaUrl, /api/sms/media proxies Twilio media (auth), thread bubbles render <img>.
metadata:
  type: project
---

**Was:** inbound picture texts were DROPPED — `sms_incoming` early-returned on empty Body (image-only MMS has no Body) and never read `NumMedia`/`MediaUrl`. Built 2026-08-06 (lead-assigned).

**Capture (sms.py `sms_incoming`):** read `NumMedia` (int) + `MediaUrl{i}`; early-return only if `not from_number or (not body and not media_urls)`. Threads `body_threaded` = caption (or '📷 Photo' if none) + one `/owner/api/sms/media?url=<urlencoded twilio media url>` line per image. `body` stays the caption for keyword/triage/reply logic; only the conv-append uses `body_threaded`.

**Proxy (sms.py `GET /api/sms/media?url=`):** Twilio media URLs need HTTP Basic auth (browser <img> → 401), so the inbox <img> points here; fetches with `httpx.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))` + streams back with the content-type. SSRF-guarded: url must `startswith('https://api.twilio.com/')` AND contain `/Accounts/<TWILIO_ACCOUNT_SID>`. DJ-facing/PROTECTED (his browser cookie loads the <img>) — no authz whitelist.

**Render:** `wsc_thread.js bodyHtml` detects the `/owner/api/sms/media?` path → `<a><img class="wsct-img"></a>` (+ any caption), mirroring the voicemail `<audio>` pattern — so it shows in the inbox thread AND job-detail/Customer-Brain Texts (all use WSCThread bubbles). `v2_inbox` list snippet shows "📷 Photo" for media (like "🎙️ Voicemail"). Emoji inbound already round-trips (UTF-8) — no change.

**Verified:** /api/sms/media rejects non-Twilio url (400); thread renders <img>. NOT end-to-end tested with a real inbound MMS (needs Twilio to POST one) — DJ verifies on the next real picture text.
