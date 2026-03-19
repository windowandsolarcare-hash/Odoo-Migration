# ==============================================================================
# WORKIZ STOP REQUEST WEBHOOK HANDLER - ODOO STUDIO WEBHOOK
# Author: DJ Sanders
# Date: 2026-03-08
# GitHub: windowandsolarcare-hash/Odoo-Migration
# ==============================================================================
# PURPOSE:
# Odoo Studio webhook that receives Workiz job status change webhooks.
# When a job status is set to "STOP - do not CALL or TEXT", this webhook:
# 1. Extracts customer phone from the Workiz payload
# 2. Finds the Contact in Odoo by phone or Workiz client ID
# 3. Sets is_blacklisted = True (marketing blacklist)
# 4. Logs the opt-out activity to their CRM Activity History
#
# EXPECTED WORKIZ PAYLOAD (NEW FORMAT):
# {
#   "trigger": {"type": "job_status_stop_-_do_not_call_or_text"},
#   "data": {
#     "uuid": "B6GB1D",
#     "clientInfo": {
#       "serialId": 1040,
#       "firstName": "Jean",
#       "lastName": "Faenza",
#       "primaryPhone": "8058131909"
#     }
#   }
# }
#
# ALSO SUPPORTS OLD FLAT FORMAT (backward compatible)
# ==============================================================================

# Parse webhook payload
payload = json.loads(payload)  # Odoo provides 'payload' variable

# Extract data from Workiz webhook (supports both old and new formats)
data = payload.get('data', payload)  # New format has nested 'data', old format is flat
client_info = data.get('clientInfo', data)  # New format has nested 'clientInfo', old format is flat

# Extract job details (try new format first, fallback to old)
workiz_job_id = data.get('uuid') or data.get('UUID') or payload.get('JobId', 'N/A')

# Extract client/contact info (try new nested format first, fallback to old flat format)
workiz_client_id = client_info.get('serialId') or data.get('ClientId') or payload.get('ClientId')
customer_phone = client_info.get('primaryPhone') or data.get('Phone') or payload.get('Phone', '')
first_name = client_info.get('firstName') or data.get('FirstName') or payload.get('FirstName', '')
last_name = client_info.get('lastName') or data.get('LastName') or payload.get('LastName', '')
customer_name = f"{first_name} {last_name}".strip()

# Status (can be in multiple places)
job_status = data.get('status') or data.get('Status') or payload.get('Status', '')
sub_status = data.get('subStatus', {})
if isinstance(sub_status, dict):
    sub_status_name = sub_status.get('name', '')
else:
    sub_status_name = str(sub_status)

# Log webhook received
env.user.message_post(body=f"[WEBHOOK] Received STOP request - Job: {workiz_job_id}, Customer: {customer_name}, Phone: {customer_phone}, Status: {job_status}, SubStatus: {sub_status_name}, ClientId: {workiz_client_id}")

# Normalize phone number (remove formatting)
phone_clean = ''.join(filter(str.isdigit, customer_phone))

if not phone_clean and not workiz_client_id:
    env.user.message_post(body="[ERROR] No phone or ClientId in webhook payload")
    result = None
else:
    # Search for Contact by phone or Workiz Location ID
    domain = []
    
    if workiz_client_id:
        # First try Workiz Location ID (most reliable)
        domain = [('x_studio_x_studio_location_id', '=', str(workiz_client_id))]
        contacts = env['res.partner'].search(domain, limit=1)
        
        if not contacts and phone_clean:
            # Fallback to phone search
            domain = [
                '|', '|',
                ('phone', 'ilike', phone_clean[-10:]),
                ('mobile', 'ilike', phone_clean[-10:]),
                ('phone', '=', customer_phone)
            ]
            contacts = env['res.partner'].search(domain, limit=1)
    elif phone_clean:
        # Only phone available
        domain = [
            '|', '|',
            ('phone', 'ilike', phone_clean[-10:]),
            ('mobile', 'ilike', phone_clean[-10:]),
            ('phone', '=', customer_phone)
        ]
        contacts = env['res.partner'].search(domain, limit=1)
    else:
        contacts = None
    
    if not contacts:
        env.user.message_post(body=f"[ERROR] Contact not found - Phone: {customer_phone}, ClientId: {workiz_client_id}")
        result = None
    else:
        contact = contacts[0]
        
        # Check if already blacklisted
        if contact.is_blacklisted:
            env.user.message_post(body=f"[INFO] Contact {contact.name} (ID: {contact.id}) was already blacklisted")
        else:
            # Set is_blacklisted = True
            contact.write({'is_blacklisted': True})
            
            # Log the opt-out activity
            status_info = f"{job_status} / {sub_status_name}" if sub_status_name else job_status
            activity_vals = {
                'x_name': f"SMS Opt-Out Request - Job {workiz_job_id}",
                'x_description': f"Customer replied STOP to SMS. Manually marked in Workiz job {workiz_job_id} (Status: {status_info}). Blacklisted from future campaigns.",
                'x_contact_id': contact.id,
                'x_campaign_id': 1
            }
            
            contact.write({
                "x_crm_activity_log_ids": [[0, 0, activity_vals]]
            })
            
            env.user.message_post(body=f"[SUCCESS] Contact {contact.name} (ID: {contact.id}) blacklisted successfully. Future reactivation campaigns will skip this contact.")
        
        result = contact

# Return the contact record (Odoo Studio webhook expects this)
result = result if 'result' in locals() else None
