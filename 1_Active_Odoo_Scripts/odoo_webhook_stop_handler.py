"""
WORKIZ STOP REQUEST WEBHOOK HANDLER - ODOO STUDIO WEBHOOK
Author: DJ Sanders
Date: 2026-03-08
GitHub: windowandsolarcare-hash/Odoo-Migration

PURPOSE:
Odoo Studio webhook that receives Workiz job status change webhooks.
When a job status is set to "STOP - do not CALL or TEXT", this webhook:
1. Extracts customer phone from the Workiz payload
2. Finds the Contact in Odoo by phone or Workiz client ID
3. Sets is_blacklisted = True (marketing blacklist)
4. Logs the opt-out activity to their CRM Activity History

ODOO STUDIO SETUP:
1. Studio → Webhooks → New
2. Name: "Workiz STOP Request Handler"
3. Enable "Log Calls" for debugging
4. Target Record: Contact (res.partner)
5. Paste this code in "Target Record code" section
6. Copy the generated webhook URL
7. Configure in Workiz Settings → Webhooks → "Job Status Changed"
   - URL: [Paste Odoo webhook URL]
   - Filter: Status = "STOP - do not CALL or TEXT"

EXPECTED WORKIZ PAYLOAD:
{
  "JobId": "ABC123",
  "UUID": "MJUERK",
  "ClientId": 12345,
  "Status": "STOP - do not CALL or TEXT",
  "FirstName": "John",
  "LastName": "Doe",
  "Phone": "555-123-4567",
  "Email": "john@example.com"
}

NOTE: This code runs in Odoo's safe_eval environment:
- No imports allowed (use built-in env objects)
- Available: env, requests, datetime, json
"""

# Parse webhook payload
payload = json.loads(payload)  # Odoo provides 'payload' variable

# Extract data from Workiz webhook
workiz_job_id = payload.get('JobId', payload.get('UUID', 'N/A'))
workiz_client_id = payload.get('ClientId')
customer_phone = payload.get('Phone', '')
customer_name = f"{payload.get('FirstName', '')} {payload.get('LastName', '')}".strip()
job_status = payload.get('Status', '')

# Log webhook received
env.user.message_post(body=f"[WEBHOOK] Received STOP request - Job: {workiz_job_id}, Customer: {customer_name}, Phone: {customer_phone}")

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
            activity_vals = {
                'x_name': f"SMS Opt-Out Request",
                'x_activity_type': 'opt_out',
                'x_description': f"Customer replied STOP to SMS. Manually marked in Workiz job {workiz_job_id}. Blacklisted from future campaigns.",
                'x_contact_id': contact.id,
                'x_campaign_id': 1
            }
            
            env['x_crm_activity_log'].create(activity_vals)
            
            env.user.message_post(body=f"[SUCCESS] Contact {contact.name} (ID: {contact.id}) blacklisted successfully. Future reactivation campaigns will skip this contact.")
        
        result = contact

# Return the contact record (Odoo Studio webhook expects this)
result = result if 'result' in locals() else None
