"""
Deep Dive Reconciliation
=========================
Check all move lines to understand why reconciliation isn't working.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check All Move Lines
# ==============================================================================

def check_all_move_lines():
    """Check all move lines for payment and invoice."""
    print("\n[*] Checking all move lines...")
    
    # Get invoice move lines
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
                [[["move_id", "=", 11]]],  # Invoice ID 11
                {
                    "fields": ["id", "name", "account_id", "debit", "credit", "balance", "reconciled", "full_reconcile_id", "matched_debit_ids", "matched_credit_ids"]
                }
            ]
        }
    }
    
    response_invoice = requests.post(ODOO_URL, json=payload_invoice, timeout=10)
    invoice_lines = response_invoice.json().get("result", [])
    
    print(f"\n[INFO] Invoice (ID: 11) move lines: {len(invoice_lines)}")
    for line in invoice_lines:
        account_name = line.get('account_id', [None, 'N/A'])[1] if line.get('account_id') else 'N/A'
        print(f"   Line {line.get('id')}: {line.get('name', 'N/A')[:50]}")
        print(f"      Account: {account_name}")
        print(f"      Debit: ${line.get('debit', 0):.2f}, Credit: ${line.get('credit', 0):.2f}, Balance: ${line.get('balance', 0):.2f}")
        print(f"      Reconciled: {line.get('reconciled', False)}")
        if line.get('full_reconcile_id'):
            print(f"      Full Reconcile ID: {line.get('full_reconcile_id', [None])[0]}")
        if line.get('matched_debit_ids'):
            print(f"      Matched Debits: {line.get('matched_debit_ids', [])}")
        if line.get('matched_credit_ids'):
            print(f"      Matched Credits: {line.get('matched_credit_ids', [])}")
    
    # Get payment move lines
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
                [[["payment_id", "=", 18]]],  # Payment ID 18
                {
                    "fields": ["id", "name", "account_id", "debit", "credit", "balance", "reconciled", "full_reconcile_id", "matched_debit_ids", "matched_credit_ids"]
                }
            ]
        }
    }
    
    response_payment = requests.post(ODOO_URL, json=payload_payment, timeout=10)
    payment_lines = response_payment.json().get("result", [])
    
    print(f"\n[INFO] Payment (ID: 18) move lines: {len(payment_lines)}")
    for line in payment_lines:
        account_name = line.get('account_id', [None, 'N/A'])[1] if line.get('account_id') else 'N/A'
        print(f"   Line {line.get('id')}: {line.get('name', 'N/A')[:50]}")
        print(f"      Account: {account_name}")
        print(f"      Debit: ${line.get('debit', 0):.2f}, Credit: ${line.get('credit', 0):.2f}, Balance: ${line.get('balance', 0):.2f}")
        print(f"      Reconciled: {line.get('reconciled', False)}")
        if line.get('full_reconcile_id'):
            print(f"      Full Reconcile ID: {line.get('full_reconcile_id', [None])[0]}")
        if line.get('matched_debit_ids'):
            print(f"      Matched Debits: {line.get('matched_debit_ids', [])}")
        if line.get('matched_credit_ids'):
            print(f"      Matched Credits: {line.get('matched_credit_ids', [])}")
    
    # Find receivable lines that should be reconciled
    invoice_receivable = [l for l in invoice_lines if l.get('balance', 0) > 0 and not l.get('reconciled', False)]
    payment_receivable = [l for l in payment_lines if l.get('balance', 0) < 0 and not l.get('reconciled', False)]
    
    print(f"\n[INFO] Unreconciled receivable lines:")
    print(f"   Invoice receivable (positive balance): {len(invoice_receivable)}")
    print(f"   Payment receivable (negative balance): {len(payment_receivable)}")
    
    if invoice_receivable and payment_receivable:
        print(f"\n[*] Found lines to reconcile!")
        invoice_line_id = invoice_receivable[0].get('id')
        payment_line_id = payment_receivable[0].get('id')
        
        print(f"   Invoice line ID: {invoice_line_id}")
        print(f"   Payment line ID: {payment_line_id}")
        
        # Try to reconcile
        line_ids = [invoice_line_id, payment_line_id]
        
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
            print(f"\n[OK] Reconciliation successful!")
            return True
        else:
            error = response_reconcile.json().get("error", {})
            print(f"\n[!] Reconciliation failed: {error}")
            return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("DEEP DIVE: Reconciliation Issue")
    print("="*70)
    
    reconciled = check_all_move_lines()
    
    if reconciled:
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print("\nPayment has been reconciled with invoice.")
        print("Please refresh the invoice page - it should show as paid.")
    else:
        print("\n" + "="*70)
        print("ANALYSIS:")
        print("="*70)
        print("\nThe payment register wizard should have reconciled automatically,")
        print("but it didn't. This might be because:")
        print("1. The wizard didn't complete the reconciliation step")
        print("2. There's a timing issue")
        print("3. The payment lines weren't created correctly")
        print("\nWe may need to ensure the payment register wizard completes")
        print("the full reconciliation process, or manually reconcile after posting.")
    print("="*70)

