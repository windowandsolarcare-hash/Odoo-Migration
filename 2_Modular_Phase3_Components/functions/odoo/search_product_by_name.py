"""Search for Odoo product by name and return product ID"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def search_product_by_name(product_name):
    """
    Search for Odoo product by name and return product ID.
    
    Args:
        product_name (str): Product name to search for
    
    Returns:
        int: Product ID if found, None otherwise
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
                "product.product",
                "search_read",
                [[["name", "=", product_name]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]["id"]
        return None
    except:
        return None
