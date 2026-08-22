---
name: Odoo action_confirm resets date_order to current time
description: Calling action_confirm() on a sale.order resets date_order to datetime.now() — must write it back immediately after confirming
type: project
---

Odoo's `action_confirm()` internally resets `date_order` to the current timestamp as part of its confirmation logic.

**Why:** When Phase 4 confirms an existing draft SO (e.g. user changes job status to Pending Scheduled on a job whose SO was previously created but never confirmed), `date_order` gets overwritten with the current time instead of the Workiz JobDateTime. First observed on SO 004253 (2026-04-01). Does not affect new SO creation because the date is set in the creation payload before confirm runs in the same transaction.

**How to apply:** After any `action_confirm()` call on an existing SO, immediately do a separate `write` call to restore `date_order` to the correct UTC value. In Phase 4, `confirm_sales_order(so_id, date_order_utc=...)` now does this automatically — always pass the date when calling it.
