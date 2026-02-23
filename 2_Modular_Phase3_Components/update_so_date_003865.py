"""
One-off: Set order date (date_order) for SO 003865 to 12/9/2025.
Run from this folder: python update_so_date_003865.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.utils.convert_pacific_to_utc import convert_pacific_to_utc


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(
        ODOO_URL,
        json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    # Find SO by name (e.g. 003865 or S003865)
    for name in ["003865", "S003865"]:
        rows = odoo_rpc(
            "sale.order",
            "search_read",
            [[["name", "=", name]]],
            {"fields": ["id", "name", "date_order"], "limit": 1},
        )
        if rows:
            break
    if not rows:
        # Try ilike in case of spacing
        rows = odoo_rpc(
            "sale.order",
            "search_read",
            [[["name", "ilike", "003865"]]],
            {"fields": ["id", "name", "date_order"], "limit": 5},
        )
    if not rows:
        print("[!] No sales order found with name 003865 or S003865.")
        return
    so = rows[0]
    so_id = so["id"]
    so_name = so["name"]
    # User time is always Pacific; Odoo stores UTC. Convert before writing.
    pacific_datetime = "2025-12-09 09:30:00"  # 12/9/2025 9:30 AM Pacific
    new_date = convert_pacific_to_utc(pacific_datetime)
    odoo_rpc("sale.order", "write", [[so_id], {"date_order": new_date}])
    print(f"[OK] Updated SO {so_name} (id {so_id}) order date to {pacific_datetime} Pacific (stored as {new_date} UTC).")
    print(f"     Previous date_order: {so.get('date_order')}")


if __name__ == "__main__":
    main()
