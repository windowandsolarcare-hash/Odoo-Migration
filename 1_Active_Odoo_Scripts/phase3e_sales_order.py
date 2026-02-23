# ==============================================================================
# PHASE 3E: CREATE SALES ORDER
# ==============================================================================
# Purpose: Create Odoo sales order mirroring Workiz job after booking
# Created: 2026-02-05
# Status: Development - Ready for testing
# ==============================================================================

import requests
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

WORKIZ_API_BASE = "https://api.workiz.com/api/v1"
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"

def get_workiz_job_details(job_uuid):
    """
    Get job details from Workiz API by UUID.
    
    Args:
        job_uuid (str): Workiz job UUID
        
    Returns:
        dict: Job details including SerialId, or None if error
    """
    # Workiz GET endpoint: /job/get/{uuid}/ with auth in query params
    url = f"{WORKIZ_API_BASE}/{WORKIZ_API_TOKEN}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    print(f"🔍 Fetching Workiz job details for UUID: {job_uuid}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            response_json = response.json()
            
            # Workiz response structure: {'data': {...job details...}, 'flag': true, 'code': 200}
            job_data = response_json.get('data', {})
            
            # If data is an array, take first element
            if isinstance(job_data, list) and len(job_data) > 0:
                job_data = job_data[0]
            
            serial_id = job_data.get('SerialId', '')
            print(f"✅ Job found - SerialId: {serial_id}")
            
            return job_data
        else:
            print(f"❌ Workiz API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error fetching Workiz job: {e}")
        return None


def format_serial_id_for_odoo(serial_id):
    """
    Pad Workiz SerialId with leading zeros for Odoo sales order name.
    
    Args:
        serial_id (str or int): Workiz SerialId (e.g., "4111" or 4111)
        
    Returns:
        str: Padded serial ID (e.g., "004111")
    """
    serial_str = str(serial_id)
    padded = serial_str.zfill(6)  # Pad to 6 digits with leading zeros
    print(f"🔢 Serial ID formatted: {serial_id} → {padded}")
    return padded


# ==============================================================================
# PHASE 3E FUNCTION
# ==============================================================================

def get_property_for_contact(contact_id, service_address):
    """
    Find property record for the service address.
    
    Args:
        contact_id (int): Contact ID (parent)
        service_address (str): Service address
        
    Returns:
        int: Property ID or None
    """
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
                [[
                    ["street", "=", service_address],
                    ["x_studio_x_studio_record_category", "=", "Property"]
                ]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]["id"]
        return None
    except:
        return None


def create_sales_order(contact_id, property_id, workiz_job_data, booking_datetime, order_name=""):
    """
    Create Odoo sales order with full Workiz job details.
    
    Args:
        contact_id (int): Odoo contact ID (partner_id)
        property_id (int): Odoo property ID (partner_shipping_id)
        workiz_job_data (dict): Full Workiz job data from GET API
        booking_datetime (str): Booking date/time (YYYY-MM-DD HH:MM:SS UTC)
        order_name (str): Padded SerialId for order name
        
    Returns:
        dict: {'success': bool, 'sales_order_id': int, 'message': str}
        
    TESTED: 2026-02-05 - Includes all Workiz snapshot fields
    NOTES: 
    - SubStatus used for workiz_status (not Status)
    - Formats notes as: [Job Notes] {JobNotes}\n[Comment] {Comments}
    - Tags from Workiz (text field, not IDs)
    """
    
    # Extract data from Workiz job
    workiz_uuid = workiz_job_data.get('UUID', '')
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', 'Pending')
    tags = workiz_job_data.get('Tags', '')
    gate_code = workiz_job_data.get('gate_code', '')
    pricing = workiz_job_data.get('pricing', '')
    job_notes = workiz_job_data.get('JobNotes', '')
    comments = workiz_job_data.get('Comments', '')
    
    # Format notes: [Job Notes] {content}\n[Comment] {content}
    notes_snapshot = ""
    if job_notes:
        notes_snapshot += f"[Job Notes] {job_notes}"
    if comments:
        if notes_snapshot:
            notes_snapshot += "\n"
        notes_snapshot += f"[Comment] {comments}"
    
    # Build order data with all Workiz snapshots
    order_data = {
        "partner_id": contact_id,
        "partner_shipping_id": property_id,
        "date_order": booking_datetime,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,  # Use SubStatus not Status
        "x_studio_gate_snapshot": gate_code,
        "x_studio_x_studio_pricing_snapshot": pricing,
        "x_studio_x_studio_notes_snapshot1": notes_snapshot
    }
    
    # Add tags if present
    if tags:
        order_data["x_studio_tags"] = tags  # Assuming tags field exists
    
    # Add optional name if provided
    if order_name:
        order_data["name"] = order_name
    
    # NOTE: Dropdown fields (lead_source, job_type) to be added once Calendly options match Odoo
    
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
                "sale.order",
                "create",
                [order_data]
            ]
        }
    }
    
    print(f"\n📝 Creating sales order...")
    print(f"   Contact ID: {contact_id}")
    print(f"   Property ID: {property_id}")
    print(f"   Workiz UUID: {workiz_uuid}")
    print(f"   Booking Date: {booking_datetime}")
    print(f"   Workiz Status: {workiz_substatus}")
    print(f"   Order Name: {order_name if order_name else 'Auto-generated'}")
    print(f"   Gate Code: {gate_code if gate_code else 'None'}")
    print(f"   Pricing: {pricing if pricing else 'None'}")
    print(f"   Tags: {tags if tags else 'None'}")
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            sales_order_id = result["result"]
            print(f"✅ Sales order created: ID {sales_order_id}")
            return {
                'success': True,
                'sales_order_id': sales_order_id,
                'message': f"Sales order {sales_order_id} created successfully"
            }
        else:
            error = result.get("error", {})
            print(f"❌ Error creating sales order: {error}")
            return {
                'success': False,
                'sales_order_id': None,
                'message': f"Error: {error.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        print(f"❌ Exception creating sales order: {e}")
        return {
            'success': False,
            'sales_order_id': None,
            'message': f"Exception: {str(e)}"
        }


def process_phase3e(contact, opportunity, booking_info, won_result):
    """
    Phase 3E handler: Create sales order after opportunity is Won.
    
    Args:
        contact (dict): Contact record from Phase 3A
        opportunity (dict): Opportunity record from Phase 3B
        booking_info (dict): Booking data from Calendly
        won_result (dict): Result from Phase 3D
        
    Returns:
        dict: {
            'success': bool,
            'sales_order_id': int,
            'message': str
        }
    """
    
    print("\n" + "="*70)
    print("PHASE 3E: CREATE SALES ORDER")
    print("="*70)
    print(f"Contact ID: {contact['id']}")
    print(f"Contact Name: {contact['name']}")
    print(f"Service Address: {contact['street']}")
    print(f"Workiz UUID: {opportunity['x_workiz_graveyard_uuid']}")
    print("="*70 + "\n")
    
    # Validate opportunity was marked as Won
    if not won_result.get('success'):
        print("⚠️  Opportunity not marked as Won - not creating sales order")
        return {
            'success': False,
            'sales_order_id': None,
            'message': 'Skipped - Opportunity not marked as Won'
        }
    
    # Find property record
    print(f"🔍 Finding property record for: {contact['street']}")
    property_id = get_property_for_contact(contact['id'], contact['street'])
    
    if not property_id:
        print(f"⚠️  Property not found - using contact as shipping address")
        property_id = contact['id']
    else:
        print(f"✅ Property found: ID {property_id}")
    
    # For Odoo date_order: Use original UTC time (Odoo stores in UTC)
    # For Workiz: We already converted to Pacific in Phase 3C
    # Odoo expects: YYYY-MM-DD HH:MM:SS in UTC
    booking_datetime_utc = booking_info['booking_time'].replace('T', ' ').replace('Z', '').split('.')[0]
    print(f"📅 Booking datetime for Odoo (UTC): {booking_datetime_utc}")
    
    # Get Workiz job details to retrieve SerialId
    workiz_job = get_workiz_job_details(opportunity['x_workiz_graveyard_uuid'])
    
    if not workiz_job:
        print("⚠️  Could not fetch Workiz job details - creating without serial ID")
        order_name = None
    else:
        serial_id = workiz_job.get('SerialId', '')
        order_name = format_serial_id_for_odoo(serial_id) if serial_id else None
    
    # Create sales order
    workiz_link = opportunity.get('x_workiz_graveyard_link') or f"https://app.workiz.com/root/job/{opportunity['x_workiz_graveyard_uuid']}/1"
    
    result = create_sales_order(
        contact_id=contact['id'],
        property_id=property_id,
        workiz_uuid=opportunity['x_workiz_graveyard_uuid'],
        workiz_link=workiz_link,
        booking_datetime=booking_datetime_utc,
        workiz_status="Pending",
        order_name=order_name
    )
    
    return result


# ==============================================================================
# TEST WITH BEV HARTIN DATA
# ==============================================================================

if __name__ == "__main__":
    
    print("\n" + "🧪 "*35)
    print("TEST: Create Sales Order for Bev Hartin")
    print("🧪 "*35 + "\n")
    
    test_contact = {
        'id': 23629,
        'name': 'Bev Hartin',
        'email': 'xxxxxxOdoo@gmail.com',
        'phone': '+1 951-972-6946',
        'street': '29 Toscana Way E',
        'city': 'Rancho Mirage'
    }
    
    test_opportunity = {
        'id': 41,
        'name': 'Reactivation Campaign - Bev Hartin - 02/02/2026',
        'x_workiz_graveyard_uuid': 'SG6AMX',
        'x_workiz_graveyard_link': 'https://app.workiz.com/root/job/SG6AMX/1',
        'expected_revenue': 635.0
    }
    
    test_booking_info = {
        'name': 'Bev Hartin',
        'email': 'dansyourrealtor@gmail.com',
        'service_address': '29 Toscana Way E',
        'service_type': 'Windows Outside Only',
        'booking_time': '2026-02-20T22:30:00.000000Z'
    }
    
    test_won_result = {
        'success': True,
        'message': 'Opportunity marked as Won'
    }
    
    result = process_phase3e(test_contact, test_opportunity, test_booking_info, test_won_result)
    
    print("\n" + "="*70)
    print("PHASE 3E RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"\n✅ SALES ORDER CREATED!")
        print(f"   Sales Order ID: {result['sales_order_id']}")
        print(f"   Workiz UUID: {test_opportunity['x_workiz_graveyard_uuid']}")
        print(f"   Go check Odoo Sales → Orders to verify!")
    
    print("="*70 + "\n")
