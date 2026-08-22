---
name: project_customer_search_multifield
description: "Customer tab search (/api/search) is tokenized multi-field — name OR street OR city, partial/any-order, with any-token fallback. Not name-only anymore."
metadata:
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Shipped 2026-06-10.** Field-app **customer tab** search (`cust-search` input → `custSearch()` → `GET /owner/api/search?q=`) now searches **name OR street OR city**, not name-only.

## Backend (dashboard.py `api_search`, ~L6557)
- Query is split into whitespace tokens. **Each token** must match `name ilike t` OR `street ilike t` OR `city ilike t`, AND'd across tokens. `ilike` = substring → partial spelling + any word order both work ("rik tangle", "jim tanglewood", "la quinta", a house number like "55264").
- Built with local `_and()` / `_or()` helpers that assemble Odoo prefix-notation domains (`['&', ...]` / `['|', ...]`).
- **Any-token fallback:** if AND'ing every token returns 0 rows AND there's >1 token, it retries with the token groups OR'd — so one misspelled word doesn't zero out the whole search.
- Base filters unchanged: `active=True`, `ref!=False`, `record_category != 'Property'` (real customer Contacts only). Enrichment (next_job / last_job via Property-child resolution) unchanged.

## Why street/city work on the Contact
Contacts carry their own `street`/`city` (verified: Rik Ports Contact 23173 = "55282 Tanglewood, La Quinta"). **Edge case not covered:** a Contact whose `street` is blank but whose Property child holds the address won't match a street query — search is on Contact fields only, not Property children.

## Per-result stats (added 2026-06-10)
Each result line shows **Next Job · Last Job · Sales**:
- `next_job` / `last_job` — earliest future / latest done SO date (Property-child→Contact mapped). Enrichment SO query limits raised (next 300, last 600) to cover up to 200 matched customers.
- `total_sales` — **sum of posted `out_invoice` `amount_total`, `company_id=1`**, computed with **`account.move` `read_group`** grouped by `partner_id` (one call), mapped Property→Contact. ✅ `read_group` works on this Odoo 19 SaaS via JSON-RPC: `odoo_rpc('account.move','read_group',[domain, ['amount_total:sum'], ['partner_id']])`. Verified 2026-06-10 (Indio: 38 rows).
- **Partner result limit raised 15 → 200** — a city like Indio has 42 customers; 15 was silently truncating the list.

Also added: **visit_count** (read_group count of done SOs, key `partner_id_count`), **avg_ticket** (total_sales ÷ visit_count), and an **Overdue/Due badge**.

### Overdue/Due badge — Maintenance-gated (DJ correction 2026-06-11)
**Only Maintenance-service-type jobs can be "late." On Request / Unknown are NEVER late.** Frequency alone is NOT the gate — service type is.
- Per-SO service type field = **`x_studio_x_studio_type_of_service_so`** (Selection: `Maintenance` / `On Request` / `Unknown`). Verified 2026-06-11: 909 Maintenance / 627 On Request / 923 Unknown done jobs. (There's also a partner field `x_studio_x_type_of_service` = Maintenance/On Request/Unknown, but the badge uses the per-SO field.)
- Badge inputs come from the **most recent Maintenance-type done job only**: its date = last maintenance visit, its `x_studio_x_studio_frequency_so` = cadence (walk back to the most recent KNOWN, non-"Unknown" cadence among maintenance jobs). Among Maintenance jobs cadence is almost always set (Unknown only ~60/909).
- Logic: `cycle = freq_months*30`; `days = today - last_maint_visit`. `days >= cycle` → **overdue** (label `Overdue Nwk` if <60d over, else `Overdue Nmo`); within 21 days of due → **Due soon**. **Suppressed if a future job is already booked** (next_by). No maintenance history → no badge.
- Frontend: red `.due-overdue` / amber `.due-soon` pill on the name row.

Frontend (field.html `custSearch`): name row (+ badge), address, schedule line "Next Job · Last Job", money line "N visits · Avg $X · Sales $Y" (sales green `.cs-sales`). Expanded customer-jobs list (`toggleCustJobs`) shows a **double-gray "Past Jobs" divider** (`.cust-jobs-divider`, `border-top:4px double`) at the future→past boundary (jobs are date-desc → upcoming first).

## Navigate-to-customer link (2026-06-16)
Each customer card (field.html `custSearch` render) has a **📍 Navigate** link (`.cust-nav`) on the address line → `https://www.google.com/maps/dir/?api=1&destination=<dest>` (Google Maps directions, `onclick="event.stopPropagation()"` so it doesn't toggle the card). **`api_search` now returns `nav_lat`/`nav_lon` (the Property child's `partner_latitude`/`partner_longitude` — exact GPS) + `nav_addr` (full `street, city, CA zip`).** Frontend dest priority = GPS coords → nav_addr → displayed addr. WHY: street+city alone (no state/zip) made Maps geocode to the CITY not the house; GPS coords navigate to the exact door. The children read in api_search was extended to fetch street/city/zip/lat/lon (was id+parent_id only); `zip` added to the contact fields too for the fallback.

## Reactivation full-circle on the customer card (2026-06-16)
The customer card is the "brain" — it now surfaces reactivation status. `api_search` returns per contact:
- **`last_reactivation`** — formatted `x_studio_last_reactivation_sent` (or '').
- **`reactivation_due`** (bool) — computed in Python to MIRROR `/api/reactivation/candidates` EXACTLY: `record_category=='Contact'` AND `activelead=='Active'` AND `last_visit_all_properties < 6mo ago (183d)` AND `next_job_date` empty AND (`has_window_service` OR `has_solar_service`) AND (`last_reactivation_sent` empty OR `< 1yr ago (365d)`). Added those fields to the search read. Verified: Henry Weinstein (candidate)→due True; Adam Ruelas (sent 2019)→due True + last 'Jan 1, 2019'.
field.html card renders (each `event.stopPropagation()`): **"⚠ Past due on reactivation →"** (amber `.cust-react-due`) → `/owner/reactivation?contact_id=<id>` (opens that candidate's launch preview via existing `open_by_partner`), and **"Reactivation sent: <date> →"** (`.cust-react-sent`) → `/owner/reactivation?sent_q=<name>`. Added `?sent_q=` deep-link to reactivation.html init = open Sent tab + prefill `sent-search`. (Reactivation page already had `?contact_id=`→launch and `?book_lead=`→Sent Book sheet.)

## ⚠ `x_studio_last_reactivation_sent` = `2019-01-01` is the INIT PLACEHOLDER (DJ 2026-06-16)
When the app was first built, every contact was SEEDED with `x_studio_last_reactivation_sent = 2019-01-01` so Odoo date-filters had something to compare. **It only changes to a REAL date when a message is actually sent.** So `2019-01-01` means "never sent." ANY code reading this field must treat `2019-01-01` as empty/never-sent (e.g. customer card `last_reactivation` now blanks it; don't display "Reactivation sent: Jan 1, 2019"). Candidate/cooldown logic already works because 2019-01-01 < any cooldown window, but normalize it to '' for clarity. Applies anywhere last_reactivation_sent is read (reactivation candidate filter, customer card, analytics).

## Refinements 2026-06-16 (DJ from screenshots)
- **Duplicate-property collapse (header shows ONE per address):** Workiz makes a 2nd res.partner Property record for the same address (e.g. "5 University Cir" vs "5 University Circle", Steve Bluestein 23197). `customer_jobs` now dedups `properties` by normalized street+city+zip (lowercase, circle→cir/ave/st/dr/rd/ct/ln, strip punctuation) and keeps the record with the most recent `x_studio_x_studio_last_property_visit` (the active one with the real gate/pricing). Display-only — `all_pids` (jobs) still spans ALL property records. Works even before the Workiz dup-merge cleanup ([[project_open_tasks]]).
- **Cleaner property header (was "data dump"):** PROP_FIELDS trimmed to service-relevant only (gate/pricing/frequency/type-of-service/alternating/service-area/last-property-visit/next-job-date/prices-per-service/field-note) — dropped Address/City/ZIP/Phone (already in the customer card header) + Location ID + Active/Lead. Panel framed as a card with `🏠 <address>` head (always shown now, was only when >1).
- **Reactivation SMS reported ONLY when actually SENT:** `so_full` shows `x_studio_manual_sms_override` ("SMS Text to Send") ONLY if the customer has a **crm.lead at stage 5 (REACT_STAGE_SENT)** (`partner_id` or `x_odoo_contact_id` = contact), returned as `reactivation:{sent:<lead create_date>, message}`. A preview/campaign DRAFT (written to the candidate's last real SO by SA 562, never sent) is hidden — fixed Steve showing a never-sent message. NOTE: actual sent messages live on the graveyard lead/Workiz (information_to_remember), not the real SO's override, so the SO-view SMS section appears rarely — by design.

## Reverse link: reactivation → customer card (2026-06-16)
Closes the loop. Reactivation candidate detail (`openCandidate`, prev-tags) AND Sent lead detail (`openLead`, sd-links) each got a **🧑 Customer card** link → `/owner/field?tab=customers&cust_q=<name>&cust_pid=<partner_id>`. field.html `_custDeepLink()` (hooked into BOTH `?tab` init spots — boot-time L1635 + checkAccess L1347, via `setTimeout 650`): prefills `cust-search`, runs `custSearch`, and a one-shot `_custAutoOpenPid` makes the matching `.cust-card[data-pid]` scroll into view + `toggleCustJobs` (auto-expand). Field route = `/owner/field`.

## Customer tab = "the brain" (2026-06-16): property header + full-SO detail
DJ: customer tab is the brain. Clicking a customer expands (`toggleCustJobs`) to show:
1. **Property header** — ALL property-master fields (one `.prop-panel` per property). `/api/customer_jobs` now returns `properties: [{id, name, fields:[{label,value}]}]` — every non-empty field from a labeled `PROP_FIELDS` list (gate/pricing/frequency/type-of-service/alternating/service-area/last-visit/next-job-date/location-id/activelead/field-note/address). Multi-property customers get a panel each (`🏠 name` head).
2. **SO cards** — now also carry `tech` (`x_studio_x_studio_workiz_tech`) + `gate` (`x_studio_x_gate_snapshot`) per job.
3. **Click an SO card → full-SO modal** (`openSoFull` → `#sofull-modal`, reuses `.hist-*` styles). Endpoint **`/api/so_full?so_id=`**. REVISED 2026-06-16 (DJ: raw dump "looks better" + a confusing SMS field): now returns **curated GROUPED sections** `groups:[{title,rows:[{label,value}]}]` — **Job** (job type/status/tech/type-of-service/frequency/lead source), **Pricing** (total/pricing snapshot/pricing-check html-stripped), **Access & Notes** (gate snapshot/notes), **Order** (SO#/state→friendly/invoice status/created) — plus `links` (Workiz/Odoo pills), line items, payments, photos. Explicit field spec (not a dump-all-x_), so noise is excluded. **EXCLUDED: `x_studio_manual_sms_override` ("SMS Text to Send")** = the reactivation tool's stored DRAFT message (written to the candidate's most-recent SO on preview/launch; a saved draft is NOT a send — the text goes out via Workiz). It was showing as a confusing "I never sent this" field; removed from the view. Customer-tab SO cards open `openSoFull` (was `openCustJobRow`→live panel); live working panel still on Schedule tab.

## Quick-Launch Customer button — one-tap fix (2026-06-16)
Bug: the floating + (Quick Launch / `ql_panel.js`) **Customer** (👤) button took TWO taps to reach the Customers tab — first tap landed on schedule/stats, second switched. Cause: field.html boot loads the default **stats** tab on wide (≥600) layout, and the `?tab=customers` switch was a fragile **400ms setTimeout(showTab)** that lost the race (worse on DJ's foldable: unfolded = wide two-pane, schedule left + tabs right). FIX: new `openCustomersTab()` in field.html opens the tab in ONE tap on BOTH layouts (folded <600 = surface `#office-panel` as a full-screen overlay + Back btn; unfolded = the pane is already visible). `boot()` now honors `?tab` **synchronously** (calls openCustomersTab for customers, showTab for others, else default stats) — removed both 400ms setTimeout handlers. `ql_panel.js` Customer button calls `openCustomersTab()` when on the field page, else navigates to `/owner/field?tab=customers` (boot handles it). Field route = `/owner/field`; `#office-panel` is `display:none` <600.

## Frontend placeholder
"Search by name…" → "Name, street, or city…". `custSearch()` already forwarded the raw query verbatim; min length 2.

See [[project_render_app_architecture]]. Files: routers/owner/dashboard.py, static/owner/field.html.
