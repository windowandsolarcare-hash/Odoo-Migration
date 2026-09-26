---
name: project_gate_snapshot_gap
description: "The field/job screen reads the SO gate SNAPSHOT, not the property master — editing the master alone left jobs stale (Bruce/Galen gap). Fixed 2026-09-26: gate editable in Customer Brain + edits mirror to the SO snapshot."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-26T07:00:31.705Z
---

**Two gate fields, and the job screen reads the SNAPSHOT — not the master.** (Per the CLAUDE.md field table: `res.partner.x_studio_x_gate_code` = property master; `sale.order.x_studio_x_gate_snapshot` = snapshot "at time of job".) The field/job screen renders the SNAPSHOT (dashboard.py:583/686), so updating ONLY the property master leaves the job showing a stale/blank gate. This was the recurring "gate gap" DJ hit on **Bruce and Galen** (Galen SO 17677: gate 1254 on the property, snapshot blank — Operator hand-wrote the snapshot as a one-off).

**Fixed 2026-09-26 (brain.py df94c705, DJ-directed via Operator), two parts:**
1. **Gate is now editable in the Customer Brain detail editor.** brain.py `brain_job` (GET) Property section: `_fld('Gate', gate, 'cust_gate', True, 'text')` (was display-only). The detail editor is data-driven — field.html:2978 reads `[data-key]` → `changes[key]`, and `_fld(label, value, odoo_key, editable=True, ftype)` renders an input with `data-key=odoo_key`. On save, `changes['cust_gate']` → the existing `_CUST_PROP` map (brain.py ~217) writes the property's `x_studio_x_gate_code`. No static edit needed. **This is how to make ANY property/customer field editable in that editor:** give its `_fld` a `cust_*` key + `editable=True`; the `cust_*` key must exist in `_CUST_PROP`/`_CUST_BOTH`/`_CUST_PERSON` in `brain_job_save`. (`cust_pricing`/`cust_frequency`/`cust_type_of_service`/`cust_service_area` are already in `_CUST_PROP` but still display-only — one line each to enable if DJ asks; do NOT do unasked.)
2. **Snapshot sync on save.** In `brain_job_save`, right after the `cust_prop` property write, if `x_studio_x_gate_code` was edited, ALSO write THIS SO's `x_studio_x_gate_snapshot = new gate`. Only this SO updates; PAST SOs keep their historical snapshot ("at time of job"). Same pattern as the existing move-property snapshot write (brain.py:360). This closes the gap permanently — no more hand-writing snapshots.

**Why it matters / how to apply:** any time a "master" field is edited but a screen reads a per-SO SNAPSHOT of it, the edit must ALSO update the relevant snapshot(s) or the screen goes stale. Gate is the canonical case. See [[feedback_assistant_use_app_workflow_not_raw_api]] (Operator's one-off hand-write is exactly what a proper build removes).
