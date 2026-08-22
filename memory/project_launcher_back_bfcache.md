---
name: project_launcher_back_bfcache
description: "After using the 🚀 launcher to navigate, Back landed on the launcher (not the page before it) — because bfcache restored the prior page with the overlay still .open. Fixed: close #launch on pageshow in v2_apps.js."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T15:37:16.369Z
---

**2026-07-24 (DJ: after I use the launcher to get somewhere, Back takes me back to the launcher — I want the page I was on before I opened it).**

**Root cause (NOT history/pushState):** The launcher is a pure overlay — `WSCLauncher.open()` just adds `.open` to `#launch`; app rows are plain `<a href>` full navigations, no pushState anywhere. So `history.back()` DOES return to the prior page. The bug is the browser's **back-forward cache (bfcache)**: when you tap an app, the overlay is still `.open` as the page unloads, and bfcache restores that page *exactly as left* — launcher still showing. So Back appears to land on the launcher.

**Fix (v2_apps.js):** a `window.addEventListener('pageshow', …)` that removes `.open` from `#launch` on every show (first load is a no-op; bfcache restore closes the leftover overlay). One handler in the shared module covers all v2 pages. No change to smartBack/WSCBack.

**Reusable gotcha:** any full-screen overlay left open when the user navigates away will be restored open by bfcache on Back. Close such overlays on `pageshow`, not just on click. See [[project_v2_launcher_duplicated_stale]].

**Recurred + hardened 2026-07-25 (commit e85fa30):** DJ still landed on the launcher after Back "sometimes" (e.g. Capacity→Command Center). Browser repro showed the pageshow handler DOES fire and close it — so it's device/timing-flaky (real Samsung bfcache differs from automated test). Added belt-and-suspenders: the launcher app-row `<a>` now closes the launcher `onclick` (removes `.open`) BEFORE navigating, so the page is never bfcache-saved with it open. The ★ favorite button already `stopPropagation`s, so favoriting doesn't close it. Both mechanisms now cover it.
