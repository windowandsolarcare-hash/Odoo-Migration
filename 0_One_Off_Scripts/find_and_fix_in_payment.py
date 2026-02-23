"""
Find and Fix In Payment Status
===============================
Find invoices stuck in "in_payment" and fix them by reconciling.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Find Invoices in "In Payment" Status
# ==============================================================================

def find_in_payment_invoices():
    """Find all invoices stuck in 'in_payment' status."""
    print("\n[*] Finding invoices in 'in_payment' status...")
    
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
                    "fields": ["id", "name", "payment_state", "amount_residual", "amount_total", "state"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    invoices = response.json().get("result", [])
    
    print(f"\n[INFO] Found {len(invoices)} invoice(s) in 'in_payment' status:")
    for invoice in invoices:
        print(f"\n   Invoice {invoice.get('name')} (ID: {invoice.get('id')}):")
        print(f"      Payment State: {invoice.get('payment_state', 'N/A')}")
        print(f"      Amount Total: ${invoice.get('amount_total', 0):.2f}")
        print(f"      Amount Residual: ${invoice.get('amount_residual', 0):.2f}")
        print(f"      State: {invoice.get('state', 'N/A')}")
    
    return invoices

# ==============================================================================
# Check Payment State Field
# ==============================================================================

def check_payment_state_field():
    """Check the payment_state field definition."""
    print("\n[*] Checking payment_state field definition...")
    
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
                "ir.model.fields",
                "search_read",
                [[["model", "=", "account.move"], ["name", "=", "payment_state"]]],
                {
                    "fields": ["id", "name", "field_description", "ttype", "compute", "store", "readonly"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    field = response.json().get("result", [])
    
    if field:
        field = field[0]
        print(f"\n[OK] payment_state field:")
        print(f"   Description: {field.get('field_description', 'N/A')}")
        print(f"   Type: {field.get('ttype', 'N/A')}")
        print(f"   Compute: {field.get('compute', 'N/A')}")
        print(f"   Store: {field.get('store', False)}")
        print(f"   Readonly: {field.get('readonly', False)}")
        
        if field.get('compute'):
            print(f"\n[INFO] payment_state is a COMPUTED field")
            print(f"       It's automatically calculated based on:")
            print(f"       - amount_residual (if 0, then 'paid')")
            print(f"       - Reconciliation status")
            print(f"       - Cannot be directly written")
    
    return field[0] if field else None

# ==============================================================================
# Reconcile Invoice to Fix Payment State
# ==============================================================================

def reconcile_invoice(invoice_id):
    """Reconcile invoice to fix payment_state."""
    print(f"\n[*] Reconciling invoice {invoice_id}...")
    
    # Get invoice receivable lines
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
                [[["move_id", "=", invoice_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", ">", 0]]],
                {
                    "fields": ["id", "balance", "account_id"]
                }
            ]
        }
    }
    
    response_lines = requests.post(ODOO_URL, json=payload_lines, timeout=10)
    invoice_lines = response_lines.json().get("result", [])
    
    print(f"[INFO] Invoice receivable lines: {len(invoice_lines)}")
    
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
                    "fields": ["id", "name", "state", "move_id", "amount"]
                }
            ]
        }
    }
    
    response_payments = requests.post(ODOO_URL, json=payload_payments, timeout=10)
    payments = response_payments.json().get("result", [])
    
    print(f"[INFO] Linked payments: {len(payments)}")
    
    for payment in payments:
        print(f"   Payment {payment.get('name')} (ID: {payment.get('id')}): State: {payment.get('state', 'N/A')}")
        
        move_id = payment.get('move_id', [None])[0] if payment.get('move_id') else None
        if move_id:
            # Get payment receivable lines
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
                        [[["move_id", "=", move_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", "<", 0]]],
                        {
                            "fields": ["id", "balance"]
                        }
                    ]
                }
            }
            
            response_payment_lines = requests.post(ODOO_URL, json=payload_payment_lines, timeout=10)
            payment_lines = response_payment_lines.json().get("result", [])
            
            print(f"      Payment receivable lines: {len(payment_lines)}")
            
            # Reconcile if we have matching lines
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
                    print(f"      [OK] Reconciled!")
                    return True
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIND AND FIX: In Payment Status")
    print("="*70)
    
    # Check field definition
    field_info = check_payment_state_field()
    
    # Find invoices in in_payment
    invoices = find_in_payment_invoices()
    
    print("\n" + "="*70)
    print("WHERE 'IN PAYMENT' LIVES:")
    print("="*70)
    print("\nField: payment_state on account.move (invoice model)")
    print("Type: Computed field (automatically calculated)")
    print("Possible Values:")
    print("  - 'not_paid': Invoice not paid")
    print("  - 'in_payment': Payment registered but not fully reconciled")
    print("  - 'paid': Fully paid (amount_residual = 0)")
    print("  - 'partial': Partially paid")
    print("  - 'reversed': Reversed")
    print("\nHOW IT'S CALCULATED:")
    print("  - Based on amount_residual (if 0, then 'paid')")
    print("  - Based on reconciliation status")
    print("  - Cannot be directly written (it's computed)")
    print("\nHOW TO FIX 'IN PAYMENT':")
    print("  1. Fully reconcile the invoice receivable line with payment")
    print("  2. When amount_residual becomes 0, payment_state becomes 'paid'")
    print("  3. Use 'Apply Payment to Invoice' action to reconcile")
    
    # Try to reconcile invoices
    if invoices:
        print(f"\n[*] Attempting to reconcile {len(invoices)} invoice(s)...")
        for invoice in invoices:
            invoice_id = invoice.get('id')
            reconciled = reconcile_invoice(invoice_id)
            
            if reconciled:
                print(f"\n[OK] Invoice {invoice.get('name')} should now show as 'paid'")
                print(f"     Please refresh the invoice page")
            else:
                print(f"\n[!] Could not automatically reconcile invoice {invoice.get('name')}")
                print(f"     Use 'Apply Payment to Invoice' action manually")
    
    print("="*70)

