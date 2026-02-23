"""
Add 'form' to Create Invoice Window Action Binding
==================================================
This updates the existing window action to include 'form' in binding_view_types,
so it appears in the form view Actions menu (just like it does in list view).
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

CREATE_INVOICE_WIZARD_ACTION_ID = 478

# ==============================================================================
# Update the window action to include 'form' in binding_view_types
# ==============================================================================

def add_form_to_binding():
    """Add 'form' to the window action's binding_view_types."""
    print("\n[*] Updating window action to include 'form' view...")
    
    # First, get current binding_view_types
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
                "ir.actions.act_window",
                "read",
                [[CREATE_INVOICE_WIZARD_ACTION_ID]],
                {"fields": ["binding_view_types"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload_read, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        current_types = result[0].get('binding_view_types', '')
        print(f"[*] Current binding_view_types: {current_types}")
        
        # Add 'form' if not already present
        if 'form' in current_types:
            print("[OK] 'form' is already in binding_view_types - no update needed!")
            return True
        
        # Update to include 'form'
        new_types = current_types + ',form' if current_types else 'form'
        print(f"[*] New binding_view_types: {new_types}")
        
        payload_write = {
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
                    "write",
                    [[CREATE_INVOICE_WIZARD_ACTION_ID], {
                        "binding_view_types": new_types
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload_write, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print("[OK] Window action updated successfully!")
            print("     'Create Invoice' will now appear in form view Actions menu")
            return True
        else:
            error = result.get("error", {})
            print(f"[ERROR] Failed to update: {error}")
            return False
    else:
        print("[ERROR] Could not read window action")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD CREATE INVOICE TO FORM VIEW")
    print("="*70)
    print("\nThis will update the existing window action (ID 478)")
    print("to include 'form' in binding_view_types.")
    print("\nResult: 'Create Invoice' will appear in form view Actions menu")
    print("="*70)
    
    success = add_form_to_binding()
    
    if success:
        print("\n[SUCCESS] Done! Refresh your Odoo form view to see the change.")
    else:
        print("\n[FAILED] Could not update. Check error message above.")

