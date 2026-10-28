---
name: project_cheryl_hud_vs_launcher_two_homescreens
description: The "Cheryl App" home screen DJ/Cheryl use is saunders-render-app static/cheryl/index.html (the /cheryl/ Render HUD) — NOT cheryl-workspace launcher.html; two different launchers, easy to edit the wrong one
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-28T01:52:58.968Z
---

There are TWO "Cheryl launcher / home screen" files and they are easy to confuse (DJ explicitly flags this when asking for tile changes — "I mean the app, not the HTML launcher"):

1. **THE RENDER HUD (the real app DJ & Cheryl use daily)** = `saunders-render-app` → **`static/cheryl/index.html`**, served at **`/cheryl/`** (wsc-field-assistant.onrender.com/cheryl/). Title "Cheryl's Assistant". Its tiles are `<a class="hub-card card-XXX" href=...>` grouped into sections: **"The Cheryl App"** (Talk to Claude → claude session, Dashboard → /cheryl/hud, Tasks → /cheryl/tasks, Projects → /cheryl/goals, Ideas, Meeting, Voice Notes, Memory, WSC Hiring, HR, Shared-with-me), **"Real Estate"** (Clients), **"Personal"** (Library, Window SOP). Backed by `routers/cheryl/` (hud.py, tasks.py, goals.py, clients.py, documents.py, ideas.py, library.py, voicenote.py) + `static/cheryl/launcher.js`. **Tile anatomy:** `card-icon` (emoji) + `card-body` (`card-title` + optional `card-sub`) + `card-arrow`. Color accent per tile = a `.card-XXX { border-left: 4px solid <hex> }` in the base CSS, with an optional `@media (min-width:600px)` twin that flips to `border-left:none; border-top: 4px solid <hex>` (mirror `.card-ideas` for the clean both-layouts pattern). External links (artifacts/claude sessions) use `target="_blank" rel="noopener"`; internal use a bare `/cheryl/...` href.

2. **THE DECOY** = `cheryl-workspace` repo → **`launcher.html`** (title **"Cheryl's Apps"**). A standalone static page of artifact-link tiles (The Workbench, The Plan, Talk to Claude, Gift Book, Watch Log, Desert Route Book, Launch Runway, Print Pieces, The Numbers, The Runbook). It does NOT have the Dashboard/Tasks/Projects tile set. This is Cheryl's personal artifact-launcher, separate from the Render app. Editing THIS when DJ meant the HUD = the classic wrong-file burn.

**How to apply:** when asked to add/change a tile on "the Cheryl app" or "the home screen," edit **`static/cheryl/index.html`** in saunders-render-app. The tell: if DJ names tiles **Dashboard / Tasks / Projects**, it's the HUD (index.html). If ambiguous, grep both candidate files for the named tile set before editing. "Top-level tile, not nested under Projects" = a new `hub-card` inside the "The Cheryl App" section (siblings of the Talk/Dashboard/Tasks/Projects cards), not a child of /cheryl/goals. Specialists owns this (Cheryl app code). See [[feedback_builders_dont_sequence_or_defer]], [[project_two_quote_pages_two_launchers]] (same two-launchers hazard class).
