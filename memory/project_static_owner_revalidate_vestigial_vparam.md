---
name: project_static_owner_revalidate_vestigial_vparam
description: "main.py _owner_assets_revalidate middleware stamps Cache-Control: no-cache, must-revalidate on EVERY /static/owner/*.js|*.html, so a changed static asset (e.g. v2_apps.js) is auto-fetched fresh via ETag on the next visit — the '?v=N' query cache-busters (?v=2 on 49 pages) are VESTIGIAL. Do NOT mass-bump ?v= when editing a static owner asset; it's unnecessary churn. Verified live 2026-10-11."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T06:37:05.052Z
---

# Static /static/owner/* already revalidate — the `?v=` cache-busters are vestigial (verified 2026-10-11)

**The question that keeps coming up:** "we changed `v2_apps.js` (or another `/static/owner/*.js|.html`) but the page references it as `?v=2` and nobody bumped the cache-buster — won't repeat-visitor phones serve stale launcher JS? Should we bump `?v=` across all the pages?" **Answer: NO — the bump is not needed, and a 49-file bump is pure churn (rule-9 mass-dup trap).**

**Why (the mechanism):** `main.py` has a dedicated middleware **`_owner_assets_revalidate`** (~lines 999-1005, added 2026-07-23 for the exact "can't see the launcher changes" problem) that sets `Cache-Control: no-cache, must-revalidate` on the response for **every** path under `/static/owner/` ending in `.js` or `.html`. `no-cache` (NOT `no-store`) = the browser MAY cache but MUST revalidate every load via ETag → a cheap **304** when unchanged, a fresh **200** when the file changed. The `/static` StaticFiles mount (`app.mount("/static", StaticFiles(...))`) emits ETag + Last-Modified, so revalidation works. Net: a changed static owner asset is picked up on the **next visit** regardless of the `?v=` value.

**Verified LIVE 2026-10-11** on `https://wscare.pro/static/owner/v2_apps.js?v=2`:
- `Cache-Control: no-cache, must-revalidate` + `etag: W/"..."` + `last-modified` = that deploy's time.
- `cf-cache-status: DYNAMIC` → **Cloudflare does NOT edge-cache it** (passes to origin), so the CDN-ignores-must-revalidate caveat doesn't apply here either.
- Revalidation proof: `curl -H 'If-None-Match: <etag>'` → **304 Not Modified**. Change the file → ETag differs → fresh 200.

**Evidence it's genuinely vestigial:** `?v=2` has sat UNCHANGED across 5+ `v2_apps.js` edits (migration-cleanup stale-draft 2026-10-11, Candidate Compare tile 2026-10-10, App Building hub 2026-09-27, Ship Board, Capture tile…) with zero stale-launcher reports since the middleware landed in July. 49 owner pages reference `v2_apps.js?v=2` uniformly.

**The service worker does NOT reintroduce staleness for JS (checked the same session).** There IS a SW (`routers/auth.py` `_SW_JS` served at `/sw.js`, cache `wsc-shell-v10`, registered by v2_apps.js — see [[project_inbox_stale_sw_v2_no_update.md]]), but its `fetch` handler is **network-first for `.js`/`.css`**: `if(_code){ return (await netP) || cached }` (comment: ".js/.css change on deploy -> must be fresh"); only images/fonts are stale-while-revalidate, and page navigations are network-first with a 3.5s offline fallback. So a changed `v2_apps.js` is served fresh at BOTH layers — HTTP (no-cache + ETag revalidation) AND the SW (network-first) — falling back to cache only when truly offline (correct: the app launches offline, self-heals online). Net: no `?v=` bump needed at any layer.

**How to apply:** when editing ANY `/static/owner/*.js|*.html`, just push the file — do NOT bump `?v=`, and do NOT worry about stale launcher JS; the middleware handles freshness. (If someone ever wants belt-and-suspenders content-hashed assets, that's a build-step change, never a manual 49-file `?v=` bump.) Distinct from [[project_owner_page_nostore_cache]] — THAT is per-route HTML served via `open().read()` in dashboard.py with no header (needs a route-level `no-store`); THIS is the blanket middleware over the `/static` mount. See also [[project_sw_cache_stale_page]], [[feedback_question_when_big_picture_wrong]], [[feedback_verify_limits_before_declaring]].

**Tangent (same session):** a one-off report of DJ's `v2_home.html` home screen rendering stripped (clock stuck `--:--`, only the static Schedule card, no worklist tiles/module cards) was NOT a cache or deploy issue — v2_home.html was unchanged since 2026-09-09, its worklist endpoints all use a try/catch `jget()` (10s abort + `if(d)` guards) and the clock `tick()` runs before any fetch, so a backend can't blank it. Signature = an interrupted document/JS load over flaky signal; it self-healed on reload. Read-only page, nothing harmed.
