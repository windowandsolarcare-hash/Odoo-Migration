"""
Fix check_number Field Visibility
==================================
Update the view inheritance to ensure check_number shows when Check is selected.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Update check_number View
# ==============================================================================

def update_check_number_view():
    """Update check_number view to ensure it's visible."""
    print("\n[*] Updating check_number view inheritance...")
    
    # Odoo 19+ syntax - use invisible attribute directly
    # Show check_number when payment_method_line_id = 8 (Check)
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               placeholder="Check Number (e.g., 1234)"
               invisible="payment_method_line_id != 8"/>
    </xpath>
</data>"""
    
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
                "ir.ui.view",
                "write",
                [[2403], {  # Our check_number view ID
                    "arch": arch
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Updated check_number view")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to update view: {error}")
        return False

# ==============================================================================
# Alternative: Create New View Without Conditions
# ==============================================================================

def create_always_visible_check_number():
    """Create a new view that always shows check_number."""
    print("\n[*] Creating always-visible check_number view...")
    
    # Always show it - user can fill it when Check is selected
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               placeholder="Check Number (enter if paying by check)"/>
    </xpath>
</data>"""
    
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
                "ir.ui.view",
                "create",
                [{
                    "name": "account.payment.form.inherit.check_number.always_visible",
                    "model": "account.payment",
                    "inherit_id": 879,  # Base payment form
                    "arch": arch,
                    "type": "form",
                    "priority": 20  # Higher priority to ensure it shows
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created always-visible check_number view (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create view: {error}")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: check_number Field Visibility")
    print("="*70)
    
    # Try updating existing view first
    updated = update_check_number_view()
    
    if not updated:
        # If update fails, create new view
        view_id = create_always_visible_check_number()
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Try creating payment again")
    print("3. check_number should now appear after Payment Method field")
    print("="*70)

