---
name: project_new_job_intake
description: New Job intake app (/owner/new-job) — was shadowed by a dashboard.py dupe; now creates+links a Workiz job via SA 1338. Read before touching intake/new-job.
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
  modified: 2026-08-01T07:00:51.132Z
---

**New Job intake app** = staff-facing "create a job from scratch" wizard (Customer → Property → Job). Page `/owner/new-job`, file `routers/owner/new_job.py` + `static/owner/new_job.html`. One of 3 booking funnels (online `/book`, reactivation, intake) — see [[project_customer_portal_booking]].

## ROUTE SHADOW FIXED 2026-06-15 (same trap as [[project_reactivation_route_shadowed_in_dashboard]])
The ENTIRE intake suite (`/new-job` + all `/api/intake/*`) was **DUPLICATED in dashboard.py** (registered before new_job.py in main.py) → dashboard's older copy SHADOWED new_job.py, which was effectively dead code. Symptom: edits to new_job.py had no effect; endpoint returned stale behavior ("Date required" even with valid input). **FIX: deleted the 446-line intake block from dashboard.py (it was byte-identical to new_job.py minus new edits — diffed first). new_job.py now OWNS the routes. EDIT new_job.py, not dashboard.py.** dashboard.py 12290→11844 lines.

## NEW JOB → DIRECT ODOO (FLIPPED 2026-07-31, Workiz retirement Role 1 — LIVE, deployed to main)
**New Job now creates the Odoo SO DIRECTLY — no Workiz job, no SA 1338, no Phase 3.** This replaced the old Workiz-only flow when Workiz was retired (goes dark 2026-08-03). See [[project_workiz_retirement]], [[project_so_numbering_post_workiz]].
- `api_intake_create_job` now: writes gate/pricing to the property master, computes the job number via `_next_job_name()`, then creates a **DRAFT `sale.order`** and returns `{ok, so_id, so_name}`.
- **partner_id = partner_invoice_id = partner_shipping_id = the PROPERTY** (property-as-brain; the person is property.parent_id). The OLD commented block wrongly used contact_id as partner_id — fixed.
- **Number = `_next_job_name(service_dt)` = YY(service-year) + climbing counter**, e.g. `264935`. Counter = Odoo `ir.sequence` **code `wsc.job.seq`** (id 40, prefix '', padding 1, started at 4935 = one past legacy max 4934, company_id=False). `_next_job_counter()` lazily creates the seq if missing. Name set at create (no rename, no confirm dance). Verified: next_by_code→'4935', name→'264935'.
- **Status = `x_studio_x_studio_workiz_status='Submitted'` and the SO is left DRAFT (NOT confirmed)** = reserved, NOT on the schedule. DJ advances the status later (scheduling/confirm path = Role 4, NOT built yet).
- Also sets: `x_studio_x_studio_lead_source='Referral'` (default), tech, gate/pricing snapshots, job_type (validated), `x_job_length_min`, and `order_line` with **qty** (`product_uom_qty` from the screen's per-line qty — see qty fix below).
- Success screen: "Job created ✓ · #<number>" + "Submitted (reserved). Set it to Scheduled when ready." No Workiz link/paste.
- **DEFERRED (follow-ups, not yet done):** (1) SO `tag_ids` from the contact (Phase 3 merged contact+Workiz tags; skipped for now — sale tags are crm.tag by NAME, needs the get_sales_tag_ids mapping). (2) `project_id`/DEFAULT_PROJECT_ID (only needed at confirm-time for task-creating products; draft doesn't need it). (3) `x_studio_x_studio_frequency_so` / `type_of_service_so` at create for maintenance/recurring. (4) **Role 4: an app-side way to move a Submitted draft → Scheduled/confirmed** (was the Workiz status flip → Phase 4). Full field diff: `3_Documentation/NEW_JOB_FIELD_COMPARISON.md`.
- (History: 2026-06-15 Design B keep-SO+link; 2026-06-16 reverted to Workiz-only for numbering; 2026-07-31 flipped to direct-Odoo when Workiz retired.)

## LINE QTY (fixed 2026-07-31)
The line model (`S.lines` in v2_new_job.html) gained `qty`. Book/Duplicate now carry the source job's quantity, each line shows an editable qty box (× unit price), the total = Σ(qty×price), and qty rides into the create payload → `product_uom_qty`. Before this every line was implicitly qty 1 (a 28×$5 job booked as $5). `/api/intake/recent-jobs` card total also fixed to `Σ price_subtotal` (was `Σ price_unit`).

## KEY FACTS / GOTCHAS
- **SA 1338 supports from-scratch create** (empty source → defaults + clone_extra). **Workiz REQUIRES Address on create** — if the property has no `street`, create returns 400 and uuid comes back empty (graceful: SO still created, `[NEW-JOB]` logged). Real UI properties always have a street.
- **Workiz job DELETE API:** `POST /job/delete/{UUID}/` with JSON body `{'auth_secret':SEC, 'ID':UUID}` — the **`ID` field in the body is REQUIRED** (URL uuid alone → 400 "ID Field is Required"). GET form does not work.
- **Testing the Workiz-create path triggers Phase 3 via the real Workiz webhook**, which creates a contact+property (sometimes from the webhook payload) even if you delete the Workiz job seconds later. **Test cleanup MUST sweep for Phase-3-spawned res.partner by name/phone**, not just the SO + Workiz job. (Saw a 3rd ZZTEST contact appear from Phase 3.)
- **PT→UTC fixed:** new_job.html now sends `date_pt` (naive Pacific 'YYYY-MM-DD HH:MM:SS'); backend derives `date_order` via `_PT` (DST-correct). Old code hardcoded +7h (wrong Nov–Mar PST). Backend also derives `job_dt_pt` for the Workiz JobDateTime.
- **Multi-company:** `/api/intake/products` now filters `company_id in [1, False]` — without it, Saunders/Cheryl products appeared and picking one 500'd with a company-mismatch (CLAUDE.md rule 8). NOTE STILL OPEN: `/api/intake/employees` (hr.employee) and suggest-dates/suggest-time (sale.order) are NOT yet company-filtered.
- Still uses the OLDER suggest-dates engine (soonest open day + job count), NOT the route-tightest GPS/map engine — pending the (b) shared-scheduler refactor (reactivation + new_job + booking_requests all to share booking.py slots + _haversine + Leaflet/OSRM map).
