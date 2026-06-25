# Odoo Automated Action — "Close re-engagement + reactivation on SO confirm"
# ============================================================================
# LIVE in Odoo as base.automation id=9, server action id=1364.
# This file is the GitHub source-of-truth copy (CLAUDE.md rule #2 two-step deploy).
# Odoo runs the code stored in the server action, NOT this file — if you edit the
# logic, update BOTH this file AND ir.actions.server id 1364 (and/or base.automation 9).
#
# TRIGGER:  base.automation on sale.order, trigger='on_state_set',
#           trg_selection_field_id=2123  (state -> 'sale', i.e. ORDER CONFIRMED).
#           Fires only on CONFIRM, never on draft — which is the gate: re-engagement /
#           reactivation trigger jobs land in Odoo as DRAFTS and never confirm, so they
#           can't self-close. A real booking (DJ sets date/tech/line items -> confirm) fires it.
#
# WHAT IT DOES: when a customer's job is confirmed, close that customer's open loose ends so
# they're never double-contacted:
#   - open re-engagement project.task (name 'Re-engagement:', state 01_in_progress) -> 1_done
#   - open reactivation crm.lead (name ilike 'Reactivation Campaign', stage not Won/Lost) -> stage 4 (Won)
# Posts a reconcile note on the SO chatter. W&SC only (company_id == 1).
#
# Verified 2026-06-25 with throwaway data: draft did NOT fire; confirm closed both task+lead.
# Server-action rules followed: no imports, no docstrings, uses env/records/record.

for record in records:
    if record.state != 'sale':
        continue
    if record.company_id and record.company_id.id != 1:
        continue
    partner = record.partner_id
    if not partner:
        continue
    cust = partner.commercial_partner_id or partner
    pids = [cust.id]
    for ch in cust.child_ids:
        pids.append(ch.id)
    notes = []
    tasks = env['project.task'].search([('partner_id', 'in', pids), ('name', 'like', 'Re-engagement:'), ('state', '=', '01_in_progress')])
    if tasks:
        tasks.write({'state': '1_done'})
        notes.append(str(len(tasks)) + ' re-engagement task(s) closed')
    leads = env['crm.lead'].search([('partner_id', 'in', pids), ('name', 'ilike', 'Reactivation Campaign'), ('stage_id', 'not in', [4, 6])])
    if leads:
        leads.write({'stage_id': 4})
        notes.append(str(len(leads)) + ' reactivation lead(s) -> Won')
    if notes:
        record.message_post(body='Booking reconcile (on confirm): ' + '; '.join(notes))
