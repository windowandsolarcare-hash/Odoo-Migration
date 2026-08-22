---
name: project_navigate_gps_first
description: Field app Navigate now routes by GPS coords (not just text address); + Odoo gotcha that writing a res.partner address WIPES its lat/lon
metadata: 
  node_type: memory
  type: project
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
---

**Field app "Navigate" is now GPS-first.** Symptom that triggered this (2026-06-29): DJ tapped Navigate and Google Maps said "Can't seem to find a way there" — the pin landed in a greenbelt, not on a house.

Root cause = corrupt address text. Property 25387 (78770 Falsetto Drive, Elsa Sandvold) had `city='Sun City'` + `zip='92253'` (La Quinta) — but its real location (and stored GPS 33.7963447,-116.2880152) is **Indio 92211**. "Sun City, CA" is a community name Google reads as the town near Menifee → conflicting signals → unroutable pin. Fixed the data (city→Indio, zip→92211). Only 5 partners had city 'Sun City'; the other 4 (Robyn Tagliareni, 30061 Crestview Court, zip 92585) are the REAL Sun City/Menifee — left alone.

Durable fix (mirrors the customers-overlay nav that already worked):
- `dashboard.py` new helper `_nav_by_partner(pids)` → `{pid:{lat,lon,addr}}` (addr = street, city, State zip). Wired into the 3 schedule builders: `/api/dashboard` (today), `/api/upcoming` (28d), `/api/past_jobs`. Each job dict now carries `nav_lat`/`nav_lon`/`nav_addr`.
- `field.html` new `navUrlForJob(j)`: if `nav_lat&&nav_lon` → `maps/dir/?api=1&destination=lat,lon` (routes by coords, unambiguous); else `nav_addr||address`. `openNav()` + the crew-modal nav fallback (`_pendingNavUrl || navUrlForJob`) both use it. Jobs with no geocode (lat 0) fall back to full address incl. state.

**★ REVERSED 2026-07-01 — Navigate is now ADDRESS-first, NOT coords-first.** DJ: Maps opened to the coords and showed/pinned a "very close but WRONG" address → knocked on the wrong door. Cause: routing to raw `lat,lon` makes Google label/pin the nearest KNOWN address, which can be a neighbor. Fix: `navUrlForJob(j)` now uses `(nav_addr || address)` as the `destination` FIRST (full street/city/state-ZIP — the zip keeps geocoding accurate even with a community-name city), and only falls back to `lat,lon` when there's NO text address. This shows DJ the real street address AND routes there. Do NOT flip back to coords-first — coords route to the pin, not the door. (The earlier "Sun City can't route" case was really a DATA bug — fixed by correcting the property's city/zip, which is the right place to fix it. A complete zip'd address doesn't hit that problem.)

**★ ODOO GOTCHA (reusable): writing ANY address field (street/city/zip/state_id) on a `res.partner` RESETS `partner_latitude`/`partner_longitude` to 0.0** — Odoo clears them to force re-geocoding. Hit this 2026-06-29: fixed Falsetto city/zip and the good GPS got wiped to 0,0. **How to apply:** after any address write where you need to keep coords, immediately write the lat/lon back in a second `write()`. Reverse/forward geocode to confirm correct city/zip: Nominatim `/reverse?lat=&lon=&format=json` and `/search?street=&city=&state=&country=&format=json` (User-Agent header required).

See [[project_property_address_cascade_bug]] (related property-address data integrity) and [[project_command_center]] (the customers-overlay nav this mirrors).
