"""Update Odoo contact email address"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def update_contact_email(contact_id, new_email):
    """
    Update Odoo contact email address.
    
    Args:
        contact_id (int): Odoo contact ID
        new_email (str): New email address
    
    Returns:
        dict: {'success': bool, 'message': str (optional)}
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
                "write",
                [[contact_id], {"email": new_email}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Contact email updated!")
            return {'success': True}
        else:
            return {'success': False, 'message': 'Email update failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
