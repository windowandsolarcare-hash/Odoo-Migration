---
name: owntracks-setup-and-quirks
description: "OwnTracks Android setup, geofence clock-in/out behavior, and known gotchas"
metadata: 
  node_type: memory
  type: project
  originSessionId: bcd62e72-19be-4a09-af3f-a38378b2ba9e
---

## Connection settings (DJ's phone)
- Mode: HTTP
- URL: `https://wsc-field-assistant.onrender.com/owner/api/owntracks/webhook?token=wsc-ot-2026`
- Device ID: q5q
- Tracker ID: DJ
- TLS: not set
- Credentials: not set

## Clock-in/out logic
- `leave` Home waypoint → auto clock-IN + switch to Move mode (monitoring: 2)
- `enter` Home waypoint → auto clock-OUT + switch to Significant mode (monitoring: 1)
- Waypoint name MUST contain the word "home" (case-insensitive) — other waypoint names are ignored

## CRITICAL: monitoring modes on Android
- **Move (2):** frequent pings + geofence events. Use while working.
- **Significant (1):** cell-tower pings only (low battery) + geofence events still fire. Use at home.
- **Quiet (-1):** NO pings AND NO geofence events on Android. NEVER USE — kills the leave/enter events that drive clock-in/out. Was used 2026-05-21, caused clock-out to stop working permanently.

## Critical gotchas

**Waypoint checkbox = geofence on/off**
Unchecking a waypoint in OwnTracks (Waypoints screen) disables geofence monitoring entirely. No enter/leave events fire. DJ unchecked both his and Danny's waypoints 2026-05-15, which stopped all clock-in/out. Re-check to re-enable.

**Why:** OwnTracks checkbox = monitoring enabled/disabled, not just visibility.
**How to apply:** If clock-in/out stops working, first check that the Home waypoint checkbox is checked.

**Waypoint radius: use 200m minimum**
DJ originally set 20m radius — GPS accuracy on Android is ±5–30m indoors, so a 20m radius caused constant false enter/leave events (GPS drift clocked him out while sitting at home).
Fixed to 200m. At 200m, real GPS drift can't reach the boundary edge.

**Why:** Phone GPS is not precise enough for small radii indoors.
**How to apply:** Always recommend 150–250m for home waypoints.

## Locator settings (Advanced → Locator) — confirmed 2026-05-28
- **Minimal location displacement**: 50 metres — prevents pinging server on every GPS jitter while stationary. 0 causes a ping every second. 50 is the correct value.
- **Location interval**: 300 seconds (5-min stationary pings)
- **Location interval (Move mode)**: leave as-is (~15 sec — working fine for driving pings)

Before 2026-05-20: displacement was set high → OwnTracks only pinged while moving → only 2-4 pings per hour at job sites → stop detection unreliable.
After: ~12 pings/hour at job sites → clean stop boundaries, correct customer matching.

## Env var: OWNTRACKS_SECRET = `wsc-ot-2026`
Set on Render. If empty, the `if OWNTRACKS_SECRET` check is falsy → all tokens accepted (not a crash, just no auth).
