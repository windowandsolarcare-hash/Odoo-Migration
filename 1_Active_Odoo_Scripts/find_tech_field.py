# Find the tech/team field on sales order

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Search for the specific field
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
            "ir.model.fields",
            "search_read",
            [[
                ["model", "=", "sale.order"],
                ["name", "=", "x_studio_x_studio_workiz_tech"]
            ]],
            {"fields": ["name", "field_description", "ttype"], "limit": 1}
        ]
    }
}

response = requests.post(ODOO_URL, json=payload, timeout=10)
result = response.json()

print("Tech field on sale.order:")
for field in result.get("result", []):
    print(f"  {field['name']} - \"{field['field_description']}\" ({field['ttype']})")
