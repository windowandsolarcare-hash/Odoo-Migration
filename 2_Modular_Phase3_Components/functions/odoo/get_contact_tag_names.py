"""Get tag names from contact's category_id field"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def get_contact_tag_names(contact_id):
    """
    Get tag names from contact's category_id field.
    
    Args:
        contact_id (int): Odoo contact ID
    
    Returns:
        list: List of tag names (strings)
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
                "read",
                [[contact_id]],
                {"fields": ["category_id"]}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            category_data = result["result"][0].get("category_id", [])
            tag_names = [tag[1] for tag in category_data if len(tag) > 1]
            return tag_names
        return []
    except:
        return []
