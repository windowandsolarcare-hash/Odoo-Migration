---
name: project_cheryl_fab_launcher
description: "Cheryl-scoped 🚀 floating launcher (static/cheryl/launcher.js): a FAB on every /cheryl/ page opening a sheet of HER surfaces (Needs You/The Plan/Clients/Library/Documents-soon/Idea Board/Home). Self-contained IIFE; skips the /cheryl/ home. Injected centrally via with_cheryl_chrome (serve-time, clients/hud/plan) + a guarded self-load in the shared library.html/ideas.html. Served at /cheryl/launcher.js (cheryl/clients.py)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T16:36:23.805Z
---

**Built 2026-09-08 (DJ's strong idea from the Cheryl UX pass).** So Cheryl/DJ never hunt "which screen is this under," a 🚀 FAB sits on every /cheryl/ page and opens a sheet that jumps directly to her surfaces — a cheryl-scoped mirror of the ERP's v2_apps.js WSCLauncher, but lean (no favorites/drag/star).

**Component:** `static/cheryl/launcher.js` — a self-contained IIFE (own CSS, no deps, never throws). It (1) runs only when `location.pathname.startsWith('/cheryl')`, (2) SKIPS the /cheryl/ home (that IS the launcher), (3) injects a fixed 🚀 FAB (bottom-right, z-index ~2.1e9, brand #1e5aa8) + a bottom sheet. Surfaces are a single `APPS` array: 🔔 Needs You /cheryl/hud, 📅 The Plan /cheryl/plan, 👥 Clients /cheryl/clients, 📚 Library /cheryl/library, 📄 Documents (soon, disabled), 💡 Idea Board /cheryl/ideas, 🏠 Home /cheryl/. **Order/labels are Cheryl's to refine — it's just that array.**

**Served:** `GET /cheryl/launcher.js` (cheryl/clients.py) returns the file as `application/javascript`.

**Injected on all 5 cheryl surfaces (central, no shared-file forks):**
- `routers/cheryl/__init__.py` `with_cheryl_chrome(html)` = `with_backlink(html)` + inject `<script src="/cheryl/launcher.js" defer>` before `</body>` (idempotent).
- Applied at SERVE TIME in: `clients_page` (clients.html), `cheryl_hud` (DJ's v2_hud.html — never edited), `cheryl_plan` (Cheryl's plan-views.html wrapper).
- The SHARED `library.html` + `ideas.html` (served at BOTH /owner and /cheryl) get a **guarded self-load line** next to their LIB_BASE/IDEA_BASE detection: `if(location.pathname.indexOf('/cheryl/')===0){...append /cheryl/launcher.js}` — so DJ's /owner pages are unaffected.

**Verification:** deploy LIVE = the with_cheryl_chrome import + the /cheryl/launcher.js route registered cleanly; node-check passed on launcher.js + the two HTML edits. **Cheryl-COOKIE QC (FAB appears + navigates, absent on home, absent on /owner) is Lead's** — a Specialists session can't mint a cheryl session (see [[project_cheryl_ideas_delegation]] / [[feedback_verify_limits_before_declaring]]). Sibling: [[project_v2_launcher_duplicated_stale]] (the owner launcher — reason to keep this cheryl one a SINGLE shared file, not per-page copies).
