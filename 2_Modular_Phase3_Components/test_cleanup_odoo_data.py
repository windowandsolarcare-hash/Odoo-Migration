"""
Cleanup Test Data in Odoo
==========================
Usage: 
  python test_cleanup_odoo_data.py --so 12345
  python test_cleanup_odoo_data.py --invoice 67890
  python test_cleanup_odoo_data.py --payment 111

Deletes test Sales Orders, Invoices, or Payments from Odoo.
"""

import requests
import sys
import argparse

# Credentials
ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

def odoo_call(model, method, record_ids, params=None):
    """Generic Odoo API call"""
    
    args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, [record_ids]]
    if params:
        args.append(params)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": args
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    return response.json()

def delete_sales_order(so_id):
    """Cancel and delete Sales Order"""
    
    print(f"Deleting Sales Order {so_id}...")
    
    try:
        # Step 1: Cancel (unlock)
        print("  Cancelling...")
        result = odoo_call("sale.order", "action_cancel", [so_id])
        
        # Step 2: Delete
        print("  Deleting...")
        result = odoo_call("sale.order", "unlink", [so_id])
        
        print(f"✅ Sales Order {so_id} deleted")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def delete_invoice(invoice_id):
    """Set invoice to draft and delete"""
    
    print(f"Deleting Invoice {invoice_id}...")
    
    try:
        # Step 1: Set to draft
        print("  Setting to draft...")
        result = odoo_call("account.move", "button_draft", [invoice_id])
        
        # Step 2: Delete
        print("  Deleting...")
        result = odoo_call("account.move", "unlink", [invoice_id])
        
        print(f"✅ Invoice {invoice_id} deleted")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def delete_payment(payment_id):
    """Set payment to draft and delete"""
    
    print(f"Deleting Payment {payment_id}...")
    
    try:
        # Step 1: Set to draft
        print("  Setting to draft...")
        result = odoo_call("account.payment", "button_draft", [payment_id])
        
        # Step 2: Delete
        print("  Deleting...")
        result = odoo_call("account.payment", "unlink", [payment_id])
        
        print(f"✅ Payment {payment_id} deleted")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CLEANUP TEST DATA IN ODOO")
    print("=" * 60)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--so", type=int, help="Sales Order ID to delete")
    parser.add_argument("--invoice", type=int, help="Invoice ID to delete")
    parser.add_argument("--payment", type=int, help="Payment ID to delete")
    
    args = parser.parse_args()
    
    if not any([args.so, args.invoice, args.payment]):
        print("\n❌ Error: Must specify --so, --invoice, or --payment")
        parser.print_help()
        sys.exit(1)
    
    if args.so:
        delete_sales_order(args.so)
    
    if args.invoice:
        delete_invoice(args.invoice)
    
    if args.payment:
        delete_payment(args.payment)
