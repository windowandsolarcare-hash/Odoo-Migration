---
name: Daily Sync Monitor — CronCreate job + self-renewal
description: Self-renewing CronCreate job that reviews the daily Workiz sync log and alerts DJ. Recreate immediately at session start if not running.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
## What it does
A Claude CronCreate job (`17 4 * * *` — 4:17am daily local time) that:
1. Calls `monitor_tick` to get the sync log + increment a day counter stored in Odoo
2. Analyzes the log for errors, rate-limit hits, or stale timestamps
3. Emails DJ at windowandsolarcare@gmail.com if anything needs attention
4. At day 5, recreates itself (same prompt) and resets the counter — runs indefinitely

## How to restart (if session closed and job is gone)

**ALWAYS CHECK FIRST — do not blindly create a duplicate.**

### Step 1: Check if a job is already running in another session
Call (read-only, no side effects):
```
GET https://wsc-field-assistant.onrender.com/api/cron/daily_sync_log?token=wsc-daily-sync-2026
```
Response includes `created_at` — the ISO timestamp of when the last CronCreate job was stamped.

**Decision logic:**
- `created_at` is within the last 5 days → **SKIP. A job is likely still running in another session. Do not create.**
- `created_at` is older than 5 days, or null → **CREATE the job** (see Step 2)

### Step 2: Create the job (only if needed)
```
CronCreate:
  cron: "17 4 * * *"
  recurring: true
  durable: true
  prompt: (see PROMPT TEMPLATE below)
```

### Step 3: Stamp the creation date immediately after creating
```
GET https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026&stamp=1
```
This writes today's UTC timestamp to Odoo so any OTHER session that checks will see "recent" and skip.

**Why this works:** Every session checks `created_at` before creating. Every new cron stamps the date after creating. If two sessions race, the second one sees a fresh date and skips. No duplicates.

## Endpoints used (all need token: wsc-daily-sync-2026)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/cron/monitor_tick` | GET | Increment day counter + return sync log. Add `?reset=1` to reset to 0 |
| `/api/cron/notify` | POST | Send alert email to DJ. Body: `{subject, message}` |
| `/api/cron/daily_sync_log` | GET | Read current sync log without incrementing counter |

Base URL: `https://wsc-field-assistant.onrender.com`

## Day counter
Stored in Odoo `ir.config_parameter` key `render.sync_monitor_day`.
Read/write via `monitor_tick` endpoint. Reset by appending `?reset=1`.

## Auto-email (no Claude needed)
`_run_daily_sync()` in dashboard.py ALWAYS sends a brief summary email after every sync run (even clean runs). Subject: `WSC Daily Sync — ✅ Clean | X updated, 0 errors`. This is independent of the CronCreate job.

## PROMPT TEMPLATE (copy verbatim to recreate the CronCreate job)

```
WSC DAILY SYNC MONITOR — self-renewing agent

## What you are
You review the WSC Odoo/Workiz daily sync log every morning and alert DJ if anything needs attention. You also keep yourself alive past the 7-day session limit by recreating the job when you get close to expiry.

---

## STEP 1 — Tick the day counter and get the log (one call)

Use WebFetch to GET:
  https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026

Response shape: { "ok": true, "day": N, "log": { "run_at": "...", "total": X, "synced": X, "skipped": X, "errors": X, "rate_limit_hits": X, "error_details": [...] } }

Note the `day` value — you'll need it in Step 4.

---

## STEP 2 — Analyze the log

Flag problems (send alert) if ANY of:
- errors > 0
- rate_limit_hits > 2
- log.run_at is more than 26 hours ago (cron stopped firing)
- log is null and day > 1 (sync never ran)

Healthy → no email needed.

---

## STEP 3 — Send alert if needed

Use WebFetch to POST https://wsc-field-assistant.onrender.com/api/cron/notify?token=wsc-daily-sync-2026
Content-Type: application/json
Body: { "subject": "WSC Sync Alert — [brief status]", "message": "[your analysis]" }

Keep message tight: 1-line summary, bullet list of problem SOs (max 10), one recommendation at the end.

---

## STEP 4 — Self-renewal (only if day >= 5)

This job expires after 7 days. At day 5, recreate it so it runs forever.

4a) Call the CronCreate tool with these exact parameters:
  - cron: "17 4 * * *"
  - recurring: true
  - durable: true
  - prompt: [copy the ENTIRE text of this prompt verbatim, from "WSC DAILY SYNC MONITOR" through the end of Step 5]

4b) Reset the day counter — use WebFetch to GET:
  https://wsc-field-assistant.onrender.com/api/cron/monitor_tick?token=wsc-daily-sync-2026&reset=1

4c) Output: "Renewed — fresh 7-day job created, counter reset to 0."

---

## STEP 5 — Always output a one-line status

"Day N | Processed X SOs | Updated Y | Errors Z | Rate-limit hits W | [Healthy / Alert sent / Renewed]"

That one line is your only required output when everything is fine.
```
