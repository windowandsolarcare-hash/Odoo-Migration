"""Find opportunity linked to contact with Workiz UUID populated"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def find_opportunity(contact_id):
    """
    Find opportunity linked to contact with Workiz UUID populated.
    
    Args:
        contact_id (int): Odoo contact ID
    
    Returns:
        dict: {'success': bool, 'opportunity': dict} or {'success': False, 'message': str}
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
