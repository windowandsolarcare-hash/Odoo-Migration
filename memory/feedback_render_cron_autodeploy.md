---
name: Render cron autoDeploy causes duplicate runs on commit push
description: Render cron jobs with autoDeploy=yes fire an extra run on every code commit — disable via REST API to prevent duplicate reports
type: feedback
originSessionId: 7ad343ab-c028-433d-86f6-989416b269ac
---
Render cron jobs have `autoDeploy: yes` by default. This means every commit pushed to the watched branch triggers an immediate rebuild AND run of the cron, in addition to its scheduled time.

**Why:** Overnight sessions pushing multiple commits caused the daily sync to run 2-3x, sending duplicate emails to DJ.

**Fix:**
```bash
curl -X PATCH https://api.render.com/v1/services/{serviceId} \
  -H "Authorization: Bearer {RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"autoDeploy": "no"}'
```

RENDER_API_KEY is in `~/.claude/mcp.json` under `render → headers → Authorization`.

Service IDs:
- WSC Daily Sync: crn-d7t3c4i8qa3s73f64fhg (fixed 2026-05-08)
- WSC Submitted Jobs Scan: crn-d7t3l937uimc73dolul0 (not sending emails, low priority)

**How to apply:** Any time a new Render cron job is created, immediately disable autoDeploy via the REST API. The Render MCP `update_cron_job` tool cannot do this — must use the REST API directly.
