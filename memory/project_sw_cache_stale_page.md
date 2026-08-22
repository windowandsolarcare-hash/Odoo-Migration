---
name: project_sw_cache_stale_page
description: Field/owner app has a service worker (auth.py _SW_JS) that can serve a STALE cached page after a deploy — how to confirm + force-update
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

The Render field/owner app registers a **service worker** defined inline in `routers/auth.py` as `_SW_JS`. Page navigations are **network-first with a 3.5s timeout**, then fall back to the cached copy (so the app launches offline). On DJ's weak desert 5GE, a slow page fetch **loses the 3.5s race → serves the STALE cached page**, so a just-deployed change appears "not there" even though it's live.

**Cache name = `wsc-shell-v2`** (3 occurrences in auth.py: the activate keep-check + two `caches.open`). The activate handler deletes every cache key except the current name.

**When DJ says "I don't see it" after a confirmed deploy:**
1. **Verify the SERVER is serving it** (rules out a bad edit/wrong file) — `curl -s "https://wsc-field-assistant.onrender.com/<route>" | grep -c "<new text>"`. Most owner pages return HTML without auth. If >0, the code is live and it's purely a client cache issue. (Used 2026-07-10 for the GCal picker — server had it, phone didn't.)
2. **Confirm which file serves the route** — e.g. `/owner/command-center` → `static/owner/schedule_hub.html` (scheduler.py), NOT field.html. Same-named UI ("Add to schedule") can live in multiple files.
3. **Force-update = bump the cache version** `wsc-shell-v2` → `v3` (replace all 3 in auth.py, py_compile, push). New SW installs (skipWaiting + clients.claim), activate purges the old cache, every device re-fetches fresh. Did v2→v3 on 2026-07-10 (commit 532ad21).
4. **DJ's device:** after the auth.py deploy, fully close the app (swipe from recents) and reopen — first reopen fetches the new SW + purges old cache; may need one more reload. Quick one-off bypass: open the route with a throwaway query param (`?v=3`) — new URL = cache miss = forced network fetch.

**★ DURABLE AUTO-UPDATE FIX (2026-07-10, commit 607959c):** put SW auto-update logic at the TOP of `static/owner/ql_panel.js` (loaded by 31 of 36 owner pages — the single broadest include; `clockin-bar.js` = 22). It: registers `/sw.js`, calls `reg.update()` on load AND on `visibilitychange`→visible (catches PWA resume-from-memory, which does NO navigation so normally never checks), and reloads ONCE on `controllerchange` (guard `window.__swReloading`). Because the SW serves `/static/*.js` **network-first** + ql_panel.js has only ETag (no long max-age), the new ql_panel.js reaches the device on the next load, then force-pulls the newest SW/deploy and reloads to fresh. Pages that already had their own `controllerchange` reload (index/myday/schedule_hub) now have two handlers — harmless (reload is idempotent). ★ maintenance.html had NO SW registration at all, which is why its cards stayed stale the longest.

**Bootstrap:** the fix only starts working once the device loads the NEW ql_panel.js once — tell DJ to open any owner page with `?nocache=1` ONE time; after that it's automatic.

**Why:** stops the recurring "deployed but DJ still sees the old UI" loop for good. **How to apply:** always do step 1 (curl the live server) BEFORE assuming your push failed — the fix is usually the cache, not the code. See [[project_addschedule_gcal_picker]].
