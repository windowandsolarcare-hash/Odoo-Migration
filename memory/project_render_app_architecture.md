---
name: project_render_app_architecture
description: "Render app file-per-app architecture — one Python file per UI app, never mix apps in the same file"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

# Render App Architecture: One File Per App

**Rule:** Every app in the Render assistant has its own dedicated Python router file. Never add routes for App A into App B's file.

**Why:** DJ assigns one Claude agent per app for modifications. If two apps share a file, two agents will both fetch the file, make edits, and one will overwrite the other's work when pushing. One file = one agent = zero conflicts.

**How to apply:** When creating a new app/feature, create a new file in `routers/owner/` and register it in `main.py`. Do NOT add routes to an existing app file unless they genuinely belong to that app.

## Repo: windowandsolarcare-hash/saunders-render-app

### File → App mapping (as of 2026-05-20)

| File | App / HTML page | Routes |
|---|---|---|
| `shared.py` | Shared constants + helpers | No routes — `odoo_rpc`, `workiz_post`, `today_pt`, all config constants |
| `dashboard.py` | Core (stats, timer, search, auth) | `/api/stats/month`, `/api/dashboard`, `/api/timer/*`, `/api/attachment`, `/api/upcoming`, `/api/customer/*`, `/api/sales/day`, `/api/search`, HTML pages, `/api/auth` |
| `field.py` | Field assistant (/ask AI voice) | `/ask`, `/execute`, all tool functions (tool_search_customers etc.) |
| `activities.py` | Activities / Todos | `/api/todos`, `/api/todos/snooze`, `/api/todos/update`, `/api/todos/done`, `/api/todos/reactivate`, `/activities` page |
| `hemet.py` | Hemet Candidates | `/api/hemet_candidates`, `/api/hemet/preview_reactivation`, `/api/hemet/send_reactivation`, `/hemet` page |
| `reactivation.py` | Reactivation Campaign | `/api/reactivation/*`, `/api/followup/*` |
| `timeclock.py` | Timeclock / Payroll | `/api/payroll/clockin`, `/clockout`, `/break`, `/breaks`, `/status`, `/week`, `/shifts`, `/shift/*`, `/api/payroll/gps_ping`, `/api/owntracks/webhook` |
| `shift_review.py` | Shift Review / GPS | `/api/gcal_events`, `/api/payroll/unpaid_jobs`, `/stops`, `/employees`, `/shift_range`, `/stops/match`, `/geocode_*`, `/period_status`, `/unlock_period`, `/gusto_export`, `/upload_docs`, `/shift_review` page, `/pre-deposit` page |
| `quotes.py` | Quote Tool | `/api/quote/*` |
| `payments.py` | Payment Recording | `/api/stripe/*`, `/api/payment`, `/api/upload_zelle_csv`, `/api/record_*`, `/api/fix_payment*`, `/api/void_and_requeue`, `/api/sync_so`, `/api/sync/phase4`, `/api/whoami` |
| `stale_sos.py` | Stale SOs / Pre-Deposit | `/api/stale_sos`, `/stale_sos` page, `/api/stale_sos_with_payment_matches` |
| `submitted_jobs.py` | Submitted Jobs | `/api/submitted_jobs/*`, `/api/scheduled_sos`, `/api/cancel_so/*`, `/submitted_jobs` page |
| `calendar.py` | Calendar | `/calendar` page, `/api/calendar_jobs` |
| `po.py` | Purchase Orders | `/api/po/email_preview` |
| `cron.py` | Cron / Background Tasks | `_run_daily_sync`, `/api/cron/*`, `/api/tasker/*` |
| `planner.py` | Daily Planner | `/planner` page, `/api/planner/*` |
| `new_job.py` | New Job Intake | `/new-job` page, `/api/intake/*` |
| `gps_shifts.py` | TOMBSTONE — do not use | Split into `timeclock.py` + `shift_review.py` in 2026-05-20 refactor |

## Non-owner apps (routers/ root level, no /owner prefix)

| File | App | URL prefix |
|---|---|---|
| `routers/chorelist.py` | Today's List (chores app) | `/` (no prefix) |
| `routers/auth.py` | Auth | `/` (no prefix) |
| `routers/tech/jobs.py` | Tech field app | `/tech` |
| `routers/cheryl/clients.py` | Cheryl app | `/cheryl` |
| `routers/printing/jobs.py` | Printing jobs | `/printing` |
| `routers/printing/watcher.py` | HOF email watcher | `/printing` |

## Adding a new app

1. Create `routers/owner/<app_name>.py` with this header:
```python
from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import datetime, json, re, os, httpx, base64, csv, io
from .shared import *

router = APIRouter()
```

2. Add to `main.py`:
```python
from routers.owner import <app_name> as owner_<app_name>
# ...
app.include_router(owner_<app_name>.router, prefix="/owner")
```

3. Add the HTML file to `static/owner/<app_name>.html`

## Key: shared.py exports

All files import from `.shared` which provides: `odoo_rpc`, `workiz_get`, `workiz_post`, `today_pt`, `resolve_date`, `_owntracks_resolve_emp`, `_hav`, all config constants (`ODOO_URL`, `ODOO_API_KEY`, `WORKIZ_TOKEN`, `WORKIZ_SECRET`, `ANTHROPIC_KEY`, `CLAUDE_HAIKU`, `ODOO_USER_ID`, `DJ_EMPLOYEE_ID`, `PAYROLL_PROJECT_ID`, `GOOGLE_API_KEY`, `OWNER_EMAIL`, `CRON_SECRET`, `GCAL_CALENDARS`, etc.), and field name maps (`WORKIZ_JOB_FIELDS`, `ODOO_CONTACT_FIELDS`).
