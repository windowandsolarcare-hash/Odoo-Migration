"""
Check Missing Required Field
=============================
Check what required fields are missing in the payment wizard.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Required Fields on account.payment.register
# ==============================================================================

def check_required_fields():
    """Check what fields are required on account.payment.register."""
    print("\n[*] Checking required fields on account.payment.register...")
    
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
                "account.payment.register",
                "fields_get",
                [],
                {"attributes": ["required", "type", "string"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    fields = response.json().get("result", {})
    
    required_fields = []
    for field_name, field_info in fields.items():
        if field_info.get("required", False):
            field_type = field_info.get("type", "unknown")
            field_string = field_info.get("string", field_name)
            required_fields.append((field_name, field_type, field_string))
    
    print(f"\n[OK] Required fields on account.payment.register:")
    for field_name, field_type, field_string in required_fields:
        print(f"   • {field_name} ({field_type}): {field_string}")
    
    return required_fields

# ==============================================================================
# Check Wizard Form for Required Fields
# ==============================================================================

def check_wizard_form_required():
    """Check which required fields are in the wizard form."""
    print("\n[*] Checking wizard form for required fields...")
    
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
        
        # Check for required attributes
        import re
        required_fields = re.findall(r'<field[^>]*required="1"[^>]*name="([^"]+)"', arch)
        
        print(f"\n[OK] Fields marked as required in form:")
        for field in required_fields:
            print(f"   • {field}")
        
        # Check for invisible required fields (problem!)
        invisible_required = re.findall(r'<field[^>]*invisible="[^"]*"[^>]*required="1"[^>]*name="([^"]+)"', arch)
        if invisible_required:
            print(f"\n[!] PROBLEM: Required fields that are invisible:")
            for field in invisible_required:
                print(f"   • {field} - This will cause validation errors!")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Missing Required Field")
    print("="*70)
    
    # Check required fields
    required = check_required_fields()
    
    # Check form
    check_wizard_form_required()
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("\nSince accounting is installed, the issue is wizard configuration.")
    print("\nThe 'missing required field' error is likely:")
    print("1. Currency field not being set (even though we made it visible)")
    print("2. A required field that's invisible")
    print("3. A computed field that's not computing properly")
    print("\nBEST SOLUTION:")
    print("Use the Python script I created to bypass the wizard entirely:")
    print("  python '0_One_Off_Scripts\\create_payment_direct.py' <invoice_id> [amount] [check_number]")
    print("="*70)

