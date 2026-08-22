---
name: project_gate_pricing_snapshot_model
description: "DJ's gate-code/pricing snapshot model: SO snapshot = what it was the day of THAT job (editable, DJ enters new value); property master = most-current (read-only, meant to auto-roll-up from the snapshot ON INVOICE). ⚠ the roll-up-on-invoice is NOT wired yet."
metadata:
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-04T12:41:48.018Z
---

**DJ's model (2026-08-04), for gate code AND pricing:**
- **SO-level SNAPSHOT** (`sale.order.x_studio_x_gate_snapshot`, `sale.order.x_studio_x_studio_pricing_snapshot`) = "whatever the gate code / pricing was the day I did THAT job." **EDITABLE** — when the customer texts a new gate code, DJ enters it here for this visit. Gate codes change often; pricing less often.
- **PROPERTY MASTER** (`res.partner.x_studio_x_gate_code`, `res.partner.x_studio_x_pricing`) = "the most current one." **READ-ONLY** in the UI (don't let DJ hand-edit it). Intended to be kept current by an **auto roll-up: when the job INVOICES, the SO snapshot rolls UP to the property master, overriding the old value.**
- New jobs seed the OTHER direction: `new_job.py` L512-520 copies property master → SO snapshot at creation (so a fresh job's snapshot == the current property value "until I change it"). Verified.

**✅ ROLL-UP BUILT 2026-08-04 (trigger = marked DONE, DJ's choice):** `api_set_block_status` (dashboard.py, the mark-Done endpoint) now, when `done=true`, copies the SO snapshots UP to the property master — `res.partner.x_studio_x_gate_code = SO.x_studio_x_gate_snapshot` and `x_studio_x_pricing = SO.x_studio_x_studio_pricing_snapshot` (property = `SO.partner_shipping_id`), only for non-blank snapshots. Verified: property gate OLD111 + SO snapshot NEW999 → mark Done → property gate = NEW999. (Note: set_block_status refuses Workiz-linked SOs, so roll-up is Odoo-native jobs only — fine post-Workiz.)

**(historical) the roll-up did NOT exist before 2026-08-04.** Grepped the repo: writes to `x_studio_x_gate_code`/`x_studio_x_pricing` happen only at job CREATION (new_job.py form input; dashboard.py ~1838 reactivation booking from Workiz data) — nothing copies the SO snapshot up to the property when a job invoices/Done/pays. So the read-only "on file" property field will NOT auto-update yet. **TODO if DJ wants: on invoice (or Done/paid), write `res.partner.x_studio_x_gate_code = SO.x_studio_x_gate_snapshot` (and pricing) for the property.** Hook candidates: the payment/invoice path (`_execute_payment` / stripe success in dashboard.py) or `set_block_status` (Done). Confirm the trigger with DJ (invoice vs Done vs paid).

**so_full editor UI (dashboard.py, done 2026-08-04):** "Gate code · on file (current)" + "Pricing · on file (current)" = READ-ONLY (property master, no key). "Gate code · this job" (`x_studio_x_gate_snapshot`) + "Pricing · this job" (`x_studio_x_studio_pricing_snapshot`) = EDITABLE snapshots. **Pricing section (final 2026-08-04):** the read-only "Total" row was REMOVED (dup of the line-editor's own live Total above the Send-invoice button). **Amount due** = `amount_total` (Odoo, computed from lines) − payments (posted-invoice residuals); 0 when paid in full. **Paid?** is now COMPUTED read-only (NOT the old written `x_studio_is_paid`, which was never populated historically): "Paid ✓" when a payment exists AND amount due==0, "Partial — $X paid", else "Not paid". See [[project_so_full_start_time_edit]], CLAUDE.md field table.
