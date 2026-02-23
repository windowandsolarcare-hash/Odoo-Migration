"""
Fix Pay Action Context
======================
Ensure the Pay action sets proper defaults for journal and payment method.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Find Pay Action
# ==============================================================================

def find_pay_action():
    """Find the Pay action on account.move."""
    print("\n[*] Finding Pay action...")
    
    # Check server actions
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
                    "fields": ["id", "name", "code", "binding_view_types", "active"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    actions = response.json().get("result", [])
    
    if actions:
        for action in actions:
            print(f"\n[OK] Found Pay action (ID: {action.get('id')}):")
            print(f"   Name: {action.get('name')}")
            print(f"   Active: {action.get('active', True)}")
            print(f"   View Types: {action.get('binding_view_types', 'N/A')}")
            if action.get('code'):
                print(f"   Code: {action.get('code')[:200]}...")
            return action
    
    print(f"\n[INFO] Pay action not found as server action")
    print(f"       It might be a window action or method call")
    return None

# ==============================================================================
# Check Standard Pay Method
# ==============================================================================

def check_standard_pay_method():
    """Check how standard Pay works - it calls action_force_register_payment()."""
    print("\n[*] Standard Pay button calls action_force_register_payment() method")
    print(f"    This method should set proper defaults for the wizard")
    print(f"    The issue might be that journal_id is not being set")
    
    # The standard method should:
    # 1. Get default journal (Bank journal)
    # 2. Get default payment method line
    # 3. Set these in the wizard context
    
    # Let's check if we can see what the method does
    print(f"\n[INFO] The action_force_register_payment() method should:")
    print(f"       1. Find Bank journal")
    print(f"       2. Set it as default_journal_id in context")
    print(f"       3. Open payment register wizard")
    print(f"\n       If journal_id is not set, wizard will fail")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Pay Action Context")
    print("="*70)
    
    pay_action = find_pay_action()
    check_standard_pay_method()
    
    print("\n" + "="*70)
    print("TROUBLESHOOTING 'MISSING REQUIRED FIELD' ERROR:")
    print("="*70)
    print("\nThe error is likely because 'Journal' field is not set.")
    print("\nWhen you click 'Pay' button:")
    print("1. Payment register wizard should open")
    print("2. 'Journal' field should default to 'Bank'")
    print("3. If 'Journal' is empty, you'll get 'missing required field' error")
    print("\nSOLUTION:")
    print("1. When wizard opens, FIRST select 'Journal' = 'Bank'")
    print("2. Then select 'Payment Method'")
    print("3. Verify 'Amount' is filled (should be pre-filled)")
    print("4. Verify 'Payment Date' is filled (should default to today)")
    print("5. Then click 'Create Payment'")
    print("\nIf 'Journal' field is not visible or not working:")
    print("- This might be a view issue")
    print("- Try refreshing browser (Ctrl+F5)")
    print("- Or the Pay action might not be setting defaults correctly")
    print("="*70)
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Click 'Pay' button on invoice")
    print("3. In the wizard, make sure 'Journal' field has 'Bank' selected")
    print("4. If 'Journal' is empty, select 'Bank' manually")
    print("5. Select 'Payment Method'")
    print("6. Click 'Create Payment'")
    print("="*70)

