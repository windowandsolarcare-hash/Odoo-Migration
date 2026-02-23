"""
Add Currency Field to Payment Form
====================================
Add currency_id as a hidden field that defaults from invoice context.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check if Currency Field Already Visible
# ==============================================================================

def check_currency_in_form():
    """Check if currency_id is visible in payment form."""
    print("\n[*] Checking if currency_id is visible in payment form...")
    
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
        arch = result[0].get("arch", "")
        # Check if currency_id is visible (not just in arch, but actually displayed)
        if 'field name="currency_id"' in arch:
            # Check if it's invisible
            if 'invisible="1"' in arch or 'invisible="True"' in arch:
                print("[OK] currency_id exists but is hidden")
            else:
                print("[OK] currency_id exists and is visible")
        else:
            print("[!] currency_id field not found in form")
        return result[0]
    return None

# ==============================================================================
# Add Currency Field with Default from Context
# ==============================================================================

def add_currency_field_to_form():
    """Add currency_id as a hidden field that defaults from invoice."""
    print("\n[*] Adding currency_id field to payment form...")
    
    # Add currency_id as a hidden field that defaults from context
    # It should default from default_currency_id in context (from invoice)
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='journal_id']" position="after">
        <field name="currency_id" 
               invisible="1"
               options="{'no_create': True}"/>
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
                    "name": "account.payment.form.inherit.currency",
                    "model": "account.payment",
                    "inherit_id": 879,  # account.payment.form view ID
                    "arch": arch,
                    "type": "form"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created currency field inheritance (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create view: {error}")
        return None

# ==============================================================================
# Check Existing Currency Inheritances
# ==============================================================================

def check_existing_currency_inherit():
    """Check if currency inheritance already exists."""
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
                [[["name", "ilike", "currency"], ["model", "=", "account.payment"]]],
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
        print(f"[!] Found {len(result)} existing views with 'currency' in name:")
        for view in result:
            print(f"   • {view['name']} (ID: {view['id']})")
        return True
    else:
        print("[OK] No existing currency inheritance found")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD: Currency Field to Payment Form")
    print("="*70)
    
    # Check existing
    exists = check_existing_currency_inherit()
    
    # Check form
    form_view = check_currency_in_form()
    
    if not exists:
        # Add currency field
        view_id = add_currency_field_to_form()
        
        if view_id:
            print("\n[OK] Currency field added to payment form!")
            print("     It will be hidden but will default from invoice context")
        else:
            print("\n[!] Failed to add currency field")
            print("     The issue might be that the Pay action needs to pass")
            print("     default_currency_id in context")
    else:
        print("\n[OK] Currency inheritance may already exist")
    
    print("\n" + "="*70)
    print("NOTE:")
    print("="*70)
    print("The currency should be automatically set from the invoice when")
    print("using the Pay action. If this doesn't work, we may need to:")
    print("1. Check if invoice has currency_id set")
    print("2. Modify Pay action to explicitly pass currency in context")
    print("3. Set currency_id on Bank journal")
    print("="*70)

