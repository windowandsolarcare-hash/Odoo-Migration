---
name: project_job_seed_shared_copier
description: "job_seed.py is the ONE shared job-copier for BOTH the link-booking seed path (booking.api_request) and the Duplicate-job button (dashboard.api_duplicate_job). Never write a second copier. Gate code seeds from the PROPERTY master, not the SO snapshot."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-03T19:10:59.953Z
---

**`routers/owner/job_seed.py`** (shipped 2026-09-02, per `3_Documentation/JOB_SEEDING_SPEC.md`) is the single shared copier that carries pricing/gate/service forward onto a new job. Two callers, one implementation — **do NOT write a second copier** (CLAUDE.md rule 9; two copies of pricing logic drift and the unwatched one goes stale).

**API:**
- `find_source_job(contact_id, job_type='', property_id=None)` → most recent **Done** (`x_studio_x_studio_workiz_status='Done'`, rule 2), priced (≥1 line qty>0 & price>0), `company_id=1` job for the contact (`partner_id child_of contact_id`), matching `x_studio_x_studio_x_studio_job_type` when supplied, **preferring the same property** (`partner_shipping_id`). Returns the SO dict or None. Never raises.
- `seed_values_from(src_so_id, property_id=None)` → `{'vals': {...}, 'prov': {...}}`. `vals` may hold `order_line` (0,0,…) cmds (skips `display_type` lines, identical to the old duplicate logic), `x_studio_x_studio_type_of_service_so`, `x_studio_x_studio_frequency_so`, and `x_studio_x_gate_snapshot`. `prov` = `{src_so_name, src_date, found, over_year}`. Never raises.

**★ Gate code seeds from the PROPERTY master (`res.partner.x_studio_x_gate_code`), not the source SO's snapshot.** The SO field is a day-of snapshot (can be stale / attached to the wrong property — the Debbie Church defect 2026-09-01); the property is the live master. Source snapshot is only the fallback. **`property_id=None` ⇒ source-snapshot-only**, which is exactly `api_duplicate_job`'s original behaviour — that's how the Duplicate button stayed byte-identical after the refactor.

**Callers:**
- `routers/booking.py` `api_request` — KNOWN customers only (`if pid`), whole seed wrapped in try/except so a seed failure NEVER breaks a booking (job lands unseeded = old behaviour). Posts provenance chatter (💲 carried / ⚠ >12mo / "priced from scratch"), appends `| seeded from <name> (<date>)` to `x_studio_creation_log`. Job stays **Submitted**; nothing auto-confirms/invoices/charges.
- `routers/owner/dashboard.py` `api_duplicate_job` (~line 7695) — refactored to `vals.update(seed_values_from(so_id)['vals'])` with property_id=None. It's a daily-use button; the extract is byte-identical (rules 10+11).

**TIP lines are excluded from the seed** (added 2026-09-03, DJ-approved): `seed_values_from`'s line-copy loop skips a line whose LINE name OR PRODUCT name is exactly `'tip'` (lowercased/trimmed — exact, never substring, so a real product containing 'tip' survives). Discounts and all other lines are kept. Because this is the shared copier, the **Duplicate job** button also no longer carries tips.

Estimator numbers from wscare.pro are OUT of scope — they're what the customer was shown, recorded as untrusted chatter, never merged into seeded lines. Related: [[feedback_reuse_canonical_endpoint]], [[feedback_question_when_big_picture_wrong]].
