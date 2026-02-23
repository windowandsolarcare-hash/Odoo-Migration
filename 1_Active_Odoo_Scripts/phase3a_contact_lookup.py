# ==============================================================================
# PHASE 3A: CALENDLY WEBHOOK & CONTACT LOOKUP
# ==============================================================================
# Purpose: Receive Calendly booking webhook and find matching Odoo contact
# Created: 2026-02-05
# Status: Development - Tested with Bev Hartin test booking
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
# PHASE 3A FUNCTION
# ==============================================================================

def search_contact_by_address(service_address):
    """
    Search for Odoo contact by service address from Calendly booking.
    
    Args:
        service_address (str): Street address from Calendly (e.g., "29 Toscana Way E")
        
    Returns:
        dict: Contact record with id, name, phone, email, street, city
        None: If no contact found
        
    TESTED: 2026-02-05 - Working with Bev Hartin test booking
    NOTES: 
    - Uses exact match on street field
    - Filters by x_studio_record_category = "Contact" (excludes Property records)
    - Returns only first match (assumes unique addresses)
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
                [
                    [
                        ["street", "=", service_address],
                        ["x_studio_x_studio_record_category", "=", "Contact"]
                    ]
                ],
                {
                    "fields": ["id", "name", "phone", "email", "street", "city"],
                    "limit": 1
                }
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
            print(f"[ERROR] No contact found for address: {service_address}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error searching Odoo contact: {e}")
        return None


def process_calendly_webhook(calendly_data):
    """
    Main handler for Calendly webhook data (Phase 3A).
    
    Args:
        calendly_data (dict): Webhook payload from Calendly/Zapier
        
    Returns:
        dict: {
            'success': bool,
            'contact': dict or None,
            'booking_info': dict,
            'message': str
        }
    """
    
    # Extract booking data from Calendly
    booking_info = {
        'name': calendly_data.get('Name', ''),
        'email': calendly_data.get('Email', ''),
        'service_address': calendly_data.get('Service Address', ''),
        'service_type': calendly_data.get('Service Type', ''),
        'notes': calendly_data.get('Additional Notes', ''),
        'event_type': calendly_data.get('Event Type', ''),
        'booking_time': calendly_data.get('Booking Time', ''),
        'timezone': calendly_data.get('Timezone', ''),
        'status': calendly_data.get('Status', '')
    }
    
    print("\n" + "="*70)
    print("PHASE 3A: CALENDLY BOOKING RECEIVED")
    print("="*70)
    print(f"Customer: {booking_info['name']}")
    print(f"Email: {booking_info['email']}")
    print(f"Address: {booking_info['service_address']}")
    print(f"Service: {booking_info['service_type']}")
    print(f"Booking Time: {booking_info['booking_time']}")
    print("="*70 + "\n")
    
    # Validate required fields
    if not booking_info['service_address']:
        return {
            'success': False,
            'contact': None,
            'booking_info': booking_info,
            'message': 'Service address is missing from Calendly data'
        }
    
    # Search for contact in Odoo
    contact = search_contact_by_address(booking_info['service_address'])
    
    if contact:
        return {
            'success': True,
            'contact': contact,
            'booking_info': booking_info,
            'message': f"Contact found: {contact['name']} (ID: {contact['id']})"
        }
    else:
        return {
            'success': False,
            'contact': None,
            'booking_info': booking_info,
            'message': f"No contact found for address: {booking_info['service_address']}"
        }


# ==============================================================================
# TEST WITH BEV HARTIN DATA
# ==============================================================================

if __name__ == "__main__":
    # Test data from actual Calendly booking (2026-02-05 - Updated)
    test_calendly_data = {
        'Name': 'Bev Hartin',
        'Email': 'dansyourrealtor@gmail.com',
        'Service Address': '29 Toscana Way E',
        'Service Type': 'Windows Inside & Outside Plus Screens',
        'Additional Notes': 'Test',
        'Event Type': 'Rancho Mirage Service',
        'Booking Time': '2026-03-12T15:30:00.000000Z',
        'Timezone': 'America/Los_Angeles',
        'Status': 'active'
    }
    
    print("\n🧪 TESTING PHASE 3A with Bev Hartin booking data...\n")
    
    result = process_calendly_webhook(test_calendly_data)
    
    print("\n" + "="*70)
    print("PHASE 3A RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['contact']:
        print(f"\nContact Details:")
        print(f"  ID: {result['contact']['id']}")
        print(f"  Name: {result['contact']['name']}")
        print(f"  Email: {result['contact']['email']}")
        print(f"  Phone: {result['contact']['phone']}")
        print(f"  Street: {result['contact']['street']}")
        print(f"  City: {result['contact']['city']}")
    print("="*70 + "\n")
