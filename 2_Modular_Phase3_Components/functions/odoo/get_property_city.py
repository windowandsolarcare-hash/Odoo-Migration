"""
Get city from Odoo property record
"""
import sys
sys.path.append('../..')
import requests
from config import *


def get_property_city(property_id):
    """
    Get city from property record in Odoo.
    
    Args:
        property_id (int): Property ID in Odoo
        
    Returns:
        str: City name, or empty string if not found
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "read",
                [[property_id]],
                {"fields": ["city"]}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result", [])
        
        if result and len(result) > 0:
            city = result[0].get('city', '')
            return city if city else ''
        return ''
    
    except Exception as e:
        print(f"[ERROR] Failed to get property city: {e}")
        return ''


if __name__ == "__main__":
    # Test
    test_property_id = 24169  # Blair Becker property
    city = get_property_city(test_property_id)
    print(f"Property {test_property_id} city: {city}")
