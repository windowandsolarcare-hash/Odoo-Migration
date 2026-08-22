---
name: project_workiz_sync_field_casing
description: "Daily SO↔Workiz sync false 'Workiz=blank' discrepancies come from wrong-CASE Workiz JSON keys in _sync_so_with_workiz. Workiz job GET mixes Capitalized and lowercase field names."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce7b153f-3bb6-4e33-a982-35d4d7a9f4ba
---

# Workiz job GET returns MIXED-CASE field names — sync must match exactly

**Root cause of false "⚠ Workiz blank fields" reports on the daily sync (found 2026-07-04, SO 004689 Kay Masonbrink):** `_sync_so_with_workiz` in `routers/owner/dashboard.py` (saunders-render-app, ~line 9491) read the pricing field as `workiz_job.get('Pricing')` — **capital P**. The real Workiz job JSON key is lowercase **`pricing`**. `.get('Pricing')` → None → treated as blank → `_sync_field` records a bogus discrepancy `Odoo='…' Workiz=blank` even though Workiz and Odoo actually MATCH. Fixed `'Pricing'`→`'pricing'` (commit 630ef356, 2026-07-04). No data was wrong — Odoo, the property master, AND Workiz all held `145.00 Every 4 to 5 Months In & Out`; only the report was lying.

**FOLLOW-ON FIX same day (commit e55a9920): Workiz `pricing` is sometimes an INT, sometimes a string.** After fixing the key case, `(workiz_job.get('pricing') or '').strip()` crashed `'int' object has no attribute 'strip'` on 13 jobs where Workiz pricing = a bare number (e.g. 160, 90, 150) instead of a descriptive string ("145.00 Every 4 to 5 Months In & Out"). Fixed with `str(...)` wrap: `workiz_pricing = str(workiz_job.get('pricing') or '').strip()`. Safe because those jobs' Odoo snapshots were blank or bare numbers (no descriptive note to clobber). AFTER both fixes the daily report ran clean: 49 SOs, **0 errors, 0 discrepancies** (was 13 errors + false pricing discrepancies). Lesson: str()-wrap any Workiz numeric-ish field before .strip().

**Workiz `job/get/{uuid}/` field-name casing (verified 2026-07-04) — do NOT guess:**
- **Capitalized:** `Status`, `SubStatus`, `JobNotes`, `JobType`, `JobSource`, `JobDateTime`, `JobTotalPrice`, `JobAmountDue`, `SubTotal`, `ServiceArea`, `Team`, `LineItems`, `LastStatusUpdate`, `UUID`.
- **lowercase:** `pricing`, `frequency`, `type_of_service_2`, **`gate_code`**.
- **GATE CODE = SAME BUG as pricing, fixed 2026-07-04 (commit 1f68a21a).** `_sync_so_with_workiz` line 9490 read `workiz_job.get('GateCode')` (capital) → always None → gate ALWAYS false-flagged "Workiz=blank" and never synced. Verified against 5 gated jobs (SO 004680/004812/004735/004654/004550): the real key is lowercase **`gate_code`** every time, never `GateCode`. Fixed to `workiz_job.get('gate_code') or workiz_job.get('GateCode')` (dual-case, mirrors the read-path at dashboard.py 1775 & 6857). DJ predicted this ("gate code is same problem as pricing") — he was right.

**The sync architecture (so you know where to look):**
- Odoo cron [68] "WSC Daily SO Sync with Workiz" (SA 1158) just does `requests.get('https://wsc-field-assistant.onrender.com/owner/api/cron/daily_sync?token=wsc-daily-sync-2026')` — all real logic is in the RENDER app, not Odoo.
- `routers/owner/cron.py` `daily_sync` loops non-Done SOs with a uuid → calls `_sync_so_with_workiz(so_id)` (dashboard.py) → aggregates `r['discrepancies']` into the "⚠ Workiz blank fields" summary.
- `_sync_so_with_workiz` fetches `httpx.get('.../job/get/{uuid}/', timeout=15)` (NO User-Agent — fine from Render; only a non-Render box like DJ's Windows gets 403 without a browser UA, see below), then `_sync_field(odoo_val, workiz_val, field, label)`: if Workiz has a value and differs → update Odoo; if Workiz blank but Odoo has value → record discrepancy (never overwrites Odoo with blank — good).

**Gotcha for LOCAL Workiz API testing:** calling `api.workiz.com/api/v1/{token}/job/get/{uuid}/` from DJ's Windows box with default `urllib`/`httpx` user-agent returns **HTTP 403**. Add `headers={'User-Agent':'Mozilla/5.0'}` and it works. This is machine/edge-specific (Render is NOT affected — it gets 200), so it does NOT explain the sync bug; don't chase the 403 as the cause. **How to apply:** when debugging any "field=blank on sync" report, first fetch the live Workiz job (with a UA header) and check the EXACT key casing before assuming data is missing.
