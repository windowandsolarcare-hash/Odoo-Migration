---
name: project_route_map_geocode_on_miss
description: "Route-map \"no map pin\" = a property res.partner with 0/blank partner_latitude. Fixed via a coord backfill + geocode-on-miss (Photon, cached) in scheduler.py."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e8d15b5-9a20-4187-90d6-6f63266f2498
---

**Symptom:** a stop on the Review-Request / booking / reschedule route map shows "**no map pin**" and isn't plotted (e.g. Edward Chavez, 3660 Serenity Trail). **Cause:** that property's `res.partner.partner_latitude/longitude` = 0/blank (never geocoded). The map only plots stops with real coords. Properties accumulate pinless because creation paths don't geocode.

**Backfill done 2026-07-05:** swept all 907 Property records — 31 had 0/blank coords → geocoded 29 via Photon (`photon.komoot.io/api/?q=street, city, CA`, sanity-boxed to the service area) + Nominatim for a couple; **2 unmappable remain** = both "**69560 Corta Celeste, Cathedral City**" (props 27067 Phil Sousa + 27068) — that street isn't in OSM/Photon (new/gated), needs MANUAL coords or the app's Google geocoder. Also flagged: prop **27103 "1 Test St"** = junk test record (should be deleted, not pinned); **26945 "sun city"** = vague city-centroid geocode.

**Durable fix (scheduler.py, deployed 2026-07-05):** added `_geocode_addr(street,city)` (server-side Photon — Google key is browser-referrer-locked so it CAN'T geocode server-side; `_GEO_BOX`=(33.0,34.6,-117.8,-115.4) rejects out-of-area matches) + `_partner_coords(pr)` = returns stored coords or geocodes-on-miss and **writes the coords back to Odoo (cached)** so a property is only ever geocoded once. Wired into BOTH `prop_geo` (the new stop) and `build_day_plan` (existing day stops; Personal Time blocks skip — no address). read() always returns `id` so write-back works. ★ Writing ONLY coords is safe; writing a res.partner ADDRESS wipes coords (see [[project_navigate_gps_first]]).

★ Google Places/Geocoding key on this project is REFERRER-LOCKED to wsc-field-assistant.onrender.com → only works from the browser, NOT server-side/scripts. Use Photon (or Nominatim) for any server-side/local geocoding.
