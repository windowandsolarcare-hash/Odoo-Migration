---
name: project_schedule_command_perf
description: Command Center (v2_command.html) ~9s slow-open — root causes + the A/D/G1/G2 fixes shipped 2026-09-25; cache-first already exists via cjson/IndexedDB.
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-25T19:22:36.571Z
---

The Command Center "On the schedule" (v2_command.html + dashboard.py builders) opened in ~9s. Full diagnosis + fix in `4_Reference_Data/SCHEDULE_SLOWLOAD_FIXPLAN_2026-09-25.md`. Fixed 2026-09-25 (Specialists, Lead-directed, DJ governing principle). Key durable facts:

**Cache-first ALREADY EXISTS — do not rebuild it.** `cjson(url,keyOverride)` (v2_command.html) serves the cached copy from **IndexedDB** instantly + kicks a background network revalidate; `refreshCC()` / `pageshow` / `visibilitychange` are all wired cache-first. It covers every cjson-wrapped call. The 9s was NOT a missing render — it was (a) all ~12 calls still FIRING on open and (b) the cold first-open-of-day.

**Root causes & fixes (ALL LIVE):**
- **A (main.py `_prewarm_loop`, commit 526b1862):** the calendar_jobs SWR key is `calendar_jobs:{year}:{month}:{start}:{end}` — the schedule's ranges (today→today, -14→+21) DATE-SHIFT every day, and the boot prewarm only warmed `calendar_jobs:0:0::` (a key the schedule never calls) → cold every morning. Fix: rollover-guarded prewarm of the ACTUAL first-paint ranges (today + -14→+21) + `scheduled_sos:1`, recomputed from `today_pt()` each PT date change. Server dates match the client's `isoPlus(n)` exactly = `(today_pt()±n).isoformat()`.
- **D (dashboard.py owntracks webhook, commit 13050ea8):** GPS ping flood (~5 sync Odoo calls each, ON the async event loop, ~15/session) contended with the fan-out. Fix: in-process dedupe ≤1 processed ping/60s per emp (`_ot_last_ping`) + fire-and-forget the Odoo work via `BackgroundTasks` (moved to `_ot_process_location`). **Verified (DJ-flagged) NOT to degrade anything:** all x_gps_ping consumers are day-range clustering tuned to 8-20min thresholds (stops/shift_range/lunch/home-clockout); NO live-position/breadcrumb reader exists; no race (home was_outside check is in-task after the create); still 200s to OwnTracks (faster). Caveat: a future live-tech-map/raw-trail view WOULD need a finer rate. NB: dashboard.odoo_rpc raises **httpx.HTTPStatusError** on 429 (not OdooBusy) — see [[project_payroll_employees_swr]].
- **G1 (v2_command.html, commit ce8f9a11):** the -90d `loadNeed` skipped-reschedule scan was PREFETCHED on open (boot + refreshCC) even with the ⚠️Needs tab hidden = speculative prefetch. Fix (DJ principle: never speculatively prefetch for a possible tap — load on open/expand only): loadNeed now fires ONLY on `show('need')` expand, on `ccSearch` (lazy self-load if uncached), and on manual ↻ gated `CUR==='need'`. **The `s-overdue`/`s-tosched`/`s-booked` "pills" are vestigial** — a `display:none` div, written-only, ZERO readers — so removing the on-open scan blanks nothing (no pill-backfill needed).
- **G2 (same commit):** `offers/in_window` was uncached `_fetchJson` → switched to `cjson` (IndexedDB) so held-slot ghosts survive offline + don't re-hit the worker every open.
- **G5 (deferred, optional):** split the -14 "Past jobs" (collapsed) off the default cal:on call so first-paint loads only today→+21.

**No SW bump needed for v2_command.html changes:** the service worker (inline in routers/auth.py, `wsc-shell-v10`) serves **navigations network-first** (3.5s timeout) — a top-level page load gets the fresh deploy online and the cache self-updates. Only .js/.css are also network-first; images/fonts SWR. So an HTML-only owner-page change is a single-file deploy.

**GOVERNING PRINCIPLE (DJ 2026-09-25):** never speculatively prefetch for a possible tap — load ONLY on open/expand; cache-first (paint last-known + bg-refresh) is the FALLBACK only where the on-demand wait is unacceptable, never a blanket prefetch. Prewarm only FIRST-PAINT essentials, not secondary on-demand sections.
