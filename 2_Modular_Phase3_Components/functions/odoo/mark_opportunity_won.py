"""Mark Odoo opportunity as Won"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def mark_opportunity_won(opportunity_id):
    """
    Mark Odoo opportunity as Won.
    
    Args:
        opportunity_id (int): Odoo opportunity ID
    
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
