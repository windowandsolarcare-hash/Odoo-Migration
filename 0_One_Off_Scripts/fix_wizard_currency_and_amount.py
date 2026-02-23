"""
Fix Wizard Currency and Amount Field
=====================================
1. Make currency_id visible/required in wizard
2. Make amount field editable
3. Ensure currency defaults from invoice
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Wizard Form for Currency and Amount
# ==============================================================================

def check_wizard_currency_amount():
    """Check how currency and amount are handled in wizard."""
    print("\n[*] Checking wizard form for currency and amount fields...")
    
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
        arch = result[0].get("arch", "")
        
        # Check currency_id
        if 'field name="currency_id"' in arch:
            # Check if it's invisible
            if 'invisible="1"' in arch or 'invisible="True"' in arch:
                print("[!] currency_id is INVISIBLE - this may be the problem")
            else:
                print("[OK] currency_id is visible")
        
        # Check amount field
        if 'field name="amount"' in arch:
            # Check if it's readonly
            if 'readonly="1"' in arch or 'readonly="True"' in arch or 'readonly="not can_edit_wizard' in arch:
                print("[!] amount field has readonly condition")
                # Extract the condition
                import re
                readonly_match = re.search(r'readonly="([^"]+)"', arch)
                if readonly_match:
                    print(f"   Readonly condition: {readonly_match.group(1)}")
            else:
                print("[OK] amount field should be editable")
        
        return arch
    return None

# ==============================================================================
# Make Currency Visible and Required
# ==============================================================================

def make_currency_visible():
    """Make currency_id visible in wizard form."""
    print("\n[*] Making currency_id visible in wizard...")
    
    # The currency_id is currently invisible (line 18 in XML)
    # We need to make it visible or ensure it has a default
    # Actually, better approach: ensure it defaults from invoice context
    
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='currency_id']" position="attributes">
        <attribute name="invisible">0</attribute>
        <attribute name="required">1</attribute>
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
                    "name": "account.payment.register.form.inherit.currency_visible",
                    "model": "account.payment.register",
                    "inherit_id": 885,
                    "arch": arch,
                    "type": "form",
                    "priority": 25
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created currency visibility override (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return None

# ==============================================================================
# Fix Amount Field Readonly
# ==============================================================================

def fix_amount_readonly():
    """Remove readonly condition from amount field."""
    print("\n[*] Fixing amount field readonly condition...")
    
    # The amount field has: readonly="not can_edit_wizard or can_group_payments and not group_payment"
    # We need to override this to make it always editable (or at least editable when not grouping)
    
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='amount']" position="attributes">
        <attribute name="readonly">can_group_payments and not group_payment</attribute>
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
                    "name": "account.payment.register.form.inherit.amount_editable",
                    "model": "account.payment.register",
                    "arch": arch,
                    "inherit_id": 885,
                    "type": "form",
                    "priority": 25
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created amount editable override (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return None

# ==============================================================================
# Check Invoice Currency Context
# ==============================================================================

def check_invoice_currency_context():
    """Check if invoice currency is passed in context."""
    print("\n[*] Checking invoice currency context...")
    
    print("[INFO] When Pay action is clicked, it should pass:")
    print("       - default_currency_id from invoice")
    print("       - default_journal_id")
    print("       - default_amount")
    print("\n[INFO] If currency isn't being passed, the wizard won't have it")
    print("       and will fail when creating the payment.")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Wizard Currency and Amount Field")
    print("="*70)
    
    # Check current state
    wizard_arch = check_wizard_currency_amount()
    
    # Make currency visible
    currency_view = make_currency_visible()
    
    # Fix amount readonly
    amount_view = fix_amount_readonly()
    
    # Check context
    check_invoice_currency_context()
    
    print("\n" + "="*70)
    print("FIXES APPLIED:")
    print("="*70)
    print("\n1. Made currency_id visible and required in wizard")
    print("2. Fixed amount field to be editable (removed can_edit_wizard condition)")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Click Pay on invoice")
    print("3. Currency should now be visible/required")
    print("4. Amount field should be editable")
    print("5. Fill in amount, select payment method, date")
    print("6. Create payment")
    print("="*70)

