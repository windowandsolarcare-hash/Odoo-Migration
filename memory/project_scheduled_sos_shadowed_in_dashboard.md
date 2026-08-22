---
name: project_scheduled_sos_shadowed_in_dashboard
description: "Maintenance-to-Schedule \"1 job\" bug = /api/scheduled_sos DUPLICATED in dashboard.py (shadows submitted_jobs.py); dashboard copy kept the state-in-sale/done filter that hid all draft Submitted next-jobs"
metadata: 
  node_type: memory
  type: project
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

The **Maintenance to Schedule** app (`/owner/maintenance`, page `static/owner/maintenance.html`, backend `routers/owner/submitted_jobs.py`) lists Phase-5 auto-created **Submitted** next-jobs that still need a day/slot. The list comes from `GET /api/scheduled_sos`.

**Bug (DJ reported "1 job, not accurate" 2026-06-21):** `/api/scheduled_sos` is **defined TWICE** — `dashboard.py` (~line 7567) AND `submitted_jobs.py` (line 134). `main.py` includes `owner_dashboard.router` (line 134) **before** `owner_submitted_jobs.router` (line 144), so **dashboard.py's copy SHADOWS** the maintained one in submitted_jobs.py. Same shadow pattern as [[project_reactivation_route_shadowed_in_dashboard]].

The submitted_jobs.py copy had already been fixed (DJ 2026-06-18) to drop the state filter — but it never ran. The **dashboard.py copy still had `['state', 'in', ['sale', 'done']]`**, which hides every **draft** Submitted next-job. Phase-3-built next-jobs are DRAFT quotations, so this left only the 1 that happened to be confirmed (state=sale). Real counts (company 1, future-dated): 42 Submitted future = 41 draft + 1 sale. With the bad filter → 1.

**Fix:** changed the dashboard.py copy's filter to `['state', '!=', 'cancel']` (matching submitted_jobs.py intent). Now both copies behave identically, so include-order no longer matters. Live count went 1 → 42. Commit `18b3fd45`.

**Data facts (verified 2026-06-21):** all Submitted/not-cancel = 627, of which only 42 are date_order >= today and **585 are PAST-dated** (next-visit target date passed, never scheduled). Submitted jobs are 100% company_id=1.

**Overdue toggle added 2026-06-21** (commits dashboard 37d96cbe / maintenance.html 03aa8bee): `/api/scheduled_sos` now takes `?overdue=1`. Default (no param) = future-dated (42). Overdue branch = past-dated within last 183 days, `date_order asc` (most overdue first), and FILTERS NOISE: domain excludes job_type in [Reactivation Lead, Personal Time, Quote, Touch up] + blank job_type; Python strips test names (contains 'test' / starts 'jane doe' / 'dan saunders'). That noise filter takes the raw 116 past-6mo down to the **21 real maintenance backlog**. Each job gets `days_overdue`; response carries `overdue` bool. Page `maintenance.html` has an Upcoming/⚠️ Overdue pill toggle (`setMode`), overdue cards show a red `Nd overdue` badge. DJ chose to keep the DEFAULT list future-only; overdue is opt-in via the toggle. Edited the dashboard.py copy (the one that runs); submitted_jobs.py copy NOT updated → the two `scheduled_sos` copies are now DIVERGED again (dashboard has overdue param, submitted_jobs doesn't). Harmless since submitted_jobs copy is shadowed/dead, but delete-the-dup is still the durable fix.

**Why:** route shadowing means the file you edit may not be the file that runs. A "fixed" endpoint can still serve stale logic if an earlier-registered router defines the same path.

**How to apply:** when an owner-app endpoint behaves like old code despite a fixed file, grep ALL `routers/owner/*.py` for the route path — dashboard.py frequently holds an older duplicate that wins by registration order. Fix (or delete, with DJ approval) the dashboard.py copy, not just the dedicated router. The dashboard.py `scheduled_sos` duplicate is now in sync but still DEAD/redundant — candidate for deletion to prevent re-divergence.
