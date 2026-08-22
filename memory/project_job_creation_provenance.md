---
name: project_job_creation_provenance
description: "Permanent \"how a job was created\" log on every sale.order (x_studio_creation_log). Scheduled stamper + at-source helper. SHIPPED 2026-06-16."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ (2026-06-16): "record how any job is created — a permanent log."** Built it. Choice = BOTH (scanner now + at-source over time), NEW jobs going forward (no back-fill).

## Field
**`x_studio_creation_log`** (text, id 20873) on **sale.order** (model_id 670). Permanent, queryable. Shown in the full-SO view ("Created Via", Order section of `/api/so_full`).

## Mechanism 1 — scheduled stamper (covers everything)
`routers/owner/provenance.py` → `stamp_creation_logs()`, scheduled in main.py APScheduler **every 15 min** (`_scheduled_provenance`). Registered router (manual trigger `POST /owner/api/provenance/run`).
- Watermark param **`creation_log.since`** (UTC). First run sets it to now → only NEW jobs forward get stamped (no back-fill). (Set to 2026-06-15 once to catch the demo batch.)
- Each run: finds `sale.order` with `create_date >= since` AND `x_studio_creation_log = False`, limit 60, builds a stamp, writes it. Self-guarding (never raises).
- Stamp from signals: if Workiz uuid → "via Phase 3 (Workiz sync) | Workiz #SerialId uuid | source: <JobSource> | Workiz created <CreatedDate> by <CreatedBy>" (does a live Workiz GET, capped **12/run** w/ 1s sleep for rate limits; falls back to stored lead_source if budget spent). No uuid → cross-ref `booking.requests.pending` (so_id) = "Online Booking page", or a crm.lead graveyard partner = "Reactivation campaign", else "Direct create (Odoo / manual)".
- VERIFIED: 004745 → "...via Phase 3 (Workiz sync) | Workiz #4745 ORJ9Q9 | source: Thumbtack | Workiz created 2026-06-14 23:47:42 by Dan Saunders". 13 recent SOs all stamped; S00125 correctly = "Direct create (Odoo / manual)".

## Mechanism 2 — at-source helper (precise)
`provenance.stamp_one(so_id, source_text)` + apps set `x_studio_creation_log` in their create vals. DONE: booking.py `/api/request` stamps "via Online Booking page (wscare.pro) | customer-submitted request | <job_type>". Scanner skips already-stamped SOs (field non-empty).

## TODO (the "over time" half of BOTH)
Add precise at-source stamps in the apps we control so they read their exact name (not the scanner's generic "Phase 3"): **Reactivation SA 563** (graveyard SO create), **New Job** (it creates the Workiz job via SA 1338 → would need a marker the scanner/Phase 3 reads, since Phase 3 makes the actual SO), **Duplicate** (SA 1338), and optionally **Phase 3** (Zapier) itself. New Job/Duplicate are tricky because Phase 3 (not them) creates the SO — needs a Workiz-side marker to distinguish from a job typed directly in Workiz.
