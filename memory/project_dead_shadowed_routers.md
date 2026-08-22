---
name: project_dead_shadowed_routers
description: payments.py / timeclock.py / shift_review.py are DEAD — dashboard.py shadows them by router-include order. Editing them is a silent no-op.
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

Discovered 2026-07-15 (full-codebase audit). In `saunders-render-app`, `main.py` includes `owner_dashboard.router` (routers/owner/dashboard.py, ~12,900 lines) BEFORE `owner_payments`, `owner_timeclock`, `owner_shift_review`. `dashboard.py` re-implements every route path those three files define. FastAPI/Starlette matches the FIRST-registered route, so **routers/owner/payments.py (~1,704 lines), timeclock.py (~821), shift_review.py (~1,107) never execute in production** — dashboard.py's copies always win.

**Why it matters:** any fix/feature added to those three files has ZERO effect on the running app. This is a live footgun for future edits (and for me). Confirmed a real divergence already: crew clock-in re-tap OVERWRITES check_in in dead `timeclock.py:62` but is correctly a no-op ("keep earliest") in live `dashboard.py:10403` — so if someone "cleans up" by keeping the wrong copy, payroll hours corrupt.

**How to apply:** before touching payments / timeclock / shift-review logic, edit the copy in **dashboard.py**, not the standalone router file. When the dead files are eventually removed, diff every duplicated function against dashboard.py first — do NOT assume the twins are identical. Related structural bug found same day: two routes in dashboard.py (`:10140` sync_so_verify, `:10210` process_payment_with_sync) include `/owner` in the path string while the router is already mounted at `/owner`, so they actually serve `/owner/owner/...` and the documented path 404s. See [[project_render_app_no_auth_layer]] and the audit artifact https://claude.ai/code/artifact/48119877-c280-488f-8d95-11804b03d628 .
