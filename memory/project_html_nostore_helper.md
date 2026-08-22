---
name: project_html_nostore_helper
description: "Shared html_nostore() helper kills the recurring stale-owner-page class. Lives in routers/owner/shared.py (exported via __all__) + a LOCAL MIRROR in dashboard.py (self-contained, no shared import). Every owner page serve returns through it."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-20T21:24:05.722Z
---

**The recurring "stale owner page" bug class + its fix (2026-08-20, Lead-approved, Specialists shipped).**

Owner HTML pages served with a **bare `HTMLResponse(f.read())` / `return f.read()` (no Cache-Control) let the browser/PWA cache the page for days** — DJ (and Cheryl) keep seeing OLD JS after a deploy. Hit repeatedly (Idea Board edit/delete looked "not shipped" until `?fresh=1`). Recurring class: `project_owner_page_nostore_cache`, `project_pwa_stale_page_reload`, `project_sw_cache_stale_page`.

**The fix = one shared helper every page route calls:**
- **`html_nostore(html, status_code=200)`** in **`routers/owner/shared.py`** — a **per-route wrapper around the returned HTMLResponse** (NOT a path-prefix middleware, so it covers hand-rolled routed HTML too — the gap Portal hit on `/p/<token>`). Exported in `__all__`; every router doing `from .shared import *` gets it (field/ideas/reactivation/hemet/payments).
- Emits `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` + `Pragma: no-cache` + `Expires: 0`.
- **★ dashboard.py does NOT import shared.py** — it is self-contained (its own HTMLResponse import + its own odoo_rpc, per [[project_odoo_rpc_429_retry]]). So it carries a **LOCAL MIRROR** of `html_nostore` rather than a `from .shared import` (avoids coupling the isolated file). Two defs, one policy — same pattern as the two odoo_rpc helpers. **If you edit one html_nostore, edit both.**

**Applied to every owner page serve (2026-08-20):** dashboard.py **14 routes** (index, index_classic, quick, activities, quote_rates, deleted_jobs, stale_sos, submitted_jobs, calendar, hemet, pre_deposit, shift_review, planner, field — incl. upgrading the 2 that had the weaker `no-store, must-revalidate`), ideas.py `/ideas`, reactivation.py (reactivation + waiting), hemet.py. Commits: shared 0a65253, dashboard e6aa0e7, ideas d353749, reactivation 2d90101, hemet b55601f.

**LIMITS — don't over-trust it:** ① Prevents FUTURE staleness only. A page the phone ALREADY cached in the **PWA service worker** stays stale until an SW-cache version bump (v2_apps.js already reloads after 30-min hidden) — SW versioning is a SEPARATE track. ② `no-store` DEFEATS the ETag/304 cheap-path *in theory*. Portal adopted the helper on `/p/<token>` + `/owner/portal-links` (portal.py 5a70e486) and **MEASURED the 304 saving to be imaginary here:** Starlette's `FileResponse` does NOT honour `If-None-Match` — a conditional request returns **200 with the full bytes, never a 304**. So `no-store` costs nothing over `no-cache` on this stack → the stronger shared policy wins at zero cost, and the offered `revalidate=True` helper mode was **dropped as moot** (one policy app-wide). ★ **General trap:** an ETag in the response is NOT evidence revalidation works — the server must actually answer `If-None-Match`, and Starlette FileResponse doesn't. Send a REAL conditional request before trading freshness for a saving that may not exist. (Customer portal registers no service worker, so for customers Cache-Control genuinely IS the whole fix — the SW-cache caveat is owner-side only.)

**Verifying a dashboard.py edit — CRLF DIFF TRAP:** GitHub-fetched files are CRLF; a Python-rewritten local copy may be LF → a raw `diff` shows EVERY line changed (meaningless, ~2× line count). Always `tr -d '\r'` BOTH sides before diffing to see the REAL change set. (Line-count delta is the honest quick guard: I added ~12 lines = the helper block; the N return-line swaps are in-place.) See [[feedback_python_multiline_replace_crlf]] / CLAUDE.md "APPROACHES THAT FAILED".
