"""
Investigate Payment Form Workflow
==================================
1. Check why Cash/Credit/Check aren't showing in dropdown
2. Check payment form fields (amount, reference, etc.)
3. Understand payment creation workflow
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Method Lines (with journal filter)
# ==============================================================================

def check_payment_method_lines_with_journal():
    """Check payment method lines filtered by journal."""
    print("\n[*] Checking payment method lines by journal...")
    
    # Get Bank journal ID
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
                "account.journal",
                "search_read",
                [[["code", "=", "BNK1"]]],
                {"fields": ["id", "name"], "limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    journal_result = response.json().get("result", [])
    
    if journal_result:
        journal_id = journal_result[0]["id"]
        print(f"[OK] Bank journal ID: {journal_id}")
        
        # Get payment method lines for this journal
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
                    "search_read",
                    [[["journal_id", "=", journal_id]]],
                    {
                        "fields": ["id", "name", "payment_method_id", "journal_id"],
                        "limit": 20
                    }
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result", [])
        
        print(f"\n[OK] Found {len(result)} payment method lines for Bank journal:")
        for line in result:
            method_id = line.get('payment_method_id', [])
            method_name = method_id[1] if isinstance(method_id, list) and len(method_id) > 1 else 'N/A'
            print(f"   • ID: {line['id']}, Name: {line['name']}, Method: {method_name}")
        
        return result
    else:
        print("[!] Bank journal not found")
        return []

# ==============================================================================
# Check Account.Payment Fields
# ==============================================================================

def check_payment_fields():
    """Check what fields exist on account.payment model."""
    print("\n[*] Checking account.payment fields...")
    
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
                "account.payment",
                "fields_get",
                [],
                {"attributes": ["string", "type", "required"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    fields = response.json().get("result", {})
    
    # Look for relevant fields
    relevant_fields = [
        "amount", "payment_method_line_id", "payment_date", 
        "ref", "check_number", "communication", "payment_reference"
    ]
    
    print("\n[OK] Relevant payment fields:")
    for field_name in relevant_fields:
        if field_name in fields:
            field_info = fields[field_name]
            field_type = field_info.get("type", "unknown")
            field_string = field_info.get("string", field_name)
            required = field_info.get("required", False)
            print(f"   • {field_name} ({field_type}): {field_string} {'[REQUIRED]' if required else ''}")
        else:
            print(f"   • {field_name}: NOT FOUND")
    
    # Check for any field with "check" or "reference" in name
    print("\n[OK] Fields containing 'check' or 'reference':")
    for field_name, field_info in fields.items():
        if "check" in field_name.lower() or "reference" in field_name.lower() or "ref" in field_name.lower():
            field_type = field_info.get("type", "unknown")
            field_string = field_info.get("string", field_name)
            print(f"   • {field_name} ({field_type}): {field_string}")
    
    return fields

# ==============================================================================
# Check Payment Form View
# ==============================================================================

def check_payment_form_view():
    """Check the payment form view structure."""
    print("\n[*] Checking payment form view...")
    
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
                [[["model", "=", "account.payment"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch"],
                    "limit": 5
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} payment form views")
        # Don't print arch (too long), just confirm they exist
        for view in result:
            print(f"   • {view.get('name', 'Unnamed')} (ID: {view['id']})")
    else:
        print("[!] No payment form views found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Payment Form Workflow")
    print("="*70)
    
    # Check payment method lines
    method_lines = check_payment_method_lines_with_journal()
    
    # Check payment fields
    payment_fields = check_payment_fields()
    
    # Check form view
    form_views = check_payment_form_view()
    
    print("\n" + "="*70)
    print("FINDINGS:")
    print("="*70)
    print("\n1. Payment method lines should show if journal matches")
    print("2. Need to check if 'ref' or 'check_number' field exists")
    print("3. Amount field behavior depends on payment form configuration")
    print("="*70)

