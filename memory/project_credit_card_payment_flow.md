---
name: Credit card at-door payment flow
description: How credit card payments taken at the door in Workiz are handled differently in Phase 6
type: project
---

When Dan collects a credit card payment at the job site, Workiz records it immediately but does NOT auto-mark the job Done. This is the ONLY scenario where `JobAmountDue = 0` AND `Status != Done`.

**Why:** Credit card is collected in Workiz app on site. All other payment types (check, cash, Zelle) go through Odoo first — Phase 6 posts the payment to Workiz AND marks Done. Credit card is the reverse: payment already in Workiz, needs to flow to Odoo.

**How to apply:**

Detection in Odoo: "Sync from Workiz" server action (ID 955) checks `JobAmountDue == 0` AND `Status != Done` → sets `x_studio_pricing_mismatch` to **yellow** (`bg-warning text-dark`) "Credit Card Payment Received - Invoice in Odoo using Credit method".

DJ workflow:
1. Hit Sync from Workiz → sees yellow warning
2. Create invoice in Odoo, register payment using **"Credit"** method (account.payment.method.line ID 7)
3. Phase 6 fires, sees `workiz_type = "credit"` (derived from Odoo payment method, NOT Workiz) → **skips** addPayment to Workiz (already there) → marks job Done → flips field to green → triggers Phase 5

Phase 6 change: single `if workiz_type == "credit": skip addPayment` block around the Workiz POST. Everything else (mark Done, Phase 5 trigger) unchanged.

**Key field:** `x_studio_pricing_mismatch` on `sale.order` (HTML field)
- Yellow (`bg-warning text-dark`): credit card received, not yet invoiced in Odoo
- Green (`text-success`): fully processed — set by Phase 6 after marking Done
- Red (`text-danger`): pricing mismatch between Workiz and Odoo totals
