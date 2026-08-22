---
name: project_fixed_sheet_offscreen_headglow
description: "A position:fixed bottom-sheet renders with its RIGHT edge off-screen on phones when the PAGE has any horizontal overflow (e.g. .head-glow right:-40px). Page h-overflow widens the mobile layout viewport → the fixed sheet fills it. Fix: overflow-x:clip on html+body."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T18:29:47.394Z
---

**2026-07-25 (DJ: calendar day-sheet "not formatted correctly for my screen").** The day pop-up on v2_calendar.html rendered with its whole right side cut off on his phone — the ✕ close button, the week strip's Saturday cell, the "Nh free of Xh week" capacity line, and the action pills (Book a job / GPS / Google Cal) were all clipped at the right edge, and the pills did NOT wrap (a tell that the sheet was wider than the visible screen).

**Root cause (NOT the sheet's own CSS).** `.head-glow` is a decorative header element `position:absolute; right:-40px; width:220px` — it intentionally bleeds ~40px past the right edge. That gives the *page* ~40px of horizontal overflow (documentElement.scrollWidth 1465 vs clientWidth 1425 in test). On mobile, page horizontal overflow **widens the layout viewport**, and a `position:fixed; inset:0` element (the bottom sheet) fills the *widened* layout viewport, not the visible screen — so `width:100%`/`inset:0` resolves to device-width + the overflow, pushing the sheet's right portion off-screen. (Adding the header week-arrows `‹ › ✕` made it more noticeable but was NOT the cause.)

**What was NOT the cause (ruled out in-browser):** the sheet is a flex child of `.sheet-bg{display:flex}`, but `.sheet` has `overflow-y:auto`, which per spec computes overflow-x to `auto` too → its flex automatic-minimum-size is already 0, so it shrinks freely (measured min-content floor = 120px in a 120px container; no overflow at 320–380px container widths). So `min-width:0`/`overflow-x:hidden` on the sheet does nothing here — don't chase that.

**Fix (commit 980a087):** clip horizontal overflow at the ROOT so no decorative bleed can widen the mobile layout viewport:
```css
html{ ...; overflow-x:clip }
body{ margin:0; overflow-x:clip; ... }
```
Use `overflow-x:clip` NOT `hidden` — `clip` leaves `overflow-y:visible` (no scroll-container side-effects; sticky/fixed unaffected; nested overflow-x:auto scrollers like the month grid still scroll). Verified live after deploy: page h-overflow 0px, sheet fits a 360px container, ✕ visible, week strip fits (Sat no longer cut), pills wrap to 2 lines. Also made `.sheet-t` (sheet title) shrinkable (`flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap`) + `.sheet-h{gap:8px}` so a long weekday+date can never push the header arrows off — good hygiene once the arrows were added.

**Reusable rule:** if any v2 page's `position:fixed` overlay/sheet/bar renders with its right edge off-screen on a phone, the cause is almost always PAGE-level horizontal overflow (a decorative element bleeding past the right edge, an unwrapped wide row, negative margins), NOT the overlay's own width. Check `documentElement.scrollWidth > clientWidth` first; fix by clipping root overflow-x. See [[project_capacity_overview_screen]], [[project_clockin_bar_customer_overlay]].

**Blanket sweep 2026-07-25 (DJ approved).** `.head-glow` turned out to exist on ONLY v2_calendar.html (not "many pages" as first assumed). But to prevent this whole bug class proactively, added `html,body{overflow-x:clip}` (a dedicated rule inserted just before the first `</style>`) to **all 41 other v2_*.html** owner pages (every one that lacked it). Harmless everywhere — clip only trims content bleeding past the horizontal edge, leaves overflow-y visible, and nested horizontal scrollers (month grid, chip rows) still scroll. So any future decorative bleed / wide row on a v2 page can no longer push a fixed overlay off-screen. All 41 pushed + verified serving 200 with the clip. If a NEW page is created, include this line.
