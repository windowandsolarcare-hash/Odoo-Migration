---
name: project_render_oom_memory_leak_502s
description: "Intermittent 502 Bad Gateway on wsc-field-assistant = a SLOW memory leak riding the 512MB Starter-plan ceiling → OOM kill → restart window. Confirmed sawtooth. Prime unbounded accumulator: swr._LASTGOOD (never evicted). Fix = reduce footprint (NO plan bump, NO extra workers)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-11-05T16:15:25.275Z
---

**Incident (2026-11-05 AM, DJ frustrated, live-ops via Dispatcher):** intermittent **502 Bad Gateway** across the whole app, "several times this morning," while Render dashboard "looks up." Root-caused to a **slow memory leak** pressing the **512MB per-instance ceiling** (Render **Starter** plan, `srv-d78le0fkijhs738dsli0`, 2 instances, Oregon, **single uvicorn worker each** — start cmd `uvicorn main:app` has NO `--workers`).

**Why 502 + "looks up":** when an instance's RSS crosses 512MB Render **OOM-kills** it and restarts; during the restart there's a few-second window with no healthy instance on that route → **502**. Self-heals in seconds, so a dashboard glance between blips shows healthy. DJ was also viewing only ONE of the 2 instances.

**Evidence (Render metrics, memory_usage, per-instance sawtooth — this is PROOF not theory):**
- instance `mdss8`: climbed 434→**490MB** over 14h on 11-04, then **475→206 at 20:48 UTC** = the OOM kill (event `server_failed` reason `oomKilled memoryLimit 512Mi`, 20:49). 20:48 UTC = ~12:48 PM Pacific.
- Every instance boots ~**150MB** and climbs to **360–490MB over ~1–2 days** (~+5–30MB/hr, front-loaded in first hours). Growth tracks **work handled** (one instance plateaus ~385, another climbs to 490) → a per-request / per-scheduler accumulator, not pure uptime.
- Also 11-05 05:43 UTC one instance failed `/healthz` ("connection refused") → bounce; 10-30 "health check timed out (5s)". Each = another 502 window.
- **Each deploy resets the clock** (fresh ~150MB) — the fleet deploys often enough that it usually stays under, so OOMs only when a stretch goes without a deploy. That's why it's intermittent.
- ⚠ The specific 8:06 AM Pacific burst DJ screenshotted = **BOTH** instances a **clean simultaneous graceful restart** (SIGTERM "Shutting down"→"Waiting for connections to close", then fresh boot) with **NO deploy/OOM/health event** in Render's log → reads as a **Render host event or a manual "Restart service,"** NOT an app crash. Don't code-chase this one (Lead). If anyone clicked Restart to "fix" the 502s, that click itself caused that burst.

**CONFIRMED unbounded accumulator #1 — `routers/owner/swr.py`:** module-level `_CACHE` and `_LASTGOOD` dicts, **never evicted, no cap/LRU**. `bust()`/`bust_prefix()` only pop `_CACHE`, NEVER `_LASTGOOD`. Keys include **param-keyed, non-enumerable** `calendar_jobs:%s:%s:%s:%s` (year/month/start/end, dashboard.py:10922) and `scheduled_sos:%d` (day offset) + `whoami:<code>` (bounded) + `dashboard` (1). So `_LASTGOOD['calendar_jobs:*']` grows one full-month-payload entry per distinct calendar view ever requested since boot and never clears. Real leak, though likely only PART of the ~340MB — more accumulators still to find. **First surgical fix candidate:** bound `_CACHE`/`_LASTGOOD` with an LRU cap (leaf helper, low blast radius, removes no working logic).

**Lead's governing calls (2026-11-05):** (1) keep **workers=1** — more workers = more baseline RSS on a 512MB box = worsens the OOM; no infra change to start cmd. (2) Fix = **footprint reduction**, honoring DJ's **"do NOT bump the plan"** (his bill is already up). (3) This is **boot/infra-adjacent (high blast radius — bad start cmd/scheduler change crashes BOTH instances) → NOT auto-deploy-on-QC: STAGE the diff, Lead byte-QC, THEN deploy, watch both instances come healthy.** (4) Prime lead to chase: the **in-process scheduler + prewarm run on BOTH instances** = double memory AND double-firing correctness risk; if the answer is a **single server-side Render Cron**, scope SEPARATELY + loop Lead+DJ (new infra) — do NOT bundle a scheduler re-architecture into a memory hotfix. (5) Do NOT blind-shorten `odoo_rpc`'s `timeout=30` (shared/odoo.py:23) — a real long Odoo op would start failing; the 1-worker concurrency question (does a 30s sync call block others? sync `def` endpoints run in FastAPI's threadpool, default ~40 threads — swr.py exists precisely to stop a cold-HUD burst saturating that pool) is a SEPARATE reliability lever from memory.

**Status:** app HEALTHY again since 16:06:48 UTC (both instances serving 200s). Fix is PREVENTIVE — staged work, no emergency deploy. Related: [[feedback_durable_watcher_not_session_cron]], [[feedback_money_adjacent_staging_risk_calibrated]], [[feedback_builders_dont_sequence_or_defer]], [[feedback_reuse_canonical_endpoint]].
