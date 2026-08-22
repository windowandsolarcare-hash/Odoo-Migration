---
name: project_reactivation_booked_missing_fields
description: "Why a booked reactivation Workiz job had blank custom fields, the real root cause (legacy graveyard), and the booking-time enrichment fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

Booked reactivation Workiz jobs sometimes show blank custom fields (type_of_service_2, frequency, confirmation_method, ok_to_text, gate_code, pricing, JobSource all None). Investigated 2026-06-14 (Curtis Collins, job P4HWHZ).

**ROOT CAUSE (proven, not the obvious guess):**
- The reactivation graveyard job is CREATED by Odoo server action **563** ("Reactivation: 2. LAUNCH Campaign") when the reactivation text is sent. Its `graveyard_data` payload already copies ALL custom fields from the customer's `historical_job` (with defaults). Fresh graveyards (e.g. Ray Johnson AT0R8L, Diane Rabelo J3R55L, created 6/12) DO have all customs populated — so current creation is fine.
- Calendly booking does NOT create a job — it only `job/update`s the existing graveyard job (zapier_calendly_booking_FLATTENED_FINAL.py `update_workiz_job`, sets JobDateTime/JobType/JobNotes). The "Sent→book directly" path = reactivation.py `api_reactivation_book` (L961) updated only JobType/JobDateTime.
- **TESTED: changing a Workiz job's JobType via job/update does NOT clear custom fields** (created a test job w/ customs, changed JobType Reactivation Lead→Solar Panel Cleaning, all customs survived; deleted test job). So booking does NOT wipe fields.
- Therefore Curtis's blanks = his graveyard lead is from **Feb 2 2026** — created BEFORE the enrichment fields were added to SA 563, so his graveyard job NEVER had them. Pure legacy. His historical job (8OEJN2) is itself sparse.

**FIX (deployed 2026-06-14):** booking-time safety net so ANY legacy/incomplete graveyard ends up complete when booked (mirrors the duplicate-job field set):
- `zapier_calendly_booking_FLATTENED_FINAL.py` `update_workiz_job` — now always fetches current job + carries custom fields forward (or defaults) in the update payload: Country=US, type_of_service_2/frequency/confirmation_method/ok_to_text/JobSource (current-or-default), gate_code/pricing/last_date_cleaned (if present). (Zapier fetches from GitHub = deployed.)
- `routers/owner/reactivation.py` `api_reactivation_book` (~L961) — same carry-forward on the reply-direct book path.
- **Added `"Country": "US"` to graveyard_data** — the ONLY field the duplicate-job builder sets that the graveyard create lacked. Patched LIVE SA 563 + GitHub `1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` (two-step deploy).
- Curtis's booked job P4HWHZ manually enriched (type_of_service_2=On Request, frequency=Unknown, confirmation_method=Cell Phone, ok_to_text=Yes, JobSource=Referral, pricing kept).

**PRICING NOW BAKED AT GRAVEYARD CREATION (2026-06-16, DJ "both places"):** SA 563's clone_ctx passed `clone_line_items=actual_prices_sent` (→ Workiz `next_job_line_items`) but `clone_extra` never set the Workiz **`pricing`** field — so the graveyard's pricing was only whatever the historical job had, NOT the quoted price. Added `'pricing': actual_prices_sent` to SA 563 `clone_extra` (overrides via SA 1338's extra-merge). Two-step deploy: live SA 563 patched + GitHub `1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` (553→554 lines). NEW graveyards now carry the quoted pricing. For the LARGE backlog of LEGACY graveyards (no pricing), the Book Job sheet has a **pre-filled editable Pricing field** (reactivation.html `bk-pricing`, pre-filled from the lead's `x_price_list_text`/`price_list`, bullets stripped) → `api_reactivation_book` accepts `pricing` and sets it on the Workiz job (overrides carried-forward). Both paths now ensure pricing is present. Also: reactivation Book success now `location.href='/owner/'` (dashboard) after opening Workiz Items in a new tab.

**Workiz quirk confirmed:** job/create REQUIRES Address (400 "Address: Field is Required" without it). Custom fields DO persist on job/create.

**LINE-ITEM CLIPBOARD ON BOOKING (built 2026-06-14, DJ "both places"):** graveyard `next_job_line_items` (format `• Name: $Price`, set at creation by SA 563 from the SMS price block) is now surfaced for one-tap paste into Workiz, mirroring the Phase 5 `p5CopyAndOpen` flow (parse `Name: $Price`, cycle each price+name through clipboard = separate clips in keyboard history, then open Workiz /items).
- **Activities page (Part A):** booking now creates a Phase 5-style activity (summary starts "Add tech + line items", note `Add tech + line items<br/>WORKIZ_UUID:{uuid}<br/>{Name: $Price lines}`, activity_type_id 15). `_strip_activity_html` turns `<br/>`→newline so activities.html `buildP5Card`/`p5ParseItems` renders the existing "📋 Copy Items & Open in Workiz" card. Added in BOTH: reactivation.py `api_reactivation_book` (res_model_id 431 crm.lead, res_id lead) AND cal.py `create_odoo_activity` (res_model_id 670 SO — reshaped the old "Calendly booking: Schedule in Workiz" To-Do into this P5 card).
- **Booking screen (Part B):** reactivation.html `doBook` now calls `reactCopyItems(d.line_items)` (two-clip copy) then opens `d.workiz_items_link` (.../job/{uuid}/items). `api_reactivation_book` returns `line_items` (bullets stripped) + `workiz_items_link`.
- ir.model ids: res.partner=90, crm.lead=431, sale.order=670.
