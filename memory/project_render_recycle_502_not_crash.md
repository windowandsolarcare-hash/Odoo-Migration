---
name: project_render_recycle_502_not_crash
description: "502 triage (2026-10-13): a Render 'server_failed — HTTP health check failed (timed out after 5s)' event is usually the SIDE-EFFECT of a graceful single-instance RESTART, not a crash. Before concluding crash/OOM/endpoint-bug, pull app logs for the 'INFO: Shutting down → Application shutdown complete → uvicorn restart → [boot] ... READY' sequence; the sibling instance stays healthy throughout. Not a deploy if no build/deploy_started event near it. Fix for the user-visible 502 = idempotent gateway-retry in window.wscSend (see plan)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-14T00:00:54.793Z
---

## The fact (so future 502 triage reads the event correctly)
A Render **`server_failed` event with reason "HTTP health check failed (timed out after 5 seconds)"** is, on this app, most often the **side-effect of a graceful single-instance restart** (platform recycle), NOT a crash, OOM, or an endpoint throwing.

**Proven 2026-10-13 (DJ's Patty-confirm 502, via Dispatcher):**
- The instance (`mwkjh`) logged a CLEAN shutdown: `INFO: Shutting down` → `Waiting for application shutdown` → `Application shutdown complete` → `Finished server process` (23:52:12Z), then re-exec `Running 'uvicorn main:app'` → `[boot] lifespan startup complete -> READY` (23:52:24Z). Render then logged the `Instance ... restarted` event + the health-check-timeout `server_failed` at 23:52:29Z. The health-check "timeout" is because the process was mid-restart — a CONSEQUENCE, not the cause.
- **No build/deploy event near it** (last deploy 3.5h earlier) → NOT a deploy cycle. **No traceback / SIGKILL / OOM** → graceful, platform-initiated. **The endpoint never errored** — every confirm-flow call logged 200.
- The **sibling instance stayed healthy** the whole ~12-15s window (continuous `/healthz` 200). So the user's 502 was only the brief window their request hit the recycling instance; a retry on the healthy instance succeeds.
- Same signature seen twice that day (20:33Z + 23:52Z) and matches Operator's ~1:30 PM inbox/thread 502 → it's a recurring transient recycle, low blast radius, self-healing.

## How to triage a 502 here (order)
1. `list_events` (service `srv-d78le0fkijhs738dsli0`) — is there a `build_started`/`deploy_started` near the time? If NO → not a deploy.
2. Pull app logs for that minute — look for `Shutting down` / `Application shutdown complete` / `uvicorn running` / `[boot] ... READY`. Present → graceful restart (recycle), not a crash.
3. Check the SIBLING instance's `/healthz` in the same window — if 200 throughout, the outage was single-instance only.
4. Check the actual endpoint's request logs — a 200 (or no app-level 5xx) means the code didn't fail; the 502 was edge-level (request hit the down instance).
5. Only if you see a traceback / `SIGKILL` / OOM / `Out of memory` → a real crash.

## The fix (planned, gated — §15)
User-visible 502 on an idempotent send/confirm = closed by a **transparent gateway-retry in the LIVE `static/owner/wsc_send.js` (window.wscSend)**: on a transient (incl. 502/503/504), after the existing `send_status` re-query, AUTO-RETRY the idempotent POST (same `client_msg_id`, server dedups) so it lands on the recovered instance before ever showing the red "lost signal". Combines with [[project_inbox_false_failure_plain_path]] (same send path — the single re-query can itself fail in the same outage). Secondary: graceful-drain on SIGTERM (flip readiness unhealthy a beat before the socket closes) — surfaced shortcut-vs-durable for DJ. See [[feedback_durable_foundation_over_shortcut]], [[feedback_odoo_verify_content_not_status]].
