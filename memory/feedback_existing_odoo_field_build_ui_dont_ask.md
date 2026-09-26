---
name: feedback_existing_odoo_field_build_ui_dont_ask
description: "Customer-detail field work: if the field ALREADY EXISTS in Odoo, just build it into the app UI — don't hold/ask DJ. Only hold on DJ when a NEW Odoo field (schema change) is required."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 90c41229-811c-4085-801e-7475f63f81b9
  modified: 2026-09-26T07:02:07.186Z
---

DJ (2026-09-26): For customer-detail (and job-detail) fields — **the rule for whether to ask him:**

- **Field already EXISTS in Odoo** (it's in Odoo's own UI for add/edit/delete): **just build it into the app UI. Do NOT hold on DJ.** Surfacing existing-field UI work as a "decision" is a needless hold — the answer is obvious, the plumbing is already there.
- **Field does NOT exist in Odoo yet** (a NEW custom field / schema change is required): **THEN hold on DJ** — creating a new Odoo field is his call.

Sparked by the gate-code build: gate (`x_studio_x_gate_code`) already existed in Odoo, so exposing it as an editable input in the Customer Brain detail editor should have just been built, not flagged/parked as a gap.

**Why:** DJ wants forward progress. Every Odoo field DJ can edit must have a Render/app pathway ([[feedback_never_send_dj_to_odoo]]) — so if the field is already in Odoo, wiring it into the app UI is expected work, not a question. The only thing that genuinely needs his sign-off is adding NEW schema (a new custom field), because that's a data-model decision.

**How to apply:** Before pausing to ask DJ about a customer/job-detail field, check whether the field already exists in Odoo (fields_get / the field-names table). Exists → build it into the app UI and ship. Doesn't exist → ask DJ before creating it. Ties to [[feedback_raise_bar_on_dj_alerts]] / [[feedback_escalate_to_dj_sparingly]] (decide-and-proceed; escalate only real DJ-only decisions).
