"""Find Odoo Property by address, then get Contact from parent_id"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def search_property_and_contact(street_address):
    """
    Find Odoo Property by address, then get Contact from parent_id.
    Follows Mirror V31.11 hierarchy: Client -> Property -> Job
    
    Args:
        street_address (str): Street address to search
    
    Returns:
        dict: {'property_id', 'contact_id', 'property_name', 'contact_name', 'street'}
        OR None if not found
    """
    # Step 1: Find Property by address
    property_payload = {
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
                    ["street", "=", street_address],
                    ["x_studio_x_studio_record_category", "=", "Property"]
                ]],
                {"fields": ["id", "name", "street", "city", "parent_id"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=property_payload, timeout=10)
        result = response.json()
        
        if not result.get("result") or len(result["result"]) == 0:
            print(f"[ERROR] No Property found for address: {street_address}")
            return None
        
        property_record = result["result"][0]
        property_id = property_record['id']
        property_name = property_record['name']
        
        # Step 2: Get parent_id (Contact/Client ID)
        parent_id = property_record.get('parent_id')
        
        if not parent_id:
            print(f"[ERROR] Property {property_id} has no parent_id (Contact)")
            return None
        
        # parent_id is returned as [id, name] tuple
        contact_id = parent_id[0] if isinstance(parent_id, list) else parent_id
        contact_name = parent_id[1] if isinstance(parent_id, list) and len(parent_id) > 1 else "Unknown"
        
        print(f"[OK] Property found: {property_name} (ID: {property_id})")
        print(f"[OK] Contact found: {contact_name} (ID: {contact_id})")
        
        return {
            'property_id': property_id,
            'contact_id': contact_id,
            'property_name': property_name,
            'contact_name': contact_name,
            'street': property_record['street']
        }
        
    except Exception as e:
        print(f"[ERROR] Exception in property/contact lookup: {e}")
        return None
