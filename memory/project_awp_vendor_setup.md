---
name: Active Window Products vendor setup in Odoo + ordering rules
description: 2026-04-29 — DJ's primary screen-frame supplier. Vendor partner 26936, Customer ID 55145, Tax Exempt (resale fiscal position id 5). Order emails go to BOTH Jaime Gutierrez + Valerie Campos. 33 frame products imported with vendor pricing.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when creating POs to Active Window Products, editing AWP vendor, or building the voice-driven PO tool.**

## DJ's names for this vendor — match all of these

DJ refers to this vendor as any of: **Active**, **AWP**, **Active Window**, or **Active Window Products**. All should resolve to partner 26936. The vendor record's `x_aliases` field lists these explicitly: `"Active, AWP, Active Window, Active Window Products"`.

When parsing voice/chat, match on:
1. The partner's `name` field
2. The partner's `x_aliases` field (split on comma, strip)
3. Substring match — "active" or "awp" anywhere in DJ's text → this vendor

The same alias pattern should be applied to other vendors as we add them (Precision, etc.) by populating their `x_aliases` field.

## Vendor record

- **Partner ID:** 26936
- **Name:** Active Window Products
- **Address:** 5431 San Fernando Road West, Los Angeles, CA 90039
- **Phone:** (323) 245-5185 · Fax: (818) 246-5188
- **AWP Customer ID:** `55145` (stored in `ref` field)
- **Tax status:** Tax Exempt (resale) — `property_account_position_id` = fiscal position id 5 ("Resale - Tax Exempt"). Future POs auto-skip sales tax.
- **Supplier rank:** 1

## Default PO email template — `x_default_po_template_id`

A custom many2one field `x_default_po_template_id` on `res.partner` points to `mail.template`. AWP's value is set to template **id 49 "AWP Order Request"** — DJ's preferred Part No / Qty / Est. Price format with both Jaime + Valerie on TO.

Future PO-sending tools (Render Claude voice tool, scripts, automations) should read `partner.x_default_po_template_id`; if set, use that template. If empty, fall back to standard "Purchase: Purchase Order" (id 47).

This pattern is reusable for other vendors — set their `x_default_po_template_id` to a vendor-specific template and the tool picks it automatically.

## Order email rule — TO BOTH

When sending a PO email to AWP, recipients are **Jaime + Valerie** (both on TO line). The parent partner's `email` field is set to a comma-separated string so Odoo's "Send by Email" button does this automatically:

```
j.gutierrez@activewindowproducts.com, v.campos@activewindowproducts.com
```

Both are also followers (`message_partner_ids`) of the AWP partner record (children 26937 + 26938).

## Child contacts

- **Jaime Gutierrez** (id 26937) — Sales / Order Contact — `j.gutierrez@activewindowproducts.com`
  - Direct ordering contact. Replies within 20-30 min during business hours.
  - Format DJ uses: Part No / Qty / Est. Price table.
- **Valerie Campos** (id 26938) — Customer Service Manager — `v.campos@activewindowproducts.com` · (323) 245-5185
  - Sends price-increase letters, holiday schedules.
  - Send detailed-invoice requests to her — Jaime's accounting team only sends totals.

## Order template (DJ's historical format)

Subject: `Order Request - <description>`

```
Please process the following order:

Part No    Qty    Est. Price
1017AL     100    $1.017
1213M      40     $0.21

Total: ~$110.10

Thank you,
Dan
```

Then Jaime adds it to the next delivery (Friday delivery is the standard cycle).

## Products imported (2026-04-29)

33 frame products were created with vendor pricing (`product.supplierinfo` linked to AWP):

| SKU pattern | Product | Mill price | Color price | Finishes |
|---|---|---|---|---|
| AWP-1017{X} | 5/16" Aluminum Screen Frame .020 | $0.855/ft | $1.017/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1010{X} | 5/16" Aluminum Lip Frame .025 | $1.344/ft | $1.650/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1025{X} | 1"×5/16" Aluminum Screen Frame .025 | — | $1.510/ft | AD/AL/BL/W/Z |
| AWP-1019{X} | 3/8" Aluminum Slider Frame .025 | $1.104/ft | $1.280/ft | AD/AL/BL/G/M/T/W/Z |
| AWP-1005{X} | 3/8" Aluminum Slider Frame .020 | $0.852/ft | $0.987/ft | G/M/W/Z |

UOM = ft (id 20). Bundle/carton sizes + matching corner SKU + spline size in each product description.

**Not yet imported:** corners (1213M, 1210M, 1225M, etc.), splines, screen cloth, hardware, full screen-door catalog (Sec 11). Add when needed.

## Sample existing PO

- **P00002** — 100 ft of AWP-1017AL (5/16" Almond) @ $1.017/ft = $101.70 — draft state, awaiting confirmation
- View: https://window-solar-care.odoo.com/odoo/purchase/1

## When building the voice PO tool

Follow the rule above:
1. Search vendor by name → AWP partner 26936
2. Search products by part code → AWP-{sku}
3. Apply Resale fiscal position automatically (it's already set on partner — POs inherit it on create)
4. Default email recipients = both Jaime + Valerie (parent email already comma-separated)
5. Generate email body in the Order Request format above
6. Show DJ a preview before sending — voice misrecognition on quantities is expensive

## Related memory

- `reference_supplier_pricing.md` — paths to AWP price-list PDFs in Documents folder
- `feedback_proactive_inefficiency_capture.md` — preview-first pattern for ordering tools
- `project_quote_tool.md` — companion (customer quotes vs. supplier POs)
