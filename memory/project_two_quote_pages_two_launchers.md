---
name: project_two_quote_pages_two_launchers
description: "TWO window-quote pages exist: OLD quote.html (route /owner/quote, old ql_panel.js single-column launcher) and CURRENT v2_quote.html (/static/owner/v2_quote.html, opened by the v2 WSCLauncher ★Favorites/All tabs). DJ's daily launcher opens v2_quote.html. Edit BOTH or you edit the one he doesn't use."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-30T20:00:24.857Z
---

# Two quote pages, two launchers (2026-07-30)

Burned during the editable-quote-prices work: I added the "Edit prices" link to `quote.html`
but DJ didn't see it from his launcher — because his launcher opens a DIFFERENT quote page.

**The two quote pages (both fetch `/owner/api/quote/rates`):**
- `static/owner/quote.html` — OLD. Served by route **`/owner/quote`** (dashboard.py). Its launcher
  is the old single-column `ql_panel.js` (💲 "Quote" row → `/owner/quote`). Also had /tech ROLE
  handling. This is the one my `?fresh=1` link opened.
- `static/owner/v2_quote.html` — **CURRENT, what DJ uses.** Opened directly at
  `/static/owner/v2_quote.html` by the **v2 WSCLauncher** (`v2_apps.js`, the ★Favorites / All
  two-tab floating 🚀 launcher): `{t:'Window Quote', h:'/static/owner/v2_quote.html'}`.

**The two launchers (this is the "different-looking launcher" DJ noticed):**
- `ql_panel.js` = OLD single-column quick-launch panel (voice "Commands" tab). Sits on old pages
  like quote.html. Links Quote → `/owner/quote`.
- `v2_apps.js` WSCLauncher = the NEWER 🚀 FAB with **★Favorites / All** tabs, per-device favorites
  in localStorage `wsc_fav_apps`. This is DJ's regular launcher. Links Window Quote → v2_quote.html.

**How to apply:** any change to the window-quote UI (links, fields, pricing display) must go in
**v2_quote.html** (the live one) — and decide whether the old quote.html still needs it. When a
"pushed change not showing" report involves a page that has an old + v2 twin, check WHICH file the
launcher DJ uses actually opens before assuming cache. Open question for DJ: retire the old
quote.html + ql_panel Quote link so there's ONE quote page to maintain. See
[[feedback_question_when_big_picture_wrong]] (duplication = stop & ask).
