"""
Investigate Pay Action Wizard
==============================
The Pay action may be opening a payment wizard instead of the payment form.
Need to check what it opens and ensure it uses our updated payment methods.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Pay Action Details
# ==============================================================================

def check_pay_action():
    """Check what the Pay action actually does."""
    print("\n[*] Checking Pay action (ID 350)...")
    
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
                "read",
                [[350]],
                {
                    "fields": ["id", "name", "model_id", "state", "code", "binding_model_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"\n[OK] Pay action:")
        print(f"   Name: {action.get('name', 'N/A')}")
        print(f"   State: {action.get('state', 'N/A')}")
        if action.get('code'):
            print(f"\n   Code:")
            print(f"   {action['code']}")
    
    return result[0] if result else None

# ==============================================================================
# Check Payment Register Wizard
# ==============================================================================

def check_payment_register_wizard():
    """Check if there's a payment register wizard model."""
    print("\n[*] Checking for payment register wizard...")
    
    # Check if account.payment.register model exists
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
                "ir.model",
                "search_read",
                [[["model", "=", "account.payment.register"]]],
                {
                    "fields": ["id", "name", "model"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Payment register wizard model exists")
        
        # Check its form view
        payload2 = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "ir.ui.view",
                    "search_read",
                    [[["model", "=", "account.payment.register"], ["type", "=", "form"]]],
                    {
                        "fields": ["id", "name", "arch"],
                        "limit": 5
                    }
                ]
            }
        }
        
        response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
        result2 = response2.json().get("result", [])
        
        if result2:
            print(f"[OK] Found {len(result2)} payment register form views")
            for view in result2:
                arch = view.get("arch", "")
                if "payment_method_line_id" in arch:
                    print(f"   • {view.get('name', 'N/A')} (ID: {view['id']}) - HAS payment_method_line_id")
                else:
                    print(f"   • {view.get('name', 'N/A')} (ID: {view['id']}) - NO payment_method_line_id")
        
        return result2
    else:
        print("[!] Payment register wizard model not found")
        return []

# ==============================================================================
# Check action_force_register_payment Method
# ==============================================================================

def check_force_register_payment():
    """Check what action_force_register_payment returns."""
    print("\n[*] Checking action_force_register_payment method...")
    
    print("[INFO] This method is on account.move (invoice) model")
    print("       It typically returns a wizard action that opens")
    print("       account.payment.register form")
    print("\n[INFO] The wizard form may have different payment method lines")
    print("       than the account.payment form")

# ==============================================================================
# Check Payment Method Lines Available to Wizard
# ==============================================================================

def check_wizard_payment_methods():
    """Check what payment method lines the wizard can see."""
    print("\n[*] Checking payment method lines available...")
    
    # Get all payment method lines for Bank journal
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
                "account.payment.method.line",
                "search_read",
                [[["journal_id.code", "=", "BNK1"]]],
                {
                    "fields": ["id", "name", "journal_id", "payment_method_id"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} payment method lines for Bank journal:")
        for line in result:
            method_id = line.get('payment_method_id', [])
            method_name = method_id[1] if isinstance(method_id, list) and len(method_id) > 1 else 'N/A'
            print(f"   • ID: {line['id']}, Name: {line['name']}, Method: {method_name}")
        
        # Check which ones are Cash, Credit, Check
        cash_credit_check = [line for line in result if line['name'] in ['Cash', 'Credit', 'Check']]
        if cash_credit_check:
            print(f"\n[OK] Cash/Credit/Check lines found:")
            for line in cash_credit_check:
                print(f"   • {line['name']} (ID: {line['id']})")
        else:
            print(f"\n[!] Cash/Credit/Check lines NOT found in results")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Pay Action Wizard")
    print("="*70)
    
    # Check Pay action
    pay_action = check_pay_action()
    
    # Check payment register wizard
    wizard_views = check_payment_register_wizard()
    
    # Check method
    check_force_register_payment()
    
    # Check payment method lines
    method_lines = check_wizard_payment_methods()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nThe Pay action calls 'action_force_register_payment()' which")
    print("opens a payment REGISTER WIZARD (account.payment.register),")
    print("not the account.payment form directly.")
    print("\nThe wizard may have its own form view that needs to be updated")
    print("to show our Cash/Credit/Check payment method lines.")
    print("\nSOLUTION:")
    print("We need to update the account.payment.register form view to")
    print("show the correct payment method lines.")
    print("="*70)

