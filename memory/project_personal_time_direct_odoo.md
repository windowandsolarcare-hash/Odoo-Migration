---
name: project_personal_time_direct_odoo
description: How to create "Personal Time" calendar blocks directly in Odoo (no Workiz) so they land on the field schedule. Partner 24177, job_type "Personal Time", direct state=sale write.
metadata:
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Personal Time blocks — create directly in Odoo, skip Workiz (verified 2026-06-08)

DJ uses "Personal Time" jobs to block calendar time (dentist, doctor, errands). They are NOT billable, so there's no reason to route them through Workiz (which he's dropping). Creating them directly in Odoo lands them on the field schedule identically to the Workiz-synced ones.

## Recipe (verified working — SO 17308/S00122 appeared on the 2026-06-09 schedule)
- `sale.order` create with:
  - `partner_id = 24177` and `partner_shipping_id = 24177` — the **"Personal Time, 8401 Maruyama Drive"** partner (NOT partner 23054, the bare "Personal Time" Contact, which has zero SOs).
  - `x_studio_x_studio_x_studio_job_type = "Personal Time"`
  - `x_studio_x_studio_workiz_status = "Scheduled"` (mirrors existing)
  - `company_id = 1`
  - `date_order` = the block's START time in **UTC** (PT is UTC-7 in summer/PDT; e.g. 8 AM PT = `15:00:00` UTC). date_order = start time always.
  - optional description as an order line: `order_line=[(0,0,{"display_type":"line_note","name":"<reminder text>"})]`
- Then **set state directly**: `write([soid], {"state":"sale"})`. Schedule gate = `state in ['sale','done']` + `date_order` on that day.

## GOTCHAS
- **`action_confirm` is BROKEN on this Odoo 19 SaaS instance** for these orders — throws `TypeError: unhashable type: 'list'` deep in the enterprise `sale_external_tax` addon (`_get_and_set_external_taxes_on_eligible_records`). Workaround: **don't call action_confirm; write `state='sale'` directly.** The schedule only needs state+date_order. (May affect other direct $0/personal SO creates too.)
- **Direct Odoo creates get a `S00###` name** (Odoo's native sale.order sequence), NOT the `004###` 6-digit format. The `004###` numbers are assigned by the **Workiz sync code (Phase 3)**, not Odoo. Cosmetic only. [[project_odoo_so_name_format]]
- **Description does NOT show on the schedule LIST** — a `line_note` line leaves `service_label` empty (same as the Workiz Personal Time blocks, which store no description in Odoo at all). To make the reminder visible on the row, it must go where the field assistant reads the subtitle (service_label / job_type), not a note line. TBD if DJ wants this.
- **`call()` helper signature** (local accounting scripts): pass ids and vals as SEPARATE positional args — `call("sale.order","write",[soid],{vals})`, NOT `call(...,[[soid],{vals}])`. Fields as kwarg: `call(...,"read",[ids],fields=[...])`. Mind that `create([vals])` returns a **list** `[id]`, not a bare int. [[feedback_odoo_rpc_write_pattern]]
