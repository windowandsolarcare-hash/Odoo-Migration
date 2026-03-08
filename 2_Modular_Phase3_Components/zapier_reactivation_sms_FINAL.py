"""
ZAPIER REACTIVATION SMS - FINAL
================================
Odoo Reactivation → Workiz Graveyard Job → SMS Delivery

Author: DJ Sanders
Generated: 2026-03-06
Updated: 2026-03-06 (Applied Phase 3/4 refinements)

Consolidates 20 Zapier steps into one Python script.
Uses refined patterns from Phase 3/4 (error handling, helpers, logging).

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
# ODOO API HELPERS (Following Phase 3/4 Pattern)
# ==============================================================================

def _odoo_search_read(model, domain, fields, limit=1):
    """Helper: search_read and return result list (Phase 3/4 pattern)"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    model, "search_read",
                    [domain],
                    {"fields": fields, "limit": limit}
                ]
            }
        }
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        return response.json().get("result", [])
    except Exception as e:
        print(f"[ERROR] _odoo_search_read failed for {model}: {e}")
        return []

def _odoo_write(model, record_ids, values):
    """Helper: write to Odoo records (Phase 3/4 pattern)"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    model, "write",
                    [record_ids, values]
                ]
            }
        }
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        return response.json().get("result")
    except Exception as e:
        print(f"[ERROR] _odoo_write failed for {model}: {e}")
        return None

def _odoo_create(model, values):
    """Helper: create Odoo record (Phase 3/4 pattern)"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    model, "create",
                    [values]
                ]
            }
        }
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        return response.json().get("result")
    except Exception as e:
        print(f"[ERROR] _odoo_create failed for {model}: {e}")
        return None

# ==============================================================================
# STEP 2-3: GET OPPORTUNITY & CHATTER MESSAGE
# ==============================================================================

def get_opportunity_details(opportunity_id):
    """Get Opportunity details from Odoo (Phase 3/4 pattern)"""
    
    print(f"[*] Fetching Opportunity {opportunity_id} from Odoo...")
    
    try:
        opp_id = int(opportunity_id)
    except (ValueError, TypeError):
        print(f"[ERROR] Invalid opportunity_id: {opportunity_id}")
        return None
    
    result = _odoo_search_read(
        "crm.lead",
        [["id", "=", opp_id]],
        [
            "name", "contact_name", "phone", "email_from", "email_normalized",
            "city", "country_id", "company_id", "state_id", "description",
            "x_historical_workiz_uuid", "x_primary_service", "x_odoo_contact_id",
            "x_price_list_text", "campaign_id"
        ],
        limit=1
    )
    
    if not result or len(result) == 0:
        print(f"[ERROR] Opportunity {opp_id} not found in Odoo")
        return None
    
    print(f"[*] Found Opportunity: {result[0].get('name', 'N/A')}")
    return result[0]

def get_chatter_message(opportunity_id):
    """Get most recent SMS message from Opportunity chatter (Phase 3/4 pattern)"""
    
    print(f"[*] Fetching chatter message for Opportunity {opportunity_id}...")
    
    try:
        opp_id = int(opportunity_id)
    except (ValueError, TypeError):
        print(f"[WARNING] Invalid opportunity_id for chatter: {opportunity_id}")
        return ""
    
    result = _odoo_search_read(
        "mail.message",
        [
            ["model", "=", "crm.lead"],
            ["res_id", "=", opp_id],
            ["body", "ilike", "%855-245-2273%"]
        ],
        ["body"],
        limit=1
    )
    
    if not result or len(result) == 0:
        print("[WARNING] No chatter message found")
        return ""
    
    # Clean HTML tags
    html_body = result[0].get("body", "")
    if not html_body:
        return ""
    
    clean_text = re.sub(r'<[^>]+>', '', html_body)
    print(f"[*] Chatter message retrieved ({len(clean_text)} chars)")
    return clean_text

# ==============================================================================
# STEP 4-9: TEXT FORMATTING & EXTRACTION
# ==============================================================================

def clean_sms_for_json(text):
    """Replace newlines with escaped newlines for JSON (Phase 3/4 pattern)"""
    if not text:
        return ""
    return str(text).replace("\n", "\\n")

def extract_source_order_number(source_order_text):
    """Extract source order number from description text (Phase 3/4 pattern)"""
    
    if not source_order_text or not isinstance(source_order_text, str):
        return ""
    
    try:
        # Split by "Source Order: "
        if "Source Order:" in source_order_text:
            after_split = source_order_text.split("Source Order:")[-1]
            # Get first line
            order_number = after_split.split("\n")[0].strip()
            return order_number
    except Exception as e:
        print(f"[ERROR] extract_source_order_number failed: {e}")
    
    return ""

def extract_source_order_id(source_order_text):
    """Extract source order ID from description text (Phase 3/4 pattern)"""
    
    if not source_order_text or not isinstance(source_order_text, str):
        return ""
    
    try:
        # Split by "Source Order ID: "
        if "Source Order ID:" in source_order_text:
            after_split = source_order_text.split("Source Order ID:")[-1]
            # Get first line
            order_id = after_split.split("\n")[0].strip()
            return order_id
    except Exception as e:
        print(f"[ERROR] extract_source_order_id failed: {e}")
    
    return ""

def extract_campaign_info(campaign_field):
    """Extract campaign ID and name from Odoo campaign field (Phase 3/4 pattern)"""
    
    # campaign_field format: [1, "2026 Reactivation Campaign"]
    try:
        if isinstance(campaign_field, list) and len(campaign_field) >= 2:
            return {
                "id": campaign_field[0],
                "name": campaign_field[1]
            }
    except Exception as e:
        print(f"[ERROR] extract_campaign_info failed: {e}")
    
    return {"id": "", "name": ""}

# ==============================================================================
# STEP 10-12: WORKIZ JOB CREATION & SMS TRIGGER
# ==============================================================================

def get_historical_workiz_job(uuid):
    """Get historical job details from Workiz (Phase 3/4 pattern)"""
    
    if not uuid:
        print("[ERROR] No UUID provided for historical job")
        return None
    
    print(f"[*] Fetching historical Workiz job: {uuid}")
    
    url = f"{WORKIZ_BASE_URL}/job/get/{uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data and len(data) > 0:
                job = data[0]
                print(f"[*] Historical job found: {job.get('FirstName', '')} {job.get('LastName', '')}")
                return job
            else:
                print(f"[ERROR] Historical job {uuid} returned empty data")
                return None
        else:
            print(f"[ERROR] Historical job {uuid} API error: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout fetching historical job {uuid}")
        return None
    except Exception as e:
        print(f"[ERROR] Exception fetching historical job: {e}")
        return None

def create_graveyard_job(historical_job, sms_message):
    """Create graveyard job in Workiz for SMS delivery (Phase 3/4 pattern)"""
    
    if not historical_job:
        print("[ERROR] No historical job data provided")
        return None
    
    print("[*] Creating graveyard job in Workiz...")
    
    # Extract ClientId and strip CL- prefix if present (Phase 3/4 pattern)
    client_id_raw = historical_job.get("ClientId")
    client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
    
    if not client_id:
        print("[ERROR] No ClientId in historical job")
        return None
    
    job_data = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": client_id,
        "JobDateTime": "",  # Empty per original Zap (no scheduled date for reactivation lead)
        "FirstName": historical_job.get("FirstName", ""),
        "LastName": historical_job.get("LastName", ""),
        "Address": historical_job.get("Address", ""),
        "City": historical_job.get("City", ""),
        "State": historical_job.get("State", ""),
        "PostalCode": historical_job.get("PostalCode", ""),
        "JobType": "Reactivation Lead",
        "Unit": historical_job.get("Unit", ""),
        "ServiceArea": historical_job.get("ServiceArea", ""),
        "JobSource": historical_job.get("JobSource", "Reactivation"),
        "information_to_remember": sms_message or "",
        "JobNotes": historical_job.get("JobNotes", ""),
        "Phone": historical_job.get("Phone", "")
    }
    
    url = f"{WORKIZ_BASE_URL}/job/create/"
    
    try:
        response = requests.post(url, json=job_data, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"[*] Graveyard job created (HTTP {response.status_code})")
            
            # For HTTP 200, response contains UUID
            if response.status_code == 200:
                result = response.json()
                
                # Handle both list and dict responses from Workiz
                if isinstance(result, list):
                    # If it's a list, take the first item
                    if len(result) > 0 and isinstance(result[0], dict):
                        uuid = result[0].get('UUID')
                    else:
                        uuid = None
                elif isinstance(result, dict):
                    # If it's a dict, navigate to data.UUID
                    uuid = result.get('data', {}).get('UUID') or result.get('UUID')
                else:
                    uuid = None
                
                if uuid:
                    print(f"[*] Graveyard UUID: {uuid}")
                    return uuid
                else:
                    print("[WARNING] No UUID in response, fetching latest...")
                    return fetch_latest_graveyard_job()
            
            # For HTTP 204, need to fetch latest job
            print("[*] HTTP 204 response, fetching latest job...")
            return fetch_latest_graveyard_job()
        else:
            print(f"[ERROR] Failed to create graveyard job: HTTP {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout creating graveyard job")
        return None
    except Exception as e:
        print(f"[ERROR] Exception creating graveyard job: {e}")
        return None

def fetch_latest_graveyard_job():
    """Fetch most recent graveyard job UUID (Phase 3/4 pattern)"""
    
    print("[*] Fetching latest graveyard job from Workiz...")
    
    url = f"{WORKIZ_BASE_URL}/job/all/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json().get('data', [])
            if jobs and len(jobs) > 0:
                uuid = jobs[0].get('UUID')
                print(f"[*] Latest job UUID: {uuid}")
                return uuid
            else:
                print("[ERROR] No jobs found in Workiz")
                return None
        else:
            print(f"[ERROR] Failed to fetch jobs: HTTP {response.status_code}")
            return None
        
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout fetching latest job")
        return None
    except Exception as e:
        print(f"[ERROR] Exception fetching latest job: {e}")
        return None

def trigger_workiz_sms(graveyard_uuid):
    """Update job status to trigger Workiz SMS automation (Phase 3/4 pattern)"""
    
    if not graveyard_uuid:
        print("[ERROR] No graveyard_uuid provided for SMS trigger")
        return False
    
    print(f"[*] Triggering SMS for graveyard job: {graveyard_uuid}")
    
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
            print("[*] SMS triggered via Workiz automation")
            return True
        else:
            print(f"[ERROR] Failed to trigger SMS: HTTP {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout triggering SMS")
        return False
    except Exception as e:
        print(f"[ERROR] Exception triggering SMS: {e}")
        return False

# ==============================================================================
# STEP 13-20: ODOO LOGGING & UPDATES
# ==============================================================================

def log_activity_to_odoo(contact_id, opportunity_id, source_order_num, source_order_id, 
                         description, campaign_name, current_date):
    """Create CRM activity log record in Odoo (reliable parent write pattern)"""
    
    if not contact_id:
        print("[WARNING] No contact_id, skipping activity log")
        return None
    
    print(f"[*] Logging activity to Contact {contact_id}...")
    
    try:
        order_id_int = int(source_order_id) if source_order_id else False
    except (ValueError, TypeError):
        order_id_int = False
    
    # Activity log data (will be nested in parent write)
    activity_data = {
        "x_related_order_id": order_id_int,
        "x_activity_type": "reactivation_sent",
        "x_description": description or "",
        "x_name": f"Reactivation sent for Order {source_order_num}" if source_order_num else "Reactivation sent",
        "x_date": current_date,
        "x_campaign": campaign_name or ""
    }
    
    # RELIABLE PATTERN: Write to parent Contact using magic command [0, 0, {...}]
    # This creates the related record and establishes the relationship correctly
    contact_update = {
        "x_crm_activity_log_ids": [[0, 0, activity_data]]
    }
    
    result = _odoo_write("res.partner", [int(contact_id)], contact_update)
    
    if result:
        print(f"[*] Activity log created on Contact {contact_id}")
        return True
    else:
        print("[ERROR] Failed to log activity")
        return None

def update_contact_reactivation_date(contact_id, current_date, price_list):
    """Update contact's last reactivation sent date and price list (Phase 3/4 pattern)"""
    
    if not contact_id:
        print("[WARNING] No contact_id, skipping contact update")
        return False
    
    print(f"[*] Updating Contact {contact_id} reactivation date...")
    
    try:
        cid = int(contact_id)
    except (ValueError, TypeError):
        print(f"[ERROR] Invalid contact_id: {contact_id}")
        return False
    
    values = {
        "x_studio_last_reactivation_sent": current_date,
        "x_studio_prices_per_service": price_list or ""
    }
    
    result = _odoo_write("res.partner", [cid], values)
    
    if result:
        print("[*] Contact updated with reactivation date")
        return True
    else:
        print("[ERROR] Failed to update contact")
        return False

def update_opportunity_with_graveyard(opportunity_id, graveyard_uuid):
    """Link graveyard job back to Opportunity (Phase 3/4 pattern)"""
    
    if not graveyard_uuid:
        print("[WARNING] No graveyard_uuid, skipping opportunity update")
        return False
    
    print(f"[*] Linking graveyard job {graveyard_uuid} to Opportunity {opportunity_id}...")
    
    try:
        opp_id = int(opportunity_id)
    except (ValueError, TypeError):
        print(f"[ERROR] Invalid opportunity_id: {opportunity_id}")
        return False
    
    graveyard_link = f"https://app.workiz.com/jobs/view/{graveyard_uuid}"
    
    values = {
        "x_workiz_graveyard_uuid": graveyard_uuid,
        "x_workiz_graveyard_link": graveyard_link
    }
    
    result = _odoo_write("crm.lead", [opp_id], values)
    
    if result:
        print("[*] Opportunity linked to graveyard job")
        return True
    else:
        print("[ERROR] Failed to update opportunity")
        return False

# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main(input_data):
    """
    Main function for Zapier execution (Phase 3/4 pattern).
    
    INPUT (from webhook):
        opportunity_id: Odoo CRM lead ID
    
    OUTPUT:
        success: Boolean
        graveyard_uuid: Workiz job UUID
        message: Status message
    """
    
    print("=" * 60)
    print("REACTIVATION SMS WORKFLOW - PHASE 3/4 REFINED")
    print("=" * 60)
    
    # VALIDATE INPUT (Phase 3/4 pattern)
    if not isinstance(input_data, dict):
        print(f"[ERROR] input_data is not a dict: {type(input_data)}")
        return {
            "success": False,
            "message": "Error: Invalid input_data format"
        }
    
    # Extract input
    opportunity_id = input_data.get('opportunity_id')
    
    if not opportunity_id:
        print("[ERROR] No opportunity_id in webhook payload")
        print(f"[DEBUG] Available keys: {list(input_data.keys())}")
        return {
            "success": False,
            "message": "Error: opportunity_id required"
        }
    
    print(f"[*] Processing Opportunity ID: {opportunity_id}")
    
    # STEP 2: Get Opportunity details
    opportunity = get_opportunity_details(opportunity_id)
    if not opportunity:
        return {
            "success": False,
            "message": f"Error: Opportunity {opportunity_id} not found in Odoo"
        }
    
    contact_id = opportunity.get('x_odoo_contact_id')
    historical_uuid = opportunity.get('x_historical_workiz_uuid')
    description = opportunity.get('description', '')
    price_list = opportunity.get('x_price_list_text', '')
    
    # Source order info is in the description field (from Odoo script)
    source_order_text = description
    campaign = extract_campaign_info(opportunity.get('campaign_id'))
    
    print(f"[*] Contact ID: {contact_id}")
    print(f"[*] Historical Workiz UUID: {historical_uuid}")
    print(f"[*] Campaign: {campaign.get('name', 'N/A')}")
    
    # STEP 3-5: Get and clean SMS message from chatter
    sms_message = get_chatter_message(opportunity_id)
    if not sms_message:
        print("[WARNING] No SMS message found in chatter, using description")
        sms_message = description or "Reactivation SMS sent"
    
    sms_clean = clean_sms_for_json(sms_message)
    
    # STEP 6-9: Extract source order info
    source_order_num = extract_source_order_number(source_order_text)
    source_order_id = extract_source_order_id(source_order_text)
    
    print(f"[*] Source Order: {source_order_num} (ID: {source_order_id})")
    
    # STEP 10: Get historical Workiz job
    if not historical_uuid:
        print("[ERROR] No historical Workiz UUID on opportunity")
        return {
            "success": False,
            "message": "Error: No historical Workiz UUID on opportunity - cannot create graveyard job"
        }
    
    historical_job = get_historical_workiz_job(historical_uuid)
    if not historical_job:
        return {
            "success": False,
            "message": f"Error: Historical job {historical_uuid} not found in Workiz"
        }
    
    # STEP 11: Create graveyard job in Workiz
    graveyard_uuid = create_graveyard_job(historical_job, sms_message)
    if not graveyard_uuid:
        return {
            "success": False,
            "message": "Error: Failed to create graveyard job in Workiz"
        }
    
    print(f"[*] Graveyard job created: {graveyard_uuid}")
    
    # STEP 12: Trigger SMS by updating status
    sms_triggered = trigger_workiz_sms(graveyard_uuid)
    if not sms_triggered:
        print("[WARNING] SMS trigger failed, but graveyard job exists - may need manual trigger")
    
    # STEP 13: Get current date (Pacific time, Phase 3/4 pattern)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # STEP 14-18: JSON escape description and price list
    description_clean = clean_sms_for_json(description) if description else ""
    price_list_clean = clean_sms_for_json(price_list) if price_list else ""
    
    # STEP 17: Log activity (only if contact_id exists)
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
    else:
        print("[WARNING] No contact_id, activity log skipped")
    
    # STEP 19: Update contact reactivation date (only if contact_id exists)
    if contact_id:
        update_contact_reactivation_date(contact_id, current_date, price_list_clean)
    else:
        print("[WARNING] No contact_id, contact update skipped")
    
    # STEP 20: Link graveyard job to Opportunity
    update_opportunity_with_graveyard(opportunity_id, graveyard_uuid)
    
    print("=" * 60)
    print("✅ REACTIVATION SMS WORKFLOW COMPLETE")
    print(f"✅ Graveyard Job: {graveyard_uuid}")
    print(f"✅ Link: https://app.workiz.com/jobs/view/{graveyard_uuid}")
    print("=" * 60)
    
    return {
        "success": True,
        "graveyard_uuid": graveyard_uuid,
        "graveyard_link": f"https://app.workiz.com/jobs/view/{graveyard_uuid}",
        "opportunity_id": opportunity_id,
        "message": f"Reactivation SMS sent via graveyard job {graveyard_uuid}"
    }

# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

# NOTE: This script is designed to be executed via exec() in Zapier.
# The Zapier code should explicitly call main(input_data) and return the result.
# Do NOT auto-execute here - let Zapier control execution.
