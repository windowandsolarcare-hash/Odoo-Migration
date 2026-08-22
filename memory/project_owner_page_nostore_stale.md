---
name: project_owner_page_nostore_stale
description: "\"Fix deployed but DJ doesn't see it\" on an owner page = stale cached HTML because the route returns f.read() with no Cache-Control. Add no-store."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
  modified: 2026-07-22T15:21:06.199Z
---

**Recurring root cause.** When DJ reports a deployed UI fix "isn't there" / "button missing" / "changes not made or I can't see them" on an owner page, and the live GitHub file + live API both prove the fix IS deployed and correct, the cause is almost always a **stale cached HTML page on his phone**.

Owner-page routes that do `return f.read()` (raw string) send **no `Cache-Control` header**, so the browser/PWA caches the HTML and keeps serving the pre-fix copy across deploys. (sw.js is pure-passthrough and caches nothing, so it's the HTTP cache, not the service worker.)

## How to confirm it's a cache issue (don't theorize — verify)
1. `gh api .../contents/<page>.html | base64 -d` → confirm the live file has the fix.
2. `curl -s https://wsc-field-assistant.onrender.com/owner/<route> | grep <new text>` → confirm Render serves it.
3. For data-driven gates, hit the live JSON endpoint directly (most `/owner/api/*` ignore `access_code` server-side, so `?access_code=x` works) and confirm the records pass the gate.
If all three pass, it's DJ's cache — not the code.

## Fix (both halves)
- **Route:** return `HTMLResponse(f.read(), headers={'Cache-Control': 'no-store, must-revalidate'})` instead of bare `f.read()`. (`HTMLResponse` already imported in these routers.)
- **DJ:** must fully close & reopen the app (or hard-refresh) ONCE to clear the already-cached copy; no-store only prevents the NEXT staleness.

## Confirmed instances
- **2026-07-22 — `dashboard.py` `/field` (the MAIN field app page!)** was still bare `f.read()` with NO Cache-Control (commit f9276c3d added no-store). This bit hard: two correct field.html fixes (gate-code on schedule cards + a repaint fix) were verified live on the server via `curl .../static/owner/field.html | grep <marker>` yet DJ kept seeing the OLD behavior on his phone. field.html is a SPA — a data refresh only re-fetches data, it does NOT reload the page JS, so the stale HTML kept running the old build indefinitely. Immediate unblock given to DJ = a cache-busting URL `…/owner/field?v=0722` (new query string = new cache key = forced network fetch, also dodges the SW navigate cache). Sibling routes `/quick` `/classic` `/timeclock` in dashboard.py are STILL bare f.read() — same latent bug.
- `order.py` `/new-order`, `new_job.py` `/new-job`, `activities.py` `/activities` (commit b90d508) — the re-engagement "Launch Re-engagement Text" button was present in live code (line 741, `detailOpenFollowup()`, gated by `isReengagementTask` = `source==='task' && summary.startsWith('Re-engagement:')`; 196 tasks passed) but DJ saw no button because his phone had the old `activities.html`.

## SWEEP CANDIDATE
Other `@router.get(... HTMLResponse)` owner routes still doing bare `f.read()` will have the same bug. Grep `return f.read()` across `routers/owner/*.py` and add no-store to each. See [[project_clockin_bar_customer_overlay]] and [[feedback_ios_date_input_appearance]] (same "DJ can't see the deployed fix" symptom).
