---
name: project_reactivation_book_scriptorder
description: Reactivation Book sheet time-picker broke only via New Order deep-link — route_map.js (defines WSCTime) loaded AFTER the inline init that auto-opens the sheet. Load libs BEFORE inline init.
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# Reactivation Book sheet "won't take a time" via CC New Order (fixed 2026-07-02)

**Symptom:** Command Center → New Order → Reactivation reply ("re-engagement" in DJ's words) → deep-links to `/owner/reactivation?book_lead=<id>`, which auto-opens the Book Job sheet. Picking a time did nothing — "won't take a time." The NORMAL path (open reactivation page, tap a Sent lead, tap Book Job) worked fine.

**Root cause (client-side load order):** The Book sheet time field `#bk-time` is a `<select>` populated by `WSCTime.fill()`. `window.WSCTime` is defined in `static/owner/route_map.js` (it also defines `WSCRouteMap`/`WSCDayPlan`). In reactivation.html, `route_map.js` was loaded at the BOTTOM, AFTER the big inline `<script>`. The inline init IIFE reads `?book_lead` and calls `showBookSheet()` during page load, which runs `if (window.WSCTime) WSCTime.fill(...)`. On the deep-link path that init could run before route_map.js executed → `WSCTime` undefined → guard skipped → the `<select>` got ZERO options → no selectable time → doBook's `if(!date||!time)` fired "Pick a date and time." Normal path worked because route_map.js had long since loaded by the time the user manually tapped Book.

**Fix:** Moved `<script src="/static/owner/route_map.js">` to load BEFORE the inline script (right before it, after Leaflet which it depends on). Now WSCTime/WSCRouteMap/WSCDayPlan are always defined before any init/auto-open. One-line move, no logic changed. Commit 68b5d59.

**Rule / how to apply:** Any owner page whose inline init can auto-open a sheet from a URL deep-link (`?book_lead`, `?contact_id`, `?sent_q`, etc.) MUST load its shared-lib `<script src>` deps (route_map.js = WSCTime/WSCRouteMap/WSCDayPlan) BEFORE the inline `<script>`, not at the bottom. Setting a `<select>`.value to a value with no matching `<option>` silently no-ops — an empty WSCTime select = time silently won't set. The slot times themselves are fine (`_all_slots()` in booking.py = 8:00/9:30/11:00/12:30/2:00/3:30, all on WSCTime's 6am–7pm 15-min grid). See [[project_reactivation_sent_book]] [[project_reengagement_vs_reactivation]].
