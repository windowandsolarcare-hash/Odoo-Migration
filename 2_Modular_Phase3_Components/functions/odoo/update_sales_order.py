"""
Update Sales Order fields in Odoo
"""
import sys
sys.path.append('../..')
import requests
from config import *


def update_sales_order(so_id, updates):
    """
    Update a Sales Order in Odoo.
    
    Args:
        so_id (int): Sales Order ID
        updates (dict): Dictionary of fields to update
        
    Returns:
        bool: True if successful
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
                "sale.order",
                "write",
                [[so_id], updates]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    return result is True


if __name__ == "__main__":
    # Test - update a test SO
    test_so_id = 15777
    test_updates = {
        "x_studio_x_studio_workiz_status": "Test Update"
    }
    success = update_sales_order(test_so_id, test_updates)
    print(f"Update {'successful' if success else 'failed'}")
