"""
Manually Reconcile Payment 20
==============================
Reconcile payment ID 20 with its invoice.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Payment 20 Details
# ==============================================================================

def get_payment_20():
    """Get payment ID 20 details."""
    print("\n[*] Getting payment ID 20...")
    
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
                "account.payment",
                "read",
                [[20]],
                {
                    "fields": ["id", "name", "state", "move_id", "invoice_ids", "amount"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    payment = response.json().get("result", [])
    
    if payment:
        payment = payment[0]
        print(f"\n[OK] Payment {payment.get('name')} (ID: {payment.get('id')}):")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Move ID: {payment.get('move_id', [None])[0] if payment.get('move_id') else None}")
        print(f"   Invoice IDs: {payment.get('invoice_ids', [])}")
        print(f"   Amount: ${payment.get('amount', 0):.2f}")
        
        move_id = payment.get('move_id', [None])[0] if payment.get('move_id') else None
        invoice_ids = payment.get('invoice_ids', [])
        
        if move_id and invoice_ids:
            return payment.get('id'), move_id, invoice_ids[0]
        elif invoice_ids:
            print(f"\n[!] Payment has no move_id - it may not be fully posted")
            return payment.get('id'), None, invoice_ids[0]
    
    return None, None, None

# ==============================================================================
# Reconcile
# ==============================================================================

def reconcile(payment_id, move_id, invoice_id):
    """Reconcile payment with invoice."""
    if not move_id:
        print(f"\n[!] Cannot reconcile - payment has no move_id")
        print(f"    Payment needs to be fully posted first")
        return False
    
    print(f"\n[*] Reconciling payment {payment_id} (move {move_id}) with invoice {invoice_id}...")
    
    # Get invoice receivable line
    payload_invoice = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "account.move.line",
                "search_read",
                [[["move_id", "=", invoice_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", ">", 0]]],
                {
                    "fields": ["id", "balance"]
                }
            ]
        }
    }
    
    response_invoice = requests.post(ODOO_URL, json=payload_invoice, timeout=10)
    invoice_lines = response_invoice.json().get("result", [])
    
    # Get payment receivable line
    payload_payment = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "account.move.line",
                "search_read",
                [[["move_id", "=", move_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", "<", 0]]],
                {
                    "fields": ["id", "balance"]
                }
            ]
        }
    }
    
    response_payment = requests.post(ODOO_URL, json=payload_payment, timeout=10)
    payment_lines = response_payment.json().get("result", [])
    
    print(f"\n[INFO] Invoice receivable lines: {len(invoice_lines)}")
    print(f"[INFO] Payment receivable lines: {len(payment_lines)}")
    
    if invoice_lines and payment_lines:
        line_ids = [line.get('id') for line in invoice_lines + payment_lines]
        
        payload_reconcile = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "account.move.line",
                    "reconcile",
                    [line_ids]
                ]
            }
        }
        
        response_reconcile = requests.post(ODOO_URL, json=payload_reconcile, timeout=10)
        result = response_reconcile.json().get("result")
        
        if result:
            print(f"[OK] Reconciliation successful!")
            return True
        else:
            error = response_reconcile.json().get("error", {})
            print(f"[!] Failed: {error}")
            return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("MANUALLY RECONCILE PAYMENT 20")
    print("="*70)
    
    payment_id, move_id, invoice_id = get_payment_20()
    
    if payment_id and invoice_id:
        if move_id:
            reconciled = reconcile(payment_id, move_id, invoice_id)
            if reconciled:
                print("\n" + "="*70)
                print("SUCCESS!")
                print("="*70)
                print("\nPayment has been reconciled with invoice.")
                print("Invoice should now show as paid with $0.00 due.")
                print("\nPlease refresh the invoice page.")
            else:
                print("\n[!] Reconciliation failed")
                print("    Use the 'Apply Payment to Invoice' action (ID: 677)")
                print("    from the payment form's Actions menu")
        else:
            print("\n[!] Payment has no move_id")
            print("    The payment needs to be fully posted first")
            print("    Try clicking 'Post Payment' again")
    else:
        print("\n[!] Could not find payment or invoice")
    
    print("="*70)

