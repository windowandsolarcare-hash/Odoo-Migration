---
name: feedback_windows_curl_unicode_use_utf8_file
description: "On Windows, never inline non-ASCII (em dash, curly quotes, accents, emoji) in a shell curl POST body - write UTF-8 JSON to a file and --data-binary @file, or use python with utf-8."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9797b4b3-1353-4533-b46a-37589ecedab3
  modified: 2026-10-10T14:59:55.316Z
---

When POSTing non-ASCII text to the app from Windows (Git Bash curl), inline unicode in the command line gets sent as cp1252 bytes and the server returns a 500. It is a client-side encoding problem, not a server bug.

**Why:** 2026-10-10 seeding "TEST — Dial Check" on /owner/api/hiring/compare/extras returned a 500 with an em dash; the same call from Python with real UTF-8 passed 6 of 6 (server + DB are clean UTF8). Confirmed by Portal and Lead.

**How to apply:** write the JSON body to a UTF-8 file and `curl --data-binary @file.json`, or use Python (`json.dumps(..., ensure_ascii=False).encode('utf-8')` with a utf-8 Content-Type). Before blaming the server on a 500 with non-ASCII input, retest from Python. Related: [[feedback_odoo_verify_content_not_status]].
