---
name: project_render_app_no_auth_layer
description: The Render field app has NO server-side auth — the PIN login only returns a redirect string; every /owner endpoint is publicly reachable.
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

Discovered 2026-07-15 (full-codebase audit). `saunders-render-app` has no authentication middleware in `main.py` and no `Depends`/session guard on any router. `routers/auth.py` `/api/login` just looks up a PIN in Odoo and returns a JSON redirect string — it sets NO cookie/JWT/session, and nothing downstream re-checks identity. `ACCESS_CODE` (shared.py:53) is loaded but only used as a lookup param in `api_whoami`, never as a gate. So every `/owner`, `/tech`, `/printing`, `/cheryl` endpoint (financials, payroll, customer PII, payment record/void, and the `/ask` AI agent that can `odoo_write` any model/method + `github_push_file` to prod main) is reachable by any anonymous caller who knows the URL.

Also open as of this date (all in the audit, none fixed yet):
- Live Odoo/Workiz keys hardcoded in source (main.py:57, printing/watcher.py:24, hemet.py, submitted_jobs.py, provenance.py) — treat as leaked, rotate.
- Twilio SMS/voice webhooks unsigned (sms.py:248, voice.py) — spoofable.
- Booking token secret + several cron/admin secrets have guessable hardcoded defaults (wsc-portal-2026, wsc-daily-sync-2026, wsc2026) that become the real auth if the env var is unset.

**Why it matters:** the app "feels" gated by the PIN screen but isn't. Any security recommendation must start here — injection surface is moot when the endpoints are already open.

**How to apply:** the planned fix is a signed session issued at PIN login + one FastAPI dependency enforced on every owner/tech/printing/cheryl router include, plus key rotation. Do NOT assume the PIN protects anything today. Full report: https://claude.ai/code/artifact/48119877-c280-488f-8d95-11804b03d628 . See [[project_dead_shadowed_routers]].
