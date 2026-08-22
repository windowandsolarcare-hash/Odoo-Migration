---
name: Session May 9 2026 Summary
description: QB expense import completed, Workiz/Odoo revenue cross-reference, Calendly Cathedral City fix in reactivation code
type: project
originSessionId: bcd62e72-19be-4a09-af3f-a38378b2ba9e
---
# Session May 9 2026

## What Was Done

### QB Historical Expense Import ✅
- Ran `import_qb_expenses.py` — 3,324 journal entries created, 0 failed
- Journal 3 (Miscellaneous Operations), credit Chase Checking account 100
- Covers expenses from 2019–2025
- JE IDs start around 6966, go to ~10290

### 2025 Revenue Cross-Reference (Workiz vs Odoo)
- Workiz Done total: $80,917 (444 jobs)
- Odoo invoice total: $79,062 (439 invoices)
- Gap: $1,855
- **7 Done jobs with no Odoo invoice** (all have SOs): 3284 Brooke Coldren $740, 3632 Brooke Coldren $490, 3478 Mike Mansi $220, 3647 Rik Ports $200 (SO=$160, short $40), 3462 Claudia Duran $185 (SO=$75, short $110), 2963 Jim Hitt $165, 3337 W&M Robinson $90
- Key issue: Odoo SO origin uses zero-padded numbers (003735) — must int() both sides to match
- 4 of 7 SOs are in draft state (bulk run skipped them), 3 are confirmed and ready to invoice

### 2025 P&L
- Revenue: $79,062 | Expenses: $46,502 | Net Income: $32,560
- Top expense: Raw Materials $8,690, Office Supplies $7,465, M&E $5,564

### 2026 YTD Revenue by Month
- Jan $2,392 | Feb $3,260 | Mar $7,315 | Apr $9,523 | May (partial) $6,489
- YTD total: $28,979

### Calendly Cathedral City Fix ✅
- **Root cause:** Reactivation code city_slug mapping was missing Cathedral City — fell through to `gb` (General Booking) which has Monday 8:30am–12pm availability
- **Fix:** Added `elif "Cathedral City" in city: city_slug = "cathedral-city-service"` to ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py
- Updated both GitHub (main) and live Odoo server action 563
- Also added PAIRED CHANGE comment in code listing all current slugs
- Added PAIRED CHANGES section to CLAUDE.md

## Accounting Migration Status
- Revenue invoices: ✅ 2,109 created, dates corrected
- Payments applied: ✅ (direct JE + reconcile)
- QB expenses: ✅ 3,324 JEs
- **Remaining:** Opening balances, fixed assets, loan accounts, CC bank feeds

## Key Technical Notes
- Calendly city slugs: pmsg (Palm Springs), cathedral-city-service (Cathedral City), rm (Rancho Mirage), pd (Palm Desert), iw (Indian Wells), indlaq (Indio/La Quinta), ht (Hemet), gb (General Booking fallback)
- General Booking (gb) has MONDAY 8:30am–12pm only — don't use as default for Desert cities
- Cathedral City event type URI: https://api.calendly.com/event_types/b7ca8953-c2ba-468d-b30e-8e7c46be7243
