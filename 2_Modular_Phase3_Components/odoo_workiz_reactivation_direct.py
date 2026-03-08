"""
ODOO → WORKIZ DIRECT API INTEGRATION (NO ZAPIER)
==================================================
This script runs INSIDE Odoo Server Action via exec()
Fetched from GitHub and executed directly in Odoo context

Author: DJ Sanders
Created: 2026-03-08

PURPOSE:
- Create graveyard job in Workiz
- Update status to trigger SMS
- Link back to Odoo Opportunity
- Log activity to Contact

EXECUTION:
Called via exec() from Odoo Server Action
Has access to: env, opportunity_id, contact_id, workiz_uuid, message_body, etc.
"""

# ==============================================================================
# CONFIGURATION
# ==============================================================================

WORKIZ_BASE_URL = "https://api.workiz.com/api/v1"
WORKIZ_AUTH_SECRET = "sec_bca8dd70aeca1c1ebe0ecd38e15b8d68"

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "d2e5ccb0f5b3d96d062b41ebbb3d91a2bb8b7896"

# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

def get_workiz_job(uuid):
    """Fetch job details from Workiz"""
    url = f"{WORKIZ_BASE_URL}/job/get/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": uuid
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            return result
        return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch Workiz job: {e}")
        return None

def create_workiz_graveyard_job(historical_job, sms_message):
    """Create graveyard job in Workiz"""
    
    # Extract ClientId
    client_id_raw = historical_job.get("ClientId")
    client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
    
    if not client_id:
        print("[ERROR] No ClientId in historical job")
        return None
    
    job_data = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": client_id,
        # JobDateTime omitted = unscheduled
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
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle both list and dict responses
                if isinstance(result, list):
                    if len(result) > 0 and isinstance(result[0], dict):
                        uuid = result[0].get('UUID')
                    else:
                        uuid = None
                elif isinstance(result, dict):
                    uuid = result.get('data', {}).get('UUID') or result.get('UUID')
                else:
                    uuid = None
                
                if uuid:
                    print(f"[*] Graveyard UUID: {uuid}")
                    return uuid
        
        print(f"[ERROR] Failed to create graveyard job: HTTP {response.status_code}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception creating graveyard job: {e}")
        return None

def update_workiz_status(graveyard_uuid):
    """Update job status to trigger SMS"""
    
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
            print("[*] SMS triggered via Workiz status update")
            return True
        else:
            print(f"[ERROR] Failed to trigger SMS: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception triggering SMS: {e}")
        return False

# ==============================================================================
# MAIN EXECUTION (runs in Odoo context)
# ==============================================================================

def execute_reactivation(opportunity_id, historical_uuid, message_body, contact_id, source_order_num, source_order_id):
    """
    Main function called from Odoo Server Action
    
    Parameters passed from Odoo:
    - opportunity_id: CRM Opportunity ID
    - historical_uuid: Workiz UUID from historical job
    - message_body: SMS message text
    - contact_id: Odoo Contact ID
    - source_order_num: Source order number
    - source_order_id: Source order ID
    """
    
    print("=" * 60)
    print("REACTIVATION SMS WORKFLOW - DIRECT ODOO→WORKIZ")
    print("=" * 60)
    print(f"[*] Opportunity ID: {opportunity_id}")
    print(f"[*] Historical UUID: {historical_uuid}")
    print(f"[*] Contact ID: {contact_id}")
    
    # STEP 1: Get historical Workiz job
    print(f"[*] Fetching historical Workiz job: {historical_uuid}")
    historical_job = get_workiz_job(historical_uuid)
    
    if not historical_job:
        print("[ERROR] Failed to fetch historical job")
        return {"success": False, "message": "Historical job not found"}
    
    print(f"[*] Historical job found")
    
    # STEP 2: Create graveyard job
    print("[*] Creating graveyard job in Workiz...")
    graveyard_uuid = create_workiz_graveyard_job(historical_job, message_body)
    
    if not graveyard_uuid:
        print("[ERROR] Failed to create graveyard job")
        return {"success": False, "message": "Failed to create graveyard job"}
    
    print(f"[*] Graveyard job created: {graveyard_uuid}")
    
    # STEP 3: Update status to trigger SMS (immediate)
    print(f"[*] Triggering SMS for graveyard job: {graveyard_uuid}")
    sms_triggered = update_workiz_status(graveyard_uuid)
    
    if not sms_triggered:
        print("[WARNING] SMS trigger failed, but graveyard job exists")
    
    # STEP 5: Update Opportunity in Odoo with graveyard UUID/link
    print(f"[*] Linking graveyard job to Opportunity {opportunity_id}...")
    graveyard_link = f"https://app.workiz.com/jobs/view/{graveyard_uuid}"
    
    opportunity = env['crm.lead'].browse(int(opportunity_id))
    opportunity.write({
        'x_workiz_graveyard_uuid': graveyard_uuid,
        'x_workiz_graveyard_link': graveyard_link
    })
    print("[*] Opportunity updated with graveyard link")
    
    # STEP 6: Log activity to Contact
    if contact_id and source_order_id:
        print(f"[*] Logging activity to Contact {contact_id}...")
        
        contact = env['res.partner'].browse(int(contact_id))
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        activity_data = {
            "x_related_order_id": int(source_order_id),
            "x_activity_type": "reactivation_sent",
            "x_description": f"SMS sent via graveyard job {graveyard_uuid}",
            "x_name": f"Reactivation sent for Order {source_order_num}",
            "x_date": current_date,
            "x_campaign": "2026 Reactivation Campaign"
        }
        
        contact.write({
            "x_crm_activity_log_ids": [[0, 0, activity_data]]
        })
        print("[*] Activity logged to Contact")
    
    print("=" * 60)
    print("✅ REACTIVATION SMS WORKFLOW COMPLETE")
    print(f"✅ Graveyard Job: {graveyard_uuid}")
    print(f"✅ Link: {graveyard_link}")
    print("=" * 60)
    
    return {
        "success": True,
        "graveyard_uuid": graveyard_uuid,
        "graveyard_link": graveyard_link,
        "message": f"Reactivation SMS sent via graveyard job {graveyard_uuid}"
    }
