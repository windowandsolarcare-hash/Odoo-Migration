---
name: project_customer_analytics_datamodel
description: Customer Analytics app data model — SO.partner_id IS the Property/customer unit; properties have company_id=False; true-customer definition + verified counts
metadata: 
  node_type: memory
  type: project
  originSessionId: 5c7951e2-f25a-42b0-ac13-dd386cb454cf
---

# Customer Analytics — Data Model (verified 2026-06-11 via XML-RPC)

App: `routers/owner/analytics.py` + `static/owner/analytics.html` (separate file so multiple Clauds don't collide). Page `/owner/analytics`, tile on owner hub.

## Customer unit = the CONTACT (parent_id) — NOT the property  ⚠ changed 2026-06-11
- **`sale.order.partner_id` = a Property record** (`record_category='Property'`); its **`parent_id` = the person/Contact**. The CUSTOMER UNIT for all analytics = the **Contact** (`property.parent_id`, or the property's own id if it has no parent). Group jobs by contact, not property.
- **Why (this overrode the original "property = unit" choice):** Workiz duplicates property records over time — same physical address gets a fresh res.partner record repeatedly. Per-property splits ONE customer across several records and falsely marks the old ones "lapsed." Real case: **Linnea Rowden (contact 23001)** had 4 property records all = "560 Tewell Dr, Hemet" (ids 24168/24123/25666/26292); per-property flagged her lapsed even though serviced 2026-03-10. Contact-level = 1 Active customer, 22 jobs.
- A contact is **active if ANY of its properties** had a recent job. Drill-down passes the **contact id** as `pid` (customer_jobs aggregates the contact's properties anyway).
- Scale: 896 properties → 680 contacts → 584 true customers. 132 contacts have >1 property record (up to 4). The leaderboard/list row shows `name`=representative property address (most-recent-job property), `parent`=person, `pid`=contact id. Frequency/area/source use the most-recent-job property (`_rep(contact)`).

## ⚠️ Property records have `company_id = False` — NOT 1
- `res.partner` Property records all have `company_id` unset. Filtering properties by `['company_id','=',1]` returns **0**. NEVER company-filter the property query.
- Company scoping happens at the **sale.order** level instead: done jobs are `company_id=1`. So: count the brain from `res.partner` (no company filter), count true customers from company-1 done SOs.

## Definitions (locked with DJ 2026-06-11)
- **The brain** = distinct CONTACTS behind all Property records (`record_category='Property'`, no company filter). = 680 contacts (from 896 property records).
- **True customer** = a CONTACT with ≥1 `sale.order` where `x_studio_x_studio_workiz_status='Done'` AND `amount_total>0` AND `company_id=1`. = 584. This is the denominator for every ratio.
- **Leads / never-served** = total contacts (680) − true customers (584) = 96.
- **Revenue** = sum of `amount_total` on those qualifying done SOs.
- **Active window = flat 30 months** (DJ's choice; not frequency-based). A property is "active as of date D" if its most recent qualifying done job ≤ D is within 30 months before D. Lapsed = true customer not active.
- **As-of-date is the master knob.** Snapshot = as_of today. Chronological = as_of Dec 31 of each year, computed as it was true then. This resolves the "2021+2023 then nothing" problem: repeat-as-of-2023 = yes; repeat-as-of-2026 = lapsed. History stays true, current status reflects today.
- **Churn in year Y** = `active(endY-1) − active(endY)` (set diff of year-end active sets). New-active in Y = reverse diff.
- **Year-over-year retention[X]** = |served(X) ∩ served(X+1)| / |served(X)|, served(X)=properties with a done job in calendar year X.

## Verified counts (2026-06-11, company 1, Done, amount>0)
- 2439 qualifying done SOs · 745 distinct properties · $420,724 lifetime revenue · 0 jobs missing date_order.
- Done jobs by year: 2019:58, 2020:163, 2021:330, 2022:334, 2023:430, 2024:486, 2025:448, 2026:190(partial).
- New customers (first done job) by year: 2019:46, 2020:45, 2021:146, 2022:95, 2023:191, 2024:136, 2025:57, 2026:29.
- Lifetime repeat (≥2 done jobs): 402 of 745 (54%).

## Useful SO fields (all present, verified)
`partner_id`, `date_order` (job start, UTC, always populated on Done), `amount_total`, `x_studio_x_studio_lead_source` (e.g. Referral/Thumbtack), `x_studio_x_studio_frequency_so` (3/4/6/12 Months/Unknown), `x_studio_x_studio_type_of_service_so` (Maintenance/On Request/Unknown).
Property fields: `x_studio_x_frequency`, `x_studio_x_type_of_service`, `x_studio_x_studio_service_area`, `x_studio_activelead` ("Do Not Contact"), `parent_id`.

## Upcoming / Booked category (added 2026-06-11)
- **Problem:** a NEW contact with a future job booked but no Done job yet (e.g. Bruce Zuber, contact 27074, job 6/16) was wrongly lumped into "Leads/unserved." Two axes were conflated: *served before?* (Done job) vs *job booked ahead?* (future SO).
- **New status `Upcoming`** = contact with a CONFIRMED future job (`state in ['sale','done']`, `date_order > now`, status NOT in [Done,Canceled]) who is NOT already Active. Catches new-but-booked AND re-booked lapsed customers. Excludes "Personal Time" blocks. `next_job` per contact = soonest future (date, job_type).
- `upcoming_ids = set(next_job) - active_set`. Reclassifies: ltv status becomes Active/Upcoming/Lapsed; new-booked move from `leads_list` → `upcoming_list`; re-booked move from Lapsed → Upcoming. **Kept OUT of revenue/LTV/retention stats** (they've paid $0; DJ's call) — they graduate to Active automatically when their job is marked Done.
- KPI cards now: True customers · Active · **🗓 Upcoming** · Lapsed · Leads(strictly never-served+nothing-booked). `drill('upcoming')` → `DATA.upcoming_list`. Each customer/lead carries `next_date`+`next_type`. Card counts reconciled to actual list lengths (no formula drift). Live 2026-06-11: active 370 / upcoming 3 / lapsed 214 / leads 94.

## Drill-down (added 2026-06-11)
- Result includes `customers` array (one per true customer): `{pid, name, parent, jobs, revenue, last_job, status, freq, area, source, year}`, plus a separate `leads_list` (same shape, status='Lead', 0 jobs) for unserved contacts. `leaderboard` = top-25 by revenue.
- **EVERY metric is drillable** into the same customer-list sheet → job history. Client-side `drill(key)` filters `DATA.customers`: all 12 KPI cards (true/active/lapsed/leads/repeat/active_repeat/revenue/rev_per/avg_job/jobs_per/interval/lifespan), every leaderboard row, the **mix charts** (frequency/area/source — Chart.js `onClick` → `drillMix(field,label)`), and the per-year table's **New** column (`drillYear`). Verified filter counts == KPI counts live.
- Bottom-sheet list is sortable: most-recent / longest-gone / top-value → tap a customer → **job-history sheet**.
- **Lapsed list = two collapsible groups (2026-06-11):** the Lapsed drill (only) splits into **"🔄 To review"** (no reactivation in cooldown) and **"✅ Reactivation sent"** (last_react < 365 days) — Sent collapsed by default so DJ doesn't waste time on already-sent ones. Each customer carries `last_react` (= `x_studio_last_reactivation_sent`, batch-read for all contacts in compute). `isReactRecent(c)` = `cooldownDays(c.last_react) < REACT_COOLDOWN_DAYS(365)`. Grouping is gated to `drill('lapsed')` via the `grouped` flag on `openList`; other lists stay flat. `CUST_BY_PID` map (built in render from customers+leads) lets the history sheet look up `last_react`. Live split 2026-06-11: 214 lapsed = 128 to-review + 86 sent.
- **Cooldown warning now lives at the Reactivate button:** the job-history sheet shows a banner under the header when the opened customer's `last_react` is within cooldown — so DJ sees it WITHOUT opening the send sheet (his complaint: opening the SMS sheet just to back out = too many taps). The send-sheet warning + 2-tap override still exists as a backstop.
- **Reactivate button (2026-06-11):** the job-history sheet has a 🔄 Reactivate button that reuses the EXACT reactivation program — `POST /owner/api/reactivation/preview {so_id, partner_id}` (runs Odoo SA 562, returns `data.sms`) → editable textarea → `POST /owner/api/reactivation/launch {so_id, partner_id, sms_text}` (runs SA 563: sends SMS + Calendly link + graveyard job). Targets the customer's most-recent **Done** job's so_id (fallback newest). partner_id = the contact pid. These endpoints are proven in reactivation.html; do NOT smoke-test launch (it actually sends). "Unlapsing" lapsed customers is DJ's #1 focus.
- **"Set aside" bucket (2026-06-11):** soft-hide bucket for lapsed customers DJ doesn't want to rework but doesn't want to lose (NOT a STOP/do-not-contact). Per-row 💤 toggle in the list sheet; lists hide set-aside by default; a "💤 Set aside (N)" header button switches the same category to show only the parked ones (each with ↩ restore). Set-aside customers can still be opened + Reactivated. Stored server-side in `ir.config_parameter` key `analytics.setaside` as JSON dict `{pid: reason}` (migrates the old list-only format). Endpoints: `GET /owner/api/analytics/setaside` → `{pids:[], reasons:{pid:reason}}`; `POST` `{pid,on,reason}` toggles. Set-aside has a **reason** (quick-pick chips + free text) captured in a small sheet on set-aside; shown under the name in the parked view. Restore = one tap (↩, no prompt). **Set-aside is a pure list-view filter — it NEVER affects the KPI/chart stats** (parked customers still count in lapsed totals, revenue, etc. — per DJ "leave them statistically everywhere"). Frontend `SETASIDE` Set + `REASONS` map loaded on page load, optimistic toggle.
- **Reactivation cooldown — where it's enforced (2026-06-11 finding):** the reactivation cooldown is **365 days** and is enforced ONLY by the Reactivation-page candidate filter (`reactivation.py` candidates: `x_studio_last_reactivation_sent < one_year_ago`). **SA 563 (launch) does NOT check the cooldown — it only WRITES `x_studio_last_reactivation_sent` at the end.** So calling `/api/reactivation/launch` directly (like the analytics Reactivate button) bypasses the cooldown. Joe Cerni got a 2nd reactivation 58 days after the 1st (Apr 14 → Jun 11) this way. Fix: the analytics Reactivate button now reads `prop_details.last_reactivation_sent` from the preview response and, if < 365 days, shows a warning + requires a 2nd "send anyway" tap (`REACT_COOLDOWN_DAYS=365` in analytics.html). CLAUDE.md's "90-day cooldown" was stale — corrected to 365. (Follow-up flow is a separate 45-day cooldown, enforced server-side in both preview+launch.)
- **Render autodeploy hiccup note:** a push occasionally does NOT auto-deploy (webhook coalesced with an in-flight deploy). Manual trigger: `curl -X POST https://api.render.com/v1/services/srv-d78le0fkijhs738dsli0/deploys -H "Authorization: Bearer <rnd_ key from ~/.claude/mcp.json>" -d '{"clearCache":"do_not_clear"}'`. Build "successful" then ~60-90s zero-downtime promote before the new HTML is served.
- Job history **reuses the field-app endpoints** (do NOT rebuild): `GET /owner/api/customer_jobs?partner_id=PID&access_code=owner` (returns `{jobs:[{so_id,so_name,date,job_type,amount,status,...}]}`; it walks UP to the Contact and aggregates all sibling Property jobs) → tap a job → `GET /owner/api/so_history?so_id=ID&access_code=owner` (returns `{so:{name,date,gate_code,...}, frequency, address, lines[], payments[], photos[]}`). **Both endpoints IGNORE access_code** (no validation) so any page can call them; owner pages pass `access_code=owner`.
- Bottom-sheets (not top overlays) used deliberately so they never collide with the 36px clock-in bar. See [[project_clockin_bar_customer_overlay]].

Related: [[project_render_app_architecture]] [[project_odoo_so_name_format]]
