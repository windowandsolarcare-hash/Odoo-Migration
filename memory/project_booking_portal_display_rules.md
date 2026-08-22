---
name: project_booking_portal_display_rules
description: "Customer booking portal /api/me display rules — recent visits = Done only, usual = frequency only with a 6-to-12-month suggestive default"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e8d15b5-9a20-4187-90d6-6f63266f2498
---

Customer online-booking portal (`wscare.pro/c/{token}`) = `static/booking/index.html` + `routers/booking.py` `/api/me` (saunders-render-app). Display rules DJ set 2026-07-04:

**"Your recent visits" = Done jobs only.** The `/api/me` job query filters `x_studio_x_studio_workiz_status = 'Done'` (was `!= 'Canceled'`, which let past **Submitted quotes that never happened** show as visits — e.g. job 3787 showed as a bogus "Service" row). Done-only aligns with the CLAUDE.md done-jobs rule and guarantees a real job_type (0 Done jobs have blank job_type). Frontend history fallback label = `job_type || 'Window Cleaning'` (was `'Service'`; now basically never fires). ★ RE-VERIFIED 2026-07-09 (DJ asked again): still Done-only — Dot Gallahan's `/book/api/me` returned 3 jobs, all status Done, no Submitted/Reactivation-Lead placeholders. booking.py:433. The `_occupied_by_day`/`_jobs_by_day_geo` availability queries use `!= 'Canceled'` but they only compute busy-day occupancy — NOT customer-visible history. No change needed.

**INTERNAL vs customer-facing — don't confuse them.** The reactivation review "🧰 Recent jobs — check pricing" facts panel (outreach.html `loadFacts`, source `/api/customer_jobs`) is DJ's INTERNAL view and DOES show placeholders (Reactivation Lead, Submitted). `/api/customer_jobs` returns the RAW `x_studio_x_studio_workiz_status` as `status`. 2026-07-09: DJ first flagged "Reactivation Lead · Scheduled" as inaccurate → I suppressed status on placeholder rows → **DJ then reversed: "actually have it show status. done, submitted, etc."** So the panel now shows the real status on EVERY row again (final state). The customer portal is separate and already Done-only. NOTE: Reactivation-Lead graveyard SOs carry status 'Submitted' or 'API SMS Test Trigger' (a couple older ones = 'Scheduled') — whatever the raw field holds is shown.

**Property seeding = most-recent COMPLETED job's address, not first child.** `/api/me` now reads `partner_shipping_id` on the Done jobs and, if the most-recent job's shipping partner is one of the contact's Property children, uses THAT as `prop` (address prefill + coords + frequency source); falls back to the old first-child-Property pick only if no job match. Multi-property customers were being seeded with a wrong/stale first child (Debbie Church showed 1715 San Simeon w/ 'Unknown' instead of her actual 7615 Watson Circle w/ 6 Months — all her recent jobs are at Watson). Fixes wrong address + wrong coords + stale frequency together.

**"Suggested cleaning schedule" line = FREQUENCY ONLY** (type-of-service is intentionally NOT surfaced — DJ's call; "On Request"/"Maintenance" aren't useful to a customer). The line is informational AND suggestive (nudge to rebook on a cadence).
- Backend resolves frequency via `_clean_freq` chain: property `x_studio_x_frequency` → most-recent Done SO `x_studio_x_studio_frequency_so` → contact `x_studio_x_frequency`. **`_clean_freq` treats literal `'Unknown'`/`''`/`'false'`/`'none'` as NO-ANSWER** so a stale `Unknown` on the property record no longer short-circuits and hides the real cadence. (This fixed the "Your usual: every Unknown • Unknown" bug — Debbie Church's property was 'Unknown' but her Done jobs are '6 Months', so it now shows "every 6 Months".)
- Frontend line = **"Suggested cleaning schedule: every {freq}"** (lowercased), always shown; when frequency is truly unknown it prints the suggestive default **"every 6 to 12 months"**. DJ wanted the label to clearly read as a recommendation, not a vague "your usual".

★ General rule: `'Unknown'` is a REAL stored Workiz-default value across frequency/type-of-service fields, so it is truthy and short-circuits `or` fallbacks. Any fallback chain over these fields must treat `'Unknown'` as empty. See [[project_type_of_service_fields_map]] [[feedback_done_jobs_definition]] [[project_daily_sync_date_window_excludes_old]].
