---
name: project_inbox_stale_sw_v2_no_update
description: "The 2026-09-22 inbox re-open: after the server 429 fix, DJ's inbox STILL failed (thread-switch fired no request) because his phone was stranded on an OLD cache-first service worker serving a stale JS bundle — the v2 SPA pages register/update the SW ZERO times (only login + legacy ql_panel.js do). Fix: v2_apps.js registers+updates /sw.js + guarded controllerchange→reload; bump SW cache wsc-shell-v4→v5. Incognito confirmed. Commit 92a9f32."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T23:31:25.177Z
---

**Inbox re-open = STALE SERVICE WORKER (2026-09-22, commit 92a9f32).** After the server-side Odoo-429 fix ([[project_inbox_odoo_429_threadpool_hang]]) DJ's inbox STILL failed: slow, and selecting a different person "wouldn't pull up" (thread-SWITCH). The log-vs-reality divergence (server logs clean, DJ's phone broken — TWICE) was the clue.

## Diagnosis (server healthy → it's the client)
- DJ's REAL requests (his IP, post-deploy instance) were ALL 200 incl. thread-SWITCHES to different people, zero 429/499/500. Server + current code both fine (the v2 list row is `onclick="openThread(norm)"` → fires `GET /owner/api/inbox/thread?c=`). So DJ's tap firing NO request = he's running STALE cached JS.
- **The service worker is LIVE** (not a zombie): served at **`/sw.js`** by `routers/auth.py` (`_SW_JS`, cache `wsc-shell-v4`, `Cache-Control: no-cache/no-store`, `Service-Worker-Allowed: /`). (History: it was `static/sw.js`, removed 2026-06-29, "logic merged into auth.py _SW_JS" — that's why a file/code search for sw.js misses it. Look in routers/auth.py.) The v4 SW is well-designed: network-first for navigations + `/static/*.js|css`, and it does NOT intercept `/owner/api/*` (why DJ's API calls always reach the server).
- ★ ROOT DEFECT: **the v2 pages (DJ's daily SPA — v2_inbox/hud/apps via WSCLauncher) register/update the SW ZERO times.** Only the login page + the LEGACY `ql_panel.js` register it (ql_panel even has `controllerchange → location.reload()`). So a v2-SPA user gets STRANDED on whatever SW they last had — if that's a pre-v4 cache-FIRST SW, it serves a stale bundle forever. Survives close+reopen (a SW persists independent of the page; only unregister / clear-site-data / a SW UPDATE clears it). DECISIVE TEST: incognito (no SW) worked → confirmed.

## Fix (2 files, atomic commit 92a9f32 — all 4 Lead gates passed)
1. **static/owner/v2_apps.js** (loads on EVERY v2 page = DRY): added the proven snippet — `navigator.serviceWorker.register('/sw.js')` + `reg.update()` on load AND on `visibilitychange` (PWA resume = no navigation = no auto-check) + a **guarded** `controllerchange → location.reload()` (`if(window.__swReloading)return; window.__swReloading=true;` — one-shot, no reload loop). Mirrors ql_panel.js.
2. **routers/auth.py**: bump `wsc-shell-v4` → **v5** (all 3 occurrences). v5 install=`skipWaiting`, activate=`clients.claim` + **delete all non-v5 caches** → wipes DJ's stale cache → network-first → fresh. DJ's relogin hits the login-page `register('/sw.js')` → browser pulls v5 (no-cache) → activate wipes cache → fresh; thereafter the v2_apps.js register self-heals so it never recurs.
- ★ Did NOT bump the per-page `?v=` on the `<script>` tags — that's the 34-page repetition trap ([[feedback_question_when_big_picture_wrong]]); the central v5 cache-wipe is the single-source freshness mechanism.

## Standing lessons
- **The SW lives in `routers/auth.py` as `_SW_JS`, served at `/sw.js`** (no static file). Cache name `wsc-shell-vN` — bump N (+ its 3 refs) to force a client update.
- **A v2-SPA screen that ships client JS MUST ensure the SW updates** — otherwise a phone strands on a stale bundle and NO server fix reaches it. v2_apps.js now does this for all v2 pages.
- **"Server 200s but the phone is broken, reopen doesn't fix it, logs ≠ reality" = a service-worker/cache problem** until proven otherwise. Incognito (no SW) is the decisive test.
- Snappiness after this = the separate per-load Odoo latency → the durable PG-persisted inbox-summaries follow-on (retire the in-proc stopgap), tracked as the SPEED item after FUNCTION was restored.
