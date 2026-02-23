"""Quick delete single sales order"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
from config import *
import requests

def cancel_and_delete_so(so_id):
    # Cancel
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "action_cancel", [[so_id]]]}}
    requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Cancelled SO {so_id}")
    
    # Delete
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "unlink", [[so_id]]]}}
    requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Deleted SO {so_id}")

cancel_and_delete_so(15783)  # Path C test - Leonard Karp
