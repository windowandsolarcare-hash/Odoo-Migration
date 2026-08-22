---
name: project_x_odoo_contact_id_is_integer
description: "crm.lead x_odoo_contact_id is an INTEGER field (bare partner id), NOT a many2one — never subscript it [0]. Caused reactivation/book 'int not subscriptable' crash."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-13T14:25:54.315Z
---

**`crm.lead.x_odoo_contact_id` is an Odoo INTEGER field** (verified 2026-08-13 via ir.model.fields: `ttype="integer"`, `relation=false`). It stores the linked res.partner id as a **bare int** (e.g. `23263`), NOT a many2one `[id, name]` pair.

**Why this matters:** the usual Odoo m2o extraction idiom `(rec.get('field') or [None])[0]` — which is correct for real many2one fields — **crashes** on an integer field, because `(23263 or [None])[0]` becomes `23263[0]` → `TypeError: 'int' object is not subscriptable`.

**Bug it caused:** `POST /owner/api/reactivation/book` (routers/owner/reactivation.py) crashed with "'int' object is not subscriptable" whenever DJ tried to Book a reactivation "Sent" lead (e.g. Michael Krauss, lead 423, x_odoo_contact_id=23263). The book modal is in `v2_reactivation.html` (surfaced from New Order → existing customer, or the Reactivation Sent tab). Line was:
`contact_id = (_lr[0].get('x_odoo_contact_id') or [None])[0] if _lr else None`
Fixed 2026-08-13 to: `contact_id = (_lr[0].get('x_odoo_contact_id') or None) if _lr else None`.

**How to apply:** when reading `x_odoo_contact_id`, use the value directly (`rec.get('x_odoo_contact_id') or None`). A value of 0/False means no linked contact. Do NOT `[0]` it. Only one occurrence existed in the repo (confirmed by grep); if you add new readers, follow this. The CLAUDE.md field table lists it as "Linked res.partner ID" without noting the type — this integer-vs-m2o ambiguity is exactly what caused the crash. Related: the two Book handlers are `api_reactivation_book` (uses lead → x_odoo_contact_id) and `api_reengagement_book` (uses partner_id from body, no lead lookup).
