import sys
sys.path.append('.')
import requests
from config import *

so_id = 15805

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
            [[["id", "=", so_id]]],
            {
                "fields": [
                    "name", "x_studio_is_paid", "x_studio_tip_amount",
                    "x_studio_x_studio_workiz_status"
                ]
            }
        ]
    }
}

response = requests.post(ODOO_URL, json=payload, timeout=10)
result = response.json().get("result", [])

if result:
    so = result[0]
    print(f"Sales Order: {so['name']} (ID: {so['id']})")
    print(f"Status: {so.get('x_studio_x_studio_workiz_status')}")
    print(f"Is Paid: {so.get('x_studio_is_paid')}")
    print(f"Tip Amount: {so.get('x_studio_tip_amount')}")
else:
    print("SO not found")
