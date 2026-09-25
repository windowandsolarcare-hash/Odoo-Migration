---
name: project_broad_except_defeats_global_503_handler
description: "A local `except Exception: return 500` in a router endpoint DEFEATS the global OdooBusy→503 handler (OdooBusy is an Exception subclass, so the local except catches it first and rewraps it as a 500) AND masks real errors as generic 500s. Found as the root cause of rerun-500s on outreach/pipeline + maintenance/stranded. Grep for the pattern."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-25T15:41:37.495Z
---

# A local `except Exception → 500` defeats the global OdooBusy→503 handler

**2026-09-23, found via the new OdooBusy/429 logging during a 50-cycle rerun.** The HOME cold load 500'd on `/owner/api/outreach/pipeline` + `/owner/api/maintenance/stranded`. The `[odoo] busy/throttle: 429 res.partner.search_read` log line fired at the EXACT millisecond of the 500s — pinpointing the cause.

## The bug
Both endpoints had a local `except Exception as e: return JSONResponse(..., status_code=500)`. On a 429, `shared.odoo_rpc` raises `OdooBusy` — and **OdooBusy is an Exception subclass**, so the endpoint's own broad `except Exception` catches it FIRST and rewraps it as a **500**, BEFORE the global `@app.exception_handler(OdooBusy)` → graceful **503** can ever fire. So the whole point of the global 503 net (see [[project_odoo_throttle_resilience_pattern]]) is silently defeated by any endpoint that has a broad-except-to-500.

## Two harms
1. **Under a 429**: returns a hard 500 (client error) instead of the graceful 503 (or, once SWR-wrapped, a 200 last-good). This is what broke the HOME cold load.
2. **Always**: a broad `except Exception → 500` also masks REAL errors (a genuine KeyError/TypeError becomes a generic 500 with no traceback surfaced) — bad for debuggability.

## The fix
Let `OdooBusy` PROPAGATE out of the builder/endpoint:
- If the endpoint is SWR-wrapped, the builder should `except → raise` (or have no broad except) so SWR catches OdooBusy and serves last-good/skeleton (200).
- If not wrapped, letting OdooBusy propagate hits the global handler → graceful 503.
Verify the sub-functions the builder calls (e.g. `pipeline_counts`, `classify_customers`) also don't have an internal broad-except swallowing OdooBusy.

## How to apply
- **This is a CLASS of bug, likely present in other routers.** Grep for endpoints that do `except Exception` and return a 500-ish `JSONResponse` (or `status_code=500`) — every one of them converts a 429/OdooBusy into a 500 and masks real errors. Inventory worst-first; fix each to let OdooBusy propagate (or handle gracefully / SWR-wrap the hot ones).
- When adding a new Odoo-calling endpoint, do NOT wrap the whole thing in `except Exception → 500`. Let OdooBusy reach the global handler; catch only the specific errors you can handle.
- The diagnostic that found it: the throttled OdooBusy/429 log line (`_note_busy` in shared.odoo_rpc) at the exact timestamp of the 500 — a strong reason to keep that logging. Ties to [[project_odoo_throttle_resilience_pattern]] and [[project_static_gates_miss_semantic_placement]].

## ★ TWO throttle-exception types (2026-09-25 — corrects the assumption above)
There are **two different Odoo rpc helpers, and they raise DIFFERENT exceptions on a 429:**
- `shared.odoo_rpc` raises **`OdooBusy`** → the global `@app.exception_handler(OdooBusy)` → 503 net covers it (unless a local broad-except swallows it first, per above).
- **`dashboard.odoo_rpc` raises `httpx.HTTPStatusError` on a 429, NOT OdooBusy** → the global 503 net does **NOT** cover it, so a dashboard.py endpoint's broad `except Exception → 500` (or fallback) is the ONLY thing that catches it. Found 2026-09-25 as the root cause of the crew clock-in "Could not load employees — yourself only" (GET /owner/api/payroll/employees, dashboard.py) dropping on a transient 429. Fix used: SWR-wrap (swr() catches ANY exception incl. httpx → serves last-good; cold-miss = 503, never 500).
- **So for dashboard.py endpoints, "let OdooBusy propagate" is NOT sufficient** — either SWR-wrap (catches httpx too) or catch `httpx.HTTPStatusError` and return 503. Grep dashboard.py for `except Exception`-to-500 on Odoo paths; each is httpx-429-fragile. MIRROR to Odoo-Migration/memory/.
