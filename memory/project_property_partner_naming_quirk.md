---
name: Property partners may NOT contain the customer's name — search must walk Contact↔Property
description: 2026-04-30 — DJ has Property res.partner records named two different ways: "Customer Name, address" (e.g. "Betsy Justice, 255 E Avenida Granada") AND just the address ("47446 Rabat Dr"). A partner-name search for "betsy" misses the second pattern. Surfaced when Render Claude charged the wrong Betsy SO. Any code finding all of a customer's SOs MUST resolve the Contact, then enumerate child_ids — never rely on name-matching across properties.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when writing code that finds all of a customer's records (SOs, tasks, properties).**

## The data shape

DJ's Odoo customers are modeled as:

- **Contact** (res.partner with `x_studio_x_studio_record_category='Contact'`, `parent_id=False`, has `ref` = Workiz ClientId)
- **Property children** (res.partner with `x_studio_x_studio_record_category='Property'`, `parent_id=Contact.id`)

Property names are **inconsistent**:

| Property record | Name | Notes |
|---|---|---|
| id 26574 | `"Betsy Justice, 255 E Avenida Granada"` | "old style" — name + address |
| id 24957 | `"47446 Rabat Dr"` | "new style" — address only |

Both belong to the SAME contact (Betsy Justice, id 23238).

## Why it bites

A query like `name ilike "betsy"` returns the contact + the old-style property, but **misses** the address-only property. Any code that uses partner-name search to enumerate a customer's records will silently lose data.

Real incident (2026-04-30): Render Claude was asked to "Collect $170 from Betsy Justice." It found 1 SO via partner-name walk (the March 26 SO @ 255 Avenida, $0, empty) and tried to invoice that — failing with "No items available to invoice." The actual target SO ($170 @ 47446 Rabat Dr, April 3) was invisible because Property 24957's name doesn't contain "Betsy".

## Rule going forward

Always resolve via `parent_id`, never via name pattern:

```python
# Given any partner_id (could be Contact OR Property)
rec = odoo_rpc('res.partner', 'read', [[partner_id]],
    {'fields': ['parent_id', 'child_ids']})[0]
related = {partner_id}
contact_id = rec['parent_id'][0] if rec.get('parent_id') else partner_id
related.add(contact_id)
contact = odoo_rpc('res.partner', 'read', [[contact_id]], {'fields': ['child_ids']})[0]
related.update(contact.get('child_ids') or [])
# `related` now contains the contact + all properties — search SOs across that set
```

The helper `_find_invoiceable_sos_for_partner(partner_id)` in
`Saunders Render App/routers/owner/dashboard.py` (added 2026-04-30, commit 0e6726af) does this.

## Search by Workiz ClientId is more reliable

Every Contact has `ref` = Workiz ClientId (e.g. Betsy = `1417`). If you have a Workiz job and want to find the related Odoo Contact, search by `ref` — bypasses the naming inconsistency entirely.

```python
contact = rpc('res.partner', 'search_read',
    [[['ref', '=', str(workiz_client_id)]]],
    {'fields': ['id', 'child_ids']})
```

## Related memory

- `project_so_lines_zero_means_deleted.md` — DJ's qty=0/price=0 soft-delete pattern (also relevant to which SO is "real")
- `project_invoice_qty_delivered_gate.md` — invoice wizard gate (separate issue, doesn't fix this)
- `project_render_claude_tools.md` (and `reference_render_claude_write_tools.md`) — `record_check_payment` v2 now does the partner walk + multi-SO disambiguation + tip detection
