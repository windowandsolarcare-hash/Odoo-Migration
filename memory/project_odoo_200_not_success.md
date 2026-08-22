---
name: project_odoo_200_not_success
description: "On this Odoo stack, HTTP 200 does NOT mean success — denied attachments serve placeholder.png (200), broken /terms serves an error page (200). Verify Odoo permission/route/access changes by response CONTENT (bytes/content-type), never status code alone."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-19T15:23:50.918Z
---

**On the window-solar-care Odoo stack, a 200 status can be a served error/placeholder page — status code alone lies.** Two confirmed instances:

1. **Denied attachment (2026-08-19):** after flipping 20 `ir.attachment` job photos to `public=False`, anonymous `GET /web/image/<id>/...` still returned **HTTP 200** — but Odoo serves `placeholder.png` (~6,078 bytes, `Content-Disposition: filename=placeholder.png`) on access-denied instead of a 403. Web verified the lock by CONTENT: 20/20 now return the 6KB placeholder, 0 return the real JPEG; a still-public file returns `image/jpeg` ~52KB. A status-code check would have reported "still public / success" wrongly.
2. **Broken `/terms` route:** returns HTTP 200 while serving an Odoo account-module error page (the reason a 301 rewrite didn't "fix" it).

**How to apply:** when verifying ANY Odoo permission / route / access / publish change, assert on **response body bytes, content-type, or a content marker** — never on the status code alone. `curl -s -o /dev/null -w '%{http_code} %{size_download} %{content_type}'` and check size/type, or grep the body for the expected marker vs. `placeholder.png` / error text. See [[project_company_filter_fails_open]] (same "verify for real, don't assume" theme) and the `/terms` notes.
