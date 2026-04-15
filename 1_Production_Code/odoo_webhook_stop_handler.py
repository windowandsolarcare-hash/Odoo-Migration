# ==============================================================================
# WORKIZ STOP REQUEST WEBHOOK HANDLER - ODOO STUDIO WEBHOOK
# Author: DJ Sanders
# Date: 2026-03-19
# GitHub: windowandsolarcare-hash/Odoo-Migration
# ==============================================================================
# PURPOSE:
# Receives Workiz webhook when job SubStatus = "STOP - Do not Call or Text".
# 1. Finds Contact by Workiz location ID or phone
# 2. Adds phone to phone.blacklist
# 3. Sets x_studio_activelead = "Do Not Contact"
# 4. Posts chatter note
# 5. Logs to CRM Activity History
# 6. Marks any open CRM opportunity as Lost
#
# PAYLOAD FORMAT (Workiz sends):
# {"data": {"uuid": "B6GB1D", "clientInfo": {"serialId": 1040, "primaryPhone": "8058131909"}}}
# ==============================================================================

# payload is already a dict in Odoo 19, but check anyway
if isinstance(payload, str):
    payload = json.loads(payload)

data = payload.get('data', payload)
client_info = data.get('clientInfo', data)

workiz_job_id = data.get('uuid') or data.get('UUID') or payload.get('JobId', 'N/A')
workiz_client_id = client_info.get('serialId') or data.get('ClientId') or payload.get('ClientId')
customer_phone = client_info.get('primaryPhone') or data.get('Phone') or payload.get('Phone', '')

sub_status = data.get('subStatus', {})
sub_status_name = sub_status.get('name', '') if isinstance(sub_status, dict) else str(sub_status)
job_status = data.get('status') or data.get('Status') or payload.get('Status', '')
status_info = (job_status + ' / ' + sub_status_name) if sub_status_name else job_status

# Normalize phone to digits and E.164
phone_digits = ''.join(filter(str.isdigit, customer_phone))
if len(phone_digits) == 10:
    phone_e164 = '+1' + phone_digits
elif len(phone_digits) == 11 and phone_digits[0] == '1':
    phone_e164 = '+' + phone_digits
else:
    phone_e164 = customer_phone

# Find contact: location ID first, then phone fallback
contact = None
if workiz_client_id:
    found = env['res.partner'].search([('x_studio_x_studio_location_id', '=', str(workiz_client_id))], limit=1)
    if found:
        contact = found[0]
if not contact and phone_digits:
    found = env['res.partner'].search(['|', ('phone', 'ilike', phone_digits[-10:]), ('phone', '=', customer_phone)], limit=1)
    if found:
        contact = found[0]

if contact:
    # 1. Add phone to blacklist
    if phone_e164:
        existing_bl = env['phone.blacklist'].sudo().search([('number', '=', phone_e164)], limit=1)
        if not existing_bl:
            env['phone.blacklist'].sudo().create({'number': phone_e164})

    # 2. Set "Do Not Contact"
    contact.write({'x_studio_activelead': 'Do Not Contact'})

    # 3. Post to chatter
    contact.sudo().message_post(body='[STOP] Opted out. Job: ' + str(workiz_job_id) + ' | Blacklisted: ' + str(phone_e164))

    # 4. Log CRM activity
    contact.write({'x_crm_activity_log_ids': [[0, 0, {
        'x_name': 'SMS Opt-Out - Job ' + str(workiz_job_id),
        'x_description': 'Customer replied STOP. Phone ' + str(phone_e164) + ' blacklisted. Status: ' + str(status_info),
        'x_contact_id': contact.id,
        'x_campaign_id': 1
    }]]})

    # 5. Mark any open CRM opportunity as Lost
    open_opps = env['crm.lead'].search([
        '|',
        ('partner_id', '=', contact.id),
        ('x_odoo_contact_id', '=', contact.id),
        ('active', '=', True),
        ('type', '=', 'opportunity'),
    ])
    if open_opps:
        for opp in open_opps:
            opp.message_post(body='[STOP] Customer replied STOP to SMS. Opportunity marked Lost automatically.')
        open_opps.write({'stage_id': 6})
        open_opps.action_set_lost()
        contact.sudo().message_post(body='[STOP] ' + str(len(open_opps)) + ' opportunity/ies marked Lost. IDs: ' + str(open_opps.ids))
    else:
        contact.sudo().message_post(body='[STOP] No open opportunities found to mark Lost (contact.id=' + str(contact.id) + ')')
