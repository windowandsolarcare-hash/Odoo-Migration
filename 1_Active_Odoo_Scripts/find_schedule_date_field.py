# Find the "Job/Schedule Date" custom field on sales order

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Search for date/schedule fields on sale.order
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
                ["name", "ilike", "x_studio"],
                "|",
                ["ttype", "=", "date"],
                ["ttype", "=", "datetime"]
            ]],
               {"fields": ["name", "field_description", "ttype"], "limit": 100}
        ]
    }
}

response = requests.post(ODOO_URL, json=payload, timeout=10)
result = response.json()

print("Fields with 'schedule' in name or label:")
for field in result.get("result", []):
    print(f"  {field['name']} - \"{field['field_description']}\" ({field['ttype']})")
