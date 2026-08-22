---
name: project_frequency_service_architecture
description: "Frequency + Type-of-Service live in 3 places (SO / property / contact). WORKIZ is master; property+SO mirror down from it. Property is the reliable value; display falls back SO→property."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Three locations (verified 2026-07-13):**
- **sale.order** — `x_studio_x_studio_frequency_so`, `x_studio_x_studio_type_of_service_so` (Selection). A **per-job snapshot** of that Workiz job. NOTE: on dormant **Submitted** next-jobs it's usually **blank (448 of 526) or stale** — Phase 4 only re-syncs on a status change, so a future job keeps whatever it was born with.
- **PROPERTY record** (res.partner, `record_category='Property'`) — `x_studio_x_frequency`, `x_studio_x_type_of_service` (char). **The MASTER / reliable value** for the address's cadence. Kept current from Workiz by Phase 4.
- **CONTACT record** (res.partner, the person) — same char fields but **usually blank** for property-based customers (non-player).

**Data flow — WORKIZ is the true master; everything mirrors DOWN (there is NO SO→Workiz and NO auto SO→property):**
- **Phase 4** (5-min poll, on status change): Workiz → property `x_studio_x_frequency` (via `update_property_fields`) AND Workiz → SO `frequency_so`.
- **SA 955** (the 🔄 Sync button, per-job): Workiz → SO, then **rolls the SO's values UP to the property** IF this is the property's most-recent non-canceled job (non-empty only, so a blank never wipes the master). ← this IS the "SO→property on save" DJ wanted; it already exists, manual.
- **Phase 5** (job Done): reads the completed **Workiz** job's frequency to schedule the next cycle.
- **DJ's workflow:** he edits frequency **at the door IN WORKIZ** (Workiz still live). Correct + master-aligned. He does NOT edit it in the field app.

**The bug DJ hit (Carlos Esparza SO 004824 / Linda-style):** header "Unknown", details "3 Months", Workiz/property "6". Cause = (a) dormant Submitted SO's `frequency_so` was stale/blank; (b) `api_so_full` (dashboard.py) **never returned a top-level `frequency`/`type_of_service`** — the field.html header reads `activeJob.frequency` which was undefined → "Unknown". Details read the raw SO field (groups). So header ≠ details, and neither fell back to the property.

**FIX (2026-07-13, commits dashboard 4069bbb / field.html 58e504a):** `api_so_full` now returns top-level **`frequency`/`type_of_service` resolved SO-first, else PROPERTY** (`_eff(so_val, prop_val)` — reads partner_shipping_id then partner_id's `x_studio_x_frequency`). field.html `loadFullDetails` pushes those into the header (`ap-freq` + `pay-svc-meta`); `renderAppointment` triggers `loadFullDetails` on open when `job.frequency` is missing so the header resolves without needing an expand. Result: header + details show the real cadence (property fallback), never a false "Unknown". Optional un-done: one-time backfill of the 448 blank Submitted `frequency_so` from their property (cosmetic — the display fallback already fixes what's shown). Carlos's SO manually set to 6 to match his property. See [[project_stop_optout_true_count]] pattern of "one true value", CLAUDE.md ODOO CUSTOM FIELD NAMES.
