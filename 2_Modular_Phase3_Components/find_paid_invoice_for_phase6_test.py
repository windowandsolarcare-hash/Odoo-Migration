"""
Find a paid customer invoice in Odoo whose SO has a Workiz UUID.
Use the returned invoice_id to test: python phase6_payment_sync_to_workiz.py <invoice_id>
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

def odoo_call(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")

# Paid customer invoices
invs = odoo_call("account.move", "search_read", [
    [["move_type", "=", "out_invoice"], ["payment_state", "=", "paid"], ["state", "=", "posted"]]
], {"fields": ["id", "name", "invoice_origin", "amount_total", "payment_state"], "limit": 50, "order": "id desc"})

if not invs:
    print("No paid customer invoices found.")
    sys.exit(1)

# SOs that have Workiz UUID
so_names = [inv["invoice_origin"] for inv in invs if inv.get("invoice_origin")]
if not so_names:
    print("No invoices with sale order origin.")
    sys.exit(1)

domain = [["name", "in", so_names], ["x_studio_x_studio_workiz_uuid", "!=", False]]
sos = odoo_call("sale.order", "search_read", [domain], {"fields": ["name", "x_studio_x_studio_workiz_uuid"]})
so_with_uuid = {s["name"]: s["x_studio_x_studio_workiz_uuid"] for s in sos}

for inv in invs:
    origin = inv.get("invoice_origin")
    if origin and origin in so_with_uuid:
        print(f"Invoice ID: {inv['id']}  Name: {inv.get('name')}  Origin: {origin}  Workiz UUID: {so_with_uuid[origin]}  Amount: {inv.get('amount_total')}")
        print(f"\nRun: python phase6_payment_sync_to_workiz.py {inv['id']}")
        break
else:
    print("No paid invoice found whose SO has a Workiz UUID.")
    print("Invoices checked:", len(invs), "SO names with UUID:", len(so_with_uuid))
