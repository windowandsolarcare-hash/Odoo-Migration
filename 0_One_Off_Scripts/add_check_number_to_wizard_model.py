"""
Add Check Number to Wizard Model
==================================
Add check_number field to account.payment.register model so it can be
entered in the wizard and passed to the payment when created.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Add check_number Field to Wizard Model
# ==============================================================================

def add_check_number_field_to_model():
    """Add check_number field to account.payment.register model."""
    print("\n[*] Adding check_number field to account.payment.register model...")
    
    # Check if field already exists
    payload_check = {
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
                    ["name", "=", "check_number"]
                ]],
                {
                    "fields": ["id", "name"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_check = requests.post(ODOO_URL, json=payload_check, timeout=10)
    result_check = response_check.json().get("result", [])
    
    if result_check:
        print(f"[OK] check_number field already exists (ID: {result_check[0]['id']})")
        return result_check[0]['id']
    
    # Create the field
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
                "create",
                [{
                    "name": "check_number",
                    "model_id": "account.payment.register",  # Need to get model ID first
                    "field_description": "Check Number",
                    "ttype": "char",
                    "help": "Enter the check number if paying by check"
                }]
            ]
        }
    }
    
    # First, get the model ID
    payload_model = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.model",
                "search_read",
                [[["model", "=", "account.payment.register"]]],
                {
                    "fields": ["id", "model"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_model = requests.post(ODOO_URL, json=payload_model, timeout=10)
    model_result = response_model.json().get("result", [])
    
    if model_result:
        model_id = model_result[0]["id"]
        print(f"[OK] Found model ID: {model_id}")
        
        # Now create the field with correct model_id
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
                    "ir.model.fields",
                    "create",
                    [{
                        "name": "check_number",
                        "model_id": model_id,
                        "field_description": "Check Number",
                        "ttype": "char",
                        "help": "Enter the check number if paying by check"
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload_create, timeout=10)
        result = response.json().get("result")
        
        if result:
            print(f"[OK] Created check_number field (ID: {result})")
            return result
        else:
            error = response.json().get("error", {})
            print(f"[!] Failed to create field: {error}")
            print(f"    May need to add via Studio instead")
    else:
        print("[!] Model not found")
    
    return None

# ==============================================================================
# Add check_number to Wizard Form (After Field is Created)
# ==============================================================================

def add_check_number_to_form():
    """Add check_number field to wizard form view."""
    print("\n[*] Adding check_number to wizard form...")
    
    arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//field[@name='payment_method_line_id']" position="after">
        <field name="check_number" 
               placeholder="Check Number (e.g., 1234)"
               invisible="payment_method_line_id != 4"/>
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
                    "name": "account.payment.register.form.inherit.check_number_field",
                    "model": "account.payment.register",
                    "inherit_id": 885,
                    "arch": arch,
                    "type": "form",
                    "priority": 30
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Added check_number to form (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        print(f"    Field may need to be created first via Studio")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD: Check Number to Wizard Model")
    print("="*70)
    
    # Try to add field to model
    field_id = add_check_number_field_to_model()
    
    # Add to form
    if field_id:
        form_view = add_check_number_to_form()
    else:
        print("\n[!] Could not create field automatically")
        print("    You may need to add it via Studio:")
        print("    1. Go to Settings > Technical > Database Structure > Models")
        print("    2. Find 'account.payment.register'")
        print("    3. Add field 'check_number' (type: Char)")
        print("    4. Then we can add it to the form view")
    
    print("\n" + "="*70)
    print("ALTERNATIVE SOLUTION:")
    print("="*70)
    print("\nFor now, you can enter the check number in the Memo/Communication")
    print("field. The field is editable, so you can replace the sales order")
    print("number with the check number.")
    print("\nWe can sync this to the payment's check_number field later via")
    print("Phase 6 automation, or add the field to the wizard model manually.")
    print("="*70)

