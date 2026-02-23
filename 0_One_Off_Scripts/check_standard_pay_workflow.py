"""
Check Standard Pay Workflow
============================
Find the standard Pay action and document the workflow.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Find Standard Pay Action
# ==============================================================================

def find_standard_pay_action():
    """Find the standard Pay action on account.move."""
    print("\n[*] Finding standard Pay action...")
    
    # Check window actions
    payload_window = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.actions.act_window",
                "search_read",
                [[["name", "ilike", "Pay"], ["res_model", "=", "account.payment.register"]]],
                {
                    "fields": ["id", "name", "res_model", "binding_model_id", "binding_view_types"]
                }
            ]
        }
    }
    
    response_window = requests.post(ODOO_URL, json=payload_window, timeout=10)
    window_actions = response_window.json().get("result", [])
    
    if window_actions:
        print(f"\n[OK] Found window action(s):")
        for action in window_actions:
            print(f"   {action.get('name')} (ID: {action.get('id')})")
            print(f"      Model: {action.get('res_model', 'N/A')}")
            print(f"      Binding: {action.get('binding_model_id', [None, 'N/A'])[1] if action.get('binding_model_id') else 'N/A'}")
    
    # Check server actions
    payload_server = {
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
                [[["name", "ilike", "Pay"], ["binding_model_id.model", "=", "account.move"]]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types", "active"]
                }
            ]
        }
    }
    
    response_server = requests.post(ODOO_URL, json=payload_server, timeout=10)
    server_actions = response_server.json().get("result", [])
    
    if server_actions:
        print(f"\n[OK] Found server action(s):")
        for action in server_actions:
            print(f"   {action.get('name')} (ID: {action.get('id')})")
            print(f"      Active: {action.get('active', True)}")
            print(f"      View Types: {action.get('binding_view_types', 'N/A')}")
    
    # Check for action_force_register_payment method
    # This is what the standard Pay button calls
    print(f"\n[INFO] Standard Pay button typically calls:")
    print(f"       action_force_register_payment() method on account.move")
    print(f"       This opens the payment register wizard")
    
    return window_actions, server_actions

# ==============================================================================
# Check Payment Register Wizard
# ==============================================================================

def check_payment_register_wizard():
    """Check the payment register wizard."""
    print("\n[*] Checking payment register wizard...")
    
    # Check if model exists
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
                    "fields": ["id", "name", "model"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    model = response.json().get("result", [])
    
    if model:
        print(f"[OK] Payment register wizard model exists")
        print(f"     Model: {model[0].get('model', 'N/A')}")
        print(f"\n[INFO] The payment register wizard:")
        print(f"       - Collects payment information")
        print(f"       - Has action_create_payments() method")
        print(f"       - Creates payment, posts it, and reconciles automatically")
        return True
    else:
        print(f"[!] Payment register wizard model not found")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Standard Pay Workflow")
    print("="*70)
    
    window_actions, server_actions = find_standard_pay_action()
    wizard_exists = check_payment_register_wizard()
    
    print("\n" + "="*70)
    print("STANDARD ODOO PAYMENT WORKFLOW:")
    print("="*70)
    print("\nSTEP 1: Create Invoice from Sales Order")
    print("  - Go to Sales Order")
    print("  - Click 'Create Invoice' button")
    print("  - Select 'Regular Invoice'")
    print("  - Invoice created in draft")
    print("\nSTEP 2: Confirm Invoice")
    print("  - On invoice, click 'Confirm' button")
    print("  - Invoice moves to 'Posted' state")
    print("  - Payment state: 'Not Paid'")
    print("\nSTEP 3: Pay Invoice (STANDARD WORKFLOW)")
    print("  - On invoice, click 'Pay' button")
    print("  - Payment register wizard opens")
    print("  - Fill in:")
    print("    * Journal: Bank")
    print("    * Payment Method: (select from available methods)")
    print("    * Amount: (pre-filled with invoice amount)")
    print("    * Payment Date: (defaults to today)")
    print("  - Click 'Create Payment' button")
    print("  - Payment is:")
    print("    * Created")
    print("    * Posted (creates move and move lines)")
    print("    * Reconciled with invoice automatically")
    print("  - Invoice should show:")
    print("    * Payment state: 'Paid'")
    print("    * Amount due: $0.00")
    print("\nNOTE: The 'Create Payment' button in the wizard does everything")
    print("      in one step - no need to click Confirm then Validate")
    print("="*70)
    print("\nREADY TO TEST:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Create a new invoice from a Sales Order")
    print("3. Confirm the invoice")
    print("4. Click 'Pay' button")
    print("5. Use the payment register wizard")
    print("6. Click 'Create Payment'")
    print("7. Invoice should show as 'Paid'")
    print("="*70)

