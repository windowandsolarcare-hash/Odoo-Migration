---
name: project_nav_telemetry_and_a19_back
description: "Nav/timing telemetry (nav + slow_api beacons, /nav_stats) and the A19 shared Back handler default — both shipped 2026-09-23 in one client bundle"
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T18:56:08.933Z
---

**Two client systems shipped together 2026-09-23 (commit 7f74a217, SW cache v9).**

## Nav + timing telemetry (extends the existing client-telemetry system)
- `static/owner/wsc_telemetry.js` (`window.wscBeacon(step,o)` → POST `/owner/api/telemetry/beacon`) now emits, on top of the failure kinds, two new `kind`s:
  - **`nav`** — one per page load. `elapsed_ms` = ttr (time-to-usable-render, from the Performance API navigation entry — `domContentLoadedEventEnd - startTime`); `prev_page` = same-origin `document.referrer`; `nav_type` = navigate/reload/back_forward. Auto-fired by the lib on load (deduped once/load). These are full-page loads (each v2_*.html is its own page), so referrer IS the previous screen — no SPA route tracking.
  - **`slow_api`** — a SUCCESS-but-slow (>3s) fetch, via a **transparent global `window.fetch` wrap** in the lib. ★ Invariants (Lead + Dispatcher QC-gated — payment/messaging.send fetches pass through it): returns the ORIGINAL promise untouched; measures on a SEPARATE `p.then(onF,onR)` branch; reads ONLY `resp.status` (no body → no stream-lock); idempotent (`window.__wscFetchWrapped`); every measure/beacon step try/caught so it can NEVER throw into or alter the fetch; a wrapping-throw leaves `window.fetch` as-was. Reuse this pattern for any fetch-timing.
- Server: `telemetry_store.py` added promoted cols `prev_page` + `nav_type` (ttr reuses `elapsed_ms`) + `nav_stats(since_minutes)` (ttr p50/p95 per page + nav-transition PAIRS incl back-landings + slow_api offenders). Endpoint **`GET /owner/api/telemetry/nav_stats`** — NOTIFY_SECRET-gated in-handler (secret check FIRST, fail-closed 401), in `authz.py` PUBLIC_EXACT (cookieless fleet read), mirrors `/rate`.
- **Coverage:** `v2_apps.js` (on 46/57 v2 pages) injects `wsc_telemetry.js` if absent (rule-9, one owner). The 10 pages lacking v2_apps.js got a DIRECT lightweight `<script src=wsc_telemetry.js>` include — NOT v2_apps.js — deliberately, because **v2_apps.js auto-mounts the 🚀 launcher FAB on DOMContentLoaded**, so adding it to a recorder/QR-gate/stub would add an unwanted FAB (Option A, Lead-decided). FAB-on-every-page is a separate DJ design call. v2_schedule (redirect stub) skipped.
- Data stays in Render PG (`wsc_client_telemetry` on dpg-danl5vqjnfac7390g8g0-a), never Odoo. Render PG MCP `query_render_postgres` is READ-ONLY (can't DELETE test rows).

## A19 shared Back handler ([[project_two_quote_pages_two_launchers]] family)
- `wscBack` in `v2_apps.js` binds a capture-phase click listener (+`stopImmediatePropagation`) to any `[data-wsc-back]` element → so the attribute being PRESENT (even `""`) makes the shared handler fire and SUPPRESSES that element's own inline onclick (dead code). Same-origin in-app history → `history.back()`; cold-load → the `data-wsc-back` value, else the default.
- ★ 2026-09-23: the cold-load default changed **`v2_home.html` → `v2_hud.html`** (ONE edit fixed all 34 `data-wsc-back=""` Tier-C pages at once — rule-9, avoided 47 near-identical edits). The reported "Back → Field Day day-list" was NOT a hardcoded fallback (zero exist) — it was `history.back()` returning where DJ came from (v2_field no-param IS the live Field Day worklist, complementary to the HUD — kept, not retired; Lead option (a): accept history.back, no special-case).
- **Stragglers WITHOUT v2_apps.js** (telemetry-only) do NOT get the wscBack handler → a `data-wsc-back` on them is INERT; their INLINE onclick is the live mechanism. Fixed inline: maint_advance/maint_comms (hardcoded v2_home → v2_hud), meeting/memory (bare `history.back()` cold-dead-end → `history.length>1?back():v2_hud`).
- Deterministic per-page-declared-back (option b) is DEFERRED until the nav telemetry shows real back-landing patterns.

Related: [[feedback_question_when_big_picture_wrong]] (the rule-9 "don't grind 47 edits" call), [[feedback_verify_collection_and_live_pipe]] (the authz 401/200/gated-401 live proof), [[project_broad_except_swallows_odoobusy]] (next work: targeted Tier-1).
