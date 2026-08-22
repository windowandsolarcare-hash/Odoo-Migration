---
name: project_pwa_stale_page_reload
description: "ROOT CAUSE of \"fix deployed but DJ still sees old behavior on app resume\" — Android keeps the PWA page alive for days running OLD JS. Fixed 2026-07-26 - v2_apps.js reloads on resume after 30+ min hidden."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-07-28T22:49:07.628Z
---

DJ (2026-07-26, screenshot): "when I leave the app and come back, the launcher is the wrong launcher — I thought we addressed this." The launcher was the current WSCLauncher UI but with a stale app list (no HUD Feed) and stale-open state.

**Root cause — a THIRD staleness mechanism, distinct from the two known ones** (service-worker cached shell [[project_sw_cache_stale_page]]; no-store route caching [[project_owner_page_nostore_stale]]): **Android keeps the PWA's page alive in memory for hours-to-days. Resuming shows that old living page running the OLD JS it loaded days ago.** Deployed fixes never reach it — so every "launcher fixed" deploy worked for new loads but not the long-lived page DJ actually resumes into. (SW was NOT the villain here: .js/.css are network-first with no timeout-fallback; only navigations fall back to cache after 3.5s.)

**Fix (v2_apps.js, shared → all v2 pages):** on visibilitychange-visible, close #launch; if hidden ≥30 min AND navigator.onLine, `location.reload()`. Short app-switches stay instant; offline pages are never reloaded away. Also: NEW default-favorite apps auto-merge into wsc_fav_apps ONCE via a `wsc_fav_seen` ledger — user's deliberate un-stars stay removed.

**Why:** any "we deployed X but DJ still sees the old behavior after coming back to the app" report should suspect the living-page mechanism FIRST, before service worker or route caching.
**How to apply:** durable page-level fixes must live in v2_apps.js (loaded by every v2 page) so one deploy + one resume-reload cycle refreshes the fleet. Never diagnose resume-staleness by curling the server — the server was fine; the phone's in-memory page was old.

SUPERSEDED THE 30-MIN TIMER (2026-07-28, DJ still hit the "old screen on return" in the field — sleeps/app-switches far more often than 30 min): v2_apps.js now reloads on resume ONLY when a NEW BUILD shipped, not on a timer. `feed.py` exposes GET /owner/api/appver → {v: RENDER_GIT_COMMIT[:12] or import-time ts}; v2_apps.js `_checkVer()` reads it on load (baseline) + on visibilitychange-visible (reload if changed AND online). No deploy → no reload → field state preserved, instant app-switch. Bootstrap caveat: the CURRENTLY-alive stale page must load the new v2_apps.js once before the check is active. NOTE: import-time-ts fallback flaps across multiple instances — fine while this app runs 1 instance; if it scales out, RENDER_GIT_COMMIT must be set (it is, on Render).

ALSO (2026-07-26, "launcher is not there" on /owner/library): v2_apps.js now SELF-INJECTS the 🚀 FAB + panel (`ensureLauncherDom()`, fallback-color CSS) on any page lacking `#fab-launch` — so a NON-v2 page (library.html etc.) gets launcher + stale-page reload + Back normalization from ONE `<script src="/static/owner/v2_apps.js?v=2">` line before </body>. v2 pages keep their own markup (injection skips when #fab-launch exists). Never paste launcher HTML into a page again.
