# ==============================================================================
# PHASE 3F: UPDATE CONTACT EMAIL
# ==============================================================================
# Purpose: Update Odoo contact with email from Calendly booking
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
# PHASE 3F FUNCTION
# ==============================================================================

def update_contact_email(contact_id, email):
    """
    Update Odoo contact email field.
    
    Args:
        contact_id (int): Odoo contact ID
        email (str): Email address from Calendly
        
    Returns:
        dict: {'success': bool, 'message': str}
        
    TESTED: 2026-02-05 - Ready for testing
    NOTES: 
    - Only updates if email is provided (not empty)
    - Updates existing email or adds if missing
    """
    
    if not email:
        return {
            'success': True,
            'message': 'No email provided - skipped update'
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
                "res.partner",
                "write",
                [[contact_id], {"email": email}]
            ]
        }
    }
    
    print(f"\n[*] Updating contact email...")
    print(f"   Contact ID: {contact_id}")
    print(f"   New Email: {email}")
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") == True:
            print(f"[OK] Contact email updated!")
            return {
                'success': True,
                'message': f"Contact {contact_id} email updated to {email}"
            }
        else:
            error = result.get("error", {})
            print(f"[ERROR] Error updating email: {error}")
            return {
                'success': False,
                'message': f"Error: {error.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        print(f"[ERROR] Exception updating email: {e}")
        return {
            'success': False,
            'message': f"Exception: {str(e)}"
        }


def process_phase3f(contact, booking_info):
    """
    Phase 3F handler: Update contact email from Calendly booking.
    
    Args:
        contact (dict): Contact record from Phase 3A
        booking_info (dict): Booking data from Calendly
        
    Returns:
        dict: {
            'success': bool,
            'message': str
        }
    """
    
    print("\n" + "="*70)
    print("PHASE 3F: UPDATE CONTACT EMAIL")
    print("="*70)
    print(f"Contact ID: {contact['id']}")
    print(f"Contact Name: {contact['name']}")
    print(f"Current Email: {contact.get('email', 'None')}")
    print(f"Calendly Email: {booking_info.get('email', 'None')}")
    print("="*70 + "\n")
    
    # Update email
    result = update_contact_email(
        contact_id=contact['id'],
        email=booking_info.get('email', '')
    )
    
    return result


# ==============================================================================
# TEST WITH BEV HARTIN DATA
# ==============================================================================

if __name__ == "__main__":
    
    print("\n" + "- "*35)
    print("TEST: Update Contact Email for Bev Hartin")
    print("- "*35 + "\n")
    
    test_contact = {
        'id': 23629,
        'name': 'Bev Hartin',
        'email': 'xxxxxxOdoo@gmail.com',
        'phone': '+1 951-972-6946',
        'street': '29 Toscana Way E',
        'city': 'Rancho Mirage'
    }
    
    test_booking_info = {
        'name': 'Bev Hartin',
        'email': 'dansyourrealtor@gmail.com',
        'service_address': '29 Toscana Way E',
        'service_type': 'Windows Outside Only',
        'booking_time': '2026-02-20T22:30:00.000000Z'
    }
    
    result = process_phase3f(test_contact, test_booking_info)
    
    print("\n" + "="*70)
    print("PHASE 3F RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"\n[OK] EMAIL UPDATED!")
        print(f"   Old: {test_contact['email']}")
        print(f"   New: {test_booking_info['email']}")
        print(f"   Go check Odoo contact to verify!")
    
    print("="*70 + "\n")
