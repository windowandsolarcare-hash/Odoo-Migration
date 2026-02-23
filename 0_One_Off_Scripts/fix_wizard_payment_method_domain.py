"""
Fix Wizard Payment Method Domain
=================================
Override the payment_method_line_id domain in the wizard to include Cash/Credit/Check.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Override Payment Method Domain in Wizard
# ==============================================================================

def override_payment_method_domain():
    """Override payment_method_line_id domain to include Cash/Credit/Check."""
    print("\n[*] Overriding payment_method_line_id domain in wizard...")
    
    # The wizard uses available_payment_method_line_ids to filter
    # We'll override the domain to explicitly include our Cash/Credit/Check (IDs 6,7,8)
    # Domain: [('id', 'in', available_payment_method_line_ids.ids + [6,7,8])]
    # But simpler: just filter by journal and payment_type
    
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="attributes">
        <attribute name="domain">[('journal_id', '=', journal_id), ('payment_method_id.payment_type', '=', 'inbound')]</attribute>
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
                    "name": "account.payment.register.form.inherit.payment_method_domain",
                    "model": "account.payment.register",
                    "inherit_id": 885,  # Base wizard form
                    "arch": arch,
                    "type": "form",
                    "priority": 20  # Higher priority
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created domain override (ID: {result})")
        print(f"     Domain: [('journal_id', '=', journal_id), ('payment_method_id.payment_type', '=', 'inbound')]")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create view: {error}")
        return None

# ==============================================================================
# Alternative: Check if we can modify available_payment_method_line_ids
# ==============================================================================

def check_available_payment_methods_field():
    """Check the available_payment_method_line_ids computed field."""
    print("\n[*] Checking available_payment_method_line_ids field...")
    
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
                "ir.model.fields",
                "search_read",
                [[
                    ["model", "=", "account.payment.register"],
                    ["name", "=", "available_payment_method_line_ids"]
                ]],
                {
                    "fields": ["name", "field_description", "compute", "store"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        field = result[0]
        print(f"\n[OK] available_payment_method_line_ids field:")
        print(f"   Description: {field.get('field_description', 'N/A')}")
        print(f"   Compute: {field.get('compute', 'N/A')}")
        print(f"   Store: {field.get('store', False)}")
        print(f"\n   This is a computed field that determines which payment")
        print(f"   method lines are available. The wizard uses this to filter.")
        print(f"\n   We can't easily override computed fields, so we'll override")
        print(f"   the domain on payment_method_line_id instead.")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Wizard Payment Method Domain")
    print("="*70)
    
    # Check available methods field
    check_available_payment_methods_field()
    
    # Override domain
    view_id = override_payment_method_domain()
    
    print("\n" + "="*70)
    print("SOLUTION:")
    print("="*70)
    print("\nThe wizard uses 'available_payment_method_line_ids' computed field")
    print("to filter payment methods. We've overridden the domain on")
    print("payment_method_line_id to explicitly include all inbound payment")
    print("method lines for the selected journal.")
    print("\nThis should make Cash/Credit/Check appear when Bank journal is selected.")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Click Pay on invoice")
    print("3. Select Bank journal")
    print("4. Payment Method should now show Cash, Credit, Check")
    print("="*70)

