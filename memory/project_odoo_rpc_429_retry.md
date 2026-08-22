---
name: project_odoo_rpc_429_retry
description: "Two separate odoo_rpc helpers. shared/odoo.py (printing) now retries Odoo 429/5xx + raises clean errors (was bare res['result'] → KeyError 500). Owner-side routers/owner/shared.py odoo_rpc may still need the same fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-20T14:32:58.542Z
---

**There are TWO separate `odoo_rpc` implementations in the app** (verified 2026-08-19):
- **`shared/odoo.py`** — used by the **printing** module (`from shared.odoo import odoo_rpc`).
- **`routers/owner/shared.py`** — used by the **owner** app (dashboard.py etc., via `from .shared import *`; 600+ call sites).

**Bug (2026-08-19, DJ hit it):** Saunders "Send preview" → `POST /printing/api/jobs/<id>/preview-invoice` → **500** (`KeyError: 'result'`), client mislabeled "Network error." **The REAL root cause was NOT a 429** (Lead/Portal first theorized transient rate-limit; wrong). Empirically reproduced: the failing call is **`mail.mail.send()`, a VOID method — Odoo answers HTTP 200 with `{jsonrpc,id}` and NO `result` and NO `error`.** That is a legitimate SUCCESS (the email genuinely sends — verified test mail id 1050 reads `state:'sent'`). The old `return res["result"]` KeyError'd on that *success* → 500. So the email was sending all along; only the UI reported failure.

**★ CORE LESSON: an Odoo JSON-RPC HTTP-200 response with no `error` key is SUCCESS — even if `result` is absent.** Void methods (`send`, some `write`/`action_*`) return None and Odoo OMITS `result`. NEVER do bare `res["result"]`; do `if "error" in res: raise ...; return res.get("result")`. Diagnosing tip: `KeyError:'result'` proves there was NO `error` key (error is checked first) → it's a void/absent result, not a masked Odoo error.

**Fix history:** b66062b (first, PARTIAL/WRONG — retried on missing-`result` thinking it was a 429 symptom, which sent the email 3× then raised "Odoo is busy") → **dd5ccdf (CORRECT — `return res.get("result")` on any no-`error` 200; keep 429/5xx + non-JSON retry only).** Verified live: preview → `{ok:true, invoice:200241}`. `printing/jobs.py` 0e247fd wraps `preview_invoice`'s Odoo work → clean `{ok:false,message}` on real failure. The 429 backoff is still there for genuine rate-limits (real under 4-session load), just no longer conflated with void returns.

**Owner-side twin — NOW FIXED (2026-08-20, routers/owner/shared.py 62d4087):** it's a SEPARATE `odoo_rpc` (httpx, `resp.raise_for_status()` + `data.get('result')`) — so it never had the void-method KeyError (already used `.get`), but it had NO 429 retry: `raise_for_status()` killed the whole call on the first 429, which was failing the **5am Customer Analytics cron** and the **Weekly Report** ("Error pulling metrics: 429"). Added the same 3×-retry-with-backoff on 429/5xx (clean "Odoo is busy" on exhaustion); success + Odoo-error-body behavior unchanged, other 4xx still surface via raise_for_status. **Both odoo_rpc helpers are now 429-resilient.** Pending belt-and-suspenders (not done): light throttling of `analytics.py`'s 5am Odoo burst that self-induces the 429. See CLAUDE.md "Infrastructure Gotchas" + [[project_field_voice_history_sanitize]].
