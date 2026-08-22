---
name: project_touch_ghost_click_bottom_sheet
description: "Phone gotcha: a tap that OPENS a full-screen bottom-sheet overlay fires a delayed ghost click ~300ms later at the same spot → lands on a row or the backdrop. Guard with pointer-events:none for ~380ms."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

# Ghost-click kills tap-to-open bottom sheets on mobile (fixed 2026-07-14)

**Symptom (DJ, My Day ⋯ menu):** "sometimes it goes to Add to schedule, most time nothing." A tap on a button that opens a full-screen `position:fixed` overlay would either do nothing or trigger the first menu row.

**Cause:** on touch, after `touchend`/`pointerup` the browser fires a synthesized **`click` ~300ms later at the original touch coordinates**. If `pointerup` opened an overlay, that delayed click lands on whatever is now under that spot:
- task high on screen → click hits the **backdrop** → menu closes instantly = "nothing"
- task low on screen → the spot now overlaps the sheet's **first row** → fires "Add to schedule"

**Fix:** when opening the overlay, set `overlay.style.pointerEvents='none'`, add the open class, then `setTimeout(()=>overlay.style.pointerEvents='', 380)`. The ghost click passes through harmlessly; the sheet becomes interactive right after. (Belt-and-suspenders: also don't rely on the touch's own click.)

**Second bug, same feature:** the ⋯ is dual-purpose (tap=menu, press-drag=reorder) via a movement threshold in `attachDrag`. **6px was too tight** — a normal fat-finger tap moves >6px → misread as a drag → onTap never fires = "nothing." Raised to **11px**. Any tap-vs-drag threshold on a phone button should be ~10-12px, not 6.

**Rule for future phone UI:** any "tap opens a fixed/overlay sheet" needs the ghost-click guard, and any tap-or-drag handle needs a generous (~11px) slop threshold. Fits [[CLAUDE.md]] rule 13 (phone edge cases). Applies to field.html job ⋯ menu, schedule sheets, etc.
