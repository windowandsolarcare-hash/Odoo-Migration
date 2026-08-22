---
name: project_calendar_photo_viewer
description: "Schedule Calendar photo lightbox — lowered ✕ below the clock-in bar + Save-photo download named by customer. Also: field.html's hist-lightbox opener is MISSING (broken)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

# Calendar photo viewer — ✕ position + download (2026-06-18)

DJ views a scheduled job's photos via **Schedule Calendar** (`/owner/calendar`): tap a day → job → `openHistModal` → photo grid (`.hist-thumb`) → tap a photo → `openHistLb(src)` opens `#hist-lightbox` full-screen. The viewer lives in **`static/owner/calendar.html`** (the WORKING one).

**Fixes shipped (commit f17ce5c):**
- **✕ was at `top:16px`** → behind the fixed 36px clock-in bar (max z-index), so it was covered. Moved `#hist-lb-close` to **`top:52px`** (+ `z-index:2`). Same clock-in-bar overlay rule as [[project_clockin_bar_customer_overlay]]: any fixed top-anchored control must clear 36px.
- **Added `#hist-lb-dl` "⬇ Save photo"** button (bottom-center). `downloadLbPhoto()` fetches the current image (`_lbSrc`, same-origin `/owner/api/attachment_image` → blob) and downloads it named by the customer: `{_histCustomer}.jpg`, with ` (n)` suffix for additional photos in the session so they don't overwrite. Falls back to `window.open(src)` (long-press save) if the blob fetch fails. Buttons + the img use `event.stopPropagation()` so taps don't trigger the backdrop's `closeHistLightbox()`. `_histCustomer` is set in calendar.html `openHistModal` (= `d.so.customer`).
- "Photos I select to share" = open each photo + tap Save (reliable per-photo on mobile; batch multi-download is unreliable on phones).

## field.html lightbox was BROKEN — now FIXED (commit a83319a, 2026-06-18)
`static/owner/field.html` had the SAME `#hist-lightbox` markup + CSS and rendered photo thumbnails with `onclick="openHistLightbox(this.src)"` in BOTH `openSoFull` AND `openHistModal` — but **`openHistLightbox` / `closeHistLightbox` were NEVER DEFINED** (not in field.html, not in any loaded JS). So tapping a photo in the FIELD app's customer/job history threw ReferenceError → nothing opened. DJ said fix it. **Fixed:** defined `openHistLightbox(src)` / `closeHistLightbox()` (use field.html IDs `#hist-lightbox-img` / `#hist-lightbox-close`), lowered `#hist-lightbox-close` to `top:52px` (+z-index:2), added `#hist-lightbox-dl` "⬇ Save photo" + `downloadLbPhoto()` (blob fetch → `{_histCustomer}.jpg`, ` (n)` suffix), `event.stopPropagation()` on close/img/dl. `_histCustomer` global (field.html line ~3741) set in `openHistModal`; for `openSoFull` it falls back to whatever `_histCustomer` last held → 'photo'. Both viewers (calendar.html + field.html) now identical. [[project_community_pass]]
