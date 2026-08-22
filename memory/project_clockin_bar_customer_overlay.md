---
name: project_clockin_bar_customer_overlay
description: "Why the mobile Customers tab hid under the clock-in bar, and the fix (ql_panel.js overlay was inset:0)"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Fixed 2026-06-09.** On a phone, opening the **Customers tab** (field.html) showed the tab bar/header hidden behind the orange clock-in bar — content "sitting too high."

## Root cause — NON-OBVIOUS
The mobile Customers view is NOT shown by field.html's own CSS/JS. `#office-panel` is `display:none` below 600px and nothing in field.html reveals it. **`ql_panel.js`** (the floating "+" quick-launch panel, loaded on every owner page) is what reveals it: when you tap its Customers shortcut on a phone (`window.innerWidth < 600`), it force-shows `#office-panel` as a **full-screen overlay** with `position:fixed; inset:0`.

`inset:0` = top:0 → the overlay sits under the clock-in bar (`clockin-bar.js`: fixed, top:0, height **36px**, z-index 2147483647). The bar's normal offset (body `padding-top:36px` + shrinking `#app`/`#field-panel`) does NOT reach a separately `position:fixed` overlay, so the tab bar was hidden. The schedule view was fine because `#field-panel` IS in the bar's offset.

## Fix
`ql_panel.js` — TWO identical spots (the `ql-cust-btn` click handler ~L549 and the deep-link `_tryOpen` ~L784):
- overlay: `inset:0` → `top:36px;left:0;right:0;bottom:0;padding-top:44px` (clears the 36px bar + reserves a strip above the tab bar)
- back button: was small `✕ Done` top-right `top:14px` (hidden under bar). Now a **prominent blue `‹ Back`** button, `top:42px;left:14px`, sitting in the reserved strip ABOVE the tab bar so it doesn't overlap the Stats/Customers/Voice tabs. Clicking it resets `office-panel.style.cssText=''` (back to display:none) → returns to the schedule. (2026-06-10)
- The mobile Customers tab is shown ONLY by ql_panel (office-panel is `display:none` <600px); these two spots are the only place it becomes a full-screen overlay.

## Lesson
The clock-in bar is **36px, fixed, top:0, max z-index**. ANY full-screen `position:fixed` overlay on an owner page must start at `top:36px`, not `top:0`/`inset:0`, or the bar covers its header. The bar's body-padding/`#app`-shrink offset only protects normal-flow content, not fixed overlays. Clock-in bar visibility has been a recurring trouble spot.

**RECURRENCE 2026-06-24 (new_job.html):** New Job (`/owner/new-job`) had `.hdr { position:fixed; top:0; z-index:100 }` → the clock-in bar covered the whole header, so the **‹ Back button was invisible** and only the bottom slivers of the 3 step-progress dots (`.sdot`, green when done) peeked out — DJ saw "3 green circles" and "no back button." Fix = `.hdr { top: 36px }` (commit 6ea7a19). **SWEEP CANDIDATE:** any owner page with a `position:fixed; top:0` header + clockin-bar.js has this bug — grep `position: fixed; top: 0` across static/owner/*.html headers. Same screen also got: date field opens on tap (showPicker, was appearance:none-broken — see [[feedback_ios_date_input_appearance]]), no-store header (new_job.py) so the phone stops serving stale pages, and next_job_line_items one-per-line.
