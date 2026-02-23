"""
Mark Sales Order as Done/Locked in Odoo
"""
import sys
sys.path.append('../..')
import requests
from config import *


def mark_sales_order_done(so_id):
    """
    Mark a Sales Order as Done (completed/locked) in Odoo.
    
    In Odoo 19, this is done by setting the state directly to 'done'.
    
    Args:
        so_id (int): Sales Order ID
        
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
                [[so_id], {"state": "done"}]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    # write returns True if successful
    return result.get("result") is True


if __name__ == "__main__":
    # Test - mark a test SO as done
    test_so_id = 15804
    success = mark_sales_order_done(test_so_id)
    print(f"Mark as done: {'successful' if success else 'failed'}")
