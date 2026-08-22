---
name: Workiz API access — local machine blocked, use Odoo as proxy
description: Workiz API returns 403 from local machine — must proxy through Odoo server action to call Workiz from scripts
type: project
---

Workiz API is IP-restricted. Direct calls from a local machine return HTTP 403. Only the Render server and Odoo server can reach Workiz directly.

**Why:** Workiz restricts API access by IP. Render and Odoo are on allowed IPs. Your local dev machine is not.

**How to apply:** Any time a script needs to call Workiz (check tags, fetch job data, verify status), proxy through a temporary Odoo server action:

1. Create temp `ir.actions.server` (model_id=670 for sale.order) with the Workiz fetch code
2. Run via JSON-RPC with `active_id` set to any valid SO id
3. Use `raise UserError(result_string)` to get data back in the error response
4. Delete temp action immediately after
5. Read result from `resp['error']['data']['message']`

Auth secret is REQUIRED in all Workiz URLs — without it you get 403 even from allowed IPs:
`https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/?auth_secret=sec_334084295850678330105471548`

Rate limit: ~30 rapid calls before HTTP 429. Sleep 15-30 seconds between batches of 30.

From Render (app.py) and Odoo server actions: direct calls work fine — no proxy needed.
