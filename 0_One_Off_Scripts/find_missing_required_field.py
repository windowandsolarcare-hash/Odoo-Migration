"""
Find Missing Required Field
============================
Deep dive into payment register wizard to find what required field is missing.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Register Wizard Model Fields
# ==============================================================================

def check_wizard_fields_detailed():
    """Check all fields in payment register wizard with detailed info."""
    print("\n[*] Checking payment register wizard fields in detail...")
    
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
        
        # Get fields that might be required (check required=True OR have constraints)
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
                        "fields": ["id", "name", "field_description", "ttype", "required", "readonly", "store"]
                    }
                ]
            }
        }
        
        response_fields = requests.post(ODOO_URL, json=payload_fields, timeout=10)
        all_fields = response_fields.json().get("result", [])
        
        print(f"\n[INFO] Checking {len(all_fields)} fields...")
        
        # Check for fields that are commonly required but might not be marked as required
        critical_fields = ['journal_id', 'payment_method_line_id', 'amount', 'payment_date', 'currency_id']
        
        print(f"\n[INFO] Critical fields that might be required:")
        for field_name in critical_fields:
            field_info = next((f for f in all_fields if f.get("name") == field_name), None)
            if field_info:
                print(f"\n   {field_name} ({field_info.get('field_description', 'N/A')}):")
                print(f"      Required: {field_info.get('required', False)}")
                print(f"      Readonly: {field_info.get('readonly', False)}")
                print(f"      Type: {field_info.get('ttype', 'N/A')}")
                print(f"      Store: {field_info.get('store', False)}")
            else:
                print(f"\n   {field_name}: NOT FOUND")
        
        # Check for fields that are required but might be computed
        required_fields = [f for f in all_fields if f.get("required", False)]
        print(f"\n[INFO] Fields marked as required ({len(required_fields)}):")
        for field in required_fields:
            print(f"   - {field.get('name')} ({field.get('field_description', 'N/A')})")
        
        return all_fields
    
    return []

# ==============================================================================
# Check Wizard Form View for Hidden Required Fields
# ==============================================================================

def check_wizard_view_for_hidden_fields():
    """Check if required fields are hidden in the view."""
    print("\n[*] Checking wizard form view for hidden required fields...")
    
    # Get all form views
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
                    "fields": ["id", "name", "arch", "active", "priority"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    views = response.json().get("result", [])
    
    if views:
        # Check all views (base + inheritances)
        for view in views:
            arch = view.get("arch", "")
            
            # Look for fields with invisible="1" or invisible="True"
            import re
            invisible_pattern = r'<field[^>]*name="([^"]+)"[^>]*invisible="(True|1|[^"]*True[^"]*)"'
            invisible_fields = re.findall(invisible_pattern, arch, re.IGNORECASE)
            
            if invisible_fields:
                print(f"\n[!] View {view.get('id')} has invisible fields:")
                for field_name, condition in invisible_fields:
                    print(f"   - {field_name} (invisible: {condition})")
            
            # Look for required fields
            required_pattern = r'<field[^>]*name="([^"]+)"[^>]*required="(True|1)"'
            required_in_view = re.findall(required_pattern, arch, re.IGNORECASE)
            
            if required_in_view:
                print(f"\n[INFO] Fields marked as required in view {view.get('id')}:")
                for field_name, _ in required_in_view:
                    print(f"   - {field_name}")

# ==============================================================================
# Test Creating Payment Register Record
# ==============================================================================

def test_wizard_creation():
    """Try to create a payment register record to see what error we get."""
    print("\n[*] Testing payment register wizard creation...")
    
    # Get an invoice to test with
    payload_invoice = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "account.move",
                "search_read",
                [[["state", "=", "posted"], ["payment_state", "!=", "paid"]]],
                {
                    "fields": ["id", "name", "amount_residual"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_invoice = requests.post(ODOO_URL, json=payload_invoice, timeout=10)
    invoices = response_invoice.json().get("result", [])
    
    if invoices:
        invoice = invoices[0]
        invoice_id = invoice.get("id")
        
        print(f"\n[INFO] Testing with invoice {invoice.get('name')} (ID: {invoice_id})")
        
        # Get Bank journal
        payload_journal = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "account.journal",
                    "search_read",
                    [[["code", "=", "BNK1"]]],
                    {
                        "fields": ["id", "name", "code"],
                        "limit": 1
                    }
                ]
            }
        }
        
        response_journal = requests.post(ODOO_URL, json=payload_journal, timeout=10)
        journals = response_journal.json().get("result", [])
        
        if journals:
            journal_id = journals[0].get("id")
            
            # Try to create payment register with minimal fields
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
                        "account.payment.register",
                        "create",
                        [{
                            "journal_id": journal_id,
                            "payment_date": "2026-02-09",
                            "line_ids": [(6, 0, [invoice_id])]
                        }]
                    ]
                }
            }
            
            response_create = requests.post(ODOO_URL, json=payload_create, timeout=10)
            result = response_create.json().get("result")
            
            if result:
                print(f"[OK] Created payment register (ID: {result})")
                return True
            else:
                error = response_create.json().get("error", {})
                error_data = error.get("data", {})
                error_message = error_data.get("message", str(error))
                
                print(f"\n[!] ERROR creating payment register:")
                print(f"    {error_message}")
                
                # Parse error to find missing field
                if "required" in error_message.lower():
                    print(f"\n[!] This is the missing required field error!")
                    print(f"    Error details: {error}")
                
                return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIND MISSING REQUIRED FIELD")
    print("="*70)
    
    # Check fields
    all_fields = check_wizard_fields_detailed()
    
    # Check view
    check_wizard_view_for_hidden_fields()
    
    # Test creation
    test_result = test_wizard_creation()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nBased on the error and field analysis:")
    print("1. payment_date is the only field marked as 'required=True'")
    print("2. However, journal_id and payment_method_line_id might be")
    print("   required by validation even if not marked as required")
    print("3. The error might be coming from a computed field or constraint")
    print("\nCOMMON ISSUES:")
    print("- journal_id not set (even if not marked required)")
    print("- payment_method_line_id not set (needed for payment creation)")
    print("- currency_id not set (might be computed but failing)")
    print("\nSOLUTION:")
    print("Make sure ALL of these are filled in the wizard:")
    print("1. Journal: Must select 'Bank'")
    print("2. Payment Method: Must select one (Manual Payment, Checks, etc.)")
    print("3. Amount: Should be pre-filled")
    print("4. Payment Date: Should default to today")
    print("="*70)

