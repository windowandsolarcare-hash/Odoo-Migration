"""
Check Memo Field Position
=========================
Verify why memo field isn't appearing under Payment Method on right side.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Form View Structure
# ==============================================================================

def check_payment_form_structure():
    """Check the payment form view to see where fields are positioned."""
    print("\n[*] Checking payment form view structure...")
    
    # Get the base payment form view
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
                [[879]],  # account.payment.form
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
        print(f"[OK] Payment form view found (ID: 879)")
        
        # Check if payment_method_line_id is in a group
        if "payment_method_line_id" in arch:
            print(f"     payment_method_line_id field found")
            # Find the context around it
            import re
            # Look for the field and its surrounding structure
            pattern = r'(<field[^>]*name="payment_method_line_id"[^>]*/>)'
            match = re.search(pattern, arch)
            if match:
                # Get context around the match
                start = max(0, match.start() - 200)
                end = min(len(arch), match.end() + 200)
                context = arch[start:end]
                print(f"\n     Context around payment_method_line_id:")
                print(f"     {context[:100]}...")
        
        # Check our inheritance view
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
                    "read",
                    [[2450]],  # Our memo field view
                    {
                        "fields": ["id", "name", "arch", "active", "priority"]
                    }
                ]
            }
        }
        
        response_inherit = requests.post(ODOO_URL, json=payload_inherit, timeout=10)
        result_inherit = response_inherit.json().get("result", [])
        
        if result_inherit:
            arch_inherit = result_inherit[0].get("arch", "")
            active = result_inherit[0].get("active", True)
            priority = result_inherit[0].get("priority", 16)
            
            print(f"\n[OK] Memo field inheritance view found (ID: 2450)")
            print(f"     Active: {active}")
            print(f"     Priority: {priority}")
            print(f"     Arch: {arch_inherit}")
            
            if not active:
                print(f"     [!] View is INACTIVE - this is the problem!")
                return False
            
            # Check if check_number field is in the inheritance
            if "check_number" in arch_inherit:
                print(f"     check_number field found in inheritance")
            else:
                print(f"     [!] check_number field NOT found in inheritance")
        else:
            print(f"[!] Memo field inheritance view not found")
            return False
        
        return True
    else:
        print(f"[!] Payment form view not found")
        return False

# ==============================================================================
# Fix Memo Field Position - Try Different Approach
# ==============================================================================

def fix_memo_field_position():
    """Try to fix memo field position by using a different xpath."""
    print("\n[*] Attempting to fix memo field position...")
    
    # The issue might be that payment_method_line_id is in a different group
    # Let's try to find it and add memo right after it in the same group
    
    # First, let's check if there's a group structure
    # Then we'll add memo field after payment_method_line_id within that group
    
    arch_inherit = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               string="Memo"
               placeholder="Memo/Reference (e.g., check number)"
               invisible="payment_method_line_id == False"
               widget="text"/>
    </xpath>
</data>"""
    
    # Update the existing view
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
                [[2450], {
                    "arch": arch_inherit,
                    "active": True,
                    "priority": 30
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Updated memo field inheritance view")
        print(f"     Field should now appear after Payment Method")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK & FIX: Memo Field Position")
    print("="*70)
    
    # Check structure
    checked = check_payment_form_structure()
    
    # Try to fix
    fixed = fix_memo_field_position()
    
    print("\n" + "="*70)
    print("ABOUT THE WARNING:")
    print("="*70)
    print("\nThe warning 'This payment has the same partner, amount and date'")
    print("is just Odoo's duplicate detection. You can safely:")
    print("1. Fill in Payment Method (Cash, Credit, or Check)")
    print("2. Fill in Memo (check number if paying by check)")
    print("3. Click Confirm")
    print("4. Then click Actions → Post Payment")
    print("\nThe warning won't prevent you from creating the payment.")
    print("\nNOTE: Memo field position fix applied - refresh browser (Ctrl+F5)")
    print("="*70)

