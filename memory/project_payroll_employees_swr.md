---
name: project_payroll_employees_swr
description: Clock-in crew list GET /owner/api/payroll/employees is now SWR-hardened + boot-prewarmed; dashboard.odoo_rpc raises httpx (not OdooBusy) on 429 so the global 503 net misses it.
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-25T15:59:25.953Z
---

**GET `/owner/api/payroll/employees`** (the clock-in modal's crew list) is now SWR-hardened. Fixed 2026-09-25 (Specialists, Lead-directed live-ops expedite) after DJ's 8:30 AM PT morning clock-in showed **"Could not load employees — clock in yourself only."**

**Root cause (a real, systemic find):** `dashboard.py`'s own `odoo_rpc` (defined at dashboard.py:287) does `resp.raise_for_status()` → on a transient Odoo **429 it raises `httpx.HTTPStatusError`, NOT the shared `OdooBusy`**. So the global `@app.exception_handler(OdooBusy)→503` net does **NOT** cover any endpoint that uses dashboard.py's local rpc. The old handler's broad `except Exception → 500` turned the blip into a hard 500 → client dropped to "yourself only". (See [[project_broad_except_swallows_odoobusy]] — Lead extended that memory to flag this 2nd throttle-exception type. Any dashboard.py endpoint with a broad-except→fallback has the same gap.)

**Fix (LIVE — dashboard.py commit 7984d269 via safe_deploy, main.py 96b39d8e; Render HEAD live 15:57 UTC):**
- **dashboard.py:~13287** — extracted `_build_payroll_employees()` (the `hr.employee` search_read, byte-identical) + wrapped the handler in `_swr.swr('payroll:employees', _build_payroll_employees, ttl=300.0, cap=6.0, empty=None)`. `swr()` catches ANY builder exception (incl. httpx) → serves **last-good crew** on a transient 429. Only a true cold-miss (no last-good yet) returns **503 (retry), never 500**. The LIVE handler is dashboard.py — `shift_review.py:628` is the DEAD shadow.
- **main.py** lifespan `_prewarm_loop` boot-only block — `prewarm('payroll:employees', _pd._build_payroll_employees)` so last-good exists from ~startup (crew is stable → boot-only + on-demand ttl=300, no periodic Odoo hit).

**Residual gap (open, optional fast-follow):** the sub-second window at instance restart *before* the boot prewarm populates the cache — a clock-in that also hits a 429 there still 503s, and the CLIENT (`v2_field.html:1822`, `field.html:3777`, `clockin-bar.js:136`) currently drops to "yourself only" on ANY non-ok. A client **retry-on-503** closes it but needs a SW cache bump (v10→v11) = heavier deploy; deferred off the expedite. **Why:** don't take a SW bump on a hotfix. **How to apply:** if DJ still sees "yourself only" right after a deploy, add the client retry-on-503 (2-3 static files + SW bump). See [[feedback_no_deploy_during_customer_payment]] (this shipped in a Dispatcher-confirmed booking lull, two deploys).
