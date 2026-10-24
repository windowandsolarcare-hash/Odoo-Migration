---
name: project_healthz_flap_scheduler_block
description: "The recurring 'Server failure detected on wsc-field-assistant' Render alerts (/healthz 'timed out after 5s' + occasional connection-refused, Oct 2026) are BENIGN single-instance flaps from APScheduler minute-boundary ticks blocking the single uvicorn event loop — NOT redeploys, NOT user-facing downtime. Fix = run_in_executor wrap."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-24T03:51:06.709Z
---

**Symptom.** Render `server_failed` events on `srv-d78le0fkijhs738dsli0`, reason `"HTTP health check failed (timed out after 5 seconds)"` or `"...connect: connection refused"` against `:8000/healthz`. One instance at a time; self-heals (`server_available`) in ~8-24s. `numInstances=2` behind the LB → the other instance stays up → **no user-facing outage** (why DJ sees no matching downtime). Clusters at night (00:35-01:57 PT) and midday.

**NOT our redeploys (ruled out firsthand, Lead 2026-10-23).** Two independent proofs: (1) the service's `buildFilter.ignoredPaths = ["3_Documentation/**"]` → every `AGENT_MAIL.md` / `SESSION_ROSTER.md` / `ENDPOINT_MAP.md` commit is build-filtered (NO deploy fires); memory-mirror commits go to the **Odoo-Migration** repo, not this service → heartbeat/mail/roster ticks never redeploy at all. (2) The `server_failed` timestamps do NOT correlate with `deploy_started`/`deploy_ended` — most hit with no deploy anywhere near; every real deploy ended `succeeded` with no failure beside it. So: don't chase these alerts as "our heartbeat commits restarting the instance."

**Root cause (Specialists firsthand, metrics + app logs 2026-10-23).** Resource theory DEAD: CPU near-idle (≤0.16 core), mem ≤77% of 512MiB (the mem-halving/instance dip is the restart EFFECT, not the cause). The scheduler runs IN-PROCESS on the single uvicorn worker (1 worker, `RUN_SCHEDULER` default-on); APScheduler ticks `_scheduled_meeting_retry` / `_scheduled_email_task_pull` fire on the minute boundary and the flaps land exactly there → a blocking call (Odoo RPC) inside the tick stalls the event loop past the 5s `/healthz` probe → instance marked unhealthy → brief flap → recovers when the tick finishes.

**Fix (picked by Lead 2026-10-23, going §15).** Wrap the blocking tick bodies in `run_in_executor` so the event loop stays free to answer `/healthz` — zero cost, no topology change (it's I/O-block not CPU-load, so moving the blocking I/O to a threadpool thread fully frees the loop). **Proof-of-fix gate** (feedback_verify_collection_and_live_pipe): post-deploy, watch several minute-boundaries with zero `server_failed` (or a `/healthz` latency probe during a tick) — a green deploy is NOT proof the loop stopped blocking.
- **Parked durable option (DJ's call — costs another Render instance):** move the scheduler to the existing but-never-deployed `worker.py` as a dedicated service. The `lock acquired -> running` / `lock held elsewhere -> standing by` lines show the jobs already DB-advisory-lock-coordinate, so the migration is clean. NOT needed for this symptom — surfaced once to DJ as a foundation upgrade, not greenlit on a peer ask.

**Related thread — eMudhra CA advisory (firsthand, Lead 2026-10-23).** `certifi` is UNPINNED (transitive via `requests` → `certifi>=2023.5.7`) and Render `cache: no-cache` resolves the freshest each build. The running deploy's build log shows `Successfully installed … certifi-2026.10.23` ≥ advisory floor **2026.10.19** → the compromised eMudhra root removal IS on deployed bytes; no emergency bump. Optional hygiene floor pin `certifi>=2026.10.19` approved (floor not ceiling; makes "patched" explicit + durable).

See [[project_held_text_release_8am]] (same in-process APScheduler on the web tier, same singleton lock), [[feedback_durable_watcher_not_session_cron]], [[feedback_verify_collection_and_live_pipe]], [[feedback_cant_headlessly_seed_is_security_feature]].
