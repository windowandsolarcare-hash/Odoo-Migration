"""
ZAPIER REACTIVATION SMS - FINAL
================================
Odoo Reactivation → Workiz Graveyard Job → SMS Delivery

Author: DJ Sanders
Generated: 2026-03-05

Consolidates 20 Zapier steps into one Python script.

TRIGGER: Webhooks by Zapier - Catch Hook
INPUT: opportunity_id (from Odoo Server Action webhook)

WORKFLOW:
1. Get Opportunity details from Odoo
2. Get SMS message from Opportunity chatter
3. Get historical Workiz job data
4. Create "graveyard" job in Workiz (for SMS delivery)
5. Update job status to trigger Workiz SMS automation
6. Log activity in Odoo
7. Update contact reactivation date
8. Link graveyard job back to Opportunity

OUTPUT: success, graveyard_uuid, message
"""

import requests
import json
from datetime import datetime
import re

# ==============================================================================
# CONFIGURATION & CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# ==============================================================================
# ODOO API HELPER
# ==============================================================================

def odoo_call(model, method, domain_or_ids, fields=None, limit=None, context=None):
    """Generic Odoo JSON-RPC call"""
    
    args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, domain_or_ids]
    
    if fields or limit or context:
        params = {}
        if fields:
            params['fields'] = fields
        if limit:
            params['limit'] = limit
        if context:
            params['context'] = context
        args.append(params)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": args
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=30)
        result = response.json()
        return result.get("result")
    except Exception as e:
        print(f"[ERROR] Odoo API call failed: {e}")
        return None

# ==============================================================================
# STEP 2-3: GET OPPORTUNITY & CHATTER MESSAGE
# ==============================================================================

def get_opportunity_details(opportunity_id):
    """Get Opportunity details from Odoo"""
    
    print(f"Fetching Opportunity {opportunity_id} from Odoo...")
    
    result = odoo_call(
        "crm.lead",
        "search_read",
        [[["id", "=", int(opportunity_id)]]],
        fields=[
            "name", "contact_name", "phone", "email_from", "email_normalized",
            "city", "country_id", "company_id", "state_id", "description",
            "x_historical_workiz_uuid", "x_primary_service", "x_odoo_contact_id",
            "campaign_id", "x_studio_source_order", "x_studio_prices_per_service"
        ],
        limit=1
    )
    
    if not result or len(result) == 0:
        print(f"[ERROR] Opportunity {opportunity_id} not found")
        return None
    
    return result[0]

def get_chatter_message(opportunity_id):
    """Get most recent SMS message from Opportunity chatter"""
    
    print(f"Fetching chatter message for Opportunity {opportunity_id}...")
    
    result = odoo_call(
        "mail.message",
        "search_read",
        [[
            ["model", "=", "crm.lead"],
            ["res_id", "=", int(opportunity_id)],
            ["body", "ilike", "%855-245-2273%"]
        ]],
        fields=["body"],
        limit=1
    )
    
    if not result or len(result) == 0:
        print("[WARNING] No chatter message found")
        return ""
    
    # Clean HTML tags
    html_body = result[0].get("body", "")
    clean_text = re.sub(r'<[^>]+>', '', html_body)
    return clean_text

# ==============================================================================
# STEP 4-9: TEXT FORMATTING & EXTRACTION
# ==============================================================================

def clean_sms_for_json(text):
    """Replace newlines with escaped newlines for JSON"""
    return text.replace("\n", "\\n")

def extract_source_order_number(source_order_text):
    """Extract source order number from description text"""
    
    if not source_order_text:
        return ""
    
    # Split by "Source Order: "
    if "Source Order:" in source_order_text:
        after_split = source_order_text.split("Source Order:")[-1]
        # Get first line
        order_number = after_split.split("\n")[0].strip()
        return order_number
    
    return ""

def extract_source_order_id(source_order_text):
    """Extract source order ID from description text"""
    
    if not source_order_text:
        return ""
    
    # Split by "Source Order ID: "
    if "Source Order ID:" in source_order_text:
        after_split = source_order_text.split("Source Order ID:")[-1]
        # Get first line
        order_id = after_split.split("\n")[0].strip()
        return order_id
    
    return ""

def extract_campaign_info(campaign_field):
    """Extract campaign ID and name from Odoo campaign field"""
    
    # campaign_field format: [1, "2026 Reactivation Campaign"]
    if isinstance(campaign_field, list) and len(campaign_field) == 2:
        return {
            "id": campaign_field[0],
            "name": campaign_field[1]
        }
    
    return {"id": "", "name": ""}

# ==============================================================================
# STEP 10-12: WORKIZ JOB CREATION & SMS TRIGGER
# ==============================================================================

def get_historical_workiz_job(uuid):
    """Get historical job details from Workiz"""
    
    print(f"Fetching historical Workiz job: {uuid}")
    
    url = f"{WORKIZ_BASE_URL}/job/get/{uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                return data[0]
        
        print(f"[WARNING] Historical job {uuid} not found")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to get historical job: {e}")
        return None

def create_graveyard_job(historical_job, sms_message):
    """Create graveyard job in Workiz for SMS delivery"""
    
    print("Creating graveyard job in Workiz...")
    
    job_data = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": historical_job.get("ClientId"),
        "JobDateTime": "",  # Empty per original Zap
        "FirstName": historical_job.get("FirstName"),
        "LastName": historical_job.get("LastName"),
        "Address": historical_job.get("Address"),
        "City": historical_job.get("City"),
        "State": historical_job.get("State"),
        "PostalCode": historical_job.get("PostalCode"),
        "JobType": "Reactivation Lead",
        "Unit": historical_job.get("Unit", ""),
        "ServiceArea": historical_job.get("ServiceArea", ""),
        "JobSource": historical_job.get("JobSource", "Reactivation"),
        "information_to_remember": sms_message,
        "JobNotes": historical_job.get("JobNotes", ""),
        "Phone": historical_job.get("Phone")
    }
    
    url = f"{WORKIZ_BASE_URL}/job/create/"
    
    try:
        response = requests.post(url, json=job_data, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"✅ Graveyard job created (HTTP {response.status_code})")
            
            # For HTTP 200, response contains UUID
            if response.status_code == 200:
                result = response.json()
                return result.get('data', {}).get('UUID')
            
            # For HTTP 204, need to fetch latest job
            return fetch_latest_graveyard_job()
        else:
            print(f"[ERROR] Failed to create graveyard job: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"[ERROR] Exception creating graveyard job: {e}")
        return None

def fetch_latest_graveyard_job():
    """Fetch most recent graveyard job UUID"""
    
    url = f"{WORKIZ_BASE_URL}/job/all/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json().get('data', [])
            if jobs:
                # Return most recent job UUID
                return jobs[0].get('UUID')
        
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch latest job: {e}")
        return None

def trigger_workiz_sms(graveyard_uuid):
    """Update job status to trigger Workiz SMS automation"""
    
    print(f"Triggering SMS for graveyard job: {graveyard_uuid}")
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": graveyard_uuid,
        "Status": "Pending",
        "SubStatus": "API SMS Test Trigger"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ SMS triggered via Workiz automation")
            return True
        else:
            print(f"[ERROR] Failed to trigger SMS: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception triggering SMS: {e}")
        return False

# ==============================================================================
# STEP 13-20: ODOO LOGGING & UPDATES
# ==============================================================================

def log_activity_to_odoo(contact_id, opportunity_id, source_order_num, source_order_id, 
                         description, campaign_name, current_date):
    """Create CRM activity log record in Odoo"""
    
    print(f"Logging activity to Contact {contact_id}...")
    
    activity_data = {
        "x_odoo_contact_id": contact_id,
        "x_related_order_id": int(source_order_id) if source_order_id else False,
        "x_activity_type": "reactivation_sent",
        "x_description": description,
        "x_name": f"Reactivation sent for Order {source_order_num}",
        "x_date": current_date,
        "x_campaign": campaign_name
    }
    
    result = odoo_call(
        "x_crm_activity_log",
        "create",
        [activity_data]
    )
    
    if result:
        print(f"✅ Activity logged: {result}")
        return result
    else:
        print("[ERROR] Failed to log activity")
        return None

def update_contact_reactivation_date(contact_id, current_date, price_list):
    """Update contact's last reactivation sent date and price list"""
    
    print(f"Updating Contact {contact_id} reactivation date...")
    
    result = odoo_call(
        "res.partner",
        "write",
        [[int(contact_id)], {
            "x_studio_last_reactivation_sent": current_date,
            "x_studio_prices_per_service": price_list
        }]
    )
    
    if result:
        print("✅ Contact updated")
        return True
    else:
        print("[ERROR] Failed to update contact")
        return False

def update_opportunity_with_graveyard(opportunity_id, graveyard_uuid):
    """Link graveyard job back to Opportunity"""
    
    print(f"Linking graveyard job {graveyard_uuid} to Opportunity {opportunity_id}...")
    
    graveyard_link = f"https://app.workiz.com/jobs/view/{graveyard_uuid}"
    
    result = odoo_call(
        "crm.lead",
        "write",
        [[int(opportunity_id)], {
            "x_workiz_graveyard_uuid": graveyard_uuid,
            "x_workiz_graveyard_link": graveyard_link
        }]
    )
    
    if result:
        print("✅ Opportunity linked to graveyard job")
        return True
    else:
        print("[ERROR] Failed to update opportunity")
        return False

# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main(input_data):
    """
    Main function for Zapier execution.
    
    INPUT (from webhook):
        opportunity_id: Odoo CRM lead ID
    
    OUTPUT:
        success: Boolean
        graveyard_uuid: Workiz job UUID
        message: Status message
    """
    
    print("=" * 60)
    print("REACTIVATION SMS WORKFLOW")
    print("=" * 60)
    
    # Extract input
    opportunity_id = input_data.get('opportunity_id')
    
    if not opportunity_id:
        return {
            "success": False,
            "message": "Error: opportunity_id required"
        }
    
    print(f"Processing Opportunity ID: {opportunity_id}")
    
    # STEP 2: Get Opportunity details
    opportunity = get_opportunity_details(opportunity_id)
    if not opportunity:
        return {
            "success": False,
            "message": f"Error: Opportunity {opportunity_id} not found"
        }
    
    contact_id = opportunity.get('x_odoo_contact_id')
    historical_uuid = opportunity.get('x_historical_workiz_uuid')
    source_order_text = opportunity.get('x_studio_source_order', '')
    description = opportunity.get('description', '')
    price_list = opportunity.get('x_studio_prices_per_service', '')
    campaign = extract_campaign_info(opportunity.get('campaign_id'))
    
    print(f"Contact ID: {contact_id}")
    print(f"Historical UUID: {historical_uuid}")
    
    # STEP 3-5: Get and clean SMS message from chatter
    sms_message = get_chatter_message(opportunity_id)
    if not sms_message:
        print("[WARNING] No SMS message found in chatter, using description")
        sms_message = description
    
    sms_clean = clean_sms_for_json(sms_message)
    
    # STEP 6-9: Extract source order info
    source_order_num = extract_source_order_number(source_order_text)
    source_order_id = extract_source_order_id(source_order_text)
    
    print(f"Source Order: {source_order_num} (ID: {source_order_id})")
    
    # STEP 10: Get historical Workiz job
    if not historical_uuid:
        print("[ERROR] No historical Workiz UUID found")
        return {
            "success": False,
            "message": "Error: No historical Workiz UUID on opportunity"
        }
    
    historical_job = get_historical_workiz_job(historical_uuid)
    if not historical_job:
        return {
            "success": False,
            "message": f"Error: Historical job {historical_uuid} not found"
        }
    
    # STEP 11: Create graveyard job in Workiz
    graveyard_uuid = create_graveyard_job(historical_job, sms_message)
    if not graveyard_uuid:
        return {
            "success": False,
            "message": "Error: Failed to create graveyard job"
        }
    
    print(f"Graveyard job created: {graveyard_uuid}")
    
    # STEP 12: Trigger SMS by updating status
    sms_triggered = trigger_workiz_sms(graveyard_uuid)
    if not sms_triggered:
        print("[WARNING] SMS trigger failed, but graveyard job exists")
    
    # STEP 13: Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # STEP 14-18: JSON escape description and price list (handled by clean_sms_for_json)
    description_clean = clean_sms_for_json(description)
    price_list_clean = clean_sms_for_json(price_list)
    
    # STEP 17: Log activity
    if contact_id:
        log_activity_to_odoo(
            contact_id,
            opportunity_id,
            source_order_num,
            source_order_id,
            description_clean,
            campaign.get("name", ""),
            current_date
        )
    
    # STEP 19: Update contact reactivation date
    if contact_id:
        update_contact_reactivation_date(contact_id, current_date, price_list_clean)
    
    # STEP 20: Link graveyard job to Opportunity
    update_opportunity_with_graveyard(opportunity_id, graveyard_uuid)
    
    print("=" * 60)
    print("✅ REACTIVATION SMS WORKFLOW COMPLETE")
    print("=" * 60)
    
    return {
        "success": True,
        "graveyard_uuid": graveyard_uuid,
        "graveyard_link": f"https://app.workiz.com/jobs/view/{graveyard_uuid}",
        "message": f"Reactivation SMS sent via graveyard job {graveyard_uuid}"
    }

# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

# Zapier will pass input_data from webhook
# Example: input_data = {"opportunity_id": "43"}
output = main(input_data)
