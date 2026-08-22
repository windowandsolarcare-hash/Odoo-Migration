---
name: project_owntracks_home_detection
description: OwnTracks geofence events are unreliable — use ping-based home detection instead. Home coords stored in Odoo ir.config_parameter.
metadata: 
  node_type: memory
  type: project
  originSessionId: 38d7e751-242a-410e-8fc3-0b58bb4701dd
---

OwnTracks geofence transition events (enter/leave) are unreliable on mobile — the OS drops them when the app is backgrounded. Location pings are reliable (periodic).

**Solution deployed 2026-05-15:** On every location ping, server-side home detection runs:
- Fetch home coords from `ir.config_parameter`: `owntracks.home.{emp_id}.lat`, `.lng`, `.radius`
- Calculate haversine distance to home
- If within radius AND clocked in:
  - < 30 min → cancel attendance (short errand)
  - ≥ 30 min → clock out

**Why:** Geofence events still fire sometimes (and we still handle them), but pings are the reliable fallback.

**Home coords (DJ, emp_id=1):**
- lat: 33.8110, lng: -116.3822, radius: 200m
- San Miguelito Drive, Tri Palm Estates, Thousand Palms, CA 92276
- Stored in Odoo ir.config_parameter keys `owntracks.home.1.*`

**To add Danny's home:** Set `owntracks.home.2.lat`, `owntracks.home.2.lng`, `owntracks.home.2.radius` in Odoo → Settings → Technical → System Parameters.

**Code location:** `routers/owner/dashboard.py` — inside `api_owntracks_webhook`, section B (location ping handler), after `x_gps_ping` create call. Commit `5ea5f589`.
