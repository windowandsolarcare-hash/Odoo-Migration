"""
Search all sales orders for a property (ordered by date DESC)
"""
import sys
sys.path.append('../..')
import requests
from config import *


def search_all_sales_orders_for_property(property_id):
    """
    Get all sales orders for a property, ordered by date DESC.
    
    Args:
        property_id (int): Property ID in Odoo
        
    Returns:
        list: List of sales order records (most recent first)
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "search_read",
                [[
                    ["partner_shipping_id", "=", property_id],
                    ["state", "in", ["sale", "done"]]
                ]],
                {
                    "fields": ["id", "name", "x_studio_x_studio_workiz_uuid", "date_order"],
                    "order": "date_order desc"
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    print(f"[*] Found {len(result)} sales orders for property {property_id}")
    return result


if __name__ == "__main__":
    # Test
    test_property_id = 24169  # Blair Becker property
    orders = search_all_sales_orders_for_property(test_property_id)
    
    print("\nSales Orders:")
    for i, order in enumerate(orders):
        print(f"{i}. {order['name']} - {order['date_order']} - UUID: {order['x_studio_x_studio_workiz_uuid']}")
