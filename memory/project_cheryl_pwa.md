---
name: project_cheryl_pwa
description: "Cheryl's app is an installable PWA ('Cheryl — WSC', CJ icon) with its own web address cheryl.wscare.pro + independent login. Manifest + head-tag injection + icons — where they live."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T18:35:24.578Z
---

**Built 2026-09-12 (DJ-directed via Lead).** Cheryl's `/cheryl/` app installs to a phone home screen as a standalone PWA named **"Cheryl — WSC"** with the **CJ** icon, on its **own address `cheryl.wscare.pro`** for an independent login (host-scoped `wsc_session` cookie → separate login per host, the whole point). start_url/scope are host-RELATIVE `/cheryl/` so they work on whatever host serves them.

## Where the pieces live (app repo `saunders-render-app`)
- **`static/cheryl/manifest.webmanifest`** — name "Cheryl — Window & Solar Care", short_name "Cheryl — WSC", display standalone, portrait, theme_color `#1e5aa8`, background `#0f172a`, icons cj-192/cj-512/cj-512-maskable. Served PUBLIC (no login needed for the install fetch).
- **`routers/cheryl/__init__.py`** — `_PWA_HEAD` + `with_pwa_head(html)` inject the manifest link + `theme-color` + `apple-touch-icon` (cj-180) + `apple-mobile-web-app-capable/-title/-status-bar-style` + `mobile-web-app-capable` before `</head>`, idempotent, at SERVE TIME (never edits a static file). `with_cheryl_chrome` calls `with_pwa_head(with_backlink(html))` then adds the launcher — so every served /cheryl/ page is installable.
- **`main.py:352`** — `mimetypes.add_type('application/manifest+json','.webmanifest')` BEFORE the StaticFiles mount, so the manifest serves the correct content-type (verified live: 200 `application/manifest+json`).
- **Icons `static/cheryl/cj-{192,512,512-maskable,180}.png`** — currently **PLACEHOLDERS** (white "CJ" on `#1e5aa8`, maskable has a ~66% safe zone, generated with PIL). **Design replaces them with the real CJ monogram AT THE SAME PATHS** (matched to the ERP "AW" icon family) — no manifest/code change needed on swap. All 4 verified live 200 image/png.

## Gotchas
- New static files don't serve until Render redeploys (the manifest/icons 404 until the push's auto-deploy goes live; ~2 min). During a rolling deploy-swap an icon can flip 200→404→200 transiently — re-verify after deploys settle.
- Icons are BINARY: push via `[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes(path))` (raw bytes), not the UTF-8 text path.

Related: [[project_cheryl_talk_to_claude]], [[feedback_render_design_before_presenting]].
