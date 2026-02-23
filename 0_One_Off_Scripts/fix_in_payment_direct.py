"""
Fix In Payment Direct
=====================
payment_state is stored but readonly. Need to reconcile to change it.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Find and Fix Invoices
# ==============================================================================

def find_and_fix():
    """Find invoices in 'in_payment' and fix them."""
    print("\n[*] Finding invoices in 'in_payment' status...")
    
    # Find all invoices in in_payment
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
                "account.move",
                "search_read",
                [[["payment_state", "=", "in_payment"]]],
                {
                    "fields": ["id", "name", "payment_state", "amount_residual", "amount_total"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    invoices = response.json().get("result", [])
    
    print(f"\n[INFO] Found {len(invoices)} invoice(s) in 'in_payment':")
    for inv in invoices:
        print(f"   {inv.get('name')} (ID: {inv.get('id')}): Residual: ${inv.get('amount_residual', 0):.2f}")
    
    # For each invoice, try to reconcile
    for invoice in invoices:
        invoice_id = invoice.get('id')
        amount_residual = invoice.get('amount_residual', 0)
        
        print(f"\n[*] Processing invoice {invoice.get('name')}...")
        
        if amount_residual == 0:
            print(f"   [INFO] Amount residual is $0.00 - should be 'paid'")
            print(f"   [INFO] Trying to trigger recompute of payment_state...")
            
            # Try to write amount_residual to trigger recompute
            # Or try to write payment_state directly (might fail if readonly)
            payload_write = {
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
                        "write",
                        [[invoice_id], {
                            "payment_state": "paid"
                        }]
                    ]
                }
            }
            
            response_write = requests.post(ODOO_URL, json=payload_write, timeout=10)
            result_write = response_write.json().get("result")
            
            if result_write:
                print(f"   [OK] Attempted to write payment_state")
            else:
                error = response_write.json().get("error", {})
                print(f"   [!] Cannot write payment_state: {error.get('message', 'N/A')}")
        
        # Get receivable lines and try to reconcile
        payload_lines = {
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
                    [[["move_id", "=", invoice_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False]]],
                    {
                        "fields": ["id", "balance", "reconciled"]
                    }
                ]
            }
        }
        
        response_lines = requests.post(ODOO_URL, json=payload_lines, timeout=10)
        lines = response_lines.json().get("result", [])
        
        print(f"   [INFO] Unreconciled receivable lines: {len(lines)}")
        
        # Find payments for this invoice
        payload_payments = {
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
                    [[["invoice_ids", "in", [invoice_id]]]],
                    {
                        "fields": ["id", "name", "move_id", "state"]
                    }
                ]
            }
        }
        
        response_payments = requests.post(ODOO_URL, json=payload_payments, timeout=10)
        payments = response_payments.json().get("result", [])
        
        print(f"   [INFO] Linked payments: {len(payments)}")
        
        # Try to reconcile
        for payment in payments:
            move_id = payment.get('move_id', [None])[0] if payment.get('move_id') else None
            if move_id:
                # Get payment lines
                payload_payment_lines = {
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
                            [[["move_id", "=", move_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False]]],
                            {
                                "fields": ["id", "balance"]
                            }
                        ]
                    }
                }
                
                response_payment_lines = requests.post(ODOO_URL, json=payload_payment_lines, timeout=10)
                payment_lines = response_payment_lines.json().get("result", [])
                
                if lines and payment_lines:
                    line_ids = [l.get('id') for l in lines + payment_lines]
                    
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
                    result_reconcile = response_reconcile.json().get("result")
                    
                    if result_reconcile:
                        print(f"   [OK] Reconciled payment {payment.get('name')} with invoice")
                        break

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: In Payment Status")
    print("="*70)
    
    print("\nWHERE 'IN PAYMENT' LIVES:")
    print("="*70)
    print("\nModel: account.move (invoice)")
    print("Field: payment_state")
    print("Type: Stored field (but readonly)")
    print("Values: 'not_paid', 'in_payment', 'paid', 'partial', 'reversed'")
    print("\nHOW TO CHANGE IT:")
    print("  payment_state is readonly - cannot be directly written")
    print("  It's updated automatically when:")
    print("  1. Invoice is fully reconciled (amount_residual = 0)")
    print("  2. Odoo recalculates payment_state based on reconciliation")
    print("\nSOLUTION:")
    print("  Reconcile the payment with the invoice")
    print("  When amount_residual becomes 0, payment_state should become 'paid'")
    print("="*70)
    
    find_and_fix()
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Use 'Apply Payment to Invoice' action (ID: 677) on the payment")
    print("2. OR manually reconcile in Odoo:")
    print("   - Go to invoice")
    print("   - Click 'Payment' smart button")
    print("   - Select payment line")
    print("   - Click 'Reconcile'")
    print("3. After reconciliation, payment_state should update to 'paid'")
    print("="*70)

