---
name: project_pwa_manifest_on_every_page
description: "PWA install showing Chrome shortcut icon instead of WSC icon — manifest must be linked on every entry page, not just login."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

The Render field app's PWA `<link rel="manifest" href="/static/manifest.json">` was originally only in `static/login.html` (the `/` route). Installing from the login screen produced a proper WebAPK with the WSC icon ("worked once"). Installing while already logged in on `/owner/` or `/tech/` produced a plain Chrome-badge bookmark shortcut — because those pages registered the service worker (`/sw.js`) but had no manifest link, so Chrome couldn't build a WebAPK.

Verified all the other pieces are fine: `static/manifest.json` valid; `static/icon-192.png` is real 192x192 PNG; `static/icon-512.png` is real 512x512 PNG; `/sw.js` served by `routers/auth.py` with a fetch handler + `Service-Worker-Allowed: /`.

**Fix (2026-06-06):** added manifest link + `apple-touch-icon` + `theme-color` to the `<head>` of `static/owner/index.html` and `static/tech/index.html`. Left `static/cheryl/index.html` alone — the manifest is WSC-branded ("Window & Solar Care") and would mislabel Cheryl's install; she'd need her own manifest.

**Why:** Chrome only generates a WebAPK (custom icon, no badge) when the page being installed from links a valid manifest with 192+512 icons AND has a service worker. Missing the manifest link on the install page = generic shortcut with Chrome badge.

**How to apply:** Any new top-level entry page (a page a user might "Install" from) MUST include the manifest link in its head, not just register the SW. Old shortcuts don't auto-upgrade — user must remove the shortcut and re-install. See [[project_render_app_architecture]].
