---
name: project_livepipe_verify_booking_availability
description: How to LIVE-PIPE verify scheduling/availability changes on the deployed app (public endpoint + Odoo draft injection + control + cleanup)
metadata:
  node_type: memory
  type: project
  originSessionId: 4a3934c7-cb02-4949-8807-74eee8a68861
  modified: 2026-09-27T05:40:21.790Z
---

**Gold-standard live-pipe verify for scheduling/availability code (DJ/Lead 2026-09-26).** A green deploy ≠ the feature works ([[feedback_verify_collection_and_live_pipe]]). Prove it end-to-end on the DEPLOYED app with a real effect + a control + cleanup.

**Public observable surface (NO auth):** `GET https://wsc-field-assistant.onrender.com/book/api/availability?city=<city>&lat=&lon=` → `{suggestions:[{date,am_free,pm_free,...}], routed, city}`. This is the customer booking page backend → `booking._open_dates_for_city` → `_jobs_by_day_geo` (the reserve+duration-aware finder). `/owner/api/*` (day-plan, offers/record) is **owner-auth gated — 401 from a headless shell** (authz gate enforcing; `AUTH_ENFORCE=1`), so use the PUBLIC `/book/api/availability` to observe.

**Inject a known reserve without owner auth = create a DRAFT SO via Odoo JSON-RPC** (key at `C:\Users\dj\_odoo_key_val.txt`, DB `window-solar-care`, uid 2, `/jsonrpc` `execute_kw`): `sale.order.create` with `state:'draft'`, `company_id:1`, `x_studio_x_studio_workiz_status:'Submitted'`, `x_job_length_min:210` (210 min blocks a whole AM or PM half via duration), `date_order` in **UTC** (PDT = PT+7h; e.g. 12:30 PT = 19:30 UTC), partner/shipping = Fred Test **26339** (sandbox). A `company_id:1` draft is picked up by `held_intervals_for_range` (draft/sent + company_id in [1,False]).

**Pattern:** baseline availability → note a `pm_free:True` (or `am_free:True`) service day D + a control day → create the draft on D at 12:30 PT len210 → re-fetch: **D drops from suggestions or its half flips False**, control day UNCHANGED → **`sale.order.unlink`** the draft in a `finally` (verify cleanup: D returns to True). Proven pass 2026-09-26: draft on 2026-09-29 dropped the day, 2026-10-13 unaffected, unlink restored it, test SO 17716 cleaned (no phantom).

**Why:** repeatable read-only-on-prod-data proof (draft is transient + unlinked) that a scheduling change actually reaches the customer surface. **How to apply:** ALWAYS run this after shipping any availability/finder/reserve change; report the drop + control + cleanup to Lead/Dispatcher. Note: hemet mornings are often already `am_free:False` — target the free half. Ties [[project_scheduling_reserve_stage1]].
