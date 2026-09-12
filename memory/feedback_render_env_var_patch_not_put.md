---
name: feedback_render_env_var_patch_not_put
description: Always use POST (individual) to add/update a single Render env var — never PUT which replaces ALL env vars and wipes unspecified ones
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 38d7e751-242a-410e-8fc3-0b58bb4701dd
  modified: 2026-09-12T18:48:59.004Z
---

NEVER use PUT on the Render env-vars endpoint to add or update a single variable. PUT replaces the entire env var list — any key not included in the payload gets wiped.

**Why:** 2026-05-14 incident: added ANTHROPIC_API_KEY via PUT, which cleared STRIPE_SECRET_KEY, OWNTRACKS_SECRET, and GCAL_1_URL. Stripe key had to be recovered from memory files; GCAL_1_URL was lost and needs to be re-entered by DJ.

**How to apply:** To add or update a single Render env var, use the individual endpoint:

```bash
curl -X POST "https://api.render.com/v1/services/{serviceId}/env-vars" \
  -H "Authorization: Bearer {RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"key": "MY_KEY", "value": "my_value"}'
```

To update multiple vars safely, fetch the full list first, merge in the new values, then PUT the complete merged set. Or add vars one at a time via POST.

**Never** PUT with only the vars you know about — always assume there are others you haven't captured.

**Merged from the former `feedback_render_put_env_vars` (2026-09-12) — extra points to keep:**
- It happened TWICE — 2026-05-14 (this incident) AND again 2026-05-15 (setting only GCAL_1_NAME/GCAL_1_URL wiped ODOO_API_KEY + others). Recurring class, not a one-off.
- **Symptom to recognize:** after a bad PUT the service deploys fine but returns **Odoo AccessDenied on every request** — if you see that, check the Render env vars FIRST (ODOO_API_KEY got wiped).
- The service `wsc-field-assistant` (srv-d78le0fkijhs738dsli0) needs a full set present (ODOO_API_KEY, ANTHROPIC_API_KEY, GITHUB_TOKEN, GOOGLE_API_KEY, STRIPE_SECRET_KEY, OWNTRACKS_SECRET=`wsc-ot-2026`, OWNER_EMAIL, GCAL_1_*, GMAIL_SCENIC_APP_PASSWORD, …). **Current VALUES live in the Render dashboard + local key files, NOT in memory** (the old note here inlined a since-rotated Odoo key + retired Workiz token/secret — never re-store live secrets in a memory file; secret-scanning blocks the mirror).
