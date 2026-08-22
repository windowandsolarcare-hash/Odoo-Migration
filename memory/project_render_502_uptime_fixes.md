---
name: project_render_502_uptime_fixes
description: Two root causes of intermittent 502s on the Render field app (deploy gaps + anthropic-client memory leak) and the fixes shipped 2026-06-06.
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

The wsc-field-assistant Render app (`srv-d78le0fkijhs738dsli0`, Starter plan = 512 MB / 0.5 CPU, single instance) threw occasional 502s. Diagnosed from `get_metrics` over 48h: 502s were NOT constant — 39 total, all in one 2h window that lined up with memory hitting the 512 MB cap → OOM kill → restart. Two root causes:

**1. Deploys had no health check → restart gap.** `healthCheckPath` was empty, so every push killed the single instance and started a new one with a 10-30s 502 window. Fix: added `@app.get("/healthz")` returning `{"ok": True}` in `main.py` (no Odoo call, so an Odoo hiccup can't fail the check), then set the path via Render REST API:
`curl -X PATCH https://api.render.com/v1/services/srv-d78le0fkijhs738dsli0 -H "Authorization: Bearer <RENDER_KEY>" -d '{"serviceDetails":{"healthCheckPath":"/healthz"}}'`
(The `mcp__render__update_web_service` tool does NOT expose healthCheckPath — use the REST API. Render API key `rnd_...` lives in `~/.claude/mcp.json`.) Now deploys are zero-downtime: Render waits for /healthz on the new instance before cutting over.

**2. Memory leak: `anthropic.Anthropic()` created per request, never closed.** Each new client wraps an httpx connection pool; per-request churn made RSS climb ~116→371 MB over 16h until OOM. Was in 11 call sites across dashboard.py, field.py, notes.py (5), sms.py, printing/watcher.py (every-30-min cron — drove the overnight climb even with no traffic). Fix: ONE lazy singleton per module, reused forever:
```python
_ANTHROPIC_CLIENT = None
def get_anthropic_client():
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        _ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    return _ANTHROPIC_CLIENT
```
Lazy (not module-level instantiation) on purpose — a missing key can never crash startup. `get_anthropic_client()` lives in `routers/owner/shared.py` (exported in `__all__`); field/notes/sms use it via `from .shared import *`. dashboard.py and printing/watcher.py have their own local `_get_anthropic_client()` (separate packages/keys).

**RULE: never write `anthropic.Anthropic(...)` inline at a call site again — always use the singleton helper.** Reintroducing per-request clients brings the leak back.

All 6 files pushed in ONE atomic commit via the Git Trees API (create blobs → tree → commit → PATCH ref) because partial deploy would crash: new field/notes/sms call `get_anthropic_client()` which only exists once new shared.py lands.

**Why:** the app felt unreliable but uptime was actually ~99%+ except during deploys and the one OOM event. These two fixes remove both. Plan upgrade to Standard (2 GB, ~$25/mo) is now likely unnecessary.

**How to apply:** when 502s/uptime come up, check [[project_render_deploy_failed_check]] first (failed deploy serving stale), then memory via `get_metrics`. When adding AI code, reuse the singleton. Related: [[reference_render_tools_architecture]], [[feedback_render_put_env_vars]].

**★ 2026-07-06 — THIRD root cause + fix pattern: `async def` endpoints making BLOCKING `odoo_rpc` calls freeze the single event loop.** A slow My Day call (heavy inline reactivation query) blocked the loop for 20-28s → EVERY other request (healthz, field, etc.) 502'd = app-wide cascade on the 1-worker/0.5-CPU Starter box. NOT OOM this time (memory only **156/512 MB** during the incident — confirmed via Render REST metrics `GET https://api.render.com/v1/metrics/memory?resource=srv-d78le0fkijhs738dsli0&startTime=..&endTime=..`). **FIX = convert heavy read endpoints `async def` → plain `def`.** FastAPI runs sync `def` handlers in a THREADPOOL, so blocking Odoo calls no longer freeze the event loop and multiple run concurrently. RULE: an endpoint whose body only does blocking `odoo_rpc` (no `await`) should be `def`, NOT `async def`. POST handlers needing `await request.json()` stay async → wrap blocking work in `run_in_threadpool` (not yet done). **DONE + PROVEN** for `api_myday` + `api_myday_reactivations` (myday.py): load test = 6 concurrent /api/myday (5-6s each, ran in PARALLEL) while /healthz stayed 200 @ ~0.15s throughout (pre-fix it 502'd). **TODO: sweep the same async→def across other heavy read GETs** (field.py, dashboard.py, analytics.py, brain.py, reactivation.py candidates) — any `async def` GET doing blocking odoo_rpc with no await. **✅ FULL SWEEP DONE (2026-07-06):** applied the async→def transform to ALL 30 changed `routers/owner/*.py` (dashboard.py alone = 80 handlers; ~300 total) in ONE atomic commit via Git Trees API (commit d11b7594). AST-safe transform (only `@router` route handlers with NO await in body; POSTs w/ request.json() left async). Verified: 10 concurrent heavy reqs (6 myday + 4 dashboard) while /healthz stayed 200/instant. Reusable scripts: scratchpad `transform.py` + `atomic_commit.py`. **RESTART** = `POST https://api.render.com/v1/services/srv-d78le0fkijhs738dsli0/restart` (Render key in DJ's Drive Doc titled "Render"; read via [[project_drive_upload_no_local_auth]]-style Drive tools, use via `$(cat file)`, delete after — [[feedback_api_keys_via_file]]). ★ NEVER PUT /env-vars partial (wipes all — DJ's standing warning).
