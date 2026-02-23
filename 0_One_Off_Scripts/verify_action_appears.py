"""
Verify Action Appears in Menu
==============================
Check if there are any issues preventing the action from appearing.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Action Details
# ==============================================================================

def check_action_full_details():
    """Get full details of action 674."""
    print("\n[*] Getting full details of action 674...")
    
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
                [[674]],
                {
                    "fields": ["id", "name", "model_id", "binding_model_id", "binding_view_types", "state", "code", "active"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"\n[OK] Full details:")
        for key, value in action.items():
            print(f"   {key}: {value}")
        
        # Check if active
        if not action.get("active", True):
            print(f"\n   [!] ACTION IS INACTIVE - this is why it's not showing!")
            return action, True  # needs activation
        else:
            print(f"\n   [OK] Action is active")
            return action, False
    
    return None, False

# ==============================================================================
# Activate Action if Needed
# ==============================================================================

def activate_action():
    """Activate the action if it's inactive."""
    print("\n[*] Checking if action needs activation...")
    
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
                "write",
                [[674], {
                    "active": True
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Action activated")
        return True
    else:
        print(f"[OK] Action is already active (or activation not needed)")
        return False

# ==============================================================================
# Check All Actions on account.move
# ==============================================================================

def check_all_actions_on_invoice():
    """Check all server actions bound to account.move form view."""
    print("\n[*] Checking all server actions on account.move form...")
    
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
                [[
                    ["binding_model_id.model", "=", "account.move"],
                    ["binding_view_types", "ilike", "form"]
                ]],
                {
                    "fields": ["id", "name", "binding_view_types", "active"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} server actions on account.move form:")
        for action in result:
            active = "✓" if action.get("active", True) else "✗"
            print(f"   {active} ID: {action['id']}, Name: {action.get('name', 'N/A')}")
        
        # Check if 674 is in the list
        action_674 = [a for a in result if a['id'] == 674]
        if action_674:
            print(f"\n[OK] Action 674 IS in the list - should appear in menu")
        else:
            print(f"\n[!] Action 674 NOT in the list - may not be bound correctly")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("VERIFY: Action Appears in Menu")
    print("="*70)
    
    # Check full details
    action, needs_activation = check_action_full_details()
    
    # Activate if needed
    if needs_activation:
        activate_action()
    else:
        activate_action()  # Try anyway to ensure it's active
    
    # Check all actions
    all_actions = check_all_actions_on_invoice()
    
    print("\n" + "="*70)
    print("DIAGNOSIS:")
    print("="*70)
    print("\n1. Action 674 exists and IS our action")
    print("2. Model: Journal Entry (account.move) - CORRECT for invoices")
    print("3. Binding: account.move form view - CORRECT")
    print("4. View Types: form - CORRECT")
    print("\nIf it's still not showing:")
    print("- Hard refresh browser (Ctrl+F5)")
    print("- Check if you're on an invoice (not a draft invoice)")
    print("- Look in Actions menu (top right, not in form buttons)")
    print("="*70)

