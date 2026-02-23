"""Search for Contact (Client) in Odoo by Workiz ClientId"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def search_contact_by_client_id(client_id):
    """
    Search for Contact (Client) in Odoo by Workiz ClientId (stored in 'ref' field).
    This is the ONLY way to search - ClientId is the single source of truth.
    
    Args:
        client_id (int): Workiz ClientId
    
    Returns:
        dict: {'contact_id': int, 'name': str, 'ref': str, ...} or None if not found
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
                    ["x_studio_x_studio_record_category", "=", "Contact"],
                    ["ref", "=", str(client_id)]
                ]],
                {
                    "fields": ["id", "name", "email", "phone", "street", "ref"],
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
            print(f"[OK] Contact found: {contact['name']} (ID: {contact['id']}, ClientId: {contact['ref']})")
            return {
                'contact_id': contact['id'],
                'name': contact['name'],
                'email': contact.get('email'),
                'phone': contact.get('phone'),
                'ref': contact.get('ref')
            }
        
        print(f"[INFO] Contact not found for ClientId: {client_id}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to search contact: {e}")
        return None
