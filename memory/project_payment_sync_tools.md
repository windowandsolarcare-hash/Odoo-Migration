---
name: Payment sync Render Claude tools
description: sync_so_verify + process_payment_with_sync tools for voice-driven payment flow
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
## What They Do

**2026-05-01:** Two Render Claude tools added for payment flow integration.

### sync_so_verify
- **Purpose:** Verification only — report what sync changed before accepting payment
- **Input:** so_identifier (SO ID, SO name, Workiz UUID, or customer name)
- **Output:** Detailed sync report (fields changed, lines matched, status)
- **Triggers:** User says "sync Fred Jones open job" or "sync SO-12345"
- **Resolves identifiers:** Customer name → finds open invoiceable SO → grabs UUID automatically

### process_payment_with_sync
- **Purpose:** Full transaction — sync first, then process payment
- **Input:** so_identifier, amount, date (defaults to today if omitted)
- **Flow:** (1) sync all fields + line items, (2) create invoice, (3) record payment
- **Auto-fix:** If sync detects mismatches, runs cancel→draft→update→confirm before invoicing
- **Output:** Sync report + invoice confirmation + payment receipt
- **Triggers:** User says "process payment for Fred Jones" or "I received $150 from [customer]"

## Natural Language Resolution

Both tools support identifier resolution:
1. Try numeric SO ID
2. Try SO name (e.g., "SO-2024-001")
3. Try Workiz UUID
4. **Try customer name** — searches res.partner by name, finds their most recent open invoiceable SO (state in [sale, done] AND invoice_status='to invoice')

**Result:** User can say "sync Fred Jones" without knowing the SO ID or UUID — the tool finds everything automatically.

## Implementation Details

**Endpoints:**
- `POST /owner/api/sync_so_verify` — verification only
- `POST /owner/api/process_payment_with_sync` — full payment + sync

**Helper function:**
- `_find_so_by_identifier(identifier: str)` — resolves SO by ID/name/UUID/customer name

**Sync logic:**
Uses Phase 4A `_sync_so_with_workiz(so_id)` which:
- Compares 10+ fields (status, tech, gate, pricing, notes, job type, lead source, date_order, tags)
- Compares line items as (name, qty, price) tuples
- Only runs cancel→draft→confirm if differences found (early-exit optimization)
- Returns {'ok': bool, 'synced': bool, 'message': str, 'fields_updated': int}

## Voice Scripts

**Sync verification:**
- "Sync Fred Jones open job"
- "Sync SO-12345"
- "Check if the sync matches for [customer]"

**Payment processing:**
- "Process payment for Fred Jones"
- "I received $150 from [customer]"
- "Accept payment for [customer] on [date]"

## Commits
- First push (endpoints only): cd8a16a
- Tool registration: 73ed4ac
- Natural language resolution: ff7829c
