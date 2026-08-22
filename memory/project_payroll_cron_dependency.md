---
name: project_payroll_cron_dependency
description: "The payroll specialist fires via run_biweekly_trigger, which rode on the (suspended) Daily Sync cron — so payroll went silent. Fixed with a dedicated \"WSC Payroll\" Render cron."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T09:04:48.821Z
---

**Why the payroll specialist stopped appearing (found 2026-08-05):** `specialist_payroll.run_biweekly_trigger()` is invoked server-side from `routers/owner/cron.py`'s **daily_sync** handler. The Render cron **"WSC Daily Sync"** (hits `/owner/api/cron/daily_sync`) was **suspended by the user on 2026-07-27** — so daily_sync (and the payroll trigger it carries) hasn't run since. No payroll card ⇒ Daily Sync being off.

**Payroll cadence:** biweekly Mon–Sun, 14-day periods anchored to `_PERIOD_ANCHOR = 2026-04-20`. `run_biweekly_trigger` prepares the JUST-ENDED period's card only if it ended within the last **5 days** (idempotent — `prepare_payroll` self-withdraws if already submitted/approved; `submit_item` upserts by id `payroll:<start>_<end>`). So the trigger is DAILY-SAFE.

**Fix (2026-08-05):** created a dedicated Render cron **"WSC Payroll"** (id `crn-d9pfp5m1egvs73fbavug`, schedule `0 15 * * *` = 8am PDT daily, GET `/owner/api/payroll/cron`, not suspended) so payroll no longer depends on Daily Sync. First real card lands Mon 2026-08-10 (period 2026-07-27→08-09), then every other Monday. If Daily Sync is later un-suspended, both call the same idempotent trigger — no double-post.

**Endpoints:** `GET /api/payroll/cron[?today=YYYY-MM-DD]` (no token; posts only when fresh — `?today` future date WILL submit a card, so don't test with a future date on prod), `POST /api/payroll/prepare {start,end}` (defaults to last WEEK via `_default_period`, not biweekly). Feed card id `payroll:<start>_<end>`. Caution 2026-08-05: testing `?today=2026-08-10` posted a premature card for the not-yet-ended period; removed it (+ a stale `payroll:2026-07-20_2026-07-26`) from `wsc.feed.items`.
