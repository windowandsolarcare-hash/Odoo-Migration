---
name: project_render_cron_jobs
description: "The 4 Render cron jobs (Daily Sync SUSPENDED 2026-07-26 — triple-trigger fix), how to change a cron schedule via the Render API, A2P watcher twice-daily. Render crons run UTC."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
  modified: 2026-07-27T04:46:41.893Z
---

# Render cron jobs inventory + how to edit a cron schedule (2026-07-04)

## ★ 2026-07-26 — Daily Sync triple-trigger fixed ("why does sync email 3×/day")
DJ was getting the Daily Sync email 2-3×/day. Three independent triggers found: (1) an OLD **Zapier
scheduled zap** GET-ting `/owner/api/cron/daily_sync?token=…` ~04:02-04:04 PDT (confirmed via
Render HTTP logs — Google-Cloud IP 104.154.179.196; Zapier minute-drift signature) — **DJ must
switch this zap off in Zapier** (couldn't reach Zapier MCP from session); (2) the in-app
APScheduler in main.py at 04:17 **PDT** — the intended, KEPT owner; (3) the "WSC Daily Sync"
Render cron `17 4 * * *` which is 04:17 **UTC = 9:17 PM PDT** (UTC mistake at creation) —
**SUSPENDED via API 2026-07-26** (`POST /services/crn-d7t3c4i8qa3s73f64fhg/suspend`). Also set
`autoDeploy: no` on **WSC Submitted Jobs Scan** (was `yes` → re-ran on every push; the May-08
bug pattern, never fixed on this one). Note: Submitted Jobs Scan's `3 5 * * *` = 22:03 PDT (same
UTC quirk) — left as-is, flagged to DJ as optional. Recurring sync error: SO 004858 "No tech
assigned" — needs manual tech assignment in Workiz UI (API can't set tech).

Workspace `tea-d78l9fqdbo4c7388n9og`. All hit endpoints on `wsc-field-assistant.onrender.com` with query `?token=wsc-daily-sync-2026` (= CRON_SECRET). Schedules are **UTC**.

| Cron (service id) | Schedule (UTC) | Does | Endpoint |
|---|---|---|---|
| **WSC A2P Watcher** `crn-d8u8r368bjmc73dhq7kg` | `0 0,16 * * *` (was `*/30 * * * *`) = **twice daily, 9am & 5pm PT** | Polls Twilio for A2P/10DLC registration status (business profile / brand / campaign); pushes DJ on any status change. TEMPORARY. | `/owner/api/cron/a2p_watch` |
| **WSC Daily Sync** `crn-d7t3c4i8qa3s73f64fhg` | `17 4 * * *` | Heavy nightly Workiz↔Odoo reconcile via `dashboard._sync_so_with_workiz`; emails DJ on errors. 600s timeout. | `/owner/api/cron/daily_sync` |
| **WSC Submitted Jobs Scan** `crn-d7t3l937uimc73dolul0` | `3 5 * * *` | Refreshes the "needs scheduling" / submitted-jobs data (`_submitted_jobs_refresh_worker`). | `/owner/api/cron/submitted_jobs_scan` |
| **WSC Printing — HOF Email Check** `crn-d84cabd8nd3s73cus3hg` | `0 6 * * *` | Saunders Printing / NBHOF purchase-order watcher (company 3, not W&SC). | `/printing/api/check-po` |

(Web service = `wsc-field-assistant` `srv-d78le0fkijhs738dsli0`.)

## ★ How to change a cron schedule (the Render MCP can't)
- `mcp__render__update_cron_job` does **NOT** support schedule edits — it returns "Updating a cron job directly is not supported. Please make changes using the dashboard or the API."
- Use the raw Render API: `PATCH https://api.render.com/v1/services/{cronId}` with body **`{"serviceDetails":{"schedule":"0 0,16 * * *"}}`**. ★ A top-level `{"schedule":...}` is silently IGNORED — the field lives under `serviceDetails`. Verify with `GET /v1/services/{id}` → `serviceDetails.schedule`.
- Needs the Render API key (see [[feedback_api_keys_via_file]]).

## A2P watcher: cost + auto-cancel reminder
- It was every 30 min (48×/day) — the bulk of the ~$3.20/mo Render "Cron Jobs" line. Slowed to twice-daily 2026-07-04 (~95% cheaper) at DJ's request. Render bills crons by **actual run-time**, so frequency scales cost roughly linearly.
- It's only needed while awaiting Twilio A2P approval. cron.py (commit 054efcf) now makes the **"A2P APPROVED - you can text now"** notification also tell DJ to turn OFF the "WSC A2P Watcher" cron — self-reminder to cancel, so nothing to track. When approved, delete/suspend `crn-d8u8r368bjmc73dhq7kg`.
