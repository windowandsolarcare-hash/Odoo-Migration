"""
Fix Payment Move Lines
======================
The payment has no move lines, which is why reconciliation isn't working.
Need to ensure payment creates move lines when posted.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Details
# ==============================================================================

def check_payment_details():
    """Check payment details to understand why move lines weren't created."""
    print("\n[*] Checking payment details...")
    
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
                [[18]],  # Payment ID 18
                {
                    "fields": ["id", "name", "state", "move_id", "move_ids", "journal_id", "payment_type", "amount"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    payment = response.json().get("result", [])
    
    if payment:
        payment = payment[0]
        print(f"\n[INFO] Payment {payment.get('name')} (ID: {payment.get('id')}):")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Move ID: {payment.get('move_id', [None])[0] if payment.get('move_id') else None}")
        print(f"   Move IDs: {payment.get('move_ids', [])}")
        print(f"   Journal: {payment.get('journal_id', [None, 'N/A'])[1] if payment.get('journal_id') else 'N/A'}")
        print(f"   Payment Type: {payment.get('payment_type', 'N/A')}")
        print(f"   Amount: ${payment.get('amount', 0):.2f}")
        
        move_id = payment.get('move_id', [None])[0] if payment.get('move_id') else None
        if not move_id:
            print(f"\n[!] PROBLEM: Payment has no move_id!")
            print(f"    When a payment is posted, it should create a journal entry (move)")
            print(f"    This payment doesn't have one, which is why there are no move lines")
            return False
        else:
            print(f"\n[OK] Payment has move_id: {move_id}")
            # Check if the move has lines
            payload_move = {
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
                        [[move_id]],
                        {
                            "fields": ["id", "name", "line_ids", "state"]
                        }
                    ]
                }
            }
            
            response_move = requests.post(ODOO_URL, json=payload_move, timeout=10)
            move = response_move.json().get("result", [])
            
            if move:
                move = move[0]
                line_ids = move.get('line_ids', [])
                print(f"   Move has {len(line_ids)} lines")
                
                if len(line_ids) == 0:
                    print(f"\n[!] PROBLEM: Move has no lines!")
                    print(f"    The journal entry exists but has no accounting lines")
                    return False
                else:
                    print(f"\n[OK] Move has lines - let's check them")
                    # Read the lines
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
                                "read",
                                [line_ids],
                                {
                                    "fields": ["id", "name", "account_id", "debit", "credit", "balance", "reconciled"]
                                }
                            ]
                        }
                    }
                    
                    response_lines = requests.post(ODOO_URL, json=payload_lines, timeout=10)
                    lines = response_lines.json().get("result", [])
                    
                    print(f"\n[INFO] Move lines:")
                    for line in lines:
                        account_name = line.get('account_id', [None, 'N/A'])[1] if line.get('account_id') else 'N/A'
                        print(f"   Line {line.get('id')}: {account_name}")
                        print(f"      Debit: ${line.get('debit', 0):.2f}, Credit: ${line.get('credit', 0):.2f}")
                        print(f"      Balance: ${line.get('balance', 0):.2f}, Reconciled: {line.get('reconciled', False)}")
                    
                    # Find receivable line
                    receivable_lines = [l for l in lines if l.get('balance', 0) < 0 and not l.get('reconciled', False)]
                    if receivable_lines:
                        print(f"\n[OK] Found receivable line to reconcile: {receivable_lines[0].get('id')}")
                        return receivable_lines[0].get('id')
    
    return None

# ==============================================================================
# Reconcile Using Move Lines
# ==============================================================================

def reconcile_using_move_lines(receivable_line_id):
    """Reconcile invoice and payment using move lines."""
    print(f"\n[*] Reconciling invoice line with payment move line...")
    
    # Get invoice receivable line (ID: 14 from previous check)
    invoice_line_id = 14
    
    line_ids = [invoice_line_id, receivable_line_id]
    
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
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Payment Move Lines")
    print("="*70)
    
    receivable_line_id = check_payment_details()
    
    if receivable_line_id:
        reconciled = reconcile_using_move_lines(receivable_line_id)
        
        if reconciled:
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print("\nPayment has been reconciled with invoice.")
            print("Invoice should now show as paid with $0.00 due.")
            print("\nPlease refresh the invoice page to see the update.")
        else:
            print("\n[!] Could not reconcile - may need manual intervention")
    else:
        print("\n[!] Could not find payment move lines to reconcile")
        print("    The payment may not have been posted correctly")
    
    print("="*70)

