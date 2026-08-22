---
name: SO line items with qty=0 / subtotal=0 are "soft-deleted" — ignore them
description: 2026-04-28 — Odoo blocks hard delete of order lines on confirmed sale.orders ("set to 0 instead" error). DJ's workflow is to zero out the qty/price as a soft-delete. Any analysis that walks order lines (service classification, totals, line counts) MUST filter out zero-value lines or it'll see ghosts.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Odoo blocks hard-delete of `sale.order.line` records on confirmed sale.orders (state `sale` or `done`) with `UserError("You cannot remove an order line ... set the quantity to 0 instead")`. DJ's standard workflow is to zero the line out — qty=0 and price=0 — as the "soft delete."

**Why:** caused a confusing case on 2026-04-28 — Bud Piraino's SO showed `Window ⚠` in the field assistant because my code saw both Solar and Window in his order lines. But the Solar line had been zeroed out by DJ — it was effectively deleted. The naive read pulled the line name regardless of its values.

**How to apply:**
- Any code that reads `sale.order.line` for analysis (service classification, line counts, billing summaries, etc.) must include `price_subtotal` and `product_uom_qty` in the fields and skip lines where both are zero.
- Don't try to delete the line yourself either — Odoo will reject it. Set qty=0 (and price=0) instead. Same rule applies for one-off scripts.
- Pattern:

```python
lines = odoo_rpc('sale.order.line', 'read', [line_ids],
    {'fields': ['id', 'name', 'order_id', 'price_subtotal', 'product_uom_qty']}) or []
for ln in lines:
    qty = float(ln.get('product_uom_qty') or 0)
    subtotal = float(ln.get('price_subtotal') or 0)
    if qty == 0 and subtotal == 0:
        continue  # soft-deleted
    # ... process the live line
```

- This is parallel to `project_so_unlink_needs_cancel.md` (which is about the SO itself, not its lines).

**Also note:** `amount_total` on the SO already correctly excludes zero-value lines (since they sum to 0 anyway), so SO-level totals are unaffected by this. The bug only surfaces in code that reads individual lines.
