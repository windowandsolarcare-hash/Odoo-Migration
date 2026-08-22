---
name: project_daily_sync_zapier_survivor
description: "The daily \"WSC Daily Sync\" report emails survive in a ZAPIER zap even though the app-side sync is fully retired — the zap runs its own copy + emails at 4am PT. Only DJ can turn it off (in Zapier)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T13:41:50.290Z
---

**Symptom (2026-08-05):** DJ still gets a "WSC Daily Sync — …| N updated, N errors" email every morning (~4:00 PDT), from windowandsolarcare@gmail.com, despite the daily Workiz→Odoo sync being "retired."

**All app/Render triggers are confirmed OFF:**
- `main.py` internal APScheduler `_scheduled_daily_sync` (4:17am) — **commented out 2026-08-03** (line ~159). The 4:17 emails stopped after Aug 2 (matches).
- Render cron **"WSC Daily Sync"** (`crn-d7t3c4i8qa3s73f64fhg`, `17 4 * * *`) — **suspended** by user 2026-07-27.
- `routers/owner/cron.py` `_run_daily_sync()` — first line is `return` (no-op since 2026-08-03); the endpoint `GET /api/cron/daily_sync` only `background_tasks.add_task(_run_daily_sync)` → does nothing. Live deploy is current (verified via list_deploys, autoDeploy=on).

**The survivor = a Zapier zap.** App request logs show `GET /owner/api/cron/daily_sync?token=wsc-daily-sync-2026` at ~11:01 UTC daily from **Google Cloud IP 104.154.179.196** (Zapier runs on GCP). Since the endpoint is a no-op yet a real report (real SO counts) still emails ~5 min later, the zap runs its OWN copy of the old sync code (Workiz→Odoo + Gmail send) and just pings the dead endpoint as a leftover. The email format strings ("Rate-limit hits", "Actually updated") exist ONLY in cron.py — so the zap has a pre-Aug-3 copy of that logic.

**Fix = DJ turns off the zap in Zapier** (a daily/scheduled zap firing ~4am that runs the sync / sends "WSC Daily Sync"). NOT reachable via the Zapier MCP (that only exposes actions Claude can run, not the user's standing zaps), and NOT killable server-side (the zap talks to Workiz/Odoo directly, bypassing the app). token `wsc-daily-sync-2026` is shared by other crons (submitted_jobs_scan, a2p_watch) so DON'T rotate it.

**What Daily Sync did (safe to fully kill):** Workiz→Odoo SO sync (retiring w/ Workiz) + rode the payroll (`run_biweekly_trigger`) and weekly-digest specialists. Those now have independent triggers — payroll = new dedicated "WSC Payroll" cron ([[project_payroll_cron_dependency]]); weekly digest = `main.py` `_scheduled_weekly_report` (Mon 7am, still active). So nothing important is lost.
