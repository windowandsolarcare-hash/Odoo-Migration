---
name: project_pointerup_open_ghost_click
description: "Opening a menu/sheet in a pointerup handler behind a full-screen backdrop self-closes on touch — the browser's synthesized ghost-click hits the backdrop. Guard with an openedAt<400ms check + preventDefault."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T14:55:27.728Z
---

**A tap that OPENS a full-screen overlay from a `pointerup` handler will instantly self-close on touch devices** unless you defeat the ghost-click. Burned 2026-09-09 on the Cheryl FAB launcher (`static/cheryl/launcher.js`) after making it draggable: I moved "open the sheet" into `pointerup` (to distinguish tap from drag). On touch, the browser fires a SYNTHESIZED `click` ~300ms after the tap at the same coordinates — by then the full-screen `#cl-sheet` backdrop is open, so that ghost-click lands on the backdrop → the backdrop's tap-to-close handler fires → the sheet opens then instantly closes = a "flash," launcher unusable. DJ: "continues to flash when pressed, can't access the launcher." `setPointerCapture` makes it worse.

**The fix (three parts, all needed):**
1. In `open()`, record `openedAt = Date.now()` (module-scoped).
2. In the backdrop/overlay click handler, FIRST line: `if (Date.now() - openedAt < 400) return;` — swallow the ghost-click that immediately follows the opening tap. (Backdrop-tap-to-close still works after the window.)
3. In the `pointerup` tap branch (the one that calls `open()`), `e.preventDefault()` to suppress the synthesized click where the browser honors it.

**How to apply / when it bites:** ANY time you open a modal/sheet/menu from `pointerup` (or `touchend`) AND that overlay has a backdrop or any element under the tap point with its own click-to-dismiss — the synthesized click re-triggers it. The `openedAt`-window guard is the robust fix (works regardless of `setPointerCapture`). Alternative (open on native `click`, skip when a `moved` drag flag is set) works too but verify `setPointerCapture` still lets the click fire. Root pattern: distinguishing tap-vs-drag on `pointerup` is correct, but the open-action must be ghost-click-protected.

See [[feedback_disable_pull_to_refresh]] and the phone-edge-cases rules (double-tap/timeout) in CLAUDE.md.
