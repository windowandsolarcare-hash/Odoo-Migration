---
name: project_render_python_pin_incident
description: "Render Python runtime is pinned to 3.12.8 via .python-version — why, and the two latent bugs the 3.14 venv rebuild exposed (cgi removal, BackgroundTasks import)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5c7951e2-f25a-42b0-ac13-dd386cb454cf
---

# Render Python pinned to 3.12.8 — deploy incident 2026-06-11

**There is now a `.python-version` file (`3.12.8`) in the repo root.** Do NOT remove it. requirements.txt is fully UNPINNED (fastapi, httpx, anthropic, etc. all float). That combo is a landmine: when Render rebuilds the venv it grabs the latest of everything.

## What happened
Pushing the new analytics app triggered a venv rebuild. Render auto-bumped the runtime to **Python 3.14.3**, which **removed the `cgi` stdlib module**. The cached/old `httpx` does `import cgi` at module load → every deploy hit `ModuleNotFoundError: No module named 'cgi'` at `dashboard.py` `import httpx`. The live site kept serving the OLD instance (build "succeeded" but `update_failed` on start), so it looked fine while no new code could ship.

**Fix:** added `.python-version` = `3.12.8` → forces a runtime with `cgi` present. httpx import then works.

## Second latent bug the fresh venv exposed
With a fresh venv came a **newer FastAPI** that **evaluates route-handler type annotations at import time** (decoration). Two handlers used `background_tasks: BackgroundTasks` in their signature but never imported `BackgroundTasks` → `NameError` at import, crashing the whole app:
- `routers/owner/payments.py:371` (api_stripe_success)
- `routers/owner/shift_review.py:870` (api_payroll_geocode_properties)
Fix = add `BackgroundTasks` to each file's `from fastapi import ...` line. The old FastAPI tolerated the missing import (lazy annotation); the new one doesn't.

## Lessons / how to apply
- **`update_failed` = app crashed on START, not a build error.** Render serves the last good build silently. Always check `list_deploys` status after a push; if `update_failed`, pull `list_logs` (type=app) for the traceback. (Workspace for render MCP = `tea-d78l9fqdbo4c7388n9og` — select it, never ask DJ.) See [[project_render_deploy_failed_check.md]].
- Because deps are unpinned, ANY future venv rebuild can pull newer FastAPI/Pydantic that breaks on patterns the old versions tolerated. If a deploy suddenly fails on a NameError/import in a file you didn't touch, it's this — scan all routers for FastAPI signature types (BackgroundTasks/Depends/Form/etc.) used but not imported.
- Better durable fix (NOT done yet, would need known-good versions): pin fastapi/uvicorn/httpx/anthropic in requirements.txt.

Related: [[project_customer_analytics_datamodel]] [[project_render_app_architecture]]
