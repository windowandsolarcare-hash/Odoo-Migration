---
name: project_dan_cheryl_library
description: "Dan & Cheryl's Library — shared self-help content app built INTO the Render app (routers/owner/library.py + static/owner/library.html), Odoo-backed shared storage, server-side Anthropic Verify. Reachable at /owner/library, launcher, and Cheryl's hub."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-20T22:16:42.887Z
---

# Dan & Cheryl's Library (2026-07-20)

A private shared library where Cheryl saves self-help videos/screenshots from social
media and Dan browses them. DJ approved building it INTO the existing Render app (not a
new repo/subdomain) to avoid new API keys/infra — "once it's up we can break it off to
library.wscare.pro later." Personal-side mixing is fine.

**Files (repo windowandsolarcare-hash/saunders-render-app):**
- `routers/owner/library.py` — router, mounted `/owner`. Endpoints: `/library` (page),
  `/api/library/list|add|update|note|delete|verify|fetch_title`, `/api/library/image/{att_id}`.
- `static/owner/library.html` — dark-theme SPA (DM Serif Display + Inter). Identity picker
  (Dan teal / Cheryl gold) in localStorage `dclib_user` — NO PIN (app already gated; PIN is
  cosmetic here). Add panel (video link w/ server-side title fetch, or screenshot upload),
  library cards, Truth Meter, lightbox.
- Registered in `main.py` (import owner_library + include_router).
- Entry points: launcher `static/owner/ql_panel.js` (📚 row) + Cheryl hub
  `static/cheryl/index.html` (`.card-library` "Our Library" card).

**Storage (no new Odoo model):** one JSON blob in `ir.config_parameter` key **`dclib.data`**
= `{"entries":[...], "cats":[...]}`. Each entry: id, type(video|screenshot), url, imageAtt,
title, claim, category, addedBy(dan|cheryl), addedAt, watched, truth, notes[]. Screenshot
images are stored as **ir.attachment** (res_model='ir.config_parameter') and referenced by
attachment id — NOT base64 in the blob (keeps the param small). Served back via
`/owner/api/library/image/{id}` which reads `datas`+`mimetype`. Read-modify-write on each
mutation (low volume, races acceptable).

**Verify (Truth Meter):** server-side only. Browser CANNOT call api.anthropic.com directly
(CORS + would expose key), so `/api/library/verify` reuses `get_anthropic_client()` +
`CLAUDE_MODEL` (sonnet) with the `web_search_20260209` server tool, pause_turn loop, and a
JSON-only fact-check prompt (percent/summary/sources). Result cached on `entry.truth`.

**Why:** the original build-prompt (from another Claude) wanted a standalone static site with
browser→Anthropic calls and localStorage. Both are broken for the actual goal: a static site
can't proxy the API key and localStorage doesn't sync between two people. Backend + shared
Odoo store fixes both. See [[project_ask_ai_router]] (same Anthropic pattern reused).

**How to apply:** to change categories, edit DEFAULT_CATS in library.html. To spin it out to
its own subdomain later, the JS just needs the `/owner/api/library/*` calls repointed to the
Render app's absolute URL (CORS allow the subdomain).
