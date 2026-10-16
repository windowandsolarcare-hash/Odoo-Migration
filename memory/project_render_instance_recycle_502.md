---
name: project_render_instance_recycle_502
description: "Render starter instances are platform-recycled ~every 2-3h (clean graceful restart, NOT a crash/OOM); an in-flight request routed to the draining instance 502s for the ~12-15s window EVEN WITH 2 instances. The server_failed 'health check timed out 5s' event is a SIDE-EFFECT of the recycle, not the cause."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-16T15:32:46.868Z
---

★ CONTRADICTED 2026-10-16 (Audit independent 30-day dig — PENDING Lead synthesis + DJ approval): the "platform recycles ~every 2-3h, health-timeout is a SIDE-EFFECT" framing below is NOT supported by a full 30-day Render event pull. The `server_failed` events do NOT occur on a 2-3h cadence (they cluster — e.g. 2026-10-16 02:04, 02:42, 15:09, 15:14 — then gap 12h+); and Render's own reason string is "health check FAILED (timed out 5s)", which means `/healthz` (dependency-free, main.py:1010) did not answer = the single uvicorn event loop was FROZEN >5s. So the health-timeout is the CAUSE, not a side-effect — a blocking `odoo_rpc` (requests.post timeout=30, shared/odoo.py:23) called from an `async def` handler freezes the loop when Odoo is slow. Full proof: [[project_render_502_event_loop_freeze_blocking_odoo]]. This note's CLIENT-RETRY mitigation (below) is still a valid band-aid (it hides the 502 from the user) but does NOT fix the freeze. ⚠ This "harmless 2-3h recycle" framing likely ANCHORED the fleet away from the real cause for a month — a memory-induced mis-diagnosis (cf. the inert-launcher bug root-caused to a memory note). Read the new note as the current root cause.

Diagnosed 2026-10-13 after DJ hit a 502 confirming a customer (Patty) at 23:52Z / 4:52 PM PT — three independent reads (Lead events, Dispatcher events, Specialists logs) reconciled. wsc-field-assistant: starter plan, `numInstances=2`, `healthCheckPath=/healthz`, `startCommand=uvicorn main:app --host 0.0.0.0 --port 8000` (single worker per instance).

**Root cause — platform-initiated instance RECYCLE, not a crash, not a deploy, not a slow endpoint:**
- The host (Render) recycles a starter instance roughly every 2-3h. Observed `server_failed` events 2026-10-13 at 17:30Z (deploy-adjacent), 19:44Z, 20:33Z, 23:52Z — the non-deploy ones are platform recycles. Last deploy before the 23:52 502 ended 20:20Z (3.5h earlier), so NOT a deploy.
- Logs for the recycling instance (mwkjh) show a CLEAN graceful restart: `INFO: Shutting down` → `Application shutdown complete` → `Finished server process` → uvicorn re-exec → `[boot] lifespan startup complete -> READY` (23:52:12→24Z), then Render `Instance ... restarted` 23:52:29Z. No SIGKILL, no OOM (`evicted:false`), zero tracebacks. The confirm-flow requests all returned 200.
- The sibling instance (sxhz4) served `/healthz` 200 continuously the whole window.

**Two traps this clears up:**
1. **The `server_failed` "HTTP health check failed (timed out after 5 seconds)" event is a SIDE-EFFECT of the recycle, NOT the cause.** During the ~12-15s shutdown/re-exec the instance can't answer `/healthz`, so Render logs a health-check-timeout. Do NOT read it as "the event loop was blocked by a slow endpoint" or "OOM kill" — distinguish by pulling the instance's app logs: clean `Shutting down→READY` = recycle; a traceback or `evicted:true`/SIGKILL = a real crash/OOM. (Lead + Dispatcher both initially mis-hypothesized "blocked event loop"; the shutdown log lines disproved it.)
2. **2 instances HALVE but do NOT ERASE the 502 window.** Two instances protect against one being fully DOWN, but during an unplanned recycle Render's edge can still hand an in-flight request to the draining instance → that request 502s. So "we added a 2nd instance, why are 502s back?" — because this is a per-request routing-to-draining-instance window, not an all-instances-down outage. A retry lands on the healthy sibling and succeeds.

**Fix (the durable one): transparent client auto-retry on gateway errors (502/503/504/network-timeout) for IDEMPOTENT POSTs in the shared send path (`window.wscSend`) + the confirm POST.** The confirm/send actions are idem-keyed, so a silent resend to a healthy instance makes the recycle window invisible to the user. This is the SAME class as the inbox "lost signal" false-failure — see [[project_inbox_false_failure_plain_path]] — so COMBINE them into one send-path fix. Secondary (foundation, surface tradeoff per [[feedback_durable_foundation_over_shortcut]]): graceful SIGTERM drain so a recycling instance leaves rotation a beat before it stops answering `/healthz`. NOT fixes: more instances (halves, doesn't erase), deploy-batching (no deploy near the 502), `/healthz` changes (already dependency-free — it only "timed out" because the whole process was mid-restart).

**How to apply:** when DJ reports a one-off 502 (esp. confirm/send), don't assume a crash or a deploy. Pull Render `list_events` (look for `server_failed` + the paired `server_available`/`restarted` ~15s later) AND the instance's app logs (clean `Shutting down→READY`?), and check the sibling stayed healthy. If so it's a recycle blip → the answer to DJ is "normal host restart, your tap hit the 12s window, a retry works, and we're adding silent auto-retry." Ties [[project_render_static_deploy_propagation_window]] (the other Render zero-downtime window — that one is the deploy swap; this one is the unplanned recycle), [[feedback_odoo_verify_content_not_status]], [[feedback_sporadic_bugs_repeat_test]].

**Triage order (5 steps, to tell a recycle blip from a real crash) — service `srv-d78le0fkijhs738dsli0`:**
1. `list_events` — any `build`/`deploy_started` near the time? No → not a deploy.
2. App logs for `INFO: Shutting down` → `Application shutdown complete` → `uvicorn running` → `[boot] ... READY` = graceful recycle (not a crash).
3. Sibling instance served `/healthz` 200 throughout → single-instance blip only.
4. The endpoint's own request log shows 200 / no 5xx → the code didn't fail; the 502 was edge-level (request hit the draining instance).
5. ONLY a traceback / SIGKILL / OOM (`evicted:true`) = a real crash — handle as such, not a recycle.
