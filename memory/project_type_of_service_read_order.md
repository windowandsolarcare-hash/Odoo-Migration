---
name: project_type_of_service_read_order
description: "type_of_service / frequency display must read the SO field first, then Property, NEVER the contact (parent) which is often stale 'Unknown'. Recurring 'wrong field' bug."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**RULE — canonical read order for a job's type_of_service and frequency (display anywhere):**
1. **SO field** (per-job): `x_studio_x_studio_type_of_service_so` (Maintenance/On Request/Unknown), `x_studio_x_studio_frequency_so` (3/4/6/12 Months).
2. **Property record** (`partner_shipping_id`): `x_studio_x_type_of_service`, `x_studio_x_frequency`.
3. **Contact (parent)** `x_studio_x_type_of_service` / `x_studio_x_frequency` — LAST resort; **this is frequently stale `Unknown`** and must NOT be the primary source.

**Why:** DJ reported (2026-06-14) Karen Bellamy's last job (SO 004558 / id 17286) showed type_of_service `Unknown` on the field detail screen + the new booking portal — but it IS `Maintenance`. Root cause: code read the CONTACT field (22975 = `Unknown`) while the SO field = `Maintenance` and the Property (24097) = `Maintenance`. `frequency` was already done right (SO-first); `type_of_service` was the one reading contact-only. "Looking at the wrong field AGAIN" = this exact class.

**FIXED 2026-06-14 (dashboard.py commit 5860bce2, booking.py 5bbd6bea):**
- `api_so_history` (~4367) + 4 schedule builders (tool_get_schedule ~581, api_upcoming ~5219, the ~8602 builder, and the ~5219 dup) now: `so.get('x_studio_x_studio_type_of_service_so') or <partner fallback>`. Added `x_studio_x_studio_type_of_service_so` to each SO `search_read` field list (4328, 536, 5090, 8483). Initialized `type_of_service` before the no-partner branch in so_history to avoid NameError.
- booking.py `/api/me`: "usual" `type_of_service`/`frequency` now = Property → most-recent SO `*_so` → contact; per-job `type_of_service` added to history rows.

**When adding ANY new place that shows a job's service type/frequency:** read the SO `*_so` field first. Grep for `x_studio_x_type_of_service` used as a PRIMARY source = likely the same bug. Related: [[project_customer_portal_booking]], CLAUDE.md field table (Type of Service SO / Frequency SO rows).

## FULL AUDIT + CONTACT→PROPERTY RE-POINT (2026-06-14, DJ-directed)
DJ's data model (CONFIRMED, important): **SO = historical snapshot** (what it was that visit, e.g. gate 1234), **Property record = CURRENT truth** (gate now 6789), **Contact/parent copy = legacy, stale** (he built these fields early for old Odoo screens; now on Render). Quantified: **354 of 355** contacts whose property has a real type_of_service have a blank/`Unknown` contact-level value. So the contact-level copies of gate/pricing/frequency/type_of_service are the stale/redundant ones.

The 4 value triplets — SO snapshot field | Property(current) field | Contact(legacy) field:
- Gate: `x_studio_x_gate_snapshot` | `x_studio_x_gate_code` | `x_studio_x_gate_code`
- Pricing: `x_studio_x_studio_pricing_snapshot` | `x_studio_x_pricing` | `x_studio_x_pricing`
- Frequency: `x_studio_x_studio_frequency_so` | `x_studio_x_frequency` | `x_studio_x_frequency`
- Type of service: `x_studio_x_studio_type_of_service_so` | `x_studio_x_type_of_service` | `x_studio_x_type_of_service`
(Property & Contact share the SAME res.partner field name — difference is which record: child Property vs parent Contact.)

**RE-POINTED contact→property (commits dashboard 3dc27eaa, reactivation d1f3a297):** reactivation **candidates** + **open_by_partner** + **preview** (detail) + **followup/preview** now read service/frequency/pricing from the customer's PROPERTY (fallback to contact). ⚠ These 4 routes are DUPLICATED and **dashboard.py SHADOWS reactivation.py** (dashboard registered first in main.py L102 vs L106) — so the LIVE fix is in dashboard.py; reactivation.py edited too to keep the twins in sync. See [[project_reactivation_route_shadowed_in_dashboard]].

**LEFT AS-IS (legit, no change):** WRITES to contact/property master (intake create, new_job, field maps shared.py 196-200 + dashboard 307-311); PROPERTY reads (analytics, _hemet_candidates, hemet.py, new_job.html); per-job schedule-builder *fallbacks* to contact (dashboard 554/5148/8543 — only fire when the SO snapshot is empty, which is ~never, so low value); `tool_get_customer_profile` (AI helper, person-level by design). These are the right field for their context OR a harmless fallback.

**REMAINING IDEA (not done):** the contact-level copies could eventually be retired entirely once nothing reads them as primary; for now they're still WRITTEN on new-customer creation, so leave the fields. Don't delete Odoo fields without DJ.
