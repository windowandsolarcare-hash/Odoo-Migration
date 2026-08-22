---
name: render-put-env-vars-wipes-all
description: Render PUT /env-vars API replaces ALL env vars — never use it with a partial list
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bcd62e72-19be-4a09-af3f-a38378b2ba9e
---

**NEVER call `PUT /services/{id}/env-vars` with a partial list of env vars.**

The Render API PUT endpoint replaces the entire env var set. On 2026-05-15, setting only GCAL_1_NAME and GCAL_1_URL wiped ODOO_API_KEY, WORKIZ_TOKEN, ANTHROPIC_API_KEY, GITHUB_TOKEN, and all other vars. The service deployed successfully but returned Odoo AccessDenied on every request.

**Why:** PUT = full replace, not merge/patch. Render has no PATCH endpoint for env vars.

**How to apply:** Before setting any env var via the Render API, first GET the current list, merge your new vars in, then PUT the full combined list. Or use the Render dashboard for one-off additions to avoid the risk entirely.

## Known Render env vars for wsc-field-assistant (srv-d78le0fkijhs738dsli0)
These must ALL be present. If the service breaks with AccessDenied, check these first:
- ODOO_API_KEY: `7e92006fd5c71e4fab97261d834f2e6004b61dc6`
- WORKIZ_TOKEN: `api_1hu6lroiy5zxomcpptuwsg8heju97iwg`
- WORKIZ_SECRET: `sec_334084295850678330105471548`
- STRIPE_SECRET_KEY: in reference_stripe_mcp.md
- OWNTRACKS_SECRET: `wsc-ot-2026`
- OWNER_EMAIL: `windowandsolarcare@gmail.com`
- GCAL_1_NAME: `WSC Calendar`
- GCAL_1_URL: `https://calendar.google.com/calendar/ical/windowandsolarcare%40gmail.com/private-2ca17ff035e008c71d6fe4d556f44ae8/basic.ics`
- ANTHROPIC_API_KEY: unknown — must be re-entered from Render dashboard
- GITHUB_TOKEN: unknown — must be re-entered from Render dashboard
- GOOGLE_API_KEY: unknown — must be re-entered from Render dashboard
- GMAIL_SCENIC_APP_PASSWORD: unknown — must be re-entered from Render dashboard
