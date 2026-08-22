---
name: session_may14_summary
description: "2026-05-14/15: time_utc fix, Render env var PUT incident, voice fix, OwnTracks ping-based home detection"
metadata: 
  node_type: memory
  type: project
  originSessionId: 38d7e751-242a-410e-8fc3-0b58bb4701dd
---

## Key things done

**time_utc fix** — `tool_get_schedule` was missing `time_utc` in the job dict it builds, so today's jobs showed "Scheduled" with no time in the field modal. Added `'time_utc': so['date_order'][11:16] if so.get('date_order') else '?'` to match what the upcoming endpoint already had. Deployed commit `51e2e3f2`.

**Render env var PUT incident** — Used PUT (replace all) instead of fetch-merge-PUT when adding ANTHROPIC_API_KEY. Wiped STRIPE_SECRET_KEY, OWNTRACKS_SECRET, GCAL_1_URL, GMAIL_SCENIC_APP_PASSWORD. Rule saved to CLAUDE.md, MEMORY.md, SHARED_MEMORY.md. Pattern: always GET first, merge in Python, then PUT full list.

**Restored env vars:**
- `ANTHROPIC_API_KEY` — restored (voice was broken without it)
- `STRIPE_SECRET_KEY` — recovered from memory: `[STRIPE_KEY — in Render env]`
- `OWNTRACKS_SECRET` — recovered from OwnTracks app URL: `wsc-ot-2026`

**Still missing from Render (as of 2026-05-15):**
- `GCAL_1_URL` — Google Calendar ICS URL for W&SC calendar (DJ needs from Google Calendar settings)
- `GITHUB_TOKEN` — GitHub personal access token with repo scope (DJ needs to generate)
- `GMAIL_SCENIC_APP_PASSWORD` — dan@scenicartprint.com Gmail app password (DJ needs from Google Account security)

**OwnTracks ping-based home detection** — Geofence enter/leave events are unreliable on mobile (OS drops them). New approach: on every location ping, compare coords to home. If within radius AND clocked in ≥30 min → clock out. If <30 min → cancel attendance (short errand).
- Home coords stored in Odoo ir.config_parameter: `owntracks.home.1.lat=33.8110`, `owntracks.home.1.lng=-116.3822`, `owntracks.home.1.radius=200`
- Pattern extensible: add `owntracks.home.{emp_id}.*` for Danny when needed
- Deployed commit `5ea5f589`

**Render env vars — correct current state (all set):**
ANTHROPIC_API_KEY, WORKIZ_TOKEN, WORKIZ_SECRET, STRIPE_SECRET_KEY, OWNER_EMAIL, ODOO_API_KEY, GCAL_1_NAME, OWNTRACKS_SECRET

**Render only supports PUT for env-vars** — no POST/PATCH for individual vars. Always fetch full list first, merge, PUT complete set.
