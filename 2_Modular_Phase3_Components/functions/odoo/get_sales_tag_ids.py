"""Get Odoo sales order tag IDs (crm.tag) for given tag names"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def get_sales_tag_ids(tag_names):
    """
    Get Odoo sales order tag IDs (crm.tag) for given tag names.
    
    Args:
        tag_names: Either list of tag names or comma-separated string
    
    Returns:
        list: List of tag IDs (integers)
    """
    if not tag_names:
        return []
    
    if isinstance(tag_names, str):
        tags_list = [t.strip() for t in tag_names.split(',') if t.strip()]
    elif isinstance(tag_names, list):
        tags_list = [str(t).strip() for t in tag_names if t]
    else:
        return []
    
    tag_ids = []
    
    for tag_name in tags_list:
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
                    "crm.tag",
                    "search_read",
                    [[["name", "=", tag_name]]],
                    {"fields": ["id"], "limit": 1}
                ]
            }
        }
        
        try:
            response = requests.post(ODOO_URL, json=payload, timeout=10)
            result = response.json()
            
            if result.get("result") and len(result["result"]) > 0:
                tag_id = result["result"][0]["id"]
                tag_ids.append(tag_id)
        except:
            pass
    
    return tag_ids
