---
name: project_google_places_location
description: "Add-to-schedule has a Location autocomplete (Google Places NEW API) — type address or business name → suggestions → full address. Key in Render GOOGLE_PLACES_KEY, proxied server-side."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**★ TWO Add-to-schedule sheets — BOTH got the Location field:** (1) field.html `#block-modal` (`openBlockModal`, main-schedule button L2047), and (2) **schedule_hub.html `#ab-modal`** (`openAddBlock`, the Command Center / "main schedule" — commit 6dae86f, `ab-loc` input + `abLocSuggest`/`abLocPick`). DJ first "didn't see it" because I'd only done field.html; his main schedule is the schedule_hub. Both post to the same `/api/schedule/add_block`. If adding another entry point, remember myday.html/calendar.html also have "Add to schedule" (handoffs).

**Feature (2026-07-13):** the field-app **Add-to-schedule** sheet (`#block-modal`, field.html) has a **Location** field — type an address OR a business name → live Google suggestions → tap one → it fills the full formatted address. DJ's own Google Maps key (he'd set it up long ago but nothing used it → "doesn't work" = never wired, not broken).

**Key facts:**
- Key stored in Render env **`GOOGLE_PLACES_KEY`** (added via update_environment_variables merge). DJ emailed it to windowandsolarcare@gmail.com (subject "Google places"); retrieved via Gmail MCP. NOT referrer-locked (works server-side).
- ⚠ Uses the **NEW Places API** (`places.googleapis.com/v1/...`). The **LEGACY** Places API (`maps.googleapis.com/maps/api/place/...`) is **NOT enabled** on this project → legacy calls return `REQUEST_DENIED "calling a legacy API"`. Always use the New API.
- **Server-side proxy** (key stays in Render, never the browser): `scheduler.py` (commit be8af6d) — `GET /owner/api/places/suggest?q=` (POST places:autocomplete, locationBias circle @33.75,-116.40 r90km, includedRegionCodes us → `[{desc, place_id}]`) and `GET /owner/api/places/details?place_id=` (GET places/{id}, FieldMask formattedAddress,location,displayName → `{address, name, lat, lon}`).
- Frontend `field.html` (01afd5f): `#block-loc` input `oninput=locSuggest` (debounced 250ms) → `#block-loc-sugg` dropdown → `locPick(i)` fills address. `submitBlock` sends `address`; `openBlockModal` resets it.
- `dashboard.py` `add_block` (17bf8f9): accepts optional `address`, appends `\n📍 {address}` to the Personal-Time block's notes so it shows on the schedule row.

⚠ **Gotcha that crashed the first deploy:** in the owner routers, `from .shared import *` does **NOT** bring `os` into the module namespace (shared limits its exports) — a module-level `os.environ.get(...)` throws `NameError: name 'os' is not defined` at import → Render deploy `update_failed` (app safely stayed on old code). FIX: add an explicit `import os` to any router that uses `os` at module level (scheduler.py commit 0aeeafa). `py_compile` does NOT catch this (os is a valid name at compile time). Same likely applies to other stdlib names not re-exported by shared.

**Personal-Time block address override (2026-07-13, dashboard.py commit 1825e40):** ★ ROOT ISSUE DJ hit — ALL Personal Time blocks share ONE partner **id 23054** whose address is DJ's stale home **"8401 Maruyama Drive, Hemet"**, so every block showed Hemet as the "customer address". FIX: add_block stores the entered address as a `📍 <address>` line in the SO's `x_studio_x_studio_notes_snapshot1`; `tool_get_schedule` builder sets `job['address'] = _pt_location(notes)` for Personal Time blocks (survives `/api/dashboard`'s `if not job.get('address')` guard → the field app shows it); `/api/dashboard` loop overrides `nav_addr = job['address']` (+ lat/lon 0 so it geocodes the entered address) so navigation goes THERE not Hemet; `_personal_time_desc` strips the `📍` line so it's not doubled. Helpers `_pt_location` + updated `_personal_time_desc` at dashboard.py ~L554. NOTE: 5 builders reference `_personal_time_desc` but only the tool_get_schedule one (feeds field app) got the address key — extend to others if those views need it.

**Still v1:** block address is stored/parsed from NOTES (no structured field, no stored coords — nav geocodes the address string). Map-pin uses the geocoded address. Optional hardening: restrict the key to Places API (New) only (API restriction, NOT app/referrer — server-side must keep working). "I don't see the field" = stale SW cache; refresh.
