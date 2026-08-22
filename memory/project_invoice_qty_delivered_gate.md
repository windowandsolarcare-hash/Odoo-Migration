---
name: Invoice wizard refuses when qty_delivered=0 — must force-deliver SO lines before invoicing
description: 2026-04-30 — Odoo's sale.advance.payment.inv wizard fails with "No items available to invoice" when SO lines have qty_delivered < product_uom_qty AND the product invoicing policy is 'delivery' or service_policy is 'delivered_timesheet'. Surfaced collecting Zelle for Betsy Justice via Render Claude. Fix: write qty_delivered=product_uom_qty on real lines (qty>0, price>0) BEFORE calling create_invoices. Helper `_force_lines_deliverable(so_id)` lives in Saunders Render App/routers/owner/dashboard.py and is called by both record_check_payment and _execute_payment.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when editing any code that creates an invoice from a sale.order.**

## The gate

Odoo's `sale.advance.payment.inv.create_invoices()` wizard (Odoo 19) raises `UserError("Cannot create an invoice. No items are available to invoice.")` when **every** non-deleted SO line has `qty_to_invoice <= 0`.

`qty_to_invoice` is computed from the product's invoicing policy:

| Product type | invoicing policy | What gates `qty_to_invoice` |
|---|---|---|
| Storable / consumable | `order` (Ordered Quantities / Prepaid) | `product_uom_qty - qty_invoiced` (always available once SO confirmed) |
| Storable / consumable | `delivery` (Delivered Quantities) | `qty_delivered - qty_invoiced` (requires stock delivery or manual write) |
| Service | `service_policy='ordered_prepaid'` | Same as `order` above |
| Service | `service_policy='delivered_manual'` | Same as `delivery` — set `qty_delivered` manually |
| Service | `service_policy='delivered_timesheet'` | Sums hours from `account.analytic.line` (timesheets) for the linked task |
| Service | `service_policy='delivered_milestone'` | Requires milestone reached |

Most W&SC service products are `delivered_timesheet` or `delivered_manual`. If DJ collects payment **before** logging timesheets / before marking the FSM task done, `qty_delivered=0` on every line, `qty_to_invoice=0`, wizard refuses.

## The fix (already deployed 2026-04-30, commit 3f80c1d5)

Helper `_force_lines_deliverable(so_id)` in `Saunders Render App/routers/owner/dashboard.py`:

```python
lines = sale.order.line.search_read(domain, fields=['id', 'product_uom_qty', 'qty_delivered', 'price_unit'])
for ln in lines:
    if qty > 0 and price > 0 and delivered < qty:
        write({'qty_delivered': qty})
```

Called BEFORE `sale.advance.payment.inv.create_invoices` in both invoice paths:
1. `record_check_payment` tool (Render Claude voice flow) — line ~1300
2. `_execute_payment` (`/api/payment` field-assistant flow) — line ~2740

## Rules going forward

- **Never call `sale.advance.payment.inv.create_invoices` without first ensuring qty_delivered ≥ qty_ordered on the lines you want invoiced.** Always either (a) call `_force_lines_deliverable` first, or (b) verify timesheets are logged.
- **Soft-delete pattern compatibility** — DJ uses `qty=0 + price=0` to "delete" lines on confirmed SOs. The helper skips these (filters on `qty > 0 AND price > 0`) so it doesn't accidentally revive them.
- **Idempotent** — running it twice writes the same value the second time. Safe to call on every invoice attempt.
- **Future task→delivered hook compatibility** — if DJ marks the FSM task done after invoicing, Odoo's industry_fsm_sale module sets `qty_delivered=qty_ordered`. Same value we already wrote, no conflict.
- **Phase 6 / Zapier paths** — if any future Zapier code creates invoices from Odoo, replicate this pattern. Phase 6 currently goes Odoo→Workiz only (payment sync), not invoice creation, so it's not affected.

## What surfaced this

DJ tried "Zelle from Betsy Justice" via Render Claude. `record_check_payment` ran, fetched SO, found no draft invoice, called `create_invoices` → wizard threw the UserError. Bug existed silently in `_execute_payment` too — never triggered because most field-assistant payments happen after timesheets are logged.

## Related memory

- `project_so_lines_zero_means_deleted.md` — the qty=0/price=0 soft-delete pattern the helper respects
- `project_phase6_tech_gate.md` — payment-sync direction (Odoo→Workiz, not the other way)
- `feedback_done_jobs_definition.md` — "Done" = `x_studio_x_studio_workiz_status='Done'`, NOT invoice/payment state (relevant if you're tempted to gate this on Done status)
