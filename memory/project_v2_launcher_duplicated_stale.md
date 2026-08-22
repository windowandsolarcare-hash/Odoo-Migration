---
name: project_v2_launcher_duplicated_stale
description: "Every v2_*.html owner page hardcodes its OWN floating-🚀-launcher APPS[] list — 34 inconsistent copies (10-20 apps each). Canonical full list = v2_home.html GROUPS (~35 apps)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-24T08:05:42.057Z
---

**2026-07-22 (DJ: "what happened to the launcher? why did I have so many more programs before and now almost none").**

## Root cause
The floating 🚀 launcher on each **v2_*.html** owner page is populated from a `var APPS=[...]` array **hardcoded separately in every page**. There are ~34 copies and they're all different trimmed subsets (counted: 10–20 apps each), so the app list changes depending on which page you're on. This is NOT the old `ql_panel.js` launcher (that one runs on the ORIGINAL /owner pages — field.html, dashboard, etc. — and has its own ~17-app "Apps" menu + Shortcuts). The v2 pages do NOT load ql_panel.js.

## Canonical source of truth
`static/owner/v2_home.html` → `var GROUPS=[...]` (~line 395) = the full app directory, ~35 apps in 9 groups (Customers / Schedule & Dispatch / Sales / Marketing / Money / Team / Inputs / Reports / Tools & Links). v2_home ALSO has a tiny 4-app `APPS[]` (footer/nav) — the GROUPS array is the real directory, not that APPS.

## FIXED (durable, 2026-07-22) — shared file, DJ approved
Created **`static/owner/v2_apps.js`** = `window.WSCApps=[...]`, the SINGLE canonical list (~37 apps: Home + Command Center + all v2_home GROUPS items; Workiz/Odoo/Booking/Maps flagged `ext:true`). Then wired ALL 35 v2 pages: each page's `var APPS=[...]` replaced with `var APPS=(window.WSCApps||[]);` + a `<script src="/static/owner/v2_apps.js"></script>` tag inserted before the first `<script` (loads first, so WSCApps is defined before the inline launcher script runs). Batch script: `scratchpad/wire_launcher.py` (fetch→regex-replace→node --check→push, per file). All 35 pushed clean.

**To add/rename/remove a launcher app app-wide now: edit ONLY `v2_apps.js`.** No per-page edits.

## v2 (2026-07-23) — v2_apps.js is now a full launcher MODULE (data + UI), not just data
DJ wanted favorites/tabs/hide. Rather than paste that into 34 `renderLaunchList` copies (the very anti-pattern from [[feedback_question_when_big_picture_wrong]]), the RENDER LOGIC now also lives in `v2_apps.js`. It:
- exports `window.WSCApps` (registry; each app may set `fav:true` default-favorite, `hidden:true` never-show, `ext:true` new-tab).
- exports `window.WSCLauncher` {render, tab, star, open} — draws **★ Favorites / All** tabs, a per-app star toggle saved to `localStorage['wsc_fav_apps']` (seeded from `fav:true` defaults on first load), filter, hidden-respect.
- injects its own `<style id="wl-css">` once (classes `wl-*`), so no per-page CSS.
- on `DOMContentLoaded`, OVERRIDES each page's `window.openLauncher` + `window.renderLaunchList` → the module takes over every page with **zero per-page edits** (pages already load v2_apps.js + have #launch/#launch-list/#launch-filter). openLauncher resets to the Favorites tab each open (DJ: "Favorites first").
- Default favs (7): Command Center, Customer Brain, Stats, Inbox, My Day, Schedule Calendar, New Order.
- **Verified live in-browser 2026-07-23:** tabs switch, stars toggle + persist, star-tap doesn't navigate, no duplicates. Commit d03eb23.
- To add an app everywhere: one line in WSCApps. To hide one: add `hidden:true`. To change default favs: toggle `fav:true`.

## ★ Cache — FIXED server-side 2026-07-23 (was "can't see the launcher changes")
Root cause: StaticFiles served /static/owner assets with ETag/Last-Modified but **no Cache-Control**, so browsers heuristically cached `v2_apps.js` and kept the OLD launcher after edits (DJ: "can't see the changes in launcher").
**Durable fix (commit a0cd02d, main.py):** a `@app.middleware("http")` sets `Cache-Control: no-cache, must-revalidate` on any `/static/owner/*.js` and `*.html`. no-cache = browser caches but ALWAYS revalidates via ETag → cheap 304 when unchanged, fresh 200 when changed. So future launcher/page edits appear on the next normal load — NO manual hard-refresh, NO per-page ?v bumping needed going forward. Verified live: `curl -I .../v2_apps.js` now returns `Cache-Control: no-cache, must-revalidate`.
**One-time unstick:** also bumped the script tag to `v2_apps.js?v=2` across all 35 pages (new URL forces a fresh fetch past the already-cached copy). This was needed only because DJ's phone had cached the file under the OLD (no-Cache-Control) rules; with the header now live it won't be needed again. To break cache in future ONLY if ever necessary: bump `?v=N` — but the header should make that unnecessary.
Applies to ALL owner static assets, so any future "I don't see my change" on a v2 page should NOT recur.

## v2_apps.js also owns the shared header "‹ Back" button (2026-07-23)
DJ: "in all V2 screens put a back button in the header rather than the small arrow; screens with no back capability, put the back button." Added a 2nd IIFE to `v2_apps.js` (after the launcher one) that on DOMContentLoaded, for every `header .head-row`: finds the back-ish button (text `‹`/`←` or aria-label Back/Home), relabels it `‹ Back`, adds class `.wl-back` (auto-width pill, injected CSS), and rewires onclick → `window.WSCBack` = smartBack: `history.back()` only if in-app referrer + history>1, else Home (`/static/owner/v2_home.html`). If a header has NO back button, it INSERTS one. So every v2 page gets an identical labeled Back button from ONE file — no per-page edit. Verified live on Command Center, Stats, Home (Stats direct-load → Back went Home = the no-history fallback). Note: v2_home (the hub) also gets a Back button per "all screens" — Back there falls to Home/history. Commit 63cd438. Alphabetical launcher = commit 06b2b8a.

## Launcher DOUBLING on Home — the real "double entries" (fixed 2026-07-24)
DJ's "double entries" WAS real, only on **v2_home**: every app showed twice (a,a,b,b after the alpha sort). Cause: v2_home builds its own search/launcher index with `var APPS=(window.WSCApps||[]);` — a **reference**, not a copy — then `APPS.push(...)` extras + all GROUPS items, which MUTATED the shared `window.WSCApps` in place; its local `seen` dedupe only tracked its own additions, so it re-appended Customer Brain/Inbox/etc. that were already in WSCApps → WSCApps went 39→~78, and the shared launcher (reads window.WSCApps) doubled. Only Home did this (each page loads a fresh WSCApps). **Fix: `.slice()` to copy** — `var APPS=(window.WSCApps||[]).slice();` (commit b801b5e). ★ Any page that starts from window.WSCApps and pushes to it MUST `.slice()` first — never mutate the shared array.

## 3 pages were missing v2_apps.js entirely (fixed 2026-07-24)
v2_ai (Ask AI), v2_voice (Voice Assistant), v2_quick had NO launcher array, so the earlier batch skipped them → no shared script → old tiny ‹ arrow, no launcher, no standardized Back. Added the `<script src=/static/owner/v2_apps.js?v=2>` tag to all three (commits e2f31fa/a86685b/525d71b). Lesson: the batch keyed on `var APPS=[` — pages without a launcher were invisible to it.

## "Double entries" report (2026-07-23) — superseded (see above; it was Home)
DJ reported doubles. Live launcher on Command Center showed SINGLE entries (no dup in WSCApps; verified). Root cause was almost certainly (a) my own stale-copy regression on v2_field (I'd reverted its shared wiring in an unrelated push — re-fixed, commit 2bc7b2a) and/or (b) a cached old page on the phone. Hard refresh clears it.

## ★ FAB DRAG was never in the shared file — 4 newest pages had no drag (fixed 2026-07-30)
DJ: *"launcher doesn't float... I thought we corrected this. we agreed to have only ONE launcher
called by all screens. how did it become loose again?"* **It did not come loose — this dimension
was never consolidated.** What the July work moved into `v2_apps.js` was the app LIST, the panel
UI (favorites/tabs/filter), the CSS, the Back button, z-index and badges. What stayed per-page was
the **`<button id="fab-launch">` markup and its drag-to-move block** (~38 pasted copies). Drag was
added to v2_apps.js on 2026-07-27 (commit c079bbe) **only for the INJECTED path** — the message
literally reads "same behavior as native v2 FAB", i.e. two parallel implementations kept on
purpose, and `ensureLauncherDom()` early-returns (`if(document.getElementById('fab-launch')) return`)
on any page shipping its own button, so native FABs never got it.
**Who broke:** the 4 NEWEST v2 pages, all authored 7/24–7/25 (AFTER the consolidation) with the
simpler `class="fab"` + inline `onclick="openLauncher()"` pattern and no drag block —
**v2_goals, v2_workhours, v2_capacity, v2_journal** (audit signature: `id="fab-launch"` present but
zero `fabpos` matches). Their launcher rendered fine but was welded to the corner and ignored the
position DJ dragged to elsewhere.
**FIX (commit c3042010, ONE file):** extracted the drag IIFE out of `ensureLauncherDom()` into a
module-level `bindFabDrag(el)` (self-guarded by `el.__wlDrag`) and call it from `takeover()` for
whatever `#fab-launch` exists — injected OR native. Pages still carrying their own copy
double-bind **harmlessly**: both handlers derive the identical position from the same event, write
the same `wsc_v2_fabpos`, and `WSCLauncher.open()` is idempotent (`classList.add('open')`, not
toggle). **Verified live in-browser:** Goals FAB now drags + persists (696,190); that position
restored on v2_hud (own-drag page, click still opens once, 23 apps render) and on v2_workhours.
**LESSON — the audit to run when adding a v2 page:** `id="fab-launch"` present + `fabpos` absent =
that page has a dead launcher button. Better: new pages should ship NO fab markup at all and let
`ensureLauncherDom()` inject it. The ~38 per-page drag copies are now redundant and can be deleted
in a dedicated cleanup (not done — rule 10, they still work).
**Also ruled out (don't re-chase):** `html,body{overflow-x:clip}` on v2_goals was NOT the cause —
tested in-browser with and without; FAB stayed fixed either way.

## ★★ THE 39 DUPLICATES ARE GONE — launcher markup deleted from every page (2026-07-30, DJ ordered it)
DJ, correctly angry: *"we're discussing that we've created 38 duplicates... the drag function is
part of the launcher. Why would Claude Code leave 38 instances of a drag when we're talking about
eliminating 38 instances of anything?"* He is right, and it was the same mistake twice: the July
consolidation drew an arbitrary line around "the launcher" (list + panel UI) that excluded the
button and its drag, and then on 7/30 I fixed only the drag BINDING and again walked past the
copies. **Fix the duplication, not the symptom.**
**DONE (commit a3f07c0d, ONE atomic commit, 39 files):** deleted the per-page
`<button id="fab-launch">` AND `<div id="launch">…</div>` from all 39 pages that carried them.
`ensureLauncherDom()` in v2_apps.js now injects the FAB + panel + CSS + drag on EVERY page — the
exact path 5 pages (v2_ai, v2_quick, v2_voice, v2_schedule, v2_reminders) had already been running
on for weeks, which is what made this safe.
**Why deleting only the MARKUP was sufficient + safe (the key insight):** every page's leftover
launcher JS is already inert once the nodes are gone — the drag IIFE opens with
`var el=$('fab-launch'); if(!el) return;` (verified in all 34 that had it), and
`openLauncher`/`renderLaunchList`/`closeLauncher` are overridden by v2_apps.js's `takeover()` on
DOMContentLoaded (its listener registers first because the script tag sits before the page's
inline scripts). The `.fab`/`#launch` CSS just stops matching. So NO JS had to be touched in 39
files — the risky part was avoided entirely.
**Method worth reusing for any mass edit:** download all pages → scripted excision that REFUSES a
file rather than mangling it (3 files initially skipped = they use CRLF and the pattern only
allowed `
`; fixed with `?
`) → validate every output (tag-count parity for
script/style/body, balanced `<div>` removal, `node --check` on EVERY inline script block, assert
v2_apps.js still referenced) → **git Data API single commit** (blobs→tree→commit→update ref) so it
is one deploy and atomic, not 39 pushes → **drift guard** first: recompute each file's git blob
sha and abort if any changed upstream since download (protects against the other session).
Script: `scratchpad/strip.py` + `scratchpad/atomic_push.py`.
**Verified live in-browser after deploy:** 15 pages have fab=0/panel=0/appsjs=1; on v2_goals and
v2_hud the injected FAB exists, `position:fixed`, z-index 500, drag bound + working, position
persists across pages, launcher opens with 12 favorites / 46 apps, tabs + stars render, 0 console
errors. Screenshot confirmed.
**Rule going forward: a v2 page ships NO launcher markup at all.** Nothing to forget, nothing to
paste. If a launcher change is needed it happens in `v2_apps.js` and only there.
