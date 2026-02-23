"""
Test: Can we bind a window action directly to form view?
========================================================
Or do we need a server action wrapper?
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

CREATE_INVOICE_WIZARD_ACTION_ID = 478

# ==============================================================================
# Check if window actions can have binding_model_id
# ==============================================================================

def check_window_action_binding():
    """Check if the window action has binding fields."""
    print("\n[*] Checking if window action can be bound to form view...")
    
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
                "ir.actions.act_window",
                "read",
                [[CREATE_INVOICE_WIZARD_ACTION_ID]],
                {"fields": ["id", "name", "binding_model_id", "binding_view_types"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"[OK] Window action details:")
        print(f"   Name: {action['name']}")
        print(f"   Binding Model: {action.get('binding_model_id', 'None')}")
        print(f"   Binding View Types: {action.get('binding_view_types', 'None')}")
        
        if action.get('binding_model_id'):
            print("\n[INFO] Window action CAN be bound - we can update it directly!")
            return True
        else:
            print("\n[INFO] Window action is NOT bound - we need a server action wrapper")
            return False
    else:
        print("[ERROR] Could not read window action")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("TEST: Window Action Binding")
    print("="*70)
    
    can_bind = check_window_action_binding()
    
    print("\n" + "="*70)
    if can_bind:
        print("SOLUTION: Update the window action to add 'form' to binding_view_types")
    else:
        print("SOLUTION: Create a server action that opens the window action")
    print("="*70)

