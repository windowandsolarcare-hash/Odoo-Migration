import sys
sys.path.append('.')
import requests
from config import *

so_id = 15804

# First check current state
payload1 = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
            ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
            "sale.order", "search_read",
            [[["id", "=", so_id]]],
            {"fields": ["name", "state"]}
        ]
    }
}
response1 = requests.post(ODOO_URL, json=payload1, timeout=10)
result1 = response1.json().get("result", [])
if result1:
    print(f"SO {result1[0]['name']}: Current state = {result1[0]['state']}")

# Try action_done
print("\nTrying action_done...")
payload2 = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
            ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
            "sale.order", "action_done",
            [[so_id]]
        ]
    }
}
response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
result2 = response2.json()
print(f"Result: {result2}")
