# Check all date fields in the latest sales order

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Search for sales order by external_id workiz_SG6AMX
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
            [[["x_studio_workiz_uuid", "=", "SG6AMX"]]],
            {
                "fields": [
                    "name",
                    "date_order",
                    "commitment_date",
                    "expected_date",
                    "validity_date",
                    "create_date",
                    "write_date",
                    "signed_on"
                ],
                "limit": 1
            }
        ]
    }
}

response = requests.post(ODOO_URL, json=payload, timeout=10)
result = response.json()

if result.get("result"):
    so = result["result"][0]
    print(f"Sales Order: {so['name']}")
    print(f"  date_order (Order Date): {so.get('date_order')}")
    print(f"  expected_date (Expected Date): {so.get('expected_date')}")
    print(f"  commitment_date (Delivery Date): {so.get('commitment_date')}")
    print(f"  validity_date (Expiration): {so.get('validity_date')}")
    print(f"  signed_on (Signed On): {so.get('signed_on')}")
    print(f"  create_date (Creation Date): {so.get('create_date')}")
    print(f"  write_date (Last Updated): {so.get('write_date')}")
else:
    print("No sales order found")
