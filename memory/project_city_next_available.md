---
name: project_city_next_available
description: "Command Center '📍 Next available by city' — pick a city (no customer), get route-tight open days + day map. Reuses the shared scheduler engine."
metadata: 
  node_type: memory
  type: project
  originSessionId: b8f82f75-713b-49ec-b4d3-aeb0cffeef8f
---

# 📍 Next available by city (Command Center, 2026-07-01)

DJ's need: a customer he may not have on file calls and says "when's your next opening?" — he knows the CITY, not a customer. Wanted a quick Command-Center way to see the next available date for a city, with the same 3 options + times + map the scheduling module gives — WITHOUT it being tied to a customer/SO.

## Backend (routers/owner/scheduler.py) — reuses the engine, doesn't reinvent it
- **Refactor:** extracted `_rank_days_at(lat, lon, city, target_str, window_days, top_n)` = the coord-based core of `rank_days`. `rank_days(prop_id,...)` now just resolves `prop_geo` + city then calls it. (rank_days only ever used prop_id to get coords + city.) So property-based AND city-based ranking share ONE engine + the 7-mile rule.
- `_city_centroid(city)` → centroid (avg lat/lon) of our geocoded **Property** records in that city (`x_studio_x_studio_record_category='Property'`, `city ilike`, `partner_latitude != 0`). No external geocode. Returns `(lat, lon, n)`; `(None,None,0)` if none → ranking falls back to availability-only. Verified counts: Palm Springs 101, Hemet 353, La Quinta 41.
- `GET /api/scheduler/cities` → `{ok, cities:[…]}` = the serviceable cities = **`CITY_WEEKDAYS` keys title-cased** (Palm Springs, Rancho Mirage, Palm Desert, Indian Wells, Indio, La Quinta, Cathedral City, Hemet). That map = single source of truth for which weekday(s) we serve each city.
- `GET /api/scheduler/city-suggest?city=&window=21` → `_city_centroid` + `_rank_days_at(centroid, city, today, top_n=3)` → `{ok, city, lat, lon, prop_count, best, options[]}` — same shape as `so-suggest`.

## Frontend (static/owner/schedule_hub.html)
- Button "📍 Next available by city" (teal) under the New Order / Add-to-schedule row → `openCityAvail()`.
- `#city-modal` mirrors `#rs-modal` (reschedule sheet): a **city `<select>`** (populated once from `/api/scheduler/cities`) → `cityLoadSuggest()` → best-day chips + `WSCDayPlan.render` (route_map.js) into `city-*` containers (schedHdr/sched/slotsHdr/slots/mapHdr/mapWrap/map/mapMeta) + `city-date`/`city-time`. `cityPick`/`cityRenderDay` mirror `rsPick`/`rsRenderDay`. VIEW-ONLY — no booking button (there's no customer). Reuses `_rsDayLabel`/`_rsTime12`/`_abFillTimes` already on the page.

Same engine as [[project_cc_reschedule_best_slot]] / [[project_shared_scheduler]]. RULE stands: any new scheduling surface calls the shared scheduler + WSCDayPlan, never a bespoke minimizer.
