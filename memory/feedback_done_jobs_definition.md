---
name: Definition of DONE jobs
description: When DJ says "Done jobs" he means x_studio_x_studio_workiz_status = 'Done' on sale.order
type: feedback
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
When DJ says "Done jobs" or "completed jobs" he always means **`x_studio_x_studio_workiz_status = 'Done'`** on `sale.order`.

**Why:** That field stores the Workiz job status synced to Odoo. Historic jobs (Phase 1 migration) and current jobs (Phase 3/4) all have this field populated. Invoice-based proxies are WRONG — historic jobs were never invoiced through Odoo.

**How to apply:**
- Filter: `['x_studio_x_studio_workiz_status', '=', 'Done']` on `sale.order`
- Never use `state='done'`, `invoice_status='invoiced'`, or `invoice_ids != False` as a proxy for Done
- Never use `date_order < now` alone — that picks up future-scheduled and pending jobs
- `amount_total` is the correct field for job value (sum of line items)
