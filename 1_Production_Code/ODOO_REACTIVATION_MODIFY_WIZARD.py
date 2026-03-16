# ==============================================================================
# REACTIVATION SMS MODIFY WIZARD
# ==============================================================================
# This wizard allows manual editing of the reactivation SMS before sending
# 
# SETUP INSTRUCTIONS:
# 1. Create this as a Server Action in Odoo called "Launch (Modify Text)"
# 2. The action should be available on CRM Opportunity (crm.lead) records
# 3. This expects that PREVIEW has already run and populated x_draft_sms_message
#
# FIELDS REQUIRED ON CRM OPPORTUNITY (crm.lead):
# - x_draft_sms_message (Text) - Stores the composed SMS
# - x_draft_pricing_menu (Text) - Stores the pricing menu
# - x_studio_last_reactivation_sent (Date) - Already exists
# - x_odoo_contact_id (Many2one: res.partner)
# - x_historical_workiz_uuid (Char)
# ==============================================================================

import datetime
import requests
import json

# Configuration
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

now_utc = datetime.datetime.now()
now_pst = now_utc - datetime.timedelta(hours=8)
current_date_iso = now_pst.strftime('%Y-%m-%d')

# ==============================================================================
# STEP 1: CHECK IF SMS TEXT EXISTS
# ==============================================================================
# This assumes you're running this action on a CRM Opportunity record

for opportunity in records:
    # Read current draft SMS and pricing
    opp_vals = opportunity.read(['x_draft_sms_message', 'x_draft_pricing_menu', 'partner_id', 'x_odoo_contact_id', 'x_historical_workiz_uuid'])[0]
    
    draft_sms = opp_vals.get('x_draft_sms_message', '')
    draft_pricing = opp_vals.get('x_draft_pricing_menu', '')
    contact_id = opp_vals.get('x_odoo_contact_id')
    workiz_uuid = opp_vals.get('x_historical_workiz_uuid', 'NO_UUID_FOUND')
    
    if not draft_sms:
        opportunity.message_post(body="⚠️ No draft SMS found. Please run PREVIEW first.")
        break
    
    # ==============================================================================
    # STEP 2: SHOW EDIT FORM (MANUAL STEP)
    # ==============================================================================
    # In Odoo Studio, create a form view that shows:
    # - x_draft_sms_message (Text widget, editable)
    # - x_draft_pricing_menu (Text widget, editable)
    # - A button that triggers the SEND action below
    #
    # For now, this script assumes you've already edited the fields manually
    # and are now clicking the "Send Modified Message" button
    
    # ==============================================================================
    # STEP 3: SEND MODIFIED SMS
    # ==============================================================================
    
    opportunity.message_post(body="[DEBUG] Starting modified SMS send...")
    
    # Re-read the (potentially edited) SMS and pricing
    opp_vals_updated = opportunity.read(['x_draft_sms_message', 'x_draft_pricing_menu'])[0]
    final_sms = opp_vals_updated.get('x_draft_sms_message', '')
    final_pricing = opp_vals_updated.get('x_draft_pricing_menu', '')
    
    if not final_sms:
        opportunity.message_post(body="⚠️ SMS message is empty. Cannot send.")
        break
    
    # Get contact
    if contact_id:
        if isinstance(contact_id, list):
            contact = env['res.partner'].browse(contact_id[0])
        else:
            contact = env['res.partner'].browse(contact_id)
    else:
        contact = opportunity.partner_id
    
    if not contact:
        opportunity.message_post(body="⚠️ No contact found for this opportunity.")
        break
    
    # Get property (from original source order if available)
    # For this wizard, we'll try to get property from the opportunity's partner
    prop_record = None
    if opportunity.partner_shipping_id:
        prop_record = opportunity.partner_shipping_id
    else:
        # Search for a property linked to this contact
        properties = env['res.partner'].search([
            ('parent_id', '=', contact.id),
            ('x_studio_x_studio_record_category', '=', 'Property')
        ], limit=1)
        if properties:
            prop_record = properties[0]
    
    # ==============================================================================
    # STEP 4: UPDATE RECORDS
    # ==============================================================================
    
    # Update contact's last reactivation sent date
    contact.write({'x_studio_last_reactivation_sent': current_date_iso})
    opportunity.message_post(body=f"[DEBUG] Updated contact last reactivation date: {current_date_iso}")
    
    # Update property's pricing menu (if we found a property)
    if prop_record and final_pricing:
        prop_record.write({'x_studio_prices_per_service': final_pricing})
        opportunity.message_post(body=f"[DEBUG] Updated property pricing menu")
    
    # Post modified SMS to Opportunity chatter
    opportunity.message_post(body=f"""<p><strong>✏️ MODIFIED REACTIVATION SMS SENT</strong></p>
<p><strong>SMS Message:</strong></p>
<pre>{final_sms}</pre>
<p><strong>Pricing Menu:</strong></p>
<pre>{final_pricing}</pre>""")
    
    # Log activity to Contact
    activity_data = {
        "x_name": f"Modified Reactivation SMS sent for Opportunity {opportunity.name}",
        "x_activity_type": "reactivation_sms_modified",
        "x_description": final_sms,
        "x_related_order_id": opportunity.id
    }
    
    contact.write({
        "x_crm_activity_log_ids": [[0, 0, activity_data]]
    })
    
    opportunity.message_post(body=f"[DEBUG] Activity logged to Contact")
    
    # ==============================================================================
    # STEP 5: WORKIZ INTEGRATION
    # ==============================================================================
    
    try:
        opportunity.message_post(body=f"[DEBUG] Starting Workiz integration...")
        
        # Get historical Workiz job
        opportunity.message_post(body=f"[DEBUG] Fetching historical job: {workiz_uuid}")
        
        hist_url = f"{WORKIZ_BASE_URL}/job/get/{workiz_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
        hist_response = requests.get(hist_url, timeout=10)
        
        if hist_response.status_code != 200:
            opportunity.message_post(body=f"⚠️ Failed to fetch historical job (HTTP {hist_response.status_code})")
            break
        
        hist_result = hist_response.json()
        hist_data = hist_result.get('data', [])
        
        if hist_data and len(hist_data) > 0:
            historical_job = hist_data[0]
        else:
            opportunity.message_post(body=f"⚠️ Historical job returned empty data")
            break
        
        opportunity.message_post(body=f"[DEBUG] Historical job found")
        
        # Create graveyard job with MODIFIED SMS
        client_id_raw = historical_job.get("ClientId")
        client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
        
        if not client_id:
            opportunity.message_post(body="⚠️ No ClientId found")
            break
        
        graveyard_data = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "ClientId": client_id,
            "Status": "Pending",
            "SubStatus": "Texted - Awaiting Response",
            "JobType": "Reactivation Lead",
            "information_to_remember": final_sms,  # Use modified SMS
            "JobNotes": historical_job.get("JobNotes", ""),
            "Phone": historical_job.get("Phone", "")
        }
        
        opportunity.message_post(body=f"[DEBUG] Creating graveyard job with modified SMS...")
        
        create_response = requests.post(f"{WORKIZ_BASE_URL}/job/create/", json=graveyard_data, timeout=10)
        
        if create_response.status_code not in [200, 204]:
            opportunity.message_post(body=f"⚠️ Failed to create graveyard job (HTTP {create_response.status_code})")
            break
        
        # Extract UUID
        graveyard_uuid = None
        if create_response.status_code == 200:
            create_result = create_response.json()
            if isinstance(create_result, dict):
                data_list = create_result.get('data', [])
                if data_list and len(data_list) > 0:
                    graveyard_uuid = data_list[0].get('UUID')
            elif isinstance(create_result, list):
                if len(create_result) > 0:
                    graveyard_uuid = create_result[0].get('UUID')
        
        if not graveyard_uuid:
            opportunity.message_post(body="⚠️ Could not extract graveyard UUID from response")
            break
        
        opportunity.message_post(body=f"[DEBUG] Graveyard UUID: {graveyard_uuid}")
        
        # Trigger SMS
        status_payload = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "UUID": graveyard_uuid,
            "Status": "Pending",
            "SubStatus": "API SMS Test Trigger"
        }
        
        status_response = requests.post(f"{WORKIZ_BASE_URL}/job/update/", json=status_payload, timeout=10)
        
        if status_response.status_code == 200:
            opportunity.message_post(body=f"[DEBUG] SMS triggered successfully")
        else:
            opportunity.message_post(body=f"⚠️ SMS trigger failed (HTTP {status_response.status_code})")
        
        # Update Opportunity with graveyard link
        graveyard_link = f"https://app.workiz.com/jobs/view/{graveyard_uuid}"
        
        opportunity.write({
            'x_workiz_graveyard_uuid': graveyard_uuid,
            'x_workiz_graveyard_link': graveyard_link
        })
        
        opportunity.message_post(body=f"✅ MODIFIED SMS SENT: {graveyard_link}")
        
    except Exception as e:
        opportunity.message_post(body=f"⚠️ Workiz integration error: {e}")
    
    break
