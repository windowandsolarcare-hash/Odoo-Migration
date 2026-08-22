---
name: project_split_view
description: "Split View screen (built 2026-08-03) — two owner screens side by side in iframes for DJ's folding phone. static/owner/v2_split.html, reuses window.WSCApps, embed guards in v2_apps.js + clockin-bar.js."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-03T11:22:26.088Z
---

**DJ wanted two of his owner screens up at once on his folding phone** (instead of launcher-switching back and forth). Android split-screen can't reliably show two copies of the SAME PWA, so we built it IN the app.

## What it is
- **`static/owner/v2_split.html`** (NEW) — a host page: two panes, each an `<iframe>` of any internal owner screen, slim brand-blue header per pane: `<select>` picker, ⇄ swap, ⬌/⬍ orientation toggle, ⟳ reload, ⤢ maximize/restore. **DEFAULT = side by side (row).** Orientation is a USER TOGGLE (`wsc_split_orient`), NOT a media query — an early version keyed stacking to `max-width:720px` and DJ's fold reports <720 CSS px even when open, so it wrongly stacked (fixed 2026-08-03). **Maximize (⤢) is IN-PAGE** (`#wrap.max-L/.max-R` hides the other pane+divider; button flips to ⤡ restore) — it never navigates away, so you always get the split back with one tap (the first version's ↗ navigated `window.top` away with no return — DJ: "how do you get split back"). **Draggable divider** works both orientations. Persisted: `wsc_split_left/right/pct/orient`. Defaults L=HUD, R=Command Center.
- **Reuses `window.WSCApps`** (the canonical launcher registry, defined at v2_apps.js L12) — NO duplicated app list (rule 9). Pane pickers filter to internal embeddable screens: `!ext && !split && !hidden && href starts with '/'`. External apps (`ext:true` — Workiz/Odoo/Maps) are EXCLUDED because they block iframing (X-Frame-Options).
- Launcher tile added to WSCApps: `{ico:'🪟', t:'Split View (2 screens)', h:'/static/owner/v2_split.html', fav:true, split:true}` — the `split:true` flag also keeps it out of its own pane pickers.

## Embed guards (so panes stay clean) — both additive, `window.self !== window.top`
- **v2_apps.js `takeover()`**: if embedded (in a pane iframe) → return before injecting the 🚀 FAB/launcher chrome (shims still defined so nothing errors). Each pane would otherwise get its own floating FAB.
- **clockin-bar.js** (top of IIFE): if embedded → return, so the 36px clock-in bar doesn't stack in every pane.
- Same-origin iframes, so `window.self !== window.top` works without cross-origin throw; try/catch treats a throw as embedded.

## "Open Beside" — DJ's real flow (added 2026-08-03)
DJ's actual want: working on ONE full screen (fold closed) → unfold → tap one button → THAT screen becomes the left pane and a second opens on the right. The launch-a-blank-split-page flow didn't do that. So: **`window.WSCOpenBeside()`** (v2_apps.js) navigates to `v2_split.html?l=<current path>`; the split page reads `?l=`/`?r=` and seeds the panes (falls back to last-used/defaults). Two triggers (DJ chose BOTH): a floating **⧉ FAB** injected by v2_apps.js `ensureBesideBtn()` (fixed right, `bottom:88px` — just above the 🚀 FAB; skipped on the split page + when embedded), and a pinned **"Split with this screen"** row at the top of the 🚀 launcher list (hidden on split page + while searching). fillSelect prepends a synthetic option when `?l=` isn't a registry app href (so full screens not on the launcher, or ones with query strings, still load). Current-screen path saved as left, so it persists.

No backend changes — it just hosts existing screens live; each pane is a fully-interactive independent copy. See [[feedback_reuse_canonical_endpoint]] (reuse WSCApps not copy) + [[project_v2_launcher_duplicated_stale]].
