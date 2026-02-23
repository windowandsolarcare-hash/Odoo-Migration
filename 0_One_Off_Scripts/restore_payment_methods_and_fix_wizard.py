"""
Restore Payment Methods and Fix Wizard
=======================================
1. Restore payment method names to original
2. Find and fix missing required field in payment register wizard
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Restore Payment Method Names
# ==============================================================================

def restore_payment_method_names():
    """Restore payment method names to original Odoo names."""
    print("\n[*] Restoring payment method names to original...")
    
    # We renamed these earlier:
    # ID 1: "Manual Payment" -> "Cash"
    # ID 3: "Manual Payment" -> "Credit"  
    # ID 4: "Checks" -> "Check"
    
    # Restore to original names
    restorations = [
        {"id": 1, "original": "Manual Payment"},
        {"id": 3, "original": "Manual Payment"},
        {"id": 4, "original": "Checks"},
    ]
    
    restored = []
    for method in restorations:
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
                    "account.payment.method.line",
                    "read",
                    [[method["id"]]],
                    {
                        "fields": ["id", "name"]
                    }
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        current = response.json().get("result", [])
        
        if current:
            current_name = current[0].get("name", "")
            if current_name != method["original"]:
                # Restore original name
                payload_write = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [
                            ODOO_DB,
                            ODOO_USER_ID,
                            ODOO_API_KEY,
                            "account.payment.method.line",
                            "write",
                            [[method["id"]], {
                                "name": method["original"]
                            }]
                        ]
                    }
                }
                
                response_write = requests.post(ODOO_URL, json=payload_write, timeout=10)
                result = response_write.json().get("result")
                
                if result:
                    print(f"   [OK] Restored ID {method['id']}: '{current_name}' -> '{method['original']}'")
                    restored.append(method["id"])
                else:
                    error = response_write.json().get("error", {})
                    print(f"   [!] Failed to restore ID {method['id']}: {error}")
            else:
                print(f"   [INFO] ID {method['id']} already has original name: '{method['original']}'")
    
    return restored

# ==============================================================================
# Check Payment Register Wizard Required Fields
# ==============================================================================

def check_wizard_required_fields():
    """Check what fields are required in the payment register wizard."""
    print("\n[*] Checking payment register wizard required fields...")
    
    # Get the wizard model
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
        
        # Get required fields
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
                    [[["model_id", "=", model_id], ["required", "=", True]]],
                    {
                        "fields": ["id", "name", "field_description", "ttype", "required"]
                    }
                ]
            }
        }
        
        response_fields = requests.post(ODOO_URL, json=payload_fields, timeout=10)
        required_fields = response_fields.json().get("result", [])
        
        print(f"\n[INFO] Required fields in payment register wizard:")
        for field in required_fields:
            print(f"   - {field.get('name')} ({field.get('field_description', 'N/A')})")
        
        # Common required fields in payment register wizard:
        # - journal_id (Journal)
        # - payment_method_line_id (Payment Method)
        # - amount (Amount)
        # - payment_date (Payment Date)
        
        return required_fields
    
    return []

# ==============================================================================
# Check Payment Register Wizard Form View
# ==============================================================================

def check_wizard_form_view():
    """Check the payment register wizard form view to see what fields are shown."""
    print("\n[*] Checking payment register wizard form view...")
    
    # Find the form view
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_URL,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.ui.view",
                "search_read",
                [[["model", "=", "account.payment.register"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch", "active"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    views = response.json().get("result", [])
    
    if views:
        # Get the base view (lowest priority)
        base_view = min(views, key=lambda v: v.get("priority", 16))
        arch = base_view.get("arch", "")
        
        print(f"\n[OK] Found wizard form view (ID: {base_view.get('id')})")
        
        # Check for common required fields in the XML
        required_fields_in_view = []
        if "journal_id" in arch:
            required_fields_in_view.append("journal_id")
        if "payment_method_line_id" in arch:
            required_fields_in_view.append("payment_method_line_id")
        if "amount" in arch:
            required_fields_in_view.append("amount")
        if "payment_date" in arch:
            required_fields_in_view.append("payment_date")
        
        print(f"\n[INFO] Fields found in view: {', '.join(required_fields_in_view)}")
        
        # Check if journal_id is required but not visible
        if "journal_id" not in required_fields_in_view:
            print(f"\n[!] WARNING: journal_id might be missing from view")
            print(f"    This could be the 'missing required field' error")
        
        return base_view
    
    return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESTORE PAYMENT METHODS & FIX WIZARD")
    print("="*70)
    
    # Restore payment method names
    restored = restore_payment_method_names()
    
    # Check required fields
    required_fields = check_wizard_required_fields()
    
    # Check wizard form view
    wizard_view = check_wizard_form_view()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print(f"\nRestored {len(restored)} payment method name(s) to original")
    print("\nRequired fields in payment register wizard:")
    for field in required_fields:
        print(f"  - {field.get('name')} ({field.get('field_description', 'N/A')})")
    
    print("\n" + "="*70)
    print("TROUBLESHOOTING 'MISSING REQUIRED FIELD' ERROR:")
    print("="*70)
    print("\nCommon causes:")
    print("1. Journal not selected - Make sure 'Journal' field has a value (Bank)")
    print("2. Payment Method not selected - Make sure 'Payment Method' has a value")
    print("3. Amount is 0 or empty - Should be pre-filled but verify")
    print("4. Payment Date missing - Should default to today but verify")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Try Pay button again")
    print("3. Make sure ALL fields are filled:")
    print("   - Journal: Select 'Bank'")
    print("   - Payment Method: Select one (Manual Payment, Checks, etc.)")
    print("   - Amount: Should be pre-filled")
    print("   - Payment Date: Should default to today")
    print("4. Then click 'Create Payment'")
    print("="*70)

