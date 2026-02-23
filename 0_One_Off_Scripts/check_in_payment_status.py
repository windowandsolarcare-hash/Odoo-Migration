"""
Check In Payment Status
=======================
Find where "In Payment" status lives and how to change it to "Paid".
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Invoice Payment State
# ==============================================================================

def check_invoice_payment_state():
    """Check the invoice's payment_state field."""
    print("\n[*] Checking invoice payment state...")
    
    # Get invoice INV/2026/00001 (ID: 11)
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
                "read",
                [[11]],  # Invoice ID 11
                {
                    "fields": ["id", "name", "payment_state", "amount_residual", "amount_total", "line_ids"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    invoice = response.json().get("result", [])
    
    if invoice:
        invoice = invoice[0]
        print(f"\n[OK] Invoice {invoice.get('name')} (ID: {invoice.get('id')}):")
        print(f"   Payment State: {invoice.get('payment_state', 'N/A')}")
        print(f"   Amount Total: ${invoice.get('amount_total', 0):.2f}")
        print(f"   Amount Residual: ${invoice.get('amount_residual', 0):.2f}")
        
        # Check if payment_state is computed or stored
        # payment_state is typically a computed field based on reconciliation
        
        # Get the field definition
        payload_field = {
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
                        "fields": ["id", "name", "field_description", "ttype", "compute", "store"]
                    }
                ]
            }
        }
        
        response_field = requests.post(ODOO_URL, json=payload_field, timeout=10)
        field_result = response_field.json().get("result", [])
        
        if field_result:
            field = field_result[0]
            print(f"\n[INFO] payment_state field:")
            print(f"   Type: {field.get('ttype', 'N/A')}")
            print(f"   Compute: {field.get('compute', 'N/A')}")
            print(f"   Store: {field.get('store', False)}")
            
            if field.get('compute'):
                print(f"\n[INFO] payment_state is a COMPUTED field")
                print(f"       It's calculated based on reconciliation status")
                print(f"       Cannot be directly written - must reconcile to change it")
        
        # Check reconciliation status
        line_ids = invoice.get('line_ids', [])
        if line_ids:
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
                            "fields": ["id", "account_id", "reconciled", "full_reconcile_id", "balance"]
                        }
                    ]
                }
            }
            
            response_lines = requests.post(ODOO_URL, json=payload_lines, timeout=10)
            lines = response_lines.json().get("result", [])
            
            receivable_lines = [l for l in lines if l.get('account_id') and 'receivable' in str(l.get('account_id', [None, ''])[1]).lower()]
            
            print(f"\n[INFO] Receivable lines: {len(receivable_lines)}")
            for line in receivable_lines:
                print(f"   Line {line.get('id')}: Reconciled: {line.get('reconciled', False)}, Balance: ${line.get('balance', 0):.2f}")
                if line.get('full_reconcile_id'):
                    print(f"      Full Reconcile ID: {line.get('full_reconcile_id', [None])[0]}")
        
        return invoice.get('payment_state'), invoice.get('amount_residual', 0)
    
    return None, None

# ==============================================================================
# Force Update Payment State
# ==============================================================================

def force_update_payment_state():
    """Try to force update payment_state (may not work if computed)."""
    print("\n[*] Attempting to force update payment_state...")
    
    # Try to write payment_state directly
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
                "write",
                [[11], {
                    "payment_state": "paid"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Attempted to write payment_state")
        # Check if it worked
        payload_check = {
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
                    [[11]],
                    {
                        "fields": ["payment_state"]
                    }
                ]
            }
        }
        
        response_check = requests.post(ODOO_URL, json=payload_check, timeout=10)
        invoice_check = response_check.json().get("result", [])
        
        if invoice_check:
            print(f"   Current payment_state: {invoice_check[0].get('payment_state', 'N/A')}")
            if invoice_check[0].get('payment_state') == 'paid':
                print(f"   [OK] Successfully changed to 'paid'")
                return True
            else:
                print(f"   [!] Still shows as '{invoice_check[0].get('payment_state', 'N/A')}'")
                print(f"       payment_state is computed - cannot be directly written")
                return False
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: In Payment Status")
    print("="*70)
    
    payment_state, amount_residual = check_invoice_payment_state()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print(f"\nCurrent Status:")
    print(f"   Payment State: {payment_state}")
    print(f"   Amount Residual: ${amount_residual:.2f}")
    print(f"\nWhere 'In Payment' Lives:")
    print(f"   Field: payment_state on account.move (invoice)")
    print(f"   Type: Computed field (calculated automatically)")
    print(f"   Values: 'not_paid', 'in_payment', 'paid', 'partial', 'reversed'")
    print(f"\nHow to Change It:")
    print(f"   payment_state is COMPUTED based on reconciliation")
    print(f"   To change from 'in_payment' to 'paid':")
    print(f"   1. Fully reconcile the invoice receivable line with payment")
    print(f"   2. When amount_residual = 0, payment_state should become 'paid'")
    print(f"   3. Cannot directly write payment_state (it's computed)")
    
    if amount_residual > 0:
        print(f"\n[!] PROBLEM: Amount residual is ${amount_residual:.2f}")
        print(f"    This is why payment_state is 'in_payment' instead of 'paid'")
        print(f"    Need to reconcile payment to reduce amount_residual to $0.00")
    
    # Try to force update (will likely fail if computed)
    print(f"\n[*] Attempting to force update (will likely fail if computed)...")
    updated = force_update_payment_state()
    
    if not updated:
        print(f"\n[!] Cannot directly write payment_state - it's computed")
        print(f"    SOLUTION: Reconcile the payment with invoice")
        print(f"    Use 'Apply Payment to Invoice' action (ID: 677)")
        print(f"    OR ensure payment is fully reconciled")
    
    print("="*70)

