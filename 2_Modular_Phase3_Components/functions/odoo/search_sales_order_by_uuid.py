"""
Search for Sales Order by Workiz UUID
"""
import sys
sys.path.append('../..')
import requests
from config import *


def search_sales_order_by_uuid(workiz_uuid):
    """
    Search for a Sales Order in Odoo by Workiz UUID.
    
    Args:
        workiz_uuid (str): The Workiz job UUID
        
    Returns:
        dict or None: Sales Order record if found, None otherwise
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
                "search_read",
                [[["x_studio_x_studio_workiz_uuid", "=", workiz_uuid]]],
                {
                    "fields": [
                        "id", "name", "partner_id", "partner_shipping_id",
                        "x_studio_x_studio_workiz_uuid"
                    ],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result and len(result) > 0:
        return result[0]
    return None


if __name__ == "__main__":
    # Test
    test_uuid = "NH4YY5"  # Bev Hartin test job
    result = search_sales_order_by_uuid(test_uuid)
    if result:
        print(f"Found SO: {result['name']} (ID: {result['id']})")
    else:
        print(f"No SO found for UUID: {test_uuid}")
