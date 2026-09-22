---
name: project_zero_downtime_worker
description: "W&SC app zero-downtime plan (DJ approved 2026-09-22, Builder-2 leads) — extract the 18 cron jobs to a single-instance Render Background Worker so the web tier can go numInstances=2 without double-firing money/customer crons. CODE built + held for Lead HARD QC (money app). + the module-level import-os boot-crash catch."
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-22T20:31:43.489Z
---

**Goal:** true zero-downtime deploys — a deploy/hiccup never 502s the field tech or a customer payment. Spec: `saunders-render-app/3_Documentation/ZERO_DOWNTIME_SPEC.md`. Root cause of the 2026-09-22 502s = single web instance restarting on deploy (no healthy target). Fix = web numInstances≥2, but that would DOUBLE-FIRE the 18 in-process crons (reminders/paywatch/reengage = money/customer) → must first make the scheduler single-instance.

**Design (extract-to-worker, chosen over leader-lock):** main.py's `lifespan` boots an `AsyncIOScheduler` with 18 `_scheduled_*` jobs (line ~648). Refactor: extract the job list into a module-level **`build_scheduler()`** (funcs unchanged); the web lifespan runs it ONLY `if os.environ.get('RUN_SCHEDULER')`. New **`worker.py`** (`python worker.py`, RUN_SCHEDULER=1) imports build_scheduler from main + runs the scheduler on its own asyncio loop (import main runs module code + lazy Sentry but NOT the lifespan → no auto-start). Invariant: **web = ZERO scheduler (RUN_SCHEDULER unset → safe at N instances); worker = the ONLY scheduler (numInstances=1) → no double customer texts.** + lazy Sentry (main + worker), NO-OP until SENTRY_DSN env set (DJ provides), requirements += sentry-sdk>=2.0,<3.0.

**★★ BOOT-CRASH CATCH (reusable):** in this app `os` was imported ONLY LOCALLY inside functions (`import os` at lines 256/289/479/536), NOT at module scope. A module-level or lifespan reference to `os.environ` (my gate + Sentry block) would `NameError` at boot = money-app crash. **`python -m py_compile` does NOT catch this (it's name-resolution, not syntax).** Fix: added module-level `import os`; verify with AST that a needed import is at module scope, don't trust py_compile for name resolution. Always check that names used at module level are imported at module level.

**★ MONEY-SAFE DEPLOY SEQUENCE (ordering is the whole risk):** A) set RUN_SCHEDULER=1 on WEB env FIRST (current code ignores it) so the refactor deploy keeps web running the scheduler = NO crons gap; B) push main.py+worker.py+requirements → web still sole scheduler, zero behavior change (safe milestone); C–E COORDINATED FLIP (low-cron window, Lead-timed): stand up worker as sole scheduler + remove RUN_SCHEDULER from web + redeploy (lean GAP-over-DOUBLE: a missed tick is covered by misfire_grace_time; a double = double customer text) → verify 18 jobs fire in WORKER logs → then web numInstances=2 + fast /healthz + graceful shutdown.

**BLOCKERS/flags:** Render MCP has create_web_service but NO create-background-worker → the worker service needs DJ (dashboard New Background Worker, same repo, `python worker.py`, RUN_SCHEDULER=1) or a render.yaml. SENTRY_DSN = DJ. **STATUS: CODE built + compiled, HELD for Lead HARD QC before ANY money-app deploy; nothing deployed.** Lead QC gate: the double-fire test (web@2 + a reminder fires EXACTLY once). Coordinate the flip window (not while DJ transacts). Local working files: C:\Users\dj\wsc_main_live.py, wsc_worker.py, wsc_req.txt. See [[feedback_compile_gate_before_push]] (chain compile→push) + [[feedback_no_deploy_during_customer_payment]].
