---
name: project_service_area_field_twin
description: "Service Area lives in res.partner x_studio_service_area (values Hemet / Desert / All areas) — NOT the empty twin x_studio_x_studio_service_area that CLAUDE.md's table wrongly lists."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ce92b3e-6626-4807-9e45-23722f7fcba2
---

There are TWO near-identical Service Area fields on res.partner:
- **`x_studio_service_area`** (char) = the REAL one. Values: **'Hemet', 'Desert', 'All areas'**. Filled on 712 of 897 properties (Hemet 259 / Desert 358 on properties). This is the field to use.
- `x_studio_x_studio_service_area` (char) = empty twin, blank on all 897 properties. CLAUDE.md's ODOO CUSTOM FIELD NAMES table WRONGLY lists this one as "Service Area" — that doc entry is wrong; corrected 2026-06-11.

The two service areas are **Hemet** and **Desert** (plus 'All areas'); DJ's whole book is essentially one or the other. The value lives on the PROPERTY record (not the Contact — contact's is blank), so read it from the representative property.

Bug it caused (fixed 2026-06-11): the Customer Analytics service-area doughnut read the empty twin, so EVERY customer (incl. Nick Conway / 76201 Vía Mariposa, who is 'Desert') showed as "Unknown". Fixed by switching analytics.py (fields fetch + `_count_by` + ltv 'area') to `x_studio_service_area`. After fix: Desert 283 / Hemet 196 / All areas 67 / Unknown 39. See [[project_customer_analytics_datamodel]].

When wiring any service-area logic anywhere (analytics, field app, reactivation, reports), use `x_studio_service_area`. The frequency/type twins are fine: frequency=`x_studio_x_frequency`, type=`x_studio_x_type_of_service`.
