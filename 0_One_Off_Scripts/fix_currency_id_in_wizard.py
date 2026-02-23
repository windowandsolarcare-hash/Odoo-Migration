"""
Fix Currency ID in Wizard
==========================
currency_id is required but invisible. Need to make it visible or ensure it's set.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Current Wizard View
# ==============================================================================

def check_wizard_view():
    """Check the wizard view to see currency_id visibility."""
    print("\n[*] Checking wizard form view for currency_id...")
    
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
                [[["model", "=", "account.payment.register"], ["type", "=", "form"], ["priority", "=", 16]]],
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    views = response.json().get("result", [])
    
    if views:
        view = views[0]
        arch = view.get("arch", "")
        
        # Check if currency_id is in the view and if it's invisible
        if 'name="currency_id"' in arch:
            print(f"[OK] currency_id field found in view")
            
            # Check if it's invisible
            if 'invisible="1"' in arch or 'invisible="True"' in arch:
                print(f"[!] PROBLEM: currency_id is INVISIBLE but REQUIRED!")
                print(f"    This is why you're getting 'missing required field' error")
                
                # Check if it's required
                if 'required="1"' in arch or 'required="True"' in arch:
                    print(f"[!] currency_id is both REQUIRED and INVISIBLE - this is the bug!")
                    return True, view.get("id"), arch
        
        return False, view.get("id"), arch
    
    return False, None, ""

# ==============================================================================
# Fix Currency ID Visibility
# ==============================================================================

def fix_currency_id_visibility(view_id, arch):
    """Make currency_id visible in the wizard or ensure it's set from context."""
    print("\n[*] Fixing currency_id visibility...")
    
    # Option 1: Make currency_id visible (but it should be computed from invoice)
    # Option 2: Ensure currency_id is set from context when Pay action is called
    
    # Actually, currency_id should be computed from the invoice
    # The issue might be that it's not being set properly
    
    # Let's create a view inheritance to make currency_id visible (as readonly)
    # OR ensure it's properly set
    
    # Check if there's already an inheritance
    payload_inherit = {
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
                [[["model", "=", "account.payment.register"], ["inherit_id", "=", view_id]]],
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response_inherit = requests.post(ODOO_URL, json=payload_inherit, timeout=10)
    inheritances = response_inherit.json().get("result", [])
    
    # Create view inheritance to make currency_id visible (readonly)
    arch_inherit = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='currency_id']" position="attributes">
        <attribute name="invisible">0</attribute>
        <attribute name="readonly">1</attribute>
    </xpath>
</data>"""
    
    payload_create = {
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
                    "name": "account.payment.register.form.currency_visible",
                    "model": "account.payment.register",
                    "inherit_id": view_id,
                    "arch": arch_inherit,
                    "type": "form",
                    "priority": 30
                }]
            ]
        }
    }
    
    response_create = requests.post(ODOO_URL, json=payload_create, timeout=10)
    result = response_create.json().get("result")
    
    if result:
        print(f"[OK] Created view inheritance to make currency_id visible (ID: {result})")
        return result
    else:
        error = response_create.json().get("error", {})
        print(f"[!] Failed to create view inheritance: {error}")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Currency ID in Wizard")
    print("="*70)
    
    has_issue, view_id, arch = check_wizard_view()
    
    if has_issue and view_id:
        inherit_id = fix_currency_id_visibility(view_id, arch)
        
        if inherit_id:
            print("\n" + "="*70)
            print("FIX APPLIED!")
            print("="*70)
            print("\ncurrency_id is now visible (readonly) in the payment wizard.")
            print("It should be automatically set from the invoice currency.")
            print("\nNEXT STEPS:")
            print("1. Refresh browser (Ctrl+F5)")
            print("2. Try Pay button again")
            print("3. currency_id should now be visible and set automatically")
            print("4. Fill in Journal and Payment Method")
            print("5. Click 'Create Payment'")
        else:
            print("\n[!] Could not fix view - currency_id might need to be set from context")
    else:
        print("\n[INFO] currency_id might not be the issue")
        print("       The error could be from journal_id or payment_method_line_id")
        print("       Make sure both are selected in the wizard")
    
    print("="*70)

