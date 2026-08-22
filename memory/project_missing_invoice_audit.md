---
name: project-missing-invoice-audit
description: "2026-06-04 audit of Done SOs with no invoice. 73 created+paid. Stephen Hatch flagged. Tip product pattern documented."
metadata:
  type: project
  node_type: memory
  originSessionId: 24c0a6e0-04f5-4a84-8f83-3a947fde2927
---

## Missing Invoice Audit — 2026-06-04

### Summary by Year (Done SOs, non-zero, no invoice)

| Year | Total Done | With Invoice | Missing |
|------|-----------|-------------|---------|
| 2020 | 167 | 147 | 20 |
| 2021 | 332 | 314 | 18 |
| 2022 | 337 | 317 | 20 |
| 2023 | 435 | 414 | 21 |
| 2024 | 497 | 477 | 20 |
| 2025 | 451 | 440 | 11 (not touched) |

### What Was Done

- **73 invoices created and marked paid** (2020–2024). Script: `C:\Users\dj\create_missing_invoices.py`
- **1 flagged — Stephen Hatch SO 001803** ($185, Feb 2023): Workiz shows -$5 balance (overpaid). Do NOT auto-invoice.
- **2025 intentionally skipped** — DJ decision.

### How Invoices Were Created

1. Draft SOs: `action_confirm()` → restore `date_order` (Odoo resets it)
2. Force `qty_delivered = product_uom_qty` on all SO lines
3. `sale.advance.payment.inv` wizard with `sale_order_ids=[[6,0,[so_id]]]`, `advance_payment_method='delivered'`
4. Set `invoice_date` = SO `date_order[:10]`
5. `action_post()` on invoice
6. Payment via JE + reconcile (Chase journal 6, AR account 6) — see [[project_odoo_payment_je_approach]]

### Tip Lines Fix

34 SOs had "Tips" lines with `product_id=False` — blocks invoice wizard with "Some order lines are missing a product." Fix: assign **Tip product id=2** to the line, then invoice normally.

**Why:** These tips were added as freeform lines without selecting a product. Always check for product-less lines before bulk invoicing.

### Workiz Balance Check

Used `JobAmountDue` field from `GET /job/get/{UUID}/` to verify each job was paid before creating invoice+payment. All 73 showed $0. Ran 74 API calls in batches of 25 with 20s sleep to avoid rate limit (429).
