"""
Fix Invoice Reconciliation
==========================
The payment is posted but invoice isn't reconciled.
Need to manually reconcile the payment with the invoice.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment and Invoice Status
# ==============================================================================

def check_payment_invoice_status():
    """Check the current status of payment and invoice."""
    print("\n[*] Checking payment and invoice status...")
    
    # Find the most recent payment (PAY00008)
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
                "account.payment",
                "search_read",
                [[["name", "=", "PAY00008"]]],
                {
                    "fields": ["id", "name", "amount", "state", "invoice_ids", "reconciled_invoice_ids", "partner_id"]
                }
            ]
        }
    }
    
    response_payment = requests.post(ODOO_URL, json=payload_payment, timeout=10)
    payment_result = response_payment.json().get("result", [])
    
    if payment_result:
        payment = payment_result[0]
        print(f"\n[OK] Payment {payment.get('name')} (ID: {payment.get('id')}):")
        print(f"   Amount: ${payment.get('amount', 0):.2f}")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Linked Invoices: {payment.get('invoice_ids', [])}")
        print(f"   Reconciled Invoices: {payment.get('reconciled_invoice_ids', [])}")
        
        invoice_ids = payment.get("invoice_ids", [])
        if invoice_ids:
            # Check invoice status
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
                            "fields": ["id", "name", "amount_residual", "amount_total", "payment_state", "state"]
                        }
                    ]
                }
            }
            
            response_invoice = requests.post(ODOO_URL, json=payload_invoice, timeout=10)
            invoice_result = response_invoice.json().get("result", [])
            
            if invoice_result:
                invoice = invoice_result[0]
                print(f"\n[INFO] Invoice {invoice.get('name')} (ID: {invoice.get('id')}):")
                print(f"   Amount Total: ${invoice.get('amount_total', 0):.2f}")
                print(f"   Amount Residual: ${invoice.get('amount_residual', 0):.2f}")
                print(f"   Payment State: {invoice.get('payment_state', 'N/A')}")
                print(f"   State: {invoice.get('state', 'N/A')}")
                
                if invoice.get('amount_residual', 0) > 0:
                    print(f"\n[!] PROBLEM: Invoice still has ${invoice.get('amount_residual', 0):.2f} due")
                    print(f"    Payment is posted but not reconciled!")
                    return payment.get('id'), invoice.get('id')
    
    return None, None

# ==============================================================================
# Reconcile Payment with Invoice
# ==============================================================================

def reconcile_payment_invoice(payment_id, invoice_id):
    """Manually reconcile the payment with the invoice."""
    print(f"\n[*] Attempting to reconcile payment {payment_id} with invoice {invoice_id}...")
    
    # Method 1: Use the invoice's reconciliation method
    # The payment register wizard calls action_create_payments() which does this
    
    # Get payment lines and invoice lines
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
                    "fields": ["id", "name", "debit", "credit", "balance", "account_id", "reconciled"]
                }
            ]
        }
    }
    
    response_lines = requests.post(ODOO_URL, json=payload_lines, timeout=10)
    invoice_lines = response_lines.json().get("result", [])
    
    print(f"\n[INFO] Invoice receivable lines: {len(invoice_lines)}")
    for line in invoice_lines:
        print(f"   Line {line.get('id')}: Balance ${line.get('balance', 0):.2f}")
    
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
                [[["payment_id", "=", payment_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False]]],
                {
                    "fields": ["id", "name", "debit", "credit", "balance", "account_id", "reconciled"]
                }
            ]
        }
    }
    
    response_payment_lines = requests.post(ODOO_URL, json=payload_payment_lines, timeout=10)
    payment_lines = response_payment_lines.json().get("result", [])
    
    print(f"\n[INFO] Payment receivable lines: {len(payment_lines)}")
    for line in payment_lines:
        print(f"   Line {line.get('id')}: Balance ${line.get('balance', 0):.2f}")
    
    # Reconcile the lines
    if invoice_lines and payment_lines:
        line_ids = [line.get('id') for line in invoice_lines + payment_lines]
        
        print(f"\n[*] Reconciling {len(line_ids)} lines...")
        
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
            print(f"[OK] Reconciliation successful!")
            return True
        else:
            error = response_reconcile.json().get("error", {})
            print(f"[!] Reconciliation failed: {error}")
            
            # Try alternative method - use the payment's reconcile method
            print(f"\n[*] Trying alternative reconciliation method...")
            
            # Use the payment's action_post() which should trigger reconciliation
            # But since it's already posted, we need to manually reconcile
            
            # Try using the invoice's js_assign_outstanding_line method
            # This is what the payment register wizard does
            
            return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Invoice Reconciliation")
    print("="*70)
    
    # Check status
    payment_id, invoice_id = check_payment_invoice_status()
    
    if payment_id and invoice_id:
        # Reconcile
        reconciled = reconcile_payment_invoice(payment_id, invoice_id)
        
        if reconciled:
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print("\nPayment has been reconciled with invoice.")
            print("Invoice should now show as paid with $0.00 due.")
            print("\nPlease refresh the invoice page to see the update.")
        else:
            print("\n" + "="*70)
            print("NEED MANUAL RECONCILIATION")
            print("="*70)
            print("\nThe automatic reconciliation didn't work.")
            print("\nYou can manually reconcile in Odoo:")
            print("1. Go to the invoice")
            print("2. Click on the 'Payment' smart button")
            print("3. Select the payment line")
            print("4. Click 'Reconcile' button")
            print("\nOR we can create a server action to do this automatically.")
    else:
        print("\n[!] Could not find payment or invoice to reconcile")
    
    print("="*70)

