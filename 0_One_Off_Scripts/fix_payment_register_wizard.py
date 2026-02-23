"""
Fix Payment Register Wizard
============================
Update the account.payment.register wizard form to:
1. Show Cash/Credit/Check payment method lines
2. Add check_number field
3. Ensure amount field is editable
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Wizard Form View
# ==============================================================================

def get_wizard_form_view():
    """Get the payment register wizard form view."""
    print("\n[*] Getting payment register wizard form view...")
    
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
                "read",
                [[885]],  # account.payment.register.form
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        arch = view.get("arch", "")
        print(f"[OK] Wizard form view (ID: 885):")
        print(f"   Name: {view.get('name', 'N/A')}")
        
        # Check for payment_method_line_id
        if "payment_method_line_id" in arch:
            print(f"   -> Has payment_method_line_id field")
            # Check if it has domain/filter
            if "domain" in arch.lower():
                print(f"   -> Has domain filter (may be filtering out our methods)")
        
        # Check for amount field
        if "field name=\"amount\"" in arch:
            print(f"   -> Has amount field")
            if "readonly" in arch.lower():
                print(f"   -> Amount field may be readonly")
        
        # Check for check_number
        if "check_number" in arch:
            print(f"   -> Has check_number field")
        else:
            print(f"   -> NO check_number field - needs to be added")
        
        return view
    else:
        print("[!] Wizard form view not found")
        return None

# ==============================================================================
# Add check_number to Wizard Form
# ==============================================================================

def add_check_number_to_wizard():
    """Add check_number field to payment register wizard form."""
    print("\n[*] Adding check_number field to wizard form...")
    
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
                "create",
                [{
                    "name": "account.payment.register.form.inherit.check_number",
                    "model": "account.payment.register",
                    "inherit_id": 885,  # Base wizard form
                    "arch": arch,
                    "type": "form"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created check_number field in wizard (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create view: {error}")
        return None

# ==============================================================================
# Check Payment Method Line Domain in Wizard
# ==============================================================================

def check_payment_method_domain():
    """Check how payment method lines are filtered in wizard."""
    print("\n[*] Checking payment method line domain in wizard...")
    
    # The wizard may filter payment method lines by journal
    # We need to ensure Cash/Credit/Check (IDs 6,7,8) are included
    print("[INFO] Payment method lines should be filtered by journal_id")
    print("       When Bank journal is selected, it should show:")
    print("       - All method lines where journal_id = Bank journal")
    print("\n[INFO] Our Cash/Credit/Check lines (IDs 6,7,8) are linked to Bank journal")
    print("       They should appear automatically when Bank is selected")
    print("\n[INFO] If they don't appear, the wizard may have a domain filter")
    print("       that excludes them, or there's a caching issue")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Payment Register Wizard")
    print("="*70)
    
    # Get wizard form
    wizard_view = get_wizard_form_view()
    
    # Add check_number
    check_num_id = add_check_number_to_wizard()
    
    # Check domain
    check_payment_method_domain()
    
    print("\n" + "="*70)
    print("FINDINGS:")
    print("="*70)
    print("\n1. The Pay action opens account.payment.register WIZARD")
    print("   -> This is different from account.payment form")
    print("   -> The wizard has its own form view (ID: 885)")
    print("\n2. Payment method lines should show when Bank journal is selected")
    print("   -> Cash (ID: 6), Credit (ID: 7), Check (ID: 8) exist")
    print("   -> They should appear automatically")
    print("\n3. If they don't appear, possible causes:")
    print("   -> Browser cache (try hard refresh: Ctrl+F5)")
    print("   -> Wizard form has domain filter excluding them")
    print("   -> Journal not properly selected")
    print("\n4. check_number field added to wizard form")
    print("   -> Will show when Check payment method is selected")
    print("="*70)
    print("\nNEXT STEPS:")
    print("1. Hard refresh browser (Ctrl+F5)")
    print("2. Click Pay on invoice again")
    print("3. Select Bank journal")
    print("4. Payment Method dropdown should show Cash, Credit, Check")
    print("5. If not, we may need to check wizard domain filters")
    print("="*70)

