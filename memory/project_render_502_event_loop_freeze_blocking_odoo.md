---
name: project_render_502_event_loop_freeze_blocking_odoo
description: "The recurring app 502s are an event-loop FREEZE on a single uvicorn worker caused by blocking Odoo calls (requests.post timeout=30) made from async def handlers — NOT the HUD feed, NOT OOM, NOT deploys alone. Proven from 30 days of Render events + code."
metadata:
  node_type: memory
  type: project
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-16T15:31:27.601Z
---

**The month-long wsc-field-assistant 502s are an EVENT-LOOP FREEZE, not a slow feed, not OOM, not (only) deploys.** Independent dig by Audit 2026-10-16 (Render events/metrics/logs + live code). DJ rejected the "HUD feed too slow, missing the 5s health check" explanation; the evidence proves him right.

**PROVEN:**
- Every `server_failed` event in 30 days (16 of them) = `HTTP health check failed (timed out after 5 seconds)`. ZERO OOM, exits, evictions, disk events. (Render `list_events`, srv-d78le0fkijhs738dsli0.)
- Memory 440–475 MB vs the 536 MB (512 MiB) starter limit — never at ceiling; CPU ~0.1/0.5 (idle). Not resource exhaustion. (Render `get_metrics`.)
- `/healthz` is dependency-free (main.py:1010 — returns cached `_READY` dict, no live Odoo). ⟹ a healthz 5s-timeout can ONLY mean the single event loop was BLOCKED >5s. There is no slow-dependency path to fail healthz; only a frozen loop.
- Single worker: startCommand `uvicorn main:app` with NO `--workers` → one event loop per instance.
- `odoo_rpc` = blocking `requests.post(ODOO_URL/jsonrpc, timeout=30)` (shared/odoo.py:23). One slow Odoo call = up to 30s frozen.
- `routers/owner/dashboard.py`: 69 `async def` handlers, 625 `odoo_rpc` calls, 0 `run_in_threadpool`. A synchronous call inside an `async def` runs ON the loop → freezes it (+healthz) for the call duration. (Same in feed.py `async def api_feed_submit/_delete`.)
- ★ The feed route + scheduler are ALREADY loop-safe — NOT the healthz vector: `GET /api/feed/list` is a sync `def` (feed.py:610 → Starlette threadpool); `_sched_singleton` (main.py:705) returns a plain `def` → AsyncIOScheduler runs it via `run_in_executor` (threadpool). Threadpool Odoo calls release the GIL on socket I/O, so they do NOT freeze the loop. This is why logs show NO feed build at the misses and healthz 200s right up to them.

**STRONGLY INFERRED:** trigger = Odoo slowness / 429s (CLAUDE.md documents Odoo rate-limiting from polling). Both instances health-fail within the same ~1-min window (02:04:15+02:04:58; 20:56:08+20:56:57) = ONE Odoo slowdown freezing BOTH loops → the paid 2nd instance gives no relief (a 2nd instance only covers INDEPENDENT faults, never a shared-backend freeze). This answers "why wasn't it found in a month" (failure always reads 'health timed out' = looks like a deploy blip) and "why didn't the extra instance help."

**Caveat:** no single captured ">5s healthz gap then death" log line — a frozen loop logs nothing during the freeze. 100% confirm = pull the LAST app log line on each instance before each `server_failed`; it should repeatedly be an async Odoo endpoint (not healthz, not feed).

**Separate second contributor:** auto-deploy fires on EVERY commit to main (dozens/day during heavy fleet building) → each is a rolling restart / cold-start window = deploy-window 502s. Distinct from the loop-freeze; "fewer/batched deploys + warm-up gap" addresses ONLY this part.

**FIX (worst-first; PENDING Lead synthesis + DJ approval — do NOT ship the feed fix as 'the answer'):** (1) get blocking Odoo OFF the loop — convert hot `async def` handlers to plain `def` (already the working pattern for /api/dashboard + /api/feed/list → Starlette threadpools them) or wrap odoo_rpc in `run_in_threadpool`, or move to an async client; (2) cut the 30s odoo_rpc timeout to ~5–8s; (3) reduce Odoo 429s (throttle polling); (4) batch deploys / warm-up gap for the deploy-window 502s. The feed single-flight/warm-start/4s-cap is a real LATENCY + cold-start win but is NOT the 502 root cause.

Supersedes the partial [[project_render_instance_recycle_502]] (that captured only the deploy/recycle-window cause). Relates to [[feedback_odoo_verify_content_not_status]], [[feedback_durable_watcher_not_session_cron]]. How to apply: when the app 502s, check Render `list_events` for the failure REASON first (health-timeout vs OOM vs exit) — health-timeout = a frozen loop, hunt the blocking sync call on an async handler, not the feed.
