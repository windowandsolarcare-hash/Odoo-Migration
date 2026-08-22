---
name: project_pwa_launch_to_dashboard
description: "PWA icon launch behavior — login.html always opens the dashboard hub, NOT the last-visited page (removed the resume-last-page trap)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-07: DJ reported tapping the PWA icon launched the field assistant in mic/voice mode with no exit (Android back just closed the app). Cause: `static/login.html` had an "instant redirect" that, for a valid session (`sbg_session`, 7-day TTL), resumed `localStorage['sbg_last_page']` instead of the dashboard. `sbg_last_page` is written by `static/owner/pwa-track.js` as just `window.location.pathname` (e.g. `/owner/field`), so every launch dumped him back into the field assistant. Back-button exited because the resumed page was the first/only entry in the PWA session history.

**Fix:** changed login.html instant-redirect to always `window.location.replace(s.redirect)` (the role hub: `/owner/` or `/tech/`), removing the resume-last-page logic. Now the icon always opens the dashboard hub. (Removed the `sbg_last_page` resume per DJ's explicit request "it needs to be launched to the dashboard." `pwa-track.js` still writes the key; nothing reads it now — harmless.)

Verified the field assistant (`static/owner/field.html`) does NOT auto-open voice: default tab is `stats` (activeTab='stats'); `openVoiceModal()` only fires from the `qlMic()` quick-launch button. The owner dashboard (`static/owner/index.html`) and `ql_panel.js` also don't auto-open the mic. So the mic-on-launch was purely the resume behavior, not an auto-open.

**Manifest facts:** `start_url` = `/` (login). login.html `/` route served by `routers/auth.py`. After login, `data.redirect` = `route_map[role]` = `/owner/` or `/tech/`, stored in `sbg_session.redirect`.

**Why:** PWA launch must land somewhere the user can navigate out of. Resuming a deep modal/tab state on launch creates an inescapable screen because there's no back-history in a fresh PWA session.

**How to apply:** Keep PWA launch landing on the dashboard hub. If resume-last-page is ever re-added, exclude voice/modal states and ensure a back/exit path exists. Related: [[feedback_removing_element_leaves_dangling_ref]], [[project_pwa_manifest_on_every_page]].
