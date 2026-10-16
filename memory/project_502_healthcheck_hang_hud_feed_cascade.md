---
name: project_502_healthcheck_hang_hud_feed_cascade
description: "Repeated 502s on wsc-field-assistant are a /healthz-timeout HANG cascade (not deploys, not OOM): the HUD ~18-producer Odoo feed build bogs the single uvicorn worker past Render's 5s health window → restart → cold cache → resync rebuild → restart again."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-16T15:14:55.738Z
---

Diagnosed 2026-10-16 (DJ hitting "way too many" 502s; relayed via Dispatcher, Lead pulled same telemetry independently → converged). Render service **srv-d78le0fkijhs738dsli0** (wsc-field-assistant), starter plan, **numInstances=2**, startCommand `uvicorn main:app` (NO `--workers` → ONE async worker per instance), healthCheckPath `/healthz`.

**It is a HANG, not a crash/deploy/OOM/scale problem:**
- ZERO deploys in ~24h; 502s have no deploy behind them.
- Render events = repeated `server_failed` reason **"HTTP health check failed (timed out after 5 seconds)"** → kills+restarts the instance; the restart window is when users 502.
- `get_metrics`: **CPU idle (~0.1 of 0.5)**, **memory under the 512MB cap** (Render logs an explicit OOM event for a real OOM — we saw health-check-failed instead). `instance_count` hit **0 at 02:03–02:04 UTC** (BOTH instances unhealthy together) = total outage. Both failing within seconds = SYSTEMIC.

**Mechanism (why a cheap async /healthz still times out):** `/healthz` (main.py:1010) is async + trivial (no Odoo) — so when it can't answer in 5s the **event loop/worker is starved**. The starver is the HUD live feed: `feed.py` `/api/feed/live_list` build calls **~18 producers against Odoo, uncached** (`feed.py` comments at ~:42-49 and ~:888-892 ALREADY name it: "the scan bogs the instance -> /healthz restart"). Outbound Odoo is **sync `httpx.post(..., timeout=20)`** (`dashboard.py:299 odoo_rpc`) → one slow Odoo call can hold a worker ~20s. On 0.5 CPU, a multi-second GIL-holding merge/Odoo-wait burst starves the loop thread for >5s while the 1-min-avg CPU still reads idle (burst is <10% of a 60s window). Hot handlers (`dj_alerts` notify.py:228, `live_list` feed.py:783) are sync `def` (threadpool), so they don't block the loop *directly* — the bog is CPU/GIL + upstream stall during the heavy build (notably the **per-web-instance prewarm warm-loop in main.py** that fires the build on EVERY boot/restart on BOTH instances at once).

**The CASCADE (why "way too many"):** last-good feed cache is **in-memory only** (`_LIVE_LASTGOOD`, `_LIVE_CACHE`) → every restart wipes it → next HUD load does a **synchronous cold rebuild** capped at `_LIVE_COLD_CAP = 8.0s` (ABOVE the 5s health window) → re-bog → another health-check-fail → restart → cold again. Self-feeding. Clustering ~02:00/~15:00 UTC = prewarm-on-boot + cold-after-restart in lockstep across both instances.

**Cheapest fix (no plan bump, no money) — recommended, NOT yet shipped (needs §15 + Lead QC + DJ go; live-ops blocker so expedites):**
- Lower the cold *synchronous* build cap BELOW the 5s health window (so a cold build can never miss a ping) + always serve last-good/empty instantly and refresh in the background (single-flight). Small, low-risk, in `feed.py`.
- Durable follow-on: **persist last-good to PG** (the "deferred durability follow-on" the code already notes) so a restart serves instantly instead of cold-building → kills the cascade at the root.
- Add/verify a tight timeout on the feed-path Odoo calls so no single call parks a worker past the health window.

**Rejected:** `uvicorn --workers 2` — each worker ~150MB fresh climbing to ~450MB (in-memory cache growth/leak) on a 512MB cap → OOM. Plan bump (standard) — costs money, DJ is on a $200→$100 cost-cut. Both off the table on current plan.

**Secondary (not the 502 cause, worth a separate look):** per-instance memory climbs ~150MB→~450MB over ~1h then resets on restart = a slow leak / unbounded cache growth.

**How to re-diagnose fast next time:** `list_events` (look for server_failed "health check failed"), then `get_metrics` cpu+memory+instance_count around the timestamps — idle CPU + flat-under-cap mem + health-check-fail = loop HANG (chase blocking/un-timed upstream on the single worker), NOT OOM/scale. See [[feedback_durable_watcher_not_session_cron]], [[feedback_data_location_odoo_vs_postgres]], [[feedback_root_cause_not_just_instance]].
