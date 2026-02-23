"""
Check sale.order state for given SO names (e.g. 004160, 003892).
Run from this folder: python check_so_state.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

SO_NAMES = ["004160", "003892"]


def main():
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
                [[["name", "in", SO_NAMES]]],
                {"fields": ["id", "name", "state", "partner_id", "x_studio_x_studio_workiz_uuid"]},
            ],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=15)
    data = r.json()
    if data.get("error"):
        print("Error:", data["error"])
        return
    result = data.get("result", [])
    if not result:
        print("No sale orders found for names:", SO_NAMES)
        return
    print("SO name      | state  | id    | Workiz UUID")
    print("-" * 55)
    for so in result:
        print(f" {so.get('name', '')}   | {so.get('state', '')} | {so.get('id')} | {so.get('x_studio_x_studio_workiz_uuid', '')}")


if __name__ == "__main__":
    main()
