"""
==============================================================================
ZAPIER PHASE 3 - PART 1 of 2
==============================================================================
Imports, Credentials, and Phases 3A-3D
Paste this FIRST, then paste PART 2 immediately below it.
==============================================================================
"""

import requests
from datetime import datetime
import pytz

# ==============================================================================
# CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "1hu6lroiy5zxomcpptuwsg8heju97iwg_bW12bDN0MjhseDlwaHA5aGsxM2JuZjFzcQ"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# ==============================================================================
# PHASE 3A: CONTACT LOOKUP
# ==============================================================================

def search_contact_by_address(street_address):
    """Find Odoo contact by exact street address match."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "search_read",
                [[["street", "=", street_address]]],
                {"fields": ["id", "name", "street", "city"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            contact = result["result"][0]
            print(f"[OK] Contact found: {contact['name']} (ID: {contact['id']})")
            return contact
        else:
            print(f"[ERROR] No contact found for address: {street_address}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception in contact lookup: {e}")
        return None

# ==============================================================================
# PHASE 3B: OPPORTUNITY LOOKUP
# ==============================================================================

def find_opportunity_with_workiz_uuid(contact_id):
    """Find opportunity linked to contact with Workiz UUID populated."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "crm.lead",
                "search_read",
                [[
                    ["partner_id", "=", contact_id],
                    ["x_workiz_graveyard_uuid", "!=", False]
                ]],
                {"fields": ["id", "name", "x_workiz_graveyard_uuid"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            opp = result["result"][0]
            print(f"[OK] Opportunity found: {opp['name']} (ID: {opp['id']})")
            print(f"   Graveyard UUID: {opp['x_workiz_graveyard_uuid']}")
            return {'success': True, 'opportunity': opp}
        else:
            return {'success': False, 'message': 'No opportunity with Workiz UUID found'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ==============================================================================
# PHASE 3C: WORKIZ JOB UPDATE
# ==============================================================================

def update_workiz_job(job_uuid, booking_time_utc, job_type, job_notes=""):
    """Update Workiz job with new date/time, status, job type, and notes."""
    
    # Convert UTC to Pacific time
    utc = pytz.UTC
    pacific = pytz.timezone('America/Los_Angeles')
    
    dt_utc = datetime.fromisoformat(booking_time_utc.replace('Z', '+00:00'))
    dt_pacific = dt_utc.astimezone(pacific)
    pacific_datetime = dt_pacific.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[*] Time conversion:")
    print(f"   UTC:     {booking_time_utc}")
    print(f"   Pacific: {pacific_datetime}")
    
    # Update Workiz job
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "JobDateTime": pacific_datetime,
        "JobType": job_type,
        "Status": "Pending",
        "SubStatus": "Send Confirmation - Text"
    }
    
    # Add JobNotes if provided
    if job_notes:
        payload["JobNotes"] = job_notes
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Workiz job updated successfully!")
            return {'success': True}
        else:
            return {'success': False, 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ==============================================================================
# PHASE 3D: MARK OPPORTUNITY WON
# ==============================================================================

def mark_opportunity_won(opportunity_id):
    """Mark Odoo opportunity as Won."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "crm.lead",
                "action_set_won",
                [[opportunity_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not None:
            print(f"[OK] Opportunity {opportunity_id} marked as Won!")
            return {'success': True}
        else:
            return {'success': False, 'message': 'action_set_won failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
