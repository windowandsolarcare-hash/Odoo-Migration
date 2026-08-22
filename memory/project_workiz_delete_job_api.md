---
name: Workiz delete job API
description: How to hard-delete a Workiz job via API — endpoint, required fields, and common mistakes
type: project
---

Workiz jobs CAN be hard-deleted via API using this pattern:

```bash
curl -s -X POST "https://api.workiz.com/api/v1/{API_TOKEN}/job/delete/{UUID}/" \
  -H "Content-Type: application/json" \
  -d '{"auth_secret": "{AUTH_SECRET}", "ID": "{UUID}"}'
```

Response on success: `{"flag":true,"msg":"Job deleted"}`

**Why:** The delete endpoint exists but requires `ID` = the job UUID in the POST body (not just in the URL). Without it you get `"ID: Field is Required"`. Also requires `api.workiz.com` base URL — using `app.workiz.com` hits a Cloudflare block.

**How to apply:**
- Use `api.workiz.com` (NOT `app.workiz.com`) for all Workiz API calls
- Pass `"ID": "UUID"` in the JSON body along with `auth_secret`
- UUID goes in both the URL path AND the body `ID` field
- Rate limit kicks in around 13 rapid deletes — add `sleep 30` between batches if deleting many jobs
- Workiz's own API docs don't mention this endpoint, and the old cleanup script incorrectly stated "Workiz doesn't have a delete API" — it does

**Checking if a job is deleted (GET behavior):**
When you GET a deleted/non-existent job, Workiz returns **HTTP 204 (No Content)** — NOT 404. Empty body.
- 200 with data → job exists
- 200 with empty data → job gone
- 204 → job gone (no content)
- 404 → job not found

Always treat both 204 and 404 as "confirmed deleted" when checking before an Odoo SO deletion.
