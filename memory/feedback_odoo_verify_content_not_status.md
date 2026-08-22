---
name: feedback_odoo_verify_content_not_status
description: "On Odoo, HTTP 200 does not mean success — verify routes, permissions and access changes by response CONTENT, never by status code alone."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1cb095a1-10e5-4519-903e-c06b100b873a
  modified: 2026-08-19T15:25:10.017Z
---

**Odoo answers failures with HTTP 200 and an error/placeholder body.** A status-code check will
tell you something works when it does not. Verify by **body bytes, content-type, or a string you
expect in the content** — every time, for any route, permission or access change.

Two real cases, both caught only because the content was checked:

- **Denied `/web/image/<id>`** returns **200** with Odoo's `placeholder.png` (~6 KB,
  `Content-Disposition: filename=placeholder.png`), not a 403. After flipping
  `ir.attachment.public = False`, the URL still looked live. The tell is the filename/size, not
  the status. See [[project_marketing_site_odoo]].
- **A reserved route** (`/terms`) returns **200** while serving Odoo's *"HTTP Error"* template
  instead of the published `website.page`. See [[project_odoo_website_page_api]].

**Why:** every "is it fixed?" check on this stack is otherwise a false positive waiting to happen,
and on access changes a false positive means believing something is locked when it is still served.

**How to apply:** in sweeps, grep the fetched body for `QWebException` / `HTTP Error` and for a
string that only the *correct* page contains; for images compare `Content-Length` or the filename
against the real asset. `curl -o file -w "%{http_code}"` then inspect the file — never just
`-o /dev/null -w "%{http_code}"`.
