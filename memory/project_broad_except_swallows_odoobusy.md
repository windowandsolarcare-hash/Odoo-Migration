---
name: project_broad_except_swallows_odoobusy
description: "A local broad `except Exception → 500` in an endpoint swallows OdooBusy before the global 503 handler can fire — that's why \"rerun 500s\" appeared under Odoo 429s"
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T17:48:45.408Z
---

**A per-endpoint broad `except Exception as e: return JSONResponse(..., status_code=500)` is the reason OdooBusy showed up as a 500 instead of a 503.** (Found 2026-09-23, batch-3b piece-3, Specialists.)

`shared.odoo_rpc` raises **`OdooBusy`** on Odoo 429 / timeout / 5xx (fail-fast, timeout=5). There is a global `@app.exception_handler(OdooBusy)` in main.py that turns it into a clean **503**. But `OdooBusy` is an `Exception` subclass, so ANY endpoint that wraps its body in a broad `try/except Exception → status_code=500` **catches OdooBusy locally and rewraps it as a 500 BEFORE the global 503 handler ever sees it.** Under an Odoo-429 burst these endpoints returned 500s (the "rerun 500s" the OdooBusy throttle-log pinpointed), never 503, so the client couldn't tell "Odoo busy, retry" from a real bug.

**Confirmed offenders (fixed in batch-3b):** `/owner/api/outreach/pipeline` (outreach.py) and `/owner/api/maintenance/stranded` (submitted_jobs.py). Likely more of this shape exist — grep for `except Exception` + `status_code=500` in the routers.

**Why:** the global handler only fires if the exception PROPAGATES out of the route. A local broad except stops propagation.

**How to apply:**
- When an endpoint should serve degraded (last-good) or let Odoo-busy surface as 503, do NOT catch `OdooBusy` in a local broad except. Either narrow the except to the errors you actually handle, or `raise` (re-raise) so it reaches the global handler.
- For read/display endpoints, the fix pattern is [[project_swr_stale_while_revalidate]]: wrap in `swr()` with a builder that lets `OdooBusy` propagate (submitted_jobs: flipped `except Exception: return 500` → `except Exception: raise`; outreach: builder lambda has no local except, and `pipeline_counts`/`classify_customers` were verified to have none either). Under a 429 SWR then serves last-good / empty skeleton at 200 instead of a 500.
- Verify a builder's whole call chain has no INNER broad-except that swallows OdooBusy (a nested helper `except Exception: pass/return partial` re-introduces the bug and also hides the busy state).

Related: [[feedback_odoo_verify_content_not_status]] (200≠success), the OdooBusy fail-fast contract, and the batch-3b HOME-cold-load threadpool-hog work.
