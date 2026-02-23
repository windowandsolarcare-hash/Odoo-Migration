"""
Reset to Odoo Original State
============================
Disable/comment out all customizations and restore Odoo's original workflow.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# List of Customizations Made
# ==============================================================================

CUSTOMIZATIONS = {
    "server_actions": [
        {"id": 674, "name": "Collect Payment", "action": "disable"},
        {"id": 675, "name": "Post Payment", "action": "disable"},
        {"id": 677, "name": "Apply Payment to Invoice", "action": "disable"},
    ],
    "view_inheritances": [
        {"id": 2450, "name": "Memo field after payment method", "action": "disable"},
        {"id": 2403, "name": "Check number field on payment form", "action": "check"},  # May not exist
        {"id": 2404, "name": "Currency field on payment form", "action": "check"},
        {"id": 2406, "name": "Payment method domain override", "action": "check"},
    ],
    "payment_method_lines": [
        # We renamed existing ones, may need to restore
    ]
}

# ==============================================================================
# Disable Server Actions
# ==============================================================================

def disable_server_actions():
    """Disable all custom server actions."""
    print("\n[*] Disabling custom server actions...")
    
    disabled = []
    for action in CUSTOMIZATIONS["server_actions"]:
        action_id = action["id"]
        action_name = action["name"]
        
        # Read current action
        payload_read = {
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
                    [[action_id]],
                    {
                        "fields": ["id", "name", "active", "code"]
                    }
                ]
            }
        }
        
        response_read = requests.post(ODOO_URL, json=payload_read, timeout=10)
        action_data = response_read.json().get("result", [])
        
        if action_data:
            current_code = action_data[0].get("code", "")
            
            # Comment out the code
            commented_code = f"# DISABLED - Original Odoo workflow restored\n# {current_code.replace(chr(10), chr(10) + '# ')}"
            
            # Disable the action
            payload_disable = {
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
                        "write",
                        [[action_id], {
                            "active": False,
                            "code": commented_code
                        }]
                    ]
                }
            }
            
            response_disable = requests.post(ODOO_URL, json=payload_disable, timeout=10)
            result = response_disable.json().get("result")
            
            if result:
                print(f"   [OK] Disabled: {action_name} (ID: {action_id})")
                disabled.append(action_id)
            else:
                error = response_disable.json().get("error", {})
                print(f"   [!] Failed to disable {action_name}: {error}")
        else:
            print(f"   [INFO] Action {action_name} (ID: {action_id}) not found")
    
    return disabled

# ==============================================================================
# Disable View Inheritances
# ==============================================================================

def disable_view_inheritances():
    """Disable custom view inheritances."""
    print("\n[*] Disabling custom view inheritances...")
    
    disabled = []
    for view in CUSTOMIZATIONS["view_inheritances"]:
        view_id = view["id"]
        view_name = view["name"]
        
        # Try to read the view
        payload_read = {
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
                    "read",
                    [[view_id]],
                    {
                        "fields": ["id", "name", "active", "arch"]
                    }
                ]
            }
        }
        
        response_read = requests.post(ODOO_URL, json=payload_read, timeout=10)
        view_data = response_read.json().get("result", [])
        
        if view_data:
            # Disable the view
            payload_disable = {
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
                        "write",
                        [[view_id], {
                            "active": False
                        }]
                    ]
                }
            }
            
            response_disable = requests.post(ODOO_URL, json=payload_disable, timeout=10)
            result = response_disable.json().get("result")
            
            if result:
                print(f"   [OK] Disabled: {view_name} (ID: {view_id})")
                disabled.append(view_id)
            else:
                error = response_disable.json().get("error", {})
                print(f"   [!] Failed to disable {view_name}: {error}")
        else:
            print(f"   [INFO] View {view_name} (ID: {view_id}) not found")
    
    return disabled

# ==============================================================================
# Check Standard Pay Action
# ==============================================================================

def check_standard_pay_action():
    """Check if standard Pay action exists and is active."""
    print("\n[*] Checking standard Pay action...")
    
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
                    "fields": ["id", "name", "active", "binding_view_types"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    actions = response.json().get("result", [])
    
    if actions:
        for action in actions:
            print(f"   [OK] Found: {action.get('name')} (ID: {action.get('id')})")
            print(f"        Active: {action.get('active', True)}")
            print(f"        View Types: {action.get('binding_view_types', 'N/A')}")
        return True
    else:
        print(f"   [INFO] Standard Pay action not found (may be a window action)")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESET TO ODOO ORIGINAL STATE")
    print("="*70)
    
    print("\nThis will disable all customizations and restore Odoo's original workflow.")
    print("\nCustomizations being disabled:")
    print("  - Server Actions: Collect Payment, Post Payment, Apply Payment")
    print("  - View Inheritances: Memo field, Check number field, etc.")
    print("\nStandard Odoo workflow will be restored.")
    
    # Disable server actions
    disabled_actions = disable_server_actions()
    
    # Disable view inheritances
    disabled_views = disable_view_inheritances()
    
    # Check standard Pay action
    standard_pay_exists = check_standard_pay_action()
    
    print("\n" + "="*70)
    print("RESET COMPLETE")
    print("="*70)
    print(f"\nDisabled {len(disabled_actions)} server action(s)")
    print(f"Disabled {len(disabled_views)} view inheritance(s)")
    print("\nSTANDARD ODOO WORKFLOW:")
    print("="*70)
    print("\n1. Create Invoice from Sales Order:")
    print("   - Go to Sales Order")
    print("   - Click 'Create Invoice' (standard Odoo action)")
    print("   - Select invoice type (Regular Invoice)")
    print("   - Invoice is created in draft")
    print("\n2. Confirm Invoice:")
    print("   - Click 'Confirm' button on invoice")
    print("   - Invoice moves to 'Posted' state")
    print("\n3. Pay Invoice:")
    print("   - Click 'Pay' button on invoice (standard Odoo action)")
    print("   - Payment register wizard opens")
    print("   - Fill in payment details")
    print("   - Click 'Create Payment'")
    print("   - Payment is created, posted, and reconciled automatically")
    print("   - Invoice should show as 'Paid'")
    print("\nNEXT STEPS:")
    print("1. Refresh your browser (Ctrl+F5)")
    print("2. Try the standard workflow from scratch")
    print("3. Report any issues you encounter")
    print("="*70)

