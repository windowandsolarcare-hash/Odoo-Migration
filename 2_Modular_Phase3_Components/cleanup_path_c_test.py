"""Cleanup Path C test data - SO, Property, Contact"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
from config import *
import requests

def cancel_sales_order(so_id):
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "action_cancel", [[so_id]]]}}
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Cancelled SO {so_id}")

def delete_sales_order(so_id):
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "unlink", [[so_id]]]}}
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Deleted SO {so_id}")

def delete_property(property_id):
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "res.partner", "unlink", [[property_id]]]}}
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Deleted Property {property_id}")

def delete_contact(contact_id):
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "res.partner", "unlink", [[contact_id]]]}}
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    print(f"[OK] Deleted Contact {contact_id}")

# Path C test - latest run:
# SO: 15794
# Contact: 26335 (Leonard Karp)
# Property: 26336 (12 Vía Verde)

print("Cleaning up Leonard Karp test data...")
cancel_sales_order(15794)
delete_sales_order(15794)
delete_property(26336)
delete_contact(26335)
print("Cleanup complete!")
