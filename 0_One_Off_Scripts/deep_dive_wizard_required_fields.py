"""
Deep Dive Wizard Required Fields
=================================
Check all fields in payment register wizard and identify what's missing.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check All Fields in Payment Register Wizard
# ==============================================================================

def check_all_wizard_fields():
    """Check all fields in the payment register wizard model."""
    print("\n[*] Checking all fields in payment register wizard...")
    
    # Get model
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
                    "fields": ["id", "name", "model"]
                }
            ]
        }
    }
    
    response_model = requests.post(ODOO_URL, json=payload_model, timeout=10)
    model = response_model.json().get("result", [])
    
    if model:
        model_id = model[0]["id"]
        
        # Get ALL fields (not just required)
        payload_fields = {
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
                    [[["model_id", "=", model_id]]],
                    {
                        "fields": ["id", "name", "field_description", "ttype", "required", "readonly"]
                    }
                ]
            }
        }
        
        response_fields = requests.post(ODOO_URL, json=payload_fields, timeout=10)
        all_fields = response_fields.json().get("result", [])
        
        print(f"\n[INFO] All fields in payment register wizard ({len(all_fields)} total):")
        
        required = []
        optional = []
        
        for field in all_fields:
            field_name = field.get("name", "")
            field_desc = field.get("field_description", "")
            is_required = field.get("required", False)
            is_readonly = field.get("readonly", False)
            
            if is_required:
                required.append(field)
                print(f"\n   REQUIRED: {field_name} ({field_desc})")
                print(f"      Type: {field.get('ttype', 'N/A')}, Readonly: {is_readonly}")
            else:
                optional.append(field)
        
        print(f"\n[INFO] Summary:")
        print(f"   Required fields: {len(required)}")
        print(f"   Optional fields: {len(optional)}")
        
        return required, optional
    
    return [], []

# ==============================================================================
# Check Wizard Form View Structure
# ==============================================================================

def check_wizard_form_structure():
    """Check the wizard form view to see what fields are actually displayed."""
    print("\n[*] Checking wizard form view structure...")
    
    # Get all form views for the wizard
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
                [[["model", "=", "account.payment.register"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch", "active", "priority"],
                    "order": "priority asc"
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    views = response.json().get("result", [])
    
    if views:
        # Get the base view (lowest priority, usually 16)
        base_view = views[0]
        arch = base_view.get("arch", "")
        
        print(f"\n[OK] Base wizard form view (ID: {base_view.get('id')}, Priority: {base_view.get('priority', 16)})")
        
        # Extract field names from XML
        import re
        field_pattern = r'<field[^>]*name="([^"]+)"'
        fields_in_view = re.findall(field_pattern, arch)
        
        print(f"\n[INFO] Fields found in view ({len(fields_in_view)}):")
        for field_name in fields_in_view:
            print(f"   - {field_name}")
        
        return fields_in_view, arch
    
    return [], ""

# ==============================================================================
# Compare Required vs Displayed
# ==============================================================================

def compare_required_vs_displayed(required_fields, displayed_fields):
    """Compare required fields with what's displayed in the view."""
    print("\n[*] Comparing required fields with displayed fields...")
    
    required_names = [f.get("name") for f in required_fields]
    missing = [name for name in required_names if name not in displayed_fields]
    
    if missing:
        print(f"\n[!] PROBLEM: Required fields NOT in view:")
        for field_name in missing:
            field_info = next((f for f in required_fields if f.get("name") == field_name), None)
            if field_info:
                print(f"   - {field_name} ({field_info.get('field_description', 'N/A')})")
                print(f"     This is REQUIRED but not displayed in the form!")
        return missing
    else:
        print(f"\n[OK] All required fields are in the view")
        return []

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("DEEP DIVE: Wizard Required Fields")
    print("="*70)
    
    # Check all fields
    required, optional = check_all_wizard_fields()
    
    # Check form view
    displayed_fields, arch = check_wizard_form_structure()
    
    # Compare
    missing_fields = compare_required_vs_displayed(required, displayed_fields)
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    
    if missing_fields:
        print(f"\n[!] FOUND THE PROBLEM!")
        print(f"    Required field(s) missing from form view:")
        for field in missing_fields:
            print(f"    - {field}")
        print(f"\n    SOLUTION: Need to add these fields to the wizard form view")
    else:
        print(f"\n[INFO] All required fields are in the view")
        print(f"       The error might be:")
        print(f"       1. Field is hidden or has invisible attribute")
        print(f"       2. Field value is not being set from context")
        print(f"       3. Field validation is failing")
        print(f"\n       Common issue: journal_id might not be getting set")
        print(f"       Make sure 'Journal' field is visible and has a value")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("\n1. Refresh browser (Ctrl+F5)")
    print("2. Try Pay button again")
    print("3. When wizard opens, check:")
    print("   - Is 'Journal' field visible?")
    print("   - Does it have a value selected?")
    print("   - Is 'Payment Method' visible and selected?")
    print("   - Is 'Payment Date' visible and has a date?")
    print("4. If any field is missing or empty, that's the problem")
    print("="*70)

