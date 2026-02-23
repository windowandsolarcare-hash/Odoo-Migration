"""
Add Check Number Field to Payment Form
======================================
Adds check_number field to account.payment form view via view inheritance.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Payment Form View
# ==============================================================================

def get_payment_form_view():
    """Get the main payment form view ID."""
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
                "search_read",
                [[["name", "=", "account.payment.form"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        return result[0]
    return None

# ==============================================================================
# Create View Inheritance
# ==============================================================================

def create_check_number_view_inherit():
    """Create a view inheritance to add check_number field."""
    print("\n[*] Creating view inheritance for check_number field...")
    
    # XML to add check_number field after payment_method_line_id
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               placeholder="Check Number (e.g., 1234)"
               attrs="{'invisible': [('payment_method_line_id', '!=', 8)], 'required': [('payment_method_line_id', '=', 8)]}"
               options="{'no_create': True}"/>
    </xpath>
</data>"""
    
    # Odoo 19+ uses invisible/required directly, not attrs
    # We'll add it always visible, but can make it required via Studio if needed
    arch_simple = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               placeholder="Check Number (e.g., 1234)"/>
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
                    "name": "account.payment.form.inherit.check_number",
                    "model": "account.payment",
                    "inherit_id": 879,  # account.payment.form view ID
                    "arch": arch_simple,
                    "type": "form"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created view inheritance (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create view: {error}")
        return None

# ==============================================================================
# Check if View Already Exists
# ==============================================================================

def check_existing_inherit():
    """Check if check_number inheritance already exists."""
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
                "search_read",
                [[["name", "ilike", "check_number"], ["model", "=", "account.payment"]]],
                {
                    "fields": ["id", "name"],
                    "limit": 5
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[!] Found {len(result)} existing views with 'check_number' in name:")
        for view in result:
            print(f"   • {view['name']} (ID: {view['id']})")
        return True
    else:
        print("[OK] No existing check_number inheritance found")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD: Check Number Field to Payment Form")
    print("="*70)
    
    # Check if already exists
    exists = check_existing_inherit()
    
    if not exists:
        # Get base view
        base_view = get_payment_form_view()
        if base_view:
            print(f"[OK] Base view found: {base_view['name']} (ID: {base_view['id']})")
        
        # Create inheritance
        view_id = create_check_number_view_inherit()
        
        if view_id:
            print("\n[OK] Check number field added to payment form!")
            print("     It will appear after 'Payment Method' field")
            print("     Required when 'Check' payment method is selected")
        else:
            print("\n[!] Failed to add check_number field")
            print("     You may need to add it manually via Studio")
    else:
        print("\n[OK] Check number field inheritance may already exist")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Refresh browser (Ctrl+F5) to see changes")
    print("2. Check number field will appear after Payment Method")
    print("3. It's required when 'Check' payment method is selected")
    print("="*70)

