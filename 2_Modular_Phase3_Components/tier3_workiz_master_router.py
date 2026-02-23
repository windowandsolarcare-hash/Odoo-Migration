"""
TIER 3 MASTER ROUTER - Workiz to Odoo Integration
Handles all 3 paths based on Contact/Property existence

Path A: Contact ✅ + Property ✅ → Create Sales Order
Path B: Contact ✅ + Property ❌ → Create Property + Sales Order  
Path C: Contact ❌ + Property ❌ → Create Contact + Property + Sales Order

Date: 2026-02-05
"""

import sys
import os

# Add functions directory to path for imports
sys.path.append(os.path.dirname(__file__))

from config import *
from functions.workiz.get_job_details import get_job_details
from functions.odoo.search_contact_by_client_id import search_contact_by_client_id
from functions.odoo.create_contact import create_contact
from functions.odoo.create_property import create_property
from functions.odoo.search_property_and_contact import search_property_and_contact
from functions.odoo.find_opportunity import find_opportunity
from functions.odoo.mark_opportunity_won import mark_opportunity_won
from functions.odoo.create_sales_order import create_sales_order
from functions.odoo.confirm_sales_order import confirm_sales_order
from functions.odoo.update_sales_order_date import update_sales_order_date
from functions.odoo.update_property_fields import update_property_fields
from functions.odoo.update_contact_email import update_contact_email


# search_contact_by_client_id() is now imported from functions/odoo/search_contact_by_client_id.py


def search_property_for_contact(service_address, contact_id):
    """
    Search for Property linked to a specific Contact.
    
    Args:
        service_address (str): Service address from Workiz
        contact_id (int): Odoo contact ID
    
    Returns:
        dict: {'property_id': int, ...} or None if not found
    """
    import requests
    
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
                    ["x_studio_x_studio_record_category", "=", "Property"],
                    ["street", "=", service_address.strip()],
                    ["parent_id", "=", contact_id]
                ]],
                {"fields": ["id", "name", "street"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            property_record = result["result"][0]
            print(f"[OK] Property found: {property_record['street']} (ID: {property_record['id']})")
            return {
                'property_id': property_record['id'],
                'street': property_record['street']
            }
        
        print(f"[INFO] Property not found for address: {service_address}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to search property: {e}")
        return None


# create_contact() is now imported from functions/odoo/create_contact.py

# create_property() is now imported from functions/odoo/create_property.py


def create_opportunity(contact_id, workiz_uuid):
    """
    Create new Opportunity (crm.lead) in Odoo.
    
    Args:
        contact_id (int): Contact ID
        workiz_uuid (str): Workiz job UUID
    
    Returns:
        int: New opportunity ID or None if failed
    """
    import requests
    from datetime import datetime
    
    opp_data = {
        "name": f"Workiz Job - {workiz_uuid[:8]}",
        "partner_id": contact_id,
        "x_workiz_graveyard_uuid": workiz_uuid,
        "type": "opportunity",
        "date_open": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    
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
                "create",
                [opp_data]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            opp_id = result["result"]
            print(f"[OK] Opportunity created (ID: {opp_id})")
            return opp_id
        
        print(f"[ERROR] Failed to create opportunity: {result}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception creating opportunity: {e}")
        return None


# ============================================================================
# PATH EXECUTION FUNCTIONS
# ============================================================================

def execute_path_a(contact_id, property_id, workiz_job):
    """
    PATH A: Contact exists + Property exists
    Just create the sales order
    """
    from functions.utils.format_serial_id import format_serial_id
    from functions.utils.convert_pacific_to_utc import convert_pacific_to_utc
    from datetime import datetime
    
    print("\n" + "="*70)
    print("EXECUTING PATH A: Existing Contact + Existing Property")
    print("="*70)
    
    # Step 1: Prepare data for sales order
    # Get booking datetime from Workiz (in Pacific time) and convert to UTC
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        # Workiz JobDateTime is in Pacific time: "2026-04-03 08:30:00"
        # Convert to UTC for Odoo
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format order name
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 2: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        msg = (so_result or {}).get('message') or (so_result or {}).get('error') or 'Failed to create sales order'
        return {'success': False, 'error': msg}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 3: Confirm sales order
    confirm_result = confirm_sales_order(sales_order_id)
    if not confirm_result:
        print("[WARNING] Could not confirm sales order")
    
    # Step 4: Update date_order (fix Odoo override)
    update_result = update_sales_order_date(sales_order_id, booking_datetime)
    if not update_result:
        print("[WARNING] Could not update date_order")
    
    # Step 5: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH A COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'A',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


def execute_path_b(contact_id, service_address, workiz_job):
    """
    PATH B: Contact exists + Property DOES NOT exist
    Create property, then sales order
    """
    from functions.utils.format_serial_id import format_serial_id
    from functions.utils.convert_pacific_to_utc import convert_pacific_to_utc
    from datetime import datetime
    
    print("\n" + "="*70)
    print("EXECUTING PATH B: Existing Contact + New Property")
    print("="*70)
    
    # Step 1: Create property with Workiz LocationId and full address
    location_id = workiz_job.get('LocationId')
    property_id = create_property(contact_id, service_address, workiz_job, location_id)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    # Step 2: Prepare data for sales order
    # Convert Pacific time from Workiz to UTC for Odoo
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 5: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        msg = (so_result or {}).get('message') or (so_result or {}).get('error') or 'Failed to create sales order'
        return {'success': False, 'error': msg}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 6: Confirm sales order
    confirm_result = confirm_sales_order(sales_order_id)
    if not confirm_result:
        print("[WARNING] Could not confirm sales order")
    
    # Step 7: Update date_order
    update_result = update_sales_order_date(sales_order_id, booking_datetime)
    if not update_result:
        print("[WARNING] Could not update date_order")
    
    # Step 8: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH B COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'B',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


def execute_path_c(customer_name, service_address, workiz_job, client_id):
    """
    PATH C: Contact DOES NOT exist (and property doesn't exist)
    Create contact, property, then sales order
    """
    from functions.utils.format_serial_id import format_serial_id
    from functions.utils.convert_pacific_to_utc import convert_pacific_to_utc
    from datetime import datetime
    
    print("\n" + "="*70)
    print("EXECUTING PATH C: New Contact + New Property")
    print("="*70)
    
    # Step 1: Create contact with Workiz ClientId and all fields
    contact_id = create_contact(customer_name, client_id, workiz_job)
    if not contact_id:
        return {'success': False, 'error': 'Failed to create contact'}
    
    # Step 2: Create property with Workiz LocationId and full address
    location_id = workiz_job.get('LocationId')
    property_id = create_property(contact_id, service_address, workiz_job, location_id)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    # Step 3: Prepare data for sales order
    # Convert Pacific time from Workiz to UTC for Odoo
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 6: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        msg = (so_result or {}).get('message') or (so_result or {}).get('error') or 'Failed to create sales order'
        return {'success': False, 'error': msg}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 7: Confirm sales order
    confirm_result = confirm_sales_order(sales_order_id)
    if not confirm_result:
        print("[WARNING] Could not confirm sales order")
    
    # Step 8: Update date_order
    update_result = update_sales_order_date(sales_order_id, booking_datetime)
    if not update_result:
        print("[WARNING] Could not update date_order")
    
    # Step 9: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH C COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'C',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


# ============================================================================
# MAIN ROUTER
# ============================================================================

def main(input_data):
    """
    Master router: Determines path and executes appropriate workflow.
    
    Expected input_data from Zapier:
    {
        'job_uuid': 'ABC123',  # From Workiz trigger
    }
    """
    print("\n" + "="*70)
    print("WORKIZ -> ODOO MASTER ROUTER")
    print("="*70)
    
    # Extract job UUID from Zapier trigger
    job_uuid = input_data.get('job_uuid')
    if not job_uuid:
        return {'success': False, 'error': 'No job_uuid provided'}
    
    # Step 1: Get full Workiz job details
    print(f"\n[*] Fetching Workiz job: {job_uuid}")
    workiz_job = get_job_details(job_uuid)
    if not workiz_job:
        return {'success': False, 'error': 'Failed to fetch Workiz job'}
    
    # Extract key fields
    customer_name = workiz_job.get('FirstName', '') + ' ' + workiz_job.get('LastName', '')
    customer_name = customer_name.strip()
    service_address = workiz_job.get('Address', '').strip()
    phone = workiz_job.get('Phone', '')
    email = workiz_job.get('Email', '')
    client_id = workiz_job.get('ClientId')  # Workiz ClientId - THE KEY FIELD
    
    print(f"[*] Customer: {customer_name}")
    print(f"[*] ClientId: {client_id}")
    print(f"[*] Address: {service_address}")
    
    if not client_id:
        return {'success': False, 'error': 'Missing ClientId from Workiz job'}
    
    if not service_address:
        return {'success': False, 'error': 'Missing service address'}
    
    # Step 2: Search for Contact by ClientId (ONLY way to search)
    print(f"\n[*] Searching for Contact by ClientId: {client_id}")
    contact_result = search_contact_by_client_id(client_id)
    
    if contact_result:
        # Contact exists - check for property
        contact_id = contact_result['contact_id']
        
        print(f"\n[*] Searching for Property: {service_address}")
        property_result = search_property_for_contact(service_address, contact_id)
        
        if property_result:
            # PATH A: Both exist
            property_id = property_result['property_id']
            return execute_path_a(contact_id, property_id, workiz_job)
        else:
            # PATH B: Contact exists, property doesn't
            return execute_path_b(contact_id, service_address, workiz_job)
    else:
        # PATH C: Contact doesn't exist (property won't exist either)
        return execute_path_c(customer_name, service_address, workiz_job, client_id)


# ============================================================================
# ZAPIER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {
        'job_uuid': '90OX52'  # Path C test: Leonard Karp (NEW customer)
    }
    
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(result)
    print("="*70)
# else:
#     # For Zapier deployment
#     output = main(input_data)
