---
name: project_owner_page_nostore_cache
description: "Owner HTML pages served via open().read() with NO Cache-Control get stale-cached on DJ's phone (PWA, no service worker = plain browser HTTP cache) so pushed changes don't show. Fix: return HTMLResponse(..., headers={'Cache-Control':'no-store, must-revalidate'})."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-30T19:42:16.303Z
---

# Stale owner pages on phone = missing no-store header (2026-07-30)

**Symptom:** DJ pushes a change to an owner static page, it's confirmed live server-side
(curl shows the new markup) but his phone still shows the OLD page — "can't get access to it."

**Root cause:** the app is an installable PWA but has **no service worker** (only
`static/manifest.json`, no sw.js). So caching is plain browser HTTP cache. Many owner routes in
dashboard.py serve pages as `return f.read()` with **no Cache-Control header**, so mobile
browsers heuristically cache the HTML and keep serving the stale copy.

**Fix (per route):** serve with no-store —
`return HTMLResponse(f.read(), headers={'Cache-Control': 'no-store, must-revalidate'})`.
Applied to `/quote` (and `/quote-rates` was built with it). The route-level header is the durable
fix; it makes every future load revalidate.

**Immediate unstick for an already-cached phone:** load the page once with a throwaway query
(`/owner/quote?fresh=1`) — a distinct URL the stale cache can't answer, so it fetches fresh. After
that one load the no-store header keeps it current.

**How to apply:** when DJ reports a pushed page not updating on his phone, first `curl -D -` the
route to check for `Cache-Control: no-store`; if absent, add the HTMLResponse+no-store header to
that route in dashboard.py (or whichever router serves it). Don't mass-edit every route at once
(repetition rule) — fix the one he's blocked on and offer the rest.
