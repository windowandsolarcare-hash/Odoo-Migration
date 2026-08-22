---
name: project_city_service_weekday_map
description: The city->service-weekday routing map (Mon=0) that gates online booking + all scheduling. Lives in THREE mirrored copies; add a new city to all 3. Menifee added Tuesday 2026-07-09.
metadata: 
  node_type: memory
  type: project
  originSessionId: 65d82725-62b9-4564-8ede-09606413c213
---

**The city → service-weekday map** (weekday ints, **Mon=0**, so [1]=Tuesday) gates every date-offering surface: the wscare.pro booking portal availability, Command Center "next available by city", Phase 5 auto-schedule, reactivation Book, and intake suggest-dates.

## ★ THREE mirrored copies — change ALL 3 to add/edit a city
1. **`routers/owner/scheduler.py` `CITY_WEEKDAYS`** — the SINGLE SOURCE OF TRUTH. `_rank_days_at` / `rank_days` / `build_day_plan` + `/api/scheduler/cities` (Command Center dropdown) read it. booking.py lazy-imports it live.
2. **`routers/booking.py` `CITY_SCHEDULE`** — feeds the wscare.pro city **dropdown** (`/book/api/cities`) and is the fallback if the scheduler import hiccups. `_open_dates_for_city` uses the scheduler import for the actual routing.
3. **`routers/owner/dashboard.py` `CITY_SCHEDULE`** (~L3457, inside intake suggest-dates) — the intake mirror, has inline `# weekday` comments.

Current map (2026-07-09): palm springs Fri[4] · rancho mirage Thu/Fri[3,4] · palm desert Thu[3] · indian wells Wed/Thu[2,3] · indio Wed[2] · la quinta Wed[2] · cathedral city Wed/Thu[2,3] · **hemet Tue[1]** · **menifee Tue[1]** · **banning Tue[1]** · **beaumont Tue[1]** (menifee + the two Pass-area cities Banning/Beaumont all added 2026-07-09, DJ: "ride the Hemet work"). Matching is SUBSTRING (`if key in city_lc`), city_lc = the customer's city field lowercased.

## How an UNKNOWN city (not in the map) is handled — the two paths DIFFER
- **Online booking (wscare.pro, `_open_dates_for_city`):** ★ FIXED 2026-07-09 (was a dead-end). Unmapped city now sets `unmapped=True`, `weekdays=[0,1,2,3,4]` (Mon–Fri), `start_offset=7` and falls through the SAME slot logic → returns `routed:False` with real "request" day chips **starting no earlier than 7 days out** (out-of-area/special trip needs lead time — DJ's rule). Frontend already shows "pick a day and we'll confirm" (not "we're in your area") for routed:False + renders the chips; fit=False → "Available" badge. Mapped cities unchanged (start_offset=2). The city still isn't in the dropdown, so this path only reaches known/token customers whose stored city is unmapped. Verified: Temecula → routed:False, first option exactly 7 days out.
- **Internal scheduler (`_rank_days_at`):** unknown city → `weekdays=None` → **ALL 7 weekdays are candidates**, ranked purely by 7-mile route tightness. So Phase 5 / reactivation Book still produce dates for an unmapped city — but it won't appear in the `/api/scheduler/cities` dropdown.

## Mount prefixes (for testing live)
Booking router = **`/book`** (main.py `include_router(booking.router, prefix="/book")`). So: `/book/api/cities`, `/book/api/availability?city=`, page `/book/c/{token}`. wscare.pro proxies to `/book`. Scheduler/dashboard routers = **`/owner`** → `/owner/api/scheduler/cities`. Verified 2026-07-09: `/book/api/availability?city=Menifee` → routed:True, four Tuesday options.

★ NOT the same as the two Hemet-specific features in dashboard.py (`_hemet_candidates_data`, `_check_hemet_tomorrow`, `city ilike 'hemet'`) — those are a separate "Hemet day" reminder pipeline, NOT the routing map; don't auto-extend them when adding a routing city. Also separate from Calendly city→event-slug map (SA 563) which DJ said he doesn't care about.

(Resolved) The old `routed:False` dead-end is fixed — see the Online-booking bullet above.
