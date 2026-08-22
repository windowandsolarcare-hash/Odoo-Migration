---
name: Phase 4A comprehensive Workiz sync
description: Full SO field sync before payment (stale SO + Field Assistant) — all Workiz fields checked
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**ENHANCED 2026-05-01 (v2 — comprehensive)**

## What
Phase 4A is a comprehensive pre-payment sync function (`_sync_so_with_workiz()`) that ensures Odoo SOs match Workiz job data **completely** before accepting payment.

**v1:** Line-count only  
**v2 (CURRENT):** Full field sync — 10+ fields + line items

## Fields synced from Workiz → Odoo
- `x_studio_x_studio_workiz_status` (SubStatus)
- `x_studio_x_studio_workiz_tech` (Team member names)
- `x_studio_x_gate_snapshot` (Gate code)
- `x_studio_x_studio_pricing_snapshot` (Pricing snapshot)
- `x_studio_x_studio_notes_snapshot1` (JobNotes)
- `x_studio_x_studio_x_studio_job_type` (Job type)
- `x_studio_x_studio_lead_source` (JobSource)
- `date_order` (JobDateTime UTC)
- `tag_ids` (Tags)
- `order_line` (Line items: product ID, qty, price, description)

## How it works
1. Fetches SO with all Workiz fields + line items
2. Fetches Workiz job data
3. Compares each field (status, tech, gate, pricing, notes, job type, source, date, tags)
4. **Compares line items** by (name, qty, price) tuples — not just count
   - Handles "customer changes mind at door" scenario: Inside+Outside → Outside only
   - Detects qty or price changes
5. If any mismatch found:
   - **If SO confirmed (state='sale'):** cancel → draft → delete unmatched lines → re-confirm
   - **If SO draft:** just write field updates
6. Restores date_order after confirm (Odoo resets it)
7. Returns {'ok': bool, 'synced': bool, 'message': str, 'fields_updated': int}

**Early exit:** If all fields match AND line items match exactly → skip cancel/confirm (no disruption)

## Integration points
- **Function:** `_sync_so_with_workiz(so_id)` (line 4782)
- **Endpoint 1:** `/api/record_zelle_payment` (stale SO) — **BLOCKING**: fails payment if sync fails
- **Endpoint 2:** `/api/payment` via `_execute_payment()` (Field Assistant) — **NON-BLOCKING**: logs error but proceeds
- Both called **before** invoice creation

## Edge cases
- No Workiz UUID: skips (ok=True, synced=False)
- Workiz job missing: skips gracefully
- Workiz fetch fails: blocks payment (stale) or logs warning (Field Assistant)
- Line deletion fails: blocks payment
- DateTime conversion fails: silently skips (non-blocking)

**v2 rationale:** User requirement for low-frequency operations (like accepting payment) — "ensure EVERYTHING is synchronized, not just line counts."

## Phase 4 vs Phase 4A Logic

**The sync logic is identical.** Both check the same 10+ fields + compare line items the same way (tuple-based sets).

**Differences:**
- **Phase 4** (Workiz status changes): Field sync + task creation/deletion + full job lifecycle management
- **Phase 4A** (Before payment): Field sync only (verify + auto-fix), no task operations

**Trigger distinction:**
- Phase 4: Triggered by Workiz webhook (status change or job update)
- Phase 4A: Triggered before payment acceptance (manual via Render Claude tool or stale SO endpoint)
