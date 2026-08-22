---
name: project_launcher_fixes_2026_07_25
description: "Two shared 🚀 launcher fixes in v2_apps.js (single source, all pages): (1) force #fab-launch z500 / #launch z600 so page pop-ups can't bury the launcher; (2) close the launcher on visibilitychange-hidden so a launcher left open doesn't reappear when you resume the app."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T20:39:54.258Z
---

Both fixes are in **v2_apps.js** (the shared launcher source loaded by every v2 page), so they apply everywhere from one place — NOT per-page (per-page z-indexes were a mess: fab 15–80, launch 40–100, sheets up to 200/6000).

**1. Launcher stays reachable over pop-ups (DJ 2026-07-25: launcher hidden behind the calendar day pop-up).** The 🚀 FAB sat at a lower z-index than page bottom-sheets, so an open sheet covered it. Fix: `ensureLauncherZ()` (called in `takeover()`) injects `#fab-launch{z-index:500!important}#launch{z-index:600!important}` — #id specificity + !important overrides every page's `.fab`/`.launch` class rule. 500 is above all normal sheets (≤~200) but below the focused WSCSnooze modal (z-9000), so the FAB is hidden during a snooze (clean) yet visible over ordinary pop-ups. Verified: FAB is the hit-test top element over an open calendar day-sheet.

**2. Launcher no longer reappears on app resume (DJ 2026-07-25: "this keeps coming up when I come back to the app").** Root cause: the launcher PANEL (`#launch`) was left open, and backgrounding the app (screen sleep / app-switch) RESUMES the webview without firing `pageshow` — so the existing pageshow-close handler never ran, and the panel was still open on return. It was staying open, NOT auto-opening (no code auto-opens it; only FAB click handlers call `openLauncher`). Fix: added a `visibilitychange` handler that removes `.open` from `#launch` the moment `document.hidden` — so leaving the app closes the launcher, and it's never showing when you come back. Verified: opened launcher → dispatched visibilitychange(hidden) → panel closed.

Note: v2_home.html has its OWN launcher impl (own `openLauncher`/`#launch`) but still includes v2_apps.js, so both shared handlers (pageshow + visibilitychange) apply to it too.

See [[project_launcher_back_bfcache]], [[project_wscsnooze_shared_module]], [[project_fixed_sheet_offscreen_headglow]].
