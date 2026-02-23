"""
Investigate Payment Reconciliation
==================================
Check if payments are being properly reconciled with invoices.
The issue might be that we're bypassing Odoo's standard payment register wizard.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment and Invoice Link
# ==============================================================================

def check_payment_invoice_link():
    """Check if payments are properly linked to invoices."""
    print("\n[*] Checking payment-invoice reconciliation...")
    
    # Find a recent payment
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
                "search_read",
                [[["state", "=", "posted"]]],
                {
                    "fields": ["id", "name", "amount", "state", "invoice_ids", "reconciled_invoice_ids", "partner_id"],
                    "order": "id desc",
                    "limit": 5
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    payments = response.json().get("result", [])
    
    print(f"\n[INFO] Found {len(payments)} recent posted payments:")
    for payment in payments:
        invoice_ids = payment.get("invoice_ids", [])
        reconciled_ids = payment.get("reconciled_invoice_ids", [])
        print(f"\n  Payment {payment.get('name', 'N/A')} (ID: {payment.get('id')}):")
        print(f"    Amount: ${payment.get('amount', 0):.2f}")
        print(f"    State: {payment.get('state', 'N/A')}")
        print(f"    Linked Invoices: {invoice_ids}")
        print(f"    Reconciled Invoices: {reconciled_ids}")
        
        if invoice_ids and not reconciled_ids:
            print(f"    [!] WARNING: Payment linked to invoices but NOT reconciled!")
    
    # Check invoice payment status
    if payments:
        payment = payments[0]
        invoice_ids = payment.get("invoice_ids", [])
        if invoice_ids:
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
                        "account.move",
                        "read",
                        [invoice_ids],
                        {
                            "fields": ["id", "name", "amount_residual", "payment_state", "state"]
                        }
                    ]
                }
            }
            
            response_invoice = requests.post(ODOO_URL, json=payload_invoice, timeout=10)
            invoices = response_invoice.json().get("result", [])
            
            print(f"\n[INFO] Linked invoices:")
            for invoice in invoices:
                print(f"  Invoice {invoice.get('name', 'N/A')} (ID: {invoice.get('id')}):")
                print(f"    Amount Residual: ${invoice.get('amount_residual', 0):.2f}")
                print(f"    Payment State: {invoice.get('payment_state', 'N/A')}")
                print(f"    State: {invoice.get('state', 'N/A')}")

# ==============================================================================
# Check Standard Pay Action
# ==============================================================================

def check_standard_pay_action():
    """Check what the standard 'Pay' action does."""
    print("\n[*] Checking standard Pay action...")
    
    # Find the Pay action on account.move
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
                "ir.actions.server",
                "search_read",
                [[["name", "=", "Pay"], ["binding_model_id.model", "=", "account.move"]]],
                {
                    "fields": ["id", "name", "binding_model_id", "code", "state"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    actions = response.json().get("result", [])
    
    if actions:
        print(f"[OK] Found Pay action(s):")
        for action in actions:
            print(f"  ID: {action.get('id')}, Name: {action.get('name')}")
            print(f"  State: {action.get('state', 'N/A')}")
    else:
        print(f"[INFO] No server action named 'Pay' found")
        print(f"       Standard Pay is likely a window action that opens payment register wizard")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Payment Reconciliation Issue")
    print("="*70)
    
    check_payment_invoice_link()
    check_standard_pay_action()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nThe issue is likely that:")
    print("1. We're creating payments directly (bypassing payment register wizard)")
    print("2. Payment register wizard automatically reconciles payments with invoices")
    print("3. Direct payment creation might not trigger reconciliation")
    print("\nSOLUTION:")
    print("We should use Odoo's standard 'Pay' action which opens the")
    print("payment register wizard. This wizard handles reconciliation automatically.")
    print("="*70)

