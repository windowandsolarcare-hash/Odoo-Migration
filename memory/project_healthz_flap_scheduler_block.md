---
name: healthz-flap-scheduler-block
description: "The recurring Render 'server failure' /healthz-5s-timeout alerts = BENIGN single-instance flaps (2nd instance holds, no outage). ★ CORRECTED 2026-10-24: NOT the APScheduler ticks (those run OFF the loop, threadpooled) → run_in_executor on them is a NO-OP; it's the SAME blocking-odoo-in-async-handler event-loop freeze as project_render_502_event_loop_freeze_blocking_odoo. Plus the eMudhra certifi floor pin is shipped."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-24T04:01:26.166Z
---

**What the alerts are:** Render "Server failure detected on wsc-field-assistant" (Oct 18-23) = `/healthz timed out after 5s` (+ occasional connection-refused) health-check flaps, ONE instance at a time, self-heal 8-24s. Service = **starter, 2 instances**; the other instance keeps serving (real traffic succeeded through every window) → **no user-facing outage**. A separate benign bucket = connection-refused at deploy boundaries (new instance not yet listening), inherent to autoDeploy-on-every-commit (doc-only commits don't deploy — buildFilter ignores `3_Documentation/**`).

**★ CORRECTION 2026-10-24 (Specialists firsthand, Lead concurred) — the earlier "APScheduler minute-boundary tick blocks the loop → fix = run_in_executor" attribution was WRONG:**
- `build_scheduler()` uses `AsyncIOScheduler` (main.py:774); every `_scheduled_*` is a plain sync `def` and `_sched_singleton` returns a sync `wrapped()` (main.py:724). APScheduler's default **AsyncIOExecutor runs non-coroutine jobs via `loop.run_in_executor(None,…)`** — i.e. the jobs ALREADY run in a thread, off the event loop. **So wrapping them in run_in_executor again = a NO-OP** (would deploy green and fix nothing — the "green deploy ≠ fixed" trap). The minute-boundary correlation was a red herring (scheduler logs print every minute, so any failure sits next to one; the actual failures hit scattered minutes matching no job's cron).
- `/healthz` is `async def` + pure in-memory (main.py:1025-1034: returns a dict + `len(app.routes)`, "FAST — no live Odoo call"). A 5s timeout on THAT = the **event-loop thread itself is frozen >5s**. Metrics at the failures: CPU flat **≤0.16 core**, mem **≤77%** of 512 MiB → NOT CPU/GIL/OOM.
- **Therefore it is the SAME issue as [[project_render_502_event_loop_freeze_blocking_odoo]]** (Audit 2026-10-16): a synchronous blocking `odoo_rpc` (requests.post, timeout) called from an `async def` handler freezes the single uvicorn loop when Odoo is slow/429 (dashboard.py: 69 async handlers / 625 odoo_rpc / 0 run_in_threadpool). This flap did NOT "close the 02:04 idle path" of that memory — **it IS that idle path** (an overnight async request — e.g. the ~per-minute OwnTracks webhook / owner API calls — hitting a slow-Odoo moment). The real fix = make the blocking odoo_rpc calls in async handlers non-blocking (`run_in_threadpool` / async), a foundation-scale refactor (Lead/DJ call), NOT a scheduler change and NOT worker.py.

**eMudhra certificate item (2026-10-24):** PATCHED — the running service's build logs (last 3 deploys incl. commit 4dfddd01) show `certifi-2026.10.23`, ≥ the advisory floor 2026.10.19 (certifi is unpinned + Render builds no-cache → each deploy pulls freshest). Lead §15-confirmed firsthand. Floor pin `certifi>=2026.10.19` **SHIPPED** (requirements.txt, commit 49cd86a5) to convert "patched by luck" into "patched by explicit floor." Node/PHP advisory items N/A (we're Python).

Related: [[project_render_502_event_loop_freeze_blocking_odoo]], [[project_inbox_odoo_429_threadpool_hang]], [[feedback_verify_collection_and_live_pipe]].
